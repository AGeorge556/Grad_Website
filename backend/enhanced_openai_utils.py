import os
import json
import random
from typing import List, Dict, Optional, Tuple, Any
import logging
import re
from dataclasses import dataclass
from enum import Enum
from google.cloud.aiplatform import VertexAI
from vertexai.generative_models import GenerativeModel

# Import our Gemini utilities
from .gemini_utils import generate_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Cloud Vertex AI setup
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

if not GOOGLE_APPLICATION_CREDENTIALS:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not found. Gemini functions will not work.")

if not GOOGLE_CLOUD_PROJECT:
    logger.warning("GOOGLE_CLOUD_PROJECT environment variable not found. Gemini functions will not work.")

# Initialize Vertex AI if credentials are available
vertex_ai_initialized = False
if GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT:
    try:
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        VertexAI(project=GOOGLE_CLOUD_PROJECT, location=location)
        vertex_ai_initialized = True
        logger.info("Google Vertex AI initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google Vertex AI: {str(e)}")

def make_gemini_request(system_prompt: str, user_prompt: str, max_retries: int = 3) -> str:
    """Make a request to Gemini with error handling and retries"""
    if not vertex_ai_initialized:
        raise ValueError("Google Vertex AI not initialized. Please set GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT environment variables.")
    
    for attempt in range(max_retries):
        try:
            return generate_response(user_prompt, system_prompt)
        except Exception as e:
            logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                    raise
    return ""

# Bloom's Taxonomy levels for educational content
BLOOMS_TAXONOMY = {
    "remember": {
        "level": 1,
        "description": "Recall facts and basic concepts",
        "keywords": ["define", "list", "recall", "identify", "name", "state"],
        "question_starters": ["What is", "Who was", "When did", "Where is", "List the", "Define"]
    },
    "understand": {
        "level": 2,
        "description": "Explain ideas or concepts",
        "keywords": ["explain", "describe", "summarize", "interpret", "classify"],
        "question_starters": ["Explain why", "Describe how", "Summarize the", "What does this mean", "How would you interpret"]
    },
    "apply": {
        "level": 3,
        "description": "Use information in new situations",
        "keywords": ["apply", "demonstrate", "solve", "use", "implement"],
        "question_starters": ["How would you use", "Apply this concept to", "Solve this problem", "Demonstrate how"]
    },
    "analyze": {
        "level": 4,
        "description": "Draw connections among ideas",
        "keywords": ["analyze", "compare", "contrast", "examine", "categorize"],
        "question_starters": ["Compare and contrast", "Analyze the relationship", "What are the differences", "Examine the"]
    },
    "evaluate": {
        "level": 5,
        "description": "Justify a stand or decision",
        "keywords": ["evaluate", "judge", "critique", "assess", "justify"],
        "question_starters": ["Evaluate the effectiveness", "Judge the value of", "Critique this approach", "Assess whether"]
    },
    "create": {
        "level": 6,
        "description": "Produce new or original work",
        "keywords": ["create", "design", "develop", "formulate", "construct"],
        "question_starters": ["Design a solution", "Create a plan", "Develop a strategy", "Formulate a hypothesis"]
    }
}

def extract_key_concepts(summary: str) -> List[str]:
    """Extract key concepts from the summary using Gemini"""
    system_prompt = "You are an educational assistant that extracts key concepts from transcripts."
    user_prompt = f"""
    Analyze the following educational content and extract the 5-10 most important key concepts, terms, or topics.
    Return only a JSON array of strings, no extra text.
    
    Content: {summary}
    """
    
    try:
        response_text = make_gemini_request(system_prompt, user_prompt)
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end != -1:
            concepts = json.loads(response_text[start:end])
            return [c for c in concepts if isinstance(c, str) and c.strip()]
    except Exception as e:
        logger.error(f"Concept extraction error: {e}")
    
    # Fallback: simple keyword extraction
    words = re.findall(r'\b[A-Z][a-z]+\b', summary)
    return list(set(words))[:8]

def generate_enhanced_flashcards(summary: str, max_flashcards: int = 3, difficulty_levels: List[str] = None) -> List[Dict]:
    """Generate flashcards using Bloom's taxonomy for varied cognitive challenge"""
    
    if difficulty_levels is None:
        difficulty_levels = ["remember", "understand", "apply"]
    
    key_concepts = extract_key_concepts(summary)
    flashcards = []
    
    # Generate flashcards
    system_prompt = "You are an educational assistant that generates quiz and flashcard content from transcripts."
    user_prompt = f"""
    Create {max_flashcards} educational flashcards from this content.
    
    Focus on these key concepts if available: {', '.join(key_concepts[:5])}
    
    Each flashcard should be a JSON object with:
    - "question": A clear, specific question
    - "answer": A comprehensive but concise answer
    - "concept": The main concept being tested
    - "bloom_level": One of {difficulty_levels}
    - "difficulty": "medium"
    - "examples": []
    - "mnemonic": ""
    
    Return ONLY a JSON array of {max_flashcards} objects, no extra text.
    
    Content: {summary}
    """
    
    try:
        response_text = make_gemini_request(system_prompt, user_prompt)
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start != -1 and end != -1:
            cards = json.loads(response_text[start:end])
            for i, card in enumerate(cards):
                if (isinstance(card, dict) and 
                    'question' in card and 'answer' in card and 
                    card['question'] and card['answer']):
                    
                    # Add required fields and ID
                    card.setdefault('concept', 'General Topic')
                    card.setdefault('bloom_level', random.choice(difficulty_levels))
                    card.setdefault('difficulty', 'medium')
                    card.setdefault('examples', [])
                    card.setdefault('mnemonic', '')
                    card['id'] = random.randint(1000, 9999)
                    flashcards.append(card)
                    
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        # Generate fallback flashcards
        for i in range(max_flashcards):
            flashcards.append({
                'id': random.randint(1000, 9999),
                'question': 'What is General Topic and why is it important?',
                'answer': 'Key concept from the content\n\nImportance: Key concept in General',
                'concept': 'General Topic',
                'bloom_level': random.choice(difficulty_levels),
                'difficulty': 'medium',
                'examples': [],
                'mnemonic': ''
            })
    
    return flashcards[:max_flashcards]

def generate_enhanced_quizzes(summary: str, max_questions: int = 3) -> List[Dict]:
    """Generate multiple choice quiz questions"""
    
    system_prompt = "You are an educational assistant that generates quiz and flashcard content from transcripts."
    user_prompt = f"""
    Create {max_questions} multiple choice questions from this educational content.
    
    Each question should be a JSON object with:
    - "question": A clear, specific question
    - "type": "multiple_choice"
    - "bloom_level": One of ["remember", "understand", "apply", "analyze"]
    - "difficulty": One of ["easy", "medium", "hard"]
    - "options": Array of exactly 4 answer choices
    - "correct_answer": Index (0-3) of the correct answer
    - "explanation": Brief explanation of why the answer is correct
    - "key_concepts": Array of key concepts tested
    
    Return ONLY a JSON array of {max_questions} objects, no extra text.
    
    Content: {summary}
    """
    
    questions = []
    
    try:
        response_text = make_gemini_request(system_prompt, user_prompt)
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start != -1 and end != -1:
            parsed_questions = json.loads(response_text[start:end])
            for i, q in enumerate(parsed_questions):
                if (isinstance(q, dict) and 
                    'question' in q and 'options' in q and 'correct_answer' in q and
                    isinstance(q['options'], list) and len(q['options']) == 4 and
                    isinstance(q['correct_answer'], int) and 0 <= q['correct_answer'] < 4):
                    
                    # Add required fields and ID
                    q.setdefault('type', 'multiple_choice')
                    q.setdefault('bloom_level', random.choice(['remember', 'understand', 'apply', 'analyze']))
                    q.setdefault('difficulty', random.choice(['easy', 'medium', 'hard']))
                    q.setdefault('explanation', 'Based on the content provided.')
                    q.setdefault('key_concepts', ['General Topic'])
                    q['id'] = random.randint(1000, 9999)
                    questions.append(q)
    except Exception as e:
        logger.error(f"Error generating quizzes: {e}")
        # Generate fallback questions
        for i in range(max_questions):
            questions.append({
                'id': random.randint(1000, 9999),
                'question': 'What is the main topic of this content?',
                'type': 'multiple_choice',
                'bloom_level': random.choice(['remember', 'understand', 'apply', 'analyze']),
                'difficulty': 'medium',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 0,
                'explanation': 'This is the correct answer based on the content.',
                'key_concepts': ['General Topic']
            })
    
    return questions[:max_questions]

def enhanced_gemini_video_chat(summary: str, user_message: str, conversation_context: List[Dict] = None) -> str:
    """Enhanced chat function that incorporates summary context and conversation history"""
    
    if conversation_context is None:
        conversation_context = []
    
    # Build the conversation history
    messages = [
        {"role": "system", "content": f"You are an educational AI tutor. Use this content summary as context for your responses: {summary[:1000]}..."}
    ]
    
    # Add conversation history (up to last 5 messages to avoid token limits)
    for msg in conversation_context[-5:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ["user", "assistant"] and content:
            messages.append({"role": role, "content": content})
    
    # Add the current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Create a model instance
        model = GenerativeModel("gemini-1.0-pro")
        
        # Extract system message
        system_content = messages[0]["content"] if messages and messages[0]["role"] == "system" else None
        
        # Start a chat with the system instruction
        chat = model.start_chat(system_instruction=system_content)
        
        # Add previous messages to the chat history
        for msg in messages[1:]:
            if msg["role"] == "user":
                response = chat.send_message(msg["content"])
        
        # Return the final response
        return response.text
    except Exception as e:
        logger.error(f"Error in enhanced chat: {e}")
        return f"I'm sorry, I couldn't process your question due to a technical issue. Please try again later."

# Keep the original function names but update their implementations
def openai_generate_flashcards(summary: str, max_flashcards: int = 3):
    """Alias for generate_enhanced_flashcards for backward compatibility"""
    return generate_enhanced_flashcards(summary, max_flashcards)

def openai_generate_quizzes(summary: str, max_questions: int = 3):
    """Alias for generate_enhanced_quizzes for backward compatibility"""
    return generate_enhanced_quizzes(summary, max_questions)

def openai_video_chat(summary: str, user_message: str):
    """Alias for enhanced_gemini_video_chat for backward compatibility"""
    return enhanced_gemini_video_chat(summary, user_message)
