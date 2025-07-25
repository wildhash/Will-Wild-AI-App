"""
Mood and sentiment analysis for Crisis Support & Mental Health Agent.

This module provides mood detection, sentiment analysis, and emotional
state assessment to help inform therapeutic responses and resource
recommendations.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import Counter
from dataclasses import dataclass

from config import get_settings, logger

settings = get_settings()


@dataclass
class EmotionMatch:
    """Data class for emotion detection matches."""
    emotion: str
    keywords: List[str]
    confidence: float
    intensity: int
    context: str


class MoodAnalyzer:
    """
    Mood and sentiment analysis service.
    
    Provides methods for analyzing emotional content in user messages,
    detecting mood patterns, and tracking emotional state over time.
    """
    
    def __init__(self):
        """Initialize mood analyzer with emotion patterns and models."""
        self.emotion_patterns = self._load_emotion_patterns()
        self.sentiment_modifiers = self._load_sentiment_modifiers()
        self.intensity_indicators = self._load_intensity_indicators()
        
        # Mood tracking for sessions
        self.session_moods = {}
        
        logger.info("MoodAnalyzer initialized")
    
    def _load_emotion_patterns(self) -> Dict[str, Any]:
        """
        Load emotion detection patterns and keywords.
        
        Returns:
            Dictionary containing emotion patterns
            
        TODO: Implement machine learning-based emotion detection
        TODO: Add cultural and linguistic variations
        """
        return {
            "happy": {
                "keywords": [
                    "happy", "joy", "joyful", "excited", "thrilled", "delighted",
                    "pleased", "content", "cheerful", "upbeat", "positive",
                    "amazing", "wonderful", "fantastic", "great", "awesome"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "extremely": 2.0, "incredibly": 1.8,
                    "so": 1.3, "really": 1.2, "absolutely": 1.7
                },
                "base_confidence": 0.8
            },
            "sad": {
                "keywords": [
                    "sad", "sadness", "unhappy", "depressed", "down", "blue",
                    "miserable", "heartbroken", "devastated", "grief",
                    "sorrow", "melancholy", "gloomy", "dejected", "despondent"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "extremely": 2.0, "deeply": 1.8,
                    "so": 1.3, "really": 1.2, "utterly": 1.9
                },
                "base_confidence": 0.8
            },
            "anxious": {
                "keywords": [
                    "anxious", "anxiety", "worried", "nervous", "stressed",
                    "panic", "fearful", "scared", "terrified", "overwhelmed",
                    "tense", "restless", "uneasy", "apprehensive", "frantic"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "extremely": 2.0, "really": 1.2,
                    "so": 1.3, "incredibly": 1.8, "completely": 1.7
                },
                "base_confidence": 0.8
            },
            "angry": {
                "keywords": [
                    "angry", "anger", "mad", "furious", "rage", "irritated",
                    "annoyed", "frustrated", "livid", "outraged", "enraged",
                    "pissed", "hostile", "aggressive", "resentful"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "extremely": 2.0, "really": 1.2,
                    "so": 1.3, "incredibly": 1.8, "absolutely": 1.7
                },
                "base_confidence": 0.8
            },
            "confused": {
                "keywords": [
                    "confused", "lost", "unclear", "puzzled", "bewildered",
                    "perplexed", "mixed up", "uncertain", "unsure", "baffled",
                    "disoriented", "muddled", "foggy", "blank", "stuck"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "completely": 1.8, "totally": 1.6,
                    "so": 1.3, "really": 1.2, "utterly": 1.9
                },
                "base_confidence": 0.7
            },
            "hopeful": {
                "keywords": [
                    "hopeful", "hope", "optimistic", "positive", "confident",
                    "encouraged", "motivated", "inspired", "determined",
                    "looking forward", "excited about", "better", "improving"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "really": 1.2, "so": 1.3,
                    "quite": 1.1, "feeling": 1.2, "getting": 1.3
                },
                "base_confidence": 0.7
            },
            "guilty": {
                "keywords": [
                    "guilty", "guilt", "ashamed", "shame", "regret", "sorry",
                    "remorse", "embarrassed", "humiliated", "self-blame",
                    "fault", "responsible", "bad person", "terrible"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "extremely": 2.0, "so": 1.3,
                    "really": 1.2, "deeply": 1.8, "incredibly": 1.8
                },
                "base_confidence": 0.8
            },
            "lonely": {
                "keywords": [
                    "lonely", "alone", "isolated", "abandoned", "disconnected",
                    "left out", "excluded", "solitary", "friendless",
                    "nobody cares", "no one understands", "by myself"
                ],
                "intensity_multipliers": {
                    "very": 1.5, "so": 1.3, "completely": 1.8,
                    "totally": 1.6, "really": 1.2, "utterly": 1.9
                },
                "base_confidence": 0.8
            }
        }
    
    def _load_sentiment_modifiers(self) -> Dict[str, float]:
        """
        Load sentiment modifiers that affect overall emotional tone.
        
        Returns:
            Dictionary mapping modifiers to sentiment impact
        """
        return {
            # Positive modifiers
            "but": 0.5,  # Often indicates contrast
            "however": 0.5,
            "although": 0.6,
            "despite": 0.7,
            "even though": 0.6,
            
            # Negative modifiers
            "not": -0.8,
            "never": -0.9,
            "no": -0.7,
            "none": -0.8,
            "neither": -0.7,
            
            # Intensity modifiers
            "very": 1.3,
            "extremely": 1.8,
            "really": 1.2,
            "so": 1.2,
            "quite": 1.1,
            "rather": 1.1,
            "pretty": 1.1,
            "somewhat": 0.8,
            "a little": 0.6,
            "slightly": 0.7
        }
    
    def _load_intensity_indicators(self) -> Dict[str, int]:
        """
        Load indicators that suggest emotional intensity.
        
        Returns:
            Dictionary mapping indicators to intensity scores
        """
        return {
            # Punctuation indicators
            "!!!": 3,
            "!!": 2,
            "!": 1,
            "???": 2,
            "??": 1,
            "?": 0,
            
            # Capitalization (detected in analysis)
            "ALL_CAPS": 2,
            "Mixed_Caps": 1,
            
            # Repetition indicators
            "repeated_chars": 2,  # e.g., "sooooo"
            "repeated_words": 1,   # e.g., "no no no"
            
            # Extreme language
            "curse_words": 2,
            "superlatives": 1  # e.g., "worst", "best", "never"
        }
    
    def analyze_mood(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        Analyze mood and emotional content of a message.
        
        Args:
            message: User's message to analyze
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary with mood analysis results
            
        TODO: Implement contextual mood analysis using conversation history
        TODO: Add personality-aware mood interpretation
        """
        try:
            # Initialize analysis results
            analysis = {
                "primary_emotion": "neutral",
                "secondary_emotions": [],
                "intensity": 5,  # 1-10 scale
                "confidence": 0.0,
                "sentiment": "neutral",  # positive/negative/neutral
                "emotional_complexity": 1,  # number of emotions detected
                "indicators": [],
                "mood_trajectory": "stable",  # improving/declining/stable
                "risk_factors": []
            }
            
            # Normalize message for analysis
            normalized_message = self._normalize_for_analysis(message)
            
            # Detect emotions
            emotion_matches = self._detect_emotions(normalized_message)
            
            if emotion_matches:
                # Determine primary emotion
                primary_match = max(emotion_matches, key=lambda x: x.confidence)
                analysis["primary_emotion"] = primary_match.emotion
                analysis["confidence"] = primary_match.confidence
                analysis["intensity"] = primary_match.intensity
                
                # Add secondary emotions
                secondary_matches = [
                    match for match in emotion_matches 
                    if match.emotion != primary_match.emotion and match.confidence > 0.5
                ]
                analysis["secondary_emotions"] = [
                    {"emotion": match.emotion, "confidence": match.confidence}
                    for match in secondary_matches[:3]  # Top 3 secondary emotions
                ]
                
                analysis["emotional_complexity"] = len(emotion_matches)
            
            # Analyze sentiment
            analysis["sentiment"] = self._analyze_sentiment(normalized_message, emotion_matches)
            
            # Detect intensity indicators
            intensity_boost = self._detect_intensity_indicators(message)
            analysis["intensity"] = min(10, analysis["intensity"] + intensity_boost)
            
            # Check for risk factors
            analysis["risk_factors"] = self._detect_risk_factors(normalized_message)
            
            # Track mood trajectory if session provided
            if session_id:
                analysis["mood_trajectory"] = self._analyze_mood_trajectory(
                    session_id, analysis["primary_emotion"], analysis["intensity"]
                )
            
            # Add contextual indicators
            analysis["indicators"] = self._get_mood_indicators(message, emotion_matches)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in mood analysis: {str(e)}")
            return self._get_default_mood_analysis()
    
    def _normalize_for_analysis(self, message: str) -> str:
        """
        Normalize message for mood analysis.
        
        Args:
            message: Raw message
            
        Returns:
            Normalized message
        """
        # Convert to lowercase for analysis (preserve original for intensity detection)
        normalized = message.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Handle contractions
        contractions = {
            "i'm": "i am", "can't": "cannot", "won't": "will not",
            "don't": "do not", "isn't": "is not", "aren't": "are not",
            "wasn't": "was not", "weren't": "were not", "haven't": "have not",
            "hasn't": "has not", "hadn't": "had not", "wouldn't": "would not",
            "couldn't": "could not", "shouldn't": "should not"
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        return normalized
    
    def _detect_emotions(self, message: str) -> List[EmotionMatch]:
        """
        Detect emotions in the message using keyword matching.
        
        Args:
            message: Normalized message
            
        Returns:
            List of emotion matches
            
        TODO: Implement more sophisticated emotion detection using NLP
        """
        emotion_matches = []
        
        for emotion, pattern_info in self.emotion_patterns.items():
            keywords = pattern_info["keywords"]
            base_confidence = pattern_info["base_confidence"]
            intensity_multipliers = pattern_info["intensity_multipliers"]
            
            # Find keyword matches
            matched_keywords = []
            total_confidence = 0
            intensity_sum = 5  # Base intensity
            
            for keyword in keywords:
                if keyword in message:
                    matched_keywords.append(keyword)
                    confidence_boost = 0.1
                    
                    # Check for intensity modifiers around the keyword
                    for modifier, multiplier in intensity_multipliers.items():
                        if modifier in message and abs(message.find(modifier) - message.find(keyword)) < 10:
                            confidence_boost *= multiplier
                            intensity_sum += int(multiplier)
                    
                    total_confidence += confidence_boost
            
            if matched_keywords:
                # Calculate final confidence and intensity
                final_confidence = min(1.0, base_confidence + total_confidence)
                final_intensity = min(10, max(1, intensity_sum // len(matched_keywords)))
                
                # Extract context around matches
                context = self._extract_emotion_context(message, matched_keywords)
                
                emotion_matches.append(EmotionMatch(
                    emotion=emotion,
                    keywords=matched_keywords,
                    confidence=final_confidence,
                    intensity=final_intensity,
                    context=context
                ))
        
        # Sort by confidence
        return sorted(emotion_matches, key=lambda x: x.confidence, reverse=True)
    
    def _extract_emotion_context(self, message: str, keywords: List[str]) -> str:
        """
        Extract context around emotion keywords.
        
        Args:
            message: Full message
            keywords: Matched keywords
            
        Returns:
            Context string
        """
        if not keywords:
            return ""
        
        # Find the first keyword and extract context
        first_keyword = keywords[0]
        keyword_pos = message.find(first_keyword)
        
        if keyword_pos == -1:
            return message[:50] + "..." if len(message) > 50 else message
        
        # Extract 20 characters before and after
        start = max(0, keyword_pos - 20)
        end = min(len(message), keyword_pos + len(first_keyword) + 20)
        
        return message[start:end]
    
    def _analyze_sentiment(self, message: str, emotion_matches: List[EmotionMatch]) -> str:
        """
        Analyze overall sentiment of the message.
        
        Args:
            message: Normalized message
            emotion_matches: Detected emotions
            
        Returns:
            Sentiment classification (positive/negative/neutral)
        """
        if not emotion_matches:
            return "neutral"
        
        # Map emotions to sentiment scores
        emotion_sentiment_scores = {
            "happy": 2, "hopeful": 2, "excited": 2,
            "sad": -2, "angry": -1, "anxious": -1,
            "confused": -0.5, "guilty": -1.5, "lonely": -2
        }
        
        # Calculate weighted sentiment score
        total_score = 0
        total_weight = 0
        
        for match in emotion_matches:
            sentiment_score = emotion_sentiment_scores.get(match.emotion, 0)
            weight = match.confidence
            total_score += sentiment_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return "neutral"
        
        average_score = total_score / total_weight
        
        if average_score > 0.5:
            return "positive"
        elif average_score < -0.5:
            return "negative"
        else:
            return "neutral"
    
    def _detect_intensity_indicators(self, message: str) -> int:
        """
        Detect indicators of emotional intensity in the message.
        
        Args:
            message: Original message (with formatting)
            
        Returns:
            Intensity boost (0-3)
        """
        intensity_boost = 0
        
        # Check punctuation
        exclamation_count = message.count('!')
        if exclamation_count >= 3:
            intensity_boost += 2
        elif exclamation_count >= 2:
            intensity_boost += 1
        
        question_count = message.count('?')
        if question_count >= 3:
            intensity_boost += 1
        
        # Check for ALL CAPS words
        words = message.split()
        caps_words = [word for word in words if word.isupper() and len(word) > 2]
        if len(caps_words) > 2:
            intensity_boost += 2
        elif len(caps_words) > 0:
            intensity_boost += 1
        
        # Check for repeated characters (e.g., "sooooo")
        repeated_chars = re.findall(r'(.)\1{2,}', message.lower())
        if len(repeated_chars) > 1:
            intensity_boost += 1
        
        # Check for curse words or strong language
        strong_language = [
            "damn", "hell", "shit", "fuck", "crap", "bloody",
            "terrible", "horrible", "awful", "devastating"
        ]
        strong_count = sum(1 for word in strong_language if word in message.lower())
        if strong_count > 1:
            intensity_boost += 1
        
        return min(3, intensity_boost)  # Cap at 3
    
    def _detect_risk_factors(self, message: str) -> List[str]:
        """
        Detect risk factors in the emotional content.
        
        Args:
            message: Normalized message
            
        Returns:
            List of detected risk factors
        """
        risk_factors = []
        
        # Social isolation indicators
        isolation_keywords = [
            "nobody cares", "no one understands", "all alone",
            "no friends", "isolated", "abandoned"
        ]
        if any(keyword in message for keyword in isolation_keywords):
            risk_factors.append("social_isolation")
        
        # Hopelessness indicators
        hopelessness_keywords = [
            "no hope", "hopeless", "nothing matters", "no point",
            "give up", "can't go on"
        ]
        if any(keyword in message for keyword in hopelessness_keywords):
            risk_factors.append("hopelessness")
        
        # Self-criticism indicators
        self_criticism_keywords = [
            "hate myself", "worthless", "failure", "stupid",
            "pathetic", "useless", "burden"
        ]
        if any(keyword in message for keyword in self_criticism_keywords):
            risk_factors.append("negative_self_talk")
        
        # Sleep/appetite indicators
        physical_keywords = [
            "can't sleep", "not eating", "no appetite", "exhausted",
            "tired all the time", "can't get out of bed"
        ]
        if any(keyword in message for keyword in physical_keywords):
            risk_factors.append("physical_symptoms")
        
        return risk_factors
    
    def _analyze_mood_trajectory(self, session_id: str, emotion: str, intensity: int) -> str:
        """
        Analyze mood trajectory over the session.
        
        Args:
            session_id: Session identifier
            emotion: Current primary emotion
            intensity: Current intensity level
            
        Returns:
            Trajectory description (improving/declining/stable)
            
        TODO: Implement more sophisticated trajectory analysis
        """
        if session_id not in self.session_moods:
            self.session_moods[session_id] = []
        
        # Store current mood data
        self.session_moods[session_id].append({
            "emotion": emotion,
            "intensity": intensity
        })
        
        # Keep only last 10 entries
        if len(self.session_moods[session_id]) > 10:
            self.session_moods[session_id].pop(0)
        
        moods = self.session_moods[session_id]
        
        if len(moods) < 2:
            return "stable"
        
        # Simple trajectory analysis based on intensity changes
        recent_intensities = [mood["intensity"] for mood in moods[-3:]]
        
        if len(recent_intensities) >= 2:
            trend = recent_intensities[-1] - recent_intensities[0]
            if trend > 1:
                return "improving"
            elif trend < -1:
                return "declining"
        
        return "stable"
    
    def _get_mood_indicators(self, message: str, emotion_matches: List[EmotionMatch]) -> List[str]:
        """
        Get indicators that contributed to the mood analysis.
        
        Args:
            message: Original message
            emotion_matches: Detected emotions
            
        Returns:
            List of mood indicators
        """
        indicators = []
        
        # Add keyword indicators
        if emotion_matches:
            primary_match = emotion_matches[0]
            indicators.append(f"Keywords: {', '.join(primary_match.keywords[:3])}")
        
        # Add formatting indicators
        if '!' in message:
            indicators.append("High punctuation intensity")
        
        words = message.split()
        caps_words = [word for word in words if word.isupper() and len(word) > 2]
        if caps_words:
            indicators.append("Capitalization emphasis")
        
        # Add length indicator
        if len(words) > 50:
            indicators.append("Detailed expression")
        elif len(words) < 5:
            indicators.append("Brief expression")
        
        return indicators
    
    def _get_default_mood_analysis(self) -> Dict[str, Any]:
        """Get default mood analysis when analysis fails."""
        return {
            "primary_emotion": "neutral",
            "secondary_emotions": [],
            "intensity": 5,
            "confidence": 0.0,
            "sentiment": "neutral",
            "emotional_complexity": 1,
            "indicators": ["Analysis failed"],
            "mood_trajectory": "stable",
            "risk_factors": [],
            "error": "Mood analysis failed"
        }
    
    def get_emotion_trends(self, session_id: str) -> Dict[str, Any]:
        """
        Get emotion trends for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with emotion trends
            
        TODO: Implement comprehensive trend analysis
        """
        if session_id not in self.session_moods:
            return {"error": "No mood data for session"}
        
        moods = self.session_moods[session_id]
        
        # Count emotion frequencies
        emotion_counts = Counter(mood["emotion"] for mood in moods)
        
        # Calculate average intensity
        avg_intensity = sum(mood["intensity"] for mood in moods) / len(moods)
        
        # Identify patterns
        emotions_sequence = [mood["emotion"] for mood in moods]
        
        return {
            "session_id": session_id,
            "total_interactions": len(moods),
            "emotion_distribution": dict(emotion_counts),
            "most_common_emotion": emotion_counts.most_common(1)[0] if moods else ("neutral", 0),
            "average_intensity": round(avg_intensity, 1),
            "emotion_sequence": emotions_sequence[-5:],  # Last 5 emotions
            "trend_direction": self._calculate_overall_trend(moods)
        }
    
    def _calculate_overall_trend(self, moods: List[Dict[str, Any]]) -> str:
        """
        Calculate overall emotional trend for the session.
        
        Args:
            moods: List of mood data
            
        Returns:
            Overall trend direction
        """
        if len(moods) < 3:
            return "insufficient_data"
        
        # Map emotions to valence scores
        emotion_valence = {
            "happy": 2, "hopeful": 1.5, "content": 1,
            "neutral": 0, "confused": -0.5, "anxious": -1,
            "sad": -1.5, "angry": -1, "guilty": -2, "lonely": -2
        }
        
        # Calculate valence trend
        valence_scores = [
            emotion_valence.get(mood["emotion"], 0) for mood in moods
        ]
        
        if len(valence_scores) < 3:
            return "stable"
        
        # Simple linear trend
        first_third = sum(valence_scores[:len(valence_scores)//3])
        last_third = sum(valence_scores[-len(valence_scores)//3:])
        
        difference = last_third - first_third
        
        if difference > 1:
            return "improving"
        elif difference < -1:
            return "declining"
        else:
            return "stable"
    
    def clear_session_data(self, session_id: str):
        """
        Clear mood data for a session.
        
        Args:
            session_id: Session to clear
        """
        if session_id in self.session_moods:
            del self.session_moods[session_id]
            logger.info(f"Cleared mood data for session {session_id}")
    
    def get_analyzer_statistics(self) -> Dict[str, Any]:
        """
        Get mood analyzer statistics.
        
        Returns:
            Dictionary with analyzer statistics
        """
        total_sessions = len(self.session_moods)
        total_interactions = sum(len(moods) for moods in self.session_moods.values())
        
        # Aggregate emotion distribution
        all_emotions = []
        for moods in self.session_moods.values():
            all_emotions.extend(mood["emotion"] for mood in moods)
        
        emotion_distribution = dict(Counter(all_emotions))
        
        return {
            "active_sessions": total_sessions,
            "total_interactions": total_interactions,
            "emotion_patterns_loaded": len(self.emotion_patterns),
            "overall_emotion_distribution": emotion_distribution,
            "most_common_emotion": Counter(all_emotions).most_common(1)[0] if all_emotions else ("none", 0)
        }