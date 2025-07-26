"""
Configuration settings for Crisis Support & Mental Health Agent

This module provides centralized configuration management for the application,
including API keys, safety settings, and operational parameters.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class GeminiConfig:
    """Configuration for Gemini AI service"""
    api_key: str
    model_name: str = "gemini-1.5-pro"
    max_tokens: int = 1024
    temperature: float = 0.7
    timeout_seconds: int = 30


@dataclass
class SafetyConfig:
    """Configuration for safety protocols"""
    crisis_hotline: str = "988"
    emergency_number: str = "911"
    crisis_text_line: str = "741741"
    escalation_timeout_minutes: int = 5
    high_risk_threshold: float = 0.6
    crisis_threshold: float = 0.8


@dataclass
class SessionConfig:
    """Configuration for session management"""
    max_session_duration_hours: int = 2
    session_timeout_minutes: int = 30
    max_conversations_per_session: int = 100
    cleanup_interval_hours: int = 24


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    max_requests_per_minute: int = 60
    max_sessions_per_user: int = 5
    burst_limit: int = 10


class Config:
    """
    Main configuration class for the Crisis Support & Mental Health Agent
    
    Provides centralized access to all configuration settings with
    environment variable support and sensible defaults.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        
        # API Configuration
        self.gemini = GeminiConfig(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1024")),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            timeout_seconds=int(os.getenv("GEMINI_TIMEOUT", "30"))
        )
        
        # Safety Configuration
        self.safety = SafetyConfig(
            crisis_hotline=os.getenv("CRISIS_HOTLINE", "988"),
            emergency_number=os.getenv("EMERGENCY_CONTACT", "911"),
            crisis_text_line=os.getenv("CRISIS_TEXT_LINE", "741741"),
            escalation_timeout_minutes=int(os.getenv("ESCALATION_TIMEOUT", "5")),
            high_risk_threshold=float(os.getenv("HIGH_RISK_THRESHOLD", "0.6")),
            crisis_threshold=float(os.getenv("CRISIS_THRESHOLD", "0.8"))
        )
        
        # Session Configuration
        self.session = SessionConfig(
            max_session_duration_hours=int(os.getenv("MAX_SESSION_HOURS", "2")),
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT", "30")),
            max_conversations_per_session=int(os.getenv("MAX_CONVERSATIONS", "100")),
            cleanup_interval_hours=int(os.getenv("CLEANUP_INTERVAL", "24"))
        )
        
        # Rate Limiting Configuration
        self.rate_limit = RateLimitConfig(
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60")),
            max_sessions_per_user=int(os.getenv("MAX_SESSIONS_PER_USER", "5")),
            burst_limit=int(os.getenv("BURST_LIMIT", "10"))
        )
        
        # Application Configuration
        self.app_name = os.getenv("APP_NAME", "Crisis Support & Mental Health Agent")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        
        # Database Configuration (for future use)
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///mental_health_agent.db")
        
        # Feature Flags
        self.enable_crisis_detection = os.getenv("ENABLE_CRISIS_DETECTION", "true").lower() == "true"
        self.enable_memory_persistence = os.getenv("ENABLE_MEMORY_PERSISTENCE", "false").lower() == "true"
        self.enable_analytics = os.getenv("ENABLE_ANALYTICS", "false").lower() == "true"
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results
        
        Returns:
            Dict with validation status and any errors
        """
        errors = []
        warnings = []
        
        # Validate required API keys
        if not self.gemini.api_key:
            errors.append("GEMINI_API_KEY is required")
        
        # Validate safety thresholds
        if self.safety.high_risk_threshold >= self.safety.crisis_threshold:
            errors.append("HIGH_RISK_THRESHOLD must be less than CRISIS_THRESHOLD")
        
        if self.safety.crisis_threshold > 1.0 or self.safety.crisis_threshold < 0.0:
            errors.append("CRISIS_THRESHOLD must be between 0.0 and 1.0")
        
        # Validate session settings
        if self.session.session_timeout_minutes <= 0:
            errors.append("SESSION_TIMEOUT must be positive")
        
        if self.session.max_session_duration_hours <= 0:
            errors.append("MAX_SESSION_HOURS must be positive")
        
        # Validate rate limiting
        if self.rate_limit.max_requests_per_minute <= 0:
            errors.append("MAX_REQUESTS_PER_MINUTE must be positive")
        
        # Check for development environment warnings
        if self.environment == "development":
            if self.secret_key == "dev-secret-key-change-in-production":
                warnings.append("Using default secret key - change for production")
        
        if self.environment == "production":
            if not self.enable_memory_persistence:
                warnings.append("Memory persistence disabled in production")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_crisis_resources(self) -> Dict[str, str]:
        """Get crisis resources with current configuration"""
        return {
            "suicide_prevention_lifeline": self.safety.crisis_hotline,
            "crisis_text_line": f"Text HOME to {self.safety.crisis_text_line}",
            "emergency_services": self.safety.emergency_number,
            "online_chat": "suicidepreventionlifeline.org/chat",
            "veterans_crisis_line": "1-800-273-8255 (Press 1)"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "log_level": self.log_level,
            "gemini": {
                "model_name": self.gemini.model_name,
                "max_tokens": self.gemini.max_tokens,
                "temperature": self.gemini.temperature,
                "timeout_seconds": self.gemini.timeout_seconds,
                "api_key_configured": bool(self.gemini.api_key)
            },
            "safety": {
                "crisis_hotline": self.safety.crisis_hotline,
                "emergency_number": self.safety.emergency_number,
                "crisis_text_line": self.safety.crisis_text_line,
                "high_risk_threshold": self.safety.high_risk_threshold,
                "crisis_threshold": self.safety.crisis_threshold
            },
            "session": {
                "max_session_duration_hours": self.session.max_session_duration_hours,
                "session_timeout_minutes": self.session.session_timeout_minutes,
                "max_conversations_per_session": self.session.max_conversations_per_session
            },
            "rate_limit": {
                "max_requests_per_minute": self.rate_limit.max_requests_per_minute,
                "max_sessions_per_user": self.rate_limit.max_sessions_per_user,
                "burst_limit": self.rate_limit.burst_limit
            },
            "features": {
                "crisis_detection": self.enable_crisis_detection,
                "memory_persistence": self.enable_memory_persistence,
                "analytics": self.enable_analytics
            }
        }


# Global configuration instance
config = Config()


# Convenience function for getting configuration
def get_config() -> Config:
    """Get the global configuration instance"""
    return config