from telebot.types import LabeledPrice
from telegram.handlers.bot_instance import bot


@bot.message_handler(commands=['start'])
def send_invoice(message):
    bot.send_message(message.chat.id, f"Hello")
