"""
Privacy and data protection handler for Crisis Support & Mental Health Agent.

This module provides privacy-compliant data handling, PII detection and
redaction, data anonymization, and compliance with mental health data
protection regulations.
"""

import re
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from config import get_settings, logger

settings = get_settings()


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PIIType(Enum):
    """Types of personally identifiable information."""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    DATE_OF_BIRTH = "date_of_birth"
    MEDICAL_ID = "medical_id"
    IP_ADDRESS = "ip_address"
    LOCATION = "location"


@dataclass
class PIIMatch:
    """Data class for PII detection matches."""
    pii_type: PIIType
    value: str
    start_pos: int
    end_pos: int
    confidence: float
    context: str


class PrivacyHandler:
    """
    Privacy and data protection handler.
    
    Provides comprehensive privacy protection including PII detection,
    data anonymization, retention management, and compliance reporting.
    """
    
    def __init__(self):
        """Initialize privacy handler with detection patterns and policies."""
        self.pii_patterns = self._load_pii_patterns()
        self.retention_policies = self._load_retention_policies()
        self.anonymization_config = self._load_anonymization_config()
        
        # Tracking for privacy compliance
        self.data_processing_log = []
        self.consent_records = {}
        
        logger.info("PrivacyHandler initialized")
    
    def _load_pii_patterns(self) -> Dict[PIIType, List[Dict[str, Any]]]:
        """
        Load PII detection patterns.
        
        Returns:
            Dictionary mapping PII types to detection patterns
            
        TODO: Implement machine learning-based PII detection
        TODO: Add context-aware PII identification
        """
        return {
            PIIType.EMAIL: [{
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "confidence": 0.95,
                "description": "Email address pattern"
            }],
            PIIType.PHONE: [
                {
                    "pattern": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                    "confidence": 0.90,
                    "description": "US phone number pattern"
                },
                {
                    "pattern": r'\b\d{3}-\d{3}-\d{4}\b',
                    "confidence": 0.95,
                    "description": "Formatted phone number"
                }
            ],
            PIIType.SSN: [{
                "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
                "confidence": 0.95,
                "description": "Social Security Number"
            }],
            PIIType.CREDIT_CARD: [{
                "pattern": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                "confidence": 0.85,
                "description": "Credit card number pattern"
            }],
            PIIType.ADDRESS: [
                {
                    "pattern": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b',
                    "confidence": 0.80,
                    "description": "Street address pattern"
                },
                {
                    "pattern": r'\b\d{5}(?:-\d{4})?\b',
                    "confidence": 0.70,
                    "description": "ZIP code pattern"
                }
            ],
            PIIType.DATE_OF_BIRTH: [
                {
                    "pattern": r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
                    "confidence": 0.85,
                    "description": "Date of birth MM/DD/YYYY"
                },
                {
                    "pattern": r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+(?:19|20)\d{2}\b',
                    "confidence": 0.80,
                    "description": "Date of birth in text format"
                }
            ],
            PIIType.NAME: [
                {
                    "pattern": r'\b(?:my name is|i am|i\'m|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                    "confidence": 0.85,
                    "description": "Self-identified name"
                }
            ],
            PIIType.IP_ADDRESS: [{
                "pattern": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                "confidence": 0.90,
                "description": "IPv4 address"
            }],
            PIIType.LOCATION: [
                {
                    "pattern": r'\b(?:i live in|from|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                    "confidence": 0.75,
                    "description": "Self-reported location"
                }
            ]
        }
    
    def _load_retention_policies(self) -> Dict[str, Dict[str, Any]]:
        """
        Load data retention policies.
        
        Returns:
            Dictionary with retention policies for different data types
        """
        return {
            "conversation_data": {
                "retention_days": settings.data_retention_days,
                "classification": DataClassification.CONFIDENTIAL,
                "auto_delete": True,
                "anonymize_after": 7,  # days
                "requires_consent": True
            },
            "crisis_incidents": {
                "retention_days": 365,  # Keep longer for safety analysis
                "classification": DataClassification.RESTRICTED,
                "auto_delete": False,  # Manual review required
                "anonymize_after": 30,
                "requires_consent": False  # Safety override
            },
            "session_metadata": {
                "retention_days": 90,
                "classification": DataClassification.INTERNAL,
                "auto_delete": True,
                "anonymize_after": 14,
                "requires_consent": True
            },
            "analytics_data": {
                "retention_days": 180,
                "classification": DataClassification.INTERNAL,
                "auto_delete": True,
                "anonymize_after": 1,  # Immediate anonymization
                "requires_consent": True
            }
        }
    
    def _load_anonymization_config(self) -> Dict[str, Any]:
        """
        Load anonymization configuration.
        
        Returns:
            Configuration for data anonymization
        """
        return {
            "hash_salt": "crisis_support_agent_salt_2024",  # TODO: Use secure random salt
            "replacement_tokens": {
                PIIType.EMAIL: "[EMAIL_REDACTED]",
                PIIType.PHONE: "[PHONE_REDACTED]",
                PIIType.NAME: "[NAME_REDACTED]",
                PIIType.ADDRESS: "[ADDRESS_REDACTED]",
                PIIType.SSN: "[SSN_REDACTED]",
                PIIType.CREDIT_CARD: "[CARD_REDACTED]",
                PIIType.DATE_OF_BIRTH: "[DOB_REDACTED]",
                PIIType.IP_ADDRESS: "[IP_REDACTED]",
                PIIType.LOCATION: "[LOCATION_REDACTED]"
            },
            "preserve_structure": True,  # Keep text structure for analysis
            "hash_pii": True,  # Store hashed versions for correlation
            "log_redactions": True  # Log what was redacted
        }
    
    def detect_pii(self, text: str, context: Dict[str, Any] = None) -> List[PIIMatch]:
        """
        Detect personally identifiable information in text.
        
        Args:
            text: Text to analyze for PII
            context: Additional context for detection
            
        Returns:
            List of PII matches found
            
        TODO: Implement context-aware PII detection
        TODO: Add false positive filtering
        """
        try:
            pii_matches = []
            
            for pii_type, patterns in self.pii_patterns.items():
                for pattern_config in patterns:
                    pattern = pattern_config["pattern"]
                    base_confidence = pattern_config["confidence"]
                    
                    # Find all matches
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        # Extract context around match
                        start = max(0, match.start() - 20)
                        end = min(len(text), match.end() + 20)
                        match_context = text[start:end]
                        
                        # Adjust confidence based on context
                        adjusted_confidence = self._adjust_pii_confidence(
                            match.group(), pii_type, match_context, context
                        )
                        
                        if adjusted_confidence > 0.5:  # Confidence threshold
                            pii_matches.append(PIIMatch(
                                pii_type=pii_type,
                                value=match.group(),
                                start_pos=match.start(),
                                end_pos=match.end(),
                                confidence=adjusted_confidence,
                                context=match_context
                            ))
            
            # Sort by position for consistent processing
            pii_matches.sort(key=lambda x: x.start_pos)
            
            return pii_matches
            
        except Exception as e:
            logger.error(f"Error detecting PII: {str(e)}")
            return []
    
    def _adjust_pii_confidence(
        self,
        match_value: str,
        pii_type: PIIType,
        context: str,
        additional_context: Dict[str, Any]
    ) -> float:
        """
        Adjust PII detection confidence based on context.
        
        Args:
            match_value: Matched PII value
            pii_type: Type of PII detected
            context: Text context around match
            additional_context: Additional context information
            
        Returns:
            Adjusted confidence score
        """
        base_confidence = 0.8  # Default confidence
        
        # Context-based adjustments
        context_lower = context.lower()
        
        # Reduce confidence for common false positives
        false_positive_indicators = {
            PIIType.PHONE: ["example", "555-", "000-", "123-"],
            PIIType.EMAIL: ["example.com", "test@", "@example"],
            PIIType.ADDRESS: ["123 main", "example street"],
            PIIType.NAME: ["john doe", "jane smith", "test user"]
        }
        
        if pii_type in false_positive_indicators:
            for indicator in false_positive_indicators[pii_type]:
                if indicator in match_value.lower() or indicator in context_lower:
                    base_confidence *= 0.3  # Significantly reduce confidence
        
        # Increase confidence for self-disclosure patterns
        self_disclosure_indicators = [
            "my", "i am", "call me", "i live", "my number is"
        ]
        
        for indicator in self_disclosure_indicators:
            if indicator in context_lower:
                base_confidence = min(1.0, base_confidence * 1.2)
                break
        
        return base_confidence
    
    def redact_pii(
        self,
        text: str,
        pii_matches: List[PIIMatch] = None,
        anonymize: bool = False
    ) -> Dict[str, Any]:
        """
        Redact or anonymize PII in text.
        
        Args:
            text: Original text
            pii_matches: Pre-detected PII matches (optional)
            anonymize: Whether to anonymize (hash) rather than redact
            
        Returns:
            Dictionary with redacted text and metadata
            
        TODO: Implement reversible anonymization for authorized access
        """
        try:
            if pii_matches is None:
                pii_matches = self.detect_pii(text)
            
            if not pii_matches:
                return {
                    "redacted_text": text,
                    "original_text": text,
                    "redactions_made": 0,
                    "pii_found": [],
                    "anonymization_applied": False
                }
            
            redacted_text = text
            redaction_log = []
            offset = 0  # Track position changes due to replacements
            
            # Process matches in reverse order to maintain positions
            for match in reversed(pii_matches):
                original_value = match.value
                replacement = self._get_replacement_value(match, anonymize)
                
                # Calculate actual positions accounting for previous replacements
                actual_start = match.start_pos + offset
                actual_end = match.end_pos + offset
                
                # Perform replacement
                redacted_text = (
                    redacted_text[:actual_start] + 
                    replacement + 
                    redacted_text[actual_end:]
                )
                
                # Update offset
                offset += len(replacement) - len(original_value)
                
                # Log redaction
                redaction_log.append({
                    "pii_type": match.pii_type.value,
                    "original_value": original_value if not anonymize else "[REDACTED]",
                    "replacement": replacement,
                    "confidence": match.confidence,
                    "position": f"{match.start_pos}-{match.end_pos}"
                })
            
            # Log the redaction operation
            self._log_data_processing(
                "pii_redaction",
                {
                    "pii_types_found": [match.pii_type.value for match in pii_matches],
                    "redactions_count": len(pii_matches),
                    "anonymized": anonymize
                }
            )
            
            return {
                "redacted_text": redacted_text,
                "original_text": text if not anonymize else "[ORIGINAL_REDACTED]",
                "redactions_made": len(pii_matches),
                "pii_found": [
                    {
                        "type": match.pii_type.value,
                        "confidence": match.confidence
                    }
                    for match in pii_matches
                ],
                "redaction_log": redaction_log,
                "anonymization_applied": anonymize
            }
            
        except Exception as e:
            logger.error(f"Error redacting PII: {str(e)}")
            # Return original text on error for safety
            return {
                "redacted_text": text,
                "original_text": text,
                "redactions_made": 0,
                "pii_found": [],
                "error": str(e)
            }
    
    def _get_replacement_value(self, match: PIIMatch, anonymize: bool) -> str:
        """
        Get replacement value for PII match.
        
        Args:
            match: PII match to replace
            anonymize: Whether to use anonymized hash
            
        Returns:
            Replacement string
        """
        if not anonymize:
            # Use standard redaction token
            return self.anonymization_config["replacement_tokens"].get(
                match.pii_type, "[REDACTED]"
            )
        
        # Create anonymized hash
        salt = self.anonymization_config["hash_salt"]
        hash_input = f"{match.value}_{salt}_{match.pii_type.value}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        
        return f"[{match.pii_type.value.upper()}_{hash_value}]"
    
    def anonymize_conversation_data(
        self,
        conversation_data: Dict[str, Any],
        preserve_analytics: bool = True
    ) -> Dict[str, Any]:
        """
        Anonymize conversation data while preserving analytical value.
        
        Args:
            conversation_data: Original conversation data
            preserve_analytics: Whether to preserve data for analytics
            
        Returns:
            Anonymized conversation data
            
        TODO: Implement differential privacy techniques
        TODO: Add data utility preservation metrics
        """
        try:
            anonymized_data = conversation_data.copy()
            
            # Anonymize text content
            if "user_message" in anonymized_data:
                redaction_result = self.redact_pii(
                    anonymized_data["user_message"], 
                    anonymize=True
                )
                anonymized_data["user_message"] = redaction_result["redacted_text"]
                anonymized_data["user_message_pii_found"] = redaction_result["pii_found"]
            
            if "agent_response" in anonymized_data:
                redaction_result = self.redact_pii(
                    anonymized_data["agent_response"], 
                    anonymize=True
                )
                anonymized_data["agent_response"] = redaction_result["redacted_text"]
            
            # Handle session identifiers
            if "session_id" in anonymized_data:
                original_session_id = anonymized_data["session_id"]
                anonymized_data["session_id"] = self._anonymize_identifier(
                    original_session_id, "session"
                )
            
            if "user_id" in anonymized_data:
                original_user_id = anonymized_data["user_id"]
                anonymized_data["user_id"] = self._anonymize_identifier(
                    original_user_id, "user"
                ) if original_user_id else None
            
            # Preserve analytical data if requested
            if preserve_analytics:
                # Keep mood analysis, safety levels, etc. as they don't contain PII
                analytical_fields = [
                    "mood_analysis", "safety_level", "crisis_detected",
                    "resources_provided", "timestamp"
                ]
                for field in analytical_fields:
                    if field in conversation_data:
                        anonymized_data[field] = conversation_data[field]
            
            # Add anonymization metadata
            anonymized_data["anonymization_applied"] = True
            anonymized_data["anonymization_timestamp"] = datetime.now().isoformat()
            anonymized_data["preserve_analytics"] = preserve_analytics
            
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Error anonymizing conversation data: {str(e)}")
            # Return minimal safe data on error
            return {
                "anonymization_applied": True,
                "anonymization_error": str(e),
                "timestamp": conversation_data.get("timestamp"),
                "safety_level": conversation_data.get("safety_level", "unknown")
            }
    
    def _anonymize_identifier(self, identifier: str, identifier_type: str) -> str:
        """
        Anonymize an identifier while maintaining consistency.
        
        Args:
            identifier: Original identifier
            identifier_type: Type of identifier
            
        Returns:
            Anonymized identifier
        """
        salt = f"{self.anonymization_config['hash_salt']}_{identifier_type}"
        hash_input = f"{identifier}_{salt}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        
        return f"anon_{identifier_type}_{hash_value}"
    
    def check_data_retention_compliance(
        self,
        data_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check data retention compliance for given data items.
        
        Args:
            data_items: List of data items to check
            
        Returns:
            Compliance check results
            
        TODO: Implement automated retention policy enforcement
        """
        compliance_results = {
            "total_items": len(data_items),
            "compliant_items": 0,
            "non_compliant_items": 0,
            "items_requiring_action": [],
            "actions_required": []
        }
        
        current_time = datetime.now()
        
        for item in data_items:
            item_type = item.get("data_type", "unknown")
            timestamp_str = item.get("timestamp")
            
            if not timestamp_str:
                compliance_results["non_compliant_items"] += 1
                compliance_results["items_requiring_action"].append({
                    "item_id": item.get("id", "unknown"),
                    "issue": "missing_timestamp",
                    "action": "manual_review"
                })
                continue
            
            try:
                item_timestamp = datetime.fromisoformat(timestamp_str)
                age_days = (current_time - item_timestamp).days
                
                # Get retention policy for this data type
                retention_policy = self.retention_policies.get(
                    item_type, 
                    self.retention_policies["conversation_data"]  # Default
                )
                
                max_retention_days = retention_policy["retention_days"]
                anonymize_after_days = retention_policy["anonymize_after"]
                
                # Check retention compliance
                if age_days > max_retention_days:
                    compliance_results["non_compliant_items"] += 1
                    compliance_results["items_requiring_action"].append({
                        "item_id": item.get("id", "unknown"),
                        "issue": "retention_expired",
                        "age_days": age_days,
                        "max_retention": max_retention_days,
                        "action": "delete" if retention_policy["auto_delete"] else "manual_review"
                    })
                elif age_days > anonymize_after_days and not item.get("anonymization_applied", False):
                    compliance_results["items_requiring_action"].append({
                        "item_id": item.get("id", "unknown"),
                        "issue": "anonymization_required",
                        "age_days": age_days,
                        "anonymize_threshold": anonymize_after_days,
                        "action": "anonymize"
                    })
                else:
                    compliance_results["compliant_items"] += 1
                    
            except ValueError as e:
                compliance_results["non_compliant_items"] += 1
                compliance_results["items_requiring_action"].append({
                    "item_id": item.get("id", "unknown"),
                    "issue": "invalid_timestamp",
                    "error": str(e),
                    "action": "manual_review"
                })
        
        # Summarize required actions
        action_types = {}
        for item in compliance_results["items_requiring_action"]:
            action = item["action"]
            action_types[action] = action_types.get(action, 0) + 1
        
        compliance_results["actions_required"] = [
            {"action": action, "count": count}
            for action, count in action_types.items()
        ]
        
        # Calculate compliance rate
        compliance_results["compliance_rate"] = (
            compliance_results["compliant_items"] / max(compliance_results["total_items"], 1)
        )
        
        return compliance_results
    
    def _log_data_processing(self, operation: str, details: Dict[str, Any]):
        """
        Log data processing operation for privacy compliance.
        
        Args:
            operation: Type of operation performed
            details: Operation details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        
        self.data_processing_log.append(log_entry)
        
        # Keep only recent log entries (last 10000)
        if len(self.data_processing_log) > 10000:
            self.data_processing_log.pop(0)
        
        logger.info(f"Data processing logged: {operation}")
    
    def generate_privacy_report(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Generate privacy compliance report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Privacy compliance report
            
        TODO: Add detailed compliance metrics and recommendations
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Filter log entries by date range
        relevant_logs = [
            log for log in self.data_processing_log
            if start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date
        ]
        
        # Analyze operations
        operation_counts = {}
        pii_detection_stats = {"total_detections": 0, "types_detected": {}}
        
        for log in relevant_logs:
            operation = log["operation"]
            operation_counts[operation] = operation_counts.get(operation, 0) + 1
            
            if operation == "pii_redaction":
                pii_detection_stats["total_detections"] += 1
                for pii_type in log["details"].get("pii_types_found", []):
                    pii_detection_stats["types_detected"][pii_type] = (
                        pii_detection_stats["types_detected"].get(pii_type, 0) + 1
                    )
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "data_processing_operations": operation_counts,
            "pii_detection_statistics": pii_detection_stats,
            "total_processing_events": len(relevant_logs),
            "privacy_policies_active": len(self.retention_policies),
            "anonymization_enabled": settings.anonymize_logs,
            "compliance_features": [
                "PII detection and redaction",
                "Data retention policies",
                "Anonymization capabilities",
                "Processing audit logs",
                "Consent management (basic)"
            ],
            "recommendations": self._generate_privacy_recommendations(relevant_logs)
        }
    
    def _generate_privacy_recommendations(
        self,
        processing_logs: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate privacy improvement recommendations.
        
        Args:
            processing_logs: Recent processing logs
            
        Returns:
            List of privacy recommendations
        """
        recommendations = []
        
        # Check if PII detection is being used
        pii_operations = [log for log in processing_logs if log["operation"] == "pii_redaction"]
        if len(pii_operations) == 0:
            recommendations.append("Consider implementing regular PII scanning of stored data")
        
        # Check retention compliance
        if len(processing_logs) > 100:  # High activity
            recommendations.append("Review data retention policies for high-volume operations")
        
        # Check anonymization usage
        anonymization_ops = [
            log for log in processing_logs 
            if log["details"].get("anonymized", False)
        ]
        if len(anonymization_ops) / max(len(processing_logs), 1) < 0.5:
            recommendations.append("Consider increasing use of data anonymization")
        
        # Default recommendations
        recommendations.extend([
            "Regular privacy compliance audits recommended",
            "Consider implementing differential privacy for analytics",
            "Review and update consent management procedures"
        ])
        
        return recommendations
    
    def get_privacy_statistics(self) -> Dict[str, Any]:
        """
        Get privacy handler statistics.
        
        Returns:
            Dictionary with privacy statistics
        """
        return {
            "pii_patterns_loaded": sum(len(patterns) for patterns in self.pii_patterns.values()),
            "pii_types_supported": len(self.pii_patterns),
            "retention_policies": len(self.retention_policies),
            "processing_log_entries": len(self.data_processing_log),
            "anonymization_enabled": settings.anonymize_logs,
            "supported_data_classifications": [cls.value for cls in DataClassification],
            "supported_pii_types": [pii_type.value for pii_type in PIIType],
            "privacy_features": [
                "PII detection and redaction",
                "Data anonymization",
                "Retention policy management",
                "Processing audit logging",
                "Compliance reporting"
            ]
        }