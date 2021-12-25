from threading import Thread
from telebot import types
from Variables.error_messages import ERROR_SERVER_MESSAGE
from Variables.config import *
from Variables.text_messages import *
from Databases.database_sql import DatabaseSQL
from Requests.requests_bot import RequestsBot
from Requests.functions import FunctionsBot
from Requests.unicalizing import Unicalizing


db_sql = DatabaseSQL()
req_bot = RequestsBot()
func = FunctionsBot()
unic = Unicalizing()

unicalizing = Thread(target=unic.uncalizing)
unicalizing.start()

@bot.message_handler(commands=['start'])
def start(message: types.Message):
	try:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		unic = types.KeyboardButton('Уникализировать')
		markup.add(unic)

		bot.send_message(message.from_user.id, START_MESSAGE, reply_markup=markup)

		user = get_data_user(message)
		if user != 0:
			result_add = db_sql.add_user(user)
			if result_add != 1 and result_add != None:
				func.send_programmer_error(result_add)
	except Exception as error:
		logger.error(error)
		func.send_programmer_error(error)


@bot.message_handler(commands=['panel'])
def panel(message: types.Message):
	try:
		if message.from_user.id in admins:
			markup_inline = types.InlineKeyboardMarkup()
			statistic = types.InlineKeyboardButton(text = 'Статистика', callback_data = 'statistic')
			mailing = types.InlineKeyboardButton(text = 'Рассылка', callback_data = 'mailing')
			logs = types.InlineKeyboardButton(text = 'Скинуть logs', callback_data = 'logs')

			markup_inline.add(statistic)
			markup_inline.add(mailing)
			markup_inline.add(logs)
			bot.send_message(message.from_user.id, 'Админ панель', reply_markup=markup_inline)
		else:
			req_bot.result_message(message.text, message)

			user = get_data_user(message)
			if user != 0:
				result_add = db_sql.add_user(user)
				if result_add != 1 and result_add != None:
					func.send_programmer_error(result_add)
	except Exception as error:
		logger.error(error)
		func.send_programmer_error(error)


@bot.message_handler(content_types=["photo"])
def convet_photo(message: types.Message):
	bot.send_message(message.from_user.id, "Обработка фотографии началось")
	func.unicalization_photo(message)


@bot.message_handler(content_types=["video"])
def convet_photo(message: types.Message):
	status_user = db_sql.check_status_using(message.from_user.id)

	if status_user == 0:
		result_add = db_sql.add_file_id(message.from_user.id, message.video.file_id)

		if result_add == 1:
			count_ = len(db_sql.get_users_using())
			result_change = db_sql.change_status_using(message.from_user.id, 1)

			if result_change == 1:
				bot.send_message(message.from_user.id, f"Выше место в очереди: {count_+1}")
			else:
				bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
		else:
			bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
	elif status_user == 1:
		bot.send_message(message.from_user.id, "Вы уже стоите в очереди")
	else:
		bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)


@bot.message_handler(content_types=["text"])
def answer_message(message: types.Message):
	try:
		search = message.text.lower()
		req_bot.result_message(search, message)
			
		user = get_data_user(message)
		if user != 0:
			result_add = db_sql.add_user(user)
			if result_add != 1 and result_add != None:
				func.send_programmer_error(result_add)
	except Exception as error:
		logger.error(error)
		func.send_programmer_error(error)
	
    
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
	bot.polling(none_stop=True)
