from typing import Any

from django.core.files.base import ContentFile
from django.utils import translation
from django.utils.translation import gettext as _
from telebot.types import LabeledPrice, Message, InlineKeyboardMarkup

from receipt.models import Receipt
from telegram.handlers.bot_instance import bot
from telegram.handlers.common import ButtonStorage
from telegram.handlers.utils import user_required
from telegram.models import ReceiptStatusMessage, Status
from user.models import User


@bot.message_handler(content_types=['text'])
@user_required
def get_expenses(message: Message, user: User, **kwargs: dict[str, Any]) -> None:
    receipt = Receipt(
        owner=user,
        input_text=message.text,
    )
    receipt.save()
    status_text = _('In line')
    notification_message = bot.send_message(
        message.chat.id,
        text='\n'.join(filter(None, [message.text, '-———'*5, status_text])),
    )

    ReceiptStatusMessage.objects.create(
        receipt=receipt,
        message_id=notification_message.message_id,
        chat_id=notification_message.chat.id,
    )
    if notification_message:
        bot.delete_message(message.chat.id, message.message_id)
    receipt.save(do_analyze_input_text=True)