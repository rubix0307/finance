from abc import ABC, abstractmethod
from typing import Any
from .schemes import ChartResponse


class BaseChart(ABC):

    @abstractmethod
    def get_chart_data(self) -> ChartResponse:
        pass


class PieChart(BaseChart):
    def __init__(self, period: str = 'day', **kwargs: dict[str, Any]):
        super().__init__()
        self.period = period

    def get_chart_data(self) -> ChartResponse:
        data: list[dict[str, Any]] = []
        if self.period == 'day':
            data = [{'label': 'Утро', 'value': 30}, {'label': 'День', 'value': 50}, {'label': 'Вечер', 'value': 20}]
        elif self.period == 'week':
            data = [{'label': 'Понедельник', 'value': 100}, {'label': 'Среда', 'value': 200}, {'label': 'Пятница', 'value': 150}]

        return {
            'type': 'pie',
            'data': {
                'labels': [point['label'] for point in data],
                'datasets': [{
                    'label': f'Круговая диаграмма ({self.period})',
                    'data': [point['value'] for point in data],
                    'backgroundColor': ['red', 'blue', 'green']
                }]
            }
        }