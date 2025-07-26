import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.conversation import ChatRequest, ChatResponse
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


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    agent: TherapyAgent = Depends(get_therapy_agent)
) -> ChatResponse:
    """
    Main chat endpoint for the Crisis Support AI Agent.
    
    Accepts a user message and returns an AI-generated response with
    appropriate safety assessment and crisis detection.
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


@router.get("/health")
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