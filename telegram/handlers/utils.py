import base64
import json
from functools import wraps
from typing import Callable, Any

from django.utils import translation
from telebot.types import Message, CallbackQuery, PreCheckoutQuery

from telegram.handlers.bot_instance import bot
from telegram.utils import get_or_create_user
from user.models import User


def user_required(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(query: Message| CallbackQuery | PreCheckoutQuery, *args: Any, **kwargs: Any) -> Any:
        user = kwargs.get('user')

        if not isinstance(user, User):
            user_kwargs = {
                'username': query.from_user.username,
                'first_name': query.from_user.first_name,
                'last_name': query.from_user.last_name,
            }

            user, created = get_or_create_user(user_id=query.from_user.id, **user_kwargs)
            kwargs['user_created'] = created
            kwargs['user'] = user

        with translation.override(user.language_code):
            return func(query, *args, **kwargs)

    return wrapper

def parse_start_param(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(message: Message, *args, **kwargs) -> Any:
        if isinstance(message, CallbackQuery):
            params = None
        else:
            _, *params = message.text.rsplit(maxsplit=1)

        if params:
            encoded = params[0]
            try:
                padding = '=' * (-len(encoded) % 4)
                decoded_bytes = base64.urlsafe_b64decode(encoded + padding)
                decoded_str = decoded_bytes.decode('utf-8')
                data = json.loads(decoded_str)
                return func(message, params=data, *args, **kwargs)
            except (ValueError, json.JSONDecodeError, Exception) as e:
                print(f"Ошибка при декодировании параметра: {e}")
                return func(message, params={}, *args, **kwargs)
        else:
            return func(message, params={}, *args, **kwargs)
    return wrapper


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

def query_context(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(query: Message | CallbackQuery, *args, **kwargs) -> Any:
        with QueryContext(query):
            return func(query, *args, **kwargs)

    return wrapper