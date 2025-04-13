from functools import wraps
from typing import Callable, Any
from telebot.types import Message

from telegram.utils import get_or_create_user


def user_required(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(message: Message, *args: Any, **kwargs: Any) -> Any:
        user = get_or_create_user(user_id=message.from_user.id)
        kwargs['user_created'] = True
        kwargs['user'] = user
        return func(message, *args, **kwargs)

    return wrapper
