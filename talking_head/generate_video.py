import os
import subprocess
import logging
import uuid
import shutil
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define media directory
MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# Path to SadTalker
SADTALKER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "SadTalker")
# Use the Python 3.10 environment
VENV_PYTHON = os.path.join(SADTALKER_PATH, "sadtalker_venv", "Scripts", "python.exe")

# Default face path
DEFAULT_FACE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "default_face.jpg")
FALLBACK_VIDEO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fallback_talking_head.mp4")

def generate_talking_video(text_content, source_image_path=None, request_id=None):
    """
    Generate a talking head video from text content and a source image.
    
    Args:
        text_content (str): The text to be spoken by the talking head
        source_image_path (str, optional): Path to the source image. Defaults to the default face.
        request_id (str, optional): Unique ID for this request. Generated if not provided.
        
    Returns:
        dict: A dictionary containing the result paths and metadata
    """
    # Generate request ID if not provided
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    logger.info(f"[Request {request_id}] Starting video generation for text: '{text_content[:50]}...'")
    
    # Use default face if source image not provided
    if source_image_path is None or not os.path.exists(source_image_path):
        source_image_path = DEFAULT_FACE_PATH
        logger.info(f"[Request {request_id}] Using default face: {source_image_path}")
    
    # Create paths for intermediate files
    audio_path = os.path.join(MEDIA_DIR, f"mock_audio_{request_id}.wav")
    result_dir = os.path.join(MEDIA_DIR, f"results_{request_id}")
    final_video_path = os.path.join(MEDIA_DIR, f"talking_head_{request_id}.mp4")
    
    try:
        # Step 1: Generate audio from text
        logger.info(f"[Request {request_id}] Generating audio...")
        from talking_head.tts import text_to_speech_mock
        text_to_speech_mock(text_content, audio_path)
        logger.info(f"[Request {request_id}] Audio generated: {audio_path}")
        
        # Step 2: Run SadTalker to generate talking head video
        logger.info(f"[Request {request_id}] Starting SadTalker inference...")
        logger.info(f"[Request {request_id}] Source Image: {source_image_path}")
        logger.info(f"[Request {request_id}] Driven Audio: {audio_path}")
        logger.info(f"[Request {request_id}] Result Dir: {result_dir}")
        
        # Use batch file to properly activate virtual environment - use the Python 3.10 version
        batch_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_sadtalker_py310.bat")
        
        # Fall back to original if Python 3.10 version doesn't exist
        if not os.path.exists(batch_file_path):
            logger.warning(f"[Request {request_id}] Python 3.10 batch file not found, falling back to original")
            batch_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_sadtalker.bat")
        
        # Make sure the batch file exists
        if not os.path.exists(batch_file_path):
            logger.error(f"[Request {request_id}] Batch file not found: {batch_file_path}")
            raise Exception(f"Batch file not found: {batch_file_path}")
        
        cmd = [
            batch_file_path,
            SADTALKER_PATH,  # %1 - SadTalker directory
            audio_path,      # %2 - Audio file
            source_image_path,  # %3 - Source image
            result_dir       # %4 - Result directory
        ]
        
        logger.info(f"[Request {request_id}] Executing SadTalker command: {' '.join(cmd)}")
        
        # Run SadTalker using the batch file
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # Required for batch files
        )
        stdout, stderr = process.communicate()
        
        logger.info(f"[Request {request_id}] SadTalker stdout:\n{stdout}")
        
        if process.returncode != 0:
            logger.error(f"[Request {request_id}] SadTalker stderr:\n{stderr}")
            logger.error(f"[Request {request_id}] Video generation failed: SadTalker inference failed with return code {process.returncode}")
            
            # Clean up failed result directory
            if os.path.exists(result_dir):
                shutil.rmtree(result_dir)
                logger.info(f"[Request {request_id}] Cleaned up failed result directory: {result_dir}")
            
            # Use fallback video
            shutil.copy(FALLBACK_VIDEO_PATH, final_video_path)
            logger.info(f"[Request {request_id}] Using fallback video: {FALLBACK_VIDEO_PATH}")
            
            return {
                "video_url": f"/media/talking_head_{request_id}.mp4",
                "video_path": final_video_path,
                "processing_time_seconds": 0,
                "success": False,
                "message": "Failed to generate video, using fallback"
            }
        
        # Step 3: Find the generated video in the result directory
        result_video = None
        for root, _, files in os.walk(result_dir):
            for file in files:
                if file.endswith(".mp4"):
                    result_video = os.path.join(root, file)
                    break
            if result_video:
                break
        
        if not result_video:
            logger.error(f"[Request {request_id}] No video file found in result directory: {result_dir}")
            # Use fallback video
            shutil.copy(FALLBACK_VIDEO_PATH, final_video_path)
            logger.info(f"[Request {request_id}] Using fallback video: {FALLBACK_VIDEO_PATH}")
            
            return {
                "video_url": f"/media/talking_head_{request_id}.mp4",
                "video_path": final_video_path,
                "processing_time_seconds": 0,
                "success": False,
                "message": "Failed to generate video, using fallback"
            }
        
        # Step 4: Copy the result to the final path
        shutil.copy(result_video, final_video_path)
        logger.info(f"[Request {request_id}] Copied result video to: {final_video_path}")
        
        # Step 5: Clean up temporary files
        try:
            os.remove(audio_path)
            shutil.rmtree(result_dir)
            logger.info(f"[Request {request_id}] Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"[Request {request_id}] Error cleaning up: {str(e)}")
        
        return {
            "video_url": f"/media/talking_head_{request_id}.mp4",
            "video_path": final_video_path,
            "processing_time_seconds": 15,  # Approximate time
            "success": True,
            "message": "Video generated successfully"
        }
        
    except Exception as e:
        logger.exception(f"[Request {request_id}] Error generating talking head video: {str(e)}")
        
        # Use fallback video
        shutil.copy(FALLBACK_VIDEO_PATH, final_video_path)
        logger.info(f"[Request {request_id}] Using fallback video due to error: {FALLBACK_VIDEO_PATH}")
        
        return {
            "video_url": f"/media/talking_head_{request_id}.mp4",
            "video_path": final_video_path,
            "processing_time_seconds": 0,
            "success": False,
            "message": f"Error: {str(e)}"
        } 