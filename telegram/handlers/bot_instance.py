import os
from threading import Thread

import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

if os.getenv('run_bot') == '1':
    os.environ['run_bot'] = '0'
    bot.remove_webhook()
    Thread(target=lambda: bot.infinity_polling(
        allowed_updates=['message', 'edited_message', 'callback_query','pre_checkout_query', 'successful_payment']
    )).start()