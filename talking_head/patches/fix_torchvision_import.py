import os
import re
import sys

def patch_torchvision_imports(sadtalker_dir):
    """
    Patch the torchvision imports in the SadTalker dependencies to handle the functional_tensor module changes.
    """
    print(f"Patching torchvision imports in {sadtalker_dir}")
    
    # Define the target file
    basicsr_degradations_path = os.path.join(
        sadtalker_dir, 
        "sadtalker_venv", 
        "Lib", 
        "site-packages", 
        "basicsr", 
        "data",
        "degradations.py"
    )
    
    if not os.path.exists(basicsr_degradations_path):
        print(f"Error: Could not find file at {basicsr_degradations_path}")
        return False
    
    # Read the content of the file
    with open(basicsr_degradations_path, 'r') as f:
        content = f.read()
    
    # Check if we need to modify the file
    if 'from torchvision.transforms.functional_tensor import rgb_to_grayscale' in content:
        # Replace the problematic import
        modified_content = content.replace(
            'from torchvision.transforms.functional_tensor import rgb_to_grayscale',
            '# Original import that causes issues in newer torchvision versions\n'
            '# from torchvision.transforms.functional_tensor import rgb_to_grayscale\n'
            'try:\n'
            '    from torchvision.transforms.functional_tensor import rgb_to_grayscale\n'
            'except ImportError:\n'
            '    try:\n'
            '        from torchvision.transforms.functional import rgb_to_grayscale\n'
            '    except ImportError:\n'
            '        # Fallback implementation if import fails\n'
            '        import torch\n'
            '        def rgb_to_grayscale(img):\n'
            '            # Simple implementation: 0.2989 * R + 0.5870 * G + 0.1140 * B\n'
            '            return img.mul(torch.tensor([0.2989, 0.5870, 0.1140], \n'
            '                                      device=img.device).view(1, 3, 1, 1)).sum(dim=1, keepdim=True)'
        )
        
        # Write the modified content back to the file
        with open(basicsr_degradations_path, 'w') as f:
            f.write(modified_content)
        
        print(f"Successfully patched {basicsr_degradations_path}")
        return True
    else:
        print(f"No need to patch {basicsr_degradations_path} - import not found")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_torchvision_import.py <sadtalker_dir>")
        sys.exit(1)
    
    sadtalker_dir = sys.argv[1]
    if not os.path.exists(sadtalker_dir):
        print(f"Error: SadTalker directory '{sadtalker_dir}' does not exist")
        sys.exit(1)
    
    success = patch_torchvision_imports(sadtalker_dir)
    if success:
        print("Patch applied successfully!")
    else:
        print("No changes were made") 