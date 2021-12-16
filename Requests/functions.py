import os
import cv2     
import skimage
from random import choice
from PIL import Image, ImageEnhance
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

            result_noise = await self.noise(path_img)

            #result_blur = await self.gaussianBlur(f'{name_img}_gaussian.{type_photo}')
            result_median = await self.medianBlur(f'{name_img}_gaussian.{type_photo}')

            #result_contrast = await self.change_contrast(f'{name_img}_gaussian_blur.{type_photo}')
            result_contrast = await self.change_contrast(f'{name_img}_gaussian_median.{type_photo}')

            photo = open(f'{name_img}_gaussian_median_contrast.{type_photo}', 'rb')
            await bot.send_photo(message.from_user.id, photo)

            os.remove(path_img)
            os.remove(f'{name_img}_gaussian.{type_photo}')
            #os.remove(f'{name_img}_gaussian_blur.{type_photo}')
            #os.remove(f'{name_img}_gaussian_blur_contrast.{type_photo}')
            os.remove(f'{name_img}_gaussian_median.{type_photo}')
            os.remove(f'{name_img}_gaussian_median_contrast.{type_photo}')
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


    async def noise(self, path):
        try:
            img = skimage.io.imread(path)
            img_name = path.split(".")[0]
            img_type = path.split(".")[1]

            gauss_noiseImg = skimage.util.random_noise(img, mode='gaussian', seed=None, clip=True)
            skimage.io.imsave(f'{img_name}_gaussian.{img_type}', gauss_noiseImg)

            #salt_noiseImg = skimage.util.random_noise(img, mode='salt', seed=None, clip=True)
            #skimage.io.imsave(f'{path.split(".")[0]}_salt.jpg', salt_noiseImg)
            return 1
        except Exception as error:
            logger.error(error)
            await self.send_programmer_error(error)
            return 0


    async def gaussianBlur(self, path):
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


    async def medianBlur(self, path):
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


    async def change_contrast(self, path):
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


    async def send_programmer_error(self, error):
        try:
            message_error = f"[ERROR] {error}"
            await bot.send_message(PROGRAMMER_ID, message_error)
            await bot.send_document(PROGRAMMER_ID, open(PATH_TO_LOGS, 'rb'))
        except Exception as error:
            logger.error(error)
