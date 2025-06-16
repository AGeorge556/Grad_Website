import os
import sys
import subprocess
import platform

def install_dependencies(sadtalker_dir):
    """
    Install the necessary dependencies for SadTalker in the Python 3.10 environment.
    """
    print(f"Installing dependencies in {sadtalker_dir}")
    
    # Verify the environment
    venv_path = os.path.join(sadtalker_dir, "sadtalker_venv")
    if not os.path.exists(venv_path):
        print(f"Error: Virtual environment not found at {venv_path}")
        return False
    
    # Determine the Python executable path
    if platform.system() == "Windows":
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe = os.path.join(venv_path, "bin", "python")
    
    if not os.path.exists(python_exe):
        print(f"Error: Python executable not found at {python_exe}")
        return False
    
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install compatible versions of torch and torchvision
    print("Installing compatible torch and torchvision...")
    subprocess.run([
        python_exe, "-m", "pip", "install", 
        "torch==1.13.1", 
        "torchvision==0.14.1"
    ], check=True)
    
    # Install other required packages
    print("Installing other required packages...")
    required_packages = [
        "scipy==1.10.1",
        "librosa==0.9.2",
        "numpy==1.23.4",
        "imageio==2.19.3",
        "tqdm",
        "yacs",
        "pyyaml",
        "face-alignment==1.3.5",
        "kornia==0.6.8",
        "basicsr",
        "gfpgan"
    ]
    
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([python_exe, "-m", "pip", "install", package], check=True)
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to install {package}, continuing anyway...")
    
    print("All dependencies installed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python install_dependencies.py <sadtalker_dir>")
        sys.exit(1)
    
    sadtalker_dir = sys.argv[1]
    if not os.path.exists(sadtalker_dir):
        print(f"Error: SadTalker directory '{sadtalker_dir}' does not exist")
        sys.exit(1)
    
    success = install_dependencies(sadtalker_dir)
    if success:
        print("Dependencies installed successfully!")
    else:
        print("Failed to install dependencies") 