import os
import sys
import requests
import subprocess
from tqdm import tqdm
import shutil
import zipfile

"""
Script to download the official SadTalker checkpoints.
This ensures compatibility between model architecture and checkpoint files.
"""

def download_file(url, destination, chunk_size=8192):
    """Download a file from URL to destination with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                bar.update(len(chunk))
    return destination

def get_sadtalker_dir():
    """Get the SadTalker directory path."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Try to locate the SadTalker directory based on common locations
    possible_locations = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "SadTalker"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "SadTalker")
    ]
    
    for loc in possible_locations:
        if os.path.exists(loc):
            return loc
    
    print("Error: Could not locate SadTalker directory. Please provide it as an argument.")
    sys.exit(1)

def download_checkpoints():
    """Download the official SadTalker checkpoints."""
    sadtalker_dir = get_sadtalker_dir()
    print(f"Using SadTalker directory: {sadtalker_dir}")
    
    # Create the checkpoints directory if it doesn't exist
    checkpoints_dir = os.path.join(sadtalker_dir, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)
    
    # Try to use the official download script first
    download_script = os.path.join(sadtalker_dir, "scripts", "download_checkpoints.sh")
    if os.path.exists(download_script):
        print("Found official download script. Attempting to use it...")
        try:
            # On Windows, we'll need to use bash
            if os.name == 'nt':
                # Check if Git Bash is available
                bash_paths = [
                    "C:\\Program Files\\Git\\bin\\bash.exe",
                    "C:\\Program Files (x86)\\Git\\bin\\bash.exe"
                ]
                bash_path = None
                for path in bash_paths:
                    if os.path.exists(path):
                        bash_path = path
                        break
                
                if bash_path:
                    cmd = [bash_path, download_script]
                    subprocess.run(cmd, cwd=sadtalker_dir, check=True)
                    print("Successfully downloaded checkpoints using the official script!")
                    return True
                else:
                    print("Git Bash not found. Falling back to manual download.")
            else:
                # On Unix systems
                subprocess.run(["bash", download_script], cwd=sadtalker_dir, check=True)
                print("Successfully downloaded checkpoints using the official script!")
                return True
        except Exception as e:
            print(f"Error running official download script: {e}")
            print("Falling back to manual download...")
    
    # Manual download from Hugging Face
    print("Downloading checkpoints manually from Hugging Face...")
    
    # URLs for the checkpoints
    checkpoint_urls = {
        "epoch_20.pth": "https://huggingface.co/datasets/OpenTalker/SadTalker/resolve/main/epoch_20.pth",
        "mapping_00109-model.pth.tar": "https://huggingface.co/datasets/OpenTalker/SadTalker/resolve/main/mapping_00109-model.pth.tar",
        "SegNet_v1.pth": "https://huggingface.co/datasets/OpenTalker/SadTalker/resolve/main/SegNet_v1.pth",
    }
    
    # Download each checkpoint file
    for filename, url in checkpoint_urls.items():
        checkpoint_path = os.path.join(checkpoints_dir, filename)
        if os.path.exists(checkpoint_path):
            print(f"{filename} already exists, skipping download.")
            continue
        
        print(f"Downloading {filename}...")
        try:
            download_file(url, checkpoint_path)
            print(f"Successfully downloaded {filename}!")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
    
    # Download and extract GFPGAN checkpoints
    gfpgan_dir = os.path.join(checkpoints_dir, "checkpoints_gfpgan")
    os.makedirs(gfpgan_dir, exist_ok=True)
    
    gfpgan_url = "https://huggingface.co/datasets/OpenTalker/SadTalker/resolve/main/GFPGANv1.4.pth"
    gfpgan_path = os.path.join(gfpgan_dir, "GFPGANv1.4.pth")
    
    if not os.path.exists(gfpgan_path):
        print("Downloading GFPGAN checkpoint...")
        try:
            download_file(gfpgan_url, gfpgan_path)
            print("Successfully downloaded GFPGAN checkpoint!")
        except Exception as e:
            print(f"Error downloading GFPGAN checkpoint: {e}")
    
    print("\nCheckpoint download complete!")
    print(f"All checkpoints should now be available in: {checkpoints_dir}")
    print("\nTo verify compatibility, check that the following files exist:")
    print(f"  - {os.path.join(checkpoints_dir, 'epoch_20.pth')}")
    print(f"  - {os.path.join(checkpoints_dir, 'mapping_00109-model.pth.tar')}")
    print(f"  - {os.path.join(checkpoints_dir, 'SegNet_v1.pth')}")
    print(f"  - {os.path.join(gfpgan_dir, 'GFPGANv1.4.pth')}")
    
    # Verify the downloads
    missing_files = []
    for filename in list(checkpoint_urls.keys()) + ["checkpoints_gfpgan/GFPGANv1.4.pth"]:
        filepath = os.path.join(checkpoints_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        print("\nWarning: The following files are still missing:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nYou may need to download these files manually from the SadTalker repository.")
        return False
    else:
        print("\nAll required checkpoint files are present!")
        return True

if __name__ == "__main__":
    download_checkpoints() 