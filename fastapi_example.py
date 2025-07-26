"""
FastAPI Integration Example for Crisis Support & Mental Health Agent

This module demonstrates how to integrate the TherapyAgent into a FastAPI
web service for production deployment.

Usage:
    uvicorn fastapi_example:app --reload

Note: Set GEMINI_API_KEY in environment before running
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import get_config
from src.services.gemini_service import GeminiService
from src.services.safety_service import SafetyService
from src.services.memory_service import MemoryService
from src.agents.therapy_agent import TherapyAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crisis Support & Mental Health Agent",
    description="AI-powered mental health support with crisis intervention capabilities",
    version="0.1.0"
)

# Global services - in production, these would be dependency injected
config = get_config()
therapy_agent: Optional[TherapyAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global therapy_agent
    
    # Validate configuration
    validation = config.validate()
    if not validation["valid"]:
        logger.error("Configuration validation failed", errors=validation["errors"])
        raise RuntimeError(f"Invalid configuration: {validation['errors']}")
    
    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"Configuration warning: {warning}")
    
    # Initialize services
    try:
        gemini_service = GeminiService(
            api_key=config.gemini.api_key,
            model_name=config.gemini.model_name
        )
        safety_service = SafetyService()
        memory_service = MemoryService()
        
        therapy_agent = TherapyAgent(
            gemini_service=gemini_service,
            safety_service=safety_service,
            memory_service=memory_service
        )
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise RuntimeError(f"Service initialization failed: {str(e)}")


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    therapy_phase: str
    risk_assessment: Dict[str, Any]
    interventions: list
    safety_status: str
    recommendations: list
    resources: Dict[str, Any]
    status: str


class SessionSummaryResponse(BaseModel):
    session_id: str
    user_id: str
    duration_minutes: int
    therapy_phase: str
    total_interactions: int
    average_risk_score: float
    interventions_applied: Dict[str, Any]
    status: str


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Crisis Support & Mental Health Agent API",
        "status": "active",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "therapy_agent": therapy_agent is not None,
            "config_valid": config.validate()["valid"]
        },
        "config": config.to_dict()
    }


@app.get("/crisis-resources")
async def get_crisis_resources():
    """Get crisis intervention resources"""
    if not therapy_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    resources = await therapy_agent.safety_service.get_crisis_resources()
    return {
        "resources": resources,
        "emergency_note": "If you are in immediate danger, call 911 or go to your nearest emergency room"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat endpoint for interacting with the therapy agent"""
    if not therapy_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Process message through therapy agent
        response = await therapy_agent.process_user_message(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Schedule background cleanup if needed
        background_tasks.add_task(cleanup_expired_sessions)
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        
        # Return emergency response
        emergency_resources = await therapy_agent.safety_service.get_crisis_resources()
        
        return ChatResponse(
            message="I'm experiencing technical difficulties. If this is an emergency, please contact 988 (Suicide & Crisis Lifeline) or 911 immediately.",
            session_id=request.session_id or "error_session",
            therapy_phase="error",
            risk_assessment={"level": "unknown", "score": 0.5, "indicators": []},
            interventions=[],
            safety_status="error",
            recommendations=["Contact crisis services if in immediate danger"],
            resources=emergency_resources,
            status="error"
        )


@app.get("/session/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(session_id: str):
    """Get comprehensive session summary"""
    if not therapy_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        summary = await therapy_agent.get_session_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session summary")


@app.post("/session/{session_id}/end")
async def end_session(session_id: str, summary: Optional[str] = None):
    """End a therapy session"""
    if not therapy_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await therapy_agent.end_session(session_id, summary)
        return result
        
    except Exception as e:
        logger.error(f"Session ending failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")


@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile and therapeutic progress"""
    if not therapy_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get user profile
        profile = await therapy_agent.memory_service.get_user_profile(user_id)
        
        # Get therapeutic progress
        progress = await therapy_agent.memory_service.get_therapeutic_progress(user_id)
        
        return {
            "user_id": user_id,
            "profile": profile.__dict__ if profile else None,
            "therapeutic_progress": progress
        }
        
    except Exception as e:
        logger.error(f"User profile retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")


@app.post("/user/{user_id}/profile")
async def update_user_profile(user_id: str, profile_data: Dict[str, Any]):
    """Update user profile"""
    if not therapy_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        updated_profile = await therapy_agent.memory_service.update_user_profile(
            user_id, profile_data
        )
        
        return {
            "status": "updated",
            "profile": updated_profile.__dict__
        }
        
    except Exception as e:
        logger.error(f"User profile update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")


# Background tasks
async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    if therapy_agent:
        try:
            cleaned = await therapy_agent.gemini_service.cleanup_expired_sessions()
            memory_cleaned = await therapy_agent.memory_service.cleanup_old_memories()
            
            if cleaned > 0 or memory_cleaned > 0:
                logger.info(f"Cleaned up {cleaned} sessions and {memory_cleaned} old memories")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")


# Error handlers
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors with crisis resources"""
    logger.error(f"Internal server error: {str(exc)}")
    
    return {
        "error": "Internal server error",
        "message": "If this is a mental health emergency, please contact 988 (Suicide & Crisis Lifeline) or 911",
        "crisis_resources": config.get_crisis_resources()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key before running the server")
        sys.exit(1)
    
    # Run the server
    uvicorn.run(
        "fastapi_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )