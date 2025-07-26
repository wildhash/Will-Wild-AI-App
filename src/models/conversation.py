from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MoodData(BaseModel):
    """Represents mood analysis data for a message."""
    mood: str  # "happy", "sad", "anxious", "angry", "neutral"
    confidence: float = Field(ge=0.0, le=1.0)  # Confidence score 0.0-1.0
    keywords: List[str] = []  # Keywords that influenced the mood detection
    timestamp: datetime = Field(default_factory=datetime.now)


class Message(BaseModel):
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    mood_data: Optional[MoodData] = None  # Mood analysis for user messages


class ConversationContext(BaseModel):
    """Represents the context of a conversation with a user."""
    user_id: str
    messages: List[Message] = []
    session_start_time: datetime = Field(default_factory=datetime.now)
    risk_level: str = "low"  # low, medium, high, critical
    
    def add_message(self, role: str, content: str, mood_data: Optional[MoodData] = None):
        """Add a message to the conversation."""
        message = Message(role=role, content=content)
        if mood_data:
            message.mood_data = mood_data
        self.messages.append(message)
    
    def get_mood_timeline(self) -> List[MoodData]:
        """Get mood timeline from user messages."""
        return [msg.mood_data for msg in self.messages 
                if msg.role == "user" and msg.mood_data is not None]


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    risk_level: str = "low"
    session_id: Optional[str] = None


class MoodTimelineResponse(BaseModel):
    """Response model for mood timeline endpoint."""
    user_id: str
    session_start_time: datetime
    mood_timeline: List[MoodData]
    session_mood_summary: dict  # Aggregated mood trends for the session


class MoodSummary(BaseModel):
    """Summary of mood trends for a session."""
    dominant_mood: str
    mood_distribution: dict  # {"happy": 0.3, "sad": 0.2, etc.}
    mood_changes: int  # Number of mood transitions
    average_confidence: float