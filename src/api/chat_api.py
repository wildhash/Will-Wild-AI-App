import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from models.conversation import ChatRequest, ChatResponse
from agents.therapy_agent import TherapyAgent
from services.memory_service import MemoryService
from services.safety_service import SafetyService
from services.gemini_service import GeminiService
from services.mood_service import MoodService

logger = logging.getLogger(__name__)

# Create router for chat endpoints
router = APIRouter(prefix="/api", tags=["chat"])

# Initialize services (in production, these would be injected via dependency injection)
memory_service = MemoryService()
safety_service = SafetyService()
gemini_service = GeminiService()
mood_service = MoodService()
therapy_agent = TherapyAgent(memory_service, safety_service, gemini_service, mood_service)


def get_therapy_agent() -> TherapyAgent:
    """Dependency to get the therapy agent instance."""
    return therapy_agent


def get_mood_service() -> MoodService:
    """Dependency to get the mood service instance."""
    return mood_service


def get_memory_service() -> MemoryService:
    """Dependency to get the memory service instance."""
    return memory_service


async def cleanup_expired_sessions():
    """Background task to clean up expired sessions periodically."""
    try:
        # Clean up memory service sessions
        memory_cleaned = memory_service.cleanup_expired_sessions(max_age_hours=24)
        
        # Clean up mood service sessions
        mood_cleaned = mood_service.cleanup_old_sessions(max_age_hours=24)
        
        if memory_cleaned > 0 or mood_cleaned > 0:
            logger.info(f"Background cleanup: {memory_cleaned} conversation sessions, {mood_cleaned} mood sessions")
    except Exception as e:
        logger.error(f"Error in background cleanup: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    agent: TherapyAgent = Depends(get_therapy_agent)
) -> ChatResponse:
    """
    Main chat endpoint for the Crisis Support AI Agent with mood tracking.
    
    Accepts a user message and returns an AI-generated response with
    appropriate safety assessment, mood detection, and analytics.
    """
    try:
        # Enhanced input validation
        if not request.user_id or not request.user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")
        
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="message is required and cannot be empty")
        
        if len(request.message) > 5000:  # Reasonable message length limit
            raise HTTPException(status_code=400, detail="message is too long (max 5000 characters)")
        
        # Log the incoming request (privacy-safe logging)
        user_hash = request.user_id[:8] + "..." if len(request.user_id) > 8 else request.user_id
        logger.info(f"Processing chat request for user: {user_hash}")
        
        # Add background cleanup task periodically
        background_tasks.add_task(cleanup_expired_sessions)
        
        # Process the conversation with enhanced error handling
        result = agent.process_conversation(request.user_id, request.message)
        
        # Handle processing errors gracefully
        if "error" in result:
            error_type = result.get("error", "unknown")
            logger.error(f"Agent processing error: {error_type}")
            
            if error_type == "processing_error":
                raise HTTPException(
                    status_code=503,
                    detail="The AI service is temporarily unavailable. Please try again in a moment."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="An error occurred while processing your message"
                )
        
        # Create enhanced response with mood information
        response = ChatResponse(
            response=result["response"],
            risk_level=result["risk_level"],
            session_id=result.get("session_id"),
            mood_detected=result.get("mood_detected"),
            mood_confidence=result.get("mood_confidence"),
            mood_analytics=result.get("mood_analytics")
        )
        
        logger.info(f"Successfully processed chat for user: {user_hash}, "
                   f"risk_level: {response.risk_level}, mood: {response.mood_detected}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )


@router.get("/health")
async def health_check(
    memory_svc: MemoryService = Depends(get_memory_service),
    mood_svc: MoodService = Depends(get_mood_service)
):
    """Health check endpoint to verify the API is running with enhanced service monitoring."""
    try:
        # Check if services are working
        session_stats = memory_svc.get_session_stats()
        active_conversations = session_stats.get("active_sessions", 0)
        
        return {
            "status": "healthy",
            "service": "Crisis Support AI Agent",
            "active_conversations": active_conversations,
            "session_stats": session_stats,
            "gemini_configured": gemini_service.is_configured,
            "services": {
                "memory": "operational",
                "safety": "operational", 
                "mood_tracking": "operational",
                "gemini": "configured" if gemini_service.is_configured else "mock_mode"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "Crisis Support AI Agent",
                "error": "Service components unavailable"
            }
        )


@router.get("/conversation/{user_id}/summary")
async def get_conversation_summary(
    user_id: str,
    agent: TherapyAgent = Depends(get_therapy_agent)
):
    """
    Get a summary of the conversation for a specific user with enhanced privacy.
    
    Args:
        user_id: The user ID to get conversation summary for
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")
        
        summary = agent.get_conversation_summary(user_id)
        
        if "error" in summary:
            if summary["error"] == "summary_unavailable":
                raise HTTPException(status_code=404, detail="Conversation not found or unavailable")
            else:
                raise HTTPException(status_code=500, detail="Unable to generate conversation summary")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation summary")


@router.get("/mood/{user_id}/analytics")
async def get_mood_analytics(
    user_id: str,
    mood_svc: MoodService = Depends(get_mood_service)
):
    """
    Get mood analytics and trends for a specific user.
    
    Args:
        user_id: The user ID to get mood analytics for
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")
        
        analytics = mood_svc.get_mood_analytics(user_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=500, detail="Mood analytics temporarily unavailable")
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mood analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood analytics")


@router.get("/mood/{user_id}/history")
async def get_mood_history(
    user_id: str,
    limit: int = 20,
    mood_svc: MoodService = Depends(get_mood_service)
):
    """
    Get recent mood history for a user (privacy-safe, no raw messages).
    
    Args:
        user_id: The user ID to get mood history for
        limit: Maximum number of entries to return (default 20, max 100)
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")
        
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        
        history = mood_svc.get_session_mood_history(user_id, limit=limit)
        
        return {
            "user_session_hash": mood_svc._hash_session_id(user_id)[:8] + "...",
            "mood_history": history,
            "total_entries": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mood history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood history")


@router.post("/mood/{user_id}/feedback")
async def submit_mood_feedback(
    user_id: str,
    feedback_data: dict,
    mood_svc: MoodService = Depends(get_mood_service)
):
    """
    Submit feedback on mood detection accuracy ("Did we get your mood right?").
    
    Args:
        user_id: The user ID submitting feedback
        feedback_data: Dictionary containing feedback information
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")
        
        # Validate feedback data structure
        required_fields = ["is_correct", "detected_mood"]
        for field in required_fields:
            if field not in feedback_data:
                raise HTTPException(status_code=400, detail=f"'{field}' is required in feedback")
        
        is_correct = feedback_data.get("is_correct")
        detected_mood = feedback_data.get("detected_mood")
        actual_mood = feedback_data.get("actual_mood")  # Optional - what user says their mood really is
        
        if not isinstance(is_correct, bool):
            raise HTTPException(status_code=400, detail="'is_correct' must be a boolean")
        
        # Log feedback for future model improvements (privacy-safe)
        session_hash = mood_svc._hash_session_id(user_id)
        logger.info(f"Mood feedback received - session: {session_hash[:8]}..., "
                   f"detected: {detected_mood}, correct: {is_correct}, actual: {actual_mood}")
        
        # TODO: Store feedback in database for model training
        # TODO: Use feedback to improve mood detection algorithms
        
        return {
            "message": "Thank you for your feedback! This helps us improve mood detection.",
            "feedback_recorded": True,
            "session_hash": session_hash[:8] + "..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing mood feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process mood feedback")


@router.post("/conversation/{user_id}/end")
async def end_conversation(
    user_id: str,
    agent: TherapyAgent = Depends(get_therapy_agent)
):
    """
    End a conversation session for a user with privacy-safe cleanup.
    
    Args:
        user_id: The user ID to end conversation for
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")
        
        success = agent.end_conversation(user_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to end conversation session")
        
        # Privacy-safe response
        user_hash = user_id[:8] + "..." if len(user_id) > 8 else user_id
        
        return {
            "message": "Conversation ended successfully",
            "user_hash": user_hash,
            "status": "session_closed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end conversation")


@router.post("/admin/cleanup")
async def manual_cleanup(
    memory_svc: MemoryService = Depends(get_memory_service),
    mood_svc: MoodService = Depends(get_mood_service)
):
    """
    Manual cleanup endpoint for expired sessions (admin/maintenance use).
    """
    try:
        # Clean up expired sessions
        memory_cleaned = memory_svc.cleanup_expired_sessions(max_age_hours=24)
        mood_cleaned = mood_svc.cleanup_old_sessions(max_age_hours=24)
        
        return {
            "message": "Cleanup completed successfully",
            "conversation_sessions_cleaned": memory_cleaned,
            "mood_sessions_cleaned": mood_cleaned,
            "total_cleaned": memory_cleaned + mood_cleaned
        }
        
    except Exception as e:
        logger.error(f"Error during manual cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Cleanup operation failed")