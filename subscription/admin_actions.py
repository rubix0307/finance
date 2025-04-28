from django.conf import settings
from django.contrib import admin, messages
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import get_language, activate, gettext_lazy as _
from parler.utils.context import switch_language
from telebot.types import LabeledPrice

from .models import Plan
from telegram.handlers.bot_instance import bot


@admin.action(description=_('Create payment links for selected tariffs in all languages (atomically)'))
def create_invoice_links(modeladmin: admin.ModelAdmin, request: WSGIRequest, queryset: QuerySet[Plan]) -> None:
    original_lang = get_language()

    try:
        with transaction.atomic():
            for plan in queryset:
                for lang_code, _ in settings.LANGUAGES:
                    with switch_language(plan, lang_code):
                        title = plan.title

                        link = bot.create_invoice_link(
                            title=title,
                            description=f'-{plan.description}',
                            payload=f'plan_{plan.slug}',
                            provider_token='',
                            currency='XTR',
                            prices=[LabeledPrice(label=title, amount=plan.price_stars)],
                            subscription_period=30*24*60*60,
                        )
                        plan.link = link
                        plan.save()

        modeladmin.message_user(
            request,
            _('Payment links for all selected plans in all languages have been created successfully'),
            level=messages.SUCCESS
        )
    except Exception as e:
        modeladmin.message_user(
            request,
            _('Error creating links: ') + f'{e}',
            level=messages.ERROR
        )
    finally:
        activate(original_lang)