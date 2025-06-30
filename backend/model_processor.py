import io
import os
from pathlib import Path
# import fleep  # Not needed
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

# Import enhanced content generation
try:
    from .enhanced_openai_utils import generate_enhanced_content, AdvancedContentGenerator
except ImportError:
    try:
        from enhanced_openai_utils import generate_enhanced_content, AdvancedContentGenerator
    except ImportError:
        print("Warning: enhanced_openai_utils not available, using fallback generation")
        AdvancedContentGenerator = None

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
            
            # Generate enhanced flashcards and quizzes from summary
            flashcards, quizzes = generate_enhanced_content_from_summary(summary)
            
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

def generate_enhanced_content_from_summary(summary: str):
    """Generate sophisticated flashcards and quizzes using the enhanced AI system."""
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key or AdvancedContentGenerator is None:
            print("Warning: Enhanced generation not available, using improved fallback")
            return generate_fallback_content(summary)
        
        # Use the enhanced content generator
        generator = AdvancedContentGenerator(openai_api_key)
        result = generator.generate_balanced_content(
            content=summary,
            num_questions=3,  # Reasonable number for video processing
            num_flashcards=3
        )
        
        return result['flashcards'], result['questions']
        
    except Exception as e:
        print(f"Error in enhanced content generation: {e}")
        print("Falling back to improved generation...")
        return generate_fallback_content(summary)

def generate_fallback_content(summary: str):
    """Fallback content generation if enhanced system fails."""
    # Much better fallback than the original terrible version
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', summary) if s.strip() and len(s.strip()) > 10]
    
    # Better flashcards
    flashcards = []
    for i, sentence in enumerate(sentences[:3]):
        # Extract key concept from sentence
        words = sentence.split()
        key_concept = " ".join(words[:3]) if len(words) >= 3 else sentence
        
        flashcard = {
            "id": i + 1,
            "question": f"Explain the concept: {key_concept}",
            "answer": sentence,
            "concept": key_concept,
            "bloom_level": "understand",
            "difficulty": 2
        }
        flashcards.append(flashcard)
    
    # Better quiz questions
    quizzes = []
    for i, sentence in enumerate(sentences[:3]):
        # Create a conceptual question instead of just repeating the sentence
        words = sentence.split()
        if len(words) > 5:
            question_stem = f"What is the main idea about {' '.join(words[:3])}?"
        else:
            question_stem = f"Which statement is correct about the topic?"
        
        # Create better distractors
        other_sentences = [s for s in sentences if s != sentence]
        distractors = []
        
        if len(other_sentences) >= 3:
            distractors = random.sample(other_sentences, 3)
        else:
            distractors = other_sentences + [
                "This concept is not relevant to the topic",
                "The opposite of the correct statement",
                "A related but incorrect concept"
            ][:3]
        
        options = [sentence] + distractors[:3]
        random.shuffle(options)
        
        quiz = {
            "id": i + 1,
            "question": question_stem,
            "type": "multiple_choice",
            "options": options,
            "correct_answer": options.index(sentence),
            "difficulty": "medium",
            "explanation": f"The correct answer explains: {sentence[:100]}..."
        }
        quizzes.append(quiz)
    
    return flashcards, quizzes

# Create a singleton instance
model_processor = ModelProcessor() 