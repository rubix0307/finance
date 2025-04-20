from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import translation
from django.conf import settings


def permission_denied_view(request: WSGIRequest) -> HttpResponse:
    return render(request, '403.html', status=403)


def set_language_custom(request):
    lang = request.POST.get('language')
    next_url = request.POST.get('next', '/')
    if lang and lang in dict(settings.LANGUAGES):
        # Подхватываем язык и включаем его для текущего запроса
        translation.activate(lang)

        # Сохраняем его в сессии (если есть)
        if hasattr(request, 'session'):
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang

        # Делаем редирект и ставим куку
        response = redirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        response['Content-Language'] = lang
        return response

    return redirect(next_url)