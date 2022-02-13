from Requests.functions import FunctionsBot
from Variables.config import logger
from Variables.error_messages import ERROR_SERVER_MESSAGE
from Variables.text_messages import *
from Requests.callback_handler import *


class RequestsBot:

    def __init__(self):
        try:
            self.func_bot = FunctionsBot()
        except Exception as error:
            logger.error(error)

    def result_message(self, search, message):
        try:
            if search == "уникализировать":
                bot.send_message(message.from_user.id, UNOCALIZATION)

            elif search == "информация":
                bot.send_message(message.from_user.id, INFORMATION, disable_web_page_preview=True)

            elif search == "настройки":
                self.func_bot.settings(message.from_user.id)

            else:
                self.func_bot.else_answer(message.from_user.id)

        except Exception as error:
            bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.func_bot.send_programmer_error(error)