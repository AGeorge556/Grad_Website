@echo off
setlocal enabledelayedexpansion
echo 🔧 Running SadTalker with LOCAL MODELS ONLY (No Auto-Download)
echo Arguments: %*
echo.

REM This batch file now uses the no-download version to prevent
REM download interruptions during inference

REM Check if the no-download batch file exists
if exist "D:\University files\Graduation Project\SadTalker\run_sadtalker_no_download.bat" (
    echo ✅ Using no-download version for reliable operation
    call "D:\University files\Graduation Project\SadTalker\run_sadtalker_no_download.bat" %*
    exit /b %ERRORLEVEL%
)

REM Fallback to original logic with auto-download disabled
echo ⚠️ No-download batch not found, using fallback logic

REM Initialize variables
set CPU_FLAG=
set VERBOSE_FLAG=--verbose
set TIMEOUT_MINUTES=15

REM Parse arguments and REJECT auto-fix flag
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--cpu" set CPU_FLAG=--cpu
if /i "%~1"=="--auto-fix" (
    echo ❌ ERROR: --auto-fix is DISABLED
    echo    Auto-download during inference is not allowed
    echo    Models must be downloaded separately
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

REM Validate models directly (skip setup if models exist)
echo 🔍 Validating SadTalker models...
python "%~dp0validate_models_quick.py"

if errorlevel 1 (
    echo ⚠️ Models missing - running automatic setup...
    echo 🔄 Running one-time setup: python setup_sadtalker_once.py
    python setup_sadtalker_once.py
    if errorlevel 1 (
        echo ❌ ERROR: Automatic setup failed!
        echo.
        echo 💡 MANUAL SETUP REQUIRED:
        echo    Please run: python setup_sadtalker_once.py
        echo    from the SadTalker directory manually.
        echo.
        echo 🚫 Auto-download during inference is DISABLED to prevent
        echo    interruptions and ensure reliable operation.
        echo.
        exit /b 1
    )
    echo ✅ Automatic setup completed successfully!
)
echo ✅ Models validated - proceeding with inference
echo.

REM Execute SadTalker with LOCAL MODELS ONLY
echo 🚀 Executing SadTalker with local models (no downloads)...
echo Command: python inference_enhanced_with_video.py %FINAL_ARGS%
echo.

REM Skip environment activation for non-interactive mode
echo ⚠️ Skipping virtual environment activation for non-interactive execution
echo   Using system Python for reliable background operation

REM Run SadTalker inference with non-interactive flags
python inference_enhanced_with_video.py %FINAL_ARGS% --no-interrupt --silent --force-local-models
set SADTALKER_EXITCODE=%ERRORLEVEL%

echo.
echo 📊 SadTalker execution completed with exit code: %SADTALKER_EXITCODE%

if %SADTALKER_EXITCODE% EQU 0 (
    echo ✅ SadTalker completed successfully!
) else if %SADTALKER_EXITCODE% EQU 2 (
    echo ⚠️ SadTalker completed with fallback video (Exit Code 2)
    echo   This usually means the primary generation failed but a fallback was created
) else (
    echo ❌ SadTalker failed with exit code: %SADTALKER_EXITCODE%
    echo.
    echo 💡 COMMON ISSUES:
    echo    - Model compatibility: Ensure latest models are downloaded
    echo    - Input file issues: Check source image and audio paths  
    echo    - Memory issues: Try --cpu flag or smaller input files
    echo    - Python dependencies: Ensure all packages are installed
    echo.
    echo 🔧 TROUBLESHOOTING:
    echo    1. Check that all model files exist in checkpoints/ directory
    echo    2. Verify the source image and audio file paths are correct
    echo    3. Try running with --cpu flag for better compatibility
    echo    4. Check the detailed error messages above
)

echo.
echo 🏁 Script execution finished.
exit /b %SADTALKER_EXITCODE% 