import logging
from typing import Any

from django.utils.translation import gettext as _
from telebot import types
from telebot.types import Message
from section.models import Section
from telegram.handlers.bot_instance import bot
from telegram.handlers.utils import user_required
from telegram.utils import get_or_create_user


logger = logging.getLogger(__name__)

@user_required
def send_user_share(message: Message, section_id: int, **kwargs: dict[str, Any]) -> None:
    try:
        logger.debug(f'Find section {section_id} with owner_id={message.from_user.id}')
        section = Section.objects.get(id=section_id, owner_id=message.from_user.id)
    except Section.DoesNotExist:
        logger.debug(f'Section {section_id} does not exist')
        bot.send_message(
            message.from_user.id,
            _('You must be the owner of a room to add users to it'),
            reply_markup = types.ReplyKeyboardRemove(),
        )
        return


    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, is_persistent=False)
    keyboard.add(types.KeyboardButton(
        text=_('Add to room "%(section_name)s"') % {'section_name': section.name},
        request_user=types.KeyboardButtonRequestUsers(
            request_id=section.id,
            user_is_bot=False,
            max_quantity=min([10]),
            request_name=True,
            request_username=True,
            request_photo=True,
        )))
    bot.send_message(message.chat.id, _('Use the button below to add users to the room "%(section_name)s"') % {'section_name': section.name}, reply_markup=keyboard)
    logger.debug(f'Send message {message.from_user.id} with invite keyboard to section {section.id}')

@bot.message_handler(content_types=['users_shared'])
@user_required
def handle_user_shared(message: Message) -> None:
    try:
        logger.debug(f'Find section {message.users_shared.request_id} from users_shared.request_id')
        section = Section.objects.get(id=message.users_shared.request_id)
    except Section.DoesNotExist:
        bot.send_message(_('Room not found, users will not be added. Try again'))
        logger.debug(f'Section {message.users_shared.request_id} does not exist')
        return

    section.add_members([user for user, created in [
        get_or_create_user(
            user_id=user_data.user_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        for user_data in message.users_shared.users
    ]])

    bot.send_message(message.chat.id, _('Users added'), reply_markup=types.ReplyKeyboardRemove())
    logger.debug(f'Members added to section {message.users_shared.request_id}')