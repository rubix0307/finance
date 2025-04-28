from enum import StrEnum
from datetime import date
from django.db import models
from django.contrib.auth import get_user_model
from parler.models import TranslatableModel, TranslatedFields


class Feature(TranslatableModel):
    code = models.CharField(max_length=64, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
    )
    is_boolean = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class PlanPeriod(StrEnum):
    MONTHLY = "monthly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"


class Plan(TranslatableModel):
    slug = models.SlugField(unique=True)
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        link=models.URLField(null=True, blank=True)
    )
    period = models.CharField(
        max_length=12,
        choices=[(p.value, p.name) for p in PlanPeriod],
        default=PlanPeriod.MONTHLY,
    )
    is_active = models.BooleanField(default=False)
    price_stars = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.slug



class PlanFeature(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="features")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    limit = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("plan", "feature")


class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    started_at = models.DateField()
    expires_at = models.DateField(null=True, blank=True)

    @property
    def is_active(self) -> bool:
        today = date.today()
        return self.started_at <= today and (self.expires_at is None or today <= self.expires_at)

    def __str__(self):
        return f"{self.user} – {self.plan} [{self.started_at}…{self.expires_at or '∞'}]"


class FeatureUsage(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="usages")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    used = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("subscription", "feature")
