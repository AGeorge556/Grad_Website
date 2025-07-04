#!/usr/bin/env python3
"""
Website Backend Dependency Test Script

This script checks for all required dependencies for the Website backend
including SadTalker integration dependencies.
"""

import sys
import subprocess
from typing import List, Tuple

def test_module_import(module_name: str, import_as: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported successfully"""
    try:
        if import_as:
            if import_as == 'cv2':
                import cv2
                version = cv2.__version__
            elif import_as == 'PIL':
                from PIL import Image
                version = Image.__version__
            else:
                module = __import__(import_as)
                version = getattr(module, '__version__', 'Unknown')
        else:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'Unknown')
        
        return True, version
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Import error: {str(e)}"

def main():
    """Main dependency test function for Website backend"""
    print("=" * 60)
    print("🌐 WEBSITE BACKEND DEPENDENCY TEST")
    print("=" * 60)
    print()
    
    # Backend dependencies
    backend_dependencies = [
        ("FastAPI", "fastapi", None),
        ("Uvicorn", "uvicorn", None),
        ("Pydantic", "pydantic", None),
        ("Supabase", "supabase", None),
        ("OpenAI", "openai", None),
        ("gTTS", "gtts", None),
        ("MoviePy", "moviepy", None),
    ]
    
    # SadTalker integration dependencies
    sadtalker_dependencies = [
        ("NumPy", "numpy", None),
        ("OpenCV", "opencv-python", "cv2"),
        ("Pillow", "PIL", "PIL"),
        ("Librosa", "librosa", None),
        ("PyTorch", "torch", None),
        ("TorchVision", "torchvision", None),
        ("Face Alignment", "face_alignment", None),
        ("ImageIO", "imageio", None),
        ("SciPy", "scipy", None),
        ("PyDub", "pydub", None),
    ]
    
    print("🔧 BACKEND DEPENDENCIES:")
    backend_missing = []
    backend_passed = 0
    
    for display_name, import_name, import_as in backend_dependencies:
        print(f"   Testing {display_name}...", end=" ")
        
        success, version_or_error = test_module_import(import_name, import_as)
        
        if success:
            print(f"✅ {version_or_error}")
            backend_passed += 1
        else:
            print(f"❌ MISSING")
            backend_missing.append((display_name, import_name))
    
    print()
    print("🎭 SADTALKER INTEGRATION:")
    sadtalker_missing = []
    sadtalker_passed = 0
    
    for display_name, import_name, import_as in sadtalker_dependencies:
        print(f"   Testing {display_name}...", end=" ")
        
        success, version_or_error = test_module_import(import_name, import_as)
        
        if success:
            print(f"✅ {version_or_error}")
            sadtalker_passed += 1
        else:
            print(f"❌ MISSING")
            sadtalker_missing.append((display_name, import_name))
    
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    print(f"Backend Dependencies: {backend_passed}/{len(backend_dependencies)} ✅")
    print(f"SadTalker Integration: {sadtalker_passed}/{len(sadtalker_dependencies)} ✅")
    print()
    
    if backend_missing or sadtalker_missing:
        print("❌ MISSING DEPENDENCIES:")
        
        if backend_missing:
            print("   Backend:")
            for display_name, import_name in backend_missing:
                print(f"   - {display_name} ({import_name})")
        
        if sadtalker_missing:
            print("   SadTalker Integration:")
            for display_name, import_name in sadtalker_missing:
                print(f"   - {display_name} ({import_name})")
        
        print()
        print("📥 INSTALLATION:")
        print("   pip install -r requirements.txt")
        print()
        
        return False
    
    print("🎉 ALL DEPENDENCIES AVAILABLE!")
    print("✅ Website backend should work correctly")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 