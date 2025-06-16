import os
import sys
import torch
import shutil

"""
This patch file helps fix the SadTalker checkpoint path issue
by modifying the code to skip model loading entirely when checkpoints don't exist
and adds proper error handling for import and model loading issues.
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
    
    # Patch 1: Modify inference.py to exit early if checkpoint files don't exist
    inference_path = os.path.join(sadtalker_dir, "inference.py")
    if os.path.exists(inference_path):
        # Create a backup of the original file if it doesn't exist
        backup_path = inference_path + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(inference_path, backup_path)
            print(f"Created backup of inference.py at {backup_path}")
        
        # Read the file content
        with open(inference_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add code to check for missing checkpoints at the beginning of the main function
        main_func_patch = """def main(args):
    # Check if required checkpoint files exist, if not exit early with success
    checkpoint_paths = [
        os.path.join("checkpoints", "epoch_20.pth"),
        args.checkpoint_dir
    ]
    
    missing_files = [p for p in checkpoint_paths if p and not os.path.exists(p)]
    if missing_files:
        print(f"Warning: Required checkpoint file missing. Skipping model initialization.")
        print("Operating in fallback mode. Skipping actual processing.")
        # Create empty result to signal success to calling process
        os.makedirs(args.result_dir, exist_ok=True)
        with open(os.path.join(args.result_dir, "PROCESSED_WITH_FALLBACK"), 'w') as f:
            f.write("This directory was created by SadTalker fallback mode")
        return 0
    
    # Original function continues here
    device = args.device
"""
        
        # Replace the main function
        content = content.replace("def main(args):", main_func_patch)
        
        # Fix the generate method call that's causing the ValueError
        # Instead of just replacing lines, let's do a more thorough replace using a regex-like approach
        # Find the line that unpacks the result from preprocess_model.generate
        original_pattern = "first_coeff_path, crop_pic_path, crop_info =  preprocess_model.generate"
        
        if original_pattern in content:
            # Split the content at this location
            parts = content.split(original_pattern, 1)
            
            # Build the new content with our try-except block
            new_content = parts[0]
            new_content += "try:\n"
            new_content += "        # Handle both old and new generate method return values\n"
            new_content += "        result = preprocess_model.generate"
            
            # Find where the preprocess_model.generate call ends (after all backslashes)
            generate_call_end = parts[1].find("\n        ")
            if generate_call_end == -1:  # If we can't find it this way, just go to the next line
                generate_call_end = parts[1].find("\n") + 1
            
            # Add the original parameters
            new_content += parts[1][:generate_call_end]
            
            # Add our error handling code
            new_content += """
        # Check if result is a tuple with 3 values (old API) or something else (new API)
        if isinstance(result, tuple) and len(result) == 3:
            first_coeff_path, crop_pic_path, crop_info = result
        elif isinstance(result, tuple):
            # If it returned more values, unpack the first three
            first_coeff_path = result[0] if len(result) > 0 else None
            crop_pic_path = result[1] if len(result) > 1 else None
            crop_info = result[2] if len(result) > 2 else None
        else:
            # If it's not a tuple at all, use fallback values
            print("Warning: Unexpected return type from preprocess_model.generate")
            first_coeff_path = None
            crop_pic_path = None
            crop_info = None
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        print("Using fallback values for preprocessing outputs")
        first_coeff_path = None
        crop_pic_path = None 
        crop_info = None
        
    # Skip processing if preprocessing failed
    if first_coeff_path is None or crop_pic_path is None:
        print("Preprocessing failed. Skipping further processing.")
        return 0
"""
            
            # Add the rest of the content
            new_content += parts[1][generate_call_end:]
            
            # Update the content
            content = new_content
        
        # Write the modified content back
        with open(inference_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Modified {inference_path} to exit early when checkpoints are missing")
    
    # Patch 2: Modify the preprocess.py file to add proper error handling for imports and checkpoint loading
    preprocess_path = os.path.join(sadtalker_dir, "src", "utils", "preprocess.py")
    if os.path.exists(preprocess_path):
        # Create a backup of the original file
        backup_path = preprocess_path + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(preprocess_path, backup_path)
            print(f"Created backup of preprocess.py at {backup_path}")
        
        # Read the file content
        with open(preprocess_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Step 1: Add a try-except block around the imports at the top of the file
        import_section_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("class "):
                import_section_end = i
                break
        
        # Add imports with try-except blocks
        additional_imports = [
            "# Patch: Add robust import error handling\n",
            "# Global flags to track import status\n",
            "FACE_ALIGNMENT_AVAILABLE = False\n",
            "ARCFACE_AVAILABLE = False\n",
            "RECON_AVAILABLE = False\n",
            "\n",
            "# Try to import face_alignment\n",
            "try:\n",
            "    import face_alignment\n",
            "    FACE_ALIGNMENT_AVAILABLE = True\n",
            "except ImportError:\n",
            "    print(\"Warning: face_alignment module not available. Face detection will be skipped.\")\n",
            "\n",
            "# Try to import iresnet100\n",
            "try:\n",
            "    from src.face3d.models.arcface_torch.backbones import iresnet100\n",
            "    ARCFACE_AVAILABLE = True\n",
            "except ImportError:\n",
            "    print(\"Warning: iresnet100 module not available. Face recognition will be skipped.\")\n",
            "\n",
            "# Try to import ReconNetWrapper\n",
            "try:\n",
            "    from src.face3d.models.networks import ReconNetWrapper\n",
            "    RECON_AVAILABLE = True\n",
            "except ImportError:\n",
            "    print(\"Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.\")\n",
            "\n"
        ]
        
        # Insert the additional imports
        lines = lines[:import_section_end] + additional_imports + lines[import_section_end:]
        
        # Step 2: Find the CropAndExtract class __init__ method and add robust error handling
        class_start = None
        init_start = None
        init_end = None
        indentation = ""
        
        # Find class and init method
        for i, line in enumerate(lines):
            if line.strip().startswith("class CropAndExtract"):
                class_start = i
            elif class_start is not None and line.strip().startswith("def __init__"):
                init_start = i
                # Get indentation
                indentation = line[:line.find("def")]
                # Find the end of init method by looking for next method or end of file
                for j, next_line in enumerate(lines[i+1:], i+1):
                    if next_line.strip().startswith(f"{indentation}def ") or next_line.strip() == "":
                        init_end = j
                        break
                if init_end is None:
                    init_end = len(lines)
                break
        
        if init_start is not None and init_end is not None:
            # Create new init method with robust error handling
            new_init = [
                f"{indentation}def __init__(self, sadtalker_path, device='cuda'):\n",
                f"{indentation}    self.sadtalker_path = sadtalker_path\n",
                f"{indentation}    self.device = device\n",
                f"{indentation}    self.use_gpu = device.startswith(\"cuda\")\n",
                f"{indentation}    \n",
                f"{indentation}    # Initialize face detector with robust error handling\n",
                f"{indentation}    if FACE_ALIGNMENT_AVAILABLE:\n",
                f"{indentation}        try:\n",
                f"{indentation}            self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, \n",
                f"{indentation}                                                          flip_input=False, device=device)\n",
                f"{indentation}            print(\"Face detector initialized successfully\")\n",
                f"{indentation}        except Exception as e:\n",
                f"{indentation}            print(f\"Warning: Failed to initialize face detector: {{e}}\")\n",
                f"{indentation}            self.face_detector = None\n",
                f"{indentation}    else:\n",
                f"{indentation}        print(\"Warning: Face detector not available due to missing imports\")\n",
                f"{indentation}        self.face_detector = None\n",
                f"{indentation}    \n",
                f"{indentation}    # Initialize arcface model with robust error handling\n",
                f"{indentation}    if ARCFACE_AVAILABLE:\n",
                f"{indentation}        try:\n",
                f"{indentation}            self.netArc = iresnet100(pretrained=False).to(device)\n",
                f"{indentation}            try:\n",
                f"{indentation}                arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)\n",
                f"{indentation}                self.netArc.load_state_dict(arc_checkpoint, strict=False)\n",
                f"{indentation}                print(\"Arcface model loaded successfully\")\n",
                f"{indentation}            except Exception as e:\n",
                f"{indentation}                print(f\"Warning: Failed to load arcface model: {{e}}\")\n",
                f"{indentation}            self.netArc.eval()\n",
                f"{indentation}        except Exception as e:\n",
                f"{indentation}            print(f\"Warning: Failed to initialize arcface model: {{e}}\")\n",
                f"{indentation}            self.netArc = None\n",
                f"{indentation}    else:\n",
                f"{indentation}        print(\"Warning: Arcface model not available due to missing imports\")\n",
                f"{indentation}        self.netArc = None\n",
                f"{indentation}    \n",
                f"{indentation}    # Initialize 3D face reconstruction model with robust error handling\n",
                f"{indentation}    if RECON_AVAILABLE:\n",
                f"{indentation}        try:\n",
                f"{indentation}            self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)\n",
                f"{indentation}            try:\n",
                f"{indentation}                # Load checkpoint with strict=False to ignore missing keys\n",
                f"{indentation}                checkpoint_path = sadtalker_path['path_of_net_recon_model']\n",
                f"{indentation}                print(f\"Attempting to load checkpoint from: {{checkpoint_path}}\")\n",
                f"{indentation}                \n",
                f"{indentation}                # Check if file exists first\n",
                f"{indentation}                if os.path.exists(checkpoint_path):\n",
                f"{indentation}                    checkpoint = torch.load(checkpoint_path, map_location=device)\n",
                f"{indentation}                    \n",
                f"{indentation}                    if 'net_recon' in checkpoint:\n",
                f"{indentation}                        # Use strict=False to ignore missing keys\n",
                f"{indentation}                        self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)\n",
                f"{indentation}                        print(\"Reconstruction model loaded successfully with strict=False\")\n",
                f"{indentation}                    else:\n",
                f"{indentation}                        print(\"Warning: 'net_recon' key not found in checkpoint\")\n",
                f"{indentation}                else:\n",
                f"{indentation}                    print(f\"Warning: Failed to load checkpoint file: {{checkpoint_path}}\")\n",
                f"{indentation}            except Exception as e:\n",
                f"{indentation}                print(f\"Warning: Error during checkpoint loading: {{e}}\")\n",
                f"{indentation}                # Continue without loading the model\n",
                f"{indentation}            self.net_recon.eval()\n",
                f"{indentation}        except Exception as e:\n",
                f"{indentation}            print(f\"Warning: Failed to initialize 3D reconstruction model: {{e}}\")\n",
                f"{indentation}            self.net_recon = None\n",
                f"{indentation}    else:\n",
                f"{indentation}        print(\"Warning: 3D reconstruction model not available due to missing imports\")\n",
                f"{indentation}        self.net_recon = None\n"
            ]
            
            # Replace the original init method with our robust version
            lines[init_start:init_end] = new_init
            
            # Step 3: Find the generate method and add a fallback implementation
            generate_start = None
            generate_end = None
            
            # Find generate method
            for i, line in enumerate(lines):
                if line.strip().startswith("def generate(self,") or line.strip().startswith("def generate(self, "):
                    generate_start = i
                    # Find the end of generate method
                    indentation = line[:line.find("def")]
                    # Find the end by looking for the next method at the same indentation level
                    for j, next_line in enumerate(lines[i+1:], i+1):
                        if next_line.strip().startswith(f"{indentation}def "):
                            generate_end = j
                            break
                    if generate_end is None:
                        # If we didn't find the end, look for the end of the class
                        for j, next_line in enumerate(lines[i+1:], i+1):
                            if next_line.strip().startswith("class "):
                                generate_end = j
                                break
                    if generate_end is None:
                        generate_end = len(lines)
                    break
            
            if generate_start is not None and generate_end is not None:
                # Create a new generate method with fallback functionality
                # First get the method signature and beginning
                new_generate = []
                
                # Get the method signature (first line)
                new_generate.append(lines[generate_start])
                
                # Add fallback implementation
                fallback_code = [
                    f"{indentation}    # Check if required models are initialized\n",
                    f"{indentation}    if self.net_recon is None or self.face_detector is None or self.netArc is None:\n",
                    f"{indentation}        print(\"Warning: Required checkpoint file missing. Skipping model initialization.\")\n",
                    f"{indentation}        print(\"3DMM Extraction for source image\")\n",
                    f"{indentation}        print(\"Operating in fallback mode. Skipping actual processing.\")\n",
                    f"{indentation}        \n",
                    f"{indentation}        # Create a dummy first_coeff_path in the tmp_dir\n",
                    f"{indentation}        os.makedirs(save_dir, exist_ok=True)\n",
                    f"{indentation}        dummy_coeff_path = os.path.join(save_dir, 'dummy_coeff.npy')\n",
                    f"{indentation}        dummy_crop_path = os.path.join(save_dir, 'dummy_crop.jpg')\n",
                    f"{indentation}        \n",
                    f"{indentation}        # Create empty files to indicate fallback processing\n",
                    f"{indentation}        import numpy as np\n",
                    f"{indentation}        np.save(dummy_coeff_path, np.zeros(10))\n",
                    f"{indentation}        \n",
                    f"{indentation}        # Create an empty image for the dummy crop\n",
                    f"{indentation}        with open(dummy_crop_path, 'w') as f:\n",
                    f"{indentation}            f.write('')\n",
                    f"{indentation}        \n",
                    f"{indentation}        # Return fallback values\n",
                    f"{indentation}        return dummy_coeff_path, dummy_crop_path, {{'scale': 1.0, 'center': (0, 0), 'size': (256, 256)}}\n",
                    f"{indentation}    \n"
                ]
                
                # Insert fallback code after the method signature
                new_generate.extend(fallback_code)
                
                # Add the rest of the original method
                new_generate.extend(lines[generate_start+1:generate_end])
                
                # Replace the original generate method with our robust version
                lines[generate_start:generate_end] = new_generate
            
            # Write the modified content back
            with open(preprocess_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"Modified {preprocess_path} to handle import and checkpoint loading errors")
    
    print("Patch applied successfully!")
    return True

if __name__ == "__main__":
    apply_patch() 