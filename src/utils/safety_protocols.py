"""
Safety validation protocols for Crisis Support & Mental Health Agent.

This module provides safety validation functions, emergency protocols,
and escalation procedures to ensure user safety and appropriate crisis
response.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from config import get_settings, logger

settings = get_settings()


class CrisisLevel(Enum):
    """Enumeration of crisis severity levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseType(Enum):
    """Enumeration of crisis response types."""
    CONTINUE_CONVERSATION = "continue_conversation"
    SUPPORTIVE_RESPONSE = "supportive_response"
    ENHANCED_SUPPORT = "enhanced_support"
    SAFETY_PLANNING = "safety_planning"
    CRISIS_PROTOCOL = "crisis_protocol"
    IMMEDIATE_INTERVENTION = "immediate_intervention"


class SafetyProtocols:
    """
    Safety validation and crisis response protocols.
    
    Provides methods for validating safety assessments, implementing
    crisis response protocols, and managing emergency escalation procedures.
    """
    
    def __init__(self):
        """Initialize safety protocols with emergency procedures."""
        self.crisis_responses = self._load_crisis_responses()
        self.emergency_contacts = self._load_emergency_contacts()
        self.safety_guidelines = self._load_safety_guidelines()
        
        # Protocol tracking
        self.protocol_activations = []
        
        logger.info("SafetyProtocols initialized")
    
    def _load_crisis_responses(self) -> Dict[str, Dict[str, Any]]:
        """
        Load crisis response templates and procedures.
        
        Returns:
            Dictionary containing crisis response protocols
            
        TODO: Load from external configuration file
        TODO: Add customizable response templates
        """
        return {
            "immediate_intervention": {
                "message_template": (
                    "I'm very concerned about what you've shared. Your safety is the most important thing right now. "
                    "Please reach out to the 988 Suicide & Crisis Lifeline at 988 or text 'HELLO' to 741741 for "
                    "immediate support. If you're in immediate danger, please call 911 or go to your nearest emergency room."
                ),
                "required_resources": ["988_lifeline", "crisis_text_line", "emergency_services"],
                "escalation_required": True,
                "follow_up_needed": True,
                "documentation_level": "high"
            },
            "crisis_protocol": {
                "message_template": (
                    "I can hear that you're going through something really difficult right now. "
                    "It's important that you have support. Would you be willing to speak with a crisis counselor? "
                    "The 988 Lifeline (call 988) has trained counselors available 24/7 who can help."
                ),
                "required_resources": ["988_lifeline", "crisis_text_line"],
                "escalation_required": True,
                "follow_up_needed": True,
                "documentation_level": "high"
            },
            "safety_planning": {
                "message_template": (
                    "It sounds like you're struggling with some difficult feelings. "
                    "Let's think about some ways to keep you safe and supported. "
                    "Can you tell me about people in your life you trust or activities that usually help you feel better?"
                ),
                "required_resources": ["support_resources", "coping_strategies"],
                "escalation_required": False,
                "follow_up_needed": True,
                "documentation_level": "medium"
            },
            "enhanced_support": {
                "message_template": (
                    "Thank you for sharing this with me. It takes courage to reach out when you're struggling. "
                    "While I'm here to listen and support you, it might also be helpful to connect with additional resources. "
                    "Would you like me to share some options for professional support?"
                ),
                "required_resources": ["mental_health_professionals", "support_helplines"],
                "escalation_required": False,
                "follow_up_needed": False,
                "documentation_level": "medium"
            },
            "supportive_response": {
                "message_template": (
                    "I'm here to listen and support you. Your feelings are valid and it's okay to not be okay sometimes. "
                    "Can you tell me more about what's been on your mind?"
                ),
                "required_resources": [],
                "escalation_required": False,
                "follow_up_needed": False,
                "documentation_level": "low"
            }
        }
    
    def _load_emergency_contacts(self) -> Dict[str, Dict[str, str]]:
        """
        Load emergency contact information.
        
        Returns:
            Dictionary with emergency contacts
        """
        return {
            "988_lifeline": {
                "name": "988 Suicide & Crisis Lifeline",
                "phone": "988",
                "text": "Text HOME to 741741",
                "website": "https://988lifeline.org",
                "availability": "24/7",
                "description": "Free, confidential support for people in distress"
            },
            "crisis_text_line": {
                "name": "Crisis Text Line",
                "phone": "Text HOME to 741741",
                "website": "https://crisistextline.org",
                "availability": "24/7",
                "description": "Free crisis counseling via text message"
            },
            "emergency_services": {
                "name": "Emergency Services",
                "phone": "911",
                "availability": "24/7",
                "description": "For immediate life-threatening emergencies"
            },
            "nami_helpline": {
                "name": "NAMI HelpLine",
                "phone": "1-800-950-6264",
                "website": "https://nami.org/help",
                "availability": "Mon-Fri 10am-6pm ET",
                "description": "Information, referrals and support"
            }
        }
    
    def _load_safety_guidelines(self) -> Dict[str, List[str]]:
        """
        Load safety guidelines and best practices.
        
        Returns:
            Dictionary with safety guidelines
        """
        return {
            "crisis_response": [
                "Always prioritize user safety over conversation flow",
                "Provide immediate crisis resources when indicated",
                "Document all crisis interventions appropriately",
                "Follow up on safety concerns when possible",
                "Never provide medical diagnoses or treatment advice"
            ],
            "therapeutic_boundaries": [
                "Maintain professional therapeutic boundaries",
                "Recognize limitations of AI-based support",
                "Refer to human professionals when appropriate",
                "Respect user privacy and confidentiality",
                "Avoid giving specific medical or legal advice"
            ],
            "escalation_triggers": [
                "Explicit statements of suicide intent",
                "Specific self-harm plans or methods",
                "Threats of violence toward others",
                "Severe substance abuse or overdose risk",
                "Child abuse or safety concerns"
            ]
        }
    
    def validate_safety_assessment(
        self,
        assessment: Dict[str, Any],
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate a safety assessment and recommend appropriate protocols.
        
        Args:
            assessment: Safety assessment results
            message: Original user message
            context: Additional context information
            
        Returns:
            Validated assessment with protocol recommendations
            
        TODO: Implement multi-factor safety validation
        TODO: Add human-in-the-loop validation for critical cases
        """
        try:
            # Start with the original assessment
            validated_assessment = assessment.copy()
            
            # Perform additional validation checks
            validation_results = self._perform_validation_checks(
                assessment, message, context
            )
            
            # Update assessment based on validation
            if validation_results["severity_adjustment"]:
                original_level = assessment.get("level", "safe")
                adjusted_level = validation_results["adjusted_level"]
                
                validated_assessment["level"] = adjusted_level
                validated_assessment["validation_applied"] = True
                validated_assessment["original_level"] = original_level
                validated_assessment["adjustment_reason"] = validation_results["adjustment_reason"]
            
            # Add protocol recommendation
            protocol_recommendation = self._get_protocol_recommendation(validated_assessment)
            validated_assessment["recommended_protocol"] = protocol_recommendation
            
            # Add required actions
            validated_assessment["required_actions"] = self._get_required_actions(
                validated_assessment
            )
            
            return validated_assessment
            
        except Exception as e:
            logger.error(f"Error validating safety assessment: {str(e)}")
            # Return safe default
            return self._get_safe_default_validation(assessment)
    
    def _perform_validation_checks(
        self,
        assessment: Dict[str, Any],
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform additional validation checks on safety assessment.
        
        Args:
            assessment: Original assessment
            message: User message
            context: Additional context
            
        Returns:
            Validation results
        """
        validation = {
            "severity_adjustment": False,
            "adjusted_level": assessment.get("level", "safe"),
            "adjustment_reason": None,
            "validation_flags": []
        }
        
        current_level = assessment.get("level", "safe")
        message_lower = message.lower()
        
        # Check for escalation triggers
        escalation_triggers = [
            ("kill myself", "critical"),
            ("suicide plan", "critical"),
            ("end my life", "critical"),
            ("take pills", "high"),
            ("hurt someone", "critical"),
            ("have a gun", "critical")
        ]
        
        for trigger, min_level in escalation_triggers:
            if trigger in message_lower:
                if self._is_higher_severity(min_level, current_level):
                    validation["severity_adjustment"] = True
                    validation["adjusted_level"] = min_level
                    validation["adjustment_reason"] = f"Escalation trigger detected: {trigger}"
                    validation["validation_flags"].append(f"trigger_{trigger.replace(' ', '_')}")
                    break
        
        # Check for context-based escalation
        if context:
            # Previous crisis history
            if context.get("previous_crisis", False):
                if current_level == "medium" and not validation["severity_adjustment"]:
                    validation["severity_adjustment"] = True
                    validation["adjusted_level"] = "high"
                    validation["adjustment_reason"] = "Previous crisis history"
                    validation["validation_flags"].append("previous_crisis")
            
            # Repeated safety concerns
            recent_safety_concerns = context.get("recent_safety_concerns", 0)
            if recent_safety_concerns >= 3 and current_level in ["safe", "low"]:
                validation["severity_adjustment"] = True
                validation["adjusted_level"] = "medium"
                validation["adjustment_reason"] = "Repeated safety concerns"
                validation["validation_flags"].append("repeated_concerns")
        
        return validation
    
    def _is_higher_severity(self, level1: str, level2: str) -> bool:
        """Check if level1 is higher severity than level2."""
        severity_order = ["safe", "low", "medium", "high", "critical"]
        return severity_order.index(level1) > severity_order.index(level2)
    
    def _get_protocol_recommendation(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get protocol recommendation based on assessment.
        
        Args:
            assessment: Validated safety assessment
            
        Returns:
            Protocol recommendation
        """
        level = assessment.get("level", "safe")
        crisis_detected = assessment.get("crisis_detected", False)
        escalation_required = assessment.get("escalation_required", False)
        
        # Determine protocol type
        if escalation_required or level == "critical":
            protocol_type = "immediate_intervention"
        elif crisis_detected or level == "high":
            protocol_type = "crisis_protocol"
        elif level == "medium":
            protocol_type = "safety_planning"
        elif level == "low":
            protocol_type = "enhanced_support"
        else:
            protocol_type = "supportive_response"
        
        return {
            "protocol_type": protocol_type,
            "details": self.crisis_responses.get(protocol_type, {}),
            "activation_required": protocol_type in ["immediate_intervention", "crisis_protocol"]
        }
    
    def _get_required_actions(self, assessment: Dict[str, Any]) -> List[str]:
        """
        Get list of required actions based on assessment.
        
        Args:
            assessment: Safety assessment
            
        Returns:
            List of required actions
        """
        actions = []
        
        protocol = assessment.get("recommended_protocol", {})
        protocol_details = protocol.get("details", {})
        
        # Add resource provision requirements
        required_resources = protocol_details.get("required_resources", [])
        if required_resources:
            actions.append("provide_emergency_resources")
        
        # Add escalation requirements
        if protocol_details.get("escalation_required", False):
            actions.append("escalate_to_human")
        
        # Add follow-up requirements
        if protocol_details.get("follow_up_needed", False):
            actions.append("schedule_follow_up")
        
        # Add documentation requirements
        doc_level = protocol_details.get("documentation_level", "low")
        if doc_level in ["medium", "high"]:
            actions.append("document_interaction")
        
        return actions
    
    def get_crisis_response(
        self,
        crisis_type: str,
        severity: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get appropriate crisis response based on type and severity.
        
        Args:
            crisis_type: Type of crisis detected
            severity: Severity level
            context: Additional context
            
        Returns:
            Crisis response configuration
            
        TODO: Implement personalized crisis responses
        TODO: Add multi-language crisis response support
        """
        try:
            # Determine response protocol
            if severity == "critical":
                protocol_type = "immediate_intervention"
            elif severity == "high":
                protocol_type = "crisis_protocol"
            elif severity == "medium":
                protocol_type = "safety_planning"
            else:
                protocol_type = "enhanced_support"
            
            # Get base response
            base_response = self.crisis_responses.get(protocol_type, {})
            
            # Customize based on crisis type
            customized_response = self._customize_crisis_response(
                base_response, crisis_type, context
            )
            
            # Log protocol activation
            self._log_protocol_activation(protocol_type, crisis_type, severity)
            
            return {
                "protocol_type": protocol_type,
                "message": customized_response["message"],
                "resources": customized_response["resources"],
                "escalation_required": base_response.get("escalation_required", False),
                "follow_up_needed": base_response.get("follow_up_needed", False),
                "crisis_type": crisis_type,
                "severity": severity
            }
            
        except Exception as e:
            logger.error(f"Error getting crisis response: {str(e)}")
            return self._get_emergency_fallback_response()
    
    def _customize_crisis_response(
        self,
        base_response: Dict[str, Any],
        crisis_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Customize crisis response based on specific crisis type.
        
        Args:
            base_response: Base response template
            crisis_type: Specific crisis type
            context: Additional context
            
        Returns:
            Customized response
        """
        message_template = base_response.get("message_template", "")
        required_resources = base_response.get("required_resources", [])
        
        # Crisis-specific customizations
        customizations = {
            "suicide_risk": {
                "resources": ["988_lifeline", "crisis_text_line", "emergency_services"],
                "message_suffix": " Remember, you are not alone in this."
            },
            "self_harm": {
                "resources": ["988_lifeline", "crisis_text_line"],
                "message_suffix": " Your life has value and meaning."
            },
            "substance_abuse": {
                "resources": ["samhsa_helpline", "988_lifeline"],
                "message_suffix": " Recovery is possible with the right support."
            },
            "violence_risk": {
                "resources": ["emergency_services", "988_lifeline"],
                "message_suffix": " Let's focus on keeping everyone safe."
            }
        }
        
        customization = customizations.get(crisis_type, {})
        
        # Apply customizations
        customized_message = message_template + customization.get("message_suffix", "")
        customized_resources = customization.get("resources", required_resources)
        
        return {
            "message": customized_message,
            "resources": customized_resources
        }
    
    def _log_protocol_activation(self, protocol_type: str, crisis_type: str, severity: str):
        """
        Log protocol activation for monitoring and analysis.
        
        Args:
            protocol_type: Type of protocol activated
            crisis_type: Type of crisis
            severity: Severity level
        """
        activation = {
            "timestamp": datetime.now().isoformat(),
            "protocol_type": protocol_type,
            "crisis_type": crisis_type,
            "severity": severity
        }
        
        self.protocol_activations.append(activation)
        
        # Keep only recent activations (last 1000)
        if len(self.protocol_activations) > 1000:
            self.protocol_activations.pop(0)
        
        logger.info(f"Protocol activated: {protocol_type} for {crisis_type} ({severity})")
    
    def _get_safe_default_validation(self, original_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Get safe default validation when error occurs."""
        return {
            **original_assessment,
            "level": "safe",
            "validation_applied": True,
            "validation_error": True,
            "recommended_protocol": {
                "protocol_type": "supportive_response",
                "details": self.crisis_responses["supportive_response"],
                "activation_required": False
            },
            "required_actions": ["provide_general_support"]
        }
    
    def _get_emergency_fallback_response(self) -> Dict[str, Any]:
        """Get emergency fallback response when crisis response fails."""
        return {
            "protocol_type": "emergency_fallback",
            "message": (
                "I want to make sure you're safe. If you're having thoughts of suicide or self-harm, "
                "please reach out to the 988 Suicide & Crisis Lifeline at 988 or text 'HELLO' to 741741. "
                "If you're in immediate danger, please call 911."
            ),
            "resources": ["988_lifeline", "crisis_text_line", "emergency_services"],
            "escalation_required": True,
            "follow_up_needed": True,
            "crisis_type": "unknown",
            "severity": "high"
        }
    
    def get_emergency_resources(self) -> List[Dict[str, str]]:
        """
        Get list of emergency resources.
        
        Returns:
            List of emergency contact information
        """
        return [
            {
                "id": key,
                **details
            }
            for key, details in self.emergency_contacts.items()
        ]
    
    def validate_therapeutic_boundaries(
        self,
        agent_response: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate that agent response maintains appropriate therapeutic boundaries.
        
        Args:
            agent_response: Generated agent response
            context: Conversation context
            
        Returns:
            Validation results
            
        TODO: Implement comprehensive boundary validation
        TODO: Add automatic response correction
        """
        validation = {
            "boundaries_maintained": True,
            "violations": [],
            "corrections_needed": [],
            "approval_status": "approved"
        }
        
        response_lower = agent_response.lower()
        
        # Check for boundary violations
        violations = [
            ("medical diagnosis", "diagnose", "provide medical diagnosis"),
            ("medication advice", "medication", "provide medication advice"),
            ("legal advice", "legal", "provide legal advice"),
            ("personal disclosure", "i feel", "make personal disclosures"),
            ("romantic content", "love you", "express romantic feelings")
        ]
        
        for violation_type, keyword, description in violations:
            if keyword in response_lower:
                validation["boundaries_maintained"] = False
                validation["violations"].append(violation_type)
                validation["corrections_needed"].append(f"Remove content that attempts to {description}")
        
        # Set approval status
        if validation["violations"]:
            validation["approval_status"] = "requires_review"
            if "medical diagnosis" in validation["violations"]:
                validation["approval_status"] = "rejected"
        
        return validation
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """
        Get safety protocol statistics.
        
        Returns:
            Dictionary with safety statistics
        """
        # Count protocol activations by type
        protocol_counts = {}
        for activation in self.protocol_activations:
            protocol_type = activation["protocol_type"]
            protocol_counts[protocol_type] = protocol_counts.get(protocol_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for activation in self.protocol_activations:
            severity = activation["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_protocol_activations": len(self.protocol_activations),
            "protocol_type_distribution": protocol_counts,
            "severity_distribution": severity_counts,
            "available_protocols": list(self.crisis_responses.keys()),
            "emergency_contacts": len(self.emergency_contacts),
            "safety_guidelines": sum(len(guidelines) for guidelines in self.safety_guidelines.values())
        }
    
    def test_safety_protocols(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test safety protocols with scenarios.
        
        Args:
            test_scenarios: List of test scenarios
            
        Returns:
            Test results
            
        TODO: Implement comprehensive protocol testing
        """
        results = {
            "total_tests": len(test_scenarios),
            "passed": 0,
            "failed": 0,
            "results": []
        }
        
        for i, scenario in enumerate(test_scenarios):
            assessment = scenario.get("assessment", {})
            expected_protocol = scenario.get("expected_protocol", "")
            
            # Validate the assessment
            validated = self.validate_safety_assessment(
                assessment, 
                scenario.get("message", ""),
                scenario.get("context", {})
            )
            
            # Check if recommended protocol matches expected
            recommended = validated.get("recommended_protocol", {}).get("protocol_type", "")
            
            if recommended == expected_protocol:
                results["passed"] += 1
                status = "PASS"
            else:
                results["failed"] += 1
                status = "FAIL"
            
            results["results"].append({
                "test_id": i + 1,
                "scenario": scenario.get("description", f"Test {i + 1}"),
                "expected_protocol": expected_protocol,
                "recommended_protocol": recommended,
                "status": status
            })
        
        results["accuracy"] = results["passed"] / max(results["total_tests"], 1)
        
        logger.info(f"Safety protocol testing completed: {results['accuracy']:.2%} accuracy")
        return results