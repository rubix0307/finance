import base64
import json
from functools import wraps
from typing import Callable, Any

from django.utils import translation
from telebot.types import Message, CallbackQuery

from telegram.utils import get_or_create_user
from user.models import User


def user_required(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(query: Message| CallbackQuery, *args: Any, **kwargs: Any) -> Any:
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
