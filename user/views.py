from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from user.forms import FeedbackForm, UserLanguageForm


@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Сообщение доставлено')

    return redirect('index')


@login_required
def user_language(request):
    if request.method == 'POST':
        form = UserLanguageForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Язык сохранён")

    return redirect('index')
