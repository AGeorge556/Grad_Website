# SadTalker Backend Setup and Testing

This guide will help you set up and test the SadTalker backend for video processing in your project.

## Prerequisites

1. Python 3.8+ installed
2. SadTalker repository cloned in a directory adjacent to your project
3. Video file for testing
4. Face image for animation

## Setup Instructions

### 1. Clone SadTalker Repository

If you haven't already, clone the SadTalker repository adjacent to your project:

```bash
cd ..
cd ..
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
```

### 2. Set Up SadTalker Environment

Follow the official SadTalker setup instructions to install dependencies and download models:

```bash
python -m pip install -r requirements.txt
python scripts/download_models.py
```

### 3. Install Backend Dependencies

Install the required dependencies for the backend:

```bash
cd ../Website/backend
python -m pip install -r sadtalker_requirements.txt
```

### Default Face Image
1. Place a default face image named `default_face.png` in the `model/files` directory
2. The image should be:
   - A clear, front-facing portrait
   - High resolution (at least 512x512 pixels)
   - PNG format
   - Well-lit and professional looking
   - Neutral expression

## Running the Backend

To start the SadTalker backend server:

```bash
python backend_with_sadtalker.py
```

The server will start on http://localhost:5000 by default.

## Testing with the Test Client

You can use the provided test client to test the backend:

```bash
python test_sadtalker_client.py --video path/to/your/video.mp4 --face path/to/your/face.png
```

Options:
- `--video`: Path to the video file to process (required)
- `--face`: Path to the face image file to use for animation (required)
- `--server`: URL of the backend server (default: http://localhost:5000)

## Troubleshooting

### Common Issues

1. **SadTalker not found**: Ensure the SadTalker repository is cloned in the correct location (../SadTalker relative to your project)

2. **Missing dependencies**: Make sure all dependencies are installed correctly

3. **CUDA issues**: If you encounter CUDA-related errors, ensure you have the correct version of PyTorch installed for your CUDA version

4. **File permissions**: Ensure the uploads directory is writable

### Debugging

If you encounter issues, check the Flask server logs for detailed error messages. You can also modify the test client to print more detailed information by adding debug statements.

## Comparing Results

To compare results between different backends or configurations:

1. Run the test client against each backend
2. Compare the processing time reported by the client
3. Compare the quality of the generated videos
4. Compare the accuracy of the transcription and summarization

## Additional Resources

- [SadTalker GitHub Repository](https://github.com/OpenTalker/SadTalker)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Whisper Documentation](https://github.com/openai/whisper)