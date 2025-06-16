import torch
import torch.nn.functional as F

def rgb_to_grayscale(img, num_output_channels=1):
    """Convert RGB image to grayscale.
    
    Args:
        img (Tensor): RGB Image to be converted to grayscale.
        num_output_channels (int): number of channels of the output image (1 or 3). Default: 1
        
    Returns:
        Tensor: Grayscale version of the image
    """
    if img.shape[0] != 3:
        raise TypeError('Input image tensor should have 3 channels')
    
    # Use the ITU-R BT.601 coefficients for RGB to grayscale conversion
    r, g, b = img.unbind(0)
    l_img = (0.299 * r + 0.587 * g + 0.114 * b).unsqueeze(0)
    
    if num_output_channels == 1:
        return l_img
    
    return l_img.repeat(3, 1, 1) 