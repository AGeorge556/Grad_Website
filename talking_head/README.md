# Talking Head Generation Module

This module integrates SadTalker to generate talking head videos from text and a source image.

## Architecture

The talking head generation module consists of:

1. **SadTalker Integration**: Uses the SadTalker deep learning model to generate lifelike talking head videos
2. **Fallback Mechanism**: Provides a graceful fallback when SadTalker encounters issues
3. **Python 3.10 Environment**: Uses a dedicated Python 3.10 environment for better compatibility with SadTalker

## Compatibility Issues and Solutions

### Python Version Compatibility

SadTalker has compatibility issues with Python 3.12 due to dependencies. We've implemented:

1. A dedicated Python 3.10 virtual environment (`sadtalker_venv`) for running SadTalker
2. A batch script (`run_sadtalker_py310.bat`) that activates this environment

### Checkpoint Loading Issues

SadTalker may encounter issues loading checkpoint files due to model architecture mismatches. We've implemented:

1. Robust error handling in `patch_sadtalker.py` to gracefully handle missing or incompatible checkpoints
2. A fallback mechanism that returns a default video when model loading fails

## How to Use

```python
from talking_head.generate_video import generate_talking_video

# Generate a talking head video from text
result = generate_talking_video(
    text_content="Hello, I am a talking head video generated with SadTalker.",
    source_image_path=None  # Uses default face if not provided
)

# Access the video URL
video_url = result["video_url"]
```

## Maintenance and Troubleshooting

- **Checkpoint errors**: If you encounter checkpoint loading errors, check that the checkpoints in `SadTalker/checkpoints/` match the model architecture.
- **Python version**: Ensure Python 3.10 is available on the system
- **Environment issues**: If the Python 3.10 environment isn't working, rebuild it using:
  ```
  cd SadTalker
  "C:\Path\to\Python310\python.exe" -m venv sadtalker_venv
  .\sadtalker_venv\Scripts\activate
  pip install -r requirements.txt
  ```

## Error Handling

The module is designed to always return a video, even when errors occur:

1. First attempts to generate a video with SadTalker
2. If SadTalker fails, uses a fallback video
3. Always returns a 200 status code with either the generated or fallback video 