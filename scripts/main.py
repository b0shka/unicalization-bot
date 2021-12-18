import os
import cv2     
import skimage
import numpy as np
import moviepy.editor as moviepy
from PIL import Image, ImageEnhance
from pydub import AudioSegment
from pydub import effects
 
 
def clean_metadata_photo(filename):
	image_file = open(filename, mode="rb")
	image = Image.open(image_file)

	data = list(image.getdata())
	image_without_exif = Image.new(image.mode, image.size)
	image_without_exif.putdata(data)

	image_without_exif.save(filename)


def clean_metadata_video(filename):
	name_video = filename.split(".")[0]
	type_video = filename.split(".")[-1]

	#ffmpeg -y -i video.MP4 -c copy -map_metadata -1 -metadata title="Title" -metadata creation_time=2016-09-20T21:30:00 -map_chapters -1 "out.MP4"
	os.system(f"ffmpeg -y -i {filename} -map_metadata -1 -c:v copy -c:a copy {name_video}_clean.{type_video}")


def noise_photo(path):
	img = skimage.io.imread(path)

	gauss_noiseImg = skimage.util.random_noise(img, mode='gaussian', seed=None, clip=True)
	skimage.io.imsave(f'{path.split(".")[0]}_gaussian.jpg', gauss_noiseImg)

	#salt_noiseImg = skimage.util.random_noise(img, mode='salt', seed=None, clip=True)
	#skimage.io.imsave(f'{path.split(".")[0]}_salt.jpg', salt_noiseImg)


def gaussianBlur_photo(path):
	img = cv2.imread(path)

	blur = cv2.GaussianBlur(img, (3, 3), 0)
	cv2.imwrite(f'{path.split(".")[0]}_blur.jpg', blur)


def gaussianBlur_video(path):
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


def medianBlur_photo(path):
	img = cv2.imread(path)

	median = cv2.medianBlur(img.astype('float32'), 1)
	cv2.imwrite(f'{path.split(".")[0]}_median.jpg', median)


def medianBlur_video(path):
	name_audio = path.split(".")[0]
	type_video = path.split(".")[-1]

	cap = cv2.VideoCapture(path)
	frame_width = int(cap.get(3))
	frame_height = int(cap.get(4))
	out = cv2.VideoWriter(f'{name_audio}_blur.{type_video}', cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width, frame_height))

	while(cap.isOpened()):
		ret, frame = cap.read()
		if ret == True:
			frame = cv2.medianBlur(frame.astype('float32'), 1)
			out.write(frame)

		else:
			break

	cap.release()


def change_contrast_photo(img):
	im = Image.open(img)
	contrast = ImageEnhance.Contrast(im) # контрастность
	sharpness = ImageEnhance.Sharpness(im) # резкость
	brightness = ImageEnhance.Brightness(im) #яркость

	im_output = contrast.enhance(0.8) 
	#im_output = sharpness.enhance(0.05)
	im_output = brightness.enhance(0.8) 
	im_output.save(f'{img.split(".")[0]}_contrast.jpg') 


def speed_change(path):
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

	os.system(f"ffmpeg -y -i {name_audio}_blur.{type_video} -i {name_audio}_speed.mp3 -c copy video_speed.{type_video}")


def main():
	#img = 'img.jpg'
	#clean_metadata_photo(img)
	#noise_photo(img)

	#gaussianBlur_photo(f'{img.split(".")[0]}_gaussian.jpg')
	#medianBlur_photo(f'{img.split(".")[0]}_gaussian.jpg')

	#change_contrast_photo(f'{img.split(".")[0]}_gaussian_blur.jpg')
	#change_contrast_photo(f'{img.split(".")[0]}_gaussian_median.jpg')

	#os.remove('img_gaussian.jpg')
	#os.remove('img_gaussian_blur.jpg')
	#os.remove('img_gaussian_blur_contrast.jpg')
	#os.remove('img_gaussian_median.jpg')


	video = 'video.MP4'
	#clean_metadata_video(video)
	gaussianBlur_video(video)
	speed_change(video)

	#os.system("ffmpeg -i video_speed.MP4 -vf scale=640:360 movie_360p.MP4")
	#os.system("ffmpeg -i video_speed.MP4 -r 10 -pix_fmt yuv420p -vcodec libx264 -preset veryslow -profile:v baseline  -crf 23 -acodec aac -b:a 32k -strict -5 video_result.MP4")
	clip = moviepy.VideoFileClip("video_speed.MP4")
	clip.write_videofile("video_result.MP4")

	os.remove('video_blur.MP4')
	os.remove('video.wav')
	os.remove('video_speed.mp3')
	os.remove('video_speed.MP4')


if __name__ == "__main__":
	main()