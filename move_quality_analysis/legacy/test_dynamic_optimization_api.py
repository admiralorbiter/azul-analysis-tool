#!/usr/bin/env python3
"""
Test script for dynamic optimization API endpoints.
"""

import requests
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dynamic_optimization_api():
    """Test the dynamic optimization API endpoints."""
    
    base_url = "http://localhost:8000/api/v1"
    
    # First, create a session
    print("1. Creating session...")
    session_response = requests.post(
        f"{base_url}/auth/session",
        json={
            "user_agent": "test-script",
            "ip_address": "127.0.0.1"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Failed to create session: {session_response.status_code}")
        print(f"Response: {session_response.text}")
        return
    
    session_data = session_response.json()
    session_id = session_data.get('session_id')
    print(f"✅ Session created: {session_id}")
    
    # Test data
    test_data = {
        "fen_string": "local_eyJjZW50",
        "depth": 3
    }
    
    print(f"\n2. Testing /evaluate-endgame endpoint...")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Test evaluate-endgame endpoint with session
        response = requests.post(
            f"{base_url}/evaluate-endgame",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "X-Session-ID": session_id
            }
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server not running or not accessible")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_dynamic_optimization_api() 