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

        if "brightness" in call.data or "noise" in call.data:
            if call.data == 'brightness_photo':
                markup_inline = types.InlineKeyboardMarkup()
                low = types.InlineKeyboardButton(text = 'Низкая', callback_data = 'low_brightness_photo')
                middle = types.InlineKeyboardButton(text = 'Средняя (по умолчанию)', callback_data = 'middle_brightness_photo')
                high = types.InlineKeyboardButton(text = 'Высокая', callback_data = 'high_brightness_photo')

                markup_inline.add(low)
                markup_inline.add(middle)
                markup_inline.add(high)

                bot.send_message(user_id, 'Выберите настройку', reply_markup=markup_inline)

            elif call.data == 'brightness_video':
                markup_inline = types.InlineKeyboardMarkup()
                low = types.InlineKeyboardButton(text = 'Низкая', callback_data = 'low_brightness_video')
                middle = types.InlineKeyboardButton(text = 'Средняя (по умолчанию)', callback_data = 'middle_brightness_video')
                high = types.InlineKeyboardButton(text = 'Высокая', callback_data = 'high_brightness_video')

                markup_inline.add(low)
                markup_inline.add(middle)
                markup_inline.add(high)

                bot.send_message(user_id, 'Выберите настройку', reply_markup=markup_inline)

            elif call.data == 'noise_photo':
                markup_inline = types.InlineKeyboardMarkup()
                little = types.InlineKeyboardButton(text = 'Маленький', callback_data = 'little_noise_photo')
                middle = types.InlineKeyboardButton(text = 'Средний (по умолчанию)', callback_data = 'middle_noise_photo')
                big = types.InlineKeyboardButton(text = 'Большой', callback_data = 'big_noise_photo')

                markup_inline.add(little)
                markup_inline.add(middle)
                markup_inline.add(big)

                bot.send_message(user_id, 'Выберите настройку', reply_markup=markup_inline)

            else:
                param, characteristic, type_file = call.data.split("_")
                func.save_settings(user_id, param, f'{characteristic}_{type_file}')

        elif call.data == 'get_settings':
            func.get_settings(user_id)

        elif call.data == 'throw_settings':
            func.throw_settings(user_id)

        elif call.data == 'statistic':
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