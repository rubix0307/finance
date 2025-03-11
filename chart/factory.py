from typing import Literal, Any
from .charts import PieChart, BaseChart


class ChartFactory:
    charts = {
        'pie': PieChart,
    }

    @staticmethod
    def get_chart(chart_type: Literal['pie'], period: Literal['day'] = 'day', **kwargs: dict[str, Any]) -> BaseChart:
        chart_class = ChartFactory.charts.get(chart_type)
        if not chart_class:
            raise ValueError(f'Unknown chart type: {chart_type}')
        return chart_class(period=period, **kwargs)
