from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import openai
from google.cloud import vision
import io
import os
from PIL import Image
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

client = vision.ImageAnnotatorClient()

def detect_text_from_image(image_path):
    """Detects text in the image file."""
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        print("Detected text:")
        print(texts[0].description)  
    else:
        print("No text detected.")

    if response.error.message:
        raise Exception(f"Error: {response.error.message}")

image_path = "./images/receipt-ocr-original.jpg"
detect_text_from_image(image_path)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)