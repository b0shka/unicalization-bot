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

    async def result_message(self, search, message):
        try:
            if search == "уникализоровать":
                pass

            else:
                await self.func_bot.else_answer(message)

        except Exception as error:
            await message.answer(ERROR_SERVER_MESSAGE)
            logger.error(error)
            await self.func_bot.send_programmer_error(error)