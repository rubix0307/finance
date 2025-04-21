from typing import Any, Callable
from django.utils.translation import gettext as _
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery, InlineKeyboardButton as IKB, Message
from telegram.handlers.bot_instance import bot


class F:
    def __init__(self, data_filter: CallbackDataFilter):
        self.data_filter = data_filter

    def __call__(self, callback: CallbackQuery, **kwargs: dict[str, Any]) -> bool:
        return self.data_filter.check(callback)

class CallbackStorage:
    menu = CallbackData('name', prefix='menu')
    language = CallbackData('code', prefix='lang')


Button = Callable[..., IKB]
def make_button(default_label: str, **kwargs: Any) -> Callable[..., IKB]:
    return lambda label=None: IKB(label or _(default_label), **kwargs)

class ButtonStorage:
    web_app_main = make_button('Open the app', url='https://t.me/finance_lens_bot?startapp')
    menu_start = make_button('Main page', callback_data=CallbackStorage.menu.new(name='start'))
    menu_language = make_button('Language', callback_data=CallbackStorage.menu.new(name='language'))


class QueryContext:
    def __init__(self, query: Message | CallbackQuery):
        self.query = query

    def __enter__(self) -> Message:
        if isinstance(self.query, CallbackQuery):
            self.is_callback = True
            self.message: Message = self.query.message
        else:
            self.is_callback = False
            self.message: Message = self.query
        return self.message

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_callback:
            try:
                bot.delete_message(
                    chat_id=self.message.chat.id,
                    message_id=self.message.message_id
                )
            except Exception:
                pass