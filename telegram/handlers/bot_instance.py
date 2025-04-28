import os
from threading import Thread

import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

if settings.DEBUG and os.getenv('TELEGRAM_BOT_INFINITY_POLLING') == '1':
    start = input('Run bot pooling y/n')
    if start == 'y':
        bot.remove_webhook()
        Thread(target=lambda: bot.infinity_polling(
            allowed_updates=['message', 'edited_message', 'callback_query','pre_checkout_query', 'successful_payment']
        )).start()