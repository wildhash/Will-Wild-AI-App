"""
FastAPI application entry point for Crisis Support & Mental Health Agent.

This module sets up the main FastAPI application, configures routes,
middleware, and initializes core services.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from config import get_settings, validate_config, logger
from src.agents.therapy_agent import TherapyAgent
from src.services.safety_service import SafetyService
from src.services.memory_service import MemoryService

# Initialize settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered crisis support and mental health assistance agent using Google Gemini",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response: str
    session_id: str
    safety_level: str
    resources: Optional[list] = None
    escalation_triggered: bool = False


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    services: Dict[str, str]


# Initialize core services
therapy_agent = TherapyAgent()
safety_service = SafetyService()
memory_service = MemoryService()


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting Crisis Support & Mental Health Agent")
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed")
        raise RuntimeError("Invalid configuration")
    
    # Initialize services
    # TODO: Add proper service initialization
    logger.info("Services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Crisis Support & Mental Health Agent")
    # TODO: Add cleanup logic for services


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services={
            "therapy_agent": "active",
            "safety_service": "active",
            "memory_service": "active",
            "gemini_api": "connected"  # TODO: Add actual health checks
        }
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for therapeutic conversations.
    
    Args:
        request: Chat request containing message and session info
        
    Returns:
        ChatResponse: Agent response with safety assessment and resources
        
    TODO: Implement full conversation flow with Gemini integration
    """
    try:
        # Get or create session
        session_id = request.session_id or memory_service.create_session()
        
        # Safety check on input
        safety_assessment = safety_service.assess_message(request.message)
        
        if safety_assessment["crisis_detected"]:
            logger.warning(f"Crisis detected in session {session_id}")
            # TODO: Implement crisis response protocol
            
        # Generate therapeutic response
        response = await therapy_agent.generate_response(
            message=request.message,
            session_id=session_id,
            safety_context=safety_assessment
        )
        
        # Store conversation in memory
        memory_service.store_interaction(
            session_id=session_id,
            user_message=request.message,
            agent_response=response["message"],
            safety_level=safety_assessment["level"]
        )
        
        return ChatResponse(
            response=response["message"],
            session_id=session_id,
            safety_level=safety_assessment["level"],
            resources=response.get("resources"),
            escalation_triggered=safety_assessment["crisis_detected"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.
    
    TODO: Implement with proper privacy controls and data sanitization
    """
    try:
        history = memory_service.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Error retrieving session history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/resources/search")
async def search_resources(location: str, resource_type: str = "crisis"):
    """
    Search for mental health resources by location and type.
    
    TODO: Implement location-based resource matching
    """
    # Placeholder response
    return {
        "location": location,
        "resource_type": resource_type,
        "resources": [
            {
                "name": "988 Suicide & Crisis Lifeline",
                "phone": "988",
                "type": "crisis",
                "available": "24/7"
            }
        ]
    }


@app.get("/safety/patterns")
async def get_crisis_patterns():
    """
    Get current crisis detection patterns (for admin/debugging).
    
    TODO: Add proper authentication and authorization
    """
    patterns = safety_service.get_crisis_patterns()
    return {"patterns": patterns}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )