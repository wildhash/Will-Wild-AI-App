"""
GeminiService - Core AI service for Crisis Support & Mental Health Agent

This service provides comprehensive AI capabilities using Google's Gemini model
with specialized prompt engineering for mental health contexts, session management,
and robust safety measures.

Features:
- Mental health-focused prompt engineering
- Context and session management
- Crisis detection and safety filtering
- Rate limiting and error handling
- Async operations with proper timeout handling
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import structlog

logger = structlog.get_logger(__name__)


class RiskLevel(Enum):
    """Risk assessment levels for user interactions"""
    LOW = "low"
    MODERATE = "moderate" 
    HIGH = "high"
    CRISIS = "crisis"


class SessionState(Enum):
    """Session states for conversation management"""
    ACTIVE = "active"
    PAUSED = "paused"
    ESCALATED = "escalated"
    ENDED = "ended"


@dataclass
class ConversationTurn:
    """Represents a single turn in conversation"""
    timestamp: datetime
    user_message: str
    ai_response: str
    risk_score: float
    mood_indicators: List[str]
    interventions_suggested: List[str]


@dataclass
class SessionContext:
    """Complete session context for continuity"""
    session_id: str
    user_id: str
    start_time: datetime
    last_activity: datetime
    state: SessionState
    conversation_history: List[ConversationTurn]
    risk_level: RiskLevel
    active_interventions: List[str]
    escalation_notes: Optional[str] = None
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class GeminiService:
    """
    Production-grade GeminiService for Crisis Support & Mental Health Agent
    
    Provides comprehensive AI capabilities with specialized mental health
    prompting, safety measures, and session management.
    """
    
    # Core system prompts for different interaction contexts
    SYSTEM_PROMPTS = {
        "initial_assessment": """You are a compassionate and professional mental health support AI assistant. Your primary goals are:

1. Provide empathetic, non-judgmental support
2. Assess risk levels accurately and safely
3. Guide users toward appropriate resources and coping strategies
4. Never provide medical diagnoses or replace professional treatment

SAFETY PROTOCOLS:
- If user expresses suicidal ideation or immediate self-harm: Respond with Crisis level risk and provide immediate crisis resources
- If user describes severe symptoms: Recommend professional help while providing support
- Always validate emotions while encouraging healthy coping strategies
- Never minimize serious mental health concerns

RESPONSE GUIDELINES:
- Use warm, understanding language
- Ask clarifying questions to better understand their situation
- Provide specific, actionable coping strategies
- Include appropriate resource recommendations
- Maintain hope and emphasize that help is available

Remember: You are a support tool, not a replacement for human professionals.""",

        "ongoing_support": """Continue providing compassionate mental health support. Build on the conversation history to:

1. Reference previous concerns and progress
2. Adapt strategies based on what has/hasn't worked
3. Monitor for changes in risk level or mood
4. Reinforce positive coping mechanisms
5. Gently redirect if user seems to be escalating

Focus on evidence-based approaches like CBT techniques, mindfulness, and grounding exercises when appropriate.""",

        "crisis_intervention": """CRISIS MODE ACTIVATED. The user may be in immediate danger. Your response must:

1. Prioritize immediate safety
2. Provide crisis resources prominently
3. Use de-escalation techniques
4. Encourage immediate professional help
5. Stay with them until situation stabilizes

Crisis Resources:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911

Use calm, steady language and focus on immediate safety planning."""
    }
    
    # Risk assessment keywords and patterns
    RISK_INDICATORS = {
        "crisis": [
            "want to die", "kill myself", "end it all", "suicide", "not worth living",
            "better off dead", "can't go on", "ending my life", "final goodbye",
            "planning to hurt myself", "have a plan", "stockpiling pills"
        ],
        "high": [
            "hopeless", "worthless", "can't cope", "giving up", "nothing matters",
            "self-harm", "cutting", "hurting myself", "no point", "trapped",
            "overwhelming pain", "can't handle", "breaking down"
        ],
        "moderate": [
            "depressed", "anxious", "struggling", "difficult time", "stressed",
            "worried", "scared", "isolated", "lonely", "sad", "upset",
            "tired of life", "exhausted", "burned out"
        ]
    }
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        """
        Initialize GeminiService with comprehensive configuration
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.sessions: Dict[str, SessionContext] = {}
        self.rate_limiter = {}  # Simple rate limiting tracker
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Safety settings - balanced for mental health context
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,  # Allow some mental health discussion
        }
        
        # Generation configuration
        self.generation_config = {
            "temperature": 0.7,  # Balanced creativity and consistency
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
            "candidate_count": 1,
        }
        
        logger.info("GeminiService initialized", model=model_name)
    
    async def assess_risk_level(self, message: str, conversation_history: List[ConversationTurn] = None) -> Tuple[RiskLevel, float, List[str]]:
        """
        Comprehensive risk assessment using rule-based and AI-based analysis
        
        Args:
            message: User's message to assess
            conversation_history: Previous conversation context
            
        Returns:
            Tuple of (risk_level, confidence_score, detected_indicators)
        """
        detected_indicators = []
        rule_based_score = 0.0
        
        # Rule-based assessment
        message_lower = message.lower()
        
        # Crisis indicators (immediate danger)
        crisis_matches = [indicator for indicator in self.RISK_INDICATORS["crisis"] 
                         if indicator in message_lower]
        if crisis_matches:
            detected_indicators.extend(crisis_matches)
            rule_based_score = max(rule_based_score, 0.9)
        
        # High risk indicators
        high_matches = [indicator for indicator in self.RISK_INDICATORS["high"] 
                       if indicator in message_lower]
        if high_matches:
            detected_indicators.extend(high_matches)
            rule_based_score = max(rule_based_score, 0.7)
        
        # Moderate risk indicators
        moderate_matches = [indicator for indicator in self.RISK_INDICATORS["moderate"] 
                           if indicator in message_lower]
        if moderate_matches:
            detected_indicators.extend(moderate_matches)
            rule_based_score = max(rule_based_score, 0.4)
        
        # AI-based assessment for nuanced understanding
        try:
            ai_assessment = await self._get_ai_risk_assessment(message, conversation_history)
            ai_score = ai_assessment.get("risk_score", 0.0)
            ai_indicators = ai_assessment.get("indicators", [])
            
            # Combine rule-based and AI scores (weighted average)
            combined_score = (rule_based_score * 0.6) + (ai_score * 0.4)
            detected_indicators.extend(ai_indicators)
            
        except Exception as e:
            logger.warning("AI risk assessment failed, using rule-based only", error=str(e))
            combined_score = rule_based_score
        
        # Determine risk level
        if combined_score >= 0.8:
            risk_level = RiskLevel.CRISIS
        elif combined_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif combined_score >= 0.3:
            risk_level = RiskLevel.MODERATE
        else:
            risk_level = RiskLevel.LOW
        
        logger.info("Risk assessment completed", 
                   risk_level=risk_level.value, 
                   score=combined_score,
                   indicators=detected_indicators)
        
        return risk_level, combined_score, detected_indicators
    
    async def _get_ai_risk_assessment(self, message: str, conversation_history: List[ConversationTurn] = None) -> Dict[str, Any]:
        """
        Use Gemini for nuanced risk assessment
        
        Args:
            message: User message to assess
            conversation_history: Previous conversation turns
            
        Returns:
            Dict containing risk_score and indicators
        """
        assessment_prompt = f"""
        As a mental health assessment AI, analyze this message for suicide risk, self-harm risk, and overall mental health crisis indicators.
        
        User message: "{message}"
        
        Consider:
        1. Direct statements about self-harm or suicide
        2. Hopelessness and despair indicators
        3. Social isolation mentions
        4. Loss of interest in life
        5. Specific plans or means mentioned
        6. Substance abuse references
        7. Recent major losses or traumas
        
        Respond ONLY with valid JSON in this format:
        {{
            "risk_score": 0.0-1.0,
            "indicators": ["list", "of", "concerning", "phrases"],
            "reasoning": "Brief explanation of assessment"
        }}
        
        Score guide:
        - 0.9-1.0: Immediate crisis/suicide risk
        - 0.7-0.8: High risk, needs immediate attention
        - 0.4-0.6: Moderate risk, concerning
        - 0.0-0.3: Low risk, supportive response appropriate
        """
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    model.generate_content,
                    assessment_prompt,
                    safety_settings=self.safety_settings,
                    generation_config=self.generation_config
                ),
                timeout=10.0
            )
            
            result = json.loads(response.text.strip())
            return result
            
        except asyncio.TimeoutError:
            logger.warning("AI risk assessment timed out")
            return {"risk_score": 0.5, "indicators": [], "reasoning": "Assessment timed out"}
        except json.JSONDecodeError:
            logger.warning("AI risk assessment returned invalid JSON")
            return {"risk_score": 0.5, "indicators": [], "reasoning": "Parse error"}
        except Exception as e:
            logger.error("AI risk assessment failed", error=str(e))
            return {"risk_score": 0.5, "indicators": [], "reasoning": f"Error: {str(e)}"}
    
    async def generate_response(self, 
                              message: str, 
                              session_id: str,
                              user_id: str,
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate contextual, therapeutic response with full safety protocols
        
        Args:
            message: User's message
            session_id: Unique session identifier
            user_id: User identifier
            context: Additional context information
            
        Returns:
            Dict containing response, risk assessment, and recommendations
        """
        try:
            # Get or create session
            session = await self._get_or_create_session(session_id, user_id)
            
            # Check rate limiting
            if await self._is_rate_limited(user_id):
                return {
                    "response": "I need to take a brief pause to ensure I can provide you with the best support. Please try again in a moment.",
                    "risk_level": "low",
                    "status": "rate_limited"
                }
            
            # Assess risk level
            risk_level, risk_score, indicators = await self.assess_risk_level(
                message, session.conversation_history
            )
            
            # Update session risk level
            session.risk_level = risk_level
            session.update_activity()
            
            # Select appropriate system prompt based on context
            if risk_level == RiskLevel.CRISIS:
                system_prompt = self.SYSTEM_PROMPTS["crisis_intervention"]
                session.state = SessionState.ESCALATED
            elif len(session.conversation_history) == 0:
                system_prompt = self.SYSTEM_PROMPTS["initial_assessment"]
            else:
                system_prompt = self.SYSTEM_PROMPTS["ongoing_support"]
            
            # Build conversation context
            conversation_context = self._build_conversation_context(session)
            
            # Generate response using Gemini
            full_prompt = f"""{system_prompt}

CONVERSATION CONTEXT:
{conversation_context}

CURRENT USER MESSAGE: "{message}"

Risk Level Detected: {risk_level.value.upper()}
Risk Indicators: {', '.join(indicators) if indicators else 'None detected'}

Please provide an appropriate therapeutic response following the safety protocols above."""

            model = genai.GenerativeModel(self.model_name)
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    model.generate_content,
                    full_prompt,
                    safety_settings=self.safety_settings,
                    generation_config=self.generation_config
                ),
                timeout=30.0
            )
            
            ai_response = response.text.strip()
            
            # Post-process response for safety
            ai_response = self._post_process_response(ai_response, risk_level)
            
            # Generate recommendations based on risk level
            recommendations = self._generate_recommendations(risk_level, indicators)
            
            # Create conversation turn
            turn = ConversationTurn(
                timestamp=datetime.now(),
                user_message=message,
                ai_response=ai_response,
                risk_score=risk_score,
                mood_indicators=indicators,
                interventions_suggested=recommendations
            )
            
            # Update session
            session.conversation_history.append(turn)
            self.sessions[session_id] = session
            
            logger.info("Response generated successfully", 
                       session_id=session_id,
                       risk_level=risk_level.value,
                       response_length=len(ai_response))
            
            result = {
                "response": ai_response,
                "risk_level": risk_level.value,
                "risk_score": risk_score,
                "indicators": indicators,
                "recommendations": recommendations,
                "session_state": session.state.value,
                "status": "success"
            }
            
            # Add crisis resources if high risk
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRISIS]:
                result["crisis_resources"] = self._get_crisis_resources()
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("Response generation timed out", session_id=session_id)
            return {
                "response": "I'm having trouble processing your message right now. Please try again, or if this is an emergency, please contact 988 (Suicide & Crisis Lifeline) or 911.",
                "risk_level": "moderate",
                "status": "timeout",
                "crisis_resources": self._get_crisis_resources()
            }
            
        except Exception as e:
            logger.error("Response generation failed", session_id=session_id, error=str(e))
            return {
                "response": "I'm experiencing a technical issue. If you're in crisis, please contact 988 (Suicide & Crisis Lifeline) or 911 immediately. Otherwise, please try again in a moment.",
                "risk_level": "moderate", 
                "status": "error",
                "crisis_resources": self._get_crisis_resources()
            }
    
    async def _get_or_create_session(self, session_id: str, user_id: str) -> SessionContext:
        """Get existing session or create new one"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired():
                return session
        
        # Create new session
        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            state=SessionState.ACTIVE,
            conversation_history=[],
            risk_level=RiskLevel.LOW,
            active_interventions=[]
        )
        
        self.sessions[session_id] = session
        logger.info("New session created", session_id=session_id, user_id=user_id)
        return session
    
    async def _is_rate_limited(self, user_id: str) -> bool:
        """Simple rate limiting implementation"""
        now = time.time()
        window = 60  # 1 minute window
        max_requests = 10
        
        if user_id not in self.rate_limiter:
            self.rate_limiter[user_id] = []
        
        # Clean old requests
        self.rate_limiter[user_id] = [
            req_time for req_time in self.rate_limiter[user_id] 
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.rate_limiter[user_id]) >= max_requests:
            return True
        
        # Add current request
        self.rate_limiter[user_id].append(now)
        return False
    
    def _build_conversation_context(self, session: SessionContext) -> str:
        """Build conversation context for better continuity"""
        if not session.conversation_history:
            return "This is the beginning of the conversation."
        
        recent_turns = session.conversation_history[-3:]  # Last 3 turns for context
        context_lines = []
        
        for i, turn in enumerate(recent_turns):
            context_lines.append(f"Turn {i+1}:")
            context_lines.append(f"User: {turn.user_message}")
            context_lines.append(f"Assistant: {turn.ai_response}")
            context_lines.append(f"Risk Score: {turn.risk_score}")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def _post_process_response(self, response: str, risk_level: RiskLevel) -> str:
        """Post-process AI response for safety and quality"""
        # Ensure crisis responses include resources
        if risk_level == RiskLevel.CRISIS:
            if "988" not in response and "crisis" not in response.lower():
                response += "\n\n🚨 IMMEDIATE HELP AVAILABLE:\n• National Suicide Prevention Lifeline: 988\n• Crisis Text Line: Text HOME to 741741\n• Emergency Services: 911"
        
        # Ensure response isn't too long
        if len(response) > 1500:
            response = response[:1400] + "...\n\nI want to make sure I'm giving you focused support. How are you feeling about what we've discussed so far?"
        
        return response
    
    def _generate_recommendations(self, risk_level: RiskLevel, indicators: List[str]) -> List[str]:
        """Generate appropriate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == RiskLevel.CRISIS:
            recommendations.extend([
                "Contact crisis services immediately (988 or 911)",
                "Stay with trusted person if possible",
                "Remove access to means of self-harm",
                "Go to nearest emergency room if needed"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Consider contacting a mental health professional today",
                "Reach out to trusted friends or family",
                "Use crisis resources if feelings worsen (988)",
                "Practice safety planning techniques"
            ])
        elif risk_level == RiskLevel.MODERATE:
            recommendations.extend([
                "Consider scheduling therapy or counseling",
                "Practice self-care and coping strategies",
                "Stay connected with support system",
                "Monitor mood and seek help if worsening"
            ])
        else:
            recommendations.extend([
                "Continue healthy coping strategies",
                "Maintain regular self-care routine",
                "Stay connected with others",
                "Practice mindfulness or relaxation techniques"
            ])
        
        return recommendations
    
    def _get_crisis_resources(self) -> Dict[str, str]:
        """Get crisis intervention resources"""
        return {
            "suicide_prevention_lifeline": "988",
            "crisis_text_line": "Text HOME to 741741",
            "emergency_services": "911",
            "online_chat": "suicidepreventionlifeline.org/chat",
            "veterans_crisis_line": "1-800-273-8255, Press 1"
        }
    
    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session summary"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Calculate session metrics
        total_turns = len(session.conversation_history)
        avg_risk_score = sum(turn.risk_score for turn in session.conversation_history) / max(total_turns, 1)
        peak_risk_score = max((turn.risk_score for turn in session.conversation_history), default=0.0)
        
        # Gather all indicators mentioned
        all_indicators = []
        for turn in session.conversation_history:
            all_indicators.extend(turn.mood_indicators)
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "duration_minutes": int((session.last_activity - session.start_time).total_seconds() / 60),
            "total_turns": total_turns,
            "current_risk_level": session.risk_level.value,
            "average_risk_score": round(avg_risk_score, 2),
            "peak_risk_score": round(peak_risk_score, 2),
            "session_state": session.state.value,
            "indicators_mentioned": list(set(all_indicators)),
            "escalation_notes": session.escalation_notes,
            "last_activity": session.last_activity.isoformat()
        }
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info("Expired session cleaned up", session_id=session_id)
        
        return len(expired_sessions)


# TODO: Integration points for other services
"""
Integration TODOs:
1. Connect to MemoryService for persistent session storage
2. Connect to SafetyService for advanced safety protocols
3. Add database persistence for conversation history
4. Implement advanced analytics and monitoring
5. Add integration with external crisis systems
6. Implement user authentication and authorization
7. Add comprehensive audit logging for compliance
8. Connect to notification systems for escalation
"""