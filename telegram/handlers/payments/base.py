import time
from datetime import datetime
from typing import Any

from telebot.types import PreCheckoutQuery, SuccessfulPayment, Message

from subscription.models import Plan, Subscription
from telegram.handlers.bot_instance import bot
from telegram.handlers.utils import user_required
from telegram.models import Payment, PreCheckoutLog
from django.utils.translation import gettext as _

from user.models import User


@bot.pre_checkout_query_handler(func=lambda q: True)
@user_required
def process_pre_checkout_query(query: PreCheckoutQuery, **kwargs: dict[str, Any]) -> None:
    status = False
    error_message = None
    try:
        if not ':' in query.invoice_payload:
            raise ValueError()

        i_type, payload_detail = query.invoice_payload.split(':', maxsplit=1)
        pre_checkout_log = PreCheckoutLog.objects.create(
            currency=query.currency,
            user_id=query.from_user.id,
            pre_checkout_query_id=query.id,
            invoice_payload=query.invoice_payload,
            total_amount=query.total_amount,
        )
        status = Plan.objects.filter(
            slug=payload_detail,
            price_stars=query.total_amount,
            is_active=True,
        ).exists()
    except Exception as e:
        error_message = _('The specified tariff plan was not found.')
    finally:
        bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=status,
            error_message=error_message,
        )


@bot.message_handler(content_types=['successful_payment'])
@user_required
def payment_handler(query: Message, user: User, **kwargs: dict[str, Any]):
    payment = query.successful_payment
    Payment.objects.create(
        currency=payment.currency,
        invoice_payload=payment.invoice_payload,
        is_first_recurring=payment.is_first_recurring,
        is_recurring=payment.is_recurring,
        provider_payment_charge_id=payment.provider_payment_charge_id,
        subscription_expiration_date=payment.subscription_expiration_date,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        total_amount=payment.total_amount,
        user_id=user.id,
        chat_id=query.chat.id,
    )
    i_type, payload_detail = payment.invoice_payload.split(':', maxsplit=1)
    plan = Plan.objects.get(
        slug=payload_detail,
        price_stars=payment.total_amount,
    )
    Subscription.objects.create(
        user=user,
        plan=plan,
        started_at=datetime.fromtimestamp(time.time()),
        expires_at=datetime.fromtimestamp(payment.subscription_expiration_date),
    )

    bot.send_message(query.chat.id, _('Subscription successfully completed'))


