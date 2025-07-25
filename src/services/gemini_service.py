"""
Google Gemini API integration wrapper for Crisis Support & Mental Health Agent.

This module provides a service layer for interacting with Google's Gemini API,
with specialized methods for therapeutic conversation generation and safety-aware
response handling.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from config import get_settings, logger

settings = get_settings()


class GeminiService:
    """
    Service class for Google Gemini API integration.
    
    Provides methods for generating therapeutic responses, handling safety
    considerations, and managing conversation context with Gemini models.
    """
    
    def __init__(self):
        """Initialize Gemini service with API configuration."""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize model with safety settings
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",  # TODO: Consider gemini-pro-vision for future
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,  # Allow some mental health content
                }
            )
            
            # Conversation history for context
            self.chat_sessions = {}
            
            logger.info("GeminiService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GeminiService: {str(e)}")
            raise
    
    async def generate_therapeutic_response(
        self, 
        message: str, 
        context: Dict[str, Any], 
        session_id: str
    ) -> str:
        """
        Generate therapeutic response using Gemini API.
        
        Args:
            message: User's input message
            context: Therapeutic context including mood, safety level, etc.
            session_id: Session identifier for conversation continuity
            
        Returns:
            Generated therapeutic response string
            
        TODO: Implement sophisticated prompt engineering for therapy
        TODO: Add response post-processing for safety and appropriateness
        TODO: Integrate conversation memory and personalization
        """
        try:
            # Build therapeutic prompt
            prompt = self._build_therapeutic_prompt(message, context)
            
            # Get or create chat session
            chat = self._get_chat_session(session_id)
            
            # Generate response
            response = await self._generate_with_retry(chat, prompt)
            
            # Validate and sanitize response
            validated_response = self._validate_therapeutic_response(response, context)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"Error generating therapeutic response: {str(e)}")
            return self._get_safe_fallback_response(context)
    
    def _build_therapeutic_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """
        Build a therapeutic prompt for Gemini API.
        
        Args:
            message: User's message
            context: Therapeutic context
            
        Returns:
            Formatted prompt for Gemini
            
        TODO: Implement sophisticated prompt templates
        TODO: Add context-aware prompt customization
        TODO: Include CBT and therapeutic framework guidance
        """
        base_prompt = f"""You are a compassionate, professional mental health support AI assistant. 
Your role is to provide empathetic, evidence-based support using principles from cognitive-behavioral therapy (CBT) and person-centered therapy.

IMPORTANT GUIDELINES:
- Always prioritize user safety and well-being
- Use active listening and empathetic responses
- Ask open-ended questions to encourage reflection
- Validate emotions and experiences
- Suggest coping strategies when appropriate
- Recognize when professional help may be needed
- Never provide medical diagnoses or replace professional therapy

CURRENT CONTEXT:
- User's mood: {context.get('current_mood', 'unknown')}
- Mood intensity: {context.get('mood_intensity', 'unknown')}
- Safety level: {context.get('safety_level', 'safe')}
- Session turn: {context.get('conversation_turn', 1)}
- Suggested techniques: {', '.join(context.get('cbt_techniques', []))}

USER MESSAGE: "{message}"

Please provide a therapeutic response that:
1. Acknowledges the user's feelings
2. Asks a thoughtful follow-up question
3. Offers gentle guidance or coping strategies if appropriate
4. Maintains a warm, non-judgmental tone

Response:"""
        
        return base_prompt
    
    def _get_chat_session(self, session_id: str):
        """
        Get or create a chat session for conversation continuity.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Gemini chat session object
            
        TODO: Implement session persistence and cleanup
        TODO: Add session-specific configuration
        """
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = self.model.start_chat(history=[])
        
        return self.chat_sessions[session_id]
    
    async def _generate_with_retry(self, chat, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response with retry logic for reliability.
        
        Args:
            chat: Gemini chat session
            prompt: Input prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated response text
            
        TODO: Implement exponential backoff
        TODO: Add different retry strategies for different error types
        """
        for attempt in range(max_retries):
            try:
                response = chat.send_message(prompt)
                return response.text
                
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _validate_therapeutic_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Validate and sanitize therapeutic response.
        
        Args:
            response: Raw response from Gemini
            context: Therapeutic context
            
        Returns:
            Validated and sanitized response
            
        TODO: Implement comprehensive response validation
        TODO: Add inappropriate content filtering
        TODO: Ensure therapeutic guidelines compliance
        """
        # Basic validation
        if not response or len(response.strip()) == 0:
            return self._get_safe_fallback_response(context)
        
        # Check for inappropriate content (placeholder)
        inappropriate_keywords = ["medical diagnosis", "prescription", "medication advice"]
        response_lower = response.lower()
        
        for keyword in inappropriate_keywords:
            if keyword in response_lower:
                logger.warning(f"Potentially inappropriate content detected: {keyword}")
                # TODO: Implement more sophisticated content filtering
        
        # Ensure response ends appropriately
        if not response.endswith(('.', '?', '!')):
            response += "."
        
        return response
    
    def _get_safe_fallback_response(self, context: Dict[str, Any]) -> str:
        """
        Provide safe fallback response when generation fails.
        
        Args:
            context: Therapeutic context
            
        Returns:
            Safe fallback response
            
        TODO: Implement context-aware fallback responses
        """
        fallback_responses = {
            "anxious": "I can hear that you're feeling anxious. That must be really difficult. Can you tell me what's contributing to these feelings right now?",
            "sad": "It sounds like you're going through a tough time. Your feelings are completely valid. Would you like to share what's been weighing on your mind?",
            "angry": "I can sense your frustration. It's okay to feel angry - emotions are information. What's behind these feelings?",
            "default": "Thank you for sharing with me. I want to understand better how you're feeling. Can you tell me more about what brought you here today?"
        }
        
        mood = context.get('current_mood', 'default')
        return fallback_responses.get(mood, fallback_responses["default"])
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Use Gemini to analyze sentiment and emotional content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
            
        TODO: Implement dedicated sentiment analysis with Gemini
        TODO: Add emotion classification and intensity scoring
        """
        try:
            prompt = f"""Analyze the emotional content and sentiment of the following text. 
Provide a JSON response with:
- primary_emotion: the main emotion detected
- intensity: scale of 1-10
- additional_emotions: list of other emotions present
- sentiment: positive/negative/neutral
- crisis_indicators: any concerning language (true/false)

Text: "{text}"

Response (JSON format):"""
            
            response = await self._generate_with_retry(self.model.start_chat(), prompt)
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                logger.error("Failed to parse sentiment analysis JSON")
                return self._get_default_sentiment_analysis()
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._get_default_sentiment_analysis()
    
    def _get_default_sentiment_analysis(self) -> Dict[str, Any]:
        """Get default sentiment analysis when analysis fails."""
        return {
            "primary_emotion": "neutral",
            "intensity": 5,
            "additional_emotions": [],
            "sentiment": "neutral",
            "crisis_indicators": False
        }
    
    async def generate_cbt_exercise(self, emotion: str, context: str) -> Dict[str, Any]:
        """
        Generate personalized CBT exercise using Gemini.
        
        Args:
            emotion: Primary emotion to address
            context: Situational context
            
        Returns:
            Dictionary with CBT exercise details
            
        TODO: Implement CBT exercise generation with Gemini
        TODO: Add exercise tracking and effectiveness measurement
        """
        try:
            prompt = f"""Generate a brief, practical CBT (Cognitive Behavioral Therapy) exercise 
for someone experiencing {emotion}. The exercise should be:
- Evidence-based and therapeutic
- Easy to understand and follow
- Suitable for self-guided practice
- 3-5 steps maximum

Context: {context}

Provide a JSON response with:
- title: exercise name
- description: brief explanation
- steps: array of step-by-step instructions
- duration: estimated time in minutes
- category: type of CBT technique

Response (JSON format):"""
            
            response = await self._generate_with_retry(self.model.start_chat(), prompt)
            
            try:
                exercise = json.loads(response)
                return exercise
            except json.JSONDecodeError:
                logger.error("Failed to parse CBT exercise JSON")
                return self._get_default_cbt_exercise(emotion)
                
        except Exception as e:
            logger.error(f"Error generating CBT exercise: {str(e)}")
            return self._get_default_cbt_exercise(emotion)
    
    def _get_default_cbt_exercise(self, emotion: str) -> Dict[str, Any]:
        """Get default CBT exercise when generation fails."""
        return {
            "title": "Mindful Breathing",
            "description": "A simple breathing exercise to help manage difficult emotions",
            "steps": [
                "Find a comfortable seated position",
                "Close your eyes or soften your gaze",
                "Take a slow, deep breath in through your nose for 4 counts",
                "Hold your breath for 4 counts",
                "Exhale slowly through your mouth for 6 counts",
                "Repeat 5-10 times"
            ],
            "duration": 5,
            "category": "breathing"
        }
    
    def clear_session(self, session_id: str):
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session to clear
            
        TODO: Implement secure session cleanup
        """
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Get service health status.
        
        Returns:
            Dictionary with service health information
            
        TODO: Implement comprehensive health checks
        """
        try:
            # Simple API test
            test_response = self.model.start_chat().send_message("Hello")
            api_status = "healthy" if test_response else "unhealthy"
        except Exception:
            api_status = "unhealthy"
        
        return {
            "service": "GeminiService",
            "status": api_status,
            "active_sessions": len(self.chat_sessions),
            "model": "gemini-pro"
        }