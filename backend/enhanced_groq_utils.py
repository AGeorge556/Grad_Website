import os
import requests
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
groq_api_key = os.getenv("GROQ_API_KEY")

# In-memory conversation storage (in production, use Redis or database)
conversation_store = {}

class ConversationContext:
    def __init__(self, user_id: str = None, topic: str = None):
        self.user_id = user_id or "default"
        self.topic = topic
        self.messages = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.educational_context = {}
        
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_activity = datetime.now()
        
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages for context"""
        return self.messages[-limit:] if self.messages else []
        
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if conversation has expired"""
        return datetime.now() - self.last_activity > timedelta(hours=timeout_hours)

def get_conversation_context(user_id: str = None, topic: str = None) -> ConversationContext:
    """Get or create conversation context"""
    key = f"{user_id or 'default'}:{topic or 'general'}"
    
    if key not in conversation_store or conversation_store[key].is_expired():
        conversation_store[key] = ConversationContext(user_id, topic)
    
    return conversation_store[key]

def detect_vague_input(message: str) -> Tuple[bool, str]:
    """Detect vague or ambiguous inputs and suggest clarifications"""
    vague_patterns = [
        ("this", "Could you be more specific about what 'this' refers to?"),
        ("that thing", "What specific concept or topic are you referring to?"),
        ("explain", "What specific aspect would you like me to explain?"),
        ("help", "What particular topic or concept can I help you with?"),
        ("confused", "What specific part is confusing? I'd be happy to clarify."),
        ("don't understand", "Which concept specifically would you like me to break down?"),
    ]
    
    message_lower = message.lower()
    
    # Check for very short messages
    if len(message.strip()) < 10:
        return True, "Could you provide a bit more detail about what you'd like to learn or discuss?"
    
    # Check for vague patterns
    for pattern, suggestion in vague_patterns:
        if pattern in message_lower and len(message.strip()) < 50:
            return True, suggestion
            
    return False, ""

def generate_educational_prompt(message: str, context: ConversationContext, summary: str = None) -> str:
    """Generate an enhanced educational prompt with context"""
    
    # Base system prompt with educational focus
    system_prompt = """You are an expert AI tutor with the following characteristics:

🎓 EDUCATIONAL APPROACH:
- Use the Socratic method when appropriate - ask guiding questions to help students discover answers
- Break complex topics into digestible chunks
- Provide real-world examples and analogies
- Encourage critical thinking and deeper understanding
- Adapt your explanation level to the student's apparent knowledge level

📚 TEACHING STYLE:
- Be supportive, patient, and encouraging
- Use clear, concise language
- Provide step-by-step explanations when needed
- Offer multiple perspectives on complex topics
- Connect new concepts to previously discussed material

🔍 INTERACTION GUIDELINES:
- If a question is vague, ask clarifying questions
- Provide comprehensive but not overwhelming answers
- Use formatting (bullet points, numbered lists) for clarity
- Offer follow-up questions to deepen understanding
- Suggest related topics for further exploration

💡 LEARNING ENHANCEMENT:
- Identify key concepts and highlight them
- Provide memory aids and mnemonics when helpful
- Suggest practice problems or exercises when appropriate
- Offer different learning approaches (visual, auditory, kinesthetic)
"""

    # Add conversation context
    context_prompt = ""
    recent_messages = context.get_recent_messages(5)
    if recent_messages:
        context_prompt = "\n\n📋 CONVERSATION CONTEXT:\n"
        for msg in recent_messages[-3:]:  # Last 3 messages for context
            role_emoji = "🎓" if msg["role"] == "assistant" else "👤"
            context_prompt += f"{role_emoji} {msg['role'].title()}: {msg['content'][:200]}...\n"
    
    # Add topic/summary context if available
    topic_context = ""
    if summary:
        topic_context = f"\n\n📖 LESSON CONTEXT:\n{summary[:500]}..."
    elif context.topic:
        topic_context = f"\n\n📝 CURRENT TOPIC: {context.topic}"
    
    # Add educational context
    educational_context = ""
    if context.educational_context:
        educational_context = "\n\n🎯 LEARNING OBJECTIVES:\n"
        for key, value in context.educational_context.items():
            educational_context += f"- {key}: {value}\n"
    
    return f"{system_prompt}{context_prompt}{topic_context}{educational_context}"

def enhanced_groq_chat(message: str, user_id: str = None, topic: str = None, summary: str = None) -> Dict:
    """Enhanced chat function with conversation context and educational features"""
    
    try:
        # Get conversation context
        context = get_conversation_context(user_id, topic)
        
        # Check for vague input
        is_vague, clarification = detect_vague_input(message)
        if is_vague:
            context.add_message("user", message)
            context.add_message("assistant", clarification, {"type": "clarification"})
            return {
                "response": clarification,
                "type": "clarification",
                "suggestions": [
                    "Try asking about a specific concept or topic",
                    "Provide more context about what you're studying",
                    "Ask a more detailed question about the material"
                ]
            }
        
        # Generate enhanced prompt
        system_prompt = generate_educational_prompt(message, context, summary)
        
        # Prepare messages for API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        recent_messages = context.get_recent_messages(8)
        for msg in recent_messages:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        print(f"[DEBUG] Enhanced Groq request with {len(messages)} messages", flush=True)
        
        # Make API request
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_api_key}"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800,  # Increased for more detailed educational responses
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
        )
        
        response.raise_for_status()
        data = response.json()
        
        assistant_response = data["choices"][0]["message"]["content"]
        
        # Store conversation
        context.add_message("user", message)
        context.add_message("assistant", assistant_response, {"type": "educational_response"})
        
        # Generate follow-up suggestions based on response
        follow_up_suggestions = generate_follow_up_suggestions(message, assistant_response, context)
        
        print(f"[DEBUG] Enhanced Groq response generated", flush=True)
        
        return {
            "response": assistant_response,
            "type": "educational_response",
            "follow_up_suggestions": follow_up_suggestions,
            "conversation_id": f"{user_id or 'default'}:{topic or 'general'}",
            "message_count": len(context.messages)
        }
        
    except Exception as e:
        print(f"[DEBUG] Enhanced Groq chat error: {e}", flush=True)
        logger.error(f"Enhanced Groq chat error: {e}")
        
        # Still try to store the user message
        try:
            context = get_conversation_context(user_id, topic)
            context.add_message("user", message)
            context.add_message("assistant", "I apologize, but I'm having trouble responding right now. Could you please try rephrasing your question?", {"type": "error"})
        except:
            pass
            
        return {
            "response": "I apologize, but I'm having trouble responding right now. Could you please try rephrasing your question?",
            "type": "error",
            "follow_up_suggestions": [
                "Try asking your question in a different way",
                "Check if there are any specific terms I should know about",
                "Let me know what subject area you're studying"
            ]
        }

def generate_follow_up_suggestions(user_message: str, assistant_response: str, context: ConversationContext) -> List[str]:
    """Generate contextual follow-up suggestions"""
    
    # Basic suggestions based on message content
    message_lower = user_message.lower()
    
    if "explain" in message_lower or "what is" in message_lower:
        return [
            "Can you give me an example of this concept?",
            "How does this relate to what we discussed earlier?",
            "What are the practical applications of this?"
        ]
    elif "how" in message_lower:
        return [
            "Can you break this down into steps?",
            "What are some common mistakes to avoid?",
            "Are there alternative approaches to this?"
        ]
    elif "why" in message_lower:
        return [
            "What are the underlying principles here?",
            "How does this connect to broader concepts?",
            "Can you provide a real-world example?"
        ]
    else:
        return [
            "Can you elaborate on this topic?",
            "What questions do you have about this?",
            "Would you like to explore related concepts?"
        ]

def clear_conversation_context(user_id: str = None, topic: str = None):
    """Clear conversation context for a fresh start"""
    key = f"{user_id or 'default'}:{topic or 'general'}"
    if key in conversation_store:
        del conversation_store[key]

def get_conversation_summary(user_id: str = None, topic: str = None) -> Dict:
    """Get a summary of the current conversation"""
    context = get_conversation_context(user_id, topic)
    
    return {
        "message_count": len(context.messages),
        "duration_minutes": int((context.last_activity - context.created_at).total_seconds() / 60),
        "topic": context.topic,
        "key_concepts": list(context.educational_context.keys()) if context.educational_context else [],
        "last_activity": context.last_activity.isoformat()
    }

# Legacy function for backward compatibility
def groq_chat(message: str) -> str:
    """Legacy function for backward compatibility"""
    result = enhanced_groq_chat(message)
    return result["response"] 