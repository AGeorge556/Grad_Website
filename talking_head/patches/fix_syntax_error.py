import os
import sys

def fix_syntax_error(sadtalker_dir):
    """Fix the syntax error in degradations.py file."""
    degradations_path = os.path.join(
        sadtalker_dir, 
        "sadtalker_venv", 
        "Lib", 
        "site-packages", 
        "basicsr", 
        "data",
        "degradations.py"
    )
    
    if not os.path.exists(degradations_path):
        print(f"Error: Could not find file at {degradations_path}")
        return False

    # Write a clean version of the file
    clean_code = """import cv2
import math
import numpy as np
import random
import torch
from scipy import special
from scipy.stats import multivariate_normal

# Handle torchvision import compatibility
try:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
except ImportError:
    try:
        from torchvision.transforms.functional import rgb_to_grayscale
    except ImportError:
        # Fallback implementation if import fails
        def rgb_to_grayscale(img):
            # Simple implementation: 0.2989 * R + 0.5870 * G + 0.1140 * B
            return img.mul(torch.tensor([0.2989, 0.5870, 0.1140], 
                                       device=img.device).view(1, 3, 1, 1)).sum(dim=1, keepdim=True)

# -------------------------------------------------------------------- #"""

    # Read the file to get content after our marker
    with open(degradations_path, 'r') as f:
        content = f.read()
    
    # Find the position of the marker
    marker = "# -------------------------------------------------------------------- #"
    marker_pos = content.find(marker)
    
    if marker_pos == -1:
        print("Could not find the marker in the file")
        return False
    
    # Get all content from the marker onwards
    rest_of_file = content[marker_pos:]
    
    # Combine the clean code with the rest of the file
    with open(degradations_path, 'w') as f:
        f.write(clean_code + rest_of_file)
    
    print(f"Successfully fixed syntax error in {degradations_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_syntax_error.py <sadtalker_dir>")
        sys.exit(1)
    
    sadtalker_dir = sys.argv[1]
    if not os.path.exists(sadtalker_dir):
        print(f"Error: SadTalker directory '{sadtalker_dir}' does not exist")
        sys.exit(1)
    
    success = fix_syntax_error(sadtalker_dir)
    if success:
        print("Syntax error fixed successfully!")
    else:
        print("Failed to fix syntax error") 