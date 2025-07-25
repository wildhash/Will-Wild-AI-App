"""
Conversation context and memory service for Crisis Support & Mental Health Agent.

This module provides conversation memory management, context tracking,
and session persistence to maintain continuity in therapeutic interactions.
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

from config import get_settings, logger

settings = get_settings()


@dataclass
class ConversationTurn:
    """Data class for individual conversation turns."""
    timestamp: str
    user_message: str
    agent_response: str
    mood_analysis: Dict[str, Any]
    safety_level: str
    crisis_detected: bool
    resources_provided: List[str]
    turn_id: str


@dataclass
class SessionSummary:
    """Data class for session summaries."""
    session_id: str
    start_time: str
    last_activity: str
    total_turns: int
    primary_concerns: List[str]
    mood_progression: List[str]
    safety_incidents: int
    resources_accessed: List[str]
    therapeutic_techniques_used: List[str]
    session_outcome: str


class MemoryService:
    """
    Conversation memory and context management service.
    
    Manages conversation history, session persistence, context tracking,
    and privacy-compliant memory operations for therapeutic interactions.
    """
    
    def __init__(self):
        """Initialize memory service with session storage."""
        # In-memory storage (TODO: Replace with persistent storage)
        self.sessions: Dict[str, List[ConversationTurn]] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
        self.session_summaries: Dict[str, SessionSummary] = {}
        
        # Configuration
        self.max_session_length = settings.max_conversation_length
        self.session_timeout = settings.session_timeout_minutes
        
        # Privacy settings
        self.anonymize_storage = settings.anonymize_logs
        
        logger.info("MemoryService initialized")
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            New session ID
            
        TODO: Implement user-based session management
        TODO: Add session encryption for privacy
        """
        try:
            # Generate session ID
            timestamp = datetime.now().isoformat()
            session_data = f"{timestamp}_{user_id or 'anonymous'}"
            session_id = hashlib.md5(session_data.encode()).hexdigest()[:12]
            
            # Initialize session
            self.sessions[session_id] = []
            self.session_metadata[session_id] = {
                "created_at": timestamp,
                "last_activity": timestamp,
                "user_id": user_id,
                "total_turns": 0,
                "status": "active",
                "privacy_level": "standard"
            }
            
            logger.info(f"Created new session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def store_interaction(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        mood_analysis: Dict[str, Any] = None,
        safety_level: str = "safe",
        crisis_detected: bool = False,
        resources_provided: List[str] = None
    ) -> bool:
        """
        Store a conversation interaction in memory.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            agent_response: Agent's response
            mood_analysis: Mood analysis results
            safety_level: Safety assessment level
            crisis_detected: Whether crisis was detected
            resources_provided: List of resources provided
            
        Returns:
            Success status
            
        TODO: Implement data encryption for sensitive conversations
        TODO: Add automatic conversation summarization
        """
        try:
            # Validate session
            if session_id not in self.sessions:
                logger.warning(f"Session {session_id} not found, creating new session")
                self.sessions[session_id] = []
                self.session_metadata[session_id] = {
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "user_id": None,
                    "total_turns": 0,
                    "status": "active",
                    "privacy_level": "standard"
                }
            
            # Create conversation turn
            turn_id = f"{session_id}_turn_{len(self.sessions[session_id]) + 1}"
            
            # Apply privacy protection if enabled
            stored_user_message = self._apply_privacy_protection(user_message)
            stored_agent_response = self._apply_privacy_protection(agent_response)
            
            conversation_turn = ConversationTurn(
                timestamp=datetime.now().isoformat(),
                user_message=stored_user_message,
                agent_response=stored_agent_response,
                mood_analysis=mood_analysis or {},
                safety_level=safety_level,
                crisis_detected=crisis_detected,
                resources_provided=resources_provided or [],
                turn_id=turn_id
            )
            
            # Store the turn
            self.sessions[session_id].append(conversation_turn)
            
            # Update session metadata
            self.session_metadata[session_id]["last_activity"] = datetime.now().isoformat()
            self.session_metadata[session_id]["total_turns"] += 1
            
            # Enforce session length limits
            if len(self.sessions[session_id]) > self.max_session_length:
                # Remove oldest turns but keep session summary
                self._summarize_old_turns(session_id)
            
            # Log crisis incidents
            if crisis_detected:
                self._log_crisis_incident(session_id, conversation_turn)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return False
    
    def get_session_history(
        self,
        session_id: str,
        limit: int = None,
        include_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of turns to return
            include_analysis: Whether to include mood/safety analysis
            
        Returns:
            Dictionary with session history
            
        TODO: Add filtering options (by date, safety level, etc.)
        TODO: Implement conversation search functionality
        """
        try:
            if session_id not in self.sessions:
                return {"error": f"Session {session_id} not found"}
            
            turns = self.sessions[session_id]
            metadata = self.session_metadata[session_id]
            
            # Apply limit if specified
            if limit:
                turns = turns[-limit:]
            
            # Format conversation history
            history = []
            for turn in turns:
                turn_data = {
                    "timestamp": turn.timestamp,
                    "user_message": turn.user_message,
                    "agent_response": turn.agent_response,
                    "turn_id": turn.turn_id
                }
                
                if include_analysis:
                    turn_data.update({
                        "mood_analysis": turn.mood_analysis,
                        "safety_level": turn.safety_level,
                        "crisis_detected": turn.crisis_detected,
                        "resources_provided": turn.resources_provided
                    })
                
                history.append(turn_data)
            
            return {
                "session_id": session_id,
                "metadata": metadata,
                "conversation_history": history,
                "total_turns": len(self.sessions[session_id]),
                "returned_turns": len(history)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving session history: {str(e)}")
            return {"error": "Failed to retrieve session history"}
    
    def get_session_context(self, session_id: str, context_window: int = 5) -> Dict[str, Any]:
        """
        Get recent conversation context for session.
        
        Args:
            session_id: Session identifier
            context_window: Number of recent turns to include
            
        Returns:
            Dictionary with session context
            
        TODO: Implement intelligent context selection based on relevance
        """
        try:
            if session_id not in self.sessions:
                return {"error": f"Session {session_id} not found"}
            
            recent_turns = self.sessions[session_id][-context_window:]
            
            # Extract context information
            context = {
                "session_id": session_id,
                "recent_emotions": [],
                "safety_concerns": [],
                "recurring_themes": [],
                "therapeutic_progress": "",
                "last_resources_provided": []
            }
            
            for turn in recent_turns:
                # Collect emotions
                if turn.mood_analysis and "primary_emotion" in turn.mood_analysis:
                    context["recent_emotions"].append(turn.mood_analysis["primary_emotion"])
                
                # Collect safety concerns
                if turn.safety_level in ["high", "critical"] or turn.crisis_detected:
                    context["safety_concerns"].append({
                        "timestamp": turn.timestamp,
                        "level": turn.safety_level,
                        "crisis": turn.crisis_detected
                    })
                
                # Collect recent resources
                context["last_resources_provided"].extend(turn.resources_provided)
            
            # Identify recurring themes
            context["recurring_themes"] = self._identify_recurring_themes(recent_turns)
            
            # Assess therapeutic progress
            context["therapeutic_progress"] = self._assess_therapeutic_progress(session_id)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting session context: {str(e)}")
            return {"error": "Failed to retrieve session context"}
    
    def _apply_privacy_protection(self, text: str) -> str:
        """
        Apply privacy protection to stored text.
        
        Args:
            text: Original text
            
        Returns:
            Privacy-protected text
            
        TODO: Implement more sophisticated privacy protection
        TODO: Add PII detection and redaction
        """
        if not self.anonymize_storage:
            return text
        
        # Basic privacy protection (placeholder)
        # TODO: Implement proper PII detection and anonymization
        
        # For now, just truncate very long messages
        if len(text) > 500:
            return text[:500] + "... [truncated for privacy]"
        
        return text
    
    def _summarize_old_turns(self, session_id: str):
        """
        Summarize and remove old conversation turns.
        
        Args:
            session_id: Session identifier
            
        TODO: Implement intelligent conversation summarization
        """
        turns = self.sessions[session_id]
        
        if len(turns) <= self.max_session_length:
            return
        
        # Keep the most recent turns
        recent_turns = turns[-self.max_session_length:]
        
        # Summarize the older turns
        old_turns = turns[:-self.max_session_length]
        summary = self._create_turn_summary(old_turns)
        
        # Store summary in metadata
        if "conversation_summaries" not in self.session_metadata[session_id]:
            self.session_metadata[session_id]["conversation_summaries"] = []
        
        self.session_metadata[session_id]["conversation_summaries"].append(summary)
        
        # Update sessions with only recent turns
        self.sessions[session_id] = recent_turns
        
        logger.info(f"Summarized {len(old_turns)} old turns for session {session_id}")
    
    def _create_turn_summary(self, turns: List[ConversationTurn]) -> Dict[str, Any]:
        """
        Create a summary of conversation turns.
        
        Args:
            turns: List of conversation turns to summarize
            
        Returns:
            Dictionary with turn summary
            
        TODO: Implement AI-powered conversation summarization
        """
        if not turns:
            return {}
        
        # Basic statistical summary
        emotions = []
        safety_levels = []
        crisis_count = 0
        resources = []
        
        for turn in turns:
            if turn.mood_analysis and "primary_emotion" in turn.mood_analysis:
                emotions.append(turn.mood_analysis["primary_emotion"])
            
            safety_levels.append(turn.safety_level)
            
            if turn.crisis_detected:
                crisis_count += 1
            
            resources.extend(turn.resources_provided)
        
        return {
            "period": f"{turns[0].timestamp} to {turns[-1].timestamp}",
            "turn_count": len(turns),
            "primary_emotions": list(set(emotions)),
            "safety_incidents": crisis_count,
            "resources_provided": list(set(resources)),
            "avg_safety_level": max(set(safety_levels), key=safety_levels.count) if safety_levels else "safe"
        }
    
    def _log_crisis_incident(self, session_id: str, turn: ConversationTurn):
        """
        Log crisis incident for tracking and review.
        
        Args:
            session_id: Session identifier
            turn: Conversation turn with crisis
            
        TODO: Implement secure crisis incident logging
        TODO: Add automated escalation protocols
        """
        incident = {
            "session_id": session_id,
            "timestamp": turn.timestamp,
            "turn_id": turn.turn_id,
            "safety_level": turn.safety_level,
            "mood_primary": turn.mood_analysis.get("primary_emotion") if turn.mood_analysis else "unknown",
            "resources_provided": turn.resources_provided,
            "message_hash": hashlib.md5(turn.user_message.encode()).hexdigest()[:8] if self.anonymize_storage else None
        }
        
        # Store in metadata
        if "crisis_incidents" not in self.session_metadata[session_id]:
            self.session_metadata[session_id]["crisis_incidents"] = []
        
        self.session_metadata[session_id]["crisis_incidents"].append(incident)
        
        logger.warning(f"Crisis incident logged for session {session_id}: {turn.safety_level}")
    
    def _identify_recurring_themes(self, turns: List[ConversationTurn]) -> List[str]:
        """
        Identify recurring themes in conversation turns.
        
        Args:
            turns: List of conversation turns
            
        Returns:
            List of recurring themes
            
        TODO: Implement NLP-based theme extraction
        """
        if len(turns) < 3:
            return []
        
        # Simple keyword-based theme detection (placeholder)
        themes = []
        
        # Check for emotional patterns
        emotions = [turn.mood_analysis.get("primary_emotion", "") for turn in turns if turn.mood_analysis]
        emotion_counts = {}
        for emotion in emotions:
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # If an emotion appears in more than half the turns, it's a theme
        for emotion, count in emotion_counts.items():
            if count > len(turns) // 2:
                themes.append(f"persistent_{emotion}")
        
        return themes
    
    def _assess_therapeutic_progress(self, session_id: str) -> str:
        """
        Assess therapeutic progress for the session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Progress assessment string
            
        TODO: Implement comprehensive progress assessment
        """
        if session_id not in self.sessions or len(self.sessions[session_id]) < 3:
            return "insufficient_data"
        
        turns = self.sessions[session_id]
        
        # Simple progress assessment based on safety levels
        recent_safety = [turn.safety_level for turn in turns[-3:]]
        early_safety = [turn.safety_level for turn in turns[:3]]
        
        safety_scores = {"safe": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        
        recent_avg = sum(safety_scores[level] for level in recent_safety) / len(recent_safety)
        early_avg = sum(safety_scores[level] for level in early_safety) / len(early_safety)
        
        if recent_avg < early_avg - 0.5:
            return "improving"
        elif recent_avg > early_avg + 0.5:
            return "concerning"
        else:
            return "stable"
    
    def cleanup_expired_sessions(self):
        """
        Clean up expired sessions based on timeout settings.
        
        TODO: Implement proper session lifecycle management
        """
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, metadata in self.session_metadata.items():
            last_activity = datetime.fromisoformat(metadata["last_activity"])
            if current_time - last_activity > timedelta(minutes=self.session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            # Create final summary before deletion
            if session_id in self.sessions and self.sessions[session_id]:
                self._create_session_summary(session_id)
            
            # Remove from active sessions
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.session_metadata:
                del self.session_metadata[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _create_session_summary(self, session_id: str):
        """
        Create a comprehensive session summary.
        
        Args:
            session_id: Session identifier
            
        TODO: Implement detailed session outcome analysis
        """
        if session_id not in self.sessions:
            return
        
        turns = self.sessions[session_id]
        metadata = self.session_metadata[session_id]
        
        if not turns:
            return
        
        # Analyze session data
        emotions = []
        safety_incidents = 0
        resources = []
        techniques = []
        
        for turn in turns:
            if turn.mood_analysis and "primary_emotion" in turn.mood_analysis:
                emotions.append(turn.mood_analysis["primary_emotion"])
            
            if turn.crisis_detected:
                safety_incidents += 1
            
            resources.extend(turn.resources_provided)
            
            # TODO: Track therapeutic techniques used
        
        # Create summary
        summary = SessionSummary(
            session_id=session_id,
            start_time=metadata["created_at"],
            last_activity=metadata["last_activity"],
            total_turns=len(turns),
            primary_concerns=list(set(emotions)),
            mood_progression=emotions[-5:] if len(emotions) >= 5 else emotions,
            safety_incidents=safety_incidents,
            resources_accessed=list(set(resources)),
            therapeutic_techniques_used=techniques,
            session_outcome=self._determine_session_outcome(turns)
        )
        
        self.session_summaries[session_id] = summary
        logger.info(f"Created summary for session {session_id}")
    
    def _determine_session_outcome(self, turns: List[ConversationTurn]) -> str:
        """
        Determine the overall outcome of the session.
        
        Args:
            turns: List of conversation turns
            
        Returns:
            Session outcome description
            
        TODO: Implement sophisticated outcome assessment
        """
        if not turns:
            return "no_interaction"
        
        last_turn = turns[-1]
        
        if last_turn.crisis_detected:
            return "crisis_intervention"
        elif last_turn.safety_level in ["high", "critical"]:
            return "safety_concern"
        elif len(turns) >= 10:
            return "extended_support"
        else:
            return "brief_support"
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get memory service statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        total_turns = sum(len(turns) for turns in self.sessions.values())
        total_sessions = len(self.sessions)
        active_sessions = len([
            s for s in self.session_metadata.values()
            if s.get("status") == "active"
        ])
        
        # Crisis statistics
        total_crises = 0
        for turns in self.sessions.values():
            total_crises += sum(1 for turn in turns if turn.crisis_detected)
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_conversation_turns": total_turns,
            "total_crisis_incidents": total_crises,
            "session_summaries": len(self.session_summaries),
            "average_session_length": total_turns / max(total_sessions, 1),
            "memory_usage": "in_memory"  # TODO: Calculate actual memory usage
        }
    
    def export_session_data(
        self,
        session_id: str,
        anonymize: bool = True
    ) -> Dict[str, Any]:
        """
        Export session data for analysis or backup.
        
        Args:
            session_id: Session to export
            anonymize: Whether to anonymize the export
            
        Returns:
            Exported session data
            
        TODO: Implement secure data export with encryption
        """
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        turns = self.sessions[session_id]
        metadata = self.session_metadata[session_id]
        
        export_data = {
            "session_id": session_id if not anonymize else hashlib.md5(session_id.encode()).hexdigest()[:8],
            "metadata": metadata.copy(),
            "turns": []
        }
        
        if anonymize:
            # Remove identifying information
            export_data["metadata"].pop("user_id", None)
        
        for turn in turns:
            turn_data = asdict(turn)
            if anonymize:
                # Hash the actual messages
                turn_data["user_message"] = hashlib.md5(turn_data["user_message"].encode()).hexdigest()[:16]
                turn_data["agent_response"] = hashlib.md5(turn_data["agent_response"].encode()).hexdigest()[:16]
            
            export_data["turns"].append(turn_data)
        
        return export_data