from typing import TypedDict, Dict, Optional

class CurrencyResponseError(TypedDict):
    code: int
    info: str

class CurrencyResponse(TypedDict):
    success: bool
    terms: str
    privacy: str
    timestamp: int
    source: str
    quotes: Dict[str, float]
    error: Optional[CurrencyResponseError]