@echo off
setlocal enabledelayedexpansion

echo Debugging checkpoint validation...
cd /d "D:\University files\Graduation Project\SadTalker"
echo Current directory: %CD%

set VALIDATION_FAILED=0

echo.
echo Testing individual file checks:
echo ================================

call :check_file "checkpoints\arcface_model.pth" "Arcface Model"
echo After arcface check, VALIDATION_FAILED = !VALIDATION_FAILED!

call :check_file "checkpoints\facerecon_model.pth" "Face Reconstruction Model"  
echo After facerecon check, VALIDATION_FAILED = !VALIDATION_FAILED!

call :check_file "checkpoints\auido2pose_00140-model.pth" "Audio2Pose Model"
echo After audio2pose check, VALIDATION_FAILED = !VALIDATION_FAILED!

call :check_file "checkpoints\auido2exp_00300-model.pth" "Audio2Expression Model"
echo After audio2exp check, VALIDATION_FAILED = !VALIDATION_FAILED!

call :check_file "checkpoints\facevid2vid_00189-model.pth.tar" "FaceVid2Vid Model"
echo After facevid2vid check, VALIDATION_FAILED = !VALIDATION_FAILED!

echo.
echo Final VALIDATION_FAILED value: !VALIDATION_FAILED!

if !VALIDATION_FAILED! EQU 1 (
    echo RESULT: Validation FAILED
) else (
    echo RESULT: Validation PASSED
)

pause
exit /b 0

REM Function to check if file exists and has non-zero size
:check_file
set FILE_PATH=%~1
set FILE_NAME=%~2

echo.
echo Checking: %FILE_NAME%
echo File path: %FILE_PATH%

if not exist "%FILE_PATH%" (
    echo ❌ MISSING: %FILE_NAME% - %FILE_PATH%
    set VALIDATION_FAILED=1
    goto :eof
)

REM Check if file size is 0 bytes - using delayed expansion
for %%A in ("%FILE_PATH%") do (
    set FILE_SIZE=%%~zA
)

echo File size detected: !FILE_SIZE!

if "!FILE_SIZE!"=="0" (
    echo ❌ EMPTY: %FILE_NAME% - %FILE_PATH% (0 bytes)
    set VALIDATION_FAILED=1
    goto :eof
)

REM If we get here, file exists and has non-zero size
echo ✅ VALID: %FILE_NAME% - %FILE_PATH% (!FILE_SIZE! bytes)
goto :eof 