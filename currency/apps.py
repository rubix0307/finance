from datetime import datetime
from django.apps import AppConfig



class CurrencyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currency'

    def ready(self):
        from .models import CurrencyRateHistory, Currency

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