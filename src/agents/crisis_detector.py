"""
Pattern-based crisis keyword detector for Crisis Support & Mental Health Agent.

This module provides specialized crisis detection using pattern matching,
keyword analysis, and contextual assessment to identify potential mental
health emergencies.
"""

import json
import re
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path
from dataclasses import dataclass

from config import get_settings, logger

settings = get_settings()


@dataclass
class CrisisMatch:
    """Data class for crisis detection matches."""
    keyword: str
    pattern_type: str
    severity: str
    confidence: float
    context: str


class CrisisDetector:
    """
    Specialized crisis detection using pattern matching and keyword analysis.
    
    This class focuses specifically on detecting crisis situations through
    linguistic patterns, keywords, and contextual indicators.
    """
    
    def __init__(self):
        """Initialize crisis detector with patterns and configurations."""
        self.crisis_patterns = self._load_crisis_patterns()
        self.context_modifiers = self._load_context_modifiers()
        self.false_positive_filters = self._load_false_positive_filters()
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = self._compile_patterns()
        
        logger.info("CrisisDetector initialized")
    
    def _load_crisis_patterns(self) -> Dict[str, Any]:
        """
        Load crisis detection patterns from JSON file.
        
        Returns:
            Dictionary containing crisis patterns
            
        TODO: Implement pattern versioning and A/B testing
        """
        try:
            patterns_file = Path("src/data/crisis_patterns.json")
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    return data.get("crisis_patterns", {})
        except Exception as e:
            logger.error(f"Error loading crisis patterns: {str(e)}")
        
        return self._get_default_crisis_patterns()
    
    def _get_default_crisis_patterns(self) -> Dict[str, Any]:
        """Get default crisis patterns when file loading fails."""
        return {
            "immediate_risk": {
                "keywords": [
                    "kill myself", "end my life", "suicide plan", "take my life",
                    "going to die", "want to die", "ready to die", "can't go on", "end it all"
                ],
                "severity": "critical",
                "requires_immediate_action": True,
                "confidence_threshold": 0.9
            },
            "suicidal_ideation": {
                "keywords": [
                    "suicide", "better off dead", "don't want to live",
                    "life isn't worth", "no reason to live", "hopeless",
                    "everyone would be better", "burden to everyone"
                ],
                "severity": "high",
                "requires_immediate_action": True,
                "confidence_threshold": 0.8
            },
            "self_harm": {
                "keywords": [
                    "cut myself", "hurt myself", "self harm", "cutting",
                    "burn myself", "scratch myself", "hit myself", "punish myself", "deserve pain"
                ],
                "severity": "high",
                "requires_immediate_action": False,
                "confidence_threshold": 0.8
            },
            "substance_crisis": {
                "keywords": [
                    "overdose", "too many pills", "drinking too much",
                    "can't stop using", "addicted", "substance problem",
                    "drugs and alcohol", "using heavily"
                ],
                "severity": "high",
                "requires_immediate_action": False,
                "confidence_threshold": 0.7
            },
            "violence_risk": {
                "keywords": [
                    "hurt someone", "kill them", "violent thoughts",
                    "can't control anger", "want to hurt", "rage",
                    "weapon", "gun", "knife", "violent plan"
                ],
                "severity": "critical",
                "requires_immediate_action": True,
                "confidence_threshold": 0.9
            },
            "severe_distress": {
                "keywords": [
                    "can't cope", "falling apart", "losing it",
                    "panic attack", "can't breathe", "heart racing",
                    "going crazy", "losing my mind", "insane"
                ],
                "severity": "medium",
                "requires_immediate_action": False,
                "confidence_threshold": 0.6
            }
        }
    
    def _load_context_modifiers(self) -> Dict[str, float]:
        """
        Load context modifiers that affect crisis detection confidence.
        
        Returns:
            Dictionary mapping context indicators to confidence modifiers
            
        TODO: Implement machine learning-based context understanding
        """
        return {
            # Amplifiers (increase crisis confidence)
            "tonight": 1.3,
            "today": 1.2,
            "right now": 1.4,
            "immediately": 1.3,
            "planning": 1.5,
            "decided": 1.4,
            "ready": 1.3,
            
            # Diminishers (decrease crisis confidence)
            "sometimes": 0.7,
            "maybe": 0.6,
            "thinking about": 0.8,
            "wondering": 0.7,
            "if": 0.8,
            "hypothetical": 0.5,
            "in a movie": 0.3,
            "friend": 0.6
        }
    
    def _load_false_positive_filters(self) -> List[str]:
        """
        Load patterns that indicate false positives.
        
        Returns:
            List of false positive patterns
            
        TODO: Expand false positive detection
        """
        return [
            r"\b(in a book|in a movie|on tv|video game)\b",
            r"\b(character|fictional|story|novel)\b",
            r"\b(not me|someone else|friend|relative)\b",
            r"\b(would never|don't want to|won't)\b"
        ]
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """
        Compile regex patterns for efficient matching.
        
        Returns:
            Dictionary of compiled patterns
        """
        compiled = {}
        
        for pattern_type, pattern_info in self.crisis_patterns.items():
            compiled[pattern_type] = []
            # Use "keywords" from JSON which are treated as literal patterns
            keywords = pattern_info.get("keywords", [])
            for keyword in keywords:
                try:
                    # Convert keywords to regex patterns for word boundary matching
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    compiled[pattern_type].append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    logger.error(f"Invalid keyword pattern '{keyword}': {str(e)}")
        
        return compiled
    
    def detect_crisis_patterns(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect crisis patterns in a message.
        
        Args:
            message: User message to analyze
            context: Additional context for detection
            
        Returns:
            Dictionary with crisis detection results
            
        TODO: Implement multi-message pattern detection
        TODO: Add conversation history analysis
        """
        try:
            # Initialize detection results
            results = {
                "crisis_detected": False,
                "crisis_type": None,
                "severity": "safe",
                "confidence": 0.0,
                "matches": [],
                "immediate_action_required": False,
                "recommended_response": "continue_conversation",
                "patterns_triggered": []
            }
            
            # Normalize message
            normalized_message = self._normalize_message(message)
            
            # Check for false positives first
            if self._is_false_positive(normalized_message):
                results["false_positive_detected"] = True
                logger.info("False positive detected in crisis analysis")
                return results
            
            # Detect crisis patterns
            all_matches = []
            highest_severity_score = 0
            severity_mapping = {"safe": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
            
            for pattern_type, compiled_patterns in self.compiled_patterns.items():
                pattern_info = self.crisis_patterns[pattern_type]
                matches = self._find_pattern_matches(
                    normalized_message, 
                    compiled_patterns, 
                    pattern_type, 
                    pattern_info
                )
                
                if matches:
                    all_matches.extend(matches)
                    results["patterns_triggered"].append(pattern_type)
                    
                    # Update severity to highest found
                    pattern_severity = pattern_info["severity"]
                    severity_score = severity_mapping[pattern_severity]
                    
                    if severity_score > highest_severity_score:
                        highest_severity_score = severity_score
                        results["crisis_type"] = pattern_type
                        results["severity"] = pattern_severity
                        results["immediate_action_required"] = pattern_info.get(
                            "requires_immediate_action", False
                        )
            
            # Calculate overall confidence
            if all_matches:
                results["confidence"] = self._calculate_confidence(
                    all_matches, normalized_message, context
                )
                results["crisis_detected"] = results["confidence"] > 0.5
                results["matches"] = [
                    {
                        "keyword": match.keyword,
                        "pattern_type": match.pattern_type,
                        "confidence": match.confidence,
                        "context": match.context[:50] + "..." if len(match.context) > 50 else match.context
                    }
                    for match in all_matches
                ]
            
            # Determine recommended response
            results["recommended_response"] = self._get_recommended_response(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in crisis pattern detection: {str(e)}")
            return self._get_safe_default_result()
    
    def _normalize_message(self, message: str) -> str:
        """
        Normalize message for pattern matching.
        
        Args:
            message: Raw message
            
        Returns:
            Normalized message
        """
        # Convert to lowercase
        normalized = message.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Handle common contractions and variations
        contractions = {
            "i'm": "i am",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "isn't": "is not",
            "aren't": "are not"
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        return normalized
    
    def _is_false_positive(self, message: str) -> bool:
        """
        Check if message contains false positive indicators.
        
        Args:
            message: Normalized message
            
        Returns:
            True if false positive detected
        """
        for fp_pattern in self.false_positive_filters:
            if re.search(fp_pattern, message, re.IGNORECASE):
                return True
        return False
    
    def _find_pattern_matches(
        self, 
        message: str, 
        patterns: List[re.Pattern], 
        pattern_type: str, 
        pattern_info: Dict[str, Any]
    ) -> List[CrisisMatch]:
        """
        Find matches for a specific pattern type.
        
        Args:
            message: Normalized message
            patterns: Compiled regex patterns
            pattern_type: Type of crisis pattern
            pattern_info: Pattern configuration
            
        Returns:
            List of crisis matches
        """
        matches = []
        
        for pattern in patterns:
            for match in pattern.finditer(message):
                # Extract context around match
                start = max(0, match.start() - 20)
                end = min(len(message), match.end() + 20)
                context = message[start:end]
                
                # Calculate base confidence
                base_confidence = pattern_info.get("confidence_threshold", 0.7)
                
                # Apply context modifiers
                modified_confidence = self._apply_context_modifiers(
                    context, base_confidence
                )
                
                matches.append(CrisisMatch(
                    keyword=match.group(),
                    pattern_type=pattern_type,
                    severity=pattern_info["severity"],
                    confidence=modified_confidence,
                    context=context
                ))
        
        return matches
    
    def _apply_context_modifiers(self, context: str, base_confidence: float) -> float:
        """
        Apply context modifiers to adjust confidence.
        
        Args:
            context: Context around the match
            base_confidence: Base confidence score
            
        Returns:
            Modified confidence score
        """
        modified_confidence = base_confidence
        
        for modifier_phrase, modifier_value in self.context_modifiers.items():
            if modifier_phrase in context:
                modified_confidence *= modifier_value
        
        # Ensure confidence stays within bounds
        return max(0.0, min(1.0, modified_confidence))
    
    def _calculate_confidence(
        self, 
        matches: List[CrisisMatch], 
        message: str, 
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence in crisis detection.
        
        Args:
            matches: List of pattern matches
            message: Full message text
            context: Additional context
            
        Returns:
            Overall confidence score
        """
        if not matches:
            return 0.0
        
        # Get highest individual confidence
        max_confidence = max(match.confidence for match in matches)
        
        # Boost confidence for multiple matches
        num_matches = len(matches)
        if num_matches > 1:
            # Boost by up to 20% for multiple matches
            boost = min(0.2, (num_matches - 1) * 0.05)
            max_confidence += boost
        
        # Consider message length (very short messages might be less reliable)
        if len(message.split()) < 3:
            max_confidence *= 0.8
        
        # Ensure confidence stays within bounds
        return max(0.0, min(1.0, max_confidence))
    
    def _get_recommended_response(self, results: Dict[str, Any]) -> str:
        """
        Get recommended response based on detection results.
        
        Args:
            results: Crisis detection results
            
        Returns:
            Recommended response type
        """
        if not results["crisis_detected"]:
            return "continue_conversation"
        
        if results["immediate_action_required"]:
            return "immediate_intervention"
        
        severity = results["severity"]
        if severity == "critical":
            return "crisis_protocol"
        elif severity == "high":
            return "safety_planning"
        elif severity == "medium":
            return "enhanced_support"
        else:
            return "supportive_response"
    
    def _get_safe_default_result(self) -> Dict[str, Any]:
        """Get safe default result when detection fails."""
        return {
            "crisis_detected": False,
            "crisis_type": None,
            "severity": "safe",
            "confidence": 0.0,
            "matches": [],
            "immediate_action_required": False,
            "recommended_response": "continue_conversation",
            "patterns_triggered": [],
            "error": "Detection failed, defaulting to safe"
        }
    
    def add_custom_pattern(
        self, 
        pattern_type: str, 
        patterns: List[str], 
        severity: str, 
        immediate_action: bool = False
    ) -> bool:
        """
        Add custom crisis detection pattern.
        
        Args:
            pattern_type: Type identifier for the pattern
            patterns: List of regex patterns
            severity: Severity level (safe, low, medium, high, critical)
            immediate_action: Whether immediate action is required
            
        Returns:
            Success status
            
        TODO: Add pattern validation and testing
        """
        try:
            # Validate inputs
            valid_severities = ["safe", "low", "medium", "high", "critical"]
            if severity not in valid_severities:
                logger.error(f"Invalid severity level: {severity}")
                return False
            
            # Test pattern compilation
            compiled_test = []
            for pattern in patterns:
                try:
                    compiled_test.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{pattern}': {str(e)}")
                    return False
            
            # Add to patterns
            self.crisis_patterns[pattern_type] = {
                "patterns": patterns,
                "severity": severity,
                "requires_immediate_action": immediate_action,
                "confidence_threshold": 0.7  # Default threshold
            }
            
            # Update compiled patterns
            self.compiled_patterns[pattern_type] = compiled_test
            
            logger.info(f"Added custom crisis pattern: {pattern_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom pattern: {str(e)}")
            return False
    
    def test_pattern_detection(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test crisis pattern detection with test cases.
        
        Args:
            test_cases: List of test cases with message and expected results
            
        Returns:
            Test results summary
            
        TODO: Implement comprehensive testing framework
        """
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for i, test_case in enumerate(test_cases):
            message = test_case["message"]
            expected_crisis = test_case.get("expected_crisis", False)
            expected_severity = test_case.get("expected_severity", "safe")
            
            detection_result = self.detect_crisis_patterns(message)
            
            # Check if detection matches expectations
            crisis_match = detection_result["crisis_detected"] == expected_crisis
            severity_match = detection_result["severity"] == expected_severity
            
            if crisis_match and severity_match:
                results["passed"] += 1
                test_status = "PASS"
            else:
                results["failed"] += 1
                test_status = "FAIL"
            
            results["details"].append({
                "test_id": i + 1,
                "message": message[:50] + "..." if len(message) > 50 else message,
                "expected_crisis": expected_crisis,
                "detected_crisis": detection_result["crisis_detected"],
                "expected_severity": expected_severity,
                "detected_severity": detection_result["severity"],
                "confidence": detection_result["confidence"],
                "status": test_status
            })
        
        results["accuracy"] = results["passed"] / results["total_tests"] if results["total_tests"] > 0 else 0
        
        logger.info(f"Pattern detection test completed: {results['accuracy']:.2%} accuracy")
        return results
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about pattern usage and effectiveness.
        
        Returns:
            Dictionary with pattern statistics
            
        TODO: Implement pattern effectiveness tracking
        """
        return {
            "total_patterns": len(self.crisis_patterns),
            "pattern_types": list(self.crisis_patterns.keys()),
            "severity_distribution": {
                severity: len([p for p in self.crisis_patterns.values() if p["severity"] == severity])
                for severity in ["safe", "low", "medium", "high", "critical"]
            },
            "immediate_action_patterns": len([
                p for p in self.crisis_patterns.values() 
                if p.get("requires_immediate_action", False)
            ])
        }