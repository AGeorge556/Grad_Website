import os
import sys

def fix_degradations_file(sadtalker_dir):
    """
    Fix the duplicated imports in the degradations.py file.
    """
    print(f"Fixing degradations.py in {sadtalker_dir}")
    
    # Define the target file
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
    
    # Read the original file
    with open(degradations_path, 'r') as f:
        content = f.read()
    
    # Replace all the problematic import section with a clean implementation
    # Find the position right after the initial imports
    import_end_pos = content.find("# -------------------------------------------------------------------- #")
    
    if import_end_pos == -1:
        print("Could not find the marker for end of imports")
        return False
    
    # Get the initial imports (before our modifications)
    initial_imports = """import cv2
import math
import numpy as np
import random
import torch
from scipy import special
from scipy.stats import multivariate_normal"""
    
    # Add the clean rgb_to_grayscale implementation
    clean_implementation = """
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
"""
    
    # Get the rest of the file (after our modifications)
    rest_of_file = content[import_end_pos:]
    
    # Combine everything
    fixed_content = initial_imports + clean_implementation + rest_of_file
    
    # Write the fixed content back to the file
    with open(degradations_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Successfully fixed {degradations_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_duplicated_imports.py <sadtalker_dir>")
        sys.exit(1)
    
    sadtalker_dir = sys.argv[1]
    if not os.path.exists(sadtalker_dir):
        print(f"Error: SadTalker directory '{sadtalker_dir}' does not exist")
        sys.exit(1)
    
    success = fix_degradations_file(sadtalker_dir)
    if success:
        print("Degradations file fixed successfully!")
    else:
        print("Failed to fix degradations file") 