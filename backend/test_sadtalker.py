import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import the talking head generation function
from talking_head.generate_video import generate_talking_video, DEFAULT_FACE_IMAGE, SADTALKER_ROOT_DIR, SADTALKER_INFERENCE_SCRIPT

def test_sadtalker_setup():
    """Test if SadTalker paths are correctly configured"""
    print("\n=== SadTalker Setup Test ===")
    print(f"SadTalker Root Directory: {SADTALKER_ROOT_DIR}")
    print(f"SadTalker Inference Script: {SADTALKER_INFERENCE_SCRIPT}")
    
    if not os.path.exists(SADTALKER_ROOT_DIR):
        print(f"❌ ERROR: SadTalker directory not found at {SADTALKER_ROOT_DIR}")
        return False
    
    if not os.path.exists(SADTALKER_INFERENCE_SCRIPT):
        print(f"❌ ERROR: SadTalker inference script not found at {SADTALKER_INFERENCE_SCRIPT}")
        return False
    
    # Check for crucial subdirectories
    checkpoints_dir = os.path.join(SADTALKER_ROOT_DIR, "checkpoints")
    if not os.path.exists(checkpoints_dir) or not os.listdir(checkpoints_dir):
        print(f"❌ WARNING: Checkpoints directory is empty or not found at {checkpoints_dir}")
        print("   This might cause SadTalker to fail. Make sure you've downloaded all required models.")
    
    # Check for default face image
    if not os.path.exists(DEFAULT_FACE_IMAGE):
        print(f"❌ WARNING: Default face image not found at {DEFAULT_FACE_IMAGE}")
    else:
        print(f"✅ Default face image found at {DEFAULT_FACE_IMAGE}")
    
    print(f"✅ SadTalker appears to be correctly set up at {SADTALKER_ROOT_DIR}")
    return True

def test_generate_video():
    """Test the actual video generation"""
    print("\n=== Video Generation Test ===")
    test_text = "This is a test of the SadTalker integration. If you hear this, it's working correctly."
    
    try:
        print(f"Generating video for text: '{test_text}'")
        video_path = generate_talking_video(test_text)
        
        if video_path and os.path.exists(video_path):
            print(f"✅ Video successfully generated at: {video_path}")
            return True
        else:
            print("❌ Failed to generate video or video file not found")
            return False
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        return False

if __name__ == "__main__":
    print("=== SadTalker Integration Test ===")
    
    setup_ok = test_sadtalker_setup()
    if setup_ok:
        test_generate_video()
    else:
        print("\n❌ SadTalker setup is incomplete or incorrect. Please fix the issues before testing video generation.") 