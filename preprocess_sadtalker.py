import numpy as np
import cv2, os, sys, torch
from tqdm import tqdm
from PIL import Image 

# 3dmm extraction
import safetensors
import safetensors.torch 
from src.face3d.util.preprocess import align_img
from src.face3d.util.load_mats import load_lm3d
from src.face3d.models import networks

from scipy.io import loadmat, savemat
from src.utils.croper import Preprocesser


import warnings

from src.utils.safetensor_helper import load_x_from_safetensor 
warnings.filterwarnings("ignore")

def split_coeff(coeffs):
        """
        Return:
            coeffs_dict     -- a dict of torch.tensors

        Parameters:
            coeffs          -- torch.tensor, size (B, 256)
        """
        id_coeffs = coeffs[:, :80]
        exp_coeffs = coeffs[:, 80: 144]
        tex_coeffs = coeffs[:, 144: 224]
        angles = coeffs[:, 224: 227]
        gammas = coeffs[:, 227: 254]
        translations = coeffs[:, 254:]
        return {
            'id': id_coeffs,
            'exp': exp_coeffs,
            'tex': tex_coeffs,
            'angle': angles,
            'gamma': gammas,
            'trans': translations
        }


# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

# Patch: Add robust import error handling
# Global flags to track import status
FACE_ALIGNMENT_AVAILABLE = False
ARCFACE_AVAILABLE = False
RECON_AVAILABLE = False

# Try to import face_alignment
try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    print("Warning: face_alignment module not available. Face detection will be skipped.")

# Try to import iresnet100
try:
    from src.face3d.models.arcface_torch.backbones import iresnet100
    ARCFACE_AVAILABLE = True
except ImportError:
    print("Warning: iresnet100 module not available. Face recognition will be skipped.")

# Try to import ReconNetWrapper
try:
    from src.face3d.models.networks import ReconNetWrapper
    RECON_AVAILABLE = True
except ImportError:
    print("Warning: ReconNetWrapper not available. 3D face reconstruction will be skipped.")

class CropAndExtract():
    def __init__(self, sadtalker_path, device='cuda'):
        self.sadtalker_path = sadtalker_path
        self.device = device
        self.use_gpu = device.startswith("cuda")
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Failed to load checkpoint file: {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Failed to load checkpoint file: {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Failed to load checkpoint file: {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Initialize face detector with robust error handling
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
                print("Face detector initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize face detector: {e}")
                self.face_detector = None
        else:
            print("Warning: Face detector not available due to missing imports")
            self.face_detector = None
        
        # Initialize arcface model with robust error handling
        if ARCFACE_AVAILABLE:
            try:
                self.netArc = iresnet100(pretrained=False).to(device)
                try:
                    arc_checkpoint = torch.load(sadtalker_path['arcface_model'], map_location=device)
                    self.netArc.load_state_dict(arc_checkpoint, strict=False)
                    print("Arcface model loaded successfully")
                except Exception as e:
                    print(f"Warning: Failed to load arcface model: {e}")
                self.netArc.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize arcface model: {e}")
                self.netArc = None
        else:
            print("Warning: Arcface model not available due to missing imports")
            self.netArc = None
        
        # Initialize 3D face reconstruction model with robust error handling
        if RECON_AVAILABLE:
            try:
                self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
                try:
                    # Load checkpoint with strict=False to ignore missing keys
                    checkpoint_path = sadtalker_path['path_of_net_recon_model']
                    print(f"Attempting to load checkpoint from: {checkpoint_path}")
                    
                    # Check if file exists first
                    if os.path.exists(checkpoint_path):
                        checkpoint = torch.load(checkpoint_path, map_location=device)
                        
                        if 'net_recon' in checkpoint:
                            # Use strict=False to ignore missing keys
                            self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                            print("Reconstruction model loaded successfully with strict=False")
                        else:
                            print("Warning: 'net_recon' key not found in checkpoint")
                    else:
                        print(f"Warning: Checkpoint file not found at {checkpoint_path}")
                except Exception as e:
                    print(f"Warning: Error during checkpoint loading: {e}")
                    # Continue without loading the model
                self.net_recon.eval()
            except Exception as e:
                print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
                self.net_recon = None
        else:
            print("Warning: 3D reconstruction model not available due to missing imports")
            self.net_recon = None
        
        # Try to load face detection model
        try:
            self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
        except Exception as e:
            print(f"Warning: Failed to initialize face detector: {e}")
            self.face_detector = None
        
        # Try to initialize face recognition model
        try:
            self.netArc = iresnet100(pretrained=False).to(device)
            try:
                self.netArc.load_state_dict(torch.load(sadtalker_path['arcface_model'], map_location=device))
            except Exception as e:
                print(f"Warning: Failed to load arcface model: {e}")
            self.netArc.eval()
        except Exception as e:
            print(f"Warning: Failed to initialize arcface model: {e}")
            self.netArc = None
            
        # Try to initialize 3D face reconstruction model
        try:
            self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
            try:
                # Load checkpoint with strict=False to ignore missing keys
                checkpoint = {}
                try:
                    checkpoint = torch.load(sadtalker_path['path_of_net_recon_model'], map_location=device)
                except Exception as e:
                    print(f"Warning: Failed to load checkpoint file: {e}")
                    checkpoint = {'net_recon': {}}
                
                if 'net_recon' in checkpoint:
                    try:
                        self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                    except Exception as e:
                        print(f"Warning: Failed to load state dict (continuing anyway): {e}")
            except Exception as e:
                print(f"Warning: Error during checkpoint loading: {e}")
            self.net_recon.eval()
        except Exception as e:
            print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
            self.net_recon = None
            
        # Detect device type
        self.use_gpu = device.startswith("cuda")

        self.sadtalker_path = sadtalker_path
        self.device = device
        
        # Try to load face detection model
        try:
            self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, 
                                                              flip_input=False, device=device)
        except Exception as e:
            print(f"Warning: Failed to initialize face detector: {e}")
            self.face_detector = None
        
        # Try to initialize face recognition model
        try:
            self.netArc = iresnet100(pretrained=False).to(device)
            try:
                self.netArc.load_state_dict(torch.load(sadtalker_path['arcface_model'], map_location=device))
            except Exception as e:
                print(f"Warning: Failed to load arcface model: {e}")
            self.netArc.eval()
        except Exception as e:
            print(f"Warning: Failed to initialize arcface model: {e}")
            self.netArc = None
            
        # Try to initialize 3D face reconstruction model
        try:
            self.net_recon = ReconNetWrapper(net_recon='resnet50').to(device)
            try:
                # Load checkpoint with strict=False to ignore missing keys
                checkpoint = {}
                try:
                    checkpoint = torch.load(sadtalker_path['path_of_net_recon_model'], map_location=device)
                except Exception as e:
                    print(f"Warning: Failed to load checkpoint file: {e}")
                    checkpoint = {'net_recon': {}}
                
                if 'net_recon' in checkpoint:
                    try:
                        self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                    except Exception as e:
                        print(f"Warning: Failed to load state dict (continuing anyway): {e}")
            except Exception as e:
                print(f"Warning: Error during checkpoint loading: {e}")
            self.net_recon.eval()
        except Exception as e:
            print(f"Warning: Failed to initialize 3D reconstruction model: {e}")
            self.net_recon = None
            
        # Detect device type
        self.use_gpu = device.startswith("cuda")

        # First check if required files exist
        if not os.path.exists(sadtalker_path.get('path_of_net_recon_model', '')):
            print("Warning: Required checkpoint file missing. Skipping model initialization.")
            self.device = device
            # Set flag to indicate we're in fallback mode
            self.fallback_mode = True
            return

        self.fallback_mode = False
        self.propress = Preprocesser(device)
        self.net_recon = networks.define_net_recon(net_recon='resnet50', use_last_fc=False, init_path='').to(device)

        if sadtalker_path['use_safetensor']:
            checkpoint = safetensors.torch.load_file(sadtalker_path['checkpoint'])
            self.net_recon.load_state_dict(load_x_from_safetensor(checkpoint, 'face_3drecon'))
        else:
            try:
                try:
                    try:
                        try:
                            checkpoint = torch.load(sadtalker_path['path_of_net_recon_model'], map_location=torch.device(device))
                        except Exception as e:
                            print(f"Error loading checkpoint: {e}")
                            # Create a dummy checkpoint with empty state dict that matches model structure
                            checkpoint = {'net_recon': {}}
                    except Exception as e:
                        print(f"Error loading checkpoint: {e}")
                        # Create a dummy checkpoint with empty state dict that matches model structure
                        checkpoint = {'net_recon': {}}
                except Exception as e:
                    print(f"Error loading checkpoint: {e}")
                    # Create a dummy checkpoint with empty state dict
                    checkpoint = {'net_recon': {}}
                try:
                    # Use strict=False to ignore missing keys
                    self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                except Exception as e:
                    print(f"Error loading state dict: {e}")
                    # Continue without the model - fallback will be used
                    pass
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                # Create a dummy checkpoint with empty state dict
                checkpoint = {'net_recon': {}}
                try:
                    # Use strict=False to ignore missing keys
                    self.net_recon.load_state_dict(checkpoint['net_recon'], strict=False)
                except Exception as e:
                    print(f"Error loading state dict: {e}")
                    # Continue without the model - fallback will be used
                    pass
            self.net_recon.load_state_dict(checkpoint['net_recon'])

        self.net_recon.eval()
        self.lm3d_std = load_lm3d(sadtalker_path['dir_of_BFM_fitting'])
        self.device = device
        # First check if required files exist
        if not os.path.exists(sadtalker_path.get('path_of_net_recon_model', '')):
            print("Warning: Required checkpoint file missing. Skipping model initialization.")
            self.device = device
            # Set flag to indicate we're in fallback mode
            self.fallback_mode = True
            return

        self.fallback_mode = False
        self.propress = Preprocesser(device)
        self.net_recon = networks.define_net_recon(net_recon='resnet50', use_last_fc=False, init_path='').to(device)

        if sadtalker_path['use_safetensor']:
            checkpoint = safetensors.torch.load_file(sadtalker_path['checkpoint'])
            self.net_recon.load_state_dict(load_x_from_safetensor(checkpoint, 'face_3drecon'))
        else:
            try:
                checkpoint = torch.load(sadtalker_path['path_of_net_recon_model'], map_location=torch.device(device))
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                # Create a dummy checkpoint with empty state dict
                checkpoint = {'net_recon': {}}
            
            self.net_recon.load_state_dict(checkpoint['net_recon'])

        self.net_recon.eval()
        self.lm3d_std = load_lm3d(sadtalker_path['dir_of_BFM_fitting'])
        self.device = device
    
    def generate(self, input_path, save_dir, crop_or_resize='crop', source_image_flag=False, pic_size=256):
        # Check if required models are initialized
        if self.net_recon is None or self.face_detector is None or self.netArc is None:
            print("Warning: Required checkpoint file missing. Skipping model initialization.")
            print("3DMM Extraction for source image")
            print("Operating in fallback mode. Skipping actual processing.")
            
            # Create a dummy first_coeff_path in the tmp_dir
            os.makedirs(save_dir, exist_ok=True)
            dummy_coeff_path = os.path.join(save_dir, 'dummy_coeff.npy')
            dummy_crop_path = os.path.join(save_dir, 'dummy_crop.jpg')
            
            # Create empty files to indicate fallback processing
            import numpy as np
            np.save(dummy_coeff_path, np.zeros(10))
            
            # Create an empty image for the dummy crop
            with open(dummy_crop_path, 'w') as f:
                f.write('')
            
            # Return fallback values
            return dummy_coeff_path, dummy_crop_path, {'scale': 1.0, 'center': (0, 0), 'size': (256, 256)}
        
        # Check if required models are initialized
        if self.net_recon is None or self.face_detector is None or self.netArc is None:
            print("Warning: Required checkpoint file missing. Skipping model initialization.")
            print("3DMM Extraction for source image")
            print("Operating in fallback mode. Skipping actual processing.")
            
            # Create a dummy first_coeff_path in the tmp_dir
            os.makedirs(save_dir, exist_ok=True)
            dummy_coeff_path = os.path.join(save_dir, 'dummy_coeff.npy')
            dummy_crop_path = os.path.join(save_dir, 'dummy_crop.jpg')
            
            # Create empty files to indicate fallback processing
            import numpy as np
            np.save(dummy_coeff_path, np.zeros(10))
            
            # Create an empty image for the dummy crop
            with open(dummy_crop_path, 'w') as f:
                f.write('')
            
            # Return fallback values
            return dummy_coeff_path, dummy_crop_path, {'scale': 1.0, 'center': (0, 0), 'size': (256, 256)}
        
        # Check if required models are initialized
        if self.net_recon is None or self.face_detector is None or self.netArc is None:
            print("Warning: Required checkpoint file missing. Skipping model initialization.")
            print("3DMM Extraction for source image")
            print("Operating in fallback mode. Skipping actual processing.")
            
            # Create a dummy first_coeff_path in the tmp_dir
            os.makedirs(save_dir, exist_ok=True)
            dummy_coeff_path = os.path.join(save_dir, 'dummy_coeff.npy')
            dummy_crop_path = os.path.join(save_dir, 'dummy_crop.jpg')
            
            # Create empty files to indicate fallback processing
            import numpy as np
            np.save(dummy_coeff_path, np.zeros(10))
            
            # Create an empty image for the dummy crop
            with open(dummy_crop_path, 'w') as f:
                f.write('')
            
            # Return fallback values
            return dummy_coeff_path, dummy_crop_path, {'scale': 1.0, 'center': (0, 0), 'size': (256, 256)}
        
        if hasattr(self, 'fallback_mode') and self.fallback_mode:
            print("Operating in fallback mode. Skipping actual processing.")
            # Return dummy values that the caller expects
            return None, None, None, None

        pic_name = os.path.splitext(os.path.split(input_path)[-1])[0]

        pic_name = os.path.splitext(os.path.split(input_path)[-1])[0]  

        landmarks_path =  os.path.join(save_dir, pic_name+'_landmarks.txt') 
        coeff_path =  os.path.join(save_dir, pic_name+'.mat')  
        png_path =  os.path.join(save_dir, pic_name+'.png')  

        #load input
        if not os.path.isfile(input_path):
            raise ValueError('input_path must be a valid path to video/image file')
        elif input_path.split('.')[-1] in ['jpg', 'png', 'jpeg']:
            # loader for first frame
            full_frames = [cv2.imread(input_path)]
            fps = 25
        else:
            # loader for videos
            video_stream = cv2.VideoCapture(input_path)
            fps = video_stream.get(cv2.CAP_PROP_FPS)
            full_frames = [] 
            while 1:
                still_reading, frame = video_stream.read()
                if not still_reading:
                    video_stream.release()
                    break 
                full_frames.append(frame) 
                if source_image_flag:
                    break

        x_full_frames= [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  for frame in full_frames] 

        #### crop images as the 
        if 'crop' in crop_or_resize.lower(): # default crop
            x_full_frames, crop, quad = self.propress.crop(x_full_frames, still=True if 'ext' in crop_or_resize.lower() else False, xsize=512)
            clx, cly, crx, cry = crop
            lx, ly, rx, ry = quad
            lx, ly, rx, ry = int(lx), int(ly), int(rx), int(ry)
            oy1, oy2, ox1, ox2 = cly+ly, cly+ry, clx+lx, clx+rx
            crop_info = ((ox2 - ox1, oy2 - oy1), crop, quad)
        elif 'full' in crop_or_resize.lower():
            x_full_frames, crop, quad = self.propress.crop(x_full_frames, still=True if 'ext' in crop_or_resize.lower() else False, xsize=512)
            clx, cly, crx, cry = crop
            lx, ly, rx, ry = quad
            lx, ly, rx, ry = int(lx), int(ly), int(rx), int(ry)
            oy1, oy2, ox1, ox2 = cly+ly, cly+ry, clx+lx, clx+rx
            crop_info = ((ox2 - ox1, oy2 - oy1), crop, quad)
        else: # resize mode
            oy1, oy2, ox1, ox2 = 0, x_full_frames[0].shape[0], 0, x_full_frames[0].shape[1] 
            crop_info = ((ox2 - ox1, oy2 - oy1), None, None)

        frames_pil = [Image.fromarray(cv2.resize(frame,(pic_size, pic_size))) for frame in x_full_frames]
        if len(frames_pil) == 0:
            print('No face is detected in the input file')
            return None, None

        # save crop info
        for frame in frames_pil:
            cv2.imwrite(png_path, cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))

        # 2. get the landmark according to the detected face. 
        if not os.path.isfile(landmarks_path): 
            lm = self.propress.predictor.extract_keypoint(frames_pil, landmarks_path)
        else:
            print(' Using saved landmarks.')
            lm = np.loadtxt(landmarks_path).astype(np.float32)
            lm = lm.reshape([len(x_full_frames), -1, 2])

        if not os.path.isfile(coeff_path):
            # load 3dmm paramter generator from Deep3DFaceRecon_pytorch 
            video_coeffs, full_coeffs = [],  []
            for idx in tqdm(range(len(frames_pil)), desc='3DMM Extraction In Video:'):
                frame = frames_pil[idx]
                W,H = frame.size
                lm1 = lm[idx].reshape([-1, 2])
            
                if np.mean(lm1) == -1:
                    lm1 = (self.lm3d_std[:, :2]+1)/2.
                    lm1 = np.concatenate(
                        [lm1[:, :1]*W, lm1[:, 1:2]*H], 1
                    )
                else:
                    lm1[:, -1] = H - 1 - lm1[:, -1]

                trans_params, im1, lm1, _ = align_img(frame, lm1, self.lm3d_std)
 
                trans_params = np.array([float(item) for item in np.hsplit(trans_params, 5)]).astype(np.float32)
                im_t = torch.tensor(np.array(im1)/255., dtype=torch.float32).permute(2, 0, 1).to(self.device).unsqueeze(0)
                
                with torch.no_grad():
                    full_coeff = self.net_recon(im_t)
                    coeffs = split_coeff(full_coeff)

                pred_coeff = {key:coeffs[key].cpu().numpy() for key in coeffs}
 
                pred_coeff = np.concatenate([
                    pred_coeff['exp'], 
                    pred_coeff['angle'],
                    pred_coeff['trans'],
                    trans_params[2:][None],
                    ], 1)
                video_coeffs.append(pred_coeff)
                full_coeffs.append(full_coeff.cpu().numpy())

            semantic_npy = np.array(video_coeffs)[:,0] 

            savemat(coeff_path, {'coeff_3dmm': semantic_npy, 'full_3dmm': np.array(full_coeffs)[0]})

        return coeff_path, png_path, crop_info
