"""
Location-based provider and resource matcher for Crisis Support & Mental Health Agent.

This module provides resource matching based on user location, crisis type,
insurance, and other factors to connect users with appropriate mental health
services and support resources.
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from config import get_settings, logger

settings = get_settings()


@dataclass
class Resource:
    """Data class for mental health resources."""
    id: str
    name: str
    type: str
    description: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability: str = "unknown"
    cost: str = "unknown"
    insurance_accepted: List[str] = None
    languages: List[str] = None
    specialties: List[str] = None
    crisis_capable: bool = False
    rating: Optional[float] = None


class ResourceMatcher:
    """
    Location-based resource matcher for mental health services.
    
    This class helps match users with appropriate mental health resources
    based on their location, needs, and preferences.
    """
    
    def __init__(self):
        """Initialize resource matcher with resource data."""
        self.resources = self._load_resources()
        self.providers = self._load_providers()
        self.emergency_resources = self._load_emergency_resources()
        
        # Resource type mappings
        self.crisis_type_mapping = self._get_crisis_type_mapping()
        
        logger.info("ResourceMatcher initialized")
    
    def _load_resources(self) -> List[Resource]:
        """
        Load mental health resources from JSON file.
        
        Returns:
            List of Resource objects
            
        TODO: Implement dynamic resource loading from APIs
        TODO: Add resource validation and updates
        """
        try:
            resources_file = Path("src/data/safety_resources.json")
            if resources_file.exists():
                with open(resources_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_resource(item) for item in data.get("resources", [])]
        except Exception as e:
            logger.error(f"Error loading safety resources: {str(e)}")
        
        return self._get_default_resources()
    
    def _load_providers(self) -> List[Resource]:
        """
        Load therapy providers from JSON file.
        
        Returns:
            List of provider Resource objects
            
        TODO: Integrate with provider directories APIs
        """
        try:
            providers_file = Path("src/data/therapy_providers.json")
            if providers_file.exists():
                with open(providers_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_resource(item) for item in data.get("providers", [])]
        except Exception as e:
            logger.error(f"Error loading therapy providers: {str(e)}")
        
        return self._get_default_providers()
    
    def _load_emergency_resources(self) -> List[Resource]:
        """
        Load emergency mental health resources.
        
        Returns:
            List of emergency Resource objects
        """
        return [
            Resource(
                id="988_lifeline",
                name="988 Suicide & Crisis Lifeline",
                type="crisis_hotline",
                description="24/7 free and confidential support for people in distress",
                phone="988",
                website="https://988lifeline.org",
                availability="24/7",
                cost="free",
                languages=["English", "Spanish"],
                crisis_capable=True
            ),
            Resource(
                id="crisis_text_line",
                name="Crisis Text Line",
                type="crisis_text",
                description="Free, 24/7 crisis counseling via text message",
                phone="741741",
                website="https://crisistextline.org",
                availability="24/7",
                cost="free",
                crisis_capable=True
            ),
            Resource(
                id="emergency_services",
                name="Emergency Services",
                type="emergency",
                description="Call for immediate life-threatening emergencies",
                phone="911",
                availability="24/7",
                cost="varies",
                crisis_capable=True
            )
        ]
    
    def _dict_to_resource(self, data: Dict[str, Any]) -> Resource:
        """Convert dictionary to Resource object."""
        return Resource(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            description=data.get("description", ""),
            phone=data.get("phone"),
            website=data.get("website"),
            address=data.get("address"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            availability=data.get("availability", "unknown"),
            cost=data.get("cost", "unknown"),
            insurance_accepted=data.get("insurance_accepted", []),
            languages=data.get("languages", ["English"]),
            specialties=data.get("specialties", []),
            crisis_capable=data.get("crisis_capable", False),
            rating=data.get("rating")
        )
    
    def _get_default_resources(self) -> List[Resource]:
        """Get default resources when file loading fails."""
        return [
            Resource(
                id="nami_helpline",
                name="NAMI HelpLine",
                type="support_helpline",
                description="Information, referrals and support for mental health concerns",
                phone="1-800-950-6264",
                website="https://nami.org/help",
                availability="Mon-Fri 10am-6pm ET",
                cost="free",
                languages=["English"],
                specialties=["general mental health", "family support"]
            ),
            Resource(
                id="samhsa_helpline",
                name="SAMHSA National Helpline",
                type="treatment_referral",
                description="Treatment referral and information service",
                phone="1-800-662-4357",
                website="https://samhsa.gov/find-help/national-helpline",
                availability="24/7",
                cost="free",
                languages=["English", "Spanish"],
                specialties=["substance abuse", "mental health treatment"]
            )
        ]
    
    def _get_default_providers(self) -> List[Resource]:
        """Get default providers when file loading fails."""
        return [
            Resource(
                id="betterhelp",
                name="BetterHelp Online Therapy",
                type="online_therapy",
                description="Online therapy platform with licensed therapists",
                website="https://betterhelp.com",
                availability="flexible scheduling",
                cost="$60-90/week",
                insurance_accepted=["some plans"],
                languages=["English", "Spanish"],
                specialties=["anxiety", "depression", "relationships", "trauma"]
            ),
            Resource(
                id="psychology_today",
                name="Psychology Today Directory",
                type="provider_directory",
                description="Directory of mental health professionals",
                website="https://psychologytoday.com",
                availability="search tool",
                cost="varies by provider",
                specialties=["all specialties"]
            )
        ]
    
    def _get_crisis_type_mapping(self) -> Dict[str, List[str]]:
        """
        Get mapping of crisis types to relevant resource types.
        
        Returns:
            Dictionary mapping crisis types to resource types
        """
        return {
            "suicide_risk": ["crisis_hotline", "emergency", "crisis_text"],
            "self_harm": ["crisis_hotline", "crisis_text", "mental_health_professional"],
            "substance_abuse": ["treatment_referral", "crisis_hotline", "addiction_services"],
            "violence_risk": ["emergency", "crisis_hotline"],
            "severe_depression": ["mental_health_professional", "support_helpline"],
            "panic_anxiety": ["crisis_text", "mental_health_professional", "support_helpline"]
        }
    
    def find_relevant_resources(
        self, 
        message: str, 
        emotion: str = None, 
        location: Tuple[float, float] = None,
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Find relevant resources based on message content and context.
        
        Args:
            message: User's message
            emotion: Primary emotion detected
            location: User's location (latitude, longitude)
            user_preferences: User preferences (insurance, language, etc.)
            
        Returns:
            List of relevant resources
            
        TODO: Implement sophisticated relevance scoring
        TODO: Add machine learning-based resource matching
        """
        try:
            # Analyze message for resource needs
            resource_needs = self._analyze_resource_needs(message, emotion)
            
            # Find matching resources
            relevant_resources = []
            
            # Add emergency resources if crisis detected
            if resource_needs.get("crisis", False):
                relevant_resources.extend(self._format_resources(self.emergency_resources))
            
            # Add general resources based on needs
            for resource_type in resource_needs.get("types", []):
                matching_resources = self._find_resources_by_type(resource_type)
                relevant_resources.extend(self._format_resources(matching_resources))
            
            # Filter by location if provided
            if location:
                relevant_resources = self._filter_by_location(relevant_resources, location)
            
            # Apply user preferences
            if user_preferences:
                relevant_resources = self._apply_user_preferences(
                    relevant_resources, user_preferences
                )
            
            # Sort by relevance and return top matches
            relevant_resources = self._sort_by_relevance(relevant_resources, resource_needs)
            
            return relevant_resources[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Error finding relevant resources: {str(e)}")
            return self._format_resources(self.emergency_resources)
    
    def _analyze_resource_needs(self, message: str, emotion: str = None) -> Dict[str, Any]:
        """
        Analyze message to determine resource needs.
        
        Args:
            message: User's message
            emotion: Primary emotion
            
        Returns:
            Dictionary with resource needs analysis
            
        TODO: Implement more sophisticated needs analysis
        """
        needs = {
            "crisis": False,
            "types": [],
            "urgency": "low",
            "specialties": []
        }
        
        # Check for crisis keywords
        crisis_keywords = ["suicide", "kill myself", "end it all", "hurt myself", "overdose"]
        message_lower = message.lower()
        
        for keyword in crisis_keywords:
            if keyword in message_lower:
                needs["crisis"] = True
                needs["urgency"] = "critical"
                break
        
        # Add resource types based on emotion
        if emotion:
            emotion_mapping = {
                "anxious": ["mental_health_professional", "support_helpline"],
                "depressed": ["mental_health_professional", "crisis_text"],
                "angry": ["anger_management", "mental_health_professional"],
                "sad": ["support_helpline", "mental_health_professional"],
                "overwhelmed": ["crisis_text", "support_helpline"]
            }
            needs["types"].extend(emotion_mapping.get(emotion, []))
        
        # Default to general support if no specific needs identified
        if not needs["types"] and not needs["crisis"]:
            needs["types"] = ["support_helpline", "mental_health_professional"]
        
        return needs
    
    def _find_resources_by_type(self, resource_type: str) -> List[Resource]:
        """
        Find resources by type.
        
        Args:
            resource_type: Type of resource to find
            
        Returns:
            List of matching resources
        """
        matching_resources = []
        
        # Search in general resources
        for resource in self.resources:
            if resource.type == resource_type:
                matching_resources.append(resource)
        
        # Search in providers
        for provider in self.providers:
            if provider.type == resource_type:
                matching_resources.append(provider)
        
        return matching_resources
    
    def _format_resources(self, resources: List[Resource]) -> List[Dict[str, Any]]:
        """
        Format resources for API response.
        
        Args:
            resources: List of Resource objects
            
        Returns:
            List of formatted resource dictionaries
        """
        formatted = []
        
        for resource in resources:
            formatted.append({
                "id": resource.id,
                "name": resource.name,
                "type": resource.type,
                "description": resource.description,
                "phone": resource.phone,
                "website": resource.website,
                "address": resource.address,
                "availability": resource.availability,
                "cost": resource.cost,
                "crisis_capable": resource.crisis_capable,
                "languages": resource.languages,
                "specialties": resource.specialties,
                "rating": resource.rating
            })
        
        return formatted
    
    def _filter_by_location(
        self, 
        resources: List[Dict[str, Any]], 
        user_location: Tuple[float, float],
        max_distance_km: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Filter resources by proximity to user location.
        
        Args:
            resources: List of resources
            user_location: User's location (lat, lng)
            max_distance_km: Maximum distance in kilometers
            
        Returns:
            Filtered list of resources
            
        TODO: Implement more sophisticated location filtering
        """
        filtered_resources = []
        user_lat, user_lng = user_location
        
        for resource in resources:
            # Include resources without location data (online/phone services)
            if not resource.get("latitude") or not resource.get("longitude"):
                filtered_resources.append(resource)
                continue
            
            # Calculate distance
            resource_lat = resource["latitude"]
            resource_lng = resource["longitude"]
            distance = self._calculate_distance(
                user_lat, user_lng, resource_lat, resource_lng
            )
            
            if distance <= max_distance_km:
                resource["distance_km"] = round(distance, 1)
                filtered_resources.append(resource)
        
        return filtered_resources
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lng1: First coordinate
            lat2, lng2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    def _apply_user_preferences(
        self, 
        resources: List[Dict[str, Any]], 
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply user preferences to filter resources.
        
        Args:
            resources: List of resources
            preferences: User preferences
            
        Returns:
            Filtered resources
            
        TODO: Implement comprehensive preference matching
        """
        filtered_resources = []
        
        for resource in resources:
            # Check language preference
            preferred_language = preferences.get("language")
            if preferred_language:
                resource_languages = resource.get("languages", [])
                if preferred_language not in resource_languages and resource_languages:
                    continue
            
            # Check insurance preference
            preferred_insurance = preferences.get("insurance")
            if preferred_insurance:
                accepted_insurance = resource.get("insurance_accepted", [])
                if (accepted_insurance and 
                    preferred_insurance not in accepted_insurance and 
                    "all" not in accepted_insurance):
                    continue
            
            # Check cost preference
            max_cost = preferences.get("max_cost")
            if max_cost:
                resource_cost = resource.get("cost", "unknown")
                if resource_cost not in ["free", "unknown"] and max_cost == "free":
                    continue
            
            filtered_resources.append(resource)
        
        return filtered_resources
    
    def _sort_by_relevance(
        self, 
        resources: List[Dict[str, Any]], 
        needs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Sort resources by relevance to user needs.
        
        Args:
            resources: List of resources
            needs: Resource needs analysis
            
        Returns:
            Sorted resources
            
        TODO: Implement machine learning-based relevance scoring
        """
        def relevance_score(resource):
            score = 0
            
            # Crisis resources get highest priority
            if needs.get("crisis", False) and resource.get("crisis_capable", False):
                score += 100
            
            # Type matching
            if resource.get("type") in needs.get("types", []):
                score += 50
            
            # Distance bonus (closer is better)
            distance = resource.get("distance_km")
            if distance is not None:
                score += max(0, 20 - distance)  # Up to 20 points for being close
            
            # Free resources get bonus
            if resource.get("cost") == "free":
                score += 10
            
            # 24/7 availability bonus
            if "24/7" in resource.get("availability", ""):
                score += 10
            
            # Rating bonus
            rating = resource.get("rating")
            if rating:
                score += rating * 2
            
            return score
        
        return sorted(resources, key=relevance_score, reverse=True)
    
    def get_emergency_resources(self) -> List[Dict[str, Any]]:
        """
        Get emergency mental health resources.
        
        Returns:
            List of emergency resources
        """
        return self._format_resources(self.emergency_resources)
    
    def get_general_support_resources(self) -> List[Dict[str, Any]]:
        """
        Get general mental health support resources.
        
        Returns:
            List of general support resources
        """
        general_resources = [
            resource for resource in self.resources 
            if resource.type in ["support_helpline", "mental_health_professional"]
        ]
        return self._format_resources(general_resources)
    
    def search_providers(
        self, 
        specialty: str = None, 
        location: Tuple[float, float] = None,
        insurance: str = None,
        max_distance_km: float = 25.0
    ) -> List[Dict[str, Any]]:
        """
        Search for therapy providers based on criteria.
        
        Args:
            specialty: Desired specialty
            location: User location
            insurance: Insurance provider
            max_distance_km: Maximum distance
            
        Returns:
            List of matching providers
            
        TODO: Integrate with real provider APIs
        """
        try:
            matching_providers = []
            
            for provider in self.providers:
                # Check specialty
                if specialty:
                    provider_specialties = provider.specialties or []
                    if specialty.lower() not in [s.lower() for s in provider_specialties]:
                        continue
                
                # Check insurance
                if insurance:
                    accepted_insurance = provider.insurance_accepted or []
                    if (accepted_insurance and 
                        insurance not in accepted_insurance and 
                        "all" not in accepted_insurance):
                        continue
                
                matching_providers.append(provider)
            
            # Format and filter by location
            formatted_providers = self._format_resources(matching_providers)
            
            if location:
                formatted_providers = self._filter_by_location(
                    formatted_providers, location, max_distance_km
                )
            
            # Sort by distance and rating
            def provider_score(provider):
                score = 0
                if provider.get("rating"):
                    score += provider["rating"] * 10
                if provider.get("distance_km"):
                    score += max(0, 50 - provider["distance_km"])
                return score
            
            return sorted(formatted_providers, key=provider_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching providers: {str(e)}")
            return []
    
    def add_resource(self, resource_data: Dict[str, Any]) -> bool:
        """
        Add a new resource to the matcher.
        
        Args:
            resource_data: Resource data dictionary
            
        Returns:
            Success status
            
        TODO: Implement resource validation and persistence
        """
        try:
            resource = self._dict_to_resource(resource_data)
            
            # Validate required fields
            if not resource.name or not resource.type:
                logger.error("Resource missing required fields (name, type)")
                return False
            
            # Add to appropriate list
            if resource.type in ["therapist", "counselor", "psychiatrist"]:
                self.providers.append(resource)
            else:
                self.resources.append(resource)
            
            logger.info(f"Added new resource: {resource.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding resource: {str(e)}")
            return False
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available resources.
        
        Returns:
            Dictionary with resource statistics
        """
        total_resources = len(self.resources) + len(self.providers) + len(self.emergency_resources)
        
        # Count by type
        type_counts = {}
        for resource_list in [self.resources, self.providers, self.emergency_resources]:
            for resource in resource_list:
                resource_type = resource.type
                type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
        
        # Count crisis-capable resources
        crisis_capable = sum(
            1 for resource_list in [self.resources, self.providers, self.emergency_resources]
            for resource in resource_list
            if resource.crisis_capable
        )
        
        return {
            "total_resources": total_resources,
            "general_resources": len(self.resources),
            "providers": len(self.providers),
            "emergency_resources": len(self.emergency_resources),
            "crisis_capable": crisis_capable,
            "type_distribution": type_counts,
            "languages_supported": self._get_supported_languages(),
            "insurance_coverage": self._get_insurance_coverage()
        }
    
    def _get_supported_languages(self) -> List[str]:
        """Get list of all supported languages."""
        languages = set()
        for resource_list in [self.resources, self.providers, self.emergency_resources]:
            for resource in resource_list:
                if resource.languages:
                    languages.update(resource.languages)
        return sorted(list(languages))
    
    def _get_insurance_coverage(self) -> Dict[str, int]:
        """Get insurance coverage statistics."""
        insurance_counts = {}
        for resource_list in [self.resources, self.providers]:
            for resource in resource_list:
                if resource.insurance_accepted:
                    for insurance in resource.insurance_accepted:
                        insurance_counts[insurance] = insurance_counts.get(insurance, 0) + 1
        return insurance_counts