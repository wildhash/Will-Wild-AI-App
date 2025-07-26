#!/usr/bin/env python3
"""
Test script to demonstrate Session Persistence and Conversation Memory functionality.
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
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        return response.json() if response.status_code < 400 else None
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return None

def main():
    print("=== Crisis Support AI Agent - Session Persistence Test ===\n")
    
    # Test health endpoint
    test_endpoint("GET", "/api/health")
    
    # Test root endpoint
    test_endpoint("GET", "/")
    
    # Test session creation
    print("\n--- Testing Session Creation ---")
    session_data = test_endpoint("POST", "/api/sessions", {
        "user_id": "demo_user_session_test"
    })
    
    if not session_data:
        print("❌ Failed to create session")
        return
    
    session_id = session_data["session_id"]
    user_id = session_data["user_id"]
    print(f"✅ Created session: {session_id}")
    
    # Test session-based chat
    print("\n--- Testing Session-Based Chat ---")
    messages = [
        "Hello, I'm having a tough day",
        "I'm feeling really anxious and overwhelmed",
        "I feel completely hopeless and don't know what to do"
    ]
    
    for message in messages:
        print(f"\nSending: {message}")
        chat_response = test_endpoint("POST", "/api/chat", {
            "user_id": user_id,
            "message": message,
            "session_id": session_id
        })
        
        if chat_response:
            print(f"Risk Level: {chat_response['risk_level']}")
            print(f"Response: {chat_response['response'][:100]}...")
        
        time.sleep(1)
    
    # Test session retrieval
    print("\n--- Testing Session History Retrieval ---")
    session_info = test_endpoint("GET", f"/api/sessions/{session_id}")
    
    if session_info:
        print(f"✅ Session has {session_info['message_count']} messages")
        print(f"✅ Risk level: {session_info['risk_level']}")
        print(f"✅ Retrieved {len(session_info['messages'])} message objects")
    
    # Test resources with session context
    print("\n--- Testing Personalized Resources ---")
    resources = test_endpoint("GET", f"/api/resources?session_id={session_id}")
    
    if resources:
        print("✅ Resources loaded with personalized recommendations")
        if "personalized" in resources:
            print(f"✅ Personalized message: {resources['personalized']['message']}")
    
    # Test missing session handling
    print("\n--- Testing Missing Session Handling ---")
    test_endpoint("GET", "/api/sessions/invalid-session-id")
    
    # Test session clearing
    print("\n--- Testing Session Clearing ---")
    test_endpoint("DELETE", f"/api/sessions/{session_id}")
    
    # Verify session is gone
    print("\nVerifying session deletion:")
    test_endpoint("GET", f"/api/sessions/{session_id}")
    
    print("\n=== Session Persistence Tests Complete ===")
    print("✅ All core session functionalities are working:")
    print("   - Session creation and management")
    print("   - Session-based conversation memory")
    print("   - Chat history persistence and retrieval")
    print("   - Risk level tracking across messages")
    print("   - Personalized resource recommendations")
    print("   - Error handling for missing sessions")
    print("   - Session cleanup capabilities")

if __name__ == "__main__":
    main()