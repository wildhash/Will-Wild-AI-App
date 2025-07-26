import logging
from typing import Dict, Any
from models.conversation import ConversationContext, Message
from services.memory_service import MemoryService
from services.safety_service import SafetyService, RiskLevel
from services.gemini_service import GeminiService
from services.mood_service import MoodService

logger = logging.getLogger(__name__)


class TherapyAgent:
    """
    Main therapy agent that coordinates conversation processing,
    safety assessment, mood tracking, and response generation.
    """
    
    def __init__(self, 
                 memory_service: MemoryService,
                 safety_service: SafetyService,
                 gemini_service: GeminiService,
                 mood_service: MoodService = None):
        self.memory_service = memory_service
        self.safety_service = safety_service
        self.gemini_service = gemini_service
        self.mood_service = mood_service or MoodService()
        
        logger.info("TherapyAgent initialized with all services including mood tracking")
    
    def process_conversation(self, user_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process a conversation turn with safety assessment, mood tracking, and response generation.
        
        Args:
            user_id: Unique identifier for the user
            user_message: The user's input message
            
        Returns:
            Dictionary containing response, risk level, mood info, and session info
        """
        try:
            # Get or create conversation context
            context = self.memory_service.get_conversation_context(user_id)
            
            # Detect mood from user input
            mood_entry = self.mood_service.detect_mood(user_message, user_id)
            
            # Get mood analytics for this session
            mood_analytics = self.mood_service.get_mood_analytics(user_id)
            
            # Add user message to context with mood information
            context.add_message(
                "user", 
                user_message,
                mood_detected=mood_entry.mood_type.value,
                mood_confidence=mood_entry.confidence
            )
            
            # Update context mood information
            context.current_mood = mood_entry.mood_type.value
            context.mood_analytics = mood_analytics
            
            # Assess risk level
            risk_level = self.safety_service.assess_risk_level(user_message)
            
            # Log crisis event if needed
            if risk_level != RiskLevel.LOW:
                self.safety_service.log_crisis_event(user_id, user_message, risk_level)
                
                # Notify crisis team for high-risk situations
                if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    self.safety_service.notify_crisis_team(user_id, risk_level)
            
            # Update context risk level
            context.risk_level = risk_level.value
            
            # Generate response using Gemini with mood context
            conversation_history = self._build_conversation_prompt(context, mood_entry)
            response = self.gemini_service.generate_response(
                user_message, 
                context=conversation_history
            )
            
            # Enhance response based on mood if needed
            response = self._enhance_response_with_mood_awareness(response, mood_entry, mood_analytics)
            
            # Add safety resources if high risk
            if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                protocol = self.safety_service.get_escalation_protocol(risk_level)
                response += f"\n\n🆘 **Immediate Resources Available:**\n"
                response += f"• {protocol['hotline']}\n"
                response += f"• {protocol['immediate_action']}"
            
            # Add assistant response to context
            context.add_message("assistant", response)
            
            # Update conversation in memory
            self.memory_service.update_conversation_context(user_id, context)
            
            logger.info(f"Processed conversation for user {user_id}, "
                       f"risk level: {risk_level.value}, mood: {mood_entry.mood_type.value}")
            
            return {
                "response": response,
                "risk_level": risk_level.value,
                "session_id": context.user_id,
                "message_count": len(context.messages),
                "mood_detected": mood_entry.mood_type.value,
                "mood_confidence": mood_entry.confidence,
                "mood_analytics": mood_analytics
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation for user {user_id}: {str(e)}")
            
            # Return safe fallback response with neutral mood
            fallback_response = ("I'm experiencing a technical issue right now. "
                               "If this is an emergency, please call 988 (Suicide & Crisis Lifeline) "
                               "or 911 immediately. I'll try to help you again in a moment.")
            
            return {
                "response": fallback_response,
                "risk_level": "unknown",
                "session_id": user_id,
                "mood_detected": "neutral",
                "mood_confidence": 0.5,
                "mood_analytics": {"error": "analytics_unavailable"},
                "error": "processing_error"
            }
    
    def _build_conversation_prompt(self, context: ConversationContext, mood_entry) -> str:
        """
        Build a conversation prompt from the context with mood awareness for better AI responses.
        
        Args:
            context: The conversation context
            mood_entry: Current mood detection result
            
        Returns:
            Formatted conversation history as a prompt
        """
        prompt = ("You are a compassionate AI therapy assistant. You provide supportive, "
                 "non-judgmental responses while being trained to recognize crisis situations. "
                 "Always prioritize user safety and provide appropriate resources when needed. "
                 f"The user's current detected mood is: {mood_entry.mood_type.value} "
                 f"(confidence: {mood_entry.confidence:.2f}). "
                 f"Overall mood trend: {context.mood_analytics.get('trend', 'stable')}. "
                 "Tailor your response to be mood-appropriate and supportive.\n\n")
        
        # Add recent conversation history (last 10 messages to avoid token limit)
        recent_messages = context.messages[-10:] if len(context.messages) > 10 else context.messages
        
        for message in recent_messages[:-1]:  # Exclude the current message
            role = "Human" if message.role == "user" else "Assistant"
            # Include mood information if available
            mood_info = f" [Mood: {message.mood_detected}]" if message.mood_detected else ""
            prompt += f"{role}{mood_info}: {message.content}\n"
        
        prompt += f"\nHuman: {context.messages[-1].content}\nAssistant:"
        
        return prompt
    
    def _enhance_response_with_mood_awareness(self, response: str, mood_entry, mood_analytics: Dict) -> str:
        """
        Enhance the response based on detected mood and trends.
        
        Args:
            response: Original AI response
            mood_entry: Current mood detection result
            mood_analytics: Mood analytics and trends
            
        Returns:
            Enhanced response with mood-aware additions
        """
        try:
            # Add mood validation opportunity for certain moods
            mood_type = mood_entry.mood_type.value
            confidence = mood_entry.confidence
            
            # Only add mood feedback for confident detections
            if confidence > 0.7:
                if mood_type in ["anxious", "frustrated", "depressed"]:
                    response += f"\n\n💭 I'm sensing you might be feeling {mood_type}. Is that accurate? "
                    response += "It's okay to feel this way, and I'm here to support you."
                elif mood_type in ["positive", "excited", "hopeful"]:
                    response += f"\n\n😊 It seems like you're feeling {mood_type} - that's wonderful! "
                    response += "I'm glad to hear some positivity in your message."
            
            # Add trend awareness for concerning patterns
            trend = mood_analytics.get('trend', 'stable')
            if trend == 'declining' and mood_analytics.get('total_entries', 0) > 5:
                response += "\n\n🤗 I've noticed your mood seems to have been challenging lately. "
                response += "Remember that it's normal for emotions to fluctuate, and seeking support is a sign of strength."
            
            return response
            
        except Exception as e:
            logger.error(f"Error enhancing response with mood awareness: {str(e)}")
            return response  # Return original response if enhancement fails
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of the user's conversation session with enhanced mood information.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with conversation summary including mood analytics
        """
        try:
            context = self.memory_service.get_conversation_context(user_id)
            risk_history = self.safety_service.get_user_risk_history(user_id)
            mood_analytics = self.mood_service.get_mood_analytics(user_id)
            
            return {
                "user_id": user_id,
                "session_start": context.session_start_time.isoformat(),
                "message_count": len(context.messages),
                "current_risk_level": context.risk_level,
                "current_mood": context.current_mood,
                "crisis_events": len(risk_history),
                "mood_analytics": mood_analytics,
                "last_activity": context.messages[-1].timestamp.isoformat() if context.messages else None
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary for user {user_id}: {str(e)}")
            return {"error": "summary_unavailable"}
    
    def end_conversation(self, user_id: str) -> bool:
        """
        End a conversation session and log it with privacy protection.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if conversation was ended successfully
        """
        try:
            context = self.memory_service.get_conversation_context(user_id)
            self.memory_service.log_conversation_end(user_id, context.session_start_time)
            
            # Privacy-safe logging
            user_hash = user_id[:8] + "..." if len(user_id) > 8 else user_id
            logger.info(f"Conversation ended for user hash: {user_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending conversation for user {user_id}: {str(e)}")
            return False