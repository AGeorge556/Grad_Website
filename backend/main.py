import os
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request, status, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from moviepy.editor import VideoFileClip
import tempfile
import logging
import yt_dlp
import re
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import json
import requests
from backend.model_processor import model_processor
import base64
import traceback
import sys
import whisper
from gtts import gTTS
import spacy
from transformers import pipeline
import subprocess
from backend.groq_utils import groq_chat
from backend.gemini_utils import gemini_generate_flashcards, gemini_generate_quizzes, gemini_video_chat
from backend.mistral_utils import mistral_generate_suggestions, mistral_chat
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import shutil
import uuid
# Add the backend directory to Python path to allow imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
# Import talking head video generator modules
from talking_head.generate_video import generate_talking_video, MEDIA_DIR
from talking_head.tts import text_to_speech_mock

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("Current working directory:", os.getcwd())
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_SERVICE_KEY:", os.getenv("SUPABASE_SERVICE_KEY"))
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
print("MISTRAL_API_KEY:", "***" if os.getenv("MISTRAL_API_KEY") else "Not set")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Ensure MEDIA_DIR exists
os.makedirs(MEDIA_DIR, exist_ok=True)

# Create uploads directory for SadTalker source images
UPLOADS_DIR = os.path.join(MEDIA_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# CORS middleware configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://mpwkqvamrqwxhwozaxpa.supabase.co",
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

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Make sure this is the service role key
groq_api_key = os.getenv("GROQ_API_KEY")

print("SUPABASE_URL:", supabase_url)
print("SUPABASE_SERVICE_KEY:", supabase_key)
print("GROQ_API_KEY:", groq_api_key)

if not all([supabase_url, supabase_key, groq_api_key]):
    raise ValueError("Missing required environment variables")

# Initialize Supabase client with service role key
options = ClientOptions()
supabase: Client = create_client(
    supabase_url,
    supabase_key,
    options
)

# Load models once at startup
whisper_model = whisper.load_model("base")
summarizer = pipeline("summarization")
nlp = spacy.load("en_core_web_sm")

# Enhanced Pydantic models with validation
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class Space(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class Topic(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)

    @validator('image_url')
    def validate_image_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must be a valid HTTP(S) URL')
        return v

class VideoRequest(BaseModel):
    videoId: str = Field(..., min_length=1)
    youtubeUrl: str = Field(..., pattern=r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&[^&]*)*$')
    user_id: str

class VideoChatRequest(BaseModel):
    summary: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=1000)

# Talking Head Video Generator Models
class TextInput(BaseModel):
    summary_text: str = Field(..., min_length=1)

class YouTubeInput(BaseModel):
    youtube_url: str = Field(..., description="YouTube video URL to use as source")
    start_time: Optional[int] = Field(0, description="Start time in seconds")
    
    @validator('youtube_url')
    def validate_youtube_url(cls, v):
        if not ('youtube.com' in v or 'youtu.be' in v):
            raise ValueError('Not a valid YouTube URL')
        return v

class MistralChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Chat message for Mistral AI")

class MistralSuggestionsRequest(BaseModel):
    transcript: str = Field(..., min_length=10, max_length=10000, description="Transcript text for generating suggestions")

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
        result = generate_talking_video(request_data.summary_text)
        end_time = time.time()
        processing_time = end_time - start_time

        # Handle both string and dictionary return types for backward compatibility
        if isinstance(result, dict):
            video_path = result.get("video_path")
            success = result.get("success", True)
            video_url = result.get("video_url")
            
            if not success:
                logging.warning(f"Talking head generation reported failure but is continuing with fallback: {result.get('message')}")
        else:
            # Legacy behavior - result is a string path
            video_path = result
            video_url = None

        if video_path and os.path.exists(video_path):
            # If we don't have a video_url from the result, generate it
            if not video_url:
                # Construct the URL to access the video
                video_filename = os.path.basename(video_path)
                # Get relative path from MEDIA_DIR
                relative_video_path = os.path.relpath(video_path, MEDIA_DIR)
                # Ensure forward slashes for URL
                relative_video_path_url = relative_video_path.replace("\\", "/")
                video_url = f"/media/{relative_video_path_url}"
            
            logging.info(f"Video generation successful. Path: {video_path}, URL: {video_url}, Time: {processing_time:.2f}s")
            return JSONResponse(content={
                "message": "Video generated successfully.",
                "video_url": video_url, 
                "video_path": video_path,
                "processing_time_seconds": round(processing_time, 2)
            })
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

# Mount media directory for serving files
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Rate limited endpoints
@app.post("/chat")
@limiter.limit("10/minute")
async def chat(message: ChatMessage, request: Request):
    try:
        print("[DEBUG] Received chat message:", message, flush=True)
        response = groq_chat(message.message)
        return {"data": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/spaces")
@limiter.limit("30/minute")
async def get_spaces(user_id: str, request: Request):
    try:
        response = supabase.table("spaces").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting spaces: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spaces")
@limiter.limit("10/minute")
async def create_space(space: Space, user_id: str = None, request: Request = None):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
        
    try:
        # Verify user exists
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        if not user_response.user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create space with service role
        response = supabase.table("spaces").insert({
            "name": space.name,
            "description": space.description,
            "user_id": user_id
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create space")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating space: {str(e)}")
        if "violates row-level security policy" in str(e):
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Please check your authentication."
            )
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/spaces/{space_id}")
@limiter.limit("10/minute")
async def delete_space(space_id: str, user_id: str, request: Request):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
        
    try:
        # First, verify the space exists and belongs to the user
        space_response = supabase.table("spaces").select("*").eq("id", space_id).eq("user_id", user_id).execute()
        
        if not space_response.data:
            raise HTTPException(status_code=404, detail="Space not found or you don't have permission to delete it")
        
        # Delete related space_topics entries first (if they exist)
        try:
            supabase.table("space_topics").delete().eq("space_id", space_id).execute()
        except Exception as e:
            logger.warning(f"Could not delete space_topics for space {space_id}: {str(e)}")
        
        # Delete the space
        response = supabase.table("spaces").delete().eq("id", space_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to delete space")
            
        return {"message": "Space deleted successfully", "deleted_space_id": space_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting space: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topics")
async def get_topics(space_id: Optional[str] = None):
    if space_id:
        # Get topics for a specific space through the space_topics junction table
        try:
            response = supabase.table("space_topics").select(
                "topics(*)"
            ).eq("space_id", space_id).execute()
            
            # Extract the topics from the junction table response
            topics = []
            for item in response.data:
                if item.get("topics"):
                    topics.append(item["topics"])
            return topics
        except Exception as e:
            logger.warning(f"Could not query space_topics table: {str(e)}")
            # Return empty array if tables don't exist yet
            return []
    else:
        # Get all topics
        try:
            response = supabase.table("topics").select("*").execute()
            return response.data
        except Exception as e:
            logger.warning(f"Could not query topics table: {str(e)}")
            # Return empty array if table doesn't exist yet
            return []

@app.post("/topics/{space_id}")
async def add_topic_to_space(space_id: str, topic_id: str):
    try:
        response = supabase.table("space_topics").insert({
            "space_id": space_id,
            "topic_id": topic_id
        }).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error adding topic to space: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/topics/{user_id}")
async def get_user_topics(user_id: str):
    try:
        response = supabase.table("user_topics").select(
            "*, topics(*)").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting user topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/topics/{user_id}/{topic_id}")
async def update_user_topic(
    user_id: str,
    topic_id: str,
    is_favorite: Optional[bool] = None,
    progress: Optional[int] = None
):
    try:
        data = {
            "user_id": user_id,
            "topic_id": topic_id,
            "last_accessed": datetime.utcnow().isoformat()
        }
        if is_favorite is not None:
            data["is_favorite"] = is_favorite
        if progress is not None:
            data["progress"] = progress

        response = supabase.table("user_topics").upsert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating user topic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def download_youtube_video(url: str) -> str:
    """Download a YouTube video and return the path to the downloaded file."""
    # First, check if yt-dlp is up to date, as YouTube often changes their API
    try:
        subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], capture_output=True, check=True)
        logger.info("Successfully updated yt-dlp to the latest version")
    except Exception as e:
        logger.warning(f"Could not update yt-dlp: {str(e)}")

    # Create several fallback options with different configurations
    attempts = [
        # First attempt - standard configuration
        {
            'format': 'best[ext=mp4]/best',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'no_color': True,
            'geo_bypass': True,  # Try to bypass geo-restrictions
        },
        # Second attempt - use different format and cookies
        {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'no_color': True,
            'geo_bypass': True,
            'nocheckcertificate': True,  # Skip HTTPS certificate validation
        },
        # Third attempt - try with even more basic settings
        {
            'format': 'mp4',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'no_color': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'extractor_retries': 5,  # Retry extraction 5 times
        },
        # Fourth attempt - try with youtube-dl extract-only
        {
            'format': 'best',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': False,
            'noplaylist': True,
            'skip_download': False,
            'ignoreerrors': True,
            'no_color': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'extractor_retries': 10,
            'external_downloader': 'aria2c',  # Try using aria2c as external downloader
        }
    ]

    video_id = None
    for i, ydl_opts in enumerate(attempts):
        try:
            logger.info(f"Downloading YouTube video (attempt {i+1}/{len(attempts)}): {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info is None:
                    logger.warning(f"Attempt {i+1} failed, info is None")
                    continue
                    
                video_id = info.get('id')
                if not video_id:
                    logger.warning(f"Attempt {i+1} failed, could not get video ID")
                    continue
                
                # Try to get the filename
                try:
                    filename = ydl.prepare_filename(info)
                    if os.path.exists(filename):
                        logger.info(f"Successfully downloaded video to: {filename}")
                        return filename
                except Exception as e:
                    logger.warning(f"Could not prepare filename: {e}")
                
                # If prepare_filename didn't work, try alternative approaches
                default_filename = f"{video_id}.mp4"
                if os.path.exists(default_filename):
                    logger.info(f"Found video at default filename: {default_filename}")
                    return default_filename
                
                # Check for other extensions
                for ext in ['webm', 'mkv', 'mp4', 'avi', 'm4a']:
                    alt_filename = f"{video_id}.{ext}"
                    if os.path.exists(alt_filename):
                        logger.info(f"Found video with extension: {alt_filename}")
                        return alt_filename
                
                logger.warning(f"Attempt {i+1}: File not found after download")
        except Exception as e:
            logger.warning(f"Attempt {i+1} failed with error: {str(e)}")
    
    # As a last resort, try pytube
    if video_id:
        try:
            from pytube import YouTube
            logger.info("Trying download with pytube as last resort")
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
            if stream:
                filename = stream.download(filename=f"{video_id}_pytube.mp4")
                logger.info(f"Successfully downloaded with pytube to: {filename}")
                return filename
        except Exception as e:
            logger.warning(f"Pytube download failed: {str(e)}")
    
    # If we've tried everything and failed, raise an exception
    error_msg = f"Failed to download YouTube video after multiple attempts: {url}"
    logger.error(error_msg)
    raise HTTPException(status_code=500, detail=error_msg)

def is_valid_summary(summary: str) -> bool:
    return summary and not summary.startswith("Summary not available")

def is_valid_flashcards(flashcards: list) -> bool:
    return flashcards and not (isinstance(flashcards[0], dict) and flashcards[0].get("question", "").startswith("Flashcards not available"))

def is_valid_quiz(quizzes: list) -> bool:
    return quizzes and not (isinstance(quizzes[0], dict) and quizzes[0].get("question", "").startswith("Quiz not available"))

@app.post("/process-video/{video_id}")
async def process_video(video_id: str, video: UploadFile = File(...)):
    try:
        # Read video bytes
        if not video:
            raise HTTPException(status_code=400, detail="No video file provided")
        if isinstance(video, str):
            with open(video, "rb") as f:
                video_bytes = f.read()
        else:
            video_bytes = await video.read()
        # Process video
        print("[DEBUG] Calling model_processor.process_video")
        transcript, summary, audio_bytes, flashcards, quizzes, notes = await model_processor.process_video(video_bytes)
        print("[DEBUG] Model output:", {
            "transcript": transcript,
            "summary": summary,
            "audio_bytes_len": len(audio_bytes) if audio_bytes else 0,
            "flashcards": flashcards,
            "quizzes": quizzes,
            "notes": notes
        })
        # Convert audio bytes to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        print(f"[DEBUG] Updating video {video_id} with summary: {summary[:100]}")
        # Only update Supabase if all are valid
        if is_valid_summary(summary) and is_valid_flashcards(flashcards) and is_valid_quiz(quizzes):
            supabase.table("videos").update({
                "summary": summary,
                "flashcards": flashcards,
                "quizzes": quizzes,
                "notes": notes,
                "title": "Processed Video"
            }).eq("id", video_id).execute()
            print(f"[DEBUG] Update complete for video {video_id}")
        else:
            print(f"[DEBUG] Not updating Supabase for video {video_id} due to invalid AI results.")
        return {
            "transcript": transcript,
            "summary": summary,
            "audio": audio_base64,
            "flashcards": flashcards,
            "quizzes": quizzes,
            "notes": notes,
            "title": "Processed Video"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    try:
        if "youtu.be" in url:
            return url.split("/")[-1]
        else:
            return url.split("v=")[1].split("&")[0]
    except Exception:
        return None

def get_video_transcript(youtube_id: str) -> str:
    """Get video transcript using YouTube Transcript API."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(youtube_id)
        return " ".join([entry["text"] for entry in transcript_list])
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return ""

def get_video_info(youtube_id: str) -> dict:
    """Get video information using pytube."""
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={youtube_id}")
        return {
            "title": yt.title,
            "description": yt.description
        }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {"title": "", "description": ""}

@app.post("/process-youtube")
async def process_youtube(request: Request):
    data = await request.json()
    print("[DEBUG] Raw request data:", data, flush=True)
    video_req = VideoRequest(**data)
    try:
        logger.info(f"Processing request: {video_req}")
        youtube_id = extract_youtube_id(video_req.youtubeUrl)
        if not youtube_id:
            logger.error(f"Invalid YouTube URL: {video_req.youtubeUrl}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        # Download YouTube video to temp file
        temp_path = download_youtube_video(video_req.youtubeUrl)
        logger.info(f"YouTube video downloaded to: {temp_path}")
        with open(temp_path, "rb") as f:
            video_bytes = f.read()
        # Process video with model
        print("[DEBUG] Calling model_processor.process_video", flush=True)
        transcript, summary, audio_bytes, flashcards, quizzes, notes = await model_processor.process_video(video_bytes)
        print("[DEBUG] Model output:", {
            "transcript": transcript,
            "summary": summary,
            "audio_bytes_len": len(audio_bytes) if audio_bytes else 0,
            "flashcards": flashcards,
            "quizzes": quizzes,
            "notes": notes
        }, flush=True)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        print(f"[DEBUG] Updating video {video_req.videoId} with summary: {summary[:100]}", flush=True)
        # Only update Supabase if all are valid
        if is_valid_summary(summary) and is_valid_flashcards(flashcards) and is_valid_quiz(quizzes):
            update_payload = {
                "summary": summary or "",
                "flashcards": json.dumps(flashcards) if flashcards else "[]",
                "quizzes": json.dumps(quizzes) if quizzes else "[]",
                "notes": notes or "",
                "title": "Processed Video",
                "transcript": transcript or "",
                "youtube_id": video_req.videoId,
                "user_id": video_req.user_id,
                "status": "completed",
                "source": "youtube",
                "youtube_url": video_req.youtubeUrl,
                "file_path": None
            }
            print("[DEBUG] Supabase update payload:", update_payload, flush=True)
            print(f"[DEBUG] About to update video with id={video_req.videoId}", flush=True)
            try:
                # First try to find the video by YouTube ID
                response = supabase.table("videos").select("*").eq("youtube_id", video_req.videoId).execute()
                if response.data and len(response.data) > 0:
                    # Update existing video
                    video_id = response.data[0]['id']
                    response = supabase.table("videos").update(update_payload).eq("id", video_id).execute()
                else:
                    # Insert new video
                    response = supabase.table("videos").insert(update_payload).execute()
                
                print("[DEBUG] Supabase update response:", response, flush=True)
                if hasattr(response, 'data'):
                    print("[DEBUG] Supabase response data:", response.data, flush=True)
                if hasattr(response, 'error'):
                    print("[DEBUG] Supabase response error:", response.error, flush=True)
                if isinstance(response, dict):
                    print("[DEBUG] Supabase response keys:", response.keys(), flush=True)
            except Exception as supabase_exc:
                print("[DEBUG] Exception during Supabase update:", supabase_exc, flush=True)
                traceback.print_exc(file=sys.stdout)
                raise HTTPException(status_code=500, detail=f"Failed to update video in database: {str(supabase_exc)}")
        else:
            print(f"[DEBUG] Not updating Supabase for video {video_req.videoId} due to invalid AI results.")
            raise HTTPException(status_code=500, detail="Failed to generate valid AI results")
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
        
        return {
            "transcript": transcript,
            "summary": summary,
            "audio": audio_base64,
            "flashcards": flashcards,
            "quizzes": quizzes,
            "notes": notes,
            "title": "Processed Video"
        }
    except Exception as e:
        print("[DEBUG] Exception type:", type(e), flush=True)
        print("[DEBUG] Exception in process-youtube:", e, flush=True)
        traceback.print_exc(file=sys.stdout)
        logger.error(f"Error in process-youtube: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def split_into_chunks(text, max_length=500):
    doc = nlp(text)
    chunks, chunk = [], ''
    for sent in doc.sents:
        if len(chunk) + len(sent.text) <= max_length:
            chunk += sent.text + ' '
        else:
            chunks.append(chunk.strip())
            chunk = sent.text + ' '
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def generate_talking_head_video(audio_path: str, face_path: str, output_path: str):
    """Generate a talking head video using SadTalker."""
    # Path to our batch file that properly activates the SadTalker environment
    batch_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run_sadtalker.bat")
    
    if os.path.exists(batch_file):
        # Use the batch file if it exists
        command = [
            batch_file,
            "--driven_audio", audio_path,
            "--source_image", face_path,
            "--result_dir", os.path.dirname(output_path),
            "--enhancer", "gfpgan",
            "--preprocess", "full"
        ]
        subprocess.run(command, check=True, shell=True)
    else:
        # Fallback to direct command if batch file doesn't exist
        command = [
            "python", "inference.py",
            "--driven_audio", audio_path,
            "--source_image", face_path,
            "--result_dir", os.path.dirname(output_path),
            "--enhancer", "gfpgan",
            "--preprocess", "full"
        ]
        subprocess.run(command, cwd="../SadTalker", check=True)

@app.post("/process-video-with-talking-head")
@limiter.limit("5/minute")
async def process_video_with_talking_head(
    video: UploadFile = File(...),
    user_id: str = None,
    request: Request = None
):
    try:
        if not video.filename.lower().endswith(('.mp4', '.mov', '.avi')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only MP4, MOV, and AVI files are supported."
            )

        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            content = await video.read()
            temp_video.write(content)
            temp_video_path = temp_video.name

        try:
            # Check file existence before processing
            if not temp_video_path or not os.path.exists(temp_video_path):
                raise HTTPException(status_code=400, detail="Temporary video file not found")
            # Process video
            result = await process_video(temp_video_path, user_id)
            return result
        finally:
            # Cleanup
            if os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-flashcards")
async def generate_flashcards_api(summary: str):
    flashcards = gemini_generate_flashcards(summary)
    return {"flashcards": flashcards}

@app.post("/generate-quizzes")
async def generate_quizzes_api(summary: str):
    quizzes = gemini_generate_quizzes(summary)
    return {"quizzes": quizzes}

@app.post("/video-chat")
async def video_chat_api(req: VideoChatRequest):
    answer = gemini_video_chat(req.summary, req.message)
    return {"response": answer}

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
        result = generate_talking_video(summary_text, source_image_path)
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Handle both string and dictionary return types for backward compatibility
        if isinstance(result, dict):
            video_path = result.get("video_path")
            success = result.get("success", True)
            video_url = result.get("video_url")
            
            if not success:
                logging.warning(f"Talking head generation reported failure but is continuing with fallback: {result.get('message')}")
        else:
            # Legacy behavior - result is a string path
            video_path = result
            video_url = None
        
        if video_path and os.path.exists(video_path):
            # If we don't have a video_url from the result, generate it
            if not video_url:
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

@app.get("/videos/{video_id}/talking-head")
@limiter.limit("5/minute")
async def get_talking_head_for_video(video_id: str, request: Request):
    """
    Generate or retrieve a talking head video for an existing video by ID.
    """
    try:
        # First try to find the video by ID
        response = supabase.table("videos").select("*").eq("id", video_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
        
        video_data = response.data[0]
        summary = video_data.get("summary")
        
        if not summary:
            raise HTTPException(status_code=400, detail="Video has no summary to generate talking head")
        
        # Generate talking head video
        start_time = time.time()
        result = generate_talking_video(summary)
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Handle both string and dictionary return types for backward compatibility
        if isinstance(result, dict):
            video_path = result.get("video_path")
            success = result.get("success", True)
            video_url = result.get("video_url")
            
            if not success:
                logging.warning(f"Talking head generation reported failure but is continuing with fallback: {result.get('message')}")
        else:
            # Legacy behavior - result is a string path
            video_path = result
            video_url = None
        
        if video_path and os.path.exists(video_path):
            # If we don't have a video_url from the result, generate it
            if not video_url:
                # Get relative path from MEDIA_DIR
                relative_video_path = os.path.relpath(video_path, MEDIA_DIR)
                # Ensure forward slashes for URL
                relative_video_path_url = relative_video_path.replace("\\", "/")
                video_url = f"/media/{relative_video_path_url}"
            
            # Try to update video record with talking head URL
            # But catch the error if the column doesn't exist
            try:
                supabase.table("videos").update({
                    "talking_head_url": video_url
                }).eq("id", video_id).execute()
                logging.info(f"Updated video {video_id} with talking head URL: {video_url}")
            except Exception as db_error:
                # Log the error but continue
                logging.warning(f"Could not update video record with talking head URL: {str(db_error)}")
                logging.warning("This is likely because the 'talking_head_url' column doesn't exist in the 'videos' table.")
                logging.warning("To fix this, add the column to your Supabase table or update your database schema.")
            
            return {
                "message": "Talking head video generated successfully",
                "talking_head_url": video_url,
                "processing_time_seconds": round(processing_time, 2)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate talking head video")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating talking head for video {video_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate talking head: {str(e)}")

# Mistral AI endpoints
@app.post("/mistral-chat")
@limiter.limit("20/minute")
async def mistral_chat_endpoint(request_data: MistralChatRequest, request: Request):
    """Send a chat message to Mistral AI"""
    try:
        logger.info(f"Mistral chat request: {request_data.message[:100]}...")
        
        response = await mistral_chat(request_data.message)
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Mistral chat validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Mistral chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message with Mistral AI"
        )

@app.post("/mistral-suggestions")
@limiter.limit("15/minute")
async def mistral_suggestions_endpoint(request_data: MistralSuggestionsRequest, request: Request):
    """Generate educational suggestions from transcript using Mistral AI"""
    try:
        logger.info(f"Mistral suggestions request for transcript length: {len(request_data.transcript)}")
        
        suggestions = await mistral_generate_suggestions(request_data.transcript)
        
        return {
            "success": True,
            "suggestions": suggestions,
            "count": len(suggestions),
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Mistral suggestions validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Mistral suggestions error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate suggestions with Mistral AI"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)