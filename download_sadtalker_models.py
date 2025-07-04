import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path
import hashlib

def download_file(url, destination, expected_hash=None):
    """Download a file with progress indication and hash verification."""
    try:
        print(f"Downloading {url} to {destination}")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for download errors
        
        # Get file size for progress reporting
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Download with progress
        with open(destination, 'wb') as file:
            downloaded = 0
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded += len(data)
                # Show progress
                done = int(50 * downloaded / total_size) if total_size > 0 else 0
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded/1024/1024:.1f}MB")
                sys.stdout.flush()
            print()  # New line after progress bar
        
        # Verify hash if provided
        if expected_hash:
            file_hash = calculate_sha256(destination)
            if file_hash != expected_hash:
                print(f"Warning: Hash mismatch for {destination}")
                print(f"Expected: {expected_hash}")
                print(f"Got: {file_hash}")
                return False
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract a zip file."""
    try:
        print(f"Extracting {zip_path} to {extract_to}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
        return False

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    # Create directories
    checkpoints_dir = Path("checkpoints")
    gfpgan_weights_dir = Path("gfpgan/weights")
    
    os.makedirs(checkpoints_dir, exist_ok=True)
    os.makedirs(gfpgan_weights_dir, exist_ok=True)
    
    # Define model files to download
    legacy_models = [
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/auido2exp_00300-model.pth", 
         checkpoints_dir / "auido2exp_00300-model.pth"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/auido2pose_00140-model.pth", 
         checkpoints_dir / "auido2pose_00140-model.pth"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth", 
         checkpoints_dir / "epoch_20.pth"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/facevid2vid_00189-model.pth.tar", 
         checkpoints_dir / "facevid2vid_00189-model.pth.tar"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/shape_predictor_68_face_landmarks.dat", 
         checkpoints_dir / "shape_predictor_68_face_landmarks.dat"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/wav2lip.pth", 
         checkpoints_dir / "wav2lip.pth"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/hub.zip", 
         checkpoints_dir / "hub.zip"),
        ("https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/BFM_Fitting.zip", 
         checkpoints_dir / "BFM_Fitting.zip"),
    ]
    
    new_models = [
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar", 
         checkpoints_dir / "mapping_00109-model.pth.tar"),
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar", 
         checkpoints_dir / "mapping_00229-model.pth.tar"),
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors", 
         checkpoints_dir / "SadTalker_V0.0.2_256.safetensors"),
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors", 
         checkpoints_dir / "SadTalker_V0.0.2_512.safetensors"),
    ]
    
    gfpgan_models = [
        ("https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth", 
         gfpgan_weights_dir / "alignment_WFLW_4HG.pth"),
        ("https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth", 
         gfpgan_weights_dir / "detection_Resnet50_Final.pth"),
        ("https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth", 
         gfpgan_weights_dir / "GFPGANv1.4.pth"),
        ("https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth", 
         gfpgan_weights_dir / "parsing_parsenet.pth"),
    ]
    
    # Download legacy models
    print("\n== Downloading Legacy SadTalker Models ==")
    for url, path in legacy_models:
        if not path.exists() or path.stat().st_size == 0:
            success = download_file(url, path)
            if not success:
                print(f"Failed to download {path.name}")
        else:
            print(f"File {path.name} already exists, skipping download")
    
    # Extract zip files
    for zip_file in [checkpoints_dir / "hub.zip", checkpoints_dir / "BFM_Fitting.zip"]:
        if zip_file.exists():
            extract_zip(zip_file, checkpoints_dir)
    
    # Download new models
    print("\n== Downloading New SadTalker Models ==")
    for url, path in new_models:
        if not path.exists() or path.stat().st_size == 0:
            success = download_file(url, path)
            if not success:
                print(f"Failed to download {path.name}")
        else:
            print(f"File {path.name} already exists, skipping download")
    
    # Download GFPGAN models
    print("\n== Downloading GFPGAN Enhancer Models ==")
    for url, path in gfpgan_models:
        if not path.exists() or path.stat().st_size == 0:
            success = download_file(url, path)
            if not success:
                print(f"Failed to download {path.name}")
        else:
            print(f"File {path.name} already exists, skipping download")
    
    # Verify all files exist
    print("\n== Verifying Downloads ==")
    all_files = [path for _, path in legacy_models + new_models + gfpgan_models 
                if not str(path).endswith('.zip')]
    
    missing_files = []
    for file_path in all_files:
        if not file_path.exists() or file_path.stat().st_size == 0:
            missing_files.append(file_path)
    
    if missing_files:
        print("The following files are missing or empty:")
        for file in missing_files:
            print(f" - {file}")
        print("\nYou may need to download these files manually.")
    else:
        print("All model files have been downloaded successfully!")
    
    print("\nIf you're still experiencing errors, make sure these files are in the correct directory structure:")
    print(" - SadTalker models should be in the './checkpoints' directory")
    print(" - GFPGAN models should be in the './gfpgan/weights' directory")
    
    # Non-interactive mode: removed input() for backend compatibility

if __name__ == "__main__":
    main()
