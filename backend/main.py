import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from google.cloud import texttospeech, vision, storage
import openai
from moviepy import VideoFileClip, AudioFileClip
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from io import BytesIO
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
bucket_name = os.getenv("BUCKET_NAME")

openai.api_key = OPENAI_API_KEY

vision_client = vision.ImageAnnotatorClient()
text_to_speech_client = texttospeech.TextToSpeechClient()
storage_client = storage.Client()

def detect_image(image_path):
    """Detects object in the image file."""
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = vision_client.object_localization(image=image)
    objects = response.localized_object_annotations

    if response.error.message:
        raise Exception(f"Error: {response.error.message}")
    
    return objects[0].name if objects else "Unknown"


def generate_situation(word, language='Mandarin'):
    """Generates a short situation where the word is used."""
    prompt = f"Create at most 8 words sentence where someone would use the word '{word}' in a situation. The situation should be in {language}. Only provide the situation in the language {language} given, no additional information or context."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    situation = response["choices"][0]["message"]["content"].strip()
    return situation


def generate_audio(text, language_code='zh-CN'):
    """Converts text to speech using Google Cloud Text-to-Speech."""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = text_to_speech_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    audio_path = f"learning_audio.mp3"
    with open(audio_path, "wb") as out:
        out.write(response.audio_content)
    
    return audio_path


def create_text_image(text, font_path="font.otf", image_size=(800, 600)):
    """Create an image with the text."""
    image = Image.new("RGB", image_size, color="black")
    font_size=30
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)

    draw.text(position, text, fill="white", font=font)
    
    return np.array(image)


def create_background_image(image_path="background.jpg", size=(800, 600)):
    """Create a background image for the situation (optional)."""
    background = cv2.imread(image_path)
    background = cv2.resize(background, size)
    return background


def generate_video(text, audio_path, background_image_path="background.jpg"):
    """Generates a video from text and audio."""
    background_image = create_background_image(background_image_path)
    text_image = create_text_image(text)

    video_frame = cv2.addWeighted(background_image, 0.7, text_image, 0.3, 0)

    video_path = "learning_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_path, fourcc, 24, (800, 600))

    for _ in range(100):
        video_writer.write(video_frame)

    video_writer.release()

    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    video_clip = video_clip.with_duration(audio_clip.duration)
    video_with_audio = video_clip.with_audio(audio_clip)

    final_video_path = f"{background_image_path.split('.')[0]}_video.mp4"
    final_video_path = final_video_path.replace("images/", "")

    video_with_audio.write_videofile(final_video_path, codec='libx264')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"videos/{final_video_path}")

    blob.upload_from_filename(final_video_path)
    blob.make_public()

    return blob.public_url


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/generate")
async def generate_video_route(language: str = Form('Mandarin'), image: UploadFile = File(...)):
    if not allowed_file(image.filename):
        return {"error": "Invalid image format. Only jpg, jpeg, and png are allowed."}, 400

    filename = secure_filename(image.filename)
    image_path = os.path.join("images", filename)
    
    image_data = await image.read()
    with open(image_path, 'wb') as f:
        f.write(image_data)

    word_to_learn = detect_image(image_path)
    situation_text = generate_situation(word_to_learn, language)
    audio_file = generate_audio(situation_text, language_code='zh-CN')

    video_file = generate_video(situation_text, audio_file, background_image_path=image_path)

    print("Video generated successfully! URL:", video_file)

    return {"videoPath": video_file}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
