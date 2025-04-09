from datetime import datetime
from django.apps import AppConfig

from django.conf import settings


class CurrencyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currency'

    def ready(self):
        from .models import CurrencyRateHistory, Currency
        if not settings.DEBUG:
            try:
                usd_currency = Currency.objects.get(code='USD')
            except Currency.DoesNotExist:
                raise RuntimeError("USD currency must exist")

            if not CurrencyRateHistory.objects.filter(currency=usd_currency).exists():
                CurrencyRateHistory.objects.create(
                    currency=usd_currency,
                    per_usd=1,
                    date=datetime.now(),
                )