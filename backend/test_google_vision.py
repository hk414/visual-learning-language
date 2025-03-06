from google.cloud import vision
from google.cloud.vision_v1 import types
import io

client = vision.ImageAnnotatorClient()

with io.open('images/tomato.jpg', 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)

if response.error.message:
    raise Exception(f"API call error: {response.error.message}")
