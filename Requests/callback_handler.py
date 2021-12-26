from telebot import types
from Requests.functions import FunctionsBot
from Variables.config import PROGRAMMER_ID, logger, bot
from Variables.error_messages import *
from Variables.text_messages import *


func = FunctionsBot()


@bot.callback_query_handler(lambda call: True)
def answer(call):
    try:
        user_id = call.from_user.id

        if 'statistic' in call.data:
            func.statistic(user_id)

        elif "mailing" in call.data:
            bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

            if call.data == "mailing":
                markup_inline = types.InlineKeyboardMarkup()

                all_users = types.InlineKeyboardButton(text='Всем пользователям', callback_data = 'mailing_all_users')

                markup_inline.add(all_users)
                bot.send_message(user_id, 'Выберите кому делать рассылку', reply_markup=markup_inline)

            else:
                text_message = bot.send_message(user_id, 'Введите сообщение для рассылки')
                bot.register_next_step_handler(text_message, func.mailing, call.data, user_id)

        elif call.data == 'logs':
            if user_id == PROGRAMMER_ID:
                func.send_logs()
            else:
                bot.send_message(user_id, "Для вас эта функция ограничена")

    except Exception as error:
        bot.send_message(call.from_user.id, ERROR_SERVER_MESSAGE)
        logger.error(error)
        func.send_programmer_error(error)