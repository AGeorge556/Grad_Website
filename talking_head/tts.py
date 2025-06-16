import os
import logging
from gtts import gTTS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def text_to_speech_mock(text, output_path):
    """
    Convert text to speech using gTTS and save to the specified path.
    
    Args:
        text (str): The text to convert to speech
        output_path (str): The path to save the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        
        logger.info(f"Generated audio file with gTTS: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return False 