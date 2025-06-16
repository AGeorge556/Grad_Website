'''Compatibility layer for torchvision.transforms.functional_tensor This recreates the rgb_to_grayscale function used by SadTalker'''


import torch
import torch.nn.functional as F

