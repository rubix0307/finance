from django.db import models

from receipt.models import Receipt
from user.models import User


class AIUsageLog(models.Model):
    provider_name = models.CharField(max_length=100)
    prompt_tokens = models.PositiveIntegerField()
    completion_tokens = models.PositiveIntegerField()
    total_tokens = models.PositiveIntegerField()
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    receipt = models.ForeignKey(Receipt, null=True, blank=True, on_delete=models.SET_NULL)
    receipt_owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.provider_name} - ${self.cost_usd}"

    class Meta:
        db_table = "ai_usage_log"