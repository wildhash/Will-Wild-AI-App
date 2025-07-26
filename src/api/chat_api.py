import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.conversation import ChatRequest, ChatResponse, SessionCreateRequest, SessionResponse
from agents.therapy_agent import TherapyAgent
from services.memory_service import MemoryService
from services.safety_service import SafetyService
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Create router for chat endpoints
router = APIRouter(prefix="/api", tags=["chat"])

# Initialize services (in production, these would be injected via dependency injection)
memory_service = MemoryService()
safety_service = SafetyService()
gemini_service = GeminiService()
therapy_agent = TherapyAgent(memory_service, safety_service, gemini_service)


def get_therapy_agent() -> TherapyAgent:
    """Dependency to get the therapy agent instance."""
    return therapy_agent


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest
) -> SessionResponse:
    """
    Create a new conversation session for a user.
    
    Args:
        request: Request containing user_id
        
    Returns:
        SessionResponse with new session details
    """
    try:
        # Validate input
        if not request.user_id or not request.user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Create new session
        session_id = memory_service.create_session(request.user_id)
        context = memory_service.get_session_context(session_id)
        
        if not context:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        logger.info(f"Created new session {session_id} for user: {request.user_id}")
        
        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            created_at=context.session_start_time.isoformat(),
            message_count=len(context.messages),
            risk_level=context.risk_level,
            messages=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """
    Retrieve session information and history.
    
    Args:
        session_id: The session ID to retrieve
        
    Returns:
        SessionResponse with session details and message history
    """
    try:
        if not session_id or not session_id.strip():
            raise HTTPException(status_code=400, detail="session_id is required")
        
        context = memory_service.get_session_context(session_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get message history
        messages = memory_service.fetch_chat_history(session_id)
        
        logger.info(f"Retrieved session {session_id} with {len(messages)} messages")
        
        return SessionResponse(
            session_id=session_id,
            user_id=context.user_id,
            created_at=context.session_start_time.isoformat(),
            message_count=len(context.messages),
            risk_level=context.risk_level,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Clear/delete a specific session.
    
    Args:
        session_id: The session ID to clear
        
    Returns:
        Success message
    """
    try:
        if not session_id or not session_id.strip():
            raise HTTPException(status_code=400, detail="session_id is required")
        
        success = memory_service.clear_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Cleared session {session_id}")
        
        return {"message": "Session cleared successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear session")
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    agent: TherapyAgent = Depends(get_therapy_agent)
) -> ChatResponse:
    """
    Main chat endpoint for the Crisis Support AI Agent.
    
    Accepts a user message and returns an AI-generated response with
    appropriate safety assessment and crisis detection.
    
    Supports both session-based and user-based conversations.
    """
    try:
        # Validate input
        if not request.user_id or not request.user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")
        
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="message is required")
        
        # Log the incoming request (without sensitive data)
        logger.info(f"Processing chat request for user: {request.user_id[:8]}...")
        
        # Process the conversation
        if request.session_id:
            # Session-based conversation
            result = agent.process_session_conversation(
                request.session_id, request.user_id, request.message
            )
        else:
            # Backward compatibility: user-based conversation
            result = agent.process_conversation(request.user_id, request.message)
        
        # Handle processing errors
        if "error" in result:
            logger.error(f"Agent processing error: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your message"
            )
        
        # Create response
        response = ChatResponse(
            response=result["response"],
            risk_level=result["risk_level"],
            session_id=result.get("session_id")
        )
        
        logger.info(f"Successfully processed chat for user: {request.user_id[:8]}..., "
                   f"session: {result.get('session_id', 'N/A')}, "
                   f"risk_level: {response.risk_level}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )


@router.get("/resources")
async def get_resources(session_id: str = None):
    """
    Get mental health resources and recommendations.
    
    Args:
        session_id: Optional session ID for personalized resources
        
    Returns:
        Dictionary with mental health resources
    """
    try:
        # Base resources for everyone
        resources = {
            "emergency": {
                "title": "Emergency Resources",
                "items": [
                    {
                        "name": "National Suicide Prevention Lifeline",
                        "contact": "988",
                        "available": "24/7",
                        "description": "Free and confidential emotional support"
                    },
                    {
                        "name": "Crisis Text Line",
                        "contact": "Text HOME to 741741",
                        "available": "24/7",
                        "description": "Free, 24/7 support for those in crisis"
                    },
                    {
                        "name": "Emergency Services",
                        "contact": "911",
                        "available": "24/7",
                        "description": "For immediate medical or safety emergencies"
                    }
                ]
            },
            "support": {
                "title": "Support Resources",
                "items": [
                    {
                        "name": "NAMI Helpline",
                        "contact": "1-800-950-NAMI (6264)",
                        "available": "Mon-Fri 10am-10pm ET",
                        "description": "Mental health information and support"
                    },
                    {
                        "name": "SAMHSA National Helpline",
                        "contact": "1-800-662-4357",
                        "available": "24/7",
                        "description": "Treatment referral and information service"
                    }
                ]
            }
        }
        
        # Add personalized resources if session provided
        if session_id:
            context = memory_service.get_session_context(session_id)
            if context:
                # Add session-specific recommendations based on risk level
                if context.risk_level in ["high", "critical"]:
                    resources["personalized"] = {
                        "title": "Immediate Support Recommended",
                        "message": "Based on our conversation, immediate professional support is recommended.",
                        "priority": "high"
                    }
                elif context.risk_level == "medium":
                    resources["personalized"] = {
                        "title": "Additional Support Available",
                        "message": "Consider reaching out to these resources for additional support.",
                        "priority": "medium"
                    }
        
        logger.info(f"Provided resources for session: {session_id or 'anonymous'}")
        return resources
        
    except Exception as e:
        logger.error(f"Error getting resources: {str(e)}")
        # Return basic resources even if there's an error
        return {
            "emergency": {
                "title": "Emergency Resources",
                "items": [
                    {
                        "name": "National Suicide Prevention Lifeline",
                        "contact": "988",
                        "available": "24/7"
                    }
                ]
            }
        }
async def health_check():
    """Health check endpoint to verify the API is running."""
    try:
        # Check if services are working
        active_conversations = memory_service.get_active_conversations_count()
        
        return {
            "status": "healthy",
            "service": "Crisis Support AI Agent",
            "active_conversations": active_conversations,
            "gemini_configured": gemini_service.is_configured
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Service unavailable"
            }
        )


@router.get("/conversation/{user_id}/summary")
async def get_conversation_summary(
    user_id: str,
    agent: TherapyAgent = Depends(get_therapy_agent)
):
    """
    Get a summary of the conversation for a specific user.
    
    Args:
        user_id: The user ID to get conversation summary for
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")
        
        summary = agent.get_conversation_summary(user_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get conversation summary")


@router.post("/conversation/{user_id}/end")
async def end_conversation(
    user_id: str,
    agent: TherapyAgent = Depends(get_therapy_agent)
):
    """
    End a conversation session for a user.
    
    Args:
        user_id: The user ID to end conversation for
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")
        
        success = agent.end_conversation(user_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to end conversation")
        
        return {"message": "Conversation ended successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end conversation")