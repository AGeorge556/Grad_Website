import os
import json
import logging
from typing import List, Dict, Any, Optional
import time

# Fix the import - VertexAI is not directly importable in some versions
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google Vertex AI
try:
    # Check for GOOGLE_APPLICATION_CREDENTIALS environment variable
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.warning("GOOGLE_APPLICATION_CREDENTIALS not found in environment variables")
    
    # Initialize VertexAI
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if project_id:
        # Use the correct initialization method based on the installed version
        aiplatform.init(project=project_id, location=location)
        logger.info("Google Vertex AI initialized successfully")
    else:
        logger.warning("GOOGLE_CLOUD_PROJECT not found in environment variables")
        
except Exception as e:
    logger.error(f"Failed to initialize Google Vertex AI: {str(e)}")

def generate_response(prompt_text: str, system_prompt: str = None) -> str:
    """
    Generate a response using Gemini 1.0 Pro model
    
    Args:
        prompt_text: The user prompt text
        system_prompt: Optional system prompt to set context
        
    Returns:
        The generated text response
    """
    try:
        # Initialize the Gemini model
        model = GenerativeModel("gemini-1.0-pro")
        
        if system_prompt:
            # For Gemini, we need to include the system prompt as part of the conversation
            chat = model.start_chat(system_instruction=system_prompt)
            response = chat.send_message(prompt_text)
        else:
            # Simple single prompt
            response = model.generate_content(prompt_text)
            
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating response with Gemini: {str(e)}")
        raise ValueError(f"Gemini API error: {str(e)}")

class GeminiService:
    """Backend service for Google Vertex AI Gemini API calls"""
    
    def __init__(self):
        self.model_name = "gemini-1.0-pro"
        self.is_configured = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.getenv("GOOGLE_CLOUD_PROJECT"))
        
    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Make a request to Gemini API with error handling"""
        if not self.is_configured:
            raise ValueError("Google Vertex AI is not properly configured. Please check GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        
        try:
            # Extract system message if present
            system_prompt = None
            user_messages = []
            
            for message in messages:
                if message["role"] == "system":
                    system_prompt = message["content"]
                elif message["role"] == "user":
                    user_messages.append(message["content"])
            
            # Combine all user messages into a single prompt
            prompt_text = "\n".join(user_messages)
            
            # Initialize the model
            model = GenerativeModel(self.model_name)
            
            if system_prompt:
                # With system instruction
                chat = model.start_chat(system_instruction=system_prompt)
                response = chat.send_message(prompt_text)
            else:
                # Without system instruction
                response = model.generate_content(prompt_text)
                
            return response.text
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            if "permissions" in str(e).lower() or "credentials" in str(e).lower():
                raise ValueError("Authentication error: Please check your Google Cloud credentials")
            elif "quota" in str(e).lower() or "rate" in str(e).lower():
                raise ValueError("Rate limit exceeded: Please try again later")
            else:
                raise ValueError(f"Gemini API error: {str(e)}")
    
    async def generate_suggestions(self, transcript: str) -> List[Dict[str, str]]:
        """Generate educational suggestions from transcript"""
        try:
            if not transcript or len(transcript.strip()) == 0:
                return []
            
            # Truncate transcript if too long to avoid token limits
            max_transcript_length = 3000
            if len(transcript) > max_transcript_length:
                transcript = transcript[:max_transcript_length] + "..."
            
            prompt = f"""Analyze this transcript and generate 3-5 relevant educational questions or discussion points. 
            
Format your response as a JSON array of objects, where each object has:
- id: a unique string identifier (like "suggestion-1", "suggestion-2", etc.)
- text: the full question or discussion point
- shortcut: a brief version of the text (max 5 words)

Transcript: {transcript}

Respond with ONLY the JSON array, no additional text or formatting."""
            
            messages = [
                {"role": "system", "content": "You are an educational assistant that generates quiz and discussion content from transcripts."},
                {"role": "user", "content": prompt}
            ]
            
            response_content = self._make_request(messages, max_tokens=800)
            
            if not response_content:
                return []
            
            # Clean the response to ensure it's valid JSON
            cleaned_content = response_content.strip()
            # Remove markdown code blocks if present
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            try:
                suggestions_data = json.loads(cleaned_content)
                
                if not isinstance(suggestions_data, list):
                    logger.warning("Response is not a JSON array")
                    return []
                
                suggestions = []
                for i, item in enumerate(suggestions_data[:5]):  # Limit to 5 suggestions
                    suggestion = {
                        "id": item.get("id", f"suggestion-{i+1}"),
                        "text": item.get("text", ""),
                        "shortcut": item.get("shortcut", item.get("text", "")[:30] + "..." if len(item.get("text", "")) > 30 else item.get("text", ""))
                    }
                    if suggestion["text"]:  # Only add if text is not empty
                        suggestions.append(suggestion)
                
                return suggestions
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}, Content: {cleaned_content}")
                return []
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []
    
    async def send_message(self, message: str) -> str:
        """Send a chat message and get response"""
        try:
            if not message or len(message.strip()) == 0:
                return "Please provide a message."
            
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant focused on educational content and learning."},
                {"role": "user", "content": message}
            ]
            
            response_content = self._make_request(messages, max_tokens=1000)
            
            if not response_content:
                return "I'm sorry, I couldn't generate a response. Please try again."
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                return "AI assistant is not available. Please check the API configuration."
            else:
                return "Failed to get a response from the AI assistant. Please try again later."

# Create a global instance
gemini_service = GeminiService()

# Convenience functions for API compatibility
async def gemini_generate_suggestions(transcript: str) -> List[Dict[str, str]]:
    """Generate suggestions from transcript (returns dict format)"""
    return await gemini_service.generate_suggestions(transcript)

async def gemini_chat(message: str) -> str:
    """Send chat message to Gemini (returns string response)"""
    return await gemini_service.send_message(message)

# Fallback functions for compatibility with enhanced_openai_utils.py
def gemini_generate_flashcards(summary: str, max_flashcards: int = 3):
    """Generate flashcards from summary"""
    try:
        # Create a model instance
        model = GenerativeModel("gemini-1.0-pro")
        
        prompt = f"""Create {max_flashcards} educational flashcards from this content.
        
Each flashcard should be a JSON object with:
- "question": A clear, specific question
- "answer": A comprehensive but concise answer
- "concept": The main concept being tested
- "bloom_level": One of ["remember", "understand", "apply"]
- "difficulty": "medium"

Return ONLY a JSON array of {max_flashcards} objects, no extra text.

Content: {summary}
"""
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Extract JSON
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            cards = json.loads(text[start:end])
            for i, card in enumerate(cards):
                if isinstance(card, dict) and 'question' in card and 'answer' in card:
                    card.setdefault('id', i + 1000)
                    card.setdefault('concept', 'General Topic')
                    card.setdefault('bloom_level', 'understand')
                    card.setdefault('difficulty', 'medium')
                    card.setdefault('examples', [])
                    card.setdefault('mnemonic', '')
            return cards[:max_flashcards]
        return []
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        return []

def gemini_generate_quizzes(summary: str, max_questions: int = 3):
    """Generate quizzes from summary"""
    try:
        # Create a model instance
        model = GenerativeModel("gemini-1.0-pro")
        
        prompt = f"""Create {max_questions} multiple choice questions from this educational content.
        
Each question should be a JSON object with:
- "question": A clear, specific question
- "options": Array of exactly 4 answer choices
- "correct_answer": Index (0-3) of the correct answer
- "explanation": Brief explanation of why the answer is correct

Return ONLY a JSON array of {max_questions} objects, no extra text.

Content: {summary}
"""
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Extract JSON
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            questions = json.loads(text[start:end])
            for i, q in enumerate(questions):
                if isinstance(q, dict) and 'question' in q and 'options' in q and 'correct_answer' in q:
                    q.setdefault('id', i + 1000)
                    q.setdefault('type', 'multiple_choice')
                    q.setdefault('bloom_level', 'understand')
                    q.setdefault('difficulty', 'medium')
                    q.setdefault('key_concepts', ['General Topic'])
            return questions[:max_questions]
        return []
    except Exception as e:
        logger.error(f"Error generating quizzes: {e}")
        return []

def gemini_video_chat(summary: str, user_message: str):
    """Chat about video content"""
    try:
        # Create a model instance
        model = GenerativeModel("gemini-1.0-pro")
        
        prompt = f"""Given this summary: {summary}
Answer the following question as an AI tutor: {user_message}"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error in video chat: {e}")
        return "I'm sorry, I couldn't process your question. Please try again." 