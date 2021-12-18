import os
import cv2     
import skimage
from random import choice
from PIL import Image, ImageEnhance
from pydub import AudioSegment, effects
import numpy as np
import moviepy.editor as moviepy
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


    async def else_answer(self, message):
        try:
            choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
            await message.answer(choice(choice_text))
        except Exception as error:
            await message.answer(ERROR_SERVER_MESSAGE)
            logger.error(error)
            await self.send_programmer_error(error)


    async def unicalization_photo(self, message):
        try:
            file_info = await bot.get_file(message.photo[-1].file_id)

            type_photo = file_info['file_path'].split(".")[-1]
            name_img = f'{PATH_TO_BOT}/img/img_{message.from_user.id}'
            path_img = f'{name_img}.{type_photo}'

            await bot.download_file(file_info.file_path, path_img)

            result_clean = await self.clean_metadata_photo(path_img)
            if result_clean != 1:
                await self.send_programmer_error(result_clean)

            result_noise = await self.noise_photo(path_img)
            if result_noise != 1:
                await self.send_programmer_error(result_noise)

            #result_blur = await self.gaussianBlur_photo(f'{name_img}_gaussian.{type_photo}')
            #result_median = await self.medianBlur_photo(f'{name_img}_gaussian.{type_photo}')
            result_blur = await self.gaussianBlur_photo(f'{name_img}_salt.{type_photo}')
            if result_blur != 1:
                await self.send_programmer_error(result_blur)

            #result_contrast = await self.change_contrast_photo(f'{name_img}_gaussian_blur.{type_photo}')
            #result_contrast = await self.change_contrast_photo(f'{name_img}_gaussian_median.{type_photo}')
            result_contrast = await self.change_contrast_photo(f'{name_img}_salt_blur.{type_photo}')
            if result_contrast != 1:
                await self.send_programmer_error(result_contrast)

            #photo = open(f'{name_img}_gaussian_blur_contrast.{type_photo}', 'rb')
            #photo = open(f'{name_img}_gaussian_median_contrast.{type_photo}', 'rb')
            photo = open(f'{name_img}_salt_blur_contrast.{type_photo}', 'rb')
            await bot.send_photo(message.from_user.id, photo)

            os.remove(path_img)
            #os.remove(f'{name_img}_gaussian.{type_photo}')
            os.remove(f'{name_img}_salt.{type_photo}')

            #os.remove(f'{name_img}_gaussian_blur.{type_photo}')
            #os.remove(f'{name_img}_gaussian_blur_contrast.{type_photo}')

            #os.remove(f'{name_img}_gaussian_median.{type_photo}')
            #os.remove(f'{name_img}_gaussian_median_contrast.{type_photo}')

            os.remove(f'{name_img}_salt_blur.{type_photo}')
            os.remove(f'{name_img}_salt_blur_contrast.{type_photo}')
        except Exception as error:
            await message.answer(ERROR_SERVER_MESSAGE)
            logger.error(error)
            await self.send_programmer_error(error)


    async def unicalization_video(self, message):
        try:
            file_info = await bot.get_file(message.video.file_id)

            type_video = file_info['file_path'].split(".")[-1]
            name_video = f'{PATH_TO_BOT}/videos/video_{message.from_user.id}'
            path_video = f'{name_video}.{type_video}'

            await bot.download_file(file_info.file_path, path_video)

            result_clean = await self.clean_metadata_video(path_video)
            if result_clean != 1:
                await self.send_programmer_error(result_clean)

            result_blur = await self.gaussianBlur_video(f'{name_video}_clean.{type_video}')
            if result_blur != 1:
                await self.send_programmer_error(result_blur)

            result_speed = await self.speed_change(f'{name_video}_clean.{type_video}')
            if result_speed != 1:
                await self.send_programmer_error(result_speed)

            clip = moviepy.VideoFileClip(f"{name_video}_clean_speed.{type_video}")
            clip.write_videofile(f"{name_video}_result.{type_video}")

            with open(f'{name_video}_result.{type_video}', 'rb') as video:
                await message.answer_video(video)

            os.remove(path_video)
            os.remove(f'{name_video}_clean.{type_video}')
            os.remove(f'{name_video}_clean_blur.{type_video}')
            os.remove(f'{name_video}_clean_speed.{type_video}')
            os.remove(f'{name_video}_clean.wav')
            os.remove(f'{name_video}_clean_speed.mp3')
            os.remove(f'{name_video}_result.{type_video}')
        except Exception as error:
            await message.answer(ERROR_SERVER_MESSAGE)
            logger.error(error)
            await self.send_programmer_error(error)


    async def clean_metadata_photo(self, path):
        try:
            image_file = open(path, mode="rb")
            image = Image.open(image_file)

            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)

            image_without_exif.save(path)

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def clean_metadata_video(self, path):
        try:
            name_video = path.split(".")[0]
            type_video = path.split(".")[-1]
            os.system(f"ffmpeg -y -i {path} -map_metadata -1 -c:v copy -c:a copy {name_video}_clean.{type_video}")

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def noise_photo(self, path):
        try:
            img = skimage.io.imread(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            #gauss_noiseImg = skimage.util.random_noise(img, mode='gaussian', seed=None, clip=True)
            #skimage.io.imsave(f'{img_name}_gaussian.{img_type}', gauss_noiseImg)

            salt_noiseImg = skimage.util.random_noise(img, mode='salt', seed=None, clip=True)
            skimage.io.imsave(f'{img_name}_salt.{img_type}', salt_noiseImg)
            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def gaussianBlur_photo(self, path):
        try:
            img = cv2.imread(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            blur = cv2.GaussianBlur(img, (3, 3), 0)
            cv2.imwrite(f'{img_name}_blur.{img_type}', blur)

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def gaussianBlur_video(self, path):
        try:
            name_audio = path.split(".")[0]
            type_video = path.split(".")[-1]

            contrast = 0.8
            brightness = 0.8

            cap = cv2.VideoCapture(path)
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            output = cv2.VideoWriter(f'{name_audio}_blur.{type_video}', cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width, frame_height))

            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret == True:
                    s_vs_p = 0.5
                    amount = 0.004
                    out = np.copy(frame)
                    num_salt = np.ceil(amount * frame.size * s_vs_p)
                    coords = [np.random.randint(0, i - 1, int(num_salt))
                            for i in frame.shape]
                    out[coords] = 1

                    num_pepper = np.ceil(amount* frame.size * (1. - s_vs_p))
                    coords = [np.random.randint(0, i - 1, int(num_pepper))
                            for i in frame.shape]
                    out[coords] = 0

                    frame = cv2.GaussianBlur(out, (3, 3), 0)

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    frame[:,:,2] = np.clip(contrast * frame[:,:,2] + brightness, 0, 255)
                    frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

                    output.write(frame)

                else:
                    break

            cap.release()

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def medianBlur_photo(self, path):
        try:
            img = cv2.imread(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            median = cv2.medianBlur(img.astype('float32'), 1)
            cv2.imwrite(f'{img_name}_median.{img_type}', median)

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def change_contrast_photo(self, path):
        try:
            img = Image.open(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            contrast = ImageEnhance.Contrast(img) # контрастность
            sharpness = ImageEnhance.Sharpness(img) # резкость
            brightness = ImageEnhance.Brightness(img) #яркость

            im_output = contrast.enhance(0.8) 
            #im_output = sharpness.enhance(0.05)
            im_output = brightness.enhance(0.8) 
            im_output.save(f'{img_name}_contrast.{img_type}') 

            #im_output = contrast.enhance(1.2) 
            #im_output = sharpness.enhance(0.05)
            #im_output = brightness.enhance(1.2) 
            #im_output.save(f'{img.split(".")[0]}_contrast_2.jpg')

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def speed_change(self, path):
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

            os.system(f"ffmpeg -y -i {name_audio}_blur.{type_video} -i {name_audio}_speed.mp3 -c copy {name_audio}_speed.{type_video}")

            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def send_programmer_error(self, error):
        try:
            message_error = f"[ERROR] {error}"
            await bot.send_message(PROGRAMMER_ID, message_error)
            await bot.send_document(PROGRAMMER_ID, open(PATH_TO_LOGS, 'rb'))
        except Exception as error:
            logger.error(error)
