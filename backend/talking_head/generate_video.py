import os
import subprocess
import uuid
import logging
import shutil
import time
import psutil
import json
from .tts import text_to_speech_mock # Use relative import within the package
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Performance profiling decorator
def profile_execution_time(func):
    """Decorator to profile function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"⏱️ {func.__name__} execution time: {execution_time:.2f} seconds")
        return result
    return wrapper

def check_gpu_availability():
    """Check if GPU is available for acceleration"""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            logging.info(f"🎮 GPU Available: {gpu_name} ({gpu_memory:.1f}GB)")
            return True, gpu_name
        else:
            logging.warning("⚠️ GPU Not Available - Using CPU (slower)")
            return False, "CPU"
    except ImportError:
        logging.warning("⚠️ PyTorch not available - Cannot check GPU")
        return False, "Unknown"

def monitor_system_resources():
    """Monitor system resources during processing"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    available_memory = memory.available / (1024**3)  # GB
    
    logging.info(f"🖥️ System Resources - CPU: {cpu_percent}%, Memory: {memory_percent}% ({available_memory:.1f}GB available)")
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'available_memory_gb': available_memory
    }

def validate_sadtalker_setup():
    """Validate SadTalker setup before execution"""
    sadtalker_dir = ENHANCED_SADTALKER_PATH
    
    # Check if early_compatibility_patch exists
    patch_file = os.path.join(sadtalker_dir, "early_compatibility_patch.py")
    if not os.path.exists(patch_file):
        logging.warning(f"early_compatibility_patch.py not found at {patch_file}")
        return False
    
    # Check if enhanced inference exists
    enhanced_inference_file = os.path.join(sadtalker_dir, "inference_enhanced_with_video.py")
    if not os.path.exists(enhanced_inference_file):
        logging.warning(f"inference_enhanced_with_video.py not found at {enhanced_inference_file}")
        return False
    
    # Check if functional_tensor_patch exists
    functional_patch_file = os.path.join(sadtalker_dir, "functional_tensor_patch.py")
    if not os.path.exists(functional_patch_file):
        logging.warning(f"functional_tensor_patch.py not found at {functional_patch_file}")
        return False
    
    # Check if batch file exists
    if not os.path.exists(SADTALKER_BATCH_FILE):
        logging.warning(f"SadTalker batch file not found at {SADTALKER_BATCH_FILE}")
        return False
    
    logging.info("✅ SadTalker setup validation passed")
    return True

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

# Performance Configuration
PERFORMANCE_MODE = "balanced"  # Options: "fast", "balanced", "quality"
PERFORMANCE_CONFIGS = {
    "fast": {
        "timeout": 900,  # 15 minutes
        "preprocess": "crop",
        "enhancer": "none",
        "size": 256,
        "expression_scale": 1.0
    },
    "balanced": {
        "timeout": 900,  # 15 minutes
        "preprocess": "crop",  # Changed from "full" to "crop" for speed
        "enhancer": "gfpgan",
        "size": 256,
        "expression_scale": 1.0
    },
    "quality": {
        "timeout": 900,  # 15 minutes
        "preprocess": "full",
        "enhancer": "gfpgan",
        "size": 512,
        "expression_scale": 1.0
    }
}

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

@profile_execution_time
def generate_talking_video(text, source_image_path=None, performance_mode=None):
    """
    Generate a talking head video from text input with performance optimization.
    
    Args:
        text (str): The text to be spoken by the talking head.
        source_image_path (str, optional): Path to a custom source image. If None, default face is used.
        performance_mode (str, optional): Performance mode - "fast", "balanced", or "quality"
        
    Returns:
        str: Path to the generated video file.
    """
    try:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Use performance mode configuration
        if performance_mode is None:
            performance_mode = PERFORMANCE_MODE
        
        config = PERFORMANCE_CONFIGS.get(performance_mode, PERFORMANCE_CONFIGS["balanced"])
        
        logging.info(f"[Request {request_id}] Starting video generation for text: '{text[:50]}...'")
        logging.info(f"[Request {request_id}] Performance mode: {performance_mode}")
        logging.info(f"[Request {request_id}] Configuration: {config}")
        
        # System resource monitoring
        system_resources = monitor_system_resources()
        gpu_available, gpu_info = check_gpu_availability()
        
        # Step 1: Generate audio from text
        audio_start_time = time.time()
        logging.info(f"[Request {request_id}] Generating audio...")
        audio_path = text_to_speech_mock(text, request_id)
        audio_duration = time.time() - audio_start_time
        logging.info(f"[Request {request_id}] Audio generated in {audio_duration:.2f}s: {audio_path}")
        
        # Step 2: Create result directory
        result_dir = os.path.join(MEDIA_DIR, f"results_{request_id}")
        os.makedirs(result_dir, exist_ok=True)
        
        # Step 3: Choose source image
        if not source_image_path or not os.path.exists(source_image_path):
            source_image_path = DEFAULT_FACE_IMAGE
            if not os.path.exists(source_image_path):
                raise FileNotFoundError(f"Default face image not found at {source_image_path}")
        
        # Step 4: Validate SadTalker setup before running
        validation_start_time = time.time()
        logging.info(f"[Request {request_id}] Validating SadTalker setup...")
        if not validate_sadtalker_setup():
            raise RuntimeError("SadTalker setup validation failed. Please check the logs for missing components.")
        validation_duration = time.time() - validation_start_time
        logging.info(f"[Request {request_id}] Setup validation completed in {validation_duration:.2f}s")
        
        # Step 5: Run SadTalker to generate video
        sadtalker_start_time = time.time()
        logging.info(f"[Request {request_id}] Starting SadTalker inference...")
        logging.info(f"[Request {request_id}] Source Image: {source_image_path}")
        logging.info(f"[Request {request_id}] Driven Audio: {audio_path}")
        logging.info(f"[Request {request_id}] Result Dir: {result_dir}")
        
        try:
            # Configure SadTalker command with performance optimizations
            logging.info(f"[Request {request_id}] Using direct Python call to avoid batch file hanging")
            
            # Use direct Python call to SadTalker inference script
            sadtalker_script = os.path.join(SADTALKER_ROOT_DIR, "inference_enhanced_with_video.py")
            if os.path.exists(sadtalker_script):
                # Build optimized command with hardcoded fast settings
                sadtalker_cmd = [
                    "python",
                    sadtalker_script,
                    "--driven_audio", audio_path,
                    "--source_image", source_image_path,
                    "--result_dir", result_dir,
                    "--preprocess", "resize",  # Use resize instead of crop for faster processing
                    "--still",  # Prevents expression changes
                    "--cpu",  # Force CPU mode for consistency
                    "--silent",  # Suppress verbose output
                    "--no-interrupt",  # Non-interactive mode
                    "--force-local-models",  # Use local models only
                    "--size", "256",  # Use 256 size for faster processing
                    "--enhancer", "gfpgan"  # Use GFPGAN enhancer
                ]
                
                logging.info(f"[Request {request_id}] Executing SadTalker command: {' '.join(sadtalker_cmd)}")
                logging.info(f"[Request {request_id}] Working directory: {SADTALKER_ROOT_DIR}")
                logging.info(f"[Request {request_id}] Timeout: {config['timeout']} seconds")
                logging.info(f"[Request {request_id}] Starting subprocess...")
                
                # Run SadTalker process with configurable timeout
                process_start_time = time.time()
                process = None
                try:
                    process = subprocess.run(
                        sadtalker_cmd,
                        cwd=SADTALKER_ROOT_DIR,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=config["timeout"]  # Configurable timeout based on performance mode
                    )
                    elapsed_time = time.time() - process_start_time
                    logging.info(f"[Request {request_id}] Subprocess completed in {elapsed_time:.2f} seconds")
                    
                    # Log performance metrics
                    performance_metrics = {
                        "request_id": request_id,
                        "performance_mode": performance_mode,
                        "total_time": elapsed_time,
                        "audio_generation_time": audio_duration,
                        "validation_time": validation_duration,
                        "sadtalker_time": elapsed_time,
                        "gpu_available": gpu_available,
                        "gpu_info": gpu_info,
                        "system_resources": system_resources,
                        "config": config
                    }
                    
                    # Save performance metrics to file
                    metrics_file = os.path.join(result_dir, f"performance_metrics_{request_id}.json")
                    with open(metrics_file, 'w') as f:
                        json.dump(performance_metrics, f, indent=2)
                    
                    logging.info(f"[Request {request_id}] Performance metrics saved to {metrics_file}")
                    
                except subprocess.TimeoutExpired:
                    elapsed_time = time.time() - process_start_time
                    logging.error(f"[Request {request_id}] SadTalker process timed out after {elapsed_time:.2f} seconds")
                    logging.error(f"[Request {request_id}] This may indicate missing dependencies, model issues, or heavy processing")
                    logging.error(f"[Request {request_id}] Consider switching to 'fast' performance mode or checking GPU availability")
                    
                    # Kill the process if it's still running
                    if process and process.poll() is None:
                        try:
                            process.kill()
                            logging.info(f"[Request {request_id}] Terminated timed-out process")
                        except:
                            pass
                    
                    raise RuntimeError(f"SadTalker process timed out after {elapsed_time:.2f} seconds - try 'fast' performance mode or check dependencies")
                    
            else:
                # Fallback to original inference script with optimized settings
                logging.warning(f"[Request {request_id}] Enhanced inference script not found, using fallback")
                sadtalker_cmd = [
                    "python",
                    SADTALKER_INFERENCE_SCRIPT,
                    "--driven_audio", audio_path,
                    "--source_image", source_image_path,
                    "--result_dir", result_dir,
                    "--preprocess", "resize",  # Use resize instead of crop for faster processing
                    "--still",  # Prevents expression changes
                    "--cpu",  # Force CPU mode for consistency
                    "--size", "256",  # Use 256 size for faster processing
                    "--enhancer", "gfpgan"  # Use GFPGAN enhancer
                ]
                
                logging.info(f"[Request {request_id}] Executing SadTalker command: {' '.join(sadtalker_cmd)}")
                logging.info(f"[Request {request_id}] Working directory: {SADTALKER_ROOT_DIR}")
                logging.info(f"[Request {request_id}] Starting subprocess...")
                
                # Run SadTalker process with configurable timeout
                process_start_time = time.time()
                try:
                    process = subprocess.run(
                        sadtalker_cmd,
                        cwd=SADTALKER_ROOT_DIR,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=config["timeout"]  # Configurable timeout based on performance mode
                    )
                    elapsed_time = time.time() - process_start_time
                    logging.info(f"[Request {request_id}] Subprocess completed in {elapsed_time:.2f} seconds")
                except subprocess.TimeoutExpired:
                    elapsed_time = time.time() - process_start_time
                    logging.error(f"[Request {request_id}] SadTalker process timed out after {elapsed_time:.2f} seconds")
                    logging.error(f"[Request {request_id}] This may indicate missing dependencies, model issues, or heavy processing")
                    logging.error(f"[Request {request_id}] Consider switching to 'fast' performance mode or checking GPU availability")
                    raise RuntimeError(f"SadTalker process timed out after {elapsed_time:.2f} seconds - try 'fast' performance mode or check dependencies")
            
            # Log subprocess output for debugging
            if process.stdout:
                logging.info(f"[Request {request_id}] SadTalker stdout:\n{process.stdout}")
            if process.stderr:
                logging.warning(f"[Request {request_id}] SadTalker stderr:\n{process.stderr}")
            
            # Check return code properly with detailed error analysis
            if process.returncode == 1:
                logging.error(f"[Request {request_id}] ❌ SadTalker FAILED with exit code 1")
                logging.error(f"[Request {request_id}] SadTalker stderr:\n{process.stderr}")
                
                # Analyze common error patterns
                stderr_lower = process.stderr.lower() if process.stderr else ""
                if "librosa" in stderr_lower:
                    error_msg = "SadTalker failed - librosa audio processing library missing. Install with: pip install librosa==0.9.2"
                elif "face_alignment" in stderr_lower:
                    error_msg = "SadTalker failed - face_alignment library missing. Install with: pip install face_alignment==1.3.5"
                elif "torch" in stderr_lower:
                    error_msg = "SadTalker failed - PyTorch missing or incompatible. Install with: pip install torch torchvision"
                elif "modulenotfounderror" in stderr_lower:
                    error_msg = "SadTalker failed - missing Python dependencies. Run: pip install -r requirements.txt"
                elif "model" in stderr_lower and ("missing" in stderr_lower or "not found" in stderr_lower):
                    error_msg = "SadTalker failed - model checkpoints missing. Run setup_sadtalker_once.py"
                else:
                    error_msg = "SadTalker inference failed - check logs for specific error details"
                
                logging.error(f"[Request {request_id}] Diagnosis: {error_msg}")
                raise RuntimeError(error_msg)
                
            elif process.returncode == 2:
                logging.warning(f"[Request {request_id}] ⚠️ SadTalker used fallback video (exit code 2)")
                logging.info(f"[Request {request_id}] SadTalker stderr:\n{process.stderr}")
                # Continue execution - fallback video was created
                
            elif process.returncode != 0:
                logging.error(f"[Request {request_id}] ❌ SadTalker failed with unexpected exit code {process.returncode}")
                logging.error(f"[Request {request_id}] SadTalker stderr:\n{process.stderr}")
                error_msg = f"SadTalker inference failed with return code {process.returncode}. Check dependencies and model files."
                raise RuntimeError(error_msg)
            
            # Find the generated video
            video_files = []
            
            # Look for various video file patterns that might be created
            patterns_to_check = [
                "*.mp4",
                "*enhanced*.mp4", 
                "*_full.mp4",
                "fallback_talking_head.mp4"
            ]
            
            for pattern in patterns_to_check:
                found_files = list(Path(result_dir).glob(pattern))
                if found_files:
                    video_files.extend(found_files)
                    break  # Use first pattern that finds files
            
            # Also check parent directory for moved files
            if not video_files:
                parent_dir = os.path.dirname(result_dir)
                for pattern in patterns_to_check:
                    found_files = list(Path(parent_dir).glob(pattern))
                    if found_files:
                        video_files.extend(found_files)
                        break
            
            if not video_files:
                # Check if there's a success file indicating completion
                success_files = list(Path(result_dir).glob("*success*.txt"))
                if success_files:
                    print(f"[Request {request_id}] Found success indicator but no video file")
                    # Look for any video files in subdirectories
                    video_files = list(Path(result_dir).rglob("*.mp4"))
                
                if not video_files:
                    raise FileNotFoundError(f"No video files found in {result_dir}")
            
            # Return the path to the generated video (prefer enhanced/full versions)
            video_path = str(video_files[0])
            
            # Check if this is a fallback video
            is_fallback = "fallback" in os.path.basename(video_path).lower()
            if is_fallback or process.returncode == 2:
                logging.warning(f"[Request {request_id}] ⚠️ FALLBACK VIDEO USED - SadTalker inference failed")
                logging.warning(f"[Request {request_id}] Fallback video path: {video_path}")
                logging.warning(f"[Request {request_id}] This is NOT a successful talking head generation")
            else:
                total_time = time.time() - start_time
                logging.info(f"[Request {request_id}] ✅ ACTUAL SADTALKER SUCCESS: {video_path}")
                logging.info(f"[Request {request_id}] Total generation time: {total_time:.2f} seconds")
            
            return video_path
        
        except Exception as e:
            logging.error(f"[Request {request_id}] Video generation failed: {str(e)}")
            
            # If there's a fallback video available, use it
            if os.path.exists(FALLBACK_VIDEO):
                fallback_output = os.path.join(MEDIA_DIR, f"talking_head_{request_id}.mp4")
                shutil.copy(FALLBACK_VIDEO, fallback_output)
                logging.warning(f"[Request {request_id}] ⚠️ USING EMERGENCY FALLBACK - SadTalker completely failed")
                logging.warning(f"[Request {request_id}] Emergency fallback video: {fallback_output}")
                return fallback_output
            
            # Re-raise the exception if no fallback is available
            raise
    
    except Exception as e:
        logging.error(f"Error in generate_talking_video: {str(e)}")
        raise

# Performance mode selection function
def set_performance_mode(mode):
    """Set the global performance mode"""
    global PERFORMANCE_MODE
    if mode in PERFORMANCE_CONFIGS:
        PERFORMANCE_MODE = mode
        logging.info(f"Performance mode set to: {mode}")
    else:
        logging.warning(f"Invalid performance mode: {mode}. Using default: {PERFORMANCE_MODE}")

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
            # Test with fast performance mode
            video_file = generate_talking_video(test_text, performance_mode="fast")
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