import os
from threading import Thread

import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

if settings.DEBUG and os.getenv('TELEGRAM_BOT_INFINITY_POLLING') == '1':
    bot.remove_webhook()
    Thread(target=bot.infinity_polling).start()