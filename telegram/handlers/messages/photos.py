from typing import Any

from django.core.files.base import ContentFile
from django.utils import translation
from django.utils.translation import gettext as _
from telebot.types import LabeledPrice, Message, InlineKeyboardMarkup

from receipt.models import Receipt
from telegram.handlers.bot_instance import bot
from telegram.handlers.common import ButtonStorage
from telegram.handlers.utils import user_required, feature_required
from telegram.models import ReceiptStatusMessage, Status
from user.models import User


@bot.message_handler(content_types=['photo'])
@user_required
@feature_required('analyze_photo')
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
        status_text = None
        markup = None
        input_text = receipt_status.receipt.input_text or ''
        if receipt_status.status == Status.IN_PROGRESS:
            status_text = _('In progress')
        elif receipt_status.status == Status.PROCESSED:
            status_text = _('Analysis completed')
            markup = InlineKeyboardMarkup()
            markup.add(ButtonStorage.web_app_main())

        elif receipt_status.status == Status.ERROR:
            status_text = _('Analysis error')

        if status_text:
            try:
                send_data = {
                    'chat_id': receipt_status.chat_id,
                    'message_id': receipt_status.message_id,
                    'reply_markup': markup,
                }

                if receipt_status.receipt.input_text:
                    bot.edit_message_text(
                        text='\n'.join(filter(None, [input_text, '-———'*3, status_text])),
                        **send_data,
                    )
                else:
                    bot.edit_message_caption(
                        caption='\n'.join(filter(None, [input_text, status_text])),
                        **send_data,
                    )

            except Exception as ex:
                ...
