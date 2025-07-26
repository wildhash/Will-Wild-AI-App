import logging
import re
from typing import Dict, List, Tuple
from models.conversation import MoodData

logger = logging.getLogger(__name__)


class MoodAnalysisService:
    """
    Rule-based mood analysis service for MVP implementation.
    
    TODO: Replace with AI/NLP-based analysis for more sophisticated detection.
    TODO: Add more granular mood states beyond basic emotions.
    TODO: Consider context and conversation history for better accuracy.
    """
    
    def __init__(self):
        # Define mood keywords for rule-based detection
        self.mood_keywords = {
            "happy": {
                "keywords": [
                    "happy", "joy", "joyful", "excited", "great", "wonderful", 
                    "amazing", "fantastic", "excellent", "thrilled", "delighted",
                    "cheerful", "glad", "pleased", "content", "satisfied",
                    "elated", "ecstatic", "blissful", "upbeat", "positive"
                ],
                "weight": 1.0
            },
            "sad": {
                "keywords": [
                    "sad", "down", "depressed", "miserable", "awful", "terrible",
                    "heartbroken", "devastated", "disappointed", "upset", "blue",
                    "gloomy", "melancholy", "sorrowful", "dejected", "despondent",
                    "grief", "mourning", "crying", "tears", "lonely"
                ],
                "weight": 1.0
            },
            "anxious": {
                "keywords": [
                    "anxious", "worried", "nervous", "stressed", "panic", "fear",
                    "scared", "terrified", "overwhelmed", "tense", "restless",
                    "uneasy", "concerned", "troubled", "frightened", "agitated",
                    "apprehensive", "paranoid", "insecure", "uncertain"
                ],
                "weight": 1.0
            },
            "angry": {
                "keywords": [
                    "angry", "mad", "furious", "frustrated", "irritated", "rage",
                    "annoyed", "outraged", "livid", "hostile", "bitter", "resentful",
                    "indignant", "irate", "enraged", "aggravated", "pissed",
                    "infuriated", "incensed", "disgusted"
                ],
                "weight": 1.0
            }
        }
        
        # Intensity modifiers to adjust confidence
        self.intensity_modifiers = {
            "very": 1.3,
            "extremely": 1.5,
            "really": 1.2,
            "so": 1.2,
            "quite": 1.1,
            "pretty": 1.1,
            "somewhat": 0.8,
            "a bit": 0.7,
            "slightly": 0.6,
            "kind of": 0.7,
            "sort of": 0.7
        }
        
        logger.info("MoodAnalysisService initialized with rule-based keyword detection")
    
    def analyze_mood(self, message: str) -> MoodData:
        """
        Analyze the mood of a user message using rule-based keyword matching.
        
        Args:
            message: The user's message text
            
        Returns:
            MoodData with detected mood, confidence, and contributing keywords
        """
        message_lower = message.lower()
        mood_scores = {}
        detected_keywords = []
        
        # Score each mood based on keyword matches
        for mood, data in self.mood_keywords.items():
            score = 0.0
            mood_keywords = []
            
            for keyword in data["keywords"]:
                if self._find_keyword_in_text(keyword, message_lower):
                    base_score = data["weight"]
                    # Apply intensity modifiers
                    modified_score = self._apply_intensity_modifiers(keyword, message_lower, base_score)
                    score += modified_score
                    mood_keywords.append(keyword)
            
            if score > 0:
                mood_scores[mood] = score
                detected_keywords.extend(mood_keywords)
        
        # Determine dominant mood and confidence
        if not mood_scores:
            # No mood keywords detected, default to neutral
            return MoodData(
                mood="neutral",
                confidence=0.5,
                keywords=[],
            )
        
        # Find the mood with highest score
        dominant_mood = max(mood_scores, key=mood_scores.get)
        max_score = mood_scores[dominant_mood]
        
        # Calculate confidence based on score strength and uniqueness
        total_score = sum(mood_scores.values())
        confidence = min(0.95, max(0.1, max_score / max(total_score, 1.0)))
        
        # Adjust confidence if multiple moods are detected (lower confidence)
        if len(mood_scores) > 1:
            confidence *= 0.8
        
        # Filter keywords to only those contributing to the dominant mood
        contributing_keywords = [kw for kw in detected_keywords 
                               if kw in self.mood_keywords[dominant_mood]["keywords"]]
        
        logger.debug(f"Mood analysis: '{message[:50]}...' -> {dominant_mood} "
                    f"(confidence: {confidence:.2f}, keywords: {contributing_keywords})")
        
        return MoodData(
            mood=dominant_mood,
            confidence=round(confidence, 2),
            keywords=contributing_keywords[:5],  # Limit to top 5 keywords
        )
    
    def _find_keyword_in_text(self, keyword: str, text: str) -> bool:
        """
        Find keyword in text using word boundary matching.
        
        Args:
            keyword: The keyword to search for
            text: The text to search in
            
        Returns:
            True if keyword is found as a whole word
        """
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _apply_intensity_modifiers(self, keyword: str, message: str, base_score: float) -> float:
        """
        Apply intensity modifiers to adjust the base score.
        
        Args:
            keyword: The matched keyword
            message: The full message text
            base_score: The base score for the keyword
            
        Returns:
            Modified score with intensity adjustments
        """
        score = base_score
        
        # Look for intensity modifiers near the keyword
        for modifier, multiplier in self.intensity_modifiers.items():
            # Check if modifier appears within 3 words of the keyword
            pattern = rf'\b{re.escape(modifier)}\b.{{0,20}}\b{re.escape(keyword)}\b'
            if re.search(pattern, message, re.IGNORECASE):
                score *= multiplier
                break  # Only apply the first modifier found
        
        return score
    
    def calculate_session_mood_summary(self, mood_timeline: List[MoodData]) -> Dict:
        """
        Calculate aggregated mood trends for a session.
        
        Args:
            mood_timeline: List of mood data points from the session
            
        Returns:
            Dictionary with mood summary statistics
        """
        if not mood_timeline:
            return {
                "dominant_mood": "neutral",
                "mood_distribution": {},
                "mood_changes": 0,
                "average_confidence": 0.0
            }
        
        # Count mood occurrences
        mood_counts = {}
        confidence_sum = 0.0
        
        for mood_data in mood_timeline:
            mood = mood_data.mood
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            confidence_sum += mood_data.confidence
        
        # Calculate distribution
        total_moods = len(mood_timeline)
        mood_distribution = {
            mood: round(count / total_moods, 2) 
            for mood, count in mood_counts.items()
        }
        
        # Find dominant mood
        dominant_mood = max(mood_counts, key=mood_counts.get)
        
        # Count mood changes
        mood_changes = 0
        for i in range(1, len(mood_timeline)):
            if mood_timeline[i].mood != mood_timeline[i-1].mood:
                mood_changes += 1
        
        # Average confidence
        average_confidence = round(confidence_sum / total_moods, 2)
        
        return {
            "dominant_mood": dominant_mood,
            "mood_distribution": mood_distribution,
            "mood_changes": mood_changes,
            "average_confidence": average_confidence
        }