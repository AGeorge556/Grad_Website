@echo off
echo Creating directories...

set SADTALKER_DIR=D:\University files\Graduation Project\SadTalker
set WEBSITE_DIR=D:\University files\Graduation Project\Website

if not exist "%SADTALKER_DIR%" (
    echo Error: SadTalker directory not found at %SADTALKER_DIR%
    echo Please update the SADTALKER_DIR variable in this script
    pause
    exit /b 1
)

cd /d "%SADTALKER_DIR%"
mkdir checkpoints 2>nul
mkdir gfpgan\weights 2>nul

echo Downloading SadTalker model files (both legacy and new versions)...

:: Legacy models (essential files)
echo Downloading legacy model files...

if not exist "checkpoints\auido2exp_00300-model.pth" (
    echo Downloading auido2exp_00300-model.pth...
    curl -L -o checkpoints\auido2exp_00300-model.pth https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/auido2exp_00300-model.pth
) else (
    echo auido2exp_00300-model.pth already exists, skipping...
)

if not exist "checkpoints\auido2pose_00140-model.pth" (
    echo Downloading auido2pose_00140-model.pth...
    curl -L -o checkpoints\auido2pose_00140-model.pth https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/auido2pose_00140-model.pth
) else (
    echo auido2pose_00140-model.pth already exists, skipping...
)

if not exist "checkpoints\epoch_20.pth" (
    echo Downloading epoch_20.pth...
    curl -L -o checkpoints\epoch_20.pth https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth
) else (
    echo epoch_20.pth already exists, skipping...
)

if not exist "checkpoints\facevid2vid_00189-model.pth.tar" (
    echo Downloading facevid2vid_00189-model.pth.tar...
    curl -L -o checkpoints\facevid2vid_00189-model.pth.tar https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/facevid2vid_00189-model.pth.tar
) else (
    echo facevid2vid_00189-model.pth.tar already exists, skipping...
)

if not exist "checkpoints\shape_predictor_68_face_landmarks.dat" (
    echo Downloading shape_predictor_68_face_landmarks.dat...
    curl -L -o checkpoints\shape_predictor_68_face_landmarks.dat https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/shape_predictor_68_face_landmarks.dat
) else (
    echo shape_predictor_68_face_landmarks.dat already exists, skipping...
)

if not exist "checkpoints\wav2lip.pth" (
    echo Downloading wav2lip.pth...
    curl -L -o checkpoints\wav2lip.pth https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/wav2lip.pth
) else (
    echo wav2lip.pth already exists, skipping...
)

if not exist "checkpoints\hub.zip" (
    echo Downloading hub.zip...
    curl -L -o checkpoints\hub.zip https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/hub.zip
    echo Extracting hub.zip...
    powershell -command "Expand-Archive -Path checkpoints\hub.zip -DestinationPath checkpoints -Force"
) else (
    echo hub.zip already exists, checking extraction...
    if not exist "checkpoints\hub" (
        echo Extracting hub.zip...
        powershell -command "Expand-Archive -Path checkpoints\hub.zip -DestinationPath checkpoints -Force"
    )
)

:: Download BFM files which are needed for face reconstruction
if not exist "checkpoints\BFM_Fitting.zip" (
    echo Downloading BFM_Fitting.zip...
    curl -L -o checkpoints\BFM_Fitting.zip https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/BFM_Fitting.zip
    echo Extracting BFM_Fitting.zip...
    powershell -command "Expand-Archive -Path checkpoints\BFM_Fitting.zip -DestinationPath checkpoints -Force"
) else (
    echo BFM_Fitting.zip already exists, checking extraction...
    if not exist "checkpoints\BFM" (
        echo Extracting BFM_Fitting.zip...
        powershell -command "Expand-Archive -Path checkpoints\BFM_Fitting.zip -DestinationPath checkpoints -Force"
    )
)

:: New models (OpenTalker version)
echo Downloading new model files...
if not exist "checkpoints\mapping_00109-model.pth.tar" (
    echo Downloading mapping_00109-model.pth.tar...
    curl -L -o checkpoints\mapping_00109-model.pth.tar https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar
) else (
    echo mapping_00109-model.pth.tar already exists, skipping...
)

if not exist "checkpoints\mapping_00229-model.pth.tar" (
    echo Downloading mapping_00229-model.pth.tar...
    curl -L -o checkpoints\mapping_00229-model.pth.tar https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar
) else (
    echo mapping_00229-model.pth.tar already exists, skipping...
)

if not exist "checkpoints\SadTalker_V0.0.2_256.safetensors" (
    echo Downloading SadTalker_V0.0.2_256.safetensors...
    curl -L -o checkpoints\SadTalker_V0.0.2_256.safetensors https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors
) else (
    echo SadTalker_V0.0.2_256.safetensors already exists, skipping...
)

if not exist "checkpoints\SadTalker_V0.0.2_512.safetensors" (
    echo Downloading SadTalker_V0.0.2_512.safetensors...
    curl -L -o checkpoints\SadTalker_V0.0.2_512.safetensors https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors
) else (
    echo SadTalker_V0.0.2_512.safetensors already exists, skipping...
)

:: GFPGAN enhancer models
echo Downloading GFPGAN enhancer models...
if not exist "gfpgan\weights\alignment_WFLW_4HG.pth" (
    echo Downloading alignment_WFLW_4HG.pth...
    curl -L -o gfpgan\weights\alignment_WFLW_4HG.pth https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth
) else (
    echo alignment_WFLW_4HG.pth already exists, skipping...
)

if not exist "gfpgan\weights\detection_Resnet50_Final.pth" (
    echo Downloading detection_Resnet50_Final.pth...
    curl -L -o gfpgan\weights\detection_Resnet50_Final.pth https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth
) else (
    echo detection_Resnet50_Final.pth already exists, skipping...
)

if not exist "gfpgan\weights\GFPGANv1.4.pth" (
    echo Downloading GFPGANv1.4.pth...
    curl -L -o gfpgan\weights\GFPGANv1.4.pth https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
) else (
    echo GFPGANv1.4.pth already exists, skipping...
)

if not exist "gfpgan\weights\parsing_parsenet.pth" (
    echo Downloading parsing_parsenet.pth...
    curl -L -o gfpgan\weights\parsing_parsenet.pth https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth
) else (
    echo parsing_parsenet.pth already exists, skipping...
)

echo.
echo All model files downloaded successfully to: %SADTALKER_DIR%
echo.
echo Now applying patch to fix the "too many values to unpack" error...
cd /d "%WEBSITE_DIR%"
cd talking_head
python patches\patch_sadtalker.py "%SADTALKER_DIR%"

echo.
echo If you're still experiencing errors, make sure these files are in the correct directory structure:
echo - SadTalker models should be in the '%SADTALKER_DIR%\checkpoints' directory
echo - GFPGAN models should be in the '%SADTALKER_DIR%\gfpgan\weights' directory
pause
