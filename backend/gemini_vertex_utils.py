import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

# Fix the import - VertexAI is not directly importable in some versions
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google Vertex AI
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

if not GOOGLE_APPLICATION_CREDENTIALS:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS not found in environment variables")

if not GOOGLE_CLOUD_PROJECT:
    logger.warning("GOOGLE_CLOUD_PROJECT environment variable not found")

# Initialize Vertex AI if credentials are available
client = None
vertex_ai_initialized = False
if GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT:
    try:
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        # Use the correct initialization method
        aiplatform.init(project=GOOGLE_CLOUD_PROJECT, location=location)
        vertex_ai_initialized = True
        logger.info("Google Vertex AI initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google Vertex AI: {str(e)}")

@dataclass
class Suggestion:
    id: str
    text: str
    shortcut: str

class GeminiService:
    """Backend service for Google Vertex AI Gemini API calls"""
    
    def __init__(self):
        self.model = "gemini-1.0-pro"
        self.is_configured = vertex_ai_initialized
        
    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Make a request to Gemini API with error handling"""
        if not self.is_configured:
            raise ValueError("Google Vertex AI is not properly configured. Please check GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT environment variables.")
        
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
            model = GenerativeModel(self.model)
            
            if system_prompt:
                # With system instruction
                chat = model.start_chat(system_instruction=system_prompt)
                response = chat.send_message(prompt_text)
            else:
                # Without system instruction
                response = model.generate_content(prompt_text)
                
            return response.text
                
        except Exception as e:
            if "permissions" in str(e).lower() or "credentials" in str(e).lower():
                raise ValueError("Authentication error: Please check your Google Cloud credentials")
            elif "quota" in str(e).lower() or "rate" in str(e).lower():
                raise ValueError("Rate limit exceeded: Please try again later")
            else:
                logger.error(f"Gemini API error: {str(e)}")
                raise ValueError(f"Gemini API error: {str(e)}")
    
    async def generate_suggestions(self, transcript: str) -> List[Suggestion]:
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
                    suggestion = Suggestion(
                        id=item.get("id", f"suggestion-{i+1}"),
                        text=item.get("text", ""),
                        shortcut=item.get("shortcut", item.get("text", "")[:30] + "..." if len(item.get("text", "")) > 30 else item.get("text", ""))
                    )
                    if suggestion.text:  # Only add if text is not empty
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
            if "api key" in str(e).lower() or "unauthorized" in str(e).lower():
                return "AI assistant is not available. Please check the API configuration."
            else:
                return "Failed to get a response from the AI assistant. Please try again later."

# Create a global instance
gemini_service = GeminiService()

# Convenience functions for API compatibility
async def gemini_generate_suggestions(transcript: str) -> List[Dict[str, str]]:
    """Generate suggestions from transcript (returns dict format)"""
    suggestions = await gemini_service.generate_suggestions(transcript)
    return [
        {
            "id": s.id,
            "text": s.text,
            "shortcut": s.shortcut
        }
        for s in suggestions
    ]

async def gemini_chat(message: str) -> str:
    """Send chat message to Gemini (returns string response)"""
    return await gemini_service.send_message(message) 