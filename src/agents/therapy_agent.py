"""
TherapyAgent - Core therapeutic agent for Crisis Support & Mental Health MVP

This agent orchestrates the complete mental health support workflow, integrating
Gemini AI, safety protocols, memory management, and evidence-based therapeutic
interventions including CBT, grounding techniques, and crisis management.

Features:
- Rule-based and AI-powered risk assessment
- CBT and grounding technique implementation
- Crisis escalation and safety protocols
- Session memory and therapeutic progress tracking
- Multi-modal intervention strategies
- Comprehensive error handling and logging
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid

import structlog

from ..services.gemini_service import GeminiService, RiskLevel, SessionContext
from ..services.safety_service import SafetyService, SafetyLevel, SafetyAssessment
from ..services.memory_service import MemoryService, MemoryType, UserProfile

logger = structlog.get_logger(__name__)


class InterventionType(Enum):
    """Types of therapeutic interventions"""
    CBT_COGNITIVE_RESTRUCTURING = "cbt_cognitive_restructuring"
    CBT_BEHAVIORAL_ACTIVATION = "cbt_behavioral_activation"
    GROUNDING_5_4_3_2_1 = "grounding_5_4_3_2_1"
    GROUNDING_BREATHING = "grounding_breathing"
    MINDFULNESS = "mindfulness"
    CRISIS_DEESCALATION = "crisis_deescalation"
    SAFETY_PLANNING = "safety_planning"
    RESOURCE_CONNECTION = "resource_connection"


class TherapyPhase(Enum):
    """Phases of therapy interaction"""
    INITIAL_ASSESSMENT = "initial_assessment"
    RAPPORT_BUILDING = "rapport_building"
    INTERVENTION = "intervention" 
    SKILL_PRACTICE = "skill_practice"
    PROGRESS_REVIEW = "progress_review"
    CRISIS_MANAGEMENT = "crisis_management"
    CLOSURE = "closure"


@dataclass
class InterventionResult:
    """Result of a therapeutic intervention"""
    intervention_type: InterventionType
    effectiveness_score: float
    user_engagement: float
    completion_status: str
    user_feedback: Optional[str]
    next_steps: List[str]
    timestamp: datetime


@dataclass
class TherapySession:
    """Complete therapy session data"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    phase: TherapyPhase
    interventions_applied: List[InterventionResult]
    risk_assessments: List[Dict[str, Any]]
    therapeutic_goals: List[str]
    session_summary: Optional[str]
    outcome_metrics: Dict[str, float]


class TherapyAgent:
    """
    Production-grade TherapyAgent for Crisis Support & Mental Health

    Orchestrates comprehensive mental health support by integrating:
    - AI-powered conversation through GeminiService
    - Safety protocols through SafetyService  
    - Memory and progress tracking through MemoryService
    - Evidence-based therapeutic interventions
    - Crisis management and escalation procedures
    """
    
    # CBT intervention templates
    CBT_INTERVENTIONS = {
        "thought_challenging": {
            "prompt": "I notice you mentioned some challenging thoughts. Let's explore them together. Can you tell me more about what's going through your mind right now?",
            "questions": [
                "What evidence supports this thought?",
                "What evidence contradicts it?",
                "How would you advise a friend having this thought?",
                "What's the most realistic way to look at this situation?"
            ],
            "reframe_examples": [
                "Instead of 'I always fail,' try 'I've had setbacks, but I've also had successes'",
                "Instead of 'Nothing ever works out,' try 'Some things are challenging, but solutions exist'",
                "Instead of 'I'm worthless,' try 'I'm struggling right now, but I have value'"
            ]
        },
        "behavioral_activation": {
            "activities": [
                "Take a 5-minute walk outside",
                "Listen to a favorite song",
                "Call or text someone you care about",
                "Do one small household task",
                "Practice a hobby for 10 minutes",
                "Write three things you're grateful for"
            ],
            "scheduling_tips": [
                "Start with just 5-10 minutes",
                "Choose activities you used to enjoy",
                "Schedule activities at your best time of day",
                "Plan one small activity daily"
            ]
        }
    }
    
    # Grounding technique templates
    GROUNDING_TECHNIQUES = {
        "5_4_3_2_1": {
            "name": "5-4-3-2-1 Grounding",
            "instructions": [
                "Name 5 things you can see around you",
                "Name 4 things you can touch or feel",
                "Name 3 things you can hear",
                "Name 2 things you can smell",
                "Name 1 thing you can taste"
            ],
            "guidance": "Take your time with each step. This helps bring your attention back to the present moment."
        },
        "box_breathing": {
            "name": "Box Breathing",
            "instructions": [
                "Breathe in slowly for 4 counts",
                "Hold your breath for 4 counts", 
                "Breathe out slowly for 4 counts",
                "Hold empty for 4 counts",
                "Repeat 4-6 times"
            ],
            "guidance": "Focus only on counting and breathing. This helps calm your nervous system."
        },
        "body_scan": {
            "name": "Quick Body Scan",
            "instructions": [
                "Start at the top of your head",
                "Notice any tension or sensations",
                "Slowly move your attention down your body",
                "Breathe into any areas of tension",
                "End at your toes"
            ],
            "guidance": "This helps you reconnect with your physical self and the present moment."
        }
    }
    
    def __init__(self, 
                 gemini_service: GeminiService,
                 safety_service: SafetyService,
                 memory_service: MemoryService):
        """
        Initialize TherapyAgent with required services
        
        Args:
            gemini_service: AI conversation service
            safety_service: Safety assessment and crisis management
            memory_service: Session and user memory management
        """
        self.gemini_service = gemini_service
        self.safety_service = safety_service
        self.memory_service = memory_service
        
        # Active sessions tracking
        self.active_sessions: Dict[str, TherapySession] = {}
        
        # Intervention effectiveness tracking
        self.intervention_analytics: Dict[str, List[float]] = {}
        
        logger.info("TherapyAgent initialized with all services")
    
    async def process_user_message(self, 
                                 message: str,
                                 user_id: str,
                                 session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message with comprehensive therapeutic response
        
        Args:
            message: User's message
            user_id: User identifier  
            session_id: Session identifier (creates new if None)
            
        Returns:
            Dict with therapeutic response and session data
        """
        try:
            # Create session if needed
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Get or create therapy session
            therapy_session = await self._get_or_create_session(session_id, user_id)
            
            # Get user profile for personalization
            user_profile = await self.memory_service.get_user_profile(user_id)
            
            # Comprehensive risk assessment
            risk_assessment = await self._comprehensive_risk_assessment(
                message, user_id, session_id, user_profile
            )
            
            # Safety check and potential escalation
            safety_result = await self._handle_safety_protocols(
                risk_assessment, session_id, user_id
            )
            
            # Determine therapy phase and intervention strategy
            therapy_phase = await self._determine_therapy_phase(
                therapy_session, risk_assessment, user_profile
            )
            
            # Generate therapeutic response
            therapeutic_response = await self._generate_therapeutic_response(
                message, user_id, session_id, therapy_phase, risk_assessment, user_profile
            )
            
            # Apply interventions if needed
            interventions_applied = await self._apply_interventions(
                therapeutic_response, therapy_phase, risk_assessment, session_id
            )
            
            # Update session and memory
            await self._update_session_data(
                therapy_session, message, therapeutic_response, 
                risk_assessment, interventions_applied
            )
            
            # Prepare comprehensive response
            response = {
                "message": therapeutic_response["response"],
                "session_id": session_id,
                "therapy_phase": therapy_phase.value,
                "risk_assessment": {
                    "level": risk_assessment["risk_level"],
                    "score": risk_assessment["risk_score"],
                    "indicators": risk_assessment["indicators"]
                },
                "interventions": [
                    {
                        "type": intervention.intervention_type.value,
                        "effectiveness": intervention.effectiveness_score,
                        "next_steps": intervention.next_steps
                    }
                    for intervention in interventions_applied
                ],
                "safety_status": safety_result.get("status", "safe"),
                "recommendations": therapeutic_response.get("recommendations", []),
                "resources": therapeutic_response.get("crisis_resources", {}),
                "status": "success"
            }
            
            # Add crisis information if needed
            if risk_assessment["risk_level"] in ["high", "crisis"]:
                response["crisis_resources"] = await self.safety_service.get_crisis_resources()
                response["escalation_info"] = safety_result
            
            logger.info("User message processed successfully",
                       session_id=session_id,
                       user_id=user_id,
                       risk_level=risk_assessment["risk_level"],
                       therapy_phase=therapy_phase.value)
            
            return response
            
        except Exception as e:
            logger.error("Failed to process user message", 
                        error=str(e),
                        session_id=session_id,
                        user_id=user_id)
            
            return {
                "message": "I'm experiencing a technical issue right now. If this is an emergency, please contact 988 (Suicide & Crisis Lifeline) or 911 immediately. Otherwise, please try again in a moment.",
                "session_id": session_id,
                "status": "error",
                "crisis_resources": await self.safety_service.get_crisis_resources()
            }
    
    async def _comprehensive_risk_assessment(self, 
                                           message: str,
                                           user_id: str,
                                           session_id: str,
                                           user_profile: Optional[UserProfile]) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment using multiple methods
        
        Args:
            message: User message
            user_id: User identifier
            session_id: Session identifier
            user_profile: User profile data
            
        Returns:
            Dict with comprehensive risk assessment
        """
        # Get conversation history
        conversation_history = await self.memory_service.retrieve_conversation_history(
            session_id, limit=10
        )
        
        # Gemini-based risk assessment
        gemini_history = [
            {"user_message": entry.content.get("user_message", ""),
             "ai_response": entry.content.get("ai_response", ""),
             "risk_score": entry.content.get("risk_assessment", {}).get("risk_score", 0.0)}
            for entry in conversation_history
            if entry.memory_type == MemoryType.CONVERSATION
        ]
        
        gemini_risk_level, gemini_score, gemini_indicators = await self.gemini_service.assess_risk_level(
            message, gemini_history
        )
        
        # Safety service assessment
        safety_assessment = await self.safety_service.assess_safety(
            message, gemini_history, user_profile.__dict__ if user_profile else None
        )
        
        # Historical risk pattern analysis
        safety_history = await self.memory_service.get_recent_safety_history(user_id, days=7)
        historical_risk_trend = self._analyze_risk_trend(safety_history)
        
        # Combine assessments
        combined_risk_score = (
            gemini_score * 0.4 +
            (1.0 if safety_assessment.level == SafetyLevel.IMMINENT else
             0.8 if safety_assessment.level == SafetyLevel.DANGER else
             0.5 if safety_assessment.level == SafetyLevel.CONCERN else 0.2) * 0.4 +
            historical_risk_trend * 0.2
        )
        
        # Determine final risk level
        if combined_risk_score >= 0.8 or safety_assessment.level == SafetyLevel.IMMINENT:
            final_risk_level = "crisis"
        elif combined_risk_score >= 0.6 or safety_assessment.level == SafetyLevel.DANGER:
            final_risk_level = "high"
        elif combined_risk_score >= 0.3 or safety_assessment.level == SafetyLevel.CONCERN:
            final_risk_level = "moderate"
        else:
            final_risk_level = "low"
        
        # Combine indicators
        all_indicators = list(set(gemini_indicators + safety_assessment.risk_factors))
        
        comprehensive_assessment = {
            "risk_level": final_risk_level,
            "risk_score": combined_risk_score,
            "indicators": all_indicators,
            "gemini_assessment": {
                "level": gemini_risk_level.value,
                "score": gemini_score,
                "indicators": gemini_indicators
            },
            "safety_assessment": {
                "level": safety_assessment.level.value,
                "confidence": safety_assessment.confidence,
                "risk_factors": safety_assessment.risk_factors,
                "protective_factors": safety_assessment.protective_factors
            },
            "historical_trend": historical_risk_trend,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store safety assessment in memory
        await self.memory_service.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=MemoryType.SAFETY_HISTORY,
            content=comprehensive_assessment
        )
        
        return comprehensive_assessment
    
    def _analyze_risk_trend(self, safety_history: List[Dict[str, Any]]) -> float:
        """
        Analyze historical risk trend
        
        Args:
            safety_history: Recent safety assessments
            
        Returns:
            Risk trend score (0.0 to 1.0)
        """
        if not safety_history:
            return 0.5  # Neutral if no history
        
        # Get risk scores from recent history
        risk_scores = []
        for entry in safety_history[-7:]:  # Last 7 assessments
            assessment = entry.get("assessment", {})
            risk_scores.append(assessment.get("risk_score", 0.5))
        
        if len(risk_scores) < 2:
            return risk_scores[0] if risk_scores else 0.5
        
        # Calculate trend (simple linear)
        recent_avg = sum(risk_scores[-3:]) / min(3, len(risk_scores))
        older_avg = sum(risk_scores[:-3]) / max(1, len(risk_scores) - 3) if len(risk_scores) > 3 else recent_avg
        
        # Trend factor: positive means increasing risk
        trend_factor = (recent_avg - older_avg) / max(older_avg, 0.1)
        
        # Convert to risk contribution (0.0 to 1.0)
        risk_contribution = max(0.0, min(1.0, 0.5 + trend_factor))
        
        return risk_contribution
    
    async def _handle_safety_protocols(self, 
                                     risk_assessment: Dict[str, Any],
                                     session_id: str,
                                     user_id: str) -> Dict[str, Any]:
        """
        Handle safety protocols based on risk assessment
        
        Args:
            risk_assessment: Risk assessment data
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Dict with safety handling results
        """
        risk_level = risk_assessment["risk_level"]
        
        if risk_level in ["high", "crisis"]:
            # Create safety assessment object
            safety_assessment = SafetyAssessment(
                level=SafetyLevel.IMMINENT if risk_level == "crisis" else SafetyLevel.DANGER,
                confidence=risk_assessment["risk_score"],
                risk_factors=risk_assessment["indicators"],
                protective_factors=risk_assessment["safety_assessment"]["protective_factors"],
                recommendations=[], # Will be filled by safety service
                requires_escalation=True,
                timestamp=datetime.now()
            )
            
            # Initiate escalation
            escalation_result = await self.safety_service.initiate_escalation(
                safety_assessment, session_id, {"user_id": user_id}
            )
            
            logger.critical("Safety escalation initiated",
                           user_id=user_id,
                           session_id=session_id,
                           risk_level=risk_level,
                           escalation_id=escalation_result.get("escalation_id"))
            
            return escalation_result
        
        return {"status": "safe", "monitoring": True}
    
    async def _determine_therapy_phase(self, 
                                     therapy_session: TherapySession,
                                     risk_assessment: Dict[str, Any],
                                     user_profile: Optional[UserProfile]) -> TherapyPhase:
        """
        Determine appropriate therapy phase based on context
        
        Args:
            therapy_session: Current therapy session
            risk_assessment: Risk assessment data
            user_profile: User profile data
            
        Returns:
            Appropriate TherapyPhase
        """
        # Crisis takes priority
        if risk_assessment["risk_level"] in ["high", "crisis"]:
            return TherapyPhase.CRISIS_MANAGEMENT
        
        # Check session history
        session_turn_count = len(therapy_session.interventions_applied)
        
        # New user or session
        if not user_profile or session_turn_count == 0:
            return TherapyPhase.INITIAL_ASSESSMENT
        
        # Early in session - build rapport
        if session_turn_count < 3:
            return TherapyPhase.RAPPORT_BUILDING
        
        # Check if actively working on skills
        recent_interventions = therapy_session.interventions_applied[-3:]
        if any(intervention.intervention_type.value.startswith("cbt_") or 
               intervention.intervention_type.value.startswith("grounding_")
               for intervention in recent_interventions):
            return TherapyPhase.SKILL_PRACTICE
        
        # Default to intervention phase
        return TherapyPhase.INTERVENTION
    
    async def _generate_therapeutic_response(self, 
                                           message: str,
                                           user_id: str,
                                           session_id: str,
                                           therapy_phase: TherapyPhase,
                                           risk_assessment: Dict[str, Any],
                                           user_profile: Optional[UserProfile]) -> Dict[str, Any]:
        """
        Generate therapeutic response using GeminiService with phase-appropriate context
        
        Args:
            message: User message
            user_id: User identifier
            session_id: Session identifier
            therapy_phase: Current therapy phase
            risk_assessment: Risk assessment data
            user_profile: User profile data
            
        Returns:
            Dict with therapeutic response
        """
        # Build context for Gemini
        context = {
            "therapy_phase": therapy_phase.value,
            "risk_assessment": risk_assessment,
            "user_profile": user_profile.__dict__ if user_profile else None,
            "session_goals": user_profile.therapeutic_goals if user_profile else []
        }
        
        # Generate response using GeminiService
        response = await self.gemini_service.generate_response(
            message=message,
            session_id=session_id,
            user_id=user_id,
            context=context
        )
        
        return response
    
    async def _apply_interventions(self, 
                                 therapeutic_response: Dict[str, Any],
                                 therapy_phase: TherapyPhase,
                                 risk_assessment: Dict[str, Any],
                                 session_id: str) -> List[InterventionResult]:
        """
        Apply appropriate therapeutic interventions
        
        Args:
            therapeutic_response: AI therapeutic response
            therapy_phase: Current therapy phase
            risk_assessment: Risk assessment data
            session_id: Session identifier
            
        Returns:
            List of applied interventions
        """
        interventions_applied = []
        
        # Crisis interventions
        if risk_assessment["risk_level"] in ["high", "crisis"]:
            crisis_intervention = await self._apply_crisis_intervention(
                risk_assessment, session_id
            )
            interventions_applied.append(crisis_intervention)
        
        # Phase-based interventions
        elif therapy_phase == TherapyPhase.INTERVENTION:
            # Determine best intervention based on indicators
            indicators = risk_assessment["indicators"]
            
            if any(indicator in ["hopeless", "worthless", "negative thoughts"] for indicator in indicators):
                cbt_intervention = await self._apply_cbt_intervention(
                    InterventionType.CBT_COGNITIVE_RESTRUCTURING, session_id
                )
                interventions_applied.append(cbt_intervention)
            
            if any(indicator in ["isolated", "withdrawn", "inactive"] for indicator in indicators):
                behavioral_intervention = await self._apply_cbt_intervention(
                    InterventionType.CBT_BEHAVIORAL_ACTIVATION, session_id
                )
                interventions_applied.append(behavioral_intervention)
        
        elif therapy_phase == TherapyPhase.SKILL_PRACTICE:
            # Apply grounding techniques
            if any(indicator in ["anxious", "overwhelmed", "panic"] for indicator in risk_assessment["indicators"]):
                grounding_intervention = await self._apply_grounding_technique(
                    InterventionType.GROUNDING_5_4_3_2_1, session_id
                )
                interventions_applied.append(grounding_intervention)
        
        return interventions_applied
    
    async def _apply_crisis_intervention(self, 
                                       risk_assessment: Dict[str, Any],
                                       session_id: str) -> InterventionResult:
        """
        Apply crisis intervention protocols
        
        Args:
            risk_assessment: Risk assessment data
            session_id: Session identifier
            
        Returns:
            InterventionResult for crisis intervention
        """
        # TODO: Implement comprehensive crisis intervention
        # This would include:
        # - Immediate safety assessment
        # - Crisis resource provision
        # - De-escalation techniques
        # - Safety planning
        # - Professional referral coordination
        
        next_steps = [
            "Contact crisis services immediately (988)",
            "Ensure immediate physical safety",
            "Stay with trusted person if possible",
            "Schedule emergency professional consultation"
        ]
        
        intervention_result = InterventionResult(
            intervention_type=InterventionType.CRISIS_DEESCALATION,
            effectiveness_score=0.8,  # High priority intervention
            user_engagement=0.7,
            completion_status="initiated",
            user_feedback=None,
            next_steps=next_steps,
            timestamp=datetime.now()
        )
        
        logger.critical("Crisis intervention applied", 
                       session_id=session_id,
                       risk_level=risk_assessment["risk_level"])
        
        return intervention_result
    
    async def _apply_cbt_intervention(self, 
                                    intervention_type: InterventionType,
                                    session_id: str) -> InterventionResult:
        """
        Apply CBT-based intervention
        
        Args:
            intervention_type: Type of CBT intervention
            session_id: Session identifier
            
        Returns:
            InterventionResult for CBT intervention
        """
        if intervention_type == InterventionType.CBT_COGNITIVE_RESTRUCTURING:
            intervention_data = self.CBT_INTERVENTIONS["thought_challenging"]
            next_steps = [
                "Practice thought challenging with current concerns",
                "Keep a thought record for next session",
                "Notice patterns in negative thinking"
            ]
        elif intervention_type == InterventionType.CBT_BEHAVIORAL_ACTIVATION:
            intervention_data = self.CBT_INTERVENTIONS["behavioral_activation"]
            next_steps = [
                "Choose one activity to try today",
                "Schedule pleasant activities for this week",
                "Track mood before and after activities"
            ]
        else:
            next_steps = ["Continue practicing CBT techniques"]
        
        intervention_result = InterventionResult(
            intervention_type=intervention_type,
            effectiveness_score=0.7,  # CBT is evidence-based
            user_engagement=0.6,  # Depends on user readiness
            completion_status="provided",
            user_feedback=None,
            next_steps=next_steps,
            timestamp=datetime.now()
        )
        
        logger.info("CBT intervention applied", 
                   session_id=session_id,
                   intervention_type=intervention_type.value)
        
        return intervention_result
    
    async def _apply_grounding_technique(self, 
                                       intervention_type: InterventionType,
                                       session_id: str) -> InterventionResult:
        """
        Apply grounding technique intervention
        
        Args:
            intervention_type: Type of grounding technique
            session_id: Session identifier
            
        Returns:
            InterventionResult for grounding intervention
        """
        if intervention_type == InterventionType.GROUNDING_5_4_3_2_1:
            technique_data = self.GROUNDING_TECHNIQUES["5_4_3_2_1"]
        elif intervention_type == InterventionType.GROUNDING_BREATHING:
            technique_data = self.GROUNDING_TECHNIQUES["box_breathing"]
        else:
            technique_data = self.GROUNDING_TECHNIQUES["body_scan"]
        
        next_steps = [
            "Practice this technique when feeling overwhelmed",
            "Try grounding techniques at different times of day",
            "Notice which techniques work best for you"
        ]
        
        intervention_result = InterventionResult(
            intervention_type=intervention_type,
            effectiveness_score=0.8,  # Grounding is generally effective
            user_engagement=0.8,  # Usually well-received
            completion_status="guided",
            user_feedback=None,
            next_steps=next_steps,
            timestamp=datetime.now()
        )
        
        logger.info("Grounding technique applied", 
                   session_id=session_id,
                   intervention_type=intervention_type.value)
        
        return intervention_result
    
    async def _get_or_create_session(self, 
                                   session_id: str, 
                                   user_id: str) -> TherapySession:
        """
        Get existing therapy session or create new one
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            TherapySession object
        """
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Create new therapy session
        session = TherapySession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            end_time=None,
            phase=TherapyPhase.INITIAL_ASSESSMENT,
            interventions_applied=[],
            risk_assessments=[],
            therapeutic_goals=[],
            session_summary=None,
            outcome_metrics={}
        )
        
        self.active_sessions[session_id] = session
        
        logger.info("New therapy session created", 
                   session_id=session_id,
                   user_id=user_id)
        
        return session
    
    async def _update_session_data(self, 
                                 therapy_session: TherapySession,
                                 user_message: str,
                                 therapeutic_response: Dict[str, Any],
                                 risk_assessment: Dict[str, Any],
                                 interventions_applied: List[InterventionResult]):
        """
        Update session data and memory
        
        Args:
            therapy_session: Therapy session to update
            user_message: User message
            therapeutic_response: AI response
            risk_assessment: Risk assessment data
            interventions_applied: Applied interventions
        """
        # Update session
        therapy_session.interventions_applied.extend(interventions_applied)
        therapy_session.risk_assessments.append(risk_assessment)
        
        # Store conversation turn in memory
        await self.memory_service.store_conversation_turn(
            user_id=therapy_session.user_id,
            session_id=therapy_session.session_id,
            user_message=user_message,
            ai_response=therapeutic_response["response"],
            risk_assessment=risk_assessment,
            interventions=[intervention.intervention_type.value for intervention in interventions_applied]
        )
        
        # Store therapeutic progress
        progress_data = {
            "session_turn": len(therapy_session.interventions_applied),
            "risk_score": risk_assessment["risk_score"],
            "interventions_applied": [intervention.intervention_type.value for intervention in interventions_applied],
            "therapy_phase": therapy_session.phase.value,
            "user_engagement": sum(intervention.user_engagement for intervention in interventions_applied) / max(len(interventions_applied), 1)
        }
        
        await self.memory_service.store_memory(
            user_id=therapy_session.user_id,
            session_id=therapy_session.session_id,
            memory_type=MemoryType.THERAPEUTIC_PROGRESS,
            content=progress_data
        )
    
    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive session summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session summary or None if not found
        """
        if session_id not in self.active_sessions:
            return None
        
        therapy_session = self.active_sessions[session_id]
        
        # Get Gemini session summary
        gemini_summary = await self.gemini_service.get_session_summary(session_id)
        
        # Get therapeutic progress
        therapeutic_progress = await self.memory_service.get_therapeutic_progress(
            therapy_session.user_id
        )
        
        # Calculate session metrics
        avg_risk_score = sum(assessment["risk_score"] for assessment in therapy_session.risk_assessments) / max(len(therapy_session.risk_assessments), 1)
        
        interventions_summary = {}
        for intervention in therapy_session.interventions_applied:
            intervention_type = intervention.intervention_type.value
            if intervention_type not in interventions_summary:
                interventions_summary[intervention_type] = {
                    "count": 0,
                    "avg_effectiveness": 0.0,
                    "avg_engagement": 0.0
                }
            interventions_summary[intervention_type]["count"] += 1
            interventions_summary[intervention_type]["avg_effectiveness"] += intervention.effectiveness_score
            interventions_summary[intervention_type]["avg_engagement"] += intervention.user_engagement
        
        # Calculate averages
        for intervention_type in interventions_summary:
            count = interventions_summary[intervention_type]["count"]
            interventions_summary[intervention_type]["avg_effectiveness"] /= count
            interventions_summary[intervention_type]["avg_engagement"] /= count
        
        summary = {
            "session_id": session_id,
            "user_id": therapy_session.user_id,
            "duration_minutes": int((datetime.now() - therapy_session.start_time).total_seconds() / 60),
            "therapy_phase": therapy_session.phase.value,
            "total_interactions": len(therapy_session.risk_assessments),
            "average_risk_score": round(avg_risk_score, 2),
            "interventions_applied": interventions_summary,
            "gemini_session_data": gemini_summary,
            "therapeutic_progress": therapeutic_progress,
            "outcome_metrics": therapy_session.outcome_metrics,
            "status": "active" if therapy_session.end_time is None else "completed"
        }
        
        return summary
    
    async def end_session(self, session_id: str, session_summary: str = None) -> Dict[str, Any]:
        """
        End therapy session and store final summary
        
        Args:
            session_id: Session identifier
            session_summary: Optional session summary
            
        Returns:
            Dict with session closure data
        """
        if session_id not in self.active_sessions:
            return {"status": "session_not_found"}
        
        therapy_session = self.active_sessions[session_id]
        therapy_session.end_time = datetime.now()
        therapy_session.session_summary = session_summary
        therapy_session.phase = TherapyPhase.CLOSURE
        
        # Get final session summary
        final_summary = await self.get_session_summary(session_id)
        
        # Store session closure in memory
        await self.memory_service.store_memory(
            user_id=therapy_session.user_id,
            session_id=session_id,
            memory_type=MemoryType.THERAPEUTIC_PROGRESS,
            content={
                "session_closure": True,
                "final_summary": final_summary,
                "session_summary": session_summary
            }
        )
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info("Therapy session ended", 
                   session_id=session_id,
                   user_id=therapy_session.user_id,
                   duration_minutes=int((therapy_session.end_time - therapy_session.start_time).total_seconds() / 60))
        
        return {
            "status": "session_ended",
            "final_summary": final_summary,
            "session_id": session_id
        }


# TODO: Production integration points
"""
Production Integration TODOs:
1. Connect to electronic health records (EHR) systems
2. Integrate with professional therapist networks
3. Add appointment scheduling and referral systems
4. Implement comprehensive outcome measurement tools
5. Add integration with crisis intervention services
6. Create professional supervision and oversight features
7. Add compliance with healthcare regulations (HIPAA, etc.)
8. Implement advanced analytics and insights dashboards
9. Add multi-language support for diverse populations
10. Create integration with wearable devices for mood tracking
11. Add group therapy and peer support features
12. Implement advanced personalization using ML models
"""