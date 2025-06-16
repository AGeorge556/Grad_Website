from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Optional
from talking_head.generate_video import generate_talking_video, MEDIA_DIR
import os
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import shutil
import uuid
import subprocess
from pytube import YouTube

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="SadTalker API", description="API for generating talking head videos")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Ensure MEDIA_DIR exists
os.makedirs(MEDIA_DIR, exist_ok=True)

# Create uploads directory
UPLOADS_DIR = os.path.join(MEDIA_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount media directory for serving files
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Pydantic models for request validation
class TextInput(BaseModel):
    summary_text: str = Field(..., min_length=1, description="The text to convert to a talking head video")

class YouTubeInput(BaseModel):
    youtube_url: str = Field(..., description="YouTube video URL to use as source")
    start_time: Optional[int] = Field(0, description="Start time in seconds")
    
    @validator('youtube_url')
    def validate_youtube_url(cls, v):
        if not ('youtube.com' in v or 'youtu.be' in v):
            raise ValueError('Not a valid YouTube URL')
        return v

def download_youtube_frame(youtube_url: str, start_time: int = 0) -> str:
    """Download a frame from a YouTube video at the specified time."""
    request_id = str(uuid.uuid4())
    output_dir = os.path.join(UPLOADS_DIR, request_id)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        yt = YouTube(youtube_url)
        video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        
        if not video_stream:
            raise ValueError("No suitable video stream found")
        
        # Download the video
        temp_video_path = video_stream.download(output_path=output_dir)
        frame_path = os.path.join(output_dir, f"frame_{start_time}.jpg")
        
        # Extract frame using ffmpeg
        command = [
            "ffmpeg", "-y", "-i", temp_video_path, 
            "-ss", str(start_time), "-frames:v", "1", 
            frame_path
        ]
        
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg frame extraction failed: {process.stderr}")
        
        # Clean up the downloaded video
        os.remove(temp_video_path)
        
        return frame_path
        
    except Exception as e:
        logging.error(f"YouTube frame extraction failed: {e}")
        raise RuntimeError(f"Failed to extract frame from YouTube video: {e}")

@app.get("/")
async def root():
    return {"message": "SadTalker API is running. Use POST /generate-talking-video to generate videos."}

@app.post("/generate-talking-video")
@limiter.limit("5/minute")
async def generate_talking_video_endpoint(request_data: TextInput, request: Request):
    """
    Accepts text summary and generates a talking head video.
    
    Returns the path or URL to the generated video file.
    """
    logging.info(f"Received request for talking head video generation with text: '{request_data.summary_text[:100]}...")

    try:
        # Call the core generation function
        start_time = time.time()
        video_path = generate_talking_video(request_data.summary_text)
        end_time = time.time()
        processing_time = end_time - start_time

        if video_path and os.path.exists(video_path):
            # Construct the URL to access the video
            video_filename = os.path.basename(video_path)
            # Get relative path from MEDIA_DIR
            relative_video_path = os.path.relpath(video_path, MEDIA_DIR)
            # Ensure forward slashes for URL
            relative_video_path_url = relative_video_path.replace("\\", "/")
            video_url = f"/media/{relative_video_path_url}"
            
            logging.info(f"Video generation successful. Path: {video_path}, URL: {video_url}, Time: {processing_time:.2f}s")
            return {
                "message": "Video generated successfully.",
                "video_url": video_url, 
                "video_path": video_path,
                "processing_time_seconds": round(processing_time, 2)
            }
        else:
            logging.error("Video generation function returned None or file not found.")
            raise HTTPException(status_code=500, detail="Video generation failed internally.")

    except FileNotFoundError as e:
         logging.error(f"File not found error during generation: {e}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Server configuration error: {e}")
    except RuntimeError as e:
         logging.error(f"Runtime error during generation (likely SadTalker issue): {e}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Video generation failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/upload-image")
@limiter.limit("10/minute")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """
    Upload an image to use as source for talking head video generation.
    
    Returns the path to the uploaded image file.
    """
    try:
        request_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"uploaded_image_{request_id}{file_extension}"
        file_path = os.path.join(UPLOADS_DIR, unique_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return the path and URL to the uploaded file
        relative_path = os.path.relpath(file_path, MEDIA_DIR)
        relative_path_url = relative_path.replace("\\", "/")
        image_url = f"/media/{relative_path_url}"
        
        return {
            "message": "Image uploaded successfully",
            "image_path": file_path,
            "image_url": image_url
        }
    except Exception as e:
        logging.error(f"Image upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

@app.post("/youtube-to-talking-head")
@limiter.limit("5/minute")
async def youtube_to_talking_head(request: Request, youtube_data: YouTubeInput):
    """
    Extract a frame from a YouTube video and use it as source for talking head generation.
    
    Returns the path to the generated video.
    """
    try:
        # Download frame from YouTube video
        frame_path = download_youtube_frame(youtube_data.youtube_url, youtube_data.start_time)
        logging.info(f"Downloaded frame from YouTube: {frame_path}")
        
        # Generate talking head video using the extracted frame
        # Note: This would need the real text to use for speech generation
        # For now, we'll just return the frame path
        return {
            "message": "YouTube frame extracted successfully",
            "frame_path": frame_path,
            "frame_url": f"/media/uploads/{os.path.basename(os.path.dirname(frame_path))}/{os.path.basename(frame_path)}"
        }
    except Exception as e:
        logging.error(f"YouTube to talking head failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"YouTube to talking head failed: {e}")

@app.post("/generate-from-source")
@limiter.limit("5/minute")
async def generate_from_source(
    request: Request,
    summary_text: str = Form(...),
    source_image_path: str = Form(...)
):
    """
    Generate a talking head video using a specific source image and text.
    
    Returns the path to the generated video.
    """
    try:
        start_time = time.time()
        # Validate the source image path exists
        if not os.path.exists(source_image_path) and source_image_path.startswith("/media/"):
            # Try to convert from URL path to file system path
            relative_path = source_image_path.replace("/media/", "")
            source_image_path = os.path.join(MEDIA_DIR, relative_path)
        
        if not os.path.exists(source_image_path):
            raise FileNotFoundError(f"Source image not found: {source_image_path}")
        
        # Generate the talking head video
        video_path = generate_talking_video(summary_text, source_image_path)
        end_time = time.time()
        processing_time = end_time - start_time
        
        if video_path and os.path.exists(video_path):
            # Construct the URL to access the video
            relative_video_path = os.path.relpath(video_path, MEDIA_DIR)
            # Ensure forward slashes for URL
            relative_video_path_url = relative_video_path.replace("\\", "/")
            video_url = f"/media/{relative_video_path_url}"
            
            return {
                "message": "Video generated successfully with custom source",
                "video_url": video_url,
                "video_path": video_path,
                "processing_time_seconds": round(processing_time, 2)
            }
        else:
            raise HTTPException(status_code=500, detail="Video generation failed")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Generate from source failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generate from source failed: {e}")

if __name__ == "__main__":
    import uvicorn
    print("Starting SadTalker API server...")
    print(f"Media directory: {MEDIA_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=8000) 