import io
import os
from pathlib import Path
import fleep
from moviepy.editor import VideoFileClip
import whisper
from transformers import pipeline
import torch
from gtts import gTTS
import sys
import re
import random

# Import model functions
import sys
sys.path.append('..')  # Add parent directory to path
from model.src.app.speech import extract_audio, transcribe
from model.src.app.summarizer import summarize_text

class ModelProcessor:
    def __init__(self):
        # Initialize models
        self.whisper_model = whisper.load_model("base")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Create necessary directories
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    async def process_video(self, video_bytes: bytes) -> tuple[str, str, bytes, list, list, str]:
        """
        Process a video file and return transcript, summary, and audio summary.
        
        Args:
            video_bytes: The video file as bytes
            
        Returns:
            tuple: (transcript, summary, audio_bytes, flashcards, quizzes, notes)
        """
        # Save video to temp file
        temp_video_path = self.temp_dir / "temp_video.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_bytes)
            
        try:
            # Extract audio
            video = VideoFileClip(str(temp_video_path))
            audio_path = self.temp_dir / "temp_audio.wav"
            video.audio.write_audiofile(str(audio_path))
            video.close()
            
            # Transcribe
            result = self.whisper_model.transcribe(str(audio_path))
            transcript = result["text"]
            
            # Summarize using local model
            summary = summarize_text(transcript)
            
            # Generate flashcards and quizzes from summary
            flashcards = generate_flashcards_from_summary(summary)
            quizzes = generate_quiz_from_summary(summary)
            
            # Convert summary to speech
            audio_io = io.BytesIO()
            tts = gTTS(summary)
            tts.write_to_fp(audio_io)
            audio_io.seek(0)
            
            notes = "These are your notes."
            
            return transcript, summary, audio_io.getvalue(), flashcards, quizzes, notes
            
        finally:
            # Cleanup
            if temp_video_path.exists():
                temp_video_path.unlink()
            if audio_path.exists():
                audio_path.unlink()

# Local flashcard and quiz generation from summary

def generate_flashcards_from_summary(summary: str, max_flashcards: int = 5):
    sentences = re.split(r'(?<=[.!?]) +', summary)
    flashcards = []
    for i, sentence in enumerate(sentences[:max_flashcards]):
        if not sentence.strip():
            continue
        question = f"What is the key point of: \"{sentence.strip()}\"?"
        answer = sentence.strip()
        flashcards.append({
            "id": i + 1,
            "question": question,
            "answer": answer
        })
    return flashcards

def generate_quiz_from_summary(summary: str, max_questions: int = 5):
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', summary) if s.strip()]
    questions = []
    for i, sentence in enumerate(sentences[:max_questions]):
        correct = sentence
        distractors = random.sample([s for s in sentences if s != correct], k=min(3, len(sentences)-1)) if len(sentences) > 3 else ["Not mentioned", "None of the above", "Unknown"]
        options = [correct] + distractors
        random.shuffle(options)
        questions.append({
            "id": i + 1,
            "question": f"Which of the following best summarizes: \"{sentence}\"?",
            "options": options,
            "correctAnswer": options.index(correct)
        })
    return questions

# Create a singleton instance
model_processor = ModelProcessor() 