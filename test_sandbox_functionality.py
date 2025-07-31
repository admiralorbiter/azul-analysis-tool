#!/usr/bin/env python3
"""
Test script for the What-if Sandbox functionality.

This script tests the move execution API and UI integration.
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_session_creation():
    """Test session creation."""
    print("🔐 Testing session creation...")
    
    response = requests.post(f"{API_BASE}/auth/session", json={
        "user_agent": "test-script",
        "ip_address": "127.0.0.1"
    })
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        return session_id
    else:
        print(f"❌ Session creation failed: {response.status_code}")
        return None

def test_move_execution(session_id):
    """Test move execution with valid session."""
    print("🎯 Testing move execution...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": session_id
    }
    
    # Test data for a simple move
    move_data = {
        "fen_string": "initial",
        "move": {
            "source_id": 0,
            "tile_type": 0,  # red
            "pattern_line_dest": 0,
            "num_to_pattern_line": 1,
            "num_to_floor_line": 0
        },
        "agent_id": 0
    }
    
    response = requests.post(f"{API_BASE}/execute_move", 
                           headers=headers, 
                           json=move_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Move executed successfully!")
            print(f"Move: {data.get('move_executed')}")
            print(f"Game Over: {data.get('game_over')}")
            print(f"Scores: {data.get('scores')}")
            if data.get('engine_response'):
                print(f"Engine Response: {data.get('engine_response')}")
        else:
            print(f"❌ Move execution failed: {data.get('error')}")
    else:
        print(f"❌ API request failed: {response.status_code}")

def test_analysis_endpoints(session_id):
    """Test analysis endpoints."""
    print("🔍 Testing analysis endpoints...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": session_id
    }
    
    # Test exact analysis
    analysis_data = {
        "fen_string": "initial",
        "agent_id": 0,
        "depth": 3
    }
    
    response = requests.post(f"{API_BASE}/analyze", 
                           headers=headers, 
                           json=analysis_data)
    
    print(f"Analysis Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analysis successful: {data.get('best_move')}")
    else:
        print(f"❌ Analysis failed: {response.text}")

def test_ui_integration():
    """Test UI integration by checking if the web interface is accessible."""
    print("🌐 Testing UI integration...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Web UI is accessible")
            return True
        else:
            print(f"❌ Web UI returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Web UI is not accessible (connection error)")
        return False

def main():
    """Main test function."""
    print("🚀 Starting What-if Sandbox functionality tests...")
    print("=" * 50)
    
    # Test session creation
    session_id = test_session_creation()
    if not session_id:
        print("❌ Cannot proceed without valid session")
        return
    
    print("\n" + "=" * 50)
    
    # Test move execution
    test_move_execution(session_id)
    
    print("\n" + "=" * 50)
    
    # Test analysis endpoints
    test_analysis_endpoints(session_id)
    
    print("\n" + "=" * 50)
    
    # Test UI integration
    test_ui_integration()
    
    print("\n" + "=" * 50)
    print("✅ Sandbox functionality tests completed!")

if __name__ == "__main__":
    main() 