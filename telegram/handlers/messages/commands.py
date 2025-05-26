from typing import Any

from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import gettext as _

from telebot.types import Message, InlineKeyboardMarkup, CallbackQuery

from telegram.handlers.bot_instance import bot
from telegram.handlers.share.users import send_user_share
from telegram.handlers.utils import user_required, parse_start_param, QueryContext, query_context
from telegram.handlers.common import ButtonStorage, F, CallbackStorage


@user_required
def start_new_user(message: Message, **kwargs: dict[str, Any]) -> None:
    ...

@user_required
def default_start(message: Message, **kwargs: dict[str, Any]) -> None:
    markup = InlineKeyboardMarkup()
    markup.add(ButtonStorage.web_app_main())
    markup.add(ButtonStorage.web_app_faq())
    markup.add(ButtonStorage.menu_language())

    text = _(
        'Hello!\n'
        'Finance Lens is a bot for tracking your expenses.\n\n'
        'Send me a photo of a receipt or a free-form text description of your expense, and I will analyze it and show a chart in the web app via the button below.'
    )
    try:
        bot.send_photo(
            caption=text,
            photo=settings.BASE_URL + static('img/start_img.png'),
            reply_markup=markup,
        )
    except:
        bot.send_message(
            message.chat.id,
            text=text,
            reply_markup=markup,
        )



@bot.message_handler(commands=['start'])
@bot.callback_query_handler(func=F(CallbackStorage.menu.filter(name='start')))
@parse_start_param
@user_required
@query_context
def start(query: Message | CallbackQuery, params: dict[str, str | int], **kwargs: dict[str, Any]) -> None:
    if isinstance(query, CallbackQuery):
        message = query.message
    else:
        message = query

    if kwargs.get('user_created'):
        start_new_user(message, **kwargs)

    try:
        match params.get('action'):
            case 'add_member':
                send_user_share(message, section_id=params.get('section_id'), **kwargs)
                bot.delete_message(message.chat.id, message.message_id)
            case _:
                default_start(message, **kwargs)
    except Exception as e:
        default_start(message)