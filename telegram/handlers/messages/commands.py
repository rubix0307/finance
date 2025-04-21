from typing import Any
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from django.utils import translation
from django.utils.translation import gettext as _

from telegram.handlers.bot_instance import bot
from telegram.handlers.share.users import send_user_share
from telegram.handlers.utils import user_required, parse_start_param


def start_messages(message: Message, **kwargs: dict[str, Any]) -> None:
    ...


def default_start(message: Message, **kwargs: dict[str, Any]) -> None:
    user = kwargs['user']
    with translation.override(user.language_code):
        me = bot.get_me()

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(_("Open the app"), url=f'https://t.me/{me.username}?startapp'))

        bot.send_message(message.chat.id, _("Hello"), reply_markup=markup)


@bot.message_handler(commands=['start'])
@parse_start_param
@user_required
def start(message: Message, params: dict[str, str | int], **kwargs: dict[str, Any]) -> None:
    if kwargs.get('user_created'):
        start_messages(message, **kwargs)

    try:
        match params.get('action'):
            case 'add_member':
                send_user_share(message=message, section_id=params.get('section_id'), **kwargs)
                bot.delete_message(message.chat.id, message.message_id)
            case _:
                default_start(message, **kwargs)
    except Exception as e:
        default_start(message)