#!/usr/bin/env python3
"""
Test script for API endpoints.
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8001"
    
    print("Testing API endpoints...")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{base_url}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test session creation
    print("\n2. Testing session creation...")
    response = requests.post(
        f"{base_url}/api/v1/auth/session",
        json={"username": "test", "password": "test"}
    )
    print(f"Status: {response.status_code}")
    session_data = response.json()
    print(f"Response: {session_data}")
    
    if response.status_code == 200:
        session_id = session_data.get("session_id")
        
        # Test hint endpoint
        print("\n3. Testing hint endpoint...")
        headers = {"X-Session-ID": session_id}
        response = requests.post(
            f"{base_url}/api/v1/hint",
            headers=headers,
            json={
                "fen_string": "initial",
                "agent_id": 0,
                "budget": 0.2,
                "rollouts": 50
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test exact analysis endpoint
        print("\n4. Testing exact analysis endpoint...")
        response = requests.post(
            f"{base_url}/api/v1/analyze",
            headers=headers,
            json={
                "fen_string": "initial",
                "agent_id": 0,
                "depth": 3,
                "timeout": 4.0
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test neural analysis endpoint
        print("\n5. Testing neural analysis endpoint...")
        response = requests.post(
            f"{base_url}/api/v1/analyze_neural",
            headers=headers,
            json={
                "fen": "initial",
                "agent_id": 0,
                "time_budget": 2.0,
                "max_rollouts": 100
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_api() 