from typing import Any
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from telegram.handlers.bot_instance import bot
from telegram.handlers.share.users import send_user_share
from telegram.handlers.utils import user_required, parse_start_param



def default_start(message: Message) -> None:
    me = bot.get_me()
    web_app_url = f'https://t.me/{me.username}?startapp'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Открыть приложение', url=web_app_url))
    bot.send_message(message.chat.id, f'Привет', reply_markup=markup)


@bot.message_handler(commands=['start'])
@parse_start_param
@user_required
def start(message: Message, params: dict[str, str | int], **kwargs: dict[str, Any]) -> None:

    try:
        match params.get('action'):
            case 'add_member':
                send_user_share(message=message, section_id=params.get('section_id'))
                bot.delete_message(message.chat.id, message.message_id)
            case _:
                default_start(message)
    except Exception as e:
        default_start(message)