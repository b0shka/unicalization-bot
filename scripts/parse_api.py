import os
import io
from google.cloud import vision


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.curdir, 'account.json')
FILE_NAME = 'img.jpg'
client = vision.ImageAnnotatorClient()

with io.open(FILE_NAME, 'rb') as image:
    content = image.read()

image = vision.Image(content = content)
response = client.label_detection(image=image)

for label in response.label_annotations:
    print(label.description, '(%.2f%%)' % (label.score*100.))