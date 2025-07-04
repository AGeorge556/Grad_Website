#!/usr/bin/env python3
"""
Quick SadTalker Model Validator
Fast validation script for batch files - Website copy
"""

import os
import sys
from pathlib import Path

def main():
    # Change to SadTalker directory for validation
    sadtalker_dir = Path("D:/University files/Graduation Project/SadTalker")
    if sadtalker_dir.exists():
        os.chdir(sadtalker_dir)
    
    # Critical models that must exist
    critical_models = [
        'checkpoints/mapping_00109-model.pth.tar',
        'checkpoints/auido2exp_00300-model.pth',
        'checkpoints/auido2pose_00140-model.pth',
        'checkpoints/facevid2vid_00189-model.pth.tar',
        'checkpoints/shape_predictor_68_face_landmarks.dat',
        'checkpoints/wav2lip.pth',
        'checkpoints/epoch_20.pth'
    ]
    
    missing = []
    for model in critical_models:
        model_path = Path(model)
        if not model_path.exists():
            missing.append(model)
        else:
            try:
                size_mb = model_path.stat().st_size / (1024*1024)
                print(f'✅ {model} ({size_mb:.1f} MB)')
            except Exception as e:
                print(f'⚠️ {model} (could not get size: {e})')
    
    if missing:
        print('❌ MISSING MODELS:')
        for m in missing:
            print(f'   - {m}')
        print('\n⚠️ Models missing - running automatic setup...')
        return 1
    else:
        print('✅ All critical models validated - ready for inference')
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1) 