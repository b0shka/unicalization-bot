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
def unicalizing_photo(message: types.Message):
	try:
		file_id = message.photo[-1].file_id
		func.unicalization_photo(message, file_id)

		result_add = db_sql.add_file_id(message.from_user.id, file_id)
		if result_add != 1:
			logger.error(result_add)
			func.send_programmer_error(result_add)
	except Exception as error:
		logger.error(error)
		func.send_programmer_error(error)


@bot.message_handler(content_types=["video"])
def unicalizing_video(message: types.Message):
	try:
		processing_video(message, message.video.file_id)
	except Exception as error:
		logger.error(error)
		func.send_programmer_error(error)


@bot.message_handler(content_types=['document'])
def unicalizing_document(message: types.Message):
	photo_name = ['jpeg', 'jpg', 'png']
	video_name = ['mp4', 'avi', 'mkv', 'MP4', 'wav']

	file_name = message.document.file_name.split('.')
	file_id = message.document.file_id

	if file_name[-1] in photo_name:
		func.unicalization_photo(message, file_id)

		result_add = db_sql.add_file_id(message.from_user.id, file_id)
		if result_add != 1:
			logger.error(result_add)
			func.send_programmer_error(result_add)
	elif file_name[-1] in video_name:
		processing_video(message, file_id)
	else:
		func.else_answer()


def processing_video(message, file_id):
	try:
		status_user = db_sql.check_status_using(message.from_user.id)

		if status_user == 0:
			result_add = db_sql.add_file_id(message.from_user.id, file_id)

			if result_add == 1:
				count_ = len(db_sql.get_users_using())
				result_change = db_sql.change_status_using(message.from_user.id, 1)

				if result_change == 1:
					bot.send_message(message.from_user.id, f"Ваше место в очереди: {count_+1}")
				else:
					bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
			else:
				bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
		elif status_user == 1:
			bot.send_message(message.from_user.id, "Вы уже стоите в очереди")
		else:
			bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
	except Exception as error:
		logger.error(error)
		func.send_programmer_error(error)


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
