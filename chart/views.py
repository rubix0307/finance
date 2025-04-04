from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render

from .factory import ChartFactory


def get_chart_data(request: WSGIRequest) -> JsonResponse:
    chart_type = request.GET.get("chart_type", "pie")

    try:
        chart = ChartFactory.get_chart(chart_type)
        return JsonResponse(chart.get_chart_data())
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
