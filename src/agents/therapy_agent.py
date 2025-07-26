import logging
from typing import Dict, Any
from models.conversation import ConversationContext, Message
from services.memory_service import MemoryService
from services.safety_service import SafetyService, RiskLevel
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class TherapyAgent:
    """
    Main therapy agent that coordinates conversation processing,
    safety assessment, and response generation.
    """
    
    def __init__(self, 
                 memory_service: MemoryService,
                 safety_service: SafetyService,
                 gemini_service: GeminiService):
        self.memory_service = memory_service
        self.safety_service = safety_service
        self.gemini_service = gemini_service
        
        logger.info("TherapyAgent initialized with all services")
    
    def process_conversation(self, user_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process a conversation turn with safety assessment and response generation.
        
        Args:
            user_id: Unique identifier for the user
            user_message: The user's input message
            
        Returns:
            Dictionary containing response, risk level, and session info
        """
        try:
            # Get or create conversation context
            context = self.memory_service.get_conversation_context(user_id)
            
            # Add user message to context
            context.add_message("user", user_message)
            
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
            
            # Generate response using Gemini
            conversation_history = self._build_conversation_prompt(context)
            response = self.gemini_service.generate_response(
                user_message, 
                context=conversation_history
            )
            
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
            
            logger.info(f"Processed conversation for user {user_id}, risk level: {risk_level.value}")
            
            return {
                "response": response,
                "risk_level": risk_level.value,
                "session_id": context.user_id,
                "message_count": len(context.messages)
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation for user {user_id}: {str(e)}")
            
            # Return safe fallback response
            fallback_response = ("I'm experiencing a technical issue right now. "
                               "If this is an emergency, please call 988 (Suicide & Crisis Lifeline) "
                               "or 911 immediately. I'll try to help you again in a moment.")
            
            return {
                "response": fallback_response,
                "risk_level": "unknown",
                "session_id": user_id,
                "error": "processing_error"
            }
    
    def _build_conversation_prompt(self, context: ConversationContext) -> str:
        """
        Build a conversation prompt from the context for better AI responses.
        
        Args:
            context: The conversation context
            
        Returns:
            Formatted conversation history as a prompt
        """
        prompt = ("You are a compassionate AI therapy assistant. You provide supportive, "
                 "non-judgmental responses while being trained to recognize crisis situations. "
                 "Always prioritize user safety and provide appropriate resources when needed.\n\n")
        
        # Add recent conversation history (last 10 messages to avoid token limit)
        recent_messages = context.messages[-10:] if len(context.messages) > 10 else context.messages
        
        for message in recent_messages[:-1]:  # Exclude the current message
            role = "Human" if message.role == "user" else "Assistant"
            prompt += f"{role}: {message.content}\n"
        
        prompt += f"\nHuman: {context.messages[-1].content}\nAssistant:"
        
        return prompt
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of the user's conversation session.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with conversation summary
        """
        try:
            context = self.memory_service.get_conversation_context(user_id)
            risk_history = self.safety_service.get_user_risk_history(user_id)
            
            return {
                "user_id": user_id,
                "session_start": context.session_start_time.isoformat(),
                "message_count": len(context.messages),
                "current_risk_level": context.risk_level,
                "crisis_events": len(risk_history),
                "last_activity": context.messages[-1].timestamp.isoformat() if context.messages else None
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary for user {user_id}: {str(e)}")
            return {"error": "summary_unavailable"}
    
    def end_conversation(self, user_id: str) -> bool:
        """
        End a conversation session and log it.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if conversation was ended successfully
        """
        try:
            context = self.memory_service.get_conversation_context(user_id)
            self.memory_service.log_conversation_end(user_id, context.session_start_time)
            
            logger.info(f"Conversation ended for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending conversation for user {user_id}: {str(e)}")
            return False