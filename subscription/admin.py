from django.contrib import admin
from django.utils.safestring import mark_safe
from parler.admin import TranslatableAdmin

from .admin_actions import create_invoice_links
from .models import Feature, Plan, PlanFeature, Subscription, FeatureUsage



@admin.register(Feature)
class FeatureAdmin(TranslatableAdmin):
    list_display = ('code', 'name', 'is_boolean', 'description')
    list_filter = ('is_boolean',)
    search_fields = ('code', 'translations__name')

class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1
    autocomplete_fields = ['feature']
    verbose_name = 'Plan Feature'
    verbose_name_plural = 'Plan Features'

@admin.register(Plan)
class PlanAdmin(TranslatableAdmin):
    list_display = ('slug', 'title', 'period', 'feature_summary')
    list_filter = ('period', 'is_active',)
    search_fields = ('slug', 'translations__title')
    readonly_fields = ('link',)
    inlines = [PlanFeatureInline]
    actions = [create_invoice_links]

    def feature_summary(self, obj):
        items = []
        for pf in obj.features.all():
            limit = '∞' if pf.limit is None else pf.limit
            items.append(f"{pf.feature.code}: {limit}")
        return mark_safe('<br>'.join(items))
    feature_summary.short_description = 'Features & Limits'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'started_at', 'expires_at', 'is_active')
    list_filter = ('plan', 'started_at', 'expires_at')
    search_fields = ('user__email', 'user__username')
    autocomplete_fields = ['user', 'plan']
    readonly_fields = ('is_active',)

@admin.register(FeatureUsage)
class FeatureUsageAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'feature', 'used')
    list_filter = ('feature',)
    search_fields = ('subscription__user__email', 'feature__code')
    autocomplete_fields = ['subscription', 'feature']
