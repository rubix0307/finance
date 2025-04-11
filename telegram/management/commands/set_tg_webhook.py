from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse_lazy

from telegram.bot import bot



class Command(BaseCommand):
    help = 'Installs Webhook for Telegram bot'

    def handle(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        bot.remove_webhook()
        url = settings.BASE_URL + reverse_lazy('telegram_webhook')
        print(url)
        print(bot.set_webhook(url=url))
