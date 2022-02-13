import os
import cv2
import time
import skimage
import imageio
import numpy as np
import moviepy.editor as moviepy
from telebot import types
from random import choice
from PIL import Image, ImageEnhance
from pydub import AudioSegment, effects
from skimage.filters import gaussian
from skimage.util import random_noise
from skimage import img_as_ubyte
from Variables.config import *
from Variables.error_messages import *
from Variables.text_messages import *
from Databases.database_sql import DatabaseSQL


class FunctionsBot:

    def __init__(self):
        try:
            self.db_sql = DatabaseSQL()
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)


    def settings(self, user_id):
        try:
            markup_inline = types.InlineKeyboardMarkup()
            brightness_photo = types.InlineKeyboardButton(text = 'Яркость фотографии', callback_data = 'brightness_photo')
            brightness_video = types.InlineKeyboardButton(text = 'Яркость видео', callback_data = 'brightness_video')
            noise_photo = types.InlineKeyboardButton(text = 'Шум на фотографии', callback_data = 'noise_photo')
            get_settings = types.InlineKeyboardButton(text = 'Узнать свои настройки', callback_data = 'get_settings')
            throw_settings = types.InlineKeyboardButton(text = 'Сбросить к стандартным', callback_data = 'throw_settings')

            markup_inline.add(brightness_photo)
            markup_inline.add(brightness_video)
            markup_inline.add(noise_photo)
            markup_inline.add(get_settings)
            markup_inline.add(throw_settings)

            bot.send_message(user_id, 'Выберите, что настроить', reply_markup=markup_inline)
        except Exception as error:
            bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)


    def save_settings(self, user_id, param, column):
        try:
            result_save = self.db_sql.save_settings(user_id, param, column)

            if result_save == 1:
                bot.send_message(user_id, "Настройки успешно сохранены")
            else:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                logger.error(result_save)
                self.send_programmer_error(result_save)

            logger.info(f"Сохранение настроек {user_id}")
        except Exception as error:
            bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)


    def get_settings(self, user_id):
        try:
            list_settings = self.db_sql.get_all_settings(user_id)
            if list_settings == None:
                list_settings = self.db_sql.get_all_settings(user_id)
            
            if type(list_settings) == list and len(list_settings) == 1:
                list_settings = list_settings[0]
                
                if len(list_settings) != 0:
                    answer_messsage = GET_SETTINGS.replace(REPLACE_SYMBOLS_1, NAME_SETTINGS[list_settings[0]])
                    answer_messsage = answer_messsage.replace(REPLACE_SYMBOLS_2, NAME_SETTINGS[list_settings[1]])
                    answer_messsage = answer_messsage.replace(REPLACE_SYMBOLS_3, NAME_SETTINGS[list_settings[2]])
                    
                    bot.send_message(user_id, answer_messsage)
                else:
                    bot.send_message(user_id, "Данные в БД еще не успели сохраниться, попробуйте еще раз")
            else:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                logger.error(list_settings)
                self.send_programmer_error(list_settings)
                
            logger.info(f"Получение настроек {user_id}")
        except Exception as error:
            bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)


    def throw_settings(self, user_id):
        try:
            result_throw = self.db_sql.throw_settings(user_id)
            
            if result_throw == 1:
                bot.send_message(user_id, "Настройки успешно сброшены до стандартных")
            else:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                logger.error(result_throw)
                self.send_programmer_error(result_throw)
                
            logger.info(f"Сброс настроек {user_id}")
        except Exception as error:
            bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)


    def else_answer(self, user_id):
        try:
            bot.send_message(user_id, choice(CHOICE_TEXT))
        except Exception as error:
            bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)


    def unicalization_photo(self, message, file_id):
        try:
            bot.send_message(message.from_user.id, "Обработка фотографии началась")
            logger.info(f"Началась уникализация фото {message.from_user.id}")
            file_info = bot.get_file(file_id)
            file_size = file_info.file_size

            type_photo = file_info.file_path.split(".")[-1]
            name_img = f'{PATH_TO_BOT}/img/img_{message.from_user.id}'
            path_img = f'{name_img}.{type_photo}'

            downloaded_file = bot.download_file(file_info.file_path)
            with open(path_img, 'wb') as new_file:
                new_file.write(downloaded_file)
            logger.info(f"Скачивание фото {message.from_user.id}")

            if (file_size // 1048576) > 4:
                original_image = Image.open(path_img)
                width_img, height_img = original_image.size

                original_image.thumbnail((width_img * 0.6, height_img * 0.6), Image.ANTIALIAS)
                original_image.save(path_img)
                logger.info(f"Сжатие фото {message.from_user.id}")

            result_clean = self.clean_metadata_photo(path_img)
            logger.info(f"Удаление метаданных на фото {message.from_user.id}")
            if result_clean != 1:
                bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
                self.delete_photo(path_img, name_img, type_photo)
                return

            result_noise = self.noise_photo(path_img, message.from_user.id)
            logger.info(f"Добавление шума на фото {message.from_user.id}")
            if result_noise != 1:
                bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
                self.delete_photo(path_img, name_img, type_photo)
                return

            #result_blur = self.gaussianBlur_photo(f'{name_img}_noise.{type_photo}')
            result_blur = self.medianBlur_photo(f'{name_img}_noise.{type_photo}')
            logger.info(f"Добавление блюра на фото {message.from_user.id}")
            if result_blur != 1:
                bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
                self.delete_photo(path_img, name_img, type_photo)
                return

            result_contrast = self.change_contrast_photo(f'{name_img}_noise_blur.{type_photo}', message.from_user.id)
            logger.info(f"Изменение яркости на фото {message.from_user.id}")
            if result_contrast != 1:
                bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
                self.delete_photo(path_img, name_img, type_photo)
                return

            photo = open(f'{name_img}_noise_blur_contrast.{type_photo}', 'rb')
            bot.send_photo(message.from_user.id, photo)
            logger.info(f"Отправка обработанного фото {message.from_user.id}")

            self.delete_photo(path_img, name_img, type_photo)
            logger.info(f"Удаление не нужных фотографий {message.from_user.id}")
            
        except Exception as error:
            bot.send_message(message.from_user.id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)

    
    def delete_photo(self, path_img, name_img, type_photo):
        try:
            os.remove(path_img)
            os.remove(f'{name_img}_noise.{type_photo}')
            os.remove(f'{name_img}_noise_blur.{type_photo}')
            os.remove(f'{name_img}_noise_blur_contrast.{type_photo}')
        except:
            pass


    def unicalization_video(self, file_id, user_id):
        try:
            bot.send_message(user_id, "Обработка вашего видео началась")
            logger.info(f"Началась уникализация видео {user_id}")
            file_info = bot.get_file(file_id)

            type_video = file_info.file_path.split(".")[-1]
            name_video = f'{PATH_TO_BOT}/videos/video_{user_id}'
            path_video = f'{name_video}.{type_video}'

            downloaded_file = bot.download_file(file_info.file_path)
            with open(path_video, 'wb') as new_file:
                new_file.write(downloaded_file)
            logger.info(f"Скачивание видео {user_id}")

            size_video = os.path.getsize(path_video)

            result_resize = self.resizeVideo(path_video)
            logger.info(f"Изменение размера видео {user_id}")
            if result_resize != 1:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                self.delete_video(self, path_video, name_video, type_video)
                return

            result_clean = self.clean_metadata_video(path_video)
            logger.info(f"Удаление метаданных на видео {user_id}")
            if result_clean != 1:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                self.delete_video(self, path_video, name_video, type_video)
                return

            result_noise = self.noise_video(f'{name_video}_clean.{type_video}')
            logger.info(f"Добавление шума на видео {user_id}")
            if result_noise != 1:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                self.delete_video(self, path_video, name_video, type_video)
                return

            #clip = moviepy.VideoFileClip(f'{name_video}_clean_salt.{type_video}')
            #clip_blurred = clip.fl_image(self.gaussianBlur_video)
            #clip_blurred.write_videofile(f"{name_video}_clean_salt_blur.{type_video}")

            result_speed = self.speed_change_video(f'{name_video}_clean.{type_video}')
            logger.info(f"Ускорение аудио на видео {user_id}")
            if result_speed != 1:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                self.delete_video(self, path_video, name_video, type_video)
                return

            result_contrast = self.change_contrast_video(f'{name_video}_clean_speed.{type_video}', user_id)
            logger.info(f"Изменение яркости на видео {user_id}")
            if result_contrast != 1:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
                self.delete_video(self, path_video, name_video, type_video)
                return

            result_compression = self.compression_video(f"{name_video}_clean_speed_contrast.{type_video}", size_video)
            logger.info(f"Компрессия видео если она нужна {user_id}")
            
            if result_compression == 0:
                bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            elif result_compression == -1:
                with open(f'{name_video}_clean_speed_contrast.{type_video}', 'rb') as video:
                    bot.send_video(user_id, video)
            elif result_compression == 1:
                with open(f'{name_video}_result.{type_video}', 'rb') as video:
                    bot.send_video(user_id, video)

            self.delete_video(path_video, name_video, type_video)
            logger.info(f"Удаление не нужных видео {user_id}")

        except Exception as error:
            bot.send_message(user_id, ERROR_SERVER_MESSAGE)
            logger.error(error)
            self.send_programmer_error(error)


    def delete_video(self, path_video, name_video, type_video):
        try:
            os.remove(path_video)
            os.remove(f'{name_video}_clean.{type_video}')
            #os.remove(f'{name_video}_clean_salt.{type_video}')
            os.remove(f'{name_video}_clean_salt_blur.{type_video}')
            os.remove(f'{name_video}_clean_speed.{type_video}')
            os.remove(f'{name_video}_clean_speed_contrast.{type_video}')
            os.remove(f'{name_video}_clean.wav')
            os.remove(f'{name_video}_clean_speed.mp3')
            os.remove(f'{name_video}_result.{type_video}')
        except:
            pass


    def clean_metadata_photo(self, path):
        try:
            image_file = open(path, mode="rb")
            image = Image.open(image_file)

            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)

            image_without_exif.save(path)

            #image = Image.open(path)
            #image.save(path)

            return 1
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)
            return 0


    def clean_metadata_video(self, path):
        try:
            name_video = path.split(".")[0]
            type_video = path.split(".")[-1]
            os.system(f"ffmpeg -y -i {path} -map_metadata -1 -c:v copy -c:a copy {name_video}_clean.{type_video}")

            return 1
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def noise_photo(self, path, user_id):
        try:
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            param_noise = self.db_sql.get_settings(user_id, 'noise_photo')
            if param_noise == None:
                param_noise = DEFAULT_PARAM_NOISE_PHOTO
            else:
                param_noise = SETTINGS_PARAM[f'{param_noise}_noise_photo']

            image = imageio.imread(path)
            noise = np.random.poisson(param_noise, image.shape).astype(float)
            imageio.imwrite(f'{img_name}_noise.{img_type}', image + noise)

            #img = np.uint8(skimage.io.imread(path))

            #gauss_noiseImg = skimage.util.random_noise(img, mode='gaussian', seed=None, clip=True)
            #skimage.io.imsave(f'{img_name}_noise.{img_type}', img_as_ubyte(gauss_noiseImg))

            #salt_noiseImg = skimage.util.random_noise(img, mode='salt', seed=None, clip=True)
            #skimage.io.imsave(f'{img_name}_noise.{img_type}', img_as_ubyte(salt_noiseImg))
            return 1
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)
            return 0


    def noise_video(self, path):
        try:
            name_audio = path.split(".")[0]
            type_video = path.split(".")[-1]

            cap = cv2.VideoCapture(path)

            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 30

            output = cv2.VideoWriter(f'{name_audio}_salt_blur.{type_video}', fourcc, fps, (frame_width, frame_height))
            count_frame = 1

            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret == True:
                    if count_frame % 3 == 0:
                        s_vs_p = 0.5
                        amount = 0.002
                        out = np.copy(frame)
                        num_salt = np.ceil(amount * frame.size * s_vs_p)
                        coords = [np.random.randint(0, i - 1, int(num_salt))
                                for i in frame.shape]
                        out[tuple(coords)] = 1

                        num_pepper = np.ceil(amount * frame.size * (1. - s_vs_p))
                        coords = [np.random.randint(0, i - 1, int(num_pepper))
                                for i in frame.shape]
                        out[tuple(coords)] = 0
                        frame = out

                        #frame = random_noise(frame, mode='s&p', amount=0.011)
                        #frame = np.array(255 * frame, dtype=np.uint8)

                    frame = cv2.GaussianBlur(frame, (3, 3), 0)
                    output.write(frame)
                    count_frame += 1
                else:
                    break

            cap.release()
            return 1
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def medianBlur_photo(self, path):
        try:
            img = cv2.imread(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            median = cv2.medianBlur(img.astype('float32'), 1)
            cv2.imwrite(f'{img_name}_blur.{img_type}', median)

            return 1
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)
            return 0


    def gaussianBlur_photo(self, path):
        try:
            img = cv2.imread(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            blur = cv2.GaussianBlur(img, (3, 3), 0)
            cv2.imwrite(f'{img_name}_blur.{img_type}', blur)

            return 1
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)
            return 0


    def gaussianBlur_video(self, path):
        try:
            return gaussian(path.astype(float), sigma=2, truncate=1/4)
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def change_contrast_photo(self, path, user_id):
        try:
            img = Image.open(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            contrast = ImageEnhance.Contrast(img) # контрастность
            sharpness = ImageEnhance.Sharpness(img) # резкость
            brightness = ImageEnhance.Brightness(img) # яркость

            param_brightness = self.db_sql.get_settings(user_id, 'brightness_photo')
            if param_brightness == None:
                param_brightness = DEFAULT_PARAM_BRIGHTNESS_PHOTO
            else:
                param_brightness = SETTINGS_PARAM[f'{param_brightness}_brightness_photo']

            im_output = contrast.enhance(1.2) 
            #im_output = sharpness.enhance(0.05)
            im_output = brightness.enhance(param_brightness) 
            im_output.save(f'{img_name}_contrast.{img_type}')

            return 1
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)
            return 0


    def change_contrast_video(self, path, user_id):
        try:
            name_video = path.split(".")[0]
            type_video = path.split(".")[-1]

            contrast = 1.2
            gamma = 1.3
            saturation = 1

            param_brightness = self.db_sql.get_settings(user_id, 'brightness_video')
            if param_brightness == None:
                param_brightness = DEFAULT_PARAM_BRIGHTNESS_VIDEO
            else:
                if param_brightness == 'low':
                    gamma = 0.7
                elif param_brightness == 'high':
                    gamma = 1.6

                param_brightness = SETTINGS_PARAM[f'{param_brightness}_brightness_video']

            os.system(f"ffmpeg -i {path} -vf eq=contrast={contrast}:gamma={gamma}:brightness={param_brightness}:saturation={saturation} -c:a copy {name_video}_contrast.{type_video}")

            return 1
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def speed_change_video(self, path):
        try:
            name_audio = path.split(".")[0]
            type_video = path.split(".")[-1]
            os.system(f"ffmpeg -y -i {path} -ab 160k -ac 2 -ar 44100 -vn {name_audio}.wav")

            speed = 1.01
            sound = AudioSegment.from_wav(f'{name_audio}.wav')

            sound_speed = sound._spawn(sound.raw_data, overrides={
                    "frame_rate": int(sound.frame_rate * speed)
                })
            sound_speed = sound_speed.set_frame_rate(sound.frame_rate)
            sound_speed.export(f'{name_audio}_speed.mp3', format='mp3')

            #sound_speed = sound.speedup(speed, 150, 25)
            #sound_speed.export(f'{name_audio}_speed.mp3', format='mp3')

            os.system(f"ffmpeg -y -i {name_audio}_salt_blur.{type_video} -i {name_audio}_speed.mp3 -c copy {name_audio}_speed.{type_video}")

            return 1
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def resizeVideo(self, path):
        try:
            name_video = path.split(".")[0]
            type_video = path.split(".")[-1]

            cap = cv2.VideoCapture(path)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            
            if height > 720 or width > 1280:
                #clip = moviepy.VideoFileClip(path)
                #clip_resized = clip.resize(height=480)
                #clip_resized.write_videofile(f"{name_video}_480.{type_video}")

                os.system(f"ffmpeg -i {path} -vf scale=1280:720 {name_video}.{type_video}")
            return 1
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def compression_video(self, path, start_size):
        try:
            name_video = path.split(".")[0]
            type_video = path.split(".")[-1]
            size_video = os.path.getsize(path)

            if (size_video // start_size) >= 2:
                clip = moviepy.VideoFileClip(path)
                clip.write_videofile(f"{name_video}_result.{type_video}")
                return 1

            return -1
        except Exception as error:
            self.send_programmer_error(error)
            logger.error(error)
            return 0


    def statistic(self, user_id):
        try:
            count_users, count_used_users, count_used_today_users = self.db_sql.get_count_users()
            statistic_message = STATISTIC

            if count_users != None:
                statistic_message = statistic_message.replace(REPLACE_SYMBOLS_1, str(count_users[0]), 1)
            
            if count_used_users != None:
                statistic_message = statistic_message.replace(REPLACE_SYMBOLS_2, str(count_used_users[0]), 1)

            if count_used_today_users != None:
                statistic_message = statistic_message.replace(REPLACE_SYMBOLS_3, str(count_used_today_users[0]), 1)

            if count_users != None and count_used_users != None:
                statistic_message = statistic_message.replace(REPLACE_SYMBOLS_4, str(count_users[0] - count_used_users[0]), 1)
                
            bot.send_message(user_id, statistic_message)
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)


    def mailing(self, message, whom, user_id):
        try:
            message_text = message.text
            users = self.db_sql.get_id_users(whom)
            
            for user in users:
                try:
                    bot.send_message(user[0], message_text)
                    logger.info(f"Рассылка {user_id[0]}")
                except:
                    pass

            bot.send_message(user_id, f"Рассылка {len(users)} пользователям прошла успешно")
            logger.info(f"Рассылка {len(users)} пользователям прошла успешно")
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)


    def check_size_log(self):
        try:
            size_log = os.path.getsize(PATH_TO_LOGS) / 1024

            if size_log >= 1000:
                self.send_logs()
        except Exception as error:
            logger.error(error)
            self.send_programmer_error(error)


    def send_logs(self):
        try:
            bot.send_document(PROGRAMMER_ID, open(PATH_TO_LOGS, 'rb'))

            with open(PATH_TO_LOGS, 'w') as log:
                log.write("[INFO] Logs was send and clean\n")
        except Exception as error:
            logger.error(error)
            bot.send_message(PROGRAMMER_ID, error)


    def send_programmer_error(self, error):
        try:
            message_error = f"[ERROR] {error}"
            bot.send_message(PROGRAMMER_ID, message_error)
            bot.send_document(PROGRAMMER_ID, open(PATH_TO_LOGS, 'rb'))
        except Exception as error:
            logger.error(error)


    def uncalizing(self):
        try:
            while True:
                time.sleep(5)
                self.check_size_log()
                users = self.db_sql.get_users_using()
                
                if type(users) == list and len(users) > 0:
                    for user in users:
                        self.unicalization_video(user[6], user[1])
                        self.db_sql.change_status_using(user[1], 0)
        except Exception as error:
            logger.error(error)
            print(f"[ERROR] {error}")