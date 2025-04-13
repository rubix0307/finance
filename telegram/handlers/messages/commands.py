from typing import Any

from telebot.types import LabeledPrice, Message, ReplyKeyboardMarkup,InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton, WebAppInfo
from telegram.handlers.bot_instance import bot
from telegram.handlers.utils import user_required
from user.models import User


@bot.message_handler(commands=['start'])
@user_required
def start(message: Message, user: User, **kwargs: dict[str, Any]) -> None:
    me = bot.get_me()
    web_app_url = f'https://t.me/{me.username}?startapp'

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Открыть приложение', url=web_app_url))

    bot.send_message(message.chat.id, f'Привет', reply_markup=markup)
