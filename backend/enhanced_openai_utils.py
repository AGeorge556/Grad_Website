import os
import json
import random
from typing import List, Dict, Optional, Tuple, Any
import logging
import re
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI client setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY environment variable not found. OpenAI functions will not work.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_model():
    """Return the preferred OpenAI model, with fallback"""
    try:
        # Try GPT-4o first, fallback to GPT-3.5-turbo if unavailable
        return "gpt-4o"
    except Exception:
        return "gpt-3.5-turbo"

def make_openai_request(system_prompt: str, user_prompt: str, max_retries: int = 3) -> str:
    """Make a request to OpenAI with error handling and retries"""
    if client is None:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
    
    model = get_openai_model()
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                if "gpt-4o" in model:
                    # Fallback to GPT-3.5-turbo
                    logger.warning("Falling back to GPT-3.5-turbo")
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.7,
                            max_tokens=2000
                        )
                        return response.choices[0].message.content.strip()
                    except Exception as fallback_error:
                        logger.error(f"Fallback model error: {fallback_error}")
                        raise
                else:
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
    """Extract key concepts from the summary using OpenAI"""
    system_prompt = "You are an educational assistant that extracts key concepts from transcripts."
    user_prompt = f"""
    Analyze the following educational content and extract the 5-10 most important key concepts, terms, or topics.
    Return only a JSON array of strings, no extra text.
    
    Content: {summary}
    """
    
    try:
        response_text = make_openai_request(system_prompt, user_prompt)
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
        response_text = make_openai_request(system_prompt, user_prompt)
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
        response_text = make_openai_request(system_prompt, user_prompt)
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
                    q['feedback_correct'] = f"Excellent! This demonstrates {q['bloom_level']}-level thinking."
                    q['feedback_incorrect'] = f"Not quite. This question tests {q['bloom_level']}-level understanding. {q.get('explanation', '')}"
                    questions.append(q)
                    
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        # Generate fallback questions
        for i in range(max_questions):
            questions.append({
                'id': random.randint(1000, 9999),
                'question': 'What is General Topic?',
                'type': 'multiple_choice',
                'bloom_level': random.choice(['remember', 'understand', 'apply', 'analyze']),
                'difficulty': random.choice(['easy', 'medium', 'hard']),
                'options': ['Key concept from the content', 'Alternative definition', 'Incorrect definition', 'Unrelated concept'],
                'correct_answer': 0,
                'explanation': 'General Topic is defined as: Key concept from the content',
                'key_concepts': ['General Topic'],
                'feedback_correct': f"Excellent! This demonstrates {random.choice(['remember', 'understand', 'apply', 'analyze'])}-level thinking.",
                'feedback_incorrect': f"Not quite. This question tests {random.choice(['remember', 'understand', 'apply', 'analyze'])}-level understanding. General Topic is defined as: Key concept from the content"
            })
    
    return questions[:max_questions]

def generate_positive_feedback() -> str:
    """Generate encouraging feedback for correct answers"""
    feedback_options = [
        "Excellent! You've got it right.",
        "Perfect! Great understanding of the concept.",
        "Correct! You're really grasping this material.",
        "Well done! That's exactly right.",
        "Outstanding! You clearly understand this topic.",
        "Fantastic! Your knowledge is showing.",
        "Right on target! Keep up the great work.",
        "Brilliant! You've mastered this concept."
    ]
    return random.choice(feedback_options)

def generate_constructive_feedback(question: Dict) -> str:
    """Generate constructive feedback for incorrect answers"""
    question_type = question.get('type', 'multiple_choice')
    
    if question_type == 'multiple_choice':
        correct_answer = question['options'][question['correct_answer']] if 'options' in question and 'correct_answer' in question else "the correct answer"
        return f"Not quite right. The correct answer is {correct_answer}. {question.get('explanation', '')}"
    elif question_type == 'true_false':
        correct = "True" if question.get('correct_answer', 0) == 0 else "False"
        return f"Actually, the statement is {correct}. {question.get('explanation', '')}"
    else:
        return f"Good attempt! Here's what we were looking for: {question.get('sample_answer', 'Review the key concepts and try again.')}"

def enhanced_openai_video_chat(summary: str, user_message: str, conversation_context: List[Dict] = None) -> str:
    """Enhanced video chat with conversation context using OpenAI"""
    context_prompt = ""
    if conversation_context:
        context_prompt = "\n\nConversation history:\n"
        for msg in conversation_context[-3:]:  # Last 3 messages
            context_prompt += f"{msg['role']}: {msg['content']}\n"
    
    system_prompt = "You are an expert AI tutor helping a student understand educational content."
    user_prompt = f"""
    LESSON CONTENT: {summary}
    {context_prompt}
    
    STUDENT QUESTION: {user_message}
    
    Provide a helpful, educational response that:
    - Directly addresses the student's question
    - References the lesson content when relevant
    - Uses clear, encouraging language
    - Offers additional insights or connections
    - Suggests follow-up questions or topics to explore
    """
    
    try:
        return make_openai_request(system_prompt, user_prompt)
    except Exception as e:
        logger.error(f"Enhanced video chat error: {e}")
        return "I apologize, but I'm having trouble responding right now. Could you please rephrase your question?"

# Enums and dataclasses (keeping same structure)
class BloomLevel(Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand" 
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    CASE_STUDY = "case_study"
    COMPARISON = "comparison"
    DEFINITION = "definition"
    EXAMPLE = "example"
    CAUSE_EFFECT = "cause_effect"

class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class Concept:
    name: str
    definition: str
    examples: List[str]
    related_concepts: List[str]
    domain: str
    importance: float  # 0-1 scale

@dataclass
class GeneratedQuestion:
    question: str
    question_type: QuestionType
    bloom_level: BloomLevel
    difficulty: DifficultyLevel
    options: Optional[List[str]] = None
    correct_answer: Optional[int] = None
    explanation: str = ""
    distractors_rationale: List[str] = None
    key_concepts: List[str] = None

@dataclass
class GeneratedFlashcard:
    front: str
    back: str
    concept: str
    bloom_level: BloomLevel
    difficulty: DifficultyLevel
    examples: List[str] = None
    mnemonics: str = ""

class AdvancedContentGenerator:
    def __init__(self, api_key: str):
        # Store API key for OpenAI
        self.api_key = api_key
        global OPENAI_API_KEY, client
        if api_key:
            OPENAI_API_KEY = api_key
            client = OpenAI(api_key=api_key)
        elif not OPENAI_API_KEY:
            raise ValueError("No OpenAI API key provided and OPENAI_API_KEY environment variable not set.")
        
        # Domain-specific knowledge bases
        self.domain_patterns = {
            'machine_learning': {
                'key_terms': ['supervised', 'unsupervised', 'reinforcement', 'neural network', 'algorithm', 'training', 'validation', 'overfitting'],
                'common_confusions': [
                    ('supervised', 'unsupervised'),
                    ('classification', 'regression'),
                    ('training', 'testing'),
                    ('precision', 'recall')
                ],
                'application_domains': ['computer vision', 'natural language processing', 'robotics', 'recommendation systems']
            },
            'computer_science': {
                'key_terms': ['algorithm', 'data structure', 'complexity', 'recursion', 'iteration', 'optimization'],
                'common_confusions': [
                    ('stack', 'queue'),
                    ('breadth-first', 'depth-first'),
                    ('time complexity', 'space complexity')
                ],
                'application_domains': ['software engineering', 'databases', 'networks', 'security']
            }
        }

    def extract_concepts(self, content: str) -> List[Concept]:
        """Extract key concepts from content using OpenAI."""
        
        system_prompt = "You are an educational assistant that extracts key concepts from transcripts."
        user_prompt = f"""
        Analyze the following educational content and extract key concepts. For each concept, provide:
        1. The concept name
        2. A clear, concise definition
        3. 2-3 concrete examples or use cases
        4. Related concepts that students might confuse it with
        5. The domain/field it belongs to
        6. Importance level (1-10 scale)

        Content to analyze:
        {content}

        Return the response as a JSON array with this structure:
        [
            {{
                "name": "concept name",
                "definition": "clear definition",
                "examples": ["example1", "example2"],
                "related_concepts": ["related1", "related2"],
                "domain": "field name",
                "importance": 8.5
            }}
        ]
        """

        try:
            response_text = make_openai_request(system_prompt, user_prompt)
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            
            if start != -1 and end != -1:
                concepts_data = json.loads(response_text[start:end])
                
                concepts = []
                for data in concepts_data:
                    concept = Concept(
                        name=data.get('name', 'General Topic'),
                        definition=data.get('definition', 'Key concept from the content'),
                        examples=data.get('examples', []),
                        related_concepts=data.get('related_concepts', []),
                        domain=data.get('domain', 'General'),
                        importance=data.get('importance', 5.0) / 10.0
                    )
                    concepts.append(concept)
                
                return concepts
                
        except Exception as e:
            logger.error(f"Error extracting concepts: {e}")
            return [Concept("General Topic", "Key concept from the content", [], [], "General", 0.5)]

    def generate_balanced_content(self, content: str, num_questions: int = 3, 
                                num_flashcards: int = 3) -> Dict[str, Any]:
        """Generate a balanced set of questions and flashcards."""
        
        # Extract concepts from content
        concepts = self.extract_concepts(content)
        if not concepts:
            logger.warning("No concepts extracted, using fallback")
            concepts = [Concept("General Topic", "Key concept from the content", 
                              [], [], "General", 0.5)]
        
        # Generate flashcards and questions
        flashcards = generate_enhanced_flashcards(content, num_flashcards)
        questions = generate_enhanced_quizzes(content, num_questions)
        
        return {
            'questions': questions,
            'flashcards': flashcards,
            'concepts': [self._concept_to_dict(c) for c in concepts],
            'metadata': {
                'total_questions': len(questions),
                'total_flashcards': len(flashcards)
            }
        }

    def _concept_to_dict(self, concept: Concept) -> Dict[str, Any]:
        """Convert Concept dataclass to dictionary."""
        return {
            'name': concept.name,
            'definition': concept.definition,
            'examples': concept.examples,
            'related_concepts': concept.related_concepts,
            'domain': concept.domain,
            'importance': concept.importance
        }

# Backward compatibility functions
def generate_flashcards(content: str, api_key: str, num_cards: int = 3) -> List[Dict[str, Any]]:
    """Generate enhanced flashcards with backward compatibility."""
    generator = AdvancedContentGenerator(api_key)
    result = generator.generate_balanced_content(content, num_questions=0, num_flashcards=num_cards)
    return result['flashcards']

def generate_quiz_questions(content: str, api_key: str, num_questions: int = 3) -> List[Dict[str, Any]]:
    """Generate enhanced quiz questions with backward compatibility."""
    generator = AdvancedContentGenerator(api_key)
    result = generator.generate_balanced_content(content, num_questions=num_questions, num_flashcards=0)
    return result['questions']

def generate_enhanced_content(content: str, api_key: str, num_questions: int = 3, 
                            num_flashcards: int = 3) -> Dict[str, Any]:
    """Generate comprehensive enhanced educational content."""
    generator = AdvancedContentGenerator(api_key)
    return generator.generate_balanced_content(content, num_questions, num_flashcards)

# Legacy functions for backward compatibility (renamed from gemini_ to openai_)
def openai_generate_flashcards(summary: str, max_flashcards: int = 3):
    """Legacy function - returns simple format for backward compatibility"""
    enhanced_cards = generate_enhanced_flashcards(summary, max_flashcards)
    return [{"question": card["question"], "answer": card["answer"]} for card in enhanced_cards]

def openai_generate_quizzes(summary: str, max_questions: int = 3):
    """Legacy function - returns simple format for backward compatibility"""
    enhanced_quizzes = generate_enhanced_quizzes(summary, max_questions)
    return enhanced_quizzes

def openai_video_chat(summary: str, user_message: str):
    """Legacy function for backward compatibility"""
    return enhanced_openai_video_chat(summary, user_message)

# Keep the gemini_ function names for compatibility but use OpenAI
def gemini_generate_flashcards(summary: str, max_flashcards: int = 3):
    """Legacy function name maintained for backward compatibility"""
    return openai_generate_flashcards(summary, max_flashcards)

def gemini_generate_quizzes(summary: str, max_questions: int = 3):
    """Legacy function name maintained for backward compatibility"""
    return openai_generate_quizzes(summary, max_questions)

def gemini_video_chat(summary: str, user_message: str):
    """Legacy function name maintained for backward compatibility"""
    return openai_video_chat(summary, user_message)

def enhanced_gemini_video_chat(summary: str, user_message: str, conversation_context: List[Dict] = None) -> str:
    """Legacy function name maintained for backward compatibility"""
    return enhanced_openai_video_chat(summary, user_message, conversation_context)
