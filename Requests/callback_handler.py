from aiogram import types
from aiogram.dispatcher import FSMContext
from Requests.functions import FunctionsBot
from Variables.config import PROGRAMMER_ID, dp, logger, bot
from Variables.error_messages import *
from Variables.text_messages import *


func = FunctionsBot()


@dp.callback_query_handler(lambda call: True)
async def callback(call):
    try:
        user_id = call.from_user.id

        if 'choice' in call.data:            
            if call.data == 'choice_coins':
                await func.choice_coin(call.message)

            else:
                coin = call.data.split("_")[-1]
                await func.choosing_coin(user_id, coin, call.message)

        elif 'rate' in call.data:
            if call.data == 'rate':
                await func.parsing_rate(user_id, call.message)

    except Exception as error:
        await call.message.answer(ERROR_SERVER_MESSAGE)
        logger.error(error)
        await func.send_programmer_error(error)