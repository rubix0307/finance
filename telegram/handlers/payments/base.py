from telegram.handlers.bot_instance import bot


@bot.pre_checkout_query_handler(func=lambda q: True)
def process_pre_checkout_query(query):
    bot.answer_pre_checkout_query(query.id, ok=False)


@bot.message_handler(content_types=['successful_payment'])
def payment_handler(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, '✅ Подписка успешно оформлена! Спасибо!')
