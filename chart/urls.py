
from django.urls import URLPattern, path
from . import views


urlpatterns: list[URLPattern] = [
       path('get_data/', views.get_chart_data, name='get_chart_data'),
]
