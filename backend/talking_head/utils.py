# Utility functions for the talking head module
import os

def get_project_root() -> str:
    """Returns the absolute path to the project root directory."""
    # The root is two levels up from this file.
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_dir_exists(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False 