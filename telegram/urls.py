from django.conf import settings
from django.urls import path
from .views import telegram_webhook

urlpatterns = [
    path(f'webhook-{settings.TELEGRAM_BOT_TOKEN[-10:]}/', telegram_webhook, name='telegram_webhook'),
]
