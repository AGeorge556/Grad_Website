@echo on
cd %1
call sadtalker_venv\Scripts\activate.bat
python -c "import sys; print('Python path:', sys.path); import yacs; print('YACS module found at:', yacs.__file__)"

REM Apply the patches to handle missing checkpoint and import issues
cd %~dp0
python patches\patch_sadtalker.py %1
python patches\fix_torchvision_import.py %1

REM Return to SadTalker directory
cd %1
python inference.py --driven_audio %2 --source_image %3 --result_dir %4 --enhancer gfpgan --preprocess full --still
exit 