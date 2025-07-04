import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import openai
from openai import OpenAI
import time

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Mistral client
mistral_api_key = os.getenv("MISTRAL_API_KEY")
if not mistral_api_key:
    logger.warning("MISTRAL_API_KEY not found in environment variables")

# Mistral API client configuration
client = None
if mistral_api_key:
    try:
        # Mistral uses OpenAI-compatible API
        client = OpenAI(
            api_key=mistral_api_key,
            base_url="https://api.mistral.ai/v1"
        )
        logger.info("Mistral client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Mistral client: {str(e)}")

@dataclass
class Suggestion:
    id: str
    text: str
    shortcut: str

class MistralService:
    """Backend service for Mistral AI API calls"""
    
    def __init__(self):
        self.model = "mistral-large-latest"
        self.is_configured = bool(client and mistral_api_key)
        
    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Make a request to Mistral API with error handling"""
        if not self.is_configured:
            raise ValueError("Mistral API is not properly configured. Please check MISTRAL_API_KEY environment variable.")
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError("No response received from Mistral API")
                
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                raise ValueError("Unauthorized: Please check your Mistral API key")
            elif "403" in str(e) or "forbidden" in str(e).lower():
                raise ValueError("Forbidden: Your API key doesn't have permission to access this resource")
            elif "429" in str(e) or "rate limit" in str(e).lower():
                raise ValueError("Rate limit exceeded: Please try again later")
            else:
                logger.error(f"Mistral API error: {str(e)}")
                raise ValueError(f"Mistral API error: {str(e)}")
    
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
mistral_service = MistralService()

# Convenience functions for backward compatibility
async def mistral_generate_suggestions(transcript: str) -> List[Dict[str, str]]:
    """Generate suggestions from transcript (returns dict format)"""
    suggestions = await mistral_service.generate_suggestions(transcript)
    return [
        {
            "id": s.id,
            "text": s.text,
            "shortcut": s.shortcut
        }
        for s in suggestions
    ]

async def mistral_chat(message: str) -> str:
    """Send chat message to Mistral (returns string response)"""
    return await mistral_service.send_message(message) 