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

    except Exception as error:
        bot.send_message(call.from_user.id, ERROR_SERVER_MESSAGE)
        logger.error(error)
        func.send_programmer_error(error)