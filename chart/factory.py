from typing import Type
from .charts import PieChart, BaseChart

ChartType = str

class ChartFactory:
    charts: dict[ChartType, Type[BaseChart]] = {
        'pie': PieChart,
    }

    @staticmethod
    def get_chart(chart_type: ChartType) -> BaseChart:
        chart_class = ChartFactory.charts.get(chart_type)
        if not chart_class:
            raise ValueError(f'Unknown chart type: {chart_type}')
        return chart_class()
