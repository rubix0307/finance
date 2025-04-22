from typing import Any, Callable
from django.utils.translation import gettext as _
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery, InlineKeyboardButton as IKB, Message, WebAppInfo

from telegram.handlers.bot_instance import bot


class F:
    def __init__(self, data_filter: CallbackDataFilter):
        self.data_filter = data_filter

    def __call__(self, callback: CallbackQuery, **kwargs: dict[str, Any]) -> bool:
        return self.data_filter.check(callback)

class CallbackStorage:
    menu = CallbackData('name', prefix='menu')
    language = CallbackData('code', prefix='lang')


class ButtonStorage:
    web_app_main = lambda label=None: IKB(label or _('Open the app'), url='https://t.me/finance_lens_bot?startapp')
    web_app_faq = lambda label=None: IKB(label or 'FAQ', web_app=WebAppInfo(url='https://finance-lens.online/telegram/check-web-app/?next=/faq/'))
    menu_start = lambda label=None: IKB(label or _('Main page'), callback_data=CallbackStorage.menu.new(name='start'))
    menu_language = lambda label=None: IKB(label or '🌐 ' + _('Language'), callback_data=CallbackStorage.menu.new(name='language'))


