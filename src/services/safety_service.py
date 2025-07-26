import logging
from datetime import datetime
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for crisis detection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrisisEvent:
    """Represents a crisis event for logging and tracking."""
    
    def __init__(self, user_id: str, user_input: str, risk_level: RiskLevel, timestamp: datetime = None):
        self.user_id = user_id
        self.user_input = user_input
        self.risk_level = risk_level
        self.timestamp = timestamp or datetime.now()


class SafetyService:
    """
    Core safety service for crisis detection and escalation.
    
    TODO: Integrate with real alert/notification systems (SMS, email, emergency services).
    """
    
    def __init__(self):
        # In-memory storage for crisis events (MVP)
        self._crisis_events: List[CrisisEvent] = []
        self._user_risk_history: Dict[str, List[CrisisEvent]] = {}
        
        # Crisis keywords for basic detection (expand as needed)
        self._crisis_keywords = {
            RiskLevel.CRITICAL: [
                "suicide", "kill myself", "end my life", "want to die", 
                "overdose", "jumping", "hanging", "gun", "pills"
            ],
            RiskLevel.HIGH: [
                "hurt myself", "self harm", "cutting", "hopeless", 
                "can't go on", "better off dead", "harm others"
            ],
            RiskLevel.MEDIUM: [
                "depressed", "anxious", "panic", "scared", "overwhelmed",
                "can't cope", "breaking down", "crisis"
            ]
        }
        
        logger.info("SafetyService initialized with crisis detection capabilities")
    
    def assess_risk_level(self, user_input: str) -> RiskLevel:
        """
        Assess the risk level of user input based on keywords and patterns.
        
        Args:
            user_input: The user's message to analyze
            
        Returns:
            RiskLevel indicating the severity of potential crisis
        """
        user_input_lower = user_input.lower()
        
        # Check for critical risk keywords first
        for keyword in self._crisis_keywords[RiskLevel.CRITICAL]:
            if keyword in user_input_lower:
                return RiskLevel.CRITICAL
        
        # Check for high risk keywords
        for keyword in self._crisis_keywords[RiskLevel.HIGH]:
            if keyword in user_input_lower:
                return RiskLevel.HIGH
        
        # Check for medium risk keywords
        for keyword in self._crisis_keywords[RiskLevel.MEDIUM]:
            if keyword in user_input_lower:
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def log_crisis_event(self, user_id: str, user_input: str, risk_level: RiskLevel) -> None:
        """
        Log a crisis event for tracking and analysis.
        
        Args:
            user_id: Unique identifier for the user
            user_input: The user's message that triggered the event
            risk_level: The assessed risk level
        """
        event = CrisisEvent(user_id, user_input, risk_level)
        self._crisis_events.append(event)
        
        # Track per-user history
        if user_id not in self._user_risk_history:
            self._user_risk_history[user_id] = []
        self._user_risk_history[user_id].append(event)
        
        # Log to console/file for MVP
        logger.warning(
            f"CRISIS EVENT - User: {user_id}, Risk: {risk_level.value}, "
            f"Time: {event.timestamp.isoformat()}, Input: {user_input[:100]}..."
        )
        
        # TODO: Integrate with monitoring systems (Sentry, DataDog, etc.)
        # TODO: Store in persistent database for audit trail
    
    def notify_crisis_team(self, user_id: str, risk_level: RiskLevel) -> bool:
        """
        Notify the crisis response team based on risk level.
        
        Args:
            user_id: Unique identifier for the user
            risk_level: The assessed risk level
            
        Returns:
            True if notification was sent successfully
        """
        try:
            if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                # For MVP, log to console
                logger.critical(
                    f"CRISIS TEAM NOTIFICATION - URGENT: User {user_id} "
                    f"requires immediate attention. Risk Level: {risk_level.value}"
                )
                
                # TODO: Implement real notification systems:
                # - SMS alerts to crisis team
                # - Email notifications
                # - Integration with emergency services (911, crisis hotlines)
                # - Slack/Teams notifications
                # - Push notifications to mobile app
                
                print(f"🚨 CRISIS ALERT: User {user_id} needs immediate support (Risk: {risk_level.value})")
                return True
            
            elif risk_level == RiskLevel.MEDIUM:
                logger.warning(
                    f"MODERATE RISK NOTIFICATION - User {user_id} "
                    f"may need additional support. Risk Level: {risk_level.value}"
                )
                print(f"⚠️  MODERATE RISK: User {user_id} showing signs of distress (Risk: {risk_level.value})")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify crisis team for user {user_id}: {str(e)}")
            return False
    
    def get_user_risk_history(self, user_id: str) -> List[CrisisEvent]:
        """
        Get the crisis event history for a specific user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of CrisisEvent objects for the user
        """
        return self._user_risk_history.get(user_id, [])
    
    def get_escalation_protocol(self, risk_level: RiskLevel) -> Dict[str, str]:
        """
        Get the escalation protocol for a given risk level.
        
        Args:
            risk_level: The risk level to get protocol for
            
        Returns:
            Dictionary with escalation steps and resources
        """
        protocols = {
            RiskLevel.CRITICAL: {
                "immediate_action": "Contact emergency services immediately",
                "hotline": "National Suicide Prevention Lifeline: 988",
                "response_time": "Immediate (0-5 minutes)",
                "resources": "Emergency services, Crisis intervention team"
            },
            RiskLevel.HIGH: {
                "immediate_action": "Alert crisis team, initiate contact within 1 hour",
                "hotline": "Crisis Text Line: Text HOME to 741741",
                "response_time": "Within 1 hour",
                "resources": "Crisis counselor, Mental health professional"
            },
            RiskLevel.MEDIUM: {
                "immediate_action": "Provide additional resources, monitor closely",
                "hotline": "NAMI Helpline: 1-800-950-NAMI (6264)",
                "response_time": "Within 24 hours",
                "resources": "Mental health resources, Self-help tools"
            },
            RiskLevel.LOW: {
                "immediate_action": "Continue supportive conversation",
                "hotline": "Not required",
                "response_time": "Normal conversation flow",
                "resources": "General mental health resources"
            }
        }
        
        return protocols.get(risk_level, protocols[RiskLevel.LOW])