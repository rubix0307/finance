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
