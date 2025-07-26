import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path for imports
sys.path.append(str(Path(__file__).parent))

from api.chat_api import router as chat_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crisis_support_agent.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Crisis Support AI Agent",
    description="AI-powered crisis support system with safety monitoring and therapeutic assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Crisis Support AI Agent API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Crisis Support AI Agent starting up...")
    logger.info("Services initialized and ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Crisis Support AI Agent shutting down...")
    # TODO: Add cleanup for persistent services when implemented

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Crisis Support AI Agent server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )