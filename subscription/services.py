from datetime import date, datetime, timedelta
from functools import cached_property
from collections import defaultdict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, Q
from .models import Plan, Subscription, FeatureUsage

User = get_user_model()
class SubscriptionManager:
    FREE_PLAN_SLUG = getattr(settings, 'FREE_PLAN_SLUG', 'free')

    def __init__(self, user: User):
        self.user = user

    @cached_property
    def active_subs(self):
        now = datetime.now()
        qs = Subscription.objects.filter(
            user=self.user,
            started_at__lte=now
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=now)
        ).select_related('plan').prefetch_related('plan__features__feature')

        subs = list(qs)
        paid = [s for s in subs if s.plan.slug != self.FREE_PLAN_SLUG]
        if paid:
            return sorted(paid, key=lambda s: (s.expires_at or date.max))

        free = [s for s in subs if s.plan.slug == self.FREE_PLAN_SLUG]
        if free:
            return free

        free_plan = Plan.objects.get(slug=self.FREE_PLAN_SLUG)
        sub = Subscription.objects.create(
            user=self.user,
            plan=free_plan,
            started_at=now,
            expires_at=now + timedelta(days=30),
        )
        return [sub]

    @cached_property
    def aggregated(self):
        limits = defaultdict(lambda: 0)
        features = {}

        for sub in self.active_subs:
            for pf in sub.plan.features.all():
                f = pf.feature
                features[f.code] = f
                if f.is_boolean:
                    limits[f.code] = None
                else:
                    if pf.limit is None:
                        limits[f.code] = None
                    elif limits[f.code] is not None:
                        limits[f.code] += pf.limit

        usage_qs = FeatureUsage.objects.filter(
            subscription__in=self.active_subs,
            feature__code__in=limits.keys()
        ).values('feature__code').annotate(total=Sum('used'))
        used_map = {r['feature__code']: r['total'] for r in usage_qs}

        result = {}
        for code, limit in limits.items():
            used = used_map.get(code, 0)
            remaining = None if (limit is None or features[code].is_boolean) else max(limit - used, 0)
            result[code] = {
                'feature': features[code],
                'limit': limit,
                'used': used,
                'remaining': remaining,
            }
        return result

    def can(self, code: str, amount: int = 1) -> bool:
        data = self.aggregated.get(code)
        if not data:
            return False
        if data['feature'].is_boolean:
            return True
        return data['remaining'] is None or data['remaining'] >= amount

    def register(self, code: str, amount: int = 1):
        data = self.aggregated.get(code)
        if not data or data['feature'].is_boolean:
            return

        target_sub = None
        for sub in self.active_subs:
            pf = next((pf for pf in sub.plan.features.all() if pf.feature.code == code), None)
            if not pf:
                continue

            if pf.limit is None:
                target_sub = sub
                break

            usage = FeatureUsage.objects.filter(subscription=sub, feature=data['feature']).first()
            used = usage.used if usage else 0
            if used + amount <= pf.limit:
                target_sub = sub
                break

        if not target_sub:
            return

        with transaction.atomic():
            obj, _ = FeatureUsage.objects.select_for_update().get_or_create(
                subscription=target_sub,
                feature=data['feature']
            )
            obj.used += amount
            obj.save()