"""
Basic tests for Crisis Support & Mental Health Agent components

These tests verify the core functionality of the services and agents
without requiring external API calls.
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.safety_service import SafetyService, SafetyLevel
from src.services.memory_service import MemoryService, MemoryType, UserProfile
from src.config import Config


class TestSafetyService:
    """Test the SafetyService functionality"""
    
    @pytest.fixture
    def safety_service(self):
        """Create a SafetyService instance for testing"""
        return SafetyService()
    
    @pytest.mark.asyncio
    async def test_assess_safety_crisis_keywords(self, safety_service):
        """Test crisis detection with explicit keywords"""
        message = "I want to kill myself and end it all"
        assessment = await safety_service.assess_safety(message)
        
        assert assessment.level == SafetyLevel.IMMINENT
        assert assessment.requires_escalation == True
        assert "suicide_ideation" in assessment.risk_factors
        assert assessment.confidence >= 0.8
    
    @pytest.mark.asyncio
    async def test_assess_safety_self_harm(self, safety_service):
        """Test self-harm detection"""
        message = "I've been cutting myself and thinking about hurting myself more"
        assessment = await safety_service.assess_safety(message)
        
        assert assessment.level == SafetyLevel.DANGER
        assert assessment.requires_escalation == True
        assert "self_harm" in assessment.risk_factors
    
    @pytest.mark.asyncio
    async def test_assess_safety_moderate_risk(self, safety_service):
        """Test moderate risk detection"""
        message = "I feel hopeless and worthless, like nothing matters anymore"
        assessment = await safety_service.assess_safety(message)
        
        assert assessment.level == SafetyLevel.CONCERN
        assert assessment.requires_escalation == False
        assert "hopelessness" in assessment.risk_factors
    
    @pytest.mark.asyncio
    async def test_get_crisis_resources(self, safety_service):
        """Test crisis resources retrieval"""
        resources = await safety_service.get_crisis_resources()
        
        assert "national" in resources
        assert "suicide_prevention_lifeline" in resources["national"]
        assert resources["national"]["suicide_prevention_lifeline"]["phone"] == "988"
        assert "crisis_text_line" in resources["national"]
        assert "emergency_services" in resources["national"]
    
    @pytest.mark.asyncio
    async def test_initiate_escalation(self, safety_service):
        """Test escalation initiation"""
        # First create a safety assessment requiring escalation
        message = "I have a plan to end my life tonight"
        assessment = await safety_service.assess_safety(message)
        
        # Test escalation
        escalation_result = await safety_service.initiate_escalation(
            assessment, "test_session_123"
        )
        
        assert escalation_result["status"] == "escalated"
        assert "escalation_id" in escalation_result
        assert "contact_info" in escalation_result
        assert escalation_result["follow_up_required"] == True


class TestMemoryService:
    """Test the MemoryService functionality"""
    
    @pytest.fixture
    def memory_service(self):
        """Create a MemoryService instance for testing"""
        return MemoryService()
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_memory(self, memory_service):
        """Test basic memory storage and retrieval"""
        user_id = "test_user_001"
        session_id = "test_session_001"
        content = {"message": "Test conversation turn", "mood": "sad"}
        
        # Store memory
        memory_id = await memory_service.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=MemoryType.CONVERSATION,
            content=content
        )
        
        assert memory_id is not None
        assert memory_id in memory_service.memory_store
        
        # Retrieve conversation history
        history = await memory_service.retrieve_conversation_history(session_id)
        assert len(history) == 1
        assert history[0].content == content
        assert history[0].user_id == user_id
    
    @pytest.mark.asyncio
    async def test_user_profile_management(self, memory_service):
        """Test user profile creation and updates"""
        user_id = "test_user_002"
        
        # Initially no profile should exist
        profile = await memory_service.get_user_profile(user_id)
        assert profile is None
        
        # Create profile
        profile_data = {
            "preferences": {"communication_style": "gentle"},
            "therapeutic_goals": ["reduce anxiety", "improve sleep"],
            "coping_strategies": ["deep breathing", "journaling"],
            "trigger_words": ["failure", "worthless"]
        }
        
        updated_profile = await memory_service.update_user_profile(user_id, profile_data)
        
        assert updated_profile.user_id == user_id
        assert updated_profile.therapeutic_goals == ["reduce anxiety", "improve sleep"]
        assert "deep breathing" in updated_profile.coping_strategies
        
        # Retrieve profile
        retrieved_profile = await memory_service.get_user_profile(user_id)
        assert retrieved_profile is not None
        assert retrieved_profile.user_id == user_id
    
    @pytest.mark.asyncio
    async def test_search_memories(self, memory_service):
        """Test memory search functionality"""
        user_id = "test_user_003"
        session_id = "test_session_003"
        
        # Store some test memories
        await memory_service.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=MemoryType.CONVERSATION,
            content={"message": "I feel anxious about work", "emotion": "anxiety"}
        )
        
        await memory_service.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=MemoryType.CONVERSATION,
            content={"message": "My depression is getting worse", "emotion": "depression"}
        )
        
        # Search for anxiety-related memories
        results = await memory_service.search_memories(user_id, "anxious")
        assert len(results) == 1
        assert "anxious" in results[0].content["message"]
        
        # Search for depression-related memories
        results = await memory_service.search_memories(user_id, "depression")
        assert len(results) == 1
        assert "depression" in results[0].content["message"]
    
    @pytest.mark.asyncio
    async def test_therapeutic_progress_tracking(self, memory_service):
        """Test therapeutic progress tracking"""
        user_id = "test_user_004"
        session_id = "test_session_004"
        
        # Store therapeutic progress data
        progress_data = {
            "session_turn": 1,
            "mood_score": 6.5,
            "coping_strategies": ["breathing exercises"],
            "interventions_applied": ["cbt_cognitive_restructuring"],
            "user_engagement": 0.8
        }
        
        await memory_service.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=MemoryType.THERAPEUTIC_PROGRESS,
            content=progress_data
        )
        
        # Get progress summary
        progress = await memory_service.get_therapeutic_progress(user_id)
        
        assert progress["user_id"] == user_id
        assert progress["total_sessions"] >= 1
        assert "progress_metrics" in progress
        assert "insights" in progress
        assert "recommendations" in progress


class TestConfig:
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test configuration initialization with defaults"""
        config = Config()
        
        assert config.app_name == "Crisis Support & Mental Health Agent"
        assert config.safety.crisis_hotline == "988"
        assert config.safety.emergency_number == "911"
        assert config.gemini.model_name == "gemini-1.5-pro"
        assert config.session.session_timeout_minutes == 30
    
    def test_config_validation_missing_api_key(self):
        """Test configuration validation with missing API key"""
        config = Config()
        config.gemini.api_key = ""  # Simulate missing API key
        
        validation = config.validate()
        assert validation["valid"] == False
        assert any("GEMINI_API_KEY is required" in error for error in validation["errors"])
    
    def test_config_validation_invalid_thresholds(self):
        """Test configuration validation with invalid safety thresholds"""
        config = Config()
        config.gemini.api_key = "test_key"  # Set API key
        config.safety.high_risk_threshold = 0.9
        config.safety.crisis_threshold = 0.8  # Invalid: should be higher than high_risk_threshold
        
        validation = config.validate()
        assert validation["valid"] == False
        assert any("HIGH_RISK_THRESHOLD must be less than CRISIS_THRESHOLD" in error 
                  for error in validation["errors"])
    
    def test_get_crisis_resources(self):
        """Test crisis resources retrieval from config"""
        config = Config()
        resources = config.get_crisis_resources()
        
        assert resources["suicide_prevention_lifeline"] == "988"
        assert resources["emergency_services"] == "911"
        assert "crisis_text_line" in resources
        assert "online_chat" in resources


class TestIntegration:
    """Integration tests for multiple components working together"""
    
    @pytest.mark.asyncio
    async def test_services_integration(self):
        """Test that services can work together without API calls"""
        # Initialize services
        safety_service = SafetyService()
        memory_service = MemoryService()
        
        user_id = "integration_test_user"
        session_id = "integration_test_session"
        
        # Simulate a conversation turn with safety assessment
        message = "I'm feeling really down and hopeless lately"
        
        # Safety assessment
        safety_assessment = await safety_service.assess_safety(message)
        assert safety_assessment.level == SafetyLevel.CONCERN
        
        # Store conversation in memory
        conversation_data = {
            "user_message": message,
            "ai_response": "I hear that you're going through a difficult time...",
            "safety_assessment": {
                "level": safety_assessment.level.value,
                "risk_factors": safety_assessment.risk_factors,
                "confidence": safety_assessment.confidence
            }
        }
        
        memory_id = await memory_service.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=MemoryType.CONVERSATION,
            content=conversation_data
        )
        
        # Verify storage
        assert memory_id is not None
        
        # Retrieve and verify
        history = await memory_service.retrieve_conversation_history(session_id)
        assert len(history) == 1
        assert history[0].content["user_message"] == message
        assert history[0].content["safety_assessment"]["level"] == "concern"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])