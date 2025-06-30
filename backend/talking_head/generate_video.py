import os
import subprocess
import uuid
import logging
import shutil
import time
from .tts import text_to_speech_mock # Use relative import within the package
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Base directory of the talking_head module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DEFAULT_FACE_IMAGE = os.path.join(ASSETS_DIR, "default_face.jpg")
FALLBACK_VIDEO = os.path.join(ASSETS_DIR, "fallback_talking_head.mp4")

# Flag to use mock implementation instead of SadTalker
# IMPORTANT: Set to False to use the robust SadTalker implementation
USE_MOCK_IMPLEMENTATION = False

# ROBUSTNESS ENHANCEMENT: Enhanced SadTalker with fixes
ENHANCED_SADTALKER_PATH = "D:\\University files\\Graduation Project\\SadTalker"
# Use the enhanced preprocess module with all robustness fixes
ENHANCED_PREPROCESS_SCRIPT = os.path.join(ENHANCED_SADTALKER_PATH, "enhanced_preprocess.py")

# IMPORTANT: Update these paths based on the SADTALKER_SETUP.md instructions
# Windows path for SadTalker
WINDOWS_SADTALKER_PATH = ENHANCED_SADTALKER_PATH

# Path to our batch file that properly activates the SadTalker environment
SADTALKER_BATCH_FILE = "D:\\University files\\Graduation Project\\Website\\run_sadtalker_enhanced.bat"

# Check if we're in development or production mode to set proper paths
if os.path.exists("/opt/SadTalker"):
    # Production path (Linux)
    SADTALKER_INFERENCE_SCRIPT = "/opt/SadTalker/inference.py"
    SADTALKER_ROOT_DIR = "/opt/SadTalker"
elif os.path.exists(ENHANCED_SADTALKER_PATH):
    # Windows development path with robustness fixes
    SADTALKER_INFERENCE_SCRIPT = os.path.join(ENHANCED_SADTALKER_PATH, "inference.py") 
    SADTALKER_ROOT_DIR = ENHANCED_SADTALKER_PATH
    print(f"🔧 Using ENHANCED SadTalker with robustness fixes: {ENHANCED_SADTALKER_PATH}")
else:
    # Fallback to relative path
    SADTALKER_INFERENCE_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "SadTalker", "inference.py")
    SADTALKER_ROOT_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "SadTalker")

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Copy default face image if it doesn't exist
if not os.path.exists(DEFAULT_FACE_IMAGE):
    # Try to copy from PythonBackendModule (if integrating)
    source_default_face = os.path.join(BASE_DIR, "..", "PythonBackendModule", "default_face.jpg")
    if os.path.exists(source_default_face):
        shutil.copy(source_default_face, DEFAULT_FACE_IMAGE)
        logging.info(f"Copied default face image from {source_default_face} to {DEFAULT_FACE_IMAGE}")
    else:
        # Look for default face in model/files as mentioned in SADTALKER_SETUP.md
        model_default_face = os.path.join(BASE_DIR, "..", "model", "files", "default_face.png")
        if os.path.exists(model_default_face):
            shutil.copy(model_default_face, DEFAULT_FACE_IMAGE)
            logging.info(f"Copied default face image from {model_default_face} to {DEFAULT_FACE_IMAGE}")
        else:
            logging.warning(f"Default face image not found at {DEFAULT_FACE_IMAGE}. Please add a default face image.")

def generate_talking_video(text, source_image_path=None):
    """
    Generate a talking head video from text input.
    
    Args:
        text (str): The text to be spoken by the talking head.
        source_image_path (str, optional): Path to a custom source image. If None, default face is used.
        
    Returns:
        str: Path to the generated video file.
    """
    try:
        request_id = str(uuid.uuid4())
        logging.info(f"[Request {request_id}] Starting video generation for text: '{text[:50]}...'")
        
        # Step 1: Generate audio from text
        logging.info(f"[Request {request_id}] Generating audio...")
        audio_path = text_to_speech_mock(text, request_id)
        logging.info(f"[Request {request_id}] Audio generated: {audio_path}")
        
        # Step 2: Create result directory
        result_dir = os.path.join(MEDIA_DIR, f"results_{request_id}")
        os.makedirs(result_dir, exist_ok=True)
        
        # Step 3: Choose source image
        if not source_image_path or not os.path.exists(source_image_path):
            source_image_path = DEFAULT_FACE_IMAGE
            if not os.path.exists(source_image_path):
                raise FileNotFoundError(f"Default face image not found at {source_image_path}")
        
        # Step 4: Run SadTalker to generate video
        logging.info(f"[Request {request_id}] Starting SadTalker inference...")
        logging.info(f"[Request {request_id}] Source Image: {source_image_path}")
        logging.info(f"[Request {request_id}] Driven Audio: {audio_path}")
        logging.info(f"[Request {request_id}] Result Dir: {result_dir}")
        
        try:
            # Configure SadTalker command
            # Using batch file to properly activate SadTalker environment
            if os.path.exists(SADTALKER_BATCH_FILE):
                sadtalker_cmd = [
                    SADTALKER_BATCH_FILE,
                    "--driven_audio", audio_path,
                    "--source_image", source_image_path,
                    "--result_dir", result_dir,
                    "--enhancer", "gfpgan",
                    "--preprocess", "full",
                    "--still"  # Prevents expression changes
                ]
                
                logging.info(f"[Request {request_id}] Executing SadTalker command: {' '.join(sadtalker_cmd)}")
                
                # Run SadTalker process
                process = subprocess.run(
                    sadtalker_cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=True  # Required for batch files
                )
            else:
                # Fallback to direct Python call (less likely to work)
                sadtalker_cmd = [
                    "python",
                    SADTALKER_INFERENCE_SCRIPT,
                    "--driven_audio", audio_path,
                    "--source_image", source_image_path,
                    "--result_dir", result_dir,
                    "--enhancer", "gfpgan",
                    "--preprocess", "full",
                    "--still"  # Prevents expression changes
                ]
                
                logging.info(f"[Request {request_id}] Executing SadTalker command: {' '.join(sadtalker_cmd)}")
                
                # Run SadTalker process
                process = subprocess.run(
                    sadtalker_cmd,
                    cwd=SADTALKER_ROOT_DIR,
                    capture_output=True,
                    text=True,
                    check=False
                )
            
            logging.info(f"[Request {request_id}] SadTalker stdout:\n{process.stdout}")
            
            if process.returncode != 0:
                logging.error(f"[Request {request_id}] SadTalker stderr:\n{process.stderr}")
                raise RuntimeError(f"SadTalker inference failed with return code {process.returncode}")
            
            # Find the generated video
            video_files = list(Path(result_dir).glob("*.mp4"))
            if not video_files:
                raise FileNotFoundError(f"No video files found in {result_dir}")
            
            # Return the path to the generated video
            video_path = str(video_files[0])
            logging.info(f"[Request {request_id}] Video generation successful: {video_path}")
            return video_path
        
        except Exception as e:
            logging.error(f"[Request {request_id}] Video generation failed: {str(e)}")
            
            # If there's a fallback video available, use it
            if os.path.exists(FALLBACK_VIDEO):
                fallback_output = os.path.join(MEDIA_DIR, f"talking_head_{request_id}.mp4")
                shutil.copy(FALLBACK_VIDEO, fallback_output)
                logging.info(f"[Request {request_id}] Using fallback video: {fallback_output}")
                return fallback_output
            
            # Re-raise the exception if no fallback is available
            raise
    
    except Exception as e:
        logging.error(f"Error in generate_talking_video: {str(e)}")
        raise

# Example usage (for testing within the module)
if __name__ == "__main__":
    print("Testing generate_talking_video function...")
    # NOTE: This test will likely fail unless SadTalker is correctly installed
    #       at the specified path and configured with checkpoints.
    #       It also relies on the mock TTS.
    test_text = "Hello, this is a test of the talking head generation system."
    print(f"Input text: {test_text}")
    print(f"Using default image: {DEFAULT_FACE_IMAGE}")

    # Check if default image exists before running
    if not os.path.exists(DEFAULT_FACE_IMAGE):
        print(f"Error: Default face image not found at {DEFAULT_FACE_IMAGE}. Cannot run test.")
    # Check if SadTalker script path seems plausible (basic check)
    elif not os.path.exists(SADTALKER_INFERENCE_SCRIPT):
         print(f"Warning: SadTalker inference script not found at {SADTALKER_INFERENCE_SCRIPT}. Test will fail.")
         video_file = None # Skip execution if script missing
    else:
        try:
            video_file = generate_talking_video(test_text)
        except Exception as e:
            print(f"An error occurred during the test: {e}")
            video_file = None

    if video_file and os.path.exists(video_file):
        print(f"\nSuccess! Video generated at: {video_file}")
        # Optional: Clean up the generated test video and its directory
        # result_dir = os.path.dirname(video_file)
        # shutil.rmtree(result_dir)
        # print(f"Cleaned up test output directory: {result_dir}")
    else:
        print("\nVideo generation test failed or produced no output.")
        print("Please ensure SadTalker is installed, configured correctly (paths and checkpoints), and dependencies are met.") 