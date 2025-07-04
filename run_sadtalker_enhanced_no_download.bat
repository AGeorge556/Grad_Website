@echo off
setlocal enabledelayedexpansion
echo 🔧 Running SadTalker with LOCAL MODELS ONLY (No Auto-Download)
echo Arguments: %*
echo.

REM Initialize variables
set CPU_FLAG=
set VERBOSE_FLAG=--verbose
set TIMEOUT_MINUTES=15

REM Parse arguments (NO AUTO-FIX SUPPORT)
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--cpu" set CPU_FLAG=--cpu
if /i "%~1"=="--auto-fix" (
    echo ❌ ERROR: --auto-fix flag is DISABLED
    echo    SadTalker no longer downloads models during inference
    echo    Please run setup first: python setup_sadtalker_once.py
    exit /b 1
)
shift
goto parse_args
:args_done

set "FINAL_ARGS=%*"

echo 🔍 Configuration:
echo    - CPU Mode: %CPU_FLAG%
echo    - Verbose: %VERBOSE_FLAG%
echo    - Timeout: %TIMEOUT_MINUTES% minutes
echo    - Auto-fix: DISABLED (local models only)
echo    - Final Args: %FINAL_ARGS%
echo.

REM Change to SadTalker directory
echo 📂 Changing to SadTalker directory...
cd /d "D:\University files\Graduation Project\SadTalker"
if errorlevel 1 (
    echo ❌ Failed to change to SadTalker directory
    exit /b 1
)
echo ✅ Current directory: %CD%
echo.

REM Check for setup completion marker
if not exist ".sadtalker_setup_complete" (
    echo ❌ ERROR: SadTalker setup not completed!
    echo.
    echo 💡 REQUIRED SETUP:
    echo    Please run the one-time setup first:
    echo    cd SadTalker
    echo    python setup_sadtalker_once.py
    echo.
    echo    This will download all models ONCE and prevent
    echo    download interruptions during inference.
    echo.
    exit /b 1
)

echo ✅ Setup completion verified
echo.

REM Validate ALL critical checkpoint files (NO DOWNLOADS)
echo 🔍 STRICT MODEL VALIDATION (Local Files Only)
echo ==================================================
set VALIDATION_FAILED=0

echo Checking critical model files...

REM Critical OpenTalker models (fix dimension mismatch)
call :check_file "checkpoints\mapping_00109-model.pth.tar" "Mapping Model 109 (OpenTalker)"
call :check_file "checkpoints\mapping_00229-model.pth.tar" "Mapping Model 229 (OpenTalker)"
call :check_file "checkpoints\SadTalker_V0.0.2_256.safetensors" "SadTalker 256px (SafeTensors)"

REM Legacy critical models
call :check_file "checkpoints\auido2pose_00140-model.pth" "Audio2Pose Model"
call :check_file "checkpoints\auido2exp_00300-model.pth" "Audio2Expression Model"
call :check_file "checkpoints\facevid2vid_00189-model.pth.tar" "FaceVid2Vid Model"
call :check_file "checkpoints\shape_predictor_68_face_landmarks.dat" "Face Landmarks"
call :check_file "checkpoints\wav2lip.pth" "Wav2Lip Model"
call :check_file "checkpoints\epoch_20.pth" "Epoch 20 Model"

REM ArcFace model
call :check_file "checkpoints\arcface_model.pth" "ArcFace Model"

if !VALIDATION_FAILED! EQU 1 (
    echo.
    echo ❌ CRITICAL ERROR: Missing model files detected!
    echo    SadTalker CANNOT run without these models.
    echo.
    echo 💡 SOLUTION:
    echo    Run the one-time setup to download all models:
    echo    cd SadTalker
    echo    python setup_sadtalker_once.py
    echo.
    echo 🚫 Auto-download during inference is DISABLED to prevent
    echo    interruptions and ensure reliable operation.
    echo.
    exit /b 1
)

echo ✅ All critical model files validated successfully!
echo.

REM Check if environment exists
echo 🔍 Validating SadTalker environment...
if not exist "sadtalker_env\Scripts\activate.bat" (
    echo ❌ SadTalker environment not found at: sadtalker_env\Scripts\activate.bat
    echo.
    echo 💡 ENVIRONMENT SETUP:
    echo    The SadTalker virtual environment appears to be missing.
    echo.
    echo    To fix this:
    echo    1. Run: python -m venv sadtalker_env
    echo    2. Run: sadtalker_env\Scripts\activate
    echo    3. Run: pip install -r requirements.txt
    echo.
    exit /b 1
)
echo ✅ Environment found: sadtalker_env\Scripts\activate.bat

REM Activate the SadTalker virtual environment
echo 🔄 Activating SadTalker environment...
call sadtalker_env\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate environment
    exit /b 1
)
echo ✅ Environment activated successfully

REM Create results directory if it doesn't exist
for /f "tokens=* delims=" %%a in ('echo %FINAL_ARGS%') do (
    echo %%a | findstr --result_dir >nul
    if not errorlevel 1 (
        for /f "tokens=2 delims= " %%b in ("%%a") do (
            set RESULT_DIR=%%b
            if not exist "!RESULT_DIR!" (
                echo 📁 Creating results directory: !RESULT_DIR!
                mkdir "!RESULT_DIR!" 2>nul
            )
        )
    )
)

REM Execute SadTalker with LOCAL MODELS ONLY
echo 🚀 Executing SadTalker with local models (no downloads)...
echo Command: python inference_enhanced_with_video.py %FINAL_ARGS%
echo.

REM Set timeout for the operation
timeout /t 2 >nul

REM Run SadTalker inference
python inference_enhanced_with_video.py %FINAL_ARGS%
set SADTALKER_EXITCODE=%ERRORLEVEL%

echo.
echo 📊 SadTalker execution completed with exit code: %SADTALKER_EXITCODE%

if %SADTALKER_EXITCODE% EQU 0 (
    echo ✅ SadTalker completed successfully!
) else (
    echo ❌ SadTalker failed with exit code: %SADTALKER_EXITCODE%
    echo.
    echo 💡 COMMON ISSUES:
    echo    - Model compatibility: Ensure latest models are downloaded
    echo    - Input file issues: Check source image and audio paths
    echo    - Memory issues: Try --cpu flag or smaller input files
    echo    - Python dependencies: Ensure all packages are installed
    echo.
    echo 🔧 DEBUGGING:
    echo    Check the output above for specific error messages
    echo    Re-run with additional verbose flags if needed
)

echo.
echo 🏁 Script execution finished.
exit /b %SADTALKER_EXITCODE%

REM Function to check if a file exists and has reasonable size
:check_file
set FILE_PATH=%~1
set FILE_DESC=%~2

if not exist "%FILE_PATH%" (
    echo ❌ Missing: %FILE_DESC% (%FILE_PATH%)
    set VALIDATION_FAILED=1
    goto :eof
)

REM Check file size (should be > 1MB for most model files)
for %%I in ("%FILE_PATH%") do set FILE_SIZE=%%~zI
if %FILE_SIZE% LSS 1048576 (
    echo ❌ Too small: %FILE_DESC% (%FILE_PATH%) - %FILE_SIZE% bytes
    set VALIDATION_FAILED=1
) else (
    set /a FILE_SIZE_MB=%FILE_SIZE%/1048576
    echo ✅ %FILE_DESC% (!FILE_SIZE_MB! MB)
)
goto :eof 