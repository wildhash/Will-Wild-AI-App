import logging
import json
from typing import List, Dict, Any, Optional
from models.conversation import ConversationContext

logger = logging.getLogger(__name__)


class ResourceMatchingService:
    """
    MVP Resource Matching Service that recommends mental health resources
    based on chat context, mood, and risk assessment.
    
    TODO: Future enhancements for production:
    - Integration with live web search APIs (Google Custom Search, etc.)
    - Advanced AI-powered ranking with Gemini API
    - Geo-location based resource filtering
    - User preference learning and personalization
    - Real-time resource availability checking
    - Community-sourced resource validation
    """
    
    def __init__(self):
        """Initialize the resource matching service with hardcoded resources."""
        self._resources = self._load_hardcoded_resources()
        logger.info("ResourceMatchingService initialized with hardcoded resource database")
    
    def _load_hardcoded_resources(self) -> List[Dict[str, str]]:
        """
        Load hardcoded mental health resources for MVP demonstration.
        
        TODO: Replace with dynamic resource loading from:
        - External APIs (Psychology Today, SAMHSA, etc.)
        - Database with admin-managed resources
        - Community-contributed resource database
        
        Returns:
            List of resource dictionaries with name, link, description
        """
        return [
            {
                "name": "Crisis Text Line",
                "link": "https://www.crisistextline.org/",
                "description": "Free, 24/7 support via text. Text HOME to 741741 to connect with a crisis counselor."
            },
            {
                "name": "National Suicide Prevention Lifeline",
                "link": "https://988lifeline.org/",
                "description": "24/7 crisis support. Call or text 988 for immediate help with suicidal thoughts or emotional distress."
            },
            {
                "name": "BetterHelp Online Therapy",
                "link": "https://www.betterhelp.com/",
                "description": "Professional online counseling and therapy with licensed therapists. Accessible and affordable mental health care."
            },
            {
                "name": "Anxiety and Depression Association of America",
                "link": "https://adaa.org/",
                "description": "Educational resources, self-help tools, and treatment finder for anxiety and depression disorders."
            },
            {
                "name": "SAMHSA Treatment Locator",
                "link": "https://findtreatment.samhsa.gov/",
                "description": "Find mental health and substance abuse treatment facilities near you with insurance and payment options."
            },
            {
                "name": "National Alliance on Mental Illness (NAMI)",
                "link": "https://www.nami.org/",
                "description": "Mental health education, support groups, and advocacy. Comprehensive resources for individuals and families."
            },
            {
                "name": "Mindfulness and Meditation Apps",
                "link": "https://www.headspace.com/",
                "description": "Guided meditation and mindfulness exercises to help manage stress, anxiety, and improve mental well-being."
            },
            {
                "name": "Mental Health America",
                "link": "https://www.mhanational.org/",
                "description": "Mental health screening tools, educational resources, and advocacy for mental health awareness."
            },
            {
                "name": "Warmlines Directory",
                "link": "https://screening.mhanational.org/content/need-talk-someone-warmlines/",
                "description": "Non-crisis peer support lines for when you need someone to talk to but it's not an emergency."
            },
            {
                "name": "Employee Assistance Programs (EAP)",
                "link": "https://www.dol.gov/general/workplacerights/eap",
                "description": "Workplace mental health support programs. Check with your employer for confidential counseling services."
            },
            {
                "name": "Psychology Today Therapist Finder",
                "link": "https://www.psychologytoday.com/us/therapists",
                "description": "Find licensed therapists, psychiatrists, and treatment centers in your area with detailed profiles and specialties."
            },
            {
                "name": "Veterans Crisis Line",
                "link": "https://www.veteranscrisisline.net/",
                "description": "Specialized crisis support for veterans and their families. Call 988, Press 1 or text 838255."
            }
        ]
    
    def get_matched_resources(self, 
                            user_id: str, 
                            context: Optional[ConversationContext] = None,
                            risk_level: str = "low") -> List[Dict[str, str]]:
        """
        Get resources matched to user's conversation context and risk level.
        
        TODO: Enhance matching algorithm with:
        - NLP sentiment analysis for better mood detection
        - ML-based resource ranking based on user outcomes
        - Real-time resource quality scoring
        - Personalized recommendations based on user history
        
        Args:
            user_id: Unique identifier for the user
            context: Conversation context from MemoryService
            risk_level: Current risk assessment (low, medium, high, critical)
            
        Returns:
            List of matched resources ranked by relevance
        """
        try:
            matched_resources = []
            all_keywords = []
            
            # Extract keywords from conversation context
            if context and context.messages:
                conversation_text = " ".join([msg.content.lower() for msg in context.messages[-5:]])  # Last 5 messages
                all_keywords.extend(self._extract_keywords(conversation_text))
            
            # Add risk-level specific resources
            if risk_level in ["high", "critical"]:
                # Prioritize crisis resources for high-risk users
                crisis_resources = [r for r in self._resources if self._is_crisis_resource(r)]
                matched_resources.extend(crisis_resources)
                logger.info(f"Added {len(crisis_resources)} crisis resources for high-risk user {user_id}")
            
            # Add general resources based on keywords
            keyword_matched = self._match_by_keywords(all_keywords, risk_level)
            matched_resources.extend(keyword_matched)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_resources = []
            for resource in matched_resources:
                if resource["name"] not in seen:
                    unique_resources.append(resource)
                    seen.add(resource["name"])
            
            # Limit to top 8 resources for better UX
            final_resources = unique_resources[:8]
            
            logger.info(f"Matched {len(final_resources)} resources for user {user_id} "
                       f"(risk_level: {risk_level}, keywords: {len(all_keywords)})")
            
            return final_resources
            
        except Exception as e:
            logger.error(f"Error matching resources for user {user_id}: {str(e)}")
            # Return default safe resources on error
            return self._get_default_resources()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from conversation text for resource matching.
        
        TODO: Replace with advanced NLP:
        - Named Entity Recognition (NER) for specific conditions
        - Sentiment analysis for emotional state detection
        - Topic modeling for conversation theme identification
        
        Args:
            text: Conversation text to analyze
            
        Returns:
            List of extracted keywords
        """
        # Simple keyword extraction for MVP
        anxiety_keywords = ["anxious", "anxiety", "worried", "panic", "stress", "nervous", "fear"]
        depression_keywords = ["sad", "depressed", "hopeless", "empty", "worthless", "down", "grief"]
        crisis_keywords = ["suicide", "kill", "die", "hurt", "harm", "end", "give up"]
        relationship_keywords = ["relationship", "family", "partner", "marriage", "divorce", "alone"]
        work_keywords = ["work", "job", "career", "boss", "workplace", "burnout", "unemployed"]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in anxiety_keywords + depression_keywords + crisis_keywords + relationship_keywords + work_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _is_crisis_resource(self, resource: Dict[str, str]) -> bool:
        """Check if a resource is crisis-specific."""
        crisis_names = ["crisis", "suicide", "lifeline", "emergency", "veterans crisis"]
        return any(crisis_term in resource["name"].lower() for crisis_term in crisis_names)
    
    def _match_by_keywords(self, keywords: List[str], risk_level: str) -> List[Dict[str, str]]:
        """
        Match resources based on extracted keywords.
        
        TODO: Implement sophisticated matching:
        - Weighted keyword scoring
        - Context-aware resource ranking
        - User feedback integration for improved matching
        
        Args:
            keywords: List of extracted keywords
            risk_level: Current risk assessment
            
        Returns:
            List of matched resources
        """
        matched = []
        
        # Crisis keywords get crisis resources
        crisis_keywords = ["suicide", "kill", "die", "hurt", "harm", "end", "give up"]
        if any(k in crisis_keywords for k in keywords) or risk_level in ["high", "critical"]:
            matched.extend([r for r in self._resources if self._is_crisis_resource(r)])
        
        # Anxiety keywords
        anxiety_keywords = ["anxious", "anxiety", "worried", "panic", "stress", "nervous", "fear"]
        if any(k in anxiety_keywords for k in keywords):
            matched.extend([r for r in self._resources if "anxiety" in r["description"].lower() or "mindfulness" in r["name"].lower()])
        
        # Depression keywords
        depression_keywords = ["sad", "depressed", "hopeless", "empty", "worthless", "down", "grief"]
        if any(k in depression_keywords for k in keywords):
            matched.extend([r for r in self._resources if "depression" in r["description"].lower() or "therapy" in r["name"].lower()])
        
        # Always include general resources
        general_resources = [r for r in self._resources if not self._is_crisis_resource(r)][:3]
        matched.extend(general_resources)
        
        return matched
    
    def _get_default_resources(self) -> List[Dict[str, str]]:
        """
        Get default resources when matching fails.
        
        Returns:
            List of default safe resources
        """
        return [
            {
                "name": "Crisis Text Line",
                "link": "https://www.crisistextline.org/",
                "description": "Free, 24/7 support via text. Text HOME to 741741 to connect with a crisis counselor."
            },
            {
                "name": "National Suicide Prevention Lifeline", 
                "link": "https://988lifeline.org/",
                "description": "24/7 crisis support. Call or text 988 for immediate help with suicidal thoughts or emotional distress."
            },
            {
                "name": "BetterHelp Online Therapy",
                "link": "https://www.betterhelp.com/",
                "description": "Professional online counseling and therapy with licensed therapists."
            }
        ]
    
    def get_resource_count(self) -> int:
        """Get total number of available resources."""
        return len(self._resources)