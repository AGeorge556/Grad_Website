import sys
from pathlib import Path

# Get site-packages directory
site_packages = Path(sys.prefix) / 'Lib' / 'site-packages'
print(f"Site packages directory: {site_packages}")

# Create the patch file
patch_file = site_packages / 'functional_tensor_patch.py'
patch_content = '''"""
Compatibility layer for torchvision.transforms.functional_tensor
This recreates the rgb_to_grayscale function used by SadTalker
"""

import torch

def rgb_to_grayscale(img, num_output_channels=1):
    """Convert RGB image to grayscale."""
    if img.shape[0] != 3:
        raise TypeError("Input image tensor should have 3 channels")
    
    # Use the ITU-R BT.601 coefficients for RGB to grayscale conversion
    r, g, b = img.unbind(0)
    l_img = (0.299 * r + 0.587 * g + 0.114 * b).unsqueeze(0)
    
    if num_output_channels == 1:
        return l_img
    
    return l_img.repeat(3, 1, 1)
'''

print(f"Creating patch file at {patch_file}")
with open(patch_file, 'w') as f:
    f.write(patch_content)

# Find the basicsr degradations file
basicsr_dir = site_packages / 'basicsr'
degradations_file = basicsr_dir / 'data' / 'degradations.py'

if not degradations_file.exists():
    print(f"Could not find {degradations_file}")
    sys.exit(1)

print(f"Found degradations file at {degradations_file}")

# Create backup
backup_file = degradations_file.with_suffix('.py.bak')
if not backup_file.exists():
    print(f"Creating backup at {backup_file}")
    with open(degradations_file, 'r') as f:
        content = f.read()
    with open(backup_file, 'w') as f:
        f.write(content)
else:
    print(f"Backup already exists at {backup_file}")

# Read the file
with open(degradations_file, 'r') as f:
    lines = f.readlines()

# Check if patching is needed
need_patching = False
for line in lines:
    if 'from torchvision.transforms.functional_tensor import rgb_to_grayscale' in line:
        need_patching = True
        break

if not need_patching:
    print("File already patched or doesn't need patching")
    sys.exit(0)

# Modify the file
print("Patching the file...")
for i, line in enumerate(lines):
    if 'from torchvision.transforms.functional_tensor import rgb_to_grayscale' in line:
        lines[i] = '# Original: from torchvision.transforms.functional_tensor import rgb_to_grayscale\n'
        lines.insert(i+1, 'from functional_tensor_patch import rgb_to_grayscale  # Compatibility layer\n')
        break

# Write the modified file
with open(degradations_file, 'w') as f:
    f.writelines(lines)

print("Patch applied successfully!") 