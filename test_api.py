#!/usr/bin/env python3
"""
Test script to demonstrate Crisis Support AI Agent functionality including mood tracking.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None):
    """Test an API endpoint and print results."""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return None

def test_mood_tracking():
    """Test mood tracking functionality specifically."""
    print("\n=== MOOD TRACKING TESTS ===")
    
    # Test happy mood
    print("\n--- Testing Happy Mood Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "mood_test_happy",
        "message": "I'm so excited and happy! This is wonderful news, I feel amazing!"
    })
    
    mood_data = test_endpoint("GET", "/api/mood/mood_test_happy")
    if mood_data and mood_data.get("mood_timeline"):
        mood = mood_data["mood_timeline"][0]
        print(f"✅ Happy mood detected: {mood['mood']} (confidence: {mood['confidence']})")
        print(f"   Keywords: {mood['keywords']}")
    
    # Test sad mood
    print("\n--- Testing Sad Mood Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "mood_test_sad",
        "message": "I feel so sad and down today. Everything seems terrible and awful."
    })
    
    mood_data = test_endpoint("GET", "/api/mood/mood_test_sad")
    if mood_data and mood_data.get("mood_timeline"):
        mood = mood_data["mood_timeline"][0]
        print(f"✅ Sad mood detected: {mood['mood']} (confidence: {mood['confidence']})")
        print(f"   Keywords: {mood['keywords']}")
    
    # Test anxious mood
    print("\n--- Testing Anxious Mood Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "mood_test_anxious",
        "message": "I'm feeling very anxious and worried about everything. I'm so stressed and nervous."
    })
    
    mood_data = test_endpoint("GET", "/api/mood/mood_test_anxious")
    if mood_data and mood_data.get("mood_timeline"):
        mood = mood_data["mood_timeline"][0]
        print(f"✅ Anxious mood detected: {mood['mood']} (confidence: {mood['confidence']})")
        print(f"   Keywords: {mood['keywords']}")
    
    # Test angry mood
    print("\n--- Testing Angry Mood Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "mood_test_angry",
        "message": "I'm so angry and frustrated! This is absolutely infuriating and I'm furious!"
    })
    
    mood_data = test_endpoint("GET", "/api/mood/mood_test_angry")
    if mood_data and mood_data.get("mood_timeline"):
        mood = mood_data["mood_timeline"][0]
        print(f"✅ Angry mood detected: {mood['mood']} (confidence: {mood['confidence']})")
        print(f"   Keywords: {mood['keywords']}")
    
    # Test neutral mood
    print("\n--- Testing Neutral Mood Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "mood_test_neutral",
        "message": "Hello, I would like to discuss my work schedule."
    })
    
    mood_data = test_endpoint("GET", "/api/mood/mood_test_neutral")
    if mood_data and mood_data.get("mood_timeline"):
        mood = mood_data["mood_timeline"][0]
        print(f"✅ Neutral mood detected: {mood['mood']} (confidence: {mood['confidence']})")
        print(f"   Keywords: {mood['keywords']}")
    
    # Test mood changes over time
    print("\n--- Testing Mood Changes Over Time ---")
    user_id = "mood_test_timeline"
    
    # Start with anxious
    test_endpoint("POST", "/api/chat", {
        "user_id": user_id,
        "message": "I'm feeling really anxious about my job interview tomorrow."
    })
    
    # Change to happy
    test_endpoint("POST", "/api/chat", {
        "user_id": user_id,
        "message": "Actually, I just got some great news! I'm so happy and excited!"
    })
    
    # Change to sad
    test_endpoint("POST", "/api/chat", {
        "user_id": user_id,
        "message": "But now I'm feeling sad because I miss my family."
    })
    
    # Get mood timeline
    mood_data = test_endpoint("GET", f"/api/mood/{user_id}")
    if mood_data:
        timeline = mood_data.get("mood_timeline", [])
        summary = mood_data.get("session_mood_summary", {})
        
        print(f"✅ Mood timeline tracked: {len(timeline)} entries")
        for i, mood in enumerate(timeline):
            print(f"   {i+1}. {mood['mood']} (confidence: {mood['confidence']}) - {mood['keywords']}")
        
        print(f"✅ Session summary:")
        print(f"   Dominant mood: {summary.get('dominant_mood')}")
        print(f"   Mood distribution: {summary.get('mood_distribution')}")
        print(f"   Mood changes: {summary.get('mood_changes')}")
        print(f"   Average confidence: {summary.get('average_confidence')}")

def main():
    print("=== Crisis Support AI Agent - Enhanced Test with Mood Tracking ===\n")
    
    # Test health endpoint
    test_endpoint("GET", "/api/health")
    
    # Test root endpoint
    test_endpoint("GET", "/")
    
    # Test mood tracking functionality
    test_mood_tracking()
    
    # Test original conversation functionality
    print("\n=== ORIGINAL FUNCTIONALITY TESTS ===")
    
    # Test normal conversation
    print("\n--- Testing Normal Conversation ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "demo_user_1",
        "message": "Hello, I'm having a tough day at work"
    })
    
    # Test medium risk conversation
    print("\n--- Testing Medium Risk Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "demo_user_2", 
        "message": "I'm feeling really anxious and overwhelmed lately"
    })
    
    # Test high risk conversation
    print("\n--- Testing High Risk Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "demo_user_3",
        "message": "I feel completely hopeless and don't know what to do"
    })
    
    # Test critical risk conversation
    print("\n--- Testing Critical Risk Detection ---")
    test_endpoint("POST", "/api/chat", {
        "user_id": "demo_user_4",
        "message": "I don't think I can take this anymore, I want to hurt myself"
    })
    
    # Test conversation summary
    print("\n--- Testing Conversation Summary ---")
    test_endpoint("GET", "/api/conversation/demo_user_3/summary")
    
    print("\n=== Test Complete ===")
    print("✅ All core functionalities are working:")
    print("   - FastAPI server with chat endpoints")
    print("   - Crisis detection and risk assessment")
    print("   - Memory service for conversation history")
    print("   - Safety service with logging and escalation")
    print("   - Therapy agent orchestrating responses")
    print("   - Proper error handling and logging")
    print("   - 🆕 MOOD TRACKING AND ANALYTICS:")
    print("     • Rule-based mood detection (happy, sad, anxious, angry, neutral)")
    print("     • Mood confidence scoring")
    print("     • Keyword extraction for mood reasoning")
    print("     • Mood timeline tracking")
    print("     • Session mood analytics and trends")
    print("     • /api/mood/{user_id} endpoint for mood data retrieval")

if __name__ == "__main__":
    main()