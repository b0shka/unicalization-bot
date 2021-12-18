from Variables.error_messages import ERROR_SERVER_MESSAGE
from aiogram import executor, types
from Variables.config import *
from Variables.text_messages import *
from Databases.database_sql import DatabaseSQL
from Requests.requests_bot import RequestsBot
from Requests.functions import FunctionsBot


db_sql = DatabaseSQL()
req_bot = RequestsBot()
func = FunctionsBot()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	try:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		unic = types.KeyboardButton('Уникализоровать')
		markup.add(unic)

		await message.answer(START_MESSAGE, reply_markup=markup)

		user = get_data_user(message)
		if user != 0:
			result_add = await db_sql.add_user(user)
			if result_add != 1:
				await func.send_programmer_error(result_add)
	except Exception as error:
		logger.error(error)
		await func.send_programmer_error(error)


@dp.message_handler(content_types=["photo"])
async def convet_photo(message: types.Message):
	await func.unicalization_photo(message)


@dp.message_handler(content_types=["video"])
async def convet_photo(message: types.Message):
	await func.unicalization_video(message)


@dp.message_handler(content_types=["text"])
async def answer_message(message: types.Message):
	try:
		search = message.text.lower()
		await req_bot.result_message(search, message)
			
		user = get_data_user(message)
		if user != 0:
			result_add = await db_sql.add_user(user)
			if result_add != 1:
				await func.send_programmer_error(result_add)
	except Exception as error:
		logger.error(error)
		await func.send_programmer_error(error)
	
    
def get_data_user(message):
	try:
		user = {
			'user_id': message.from_user.id,
			'username': message.from_user.username,
			'first_name': message.from_user.first_name,
			'last_name': message.from_user.last_name
		}

		return user
	except Exception as error:
		logger.error(error)
		return 0



if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)