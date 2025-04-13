from typing import Any

from django.core.files.base import ContentFile
from telebot.types import LabeledPrice, Message

from receipt.models import Receipt
from telegram.handlers.bot_instance import bot
from telegram.handlers.utils import user_required
from user.models import User


@bot.message_handler(content_types=['photo'])
@user_required
def get_photo(message: Message, user: User, **kwargs: dict[str, Any]) -> None:
    bot.send_message(message.chat.id, f'Hello')

    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f'receipt_{message.message_id}.jpg'

    receipt = Receipt(
        owner=user,
    )
    receipt.save()
    receipt.photo.save(file_name, ContentFile(downloaded_file))

    bot.reply_to(message, 'Фото успешно сохранено в базу!')