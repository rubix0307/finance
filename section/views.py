from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from user.forms import FeedbackForm


def index(request: WSGIRequest) -> HttpResponse:
    return render(request, 'section/index.html', {'feedback_form': FeedbackForm()})
