from typing import TypedDict, Dict, Optional
from ninja import Schema

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

class CurrencySchema(Schema):
    code: str
