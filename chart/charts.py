from abc import ABC, abstractmethod
from typing import Any
from .schemas import ChartResponse


class BaseChart(ABC):
    _type: str

    @abstractmethod
    def get_chart_data(self) -> ChartResponse:
        pass


class PieChart(BaseChart):
    _type = 'pie'

    def get_chart_data(self) -> ChartResponse:
        data: list[dict[str, Any]] = []

        return {
            'type': self._type,
            'data': {
                'labels': [point['label'] for point in data],
                'datasets': [{
                    'label': f'Круговая диаграмма',
                    'data': [point['value'] for point in data],
                    'backgroundColor': ['red', 'blue', 'green']
                }]
            }
        }
