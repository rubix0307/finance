from receipt.models import Receipt
from .models import AIUsageLog
from .strategies import AIProviderStrategy


class AIUsageLogger:
    def __init__(self, strategy: AIProviderStrategy):
        self.strategy = strategy

    def log_usage(self, prompt_tokens: int, completion_tokens: int, receipt: Receipt) -> AIUsageLog:
        usage = self.strategy.calculate_cost(prompt_tokens, completion_tokens)

        log = AIUsageLog.objects.create(
            provider_name=self.strategy.NAME,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cost_usd=usage.cost_usd,
            receipt=receipt,
            receipt_owner=receipt.owner,
        )
        return log
