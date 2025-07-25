"""
Central configuration management for Crisis Support & Mental Health Agent.

This module handles loading environment variables, API keys, and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Application Configuration
    app_name: str = Field("Crisis Support Mental Health Agent", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    host: str = Field("localhost", env="HOST")
    port: int = Field(8000, env="PORT")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./crisis_support.db", env="DATABASE_URL")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/app.log", env="LOG_FILE")
    
    # Safety Configuration
    crisis_escalation_enabled: bool = Field(True, env="CRISIS_ESCALATION_ENABLED")
    emergency_contact_number: str = Field("988", env="EMERGENCY_CONTACT_NUMBER")
    
    # Memory/Session Configuration
    max_conversation_length: int = Field(50, env="MAX_CONVERSATION_LENGTH")
    session_timeout_minutes: int = Field(30, env="SESSION_TIMEOUT_MINUTES")
    
    # Privacy Configuration
    anonymize_logs: bool = Field(True, env="ANONYMIZE_LOGS")
    data_retention_days: int = Field(30, env="DATA_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings


def validate_config() -> bool:
    """
    Validate that all required configuration is present.
    
    Returns:
        bool: True if configuration is valid, False otherwise
        
    TODO: Add more comprehensive validation for API keys, URLs, etc.
    """
    required_settings = [
        settings.gemini_api_key,
        settings.app_name,
    ]
    
    missing_settings = [setting for setting in required_settings if not setting]
    
    if missing_settings:
        print(f"Missing required settings: {missing_settings}")
        return False
    
    return True


def setup_logging():
    """
    Setup application logging configuration.
    
    TODO: Implement proper logging setup with file rotation, 
    privacy protection, and different log levels.
    """
    import logging
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


# Initialize logger
logger = setup_logging()