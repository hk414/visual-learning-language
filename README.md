# AI-Powered Visual Learning Language App

This application helps in visual language learning by generating videos that combine image recognition, context-based text generation, speech synthesis, and video creation. The app leverages **Google Cloud Vision API** for object recognition, **OpenAI's GPT-3.5** for context generation, **Google Cloud Text-to-Speech API** for converting text into speech, and **FastAPI** for handling the web service.

## Features

- **Object Detection**: Upload an image and detect the object using Google Cloud Vision API.
- **Context Generation**: Generate a context (sentence) in a chosen language where the detected object would be used, powered by OpenAI's GPT model.
- **Text-to-Speech**: Convert the generated text into speech using Google Cloud Text-to-Speech API.
- **Video Creation**: Combine the context (text), audio, and background images to create a video.
- **Cloud Storage**: Upload and share generated videos via a public URL from Google Cloud Storage.

## Tech Stack

- **FastAPI**: A modern web framework for building the API.
- **OpenAI GPT-3**: For generating sentences based on detected objects.
- **Google Cloud APIs**:
  - **Vision API**: For object detection in uploaded images.
  - **Text-to-Speech API**: For speech synthesis from the generated text.
  - **Cloud Storage**: For storing and serving videos.
- **MoviePy**: For video processing, combining images, text, and audio.
- **Pillow (PIL)**: For text rendering on images.
- **OpenCV**: For image processing like resizing background images.

## Setup

### Prerequisites

- Python 3.7+
- Google Cloud Account with enabled APIs: Vision API, Text-to-Speech API, Cloud Storage
- OpenAI API key

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/hk414/visual-learning-language.git
   cd visual-learning-language-app
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Google Cloud credentials:
   
   - Download the service account key JSON file from Google Cloud Console and save it to your project directory.
   - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the JSON file.

   Example for Unix-based systems:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_service_account_key.json"
   ```

4. Set up your OpenAI API key:

   - Create a `.env` file in the root directory and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your-openai-api-key
   GOOGLE_APPLICATION_CREDENTIALS=path_to_your_service_account_key.json
   ```

### Running the Application

1. Run the FastAPI app locally:

   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. The app will be available at `http://127.0.0.1:8000`.

### API Endpoints

#### `POST /generate`

This endpoint generates a learning video from an uploaded image and the specified language.

##### Parameters:

- **language** (Form data, optional): The language for the generated sentence. Default is `Mandarin`.
- **image** (Form data, required): The image file to be uploaded (must be in `.jpg`, `.jpeg`, or `.png` format).

##### Example Request:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate' \
  -F 'language=Mandarin' \
  -F 'image=@/path/to/image.jpg'
```

##### Example Response:

```json
{
  "videoPath": "https://storage.googleapis.com/videos_15022025/videos/images%5C1000000034_video.mp4"
}
```

The response contains the public URL to the generated video stored in Google Cloud Storage.

## Notes

- The app uses **Google Cloud Storage** with the bucket name `videos_15022025` to store the generated videos.
- Background images can be customized by replacing the default `"background.jpg"` in the video creation process.
- The generated video will include a context-based sentence in the selected language and an audio overlay.

## Troubleshooting

- **Invalid API key**: Make sure your `OPENAI_API_KEY` and Google Cloud credentials are properly set up.
- **Invalid image format**: Ensure the uploaded image is in `.jpg`, `.jpeg`, or `.png` format.

