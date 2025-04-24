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


@bot.message_handler(content_types=['photo'])
@user_required
def get_photo(message: Message, user: User, **kwargs: dict[str, Any]) -> None:
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f'receipt_{photo.file_unique_id}.jpg'

    receipt = Receipt(
        owner=user,
        photo=ContentFile(downloaded_file, name=file_name),
    )
    receipt.save()

    notification_message = bot.send_photo(
        message.chat.id,
        caption=_('In line'),
        photo=message.photo[-1].file_id,
    )

    ReceiptStatusMessage.objects.create(
        receipt=receipt,
        message_id=notification_message.message_id,
        chat_id=notification_message.chat.id,
    )
    if notification_message:
        bot.delete_message(message.chat.id, message.message_id)
    receipt.save(do_analyze_photo=True)

def update_message(receipt_status: ReceiptStatusMessage, **kwargs: dict[str, Any]) -> None:
    with translation.override(receipt_status.receipt.owner.language_code):
        caption = None
        markup = None
        if receipt_status.status == Status.IN_PROGRESS:
            caption = _('In progress')
        elif receipt_status.status == Status.PROCESSED:
            caption = _('Analysis completed')
            markup = InlineKeyboardMarkup()
            markup.add(ButtonStorage.web_app_main())

        elif receipt_status.status == Status.ERROR:
            caption = _('Analysis error')

        if caption:
            try:
                bot.edit_message_caption(
                    caption=caption,
                    chat_id=receipt_status.chat_id,
                    message_id=receipt_status.message_id,
                    reply_markup=markup,
                )
            except Exception as ex:
                ...
