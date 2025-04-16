from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from openai import OpenAI
from moviepy.editor import VideoFileClip
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

# Check if environment variables are set
if not supabase_url or not supabase_key:
    logger.error("Missing Supabase environment variables. Please check your .env file.")
    raise ValueError("Missing required environment variables: SUPABASE_URL and/or SUPABASE_SERVICE_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if OpenAI API key is set
if not openai_api_key:
    logger.error("Missing OpenAI API key. Please check your .env file.")
    raise ValueError("Missing required environment variable: OPENAI_API_KEY")

if not all([supabase_url, supabase_key, openai_api_key]):
    raise ValueError("Missing required environment variables")

supabase: Client = create_client(supabase_url, supabase_key)
client = OpenAI(api_key=openai_api_key, base_url="https://api.openai.com/v1")

@app.post("/process-video/{video_id}")
async def process_video(video_id: str):
    try:
        logger.info(f"Processing video {video_id}")
        
        # Get video details from database
        video_response = supabase.table("videos").select("*").eq("id", video_id).single().execute()
        if not video_response.data:
            logger.error(f"Video {video_id} not found in database")
            raise HTTPException(status_code=404, detail="Video not found")

        video = video_response.data
        logger.info(f"Found video: {video}")

        # Download video from Supabase storage
        video_path = video["file_path"]
        logger.info(f"Downloading video from path: {video_path}")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                response = supabase.storage.from_("videos").download(video_path)
                if not response:
                    raise HTTPException(status_code=500, detail="Failed to download video from storage")
                temp_file.write(response)
                temp_path = temp_file.name
                logger.info(f"Video downloaded to: {temp_path}")
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to download video: {str(e)}")

        try:
            # Extract audio and generate transcript
            logger.info("Extracting audio from video")
            try:
                video_clip = VideoFileClip(temp_path)
                if not video_clip.audio:
                    logger.error("Video has no audio track")
                    raise HTTPException(status_code=400, detail="Video has no audio track")
                
                audio_clip = video_clip.audio
                audio_path = temp_path.replace(".mp4", ".mp3")
                logger.info("Writing audio file")
                audio_clip.write_audiofile(audio_path, logger=None)  # Disable moviepy's internal logging
                logger.info(f"Audio extracted to: {audio_path}")
            except Exception as e:
                logger.error(f"Error extracting audio: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error extracting audio: {str(e)}")

            # Generate summary using OpenAI
            logger.info("Generating transcript with Whisper")
            try:
                with open(audio_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                logger.info("Transcript generated successfully")
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error generating transcript: {error_message}")
                
                # Check for quota exceeded error
                if "insufficient_quota" in error_message or "exceeded your current quota" in error_message:
                    # Update video status with quota error message
                    supabase.table("videos").update({
                        "status": "failed",
                        "error_message": "OpenAI API quota exceeded. Please try again later or contact support."
                    }).eq("id", video_id).execute()
                    
                    raise HTTPException(
                        status_code=429, 
                        detail="OpenAI API quota exceeded. Please try again later or contact support."
                    )
                else:
                    raise HTTPException(status_code=500, detail=f"Error generating transcript: {error_message}")
                
            logger.info("Generating summary with GPT")
            try:
                summary = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": f"Please summarize this transcript: {transcript.text}"}
                    ]
                )
                logger.info("Summary generated successfully")
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error generating summary: {error_message}")
                
                # Check for quota exceeded error
                if "insufficient_quota" in error_message or "exceeded your current quota" in error_message:
                    # Update video status with quota error message
                    supabase.table("videos").update({
                        "status": "failed",
                        "error_message": "OpenAI API quota exceeded. Please try again later or contact support."
                    }).eq("id", video_id).execute()
                    
                    raise HTTPException(
                        status_code=429, 
                        detail="OpenAI API quota exceeded. Please try again later or contact support."
                    )
                else:
                    raise HTTPException(status_code=500, detail=f"Error generating summary: {error_message}")

            # Update video record with summary
            logger.info("Updating video record with summary")
            update_response = supabase.table("videos").update({
                "summary": summary.choices[0].message.content,
                "status": "completed"
            }).eq("id", video_id).execute()
            
            if update_response.error:
                logger.error(f"Failed to update video record: {update_response.error}")
                raise HTTPException(status_code=500, detail="Failed to update video record")

            return {"status": "success", "summary": summary.choices[0].message.content}

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Cleanup
            logger.info("Cleaning up temporary files")
            try:
                # Close video clip first to release file handles
                if 'video_clip' in locals() and video_clip:
                    video_clip.close()
                    
                # Add a small delay to ensure file handles are released
                import time
                time.sleep(0.5)
                    
                # Then delete the files
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"Could not delete temp video file: {str(e)}")
                        
                if 'audio_path' in locals() and os.path.exists(audio_path):
                    try:
                        os.unlink(audio_path)
                    except Exception as e:
                        logger.warning(f"Could not delete temp audio file: {str(e)}")
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {str(cleanup_error)}")

    except HTTPException as http_ex:
        # Update video status to failed with error message
        try:
            error_message = str(http_ex.detail)
            supabase.table("videos").update({
                "status": "failed",
                "error_message": error_message
            }).eq("id", video_id).execute()
        except Exception as update_error:
            logger.error(f"Failed to update video status: {str(update_error)}")
        raise
    except Exception as e:
        error_message = str(e)
        logger.error(f"Unexpected error: {error_message}")
        # Update video status to failed with error message
        try:
            supabase.table("videos").update({
                "status": "failed",
                "error_message": error_message if len(error_message) < 255 else error_message[:252] + "..."
            }).eq("id", video_id).execute()
        except Exception as update_error:
            logger.error(f"Failed to update video status: {str(update_error)}")
        raise HTTPException(status_code=500, detail=error_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)