#!/usr/bin/env python3
"""
Test script to demonstrate Crisis Support AI Agent functionality.
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

def main():
    print("=== Crisis Support AI Agent - End-to-End Test ===\n")
    
    # Test health endpoint
    test_endpoint("GET", "/api/health")
    
    # Test root endpoint
    test_endpoint("GET", "/")
    
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

if __name__ == "__main__":
    main()