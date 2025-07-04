from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request, status, BackgroundTasks, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Import enhanced utilities
from enhanced_groq_utils import enhanced_groq_chat, clear_conversation_context, get_conversation_summary
from enhanced_gemini_utils import (
    generate_enhanced_flashcards,
    generate_enhanced_quizzes,
    enhanced_gemini_video_chat,
    generate_enhanced_content,
    AdvancedContentGenerator
)
from session_manager import session_manager, SessionType, SessionStatus
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Enhanced AI Tutor API", version="2.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Enhanced Pydantic models
class EnhancedChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[str] = None
    topic: Optional[str] = None
    session_id: Optional[str] = None

class FlashcardRequest(BaseModel):
    summary: str = Field(..., min_length=10)
    max_flashcards: int = Field(default=8, ge=3, le=15)
    difficulty_levels: Optional[List[str]] = Field(default=["remember", "understand", "apply"])
    session_id: Optional[str] = None

class QuizRequest(BaseModel):
    summary: str = Field(..., min_length=10)
    max_questions: int = Field(default=6, ge=3, le=12)
    session_id: Optional[str] = None

class SessionRequest(BaseModel):
    user_id: str
    topic: str
    session_type: str  # "chat", "flashcards", "quiz", "video_study"
    summary: Optional[str] = None
    duration_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week

class QuizSubmission(BaseModel):
    session_id: str
    question_id: int
    user_answer: Any
    time_spent: Optional[int] = None  # seconds

class FlashcardReview(BaseModel):
    session_id: str
    card_id: str
    difficulty_rating: int = Field(..., ge=1, le=5)  # 1=too easy, 5=too hard
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    time_spent: Optional[int] = None

# Add validation before SadTalker execution
def validate_sadtalker_setup():
    """Validate SadTalker setup before execution"""
    sadtalker_dir = r"D:\University files\Graduation Project\SadTalker"
    
    # Check if early_compatibility_patch exists
    patch_file = os.path.join(sadtalker_dir, "early_compatibility_patch.py")
    if not os.path.exists(patch_file):
        logger.warning(f"early_compatibility_patch.py not found at {patch_file}")
        return False
    
    # Check if enhanced inference exists
    enhanced_inference_file = os.path.join(sadtalker_dir, "inference_enhanced.py")
    if not os.path.exists(enhanced_inference_file):
        logger.warning(f"inference_enhanced.py not found at {enhanced_inference_file}")
        return False
    
    # Check if functional_tensor_patch exists
    functional_patch_file = os.path.join(sadtalker_dir, "functional_tensor_patch.py")
    if not os.path.exists(functional_patch_file):
        logger.warning(f"functional_tensor_patch.py not found at {functional_patch_file}")
        return False
    
    logger.info("✅ SadTalker setup validation passed")
    return True

# Enhanced Chat Endpoint
@app.post("/enhanced-chat")
@limiter.limit("15/minute")
async def enhanced_chat(request: EnhancedChatMessage, http_request: Request):
    """Enhanced chat with conversation context and educational features"""
    try:
        logger.info(f"Enhanced chat request: {request.message[:100]}...")
        
        # Get or create session if provided
        session = None
        if request.session_id:
            session = session_manager.get_session(request.session_id)
        
        # Use enhanced chat function
        result = enhanced_groq_chat(
            message=request.message,
            user_id=request.user_id,
            topic=request.topic,
            summary=session.summary if session else None
        )
        
        # Update session activity if session exists
        if session:
            session_manager.update_session_activity(
                session_id=request.session_id,
                activity_type="chat",
                content={"message": request.message, "response": result["response"]}
            )
        
        return {
            "success": True,
            "data": result,
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Flashcard Generation
@app.post("/enhanced-flashcards")
@limiter.limit("10/minute")
async def enhanced_flashcards(request: FlashcardRequest, http_request: Request):
    """Generate sophisticated flashcards using advanced AI and Bloom's taxonomy"""
    try:
        logger.info(f"Enhanced flashcards request for {request.max_flashcards} cards")
        
        # Use the new advanced content generator
        generator = AdvancedContentGenerator(GEMINI_API_KEY)
        result = generator.generate_balanced_content(
            content=request.summary,
            num_questions=0,  # Only flashcards
            num_flashcards=request.max_flashcards
        )
        
        flashcards = result['flashcards']
        
        # Update session if provided
        if request.session_id:
            session_manager.update_session_activity(
                session_id=request.session_id,
                activity_type="flashcard_generation",
                content={
                    "flashcards_generated": len(flashcards),
                    "concepts_extracted": len(result.get('concepts', [])),
                    "bloom_distribution": result.get('metadata', {}).get('bloom_distribution', {}),
                    "quality_score": len(result.get('concepts', [])) * 10  # Simple quality metric
                }
            )
        
        return {
            "success": True,
            "flashcards": flashcards,
            "count": len(flashcards),
            "session_id": request.session_id,
            "metadata": {
                "concepts": result.get('concepts', []),
                "bloom_distribution": result.get('metadata', {}).get('bloom_distribution', {}),
                "quality_indicators": {
                    "concept_coverage": len(result.get('concepts', [])),
                    "cognitive_levels": len(set(card.get("bloom_level") for card in flashcards)),
                    "difficulty_range": len(set(str(card.get("difficulty")) for card in flashcards))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced flashcards error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Quiz Generation
@app.post("/enhanced-quizzes")
@limiter.limit("10/minute")
async def enhanced_quizzes(request: QuizRequest, http_request: Request):
    """Generate sophisticated quizzes with advanced AI, multiple question types, and meaningful distractors"""
    try:
        logger.info(f"Enhanced quiz request for {request.max_questions} questions")
        
        # Use the new advanced content generator
        generator = AdvancedContentGenerator(GEMINI_API_KEY)
        result = generator.generate_balanced_content(
            content=request.summary,
            num_questions=request.max_questions,
            num_flashcards=0  # Only quizzes
        )
        
        quizzes = result['questions']
        
        # Update session if provided
        if request.session_id:
            session_manager.update_session_activity(
                session_id=request.session_id,
                activity_type="quiz_generation",
                content={
                    "questions_generated": len(quizzes),
                    "concepts_extracted": len(result.get('concepts', [])),
                    "bloom_distribution": result.get('metadata', {}).get('bloom_distribution', {}),
                    "question_types": list(set(q.get("type", "unknown") for q in quizzes)),
                    "quality_score": len(result.get('concepts', [])) * 15  # Higher weight for quizzes
                }
            )
        
        return {
            "success": True,
            "quizzes": quizzes,
            "count": len(quizzes),
            "session_id": request.session_id,
            "metadata": {
                "concepts": result.get('concepts', []),
                "bloom_distribution": result.get('metadata', {}).get('bloom_distribution', {}),
                "difficulty_distribution": result.get('metadata', {}).get('difficulty_distribution', {}),
                "quality_indicators": {
                    "concept_coverage": len(result.get('concepts', [])),
                    "cognitive_levels": len(set(q.get("bloom_level") for q in quizzes)),
                    "question_types": len(set(q.get("type") for q in quizzes)),
                    "sophisticated_distractors": all(
                        len(q.get("options", [])) >= 4 for q in quizzes if q.get("type") == "multiple_choice"
                    )
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced quiz error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Session Management Endpoints
@app.post("/sessions")
@limiter.limit("20/minute")
async def create_session(request: SessionRequest, http_request: Request):
    """Create a new learning session"""
    try:
        session_type = SessionType(request.session_type.lower())
        
        session = session_manager.create_session(
            user_id=request.user_id,
            topic=request.topic,
            session_type=session_type,
            summary=request.summary,
            duration_hours=request.duration_hours
        )
        
        return {
            "success": True,
            "session": {
                "session_id": session.session_id,
                "topic": session.topic,
                "session_type": session.session_type.value,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "learning_objectives": [
                    {
                        "id": obj.id,
                        "description": obj.description,
                        "bloom_level": obj.bloom_level,
                        "completed": obj.completed
                    }
                    for obj in session.learning_objectives
                ]
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid session type: {request.session_type}")
    except Exception as e:
        logger.error(f"Session creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "session": session_manager.get_session_summary(session_id)
    }

@app.get("/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: str, 
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get sessions for a user"""
    try:
        session_status = SessionStatus(status) if status else None
        sessions = session_manager.get_user_sessions(user_id, session_status, limit)
        
        return {
            "success": True,
            "sessions": [
                {
                    "session_id": s.session_id,
                    "topic": s.topic,
                    "session_type": s.session_type.value,
                    "status": s.status.value,
                    "completion_percentage": s.completion_percentage,
                    "total_time_spent": s.total_time_spent,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat()
                }
                for s in sessions
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    except Exception as e:
        logger.error(f"Get user sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/complete")
async def complete_session(session_id: str):
    """Mark a session as completed"""
    success = session_manager.complete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "message": "Session completed successfully",
        "session_summary": session_manager.get_session_summary(session_id)
    }

# Quiz Interaction Endpoints
@app.post("/quiz-submission")
async def submit_quiz_answer(submission: QuizSubmission):
    """Submit a quiz answer and get feedback"""
    try:
        # Calculate score (simplified - in reality you'd validate against correct answer)
        score = 1.0 if submission.user_answer else 0.0  # Simplified scoring
        
        # Update session activity
        success = session_manager.update_session_activity(
            session_id=submission.session_id,
            activity_type="quiz",
            content={
                "question_id": submission.question_id,
                "user_answer": submission.user_answer
            },
            score=score,
            time_spent=submission.time_spent
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate feedback based on score
        feedback = "Excellent work! You got it right." if score > 0.5 else "Good attempt! Let's review this concept."
        
        return {
            "success": True,
            "score": score,
            "feedback": feedback,
            "correct": score > 0.5
        }
        
    except Exception as e:
        logger.error(f"Quiz submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Flashcard Interaction Endpoints
@app.post("/flashcard-review")
async def review_flashcard(review: FlashcardReview):
    """Record flashcard review and update mastery"""
    try:
        # Update session activity
        success = session_manager.update_session_activity(
            session_id=review.session_id,
            activity_type="flashcard",
            content={
                "card_id": review.card_id,
                "difficulty_rating": review.difficulty_rating
            },
            score=review.confidence_score,
            time_spent=review.time_spent
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Provide adaptive feedback
        if review.confidence_score >= 0.8:
            feedback = "Great mastery! You've got this concept down."
            recommendation = "Try more challenging questions on this topic."
        elif review.confidence_score >= 0.6:
            feedback = "Good understanding! A bit more practice will help."
            recommendation = "Review this concept once more, then move on."
        else:
            feedback = "This is a challenging concept. Let's break it down further."
            recommendation = "Consider reviewing the source material or asking for clarification."
        
        return {
            "success": True,
            "feedback": feedback,
            "recommendation": recommendation,
            "mastery_level": "high" if review.confidence_score >= 0.8 else "medium" if review.confidence_score >= 0.6 else "low"
        }
        
    except Exception as e:
        logger.error(f"Flashcard review error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation Management
@app.delete("/conversations/{user_id}")
async def clear_conversation(user_id: str, topic: Optional[str] = None):
    """Clear conversation history for a fresh start"""
    try:
        clear_conversation_context(user_id, topic)
        return {
            "success": True,
            "message": "Conversation history cleared"
        }
    except Exception as e:
        logger.error(f"Clear conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{user_id}/summary")
async def get_conversation_summary_endpoint(user_id: str, topic: Optional[str] = None):
    """Get conversation summary"""
    try:
        summary = get_conversation_summary(user_id, topic)
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Get conversation summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Progress Tracking
@app.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: str, days: int = Query(30, ge=1, le=365)):
    """Get user learning analytics"""
    try:
        sessions = session_manager.get_user_sessions(user_id, limit=100)
        
        # Calculate analytics
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == SessionStatus.COMPLETED])
        total_time = sum(s.total_time_spent for s in sessions)
        avg_engagement = sum(s.engagement_score for s in sessions) / len(sessions) if sessions else 0
        
        # Topic breakdown
        topic_stats = {}
        for session in sessions:
            topic = session.topic
            if topic not in topic_stats:
                topic_stats[topic] = {"sessions": 0, "time_spent": 0, "avg_score": 0}
            topic_stats[topic]["sessions"] += 1
            topic_stats[topic]["time_spent"] += session.total_time_spent
            if session.quiz_scores:
                topic_stats[topic]["avg_score"] = sum(session.quiz_scores) / len(session.quiz_scores)
        
        return {
            "success": True,
            "analytics": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
                "total_time_minutes": total_time // 60,
                "average_engagement_score": round(avg_engagement, 2),
                "topic_breakdown": topic_stats,
                "learning_streak": 0,  # TODO: Implement streak calculation
                "favorite_activity": "chat"  # TODO: Calculate from session data
            }
        }
        
    except Exception as e:
        logger.error(f"User analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Legacy endpoints for backward compatibility
@app.post("/chat")
@limiter.limit("10/minute")
async def legacy_chat(message: dict, request: Request):
    """Legacy chat endpoint for backward compatibility"""
    enhanced_request = EnhancedChatMessage(message=message.get("message", ""))
    return await enhanced_chat(enhanced_request, request)

@app.post("/generate-flashcards")
async def legacy_flashcards(request: dict):
    """Legacy flashcards endpoint"""
    enhanced_request = FlashcardRequest(summary=request.get("summary", ""))
    result = await enhanced_flashcards(enhanced_request, None)
    return {"flashcards": [{"question": card["question"], "answer": card["answer"]} for card in result["flashcards"]]}

@app.post("/generate-quizzes")
async def legacy_quizzes(request: dict):
    """Legacy quiz endpoint"""
    enhanced_request = QuizRequest(summary=request.get("summary", ""))
    result = await enhanced_quizzes(enhanced_request, None)
    return {"quizzes": result["quizzes"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 