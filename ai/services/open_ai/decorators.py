from functools import wraps
from typing import TypeVar, Callable, ParamSpec, cast
import openai

R = TypeVar("R")
P = ParamSpec("P")


def handle_openai_errors(func: Callable[P, R]) -> Callable[P, R | None]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except (openai.AuthenticationError, openai.NotFoundError, ValueError):
            return None
        except Exception as ex:
            return None

    return cast(Callable[P, R | None], wrapper)