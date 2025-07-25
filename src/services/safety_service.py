"""
Safety and crisis detection protocols for Crisis Support & Mental Health Agent.

This module provides safety assessment, crisis detection, and escalation
protocols to ensure user safety and appropriate response to mental health
emergencies.
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from config import get_settings, logger

settings = get_settings()


class SafetyService:
    """
    Service for safety assessment and crisis detection.
    
    Provides methods for analyzing user messages for crisis indicators,
    assessing safety levels, and triggering appropriate escalation protocols.
    """
    
    def __init__(self):
        """Initialize safety service with crisis patterns and protocols."""
        self.crisis_patterns = self._load_crisis_patterns()
        self.safety_levels = {
            "safe": {"score": 0, "description": "No immediate safety concerns"},
            "low": {"score": 1, "description": "Minor emotional distress"},
            "medium": {"score": 2, "description": "Moderate distress, monitoring needed"},
            "high": {"score": 3, "description": "Significant concern, resources recommended"},
            "critical": {"score": 4, "description": "Immediate intervention required"}
        }
        
        # Escalation tracking
        self.escalation_log = []
        
        logger.info("SafetyService initialized")
    
    def _load_crisis_patterns(self) -> Dict[str, Any]:
        """
        Load crisis detection patterns from JSON file.
        
        Returns:
            Dictionary containing crisis keywords and patterns
            
        TODO: Implement dynamic pattern loading and updates
        TODO: Add machine learning-based pattern detection
        """
        try:
            patterns_file = Path("src/data/crisis_patterns.json")
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading crisis patterns: {str(e)}")
        
        # Return default patterns if file loading fails
        return {
            "suicide_risk": {
                "keywords": ["suicide", "kill myself", "end it all", "don't want to live", 
                           "better off dead", "suicide plan", "take my life"],
                "severity": "critical",
                "response_type": "immediate_intervention"
            },
            "self_harm": {
                "keywords": ["cut myself", "hurt myself", "self harm", "cutting", 
                           "burning myself", "punish myself"],
                "severity": "high",
                "response_type": "safety_planning"
            },
            "substance_abuse": {
                "keywords": ["overdose", "too many pills", "drinking too much", 
                           "can't stop using", "substance problem"],
                "severity": "high", 
                "response_type": "resource_referral"
            },
            "violence_risk": {
                "keywords": ["hurt someone", "kill them", "violent thoughts", 
                           "can't control anger", "want to hurt"],
                "severity": "critical",
                "response_type": "immediate_intervention"
            },
            "severe_depression": {
                "keywords": ["hopeless", "nothing matters", "can't go on", 
                           "no point living", "everything is dark"],
                "severity": "medium",
                "response_type": "enhanced_support"
            },
            "panic_anxiety": {
                "keywords": ["panic attack", "can't breathe", "heart racing", 
                           "going crazy", "losing control"],
                "severity": "medium",
                "response_type": "grounding_techniques"
            }
        }
    
    def assess_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess safety level and crisis indicators in a message.
        
        Args:
            message: User's message to assess
            context: Additional context for assessment
            
        Returns:
            Dictionary with safety assessment results
            
        TODO: Implement more sophisticated NLP-based assessment
        TODO: Add context-aware risk evaluation
        TODO: Integrate with conversation history for pattern detection
        """
        try:
            # Initialize assessment
            assessment = {
                "level": "safe",
                "score": 0,
                "crisis_detected": False,
                "crisis_types": [],
                "keywords_found": [],
                "recommended_action": "continue_conversation",
                "resources_needed": [],
                "escalation_required": False
            }
            
            # Normalize message for analysis
            normalized_message = message.lower().strip()
            
            # Check against crisis patterns
            for crisis_type, pattern_info in self.crisis_patterns.items():
                matches = self._check_pattern_matches(normalized_message, pattern_info)
                
                if matches:
                    assessment["crisis_types"].append(crisis_type)
                    assessment["keywords_found"].extend(matches)
                    
                    # Update severity based on highest risk found
                    pattern_severity = pattern_info["severity"]
                    if self._is_higher_severity(pattern_severity, assessment["level"]):
                        assessment["level"] = pattern_severity
                        assessment["score"] = self.safety_levels[pattern_severity]["score"]
                        assessment["recommended_action"] = pattern_info["response_type"]
            
            # Determine if crisis detected
            assessment["crisis_detected"] = assessment["level"] in ["high", "critical"]
            assessment["escalation_required"] = assessment["level"] == "critical"
            
            # Add resource recommendations
            assessment["resources_needed"] = self._get_recommended_resources(assessment)
            
            # Log assessment if concerning
            if assessment["score"] >= 2:
                self._log_safety_concern(message, assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in safety assessment: {str(e)}")
            return self._get_safe_default_assessment()
    
    def _check_pattern_matches(self, message: str, pattern_info: Dict[str, Any]) -> List[str]:
        """
        Check for pattern matches in message.
        
        Args:
            message: Normalized message text
            pattern_info: Pattern information with keywords
            
        Returns:
            List of matched keywords
            
        TODO: Implement fuzzy matching and context-aware detection
        TODO: Add phrase and semantic matching
        """
        matches = []
        keywords = pattern_info.get("keywords", [])
        
        for keyword in keywords:
            # Simple substring matching (TODO: improve with NLP)
            if keyword in message:
                matches.append(keyword)
                
            # Check for word boundaries to avoid false positives
            if re.search(r'\b' + re.escape(keyword) + r'\b', message):
                if keyword not in matches:
                    matches.append(keyword)
        
        return matches
    
    def _is_higher_severity(self, new_severity: str, current_severity: str) -> bool:
        """Check if new severity level is higher than current."""
        severity_order = ["safe", "low", "medium", "high", "critical"]
        return severity_order.index(new_severity) > severity_order.index(current_severity)
    
    def _get_recommended_resources(self, assessment: Dict[str, Any]) -> List[str]:
        """
        Get recommended resources based on assessment.
        
        Args:
            assessment: Safety assessment results
            
        Returns:
            List of recommended resource types
            
        TODO: Implement location-based resource recommendations
        """
        resources = []
        
        if assessment["crisis_detected"]:
            resources.append("crisis_hotline")
            resources.append("emergency_services")
        
        if "suicide_risk" in assessment["crisis_types"]:
            resources.append("suicide_prevention")
        
        if "self_harm" in assessment["crisis_types"]:
            resources.append("self_harm_support")
        
        if "substance_abuse" in assessment["crisis_types"]:
            resources.append("addiction_services")
        
        if assessment["level"] in ["medium", "high"]:
            resources.append("mental_health_professionals")
            resources.append("support_groups")
        
        return resources
    
    def _log_safety_concern(self, message: str, assessment: Dict[str, Any]):
        """
        Log safety concerns for monitoring and review.
        
        Args:
            message: Original message (anonymized)
            assessment: Safety assessment results
            
        TODO: Implement secure, privacy-compliant logging
        TODO: Add alerting for critical cases
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "safety_level": assessment["level"],
            "crisis_types": assessment["crisis_types"],
            "keywords_found": assessment["keywords_found"],
            "escalation_required": assessment["escalation_required"],
            "message_hash": hash(message) if settings.anonymize_logs else message[:50] + "..."
        }
        
        self.escalation_log.append(log_entry)
        logger.warning(f"Safety concern logged: {assessment['level']} - {assessment['crisis_types']}")
        
        # TODO: Implement real-time alerting for critical cases
        if assessment["escalation_required"]:
            self._trigger_escalation_alert(log_entry)
    
    def _trigger_escalation_alert(self, log_entry: Dict[str, Any]):
        """
        Trigger escalation alert for critical cases.
        
        Args:
            log_entry: Log entry with safety concern details
            
        TODO: Implement integration with crisis response teams
        TODO: Add automated emergency service contact protocols
        """
        logger.critical(f"ESCALATION ALERT: Critical safety concern detected - {log_entry}")
        
        # TODO: Implement actual escalation protocols:
        # - Notify human counselors
        # - Prepare emergency resources
        # - Log for legal/ethical compliance
    
    def _get_safe_default_assessment(self) -> Dict[str, Any]:
        """Get safe default assessment when error occurs."""
        return {
            "level": "safe",
            "score": 0,
            "crisis_detected": False,
            "crisis_types": [],
            "keywords_found": [],
            "recommended_action": "continue_conversation",
            "resources_needed": ["general_support"],
            "escalation_required": False,
            "error": "Assessment failed, defaulting to safe"
        }
    
    def get_crisis_patterns(self) -> Dict[str, Any]:
        """
        Get current crisis detection patterns.
        
        Returns:
            Dictionary of crisis patterns
            
        TODO: Add administrative controls and pattern management
        """
        return self.crisis_patterns
    
    def update_crisis_patterns(self, new_patterns: Dict[str, Any]) -> bool:
        """
        Update crisis detection patterns.
        
        Args:
            new_patterns: New pattern definitions
            
        Returns:
            Success status
            
        TODO: Implement pattern validation and testing
        TODO: Add version control for pattern updates
        """
        try:
            # Validate new patterns
            if not self._validate_patterns(new_patterns):
                logger.error("Invalid pattern format provided")
                return False
            
            # Update patterns
            self.crisis_patterns.update(new_patterns)
            
            # Save to file
            patterns_file = Path("src/data/crisis_patterns.json")
            with open(patterns_file, 'w') as f:
                json.dump(self.crisis_patterns, f, indent=2)
            
            logger.info("Crisis patterns updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating crisis patterns: {str(e)}")
            return False
    
    def _validate_patterns(self, patterns: Dict[str, Any]) -> bool:
        """
        Validate crisis pattern format.
        
        Args:
            patterns: Patterns to validate
            
        Returns:
            Validation result
            
        TODO: Implement comprehensive pattern validation
        """
        required_fields = ["keywords", "severity", "response_type"]
        valid_severities = ["safe", "low", "medium", "high", "critical"]
        
        for pattern_name, pattern_info in patterns.items():
            if not all(field in pattern_info for field in required_fields):
                return False
            
            if pattern_info["severity"] not in valid_severities:
                return False
            
            if not isinstance(pattern_info["keywords"], list):
                return False
        
        return True
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """
        Get safety service statistics.
        
        Returns:
            Dictionary with safety statistics
            
        TODO: Implement comprehensive safety analytics
        """
        total_assessments = len(self.escalation_log)
        critical_cases = len([log for log in self.escalation_log if log["safety_level"] == "critical"])
        
        return {
            "total_assessments": total_assessments,
            "critical_cases": critical_cases,
            "patterns_active": len(self.crisis_patterns),
            "escalation_rate": critical_cases / max(total_assessments, 1),
            "last_24h_alerts": 0  # TODO: Implement time-based filtering
        }
    
    def clear_logs(self, older_than_days: int = 30):
        """
        Clear old safety logs based on retention policy.
        
        Args:
            older_than_days: Days to retain logs
            
        TODO: Implement automated log cleanup with compliance requirements
        """
        cutoff_date = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
        
        original_count = len(self.escalation_log)
        self.escalation_log = [
            log for log in self.escalation_log 
            if datetime.fromisoformat(log["timestamp"]).timestamp() > cutoff_date
        ]
        
        cleared_count = original_count - len(self.escalation_log)
        logger.info(f"Cleared {cleared_count} old safety log entries")
    
    def test_safety_patterns(self, test_messages: List[str]) -> Dict[str, Any]:
        """
        Test safety patterns against sample messages.
        
        Args:
            test_messages: List of test messages
            
        Returns:
            Test results
            
        TODO: Implement comprehensive pattern testing suite
        """
        results = {
            "total_tests": len(test_messages),
            "results": [],
            "pattern_coverage": {}
        }
        
        for message in test_messages:
            assessment = self.assess_message(message)
            results["results"].append({
                "message": message[:50] + "..." if len(message) > 50 else message,
                "assessment": assessment
            })
        
        return results