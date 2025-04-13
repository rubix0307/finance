from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path(f'webhook-{settings.TELEGRAM_BOT_TOKEN[-10:]}/', views.telegram_webhook, name='telegram_webhook'),
    path(f'authenticate-web-app/', views.authenticate_web_app, name='telegram_authenticate_web_app'),
]
