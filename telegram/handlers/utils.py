import base64
import json
from functools import wraps
from typing import Callable, Any
from telebot.types import Message

from telegram.utils import get_or_create_user


def user_required(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(message: Message, *args: Any, **kwargs: Any) -> Any:
        user_kwargs = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
        }

        user = get_or_create_user(user_id=message.from_user.id, **user_kwargs)
        kwargs['user_created'] = True
        kwargs['user'] = user
        return func(message, *args, **kwargs)

    return wrapper

def parse_start_param(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(message: Message, *args, **kwargs) -> Any:
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
