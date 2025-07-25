"""
Main therapeutic conversation logic for Crisis Support & Mental Health Agent.

This module contains the core TherapyAgent class that handles therapeutic
conversations, integrates with Gemini API, applies CBT techniques, and
manages safety protocols.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.services.gemini_service import GeminiService
from src.services.safety_service import SafetyService
from src.agents.crisis_detector import CrisisDetector
from src.agents.resource_matcher import ResourceMatcher
from src.agents.mood_analyzer import MoodAnalyzer
from src.utils.safety_protocols import SafetyProtocols
from config import get_settings, logger

settings = get_settings()


class TherapyAgent:
    """
    Main therapeutic conversation agent using Google Gemini API.
    
    This agent provides empathetic, safety-focused mental health support
    through conversational AI, incorporating CBT techniques and crisis
    intervention protocols.
    """
    
    def __init__(self):
        """Initialize the therapy agent with required services."""
        self.gemini_service = GeminiService()
        self.safety_service = SafetyService()
        self.crisis_detector = CrisisDetector()
        self.resource_matcher = ResourceMatcher()
        self.mood_analyzer = MoodAnalyzer()
        self.safety_protocols = SafetyProtocols()
        
        # Load CBT techniques
        self.cbt_techniques = self._load_cbt_techniques()
        
        # Conversation context
        self.conversation_memory = {}
        
        logger.info("TherapyAgent initialized")
    
    def _load_cbt_techniques(self) -> Dict[str, Any]:
        """
        Load CBT technique templates from JSON file.
        
        Returns:
            Dict containing CBT techniques and templates
            
        TODO: Implement dynamic loading and caching of CBT techniques
        """
        try:
            cbt_file = Path("src/data/cbt_techniques.json")
            if cbt_file.exists():
                with open(cbt_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading CBT techniques: {str(e)}")
        
        # Return default techniques if file loading fails
        return {
            "thought_challenging": {
                "description": "Help identify and challenge negative thought patterns",
                "prompts": ["What evidence supports this thought?", "What would you tell a friend?"]
            },
            "grounding": {
                "description": "5-4-3-2-1 grounding technique for anxiety",
                "steps": ["5 things you can see", "4 things you can touch", "3 things you can hear", "2 things you can smell", "1 thing you can taste"]
            }
        }
    
    async def generate_response(
        self, 
        message: str, 
        session_id: str, 
        safety_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate therapeutic response to user message.
        
        Args:
            message: User's input message
            session_id: Session identifier for context
            safety_context: Safety assessment results
            
        Returns:
            Dict containing response message, resources, and metadata
            
        TODO: Implement full Gemini integration with therapeutic prompts
        TODO: Add personalization based on conversation history
        TODO: Integrate mood tracking and CBT technique suggestions
        """
        try:
            # Analyze mood and emotional state
            mood_analysis = self.mood_analyzer.analyze_mood(message)
            
            # Check for crisis indicators
            crisis_assessment = self.crisis_detector.detect_crisis_patterns(message)
            
            # If crisis detected, prioritize safety response
            if crisis_assessment["crisis_detected"]:
                return await self._handle_crisis_response(
                    message, session_id, crisis_assessment
                )
            
            # Build therapeutic context
            context = self._build_therapeutic_context(
                message, session_id, mood_analysis, safety_context
            )
            
            # Generate response using Gemini
            response = await self.gemini_service.generate_therapeutic_response(
                message=message,
                context=context,
                session_id=session_id
            )
            
            # Apply CBT techniques if appropriate
            enhanced_response = self._apply_cbt_techniques(
                response, mood_analysis, context
            )
            
            # Find relevant resources
            resources = self.resource_matcher.find_relevant_resources(
                message, mood_analysis["primary_emotion"]
            )
            
            return {
                "message": enhanced_response,
                "mood_analysis": mood_analysis,
                "resources": resources,
                "cbt_techniques_applied": context.get("cbt_techniques", []),
                "safety_level": safety_context["level"]
            }
            
        except Exception as e:
            logger.error(f"Error generating therapeutic response: {str(e)}")
            return self._get_fallback_response(safety_context)
    
    async def _handle_crisis_response(
        self, 
        message: str, 
        session_id: str, 
        crisis_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle crisis situations with immediate safety protocols.
        
        Args:
            message: User's crisis message
            session_id: Session identifier
            crisis_assessment: Crisis detection results
            
        Returns:
            Crisis-appropriate response with safety resources
            
        TODO: Implement immediate crisis intervention protocols
        TODO: Add automatic escalation to human counselors
        TODO: Integrate with emergency services APIs
        """
        logger.warning(f"Crisis detected in session {session_id}: {crisis_assessment}")
        
        # Get emergency resources
        emergency_resources = self.resource_matcher.get_emergency_resources()
        
        # Apply safety protocols
        safety_response = self.safety_protocols.get_crisis_response(
            crisis_type=crisis_assessment["crisis_type"],
            severity=crisis_assessment["severity"]
        )
        
        return {
            "message": safety_response["message"],
            "resources": emergency_resources,
            "escalation_triggered": True,
            "crisis_type": crisis_assessment["crisis_type"],
            "immediate_action_required": True
        }
    
    def _build_therapeutic_context(
        self, 
        message: str, 
        session_id: str, 
        mood_analysis: Dict[str, Any],
        safety_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build context for therapeutic conversation.
        
        Args:
            message: Current user message
            session_id: Session identifier
            mood_analysis: Mood analysis results
            safety_context: Safety assessment
            
        Returns:
            Context dictionary for response generation
            
        TODO: Implement conversation history integration
        TODO: Add user preference and therapy goal tracking
        """
        context = {
            "session_id": session_id,
            "current_mood": mood_analysis["primary_emotion"],
            "mood_intensity": mood_analysis["intensity"],
            "safety_level": safety_context["level"],
            "conversation_turn": len(self.conversation_memory.get(session_id, [])),
            "therapeutic_approach": "person-centered",  # TODO: Make configurable
            "cbt_techniques": []
        }
        
        # Add relevant CBT techniques based on mood
        if mood_analysis["primary_emotion"] in ["anxious", "worried", "overwhelmed"]:
            context["cbt_techniques"].append("grounding")
        elif mood_analysis["primary_emotion"] in ["sad", "hopeless", "worthless"]:
            context["cbt_techniques"].append("thought_challenging")
        
        return context
    
    def _apply_cbt_techniques(
        self, 
        response: str, 
        mood_analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """
        Apply relevant CBT techniques to enhance the response.
        
        Args:
            response: Generated response from Gemini
            mood_analysis: Mood analysis results
            context: Therapeutic context
            
        Returns:
            Enhanced response with CBT techniques
            
        TODO: Implement sophisticated CBT technique integration
        TODO: Add technique effectiveness tracking
        """
        techniques_applied = context.get("cbt_techniques", [])
        
        if not techniques_applied:
            return response
        
        # Add CBT technique suggestions
        cbt_additions = []
        for technique in techniques_applied:
            if technique in self.cbt_techniques:
                cbt_info = self.cbt_techniques[technique]
                cbt_additions.append(f"\n\n**{technique.replace('_', ' ').title()} Technique:**\n{cbt_info['description']}")
        
        if cbt_additions:
            response += "\n" + "\n".join(cbt_additions)
        
        return response
    
    def _get_fallback_response(self, safety_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide fallback response when main generation fails.
        
        Args:
            safety_context: Safety assessment context
            
        Returns:
            Safe fallback response
            
        TODO: Implement more sophisticated fallback responses
        """
        fallback_messages = [
            "I'm here to listen and support you. Can you tell me more about how you're feeling?",
            "Thank you for sharing with me. Your feelings are valid and important.",
            "I want to help you work through this. What's been on your mind lately?"
        ]
        
        return {
            "message": fallback_messages[0],  # TODO: Randomize or contextualize
            "resources": self.resource_matcher.get_general_support_resources(),
            "fallback_used": True,
            "safety_level": safety_context.get("level", "safe")
        }
    
    def update_conversation_memory(
        self, 
        session_id: str, 
        user_message: str, 
        agent_response: str
    ):
        """
        Update conversation memory for context.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            agent_response: Agent's response
            
        TODO: Implement proper memory management with privacy controls
        TODO: Add conversation summarization for long sessions
        """
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        self.conversation_memory[session_id].append({
            "user_message": user_message,
            "agent_response": agent_response,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Limit memory size
        if len(self.conversation_memory[session_id]) > settings.max_conversation_length:
            self.conversation_memory[session_id].pop(0)
    
    def get_therapy_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get therapy session statistics and insights.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session statistics and insights
            
        TODO: Implement comprehensive therapy progress tracking
        """
        session_data = self.conversation_memory.get(session_id, [])
        
        return {
            "session_id": session_id,
            "total_interactions": len(session_data),
            "session_duration": "TODO",  # Calculate from timestamps
            "primary_concerns": "TODO",   # Extract from conversation
            "progress_indicators": "TODO", # Track improvement metrics
            "recommended_techniques": "TODO" # Suggest based on effectiveness
        }