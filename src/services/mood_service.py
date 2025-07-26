import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


class MoodType(Enum):
    """Different mood categories for tracking."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    HOPEFUL = "hopeful"


@dataclass
class MoodEntry:
    """Represents a single mood detection entry."""
    mood_type: MoodType
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    session_hash: str  # Anonymized session identifier
    detected_keywords: List[str]
    is_negated: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/serialization."""
        return {
            "mood_type": self.mood_type.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "session_hash": self.session_hash,
            "detected_keywords": self.detected_keywords,
            "is_negated": self.is_negated
        }


class MoodService:
    """
    Advanced mood detection and tracking service.
    
    Provides sophisticated mood analysis with negation handling,
    privacy-focused logging, and session-based analytics.
    """
    
    def __init__(self, max_entries_per_session: int = 100):
        self.max_entries_per_session = max_entries_per_session
        
        # Privacy-focused storage: session_hash -> List[MoodEntry]
        self._mood_history: Dict[str, List[MoodEntry]] = {}
        
        # Enhanced mood detection keywords with confidence scores
        self._mood_keywords = {
            MoodType.POSITIVE: {
                "happy": 0.8, "joyful": 0.9, "excited": 0.8, "great": 0.7,
                "amazing": 0.9, "wonderful": 0.8, "fantastic": 0.9, "good": 0.6,
                "cheerful": 0.8, "optimistic": 0.7, "delighted": 0.9, "pleased": 0.7,
                "content": 0.6, "satisfied": 0.6, "upbeat": 0.7, "elated": 0.9
            },
            MoodType.NEGATIVE: {
                "sad": 0.8, "upset": 0.7, "angry": 0.8, "frustrated": 0.7,
                "disappointed": 0.7, "miserable": 0.9, "terrible": 0.8, "awful": 0.8,
                "horrible": 0.8, "devastated": 0.9, "heartbroken": 0.9, "defeated": 0.8
            },
            MoodType.ANXIOUS: {
                "anxious": 0.9, "worried": 0.8, "nervous": 0.8, "stressed": 0.8,
                "panic": 0.9, "overwhelmed": 0.8, "tense": 0.7, "fearful": 0.8,
                "restless": 0.7, "on edge": 0.8, "jittery": 0.7, "uneasy": 0.7
            },
            MoodType.DEPRESSED: {
                "depressed": 0.9, "hopeless": 0.9, "empty": 0.8, "numb": 0.8,
                "worthless": 0.9, "lonely": 0.7, "isolated": 0.7, "down": 0.6,
                "blue": 0.6, "melancholy": 0.7, "despondent": 0.8, "dejected": 0.8
            },
            MoodType.EXCITED: {
                "excited": 0.9, "thrilled": 0.9, "pumped": 0.8, "energetic": 0.8,
                "enthusiastic": 0.8, "eager": 0.7, "animated": 0.7, "vibrant": 0.7
            },
            MoodType.CALM: {
                "calm": 0.8, "peaceful": 0.8, "relaxed": 0.8, "serene": 0.8,
                "tranquil": 0.8, "composed": 0.7, "centered": 0.7, "balanced": 0.7
            },
            MoodType.FRUSTRATED: {
                "frustrated": 0.9, "annoyed": 0.8, "irritated": 0.8, "aggravated": 0.8,
                "exasperated": 0.8, "fed up": 0.8, "bothered": 0.7, "vexed": 0.7
            },
            MoodType.HOPEFUL: {
                "hopeful": 0.9, "optimistic": 0.8, "confident": 0.7, "positive": 0.7,
                "encouraged": 0.8, "motivated": 0.8, "inspired": 0.8, "uplifted": 0.8
            }
        }
        
        # Negation patterns
        self._negation_patterns = [
            r'\bnot\s+',
            r'\bno\s+',
            r'\bnever\s+',
            r'\bwon\'t\s+',
            r'\bcan\'t\s+',
            r'\bdoesn\'t\s+',
            r'\bdon\'t\s+',
            r'\bisn\'t\s+',
            r'\baren\'t\s+',
            r'\bwasn\'t\s+',
            r'\bweren\'t\s+'
        ]
        
        logger.info(f"MoodService initialized with {self.max_entries_per_session} max entries per session")
    
    def detect_mood(self, user_input: str, user_id: str) -> MoodEntry:
        """
        Detect mood from user input with advanced analysis.
        
        Args:
            user_input: The user's message
            user_id: User identifier (will be hashed for privacy)
            
        Returns:
            MoodEntry with detected mood and metadata
        """
        try:
            session_hash = self._hash_session_id(user_id)
            text_lower = user_input.lower()
            
            # Check for negations
            is_negated = self._detect_negation(text_lower)
            
            # Find mood matches
            mood_scores = {}
            detected_keywords = []
            
            for mood_type, keywords in self._mood_keywords.items():
                for keyword, base_confidence in keywords.items():
                    if keyword in text_lower:
                        detected_keywords.append(keyword)
                        # Adjust confidence based on negation
                        confidence = base_confidence
                        if is_negated:
                            confidence *= 0.6  # Reduce confidence for negated statements
                        
                        if mood_type in mood_scores:
                            mood_scores[mood_type] = max(mood_scores[mood_type], confidence)
                        else:
                            mood_scores[mood_type] = confidence
            
            # Determine final mood
            if not mood_scores:
                # No clear mood detected - default to neutral
                mood_type = MoodType.NEUTRAL
                confidence = 0.5
            elif len(mood_scores) == 1:
                # Single mood detected
                mood_type, confidence = next(iter(mood_scores.items()))
                if is_negated and mood_type in [MoodType.POSITIVE, MoodType.EXCITED, MoodType.HOPEFUL]:
                    # Flip positive moods when negated
                    mood_type = MoodType.NEGATIVE
            elif len(mood_scores) > 1:
                # Multiple moods detected - could be mixed
                max_mood = max(mood_scores.items(), key=lambda x: x[1])
                if max_mood[1] > 0.8:
                    mood_type, confidence = max_mood
                else:
                    mood_type = MoodType.MIXED
                    confidence = sum(mood_scores.values()) / len(mood_scores)
            
            # Create mood entry
            mood_entry = MoodEntry(
                mood_type=mood_type,
                confidence=confidence,
                timestamp=datetime.now(),
                session_hash=session_hash,
                detected_keywords=detected_keywords,
                is_negated=is_negated
            )
            
            # Store mood entry with privacy protection
            self._store_mood_entry(session_hash, mood_entry)
            
            logger.info(f"Mood detected: {mood_type.value} (confidence: {confidence:.2f}, negated: {is_negated})")
            return mood_entry
            
        except Exception as e:
            logger.error(f"Error detecting mood: {str(e)}")
            # Return neutral mood on error
            return MoodEntry(
                mood_type=MoodType.NEUTRAL,
                confidence=0.5,
                timestamp=datetime.now(),
                session_hash=self._hash_session_id(user_id),
                detected_keywords=[],
                is_negated=False
            )
    
    def _detect_negation(self, text: str) -> bool:
        """Detect if the text contains negation patterns."""
        # Look for negation patterns followed by mood words within a reasonable distance
        words = text.split()
        for i, word in enumerate(words):
            # Check if current word matches a negation pattern
            for pattern in self._negation_patterns:
                if re.match(pattern.replace(r'\b', '').replace(r'\s+', ''), word.lower()):
                    # Check if there's a mood word within the next 3-4 words
                    for j in range(i + 1, min(i + 5, len(words))):
                        next_word = words[j].lower()
                        # Check if this word is in any mood category
                        for mood_keywords in self._mood_keywords.values():
                            if any(keyword in next_word or next_word in keyword for keyword in mood_keywords.keys()):
                                return True
        return False
    
    def _hash_session_id(self, user_id: str) -> str:
        """Hash user ID for privacy protection."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def _store_mood_entry(self, session_hash: str, mood_entry: MoodEntry) -> None:
        """Store mood entry with session limits."""
        if session_hash not in self._mood_history:
            self._mood_history[session_hash] = []
        
        self._mood_history[session_hash].append(mood_entry)
        
        # Enforce session limits
        if len(self._mood_history[session_hash]) > self.max_entries_per_session:
            # Remove oldest entries
            self._mood_history[session_hash] = self._mood_history[session_hash][-self.max_entries_per_session:]
            logger.info(f"Trimmed mood history for session {session_hash} to {self.max_entries_per_session} entries")
    
    def get_mood_analytics(self, user_id: str) -> Dict:
        """
        Get mood analytics for a user session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with mood analytics and trends
        """
        try:
            session_hash = self._hash_session_id(user_id)
            mood_entries = self._mood_history.get(session_hash, [])
            
            if not mood_entries:
                return {
                    "total_entries": 0,
                    "current_mood": "neutral",
                    "mood_distribution": {},
                    "confidence_average": 0.5,
                    "trend": "stable"
                }
            
            # Calculate mood distribution
            mood_counts = {}
            confidence_sum = 0
            
            for entry in mood_entries:
                mood_type = entry.mood_type.value
                mood_counts[mood_type] = mood_counts.get(mood_type, 0) + 1
                confidence_sum += entry.confidence
            
            # Calculate trend (last 5 vs previous 5 entries)
            trend = self._calculate_mood_trend(mood_entries)
            
            return {
                "total_entries": len(mood_entries),
                "current_mood": mood_entries[-1].mood_type.value,
                "mood_distribution": mood_counts,
                "confidence_average": confidence_sum / len(mood_entries),
                "trend": trend,
                "last_updated": mood_entries[-1].timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating mood analytics: {str(e)}")
            return {
                "total_entries": 0,
                "current_mood": "neutral",
                "mood_distribution": {},
                "confidence_average": 0.5,
                "trend": "stable",
                "error": "analytics_unavailable"
            }
    
    def _calculate_mood_trend(self, mood_entries: List[MoodEntry]) -> str:
        """Calculate mood trend based on recent entries."""
        if len(mood_entries) < 4:
            return "stable"
        
        # Take last 5 and previous 5 entries for comparison
        recent = mood_entries[-5:]
        previous = mood_entries[-10:-5] if len(mood_entries) >= 10 else mood_entries[:-5]
        
        if not previous:
            return "stable"
        
        # Calculate average mood score (positive moods = +1, negative = -1, neutral = 0)
        def mood_score(mood_type: MoodType) -> float:
            positive_moods = [MoodType.POSITIVE, MoodType.EXCITED, MoodType.HOPEFUL, MoodType.CALM]
            negative_moods = [MoodType.NEGATIVE, MoodType.DEPRESSED, MoodType.ANXIOUS, MoodType.FRUSTRATED]
            
            if mood_type in positive_moods:
                return 1.0
            elif mood_type in negative_moods:
                return -1.0
            else:
                return 0.0
        
        recent_avg = sum(mood_score(entry.mood_type) for entry in recent) / len(recent)
        previous_avg = sum(mood_score(entry.mood_type) for entry in previous) / len(previous)
        
        diff = recent_avg - previous_avg
        
        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        else:
            return "stable"
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old mood tracking sessions.
        
        Args:
            max_age_hours: Maximum age in hours for keeping sessions
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            current_time = datetime.now()
            sessions_cleaned = 0
            sessions_to_remove = []
            
            for session_hash, mood_entries in self._mood_history.items():
                if not mood_entries:
                    sessions_to_remove.append(session_hash)
                    continue
                
                # Check if the latest entry is too old
                latest_entry = max(mood_entries, key=lambda x: x.timestamp)
                age_hours = (current_time - latest_entry.timestamp).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    sessions_to_remove.append(session_hash)
            
            # Remove old sessions
            for session_hash in sessions_to_remove:
                del self._mood_history[session_hash]
                sessions_cleaned += 1
            
            if sessions_cleaned > 0:
                logger.info(f"Cleaned up {sessions_cleaned} old mood tracking sessions")
            
            return sessions_cleaned
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {str(e)}")
            return 0
    
    def get_session_mood_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get recent mood history for a session (privacy-safe).
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of mood entries (without raw message content)
        """
        try:
            session_hash = self._hash_session_id(user_id)
            mood_entries = self._mood_history.get(session_hash, [])
            
            # Return recent entries (most recent first)
            recent_entries = mood_entries[-limit:] if len(mood_entries) > limit else mood_entries
            recent_entries.reverse()
            
            return [entry.to_dict() for entry in recent_entries]
            
        except Exception as e:
            logger.error(f"Error retrieving mood history: {str(e)}")
            return []