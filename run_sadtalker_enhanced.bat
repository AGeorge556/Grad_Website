@echo off
echo 🔧 Running ENHANCED SadTalker with Robustness Fixes
echo.

REM Change to SadTalker directory
cd /d "D:\University files\Graduation Project\SadTalker"

REM Check if environment exists
if not exist "sadtalker_env\Scripts\activate.bat" (
    echo ❌ SadTalker environment not found
    echo Using fallback video generation...
    exit /b 1
)

REM Activate the SadTalker virtual environment
echo Activating SadTalker environment...
call sadtalker_env\Scripts\activate.bat

REM Check if activation worked by testing torch
python -c "import torch; print('✅ Environment activated successfully')" 2>nul
if errorlevel 1 (
    echo ❌ Environment activation failed, using fallback...
    exit /b 1
)

REM Run the enhanced SadTalker inference with robustness fixes
echo Running SadTalker with robustness enhancements...
python inference.py %*

REM Capture exit code
set EXITCODE=%ERRORLEVEL%

REM Deactivate environment
call deactivate 2>nul

echo ✅ Enhanced SadTalker execution complete (Exit Code: %EXITCODE%)
exit /b %EXITCODE% 