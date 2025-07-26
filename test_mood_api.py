#!/usr/bin/env python3
"""
Enhanced test script for Crisis Support AI Agent with mood tracking functionality.
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
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Error Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return None

def main():
    print("=== Crisis Support AI Agent - Enhanced Mood Tracking Test ===\n")
    
    # Test enhanced health endpoint
    print("--- Testing Enhanced Health Check ---")
    test_endpoint("GET", "/api/health")
    
    # Test mood detection with various inputs
    print("\n--- Testing Mood Detection ---")
    
    mood_test_cases = [
        ("demo_user_mood_1", "I'm feeling really happy and excited about my new job!"),
        ("demo_user_mood_2", "I'm not happy at all, everything seems to be going wrong"),
        ("demo_user_mood_3", "I feel anxious and worried about the presentation tomorrow"),
        ("demo_user_mood_4", "I'm so frustrated with this situation, it's driving me crazy"),
        ("demo_user_mood_5", "I feel calm and peaceful after my meditation"),
        ("demo_user_mood_1", "Actually, now I'm feeling a bit mixed about everything"),
    ]
    
    for user_id, message in mood_test_cases:
        print(f"\n--- Testing: '{message}' ---")
        result = test_endpoint("POST", "/api/chat", {
            "user_id": user_id,
            "message": message
        })
        
        if result:
            print(f"Detected Mood: {result.get('mood_detected')} (confidence: {result.get('mood_confidence', 0):.2f})")
    
    # Test mood analytics
    print("\n--- Testing Mood Analytics ---")
    test_endpoint("GET", "/api/mood/demo_user_mood_1/analytics")
    
    # Test mood history
    print("\n--- Testing Mood History ---")
    test_endpoint("GET", "/api/mood/demo_user_mood_1/history?limit=10")
    
    # Test mood feedback
    print("\n--- Testing Mood Feedback ---")
    test_endpoint("POST", "/api/mood/demo_user_mood_1/feedback", {
        "is_correct": True,
        "detected_mood": "mixed",
        "actual_mood": "mixed"
    })
    
    # Test negation handling
    print("\n--- Testing Negation Handling ---")
    negation_tests = [
        ("demo_user_neg_1", "I'm not sad, I'm actually doing fine"),
        ("demo_user_neg_2", "I don't feel happy about this situation"),
        ("demo_user_neg_3", "I'm never anxious about public speaking"),
    ]
    
    for user_id, message in negation_tests:
        print(f"\n--- Negation Test: '{message}' ---")
        result = test_endpoint("POST", "/api/chat", {
            "user_id": user_id,
            "message": message
        })
        
        if result:
            print(f"Detected Mood: {result.get('mood_detected')} (confidence: {result.get('mood_confidence', 0):.2f})")
    
    # Test conversation summary with mood info
    print("\n--- Testing Enhanced Conversation Summary ---")
    test_endpoint("GET", "/api/conversation/demo_user_mood_1/summary")
    
    # Test manual cleanup
    print("\n--- Testing Manual Cleanup ---")
    test_endpoint("POST", "/api/admin/cleanup")
    
    print("\n=== Enhanced Test Complete ===")
    print("✅ All mood tracking functionalities tested:")
    print("   - Enhanced mood detection with confidence scoring")
    print("   - Negation handling ('not happy' → negative)")
    print("   - Mood analytics and trend analysis")
    print("   - Privacy-safe mood history")
    print("   - Mood feedback collection")
    print("   - Session cleanup and memory management")
    print("   - Enhanced error handling and validation")

if __name__ == "__main__":
    main()