
from typing import Protocol
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class UsageCost:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Decimal

class AIProviderStrategy(Protocol):
    NAME: str

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> UsageCost:
        ...