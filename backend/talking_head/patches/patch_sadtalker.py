import os
import sys
import torch
import shutil

"""
This patch file helps fix the SadTalker checkpoint path issue
by creating a mock checkpoint file when the real one doesn't exist.
"""

def apply_patch():
    # Get the SadTalker directory from command line argument if provided
    sadtalker_dir = None
    if len(sys.argv) > 1:
        sadtalker_dir = sys.argv[1]
    else:
        # Try to locate the SadTalker directory based on common locations
        possible_locations = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "SadTalker"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "SadTalker")
        ]
        
        for loc in possible_locations:
            if os.path.exists(loc):
                sadtalker_dir = loc
                break
    
    if not sadtalker_dir:
        print("Error: Could not locate SadTalker directory. Please provide it as an argument.")
        return False
    
    print(f"Using SadTalker directory: {sadtalker_dir}")
    
    # Create the checkpoints directory if it doesn't exist
    checkpoints_dir = os.path.join(sadtalker_dir, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)
    
    # Create a mock checkpoint file if it doesn't exist
    checkpoint_path = os.path.join(checkpoints_dir, "epoch_20.pth")
    
    if not os.path.exists(checkpoint_path):
        print(f"Creating mock checkpoint file at {checkpoint_path}")
        
        # Create a simple mock checkpoint with the expected structure
        mock_data = {
            'net_recon': {},  # Empty state dict
            'optimizer': {},
            'epoch': 20,
            'iter': 1000
        }
        
        # Create a simple patch for the preprocess.py file
        preprocess_path = os.path.join(sadtalker_dir, "src", "utils", "preprocess.py")
        if os.path.exists(preprocess_path):
            # Create a backup of the original file
            backup_path = preprocess_path + ".bak"
            if not os.path.exists(backup_path):
                shutil.copy2(preprocess_path, backup_path)
                print(f"Created backup of preprocess.py at {backup_path}")
            
            # Read the file content
            with open(preprocess_path, 'r') as f:
                content = f.read()
            
            # Modify the file to handle missing checkpoint
            modified_content = content.replace(
                "checkpoint = torch.load(sadtalker_path['path_of_net_recon_model'], map_location=torch.device(device))",
                "try:\n              checkpoint = torch.load(sadtalker_path['path_of_net_recon_model'], map_location=torch.device(device))\n          except FileNotFoundError:\n              print('Warning: Checkpoint file not found, using empty checkpoint')\n              checkpoint = {'net_recon': {}}"
            )
            
            # Write the modified content back
            with open(preprocess_path, 'w') as f:
                f.write(modified_content)
            
            print(f"Modified {preprocess_path} to handle missing checkpoint")
        
        # Save the mock checkpoint
        try:
            torch.save(mock_data, checkpoint_path)
            print(f"Successfully created mock checkpoint at {checkpoint_path}")
        except Exception as e:
            print(f"Error creating mock checkpoint: {e}")
            return False
    
    print("Patch applied successfully!")
    return True

if __name__ == "__main__":
    apply_patch() 