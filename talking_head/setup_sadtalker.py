import os
import sys
import subprocess
import platform
from pathlib import Path

def setup_sadtalker():
    """
    Set up the SadTalker environment with all necessary patches and dependencies.
    """
    print("Setting up SadTalker environment...")
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Get the SadTalker directory (3 levels up from talking_head/patches)
    sadtalker_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "SadTalker")
    
    if not os.path.exists(sadtalker_dir):
        print(f"Error: SadTalker directory not found at {sadtalker_dir}")
        return False
    
    print(f"Found SadTalker at: {sadtalker_dir}")
    
    # Ensure the Python 3.10 virtual environment exists
    venv_path = os.path.join(sadtalker_dir, "sadtalker_venv")
    
    if not os.path.exists(venv_path):
        print(f"Creating new Python 3.10 virtual environment at {venv_path}...")
        
        # Find Python 3.10
        python310_paths = [
            r"C:\Users\Andrew George\AppData\Local\Programs\Python\Python310\python.exe",
            r"C:\Python310\python.exe",
            "/usr/bin/python3.10",
            "/usr/local/bin/python3.10"
        ]
        
        python310_exe = None
        for path in python310_paths:
            if os.path.exists(path):
                python310_exe = path
                break
        
        if not python310_exe:
            print("Error: Could not find Python 3.10 installation")
            return False
        
        print(f"Using Python 3.10 from: {python310_exe}")
        
        # Create the virtual environment
        try:
            subprocess.run([python310_exe, "-m", "venv", venv_path], check=True)
            print(f"Created virtual environment at {venv_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return False
    else:
        print(f"Using existing virtual environment at {venv_path}")
    
    # Run the dependency installation script
    print("Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, 
            os.path.join(current_dir, "patches", "install_dependencies.py"), 
            sadtalker_dir
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("Continuing with setup anyway...")
    
    # Run the torchvision import patch
    print("Applying torchvision import patch...")
    try:
        subprocess.run([
            sys.executable, 
            os.path.join(current_dir, "patches", "fix_torchvision_import.py"), 
            sadtalker_dir
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error applying torchvision import patch: {e}")
        print("Continuing with setup anyway...")
        
    # Fix duplicated imports
    print("Fixing duplicated imports...")
    try:
        subprocess.run([
            sys.executable, 
            os.path.join(current_dir, "patches", "fix_duplicated_imports.py"), 
            sadtalker_dir
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error fixing duplicated imports: {e}")
        print("Continuing with setup anyway...")
    
    # Run the SadTalker checkpoint patch
    print("Applying SadTalker checkpoint patch...")
    try:
        subprocess.run([
            sys.executable, 
            os.path.join(current_dir, "patches", "patch_sadtalker.py"), 
            sadtalker_dir
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error applying SadTalker checkpoint patch: {e}")
        print("Continuing with setup anyway...")
    
    print("\nSadTalker environment setup complete!")
    print("\nTo test the talking head feature:")
    print("1. Go to http://localhost:5174 in your browser")
    print("2. Navigate to the Text-to-Talking Head component")
    print("3. Enter some text and click 'Generate Talking Head Video'")
    
    return True

if __name__ == "__main__":
    success = setup_sadtalker()
    if not success:
        print("Setup failed")
        sys.exit(1)
    
    print("Setup completed successfully!") 