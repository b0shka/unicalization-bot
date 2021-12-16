import os
import cv2     
import skimage
from PIL import Image, ImageEnhance
 
 
def gaussianBlur(path):
	img = cv2.imread(path)

	blur = cv2.GaussianBlur(img, (3, 3), 0)
	cv2.imwrite(f'{path.split(".")[0]}_blur.jpg', blur)


def medianBlur(path):
	img = cv2.imread(path)

	median = cv2.medianBlur(img.astype('float32'), 1)
	cv2.imwrite(f'{path.split(".")[0]}_median.jpg', median)

 
def noise(path):
	img = skimage.io.imread(path)

	gauss_noiseImg = skimage.util.random_noise(img, mode='gaussian', seed=None, clip=True)
	skimage.io.imsave(f'{path.split(".")[0]}_gaussian.jpg', gauss_noiseImg)

	#salt_noiseImg = skimage.util.random_noise(img, mode='salt', seed=None, clip=True)
	#skimage.io.imsave(f'{path.split(".")[0]}_salt.jpg', salt_noiseImg)


def clean_metadata_photo(filename):
	image_file = open(filename, mode="rb")
	image = Image.open(image_file)

	data = list(image.getdata())
	image_without_exif = Image.new(image.mode, image.size)
	image_without_exif.putdata(data)

	image_without_exif.save(filename)


def clean_metadata_video(filename):
	#os.system("ffmpeg -i video.mp4 img/image%d.jpg")

	for img in os.listdir("img/"):
		clean_metadata_photo(f"img/{img}")

	os.system("ffmpeg -f image2 -i img/image%d.jpg video.mpg")


def change_contrast(img):
	im = Image.open(img)
	contrast = ImageEnhance.Contrast(im) # контрастность
	sharpness = ImageEnhance.Sharpness(im) # резкость
	brightness = ImageEnhance.Brightness(im) #яркость

	im_output = contrast.enhance(0.8) 
	#im_output = sharpness.enhance(0.05)
	im_output = brightness.enhance(0.8) 
	im_output.save(f'{img.split(".")[0]}_contrast.jpg') 

	#im_output = contrast.enhance(1.2) 
	#im_output = sharpness.enhance(0.05)
	#im_output = brightness.enhance(1.2) 
	#im_output.save(f'{img.split(".")[0]}_contrast_2.jpg')


def main():
	img = 'img.jpg'

	clean_metadata_photo(img)
	#clean_metadata_video('video.mp4')

	noise(img)

	#gaussianBlur(f'{img.split(".")[0]}_gaussian.jpg')
	medianBlur(f'{img.split(".")[0]}_gaussian.jpg')
	#gaussianBlur(f'{img.split(".")[0]}_salt.jpg')

	#change_contrast(f'{img.split(".")[0]}_gaussian_blur.jpg')
	change_contrast(f'{img.split(".")[0]}_gaussian_median.jpg')

	os.remove('img_gaussian.jpg')
	#os.remove('img_gaussian_blur.jpg')
	#os.remove('img_gaussian_blur_contrast.jpg')
	os.remove('img_gaussian_median.jpg')
	


if __name__ == "__main__":
	main()