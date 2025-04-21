from typing import Any
from telebot.types import Message, InlineKeyboardMarkup, CallbackQuery
from django.utils.translation import gettext as _

from telegram.handlers.bot_instance import bot
from telegram.handlers.share.users import send_user_share
from telegram.handlers.utils import user_required, parse_start_param
from telegram.handlers.common import ButtonStorage, F, CallbackStorage, QueryContext


@user_required
def start_new_user(message: Message, **kwargs: dict[str, Any]) -> None:
    ...

@user_required
def default_start(message: Message, **kwargs: dict[str, Any]) -> None:
    markup = InlineKeyboardMarkup()
    markup.add(ButtonStorage.web_app_main())
    markup.add(ButtonStorage.menu_language())
    bot.send_message(message.chat.id, _("Hello"), reply_markup=markup)


@bot.message_handler(commands=['start'])
@bot.callback_query_handler(func=F(CallbackStorage.menu.filter(name='start')))
@parse_start_param
@user_required
def start(query: Message | CallbackQuery, params: dict[str, str | int], **kwargs: dict[str, Any]) -> None:
    with QueryContext(query):
        if isinstance(query, CallbackQuery):
            message = query.message
        else:
            message = query

        if kwargs.get('user_created'):
            start_new_user(message, **kwargs)
            return

        try:
            match params.get('action'):
                case 'add_member':
                    send_user_share(message=message, section_id=params.get('section_id'), **kwargs)
                    bot.delete_message(message.chat.id, message.message_id)
                case _:
                    default_start(message, **kwargs)
        except Exception as e:
            default_start(message)