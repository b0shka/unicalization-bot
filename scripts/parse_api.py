import os
from google.cloud import vision
from google.cloud.vision import types


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'token.json'

client = vision.ImageAnnotatorClient()
FILE_NAME = 'img.png'

with open(FILE_NAME, 'rb') as image_file:
    content = image_file.read()

image = vision.types.Image(content=content)
#response = client.