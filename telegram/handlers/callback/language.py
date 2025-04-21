from typing import Any

from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.handlers.bot_instance import bot
from telegram.handlers.common import CallbackStorage as Storage, F, ButtonStorage, QueryContext
from telegram.handlers.utils import user_required


@bot.callback_query_handler(func=F(Storage.menu.filter(name='language')))
@user_required
def language_menu(callback: CallbackQuery, **kwargs: dict[str, Any]) -> None:
    with QueryContext(callback):
        bot.answer_callback_query(callback.id)
        markup = InlineKeyboardMarkup()
        for code, label in settings.LANGUAGES:
            btn = InlineKeyboardButton(label, callback_data=Storage.language.new(code=code))
            markup.add(btn)

        bot.send_message(callback.message.chat.id, _('Choose language'), reply_markup=markup)


@bot.callback_query_handler(func=F(Storage.language.filter()))
@user_required
def language_selected(callback: CallbackQuery, **kwargs: dict[str, Any]) -> None:
    with QueryContext(callback):
        bot.answer_callback_query(callback.id)

        data = Storage.language.parse(callback.data)
        selected_code = data['code']

        user = kwargs['user']
        is_set_new = False
        if selected_code in [code for code, label in settings.LANGUAGES]:
            user.language_code = selected_code
            user.save()
            is_set_new = True

        with translation.override(user.language_code):
            bot.send_message(
                callback.message.chat.id,
                _('Language updated') if is_set_new else _('Language not updated'),
                reply_markup=InlineKeyboardMarkup().add(ButtonStorage.menu_start()),
            )
            bot.delete_message(
                callback.message.chat.id,
                callback.message.message_id,
            )

