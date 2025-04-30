from typing import Any

from telebot.types import Message

from telegram.handlers.bot_instance import bot
from telegram.handlers.utils import user_required
from django.utils.translation import gettext as _
from user.models import User


@user_required
def default_forbidden(message: Message, user: User, **kwargs: dict[str, Any]) -> None:
    bot.reply_to(
        message,
        _('You can\'t perform this action, please check your subscription limits and capabilities')
    )