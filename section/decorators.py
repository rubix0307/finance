from typing import Callable, Any, ParamSpec
from django.core.handlers.wsgi import WSGIRequest
from functools import update_wrapper
from ninja.errors import HttpError

from .models import Section

P = ParamSpec("P")
class BaseSectionDecorator[R]:
    def __init__(self, func: Callable[P, R]) -> None:
        update_wrapper(self, func)
        self.func = func

    def __call__(self, request: WSGIRequest, section_pk: int, **kwargs: dict[str, Any]) -> R:
        return self.func(request, section_pk, **kwargs)


class SectionRequired[R](BaseSectionDecorator[R]):
    def __call__(self, request: WSGIRequest, section_pk: int, **kwargs: dict[str, Any]) -> R:
        try:
            section_obj = Section.objects.get(pk=section_pk)
        except Section.DoesNotExist:
            raise HttpError(404, 'Section not found')

        if not (
            section_obj.users.filter(pk=request.user.pk).exists() or
            section_obj.owner == request.user
        ):
            raise HttpError(403, 'Access denied')

        kwargs.update({'section': section_obj,})
        return super().__call__(request, section_pk, **kwargs)
