from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from user.forms import FeedbackForm, UserLanguageForm


def index(request: WSGIRequest) -> HttpResponse:
    context = {
        'feedback_form': FeedbackForm(),
        'language_form': UserLanguageForm(instance=request.user),
    }
    return render(request, 'section/index.html', context)
