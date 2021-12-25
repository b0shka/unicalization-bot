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

        elif call.data == 'logs':
            if user_id == PROGRAMMER_ID:
                func.send_logs()
            else:
                bot.send_message(user_id, "Для вас эта функция ограничена")

    except Exception as error:
        bot.send_message(call.from_user.id, ERROR_SERVER_MESSAGE)
        logger.error(error)
        func.send_programmer_error(error)