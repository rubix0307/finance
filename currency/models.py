from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)

    class Meta:
        db_table = 'currency'

    def __str__(self):
        return self.code


class CurrencyRateHistory(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    per_usd = models.DecimalField(max_digits=14, decimal_places=7)
    date = models.DateTimeField()

    class Meta:
        get_latest_by = ['date']
        db_table = 'currency_rate_history'

    def __str__(self):
        return f'{self.id}: {self.per_usd}'

