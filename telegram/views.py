from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
import telebot

from telegram.bot import bot
from .utils import check_webapp_signature, get_or_create_user


def check(request: WSGIRequest) -> HttpResponse:
    return render(request, 'telegram/check.html')

def authenticate_web_app(request: WSGIRequest) -> HttpResponseRedirect:

    init_data = request.GET.get('init_data', '')
    is_valid, user_id = check_webapp_signature(init_data)
    if is_valid and user_id:
        user = get_or_create_user(user_id=user_id)
        login(request, user)
        return redirect('index')
    return redirect('403')

@csrf_exempt
def telegram_webhook(request: WSGIRequest) -> HttpResponse:
    if request.method == 'POST':
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return HttpResponse('ok')
    return HttpResponse('Only POST allowed', status=405)