from functools import wraps
from typing import Callable, Any
from telebot.types import Message
from user.models import User


def user_required(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(message: Message, *args: Any, **kwargs: Any) -> Any:
        tg_id = message.from_user.id

        try:
            user = User.objects.get(id=tg_id)
        except User.DoesNotExist:
            user = User(
                id=tg_id,
            )
            user.save(is_new=True)
            kwargs["user_created"] = True

        kwargs["user"] = user
        return func(message, *args, **kwargs)

    return wrapper
