from typing import TypedDict, Dict, Optional


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