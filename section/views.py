from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch, Case, When, Value, IntegerField
from django.http import HttpResponse
from django.shortcuts import render

from subscription.models import Plan, PlanFeature
from user.forms import FeedbackForm, UserLanguageForm

@login_required
def index(request: WSGIRequest) -> HttpResponse:
    context = {
        'feedback_form': FeedbackForm(),
        'language_form': UserLanguageForm(instance=request.user),
        'plans': Plan.objects.filter(is_active=True).annotate(
            price_is_null=Case(
                When(price_stars__isnull=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by('price_is_null', 'price_stars'),
    }
    return render(request, 'section/index.html', context)
