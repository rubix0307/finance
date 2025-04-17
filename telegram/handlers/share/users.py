import logging

from telebot import types
from telebot.types import Message
from section.models import Section
from telegram.handlers.bot_instance import bot
from telegram.utils import get_or_create_user


logger = logging.getLogger(__name__)


def send_user_share(message: Message, section_id: int) -> None:
    try:
        logger.debug(f'Find section {section_id} with owner_id={message.from_user.id}')
        section = Section.objects.get(id=section_id, owner_id=message.from_user.id)
    except Section.DoesNotExist:
        logger.debug(f'Section {section_id} does not exist')
        bot.send_message(
            message.from_user.id,
            f'Вы должны быть владельцем комнаты, для добавления пользователей в нее',
            reply_markup = types.ReplyKeyboardRemove(),
        )
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, is_persistent=False)
    keyboard.add(types.KeyboardButton(
        text=f'Добавить в {section.name}',
        request_user=types.KeyboardButtonRequestUsers(
            request_id=section.id,
            user_is_bot=False,
            max_quantity=min([10]),
            request_name=True,
            request_username=True,
            request_photo=True,
        )))

    bot.send_message(message.chat.id, f'Используйте кнопку ниже, что б добавить пользователей в комнату "{section.name}"', reply_markup=keyboard)
    logger.debug(f'Send message {message.from_user.id} with invite keyboard to section {section.id}')

@bot.message_handler(content_types=['users_shared'])
def handle_user_shared(message: Message) -> None:
    try:
        logger.debug(f'Find section {message.users_shared.request_id} from users_shared.request_id')
        section = Section.objects.get(id=message.users_shared.request_id)
    except Section.DoesNotExist:
        bot.send_message('Комната не найдена, пользователи не будут добавлены. Попробуйте еще раз')
        logger.debug(f'Section {message.users_shared.request_id} does not exist')
        return

    section.add_members([
        get_or_create_user(
            user_id=user_data.user_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        for user_data in message.users_shared.users
    ])

    bot.send_message(message.chat.id, f'Пользователи добавлены', reply_markup=types.ReplyKeyboardRemove())
    logger.debug(f'Members added to section {message.users_shared.request_id}')