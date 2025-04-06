from typing import TypedDict, Dict, Optional

from ninja import Schema, Field


class Dataset(TypedDict):
    label: str
    data: list[int]
    backgroundColor: list[str]


class ChartData(TypedDict):
    labels: list[str]
    datasets: list[Dataset]


class ChartResponse(TypedDict):
    type: str
    data: ChartData

class CurrencyDataSchema(Schema):
    original: float
    converted: float

class ChartPieSchema(Schema):
    chart_title: str
    data: list['ChartPieDataSchema']

class ChartPieDataSchema(Schema):
    category_id: int
    category_name: str
    category_color: str
    value: float
    currencies: dict[str, CurrencyDataSchema] = Field(  # type: ignore
        ...,
        description="Keys are currency codes (e.g. 'EUR', 'NOK')",
        example={
            "EUR": CurrencyDataSchema(original=0, converted=0),
            "NOK": CurrencyDataSchema(original=0, converted=0)
        }
    )