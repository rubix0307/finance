from ai.strategies import UsageCost
from decimal import Decimal


class OpenAI4oStrategy:
    NAME = 'ChatGPT 4o'
    PROMPT_PRICE = Decimal('2.5')  # per 1M
    COMPLETION_PRICE = Decimal('10')  # per 1M

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> UsageCost:
        prompt_cost = (Decimal(prompt_tokens) / 1_000_000) * self.PROMPT_PRICE
        completion_cost = (Decimal(completion_tokens) / 1_000_000) * self.COMPLETION_PRICE
        total_cost = prompt_cost + completion_cost
        return UsageCost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=total_cost
        )

class OpenAI4oMiniStrategy(OpenAI4oStrategy):
    NAME = 'ChatGPT 4o-mini'
    PROMPT_PRICE = Decimal('0.15')  # per 1M
    COMPLETION_PRICE = Decimal('0.6')  # per 1M

