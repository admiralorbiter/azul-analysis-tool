#!/usr/bin/env python3
"""
Example usage of the Azul REST API (M5).

This script demonstrates how to use the REST API endpoints
for analysis, hints, and session management.
"""

import requests
import json
import time


def main():
    """Demonstrate REST API usage."""
    base_url = "http://localhost:8000"
    
    print("🚀 Azul REST API Example (M5)")
    print("=" * 40)
    
    # Step 1: Create a session
    print("\n1. Creating session...")
    response = requests.post(f"{base_url}/api/v1/auth/session")
    
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        return
    
    session_data = response.json()
    session_id = session_data['session_id']
    print(f"✅ Session created: {session_id[:16]}...")
    
    headers = {'X-Session-ID': session_id}
    
    # Step 2: Check API health
    print("\n2. Checking API health...")
    response = requests.get(f"{base_url}/api/v1/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ API Status: {health_data['status']}")
        print(f"   Version: {health_data['version']}")
    
    # Step 3: Get a fast hint
    print("\n3. Getting fast hint...")
    hint_request = {
        'fen_string': 'initial',
        'agent_id': 0,
        'budget': 0.2,
        'rollouts': 50
    }
    
    response = requests.post(
        f"{base_url}/api/v1/hint",
        headers=headers,
        json=hint_request
    )
    
    if response.status_code == 200:
        hint_data = response.json()
        print("✅ Hint received:")
        print(f"   Best move: {hint_data['hint']['best_move']}")
        print(f"   Expected value: {hint_data['hint']['expected_value']:.2f}")
        print(f"   Confidence: {hint_data['hint']['confidence']:.2f}")
        print(f"   Search time: {hint_data['hint']['search_time']:.3f}s")
        print(f"   Rollouts: {hint_data['hint']['rollouts_performed']}")
    else:
        print(f"❌ Hint request failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 4: Perform exact analysis
    print("\n4. Performing exact analysis...")
    analysis_request = {
        'fen_string': 'initial',
        'agent_id': 0,
        'depth': 3,
        'time_budget': 2.0
    }
    
    response = requests.post(
        f"{base_url}/api/v1/analyze",
        headers=headers,
        json=analysis_request
    )
    
    if response.status_code == 200:
        analysis_data = response.json()
        print("✅ Analysis completed:")
        print(f"   Best move: {analysis_data['analysis']['best_move']}")
        print(f"   Best score: {analysis_data['analysis']['best_score']:.2f}")
        print(f"   Search time: {analysis_data['analysis']['search_time']:.3f}s")
        print(f"   Nodes searched: {analysis_data['analysis']['nodes_searched']:,}")
        print(f"   Depth reached: {analysis_data['analysis']['depth_reached']}")
    else:
        print(f"❌ Analysis request failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 5: Check usage statistics
    print("\n5. Checking usage statistics...")
    response = requests.get(f"{base_url}/api/v1/stats", headers=headers)
    
    if response.status_code == 200:
        stats_data = response.json()
        print("✅ Usage statistics:")
        print(f"   General requests remaining: {stats_data['rate_limits']['general_remaining']}")
        print(f"   Heavy analyses remaining: {stats_data['rate_limits']['heavy_remaining']}")
        print(f"   Light analyses remaining: {stats_data['rate_limits']['light_remaining']}")
    else:
        print(f"❌ Stats request failed: {response.status_code}")
    
    print("\n🎉 API demonstration completed!")


if __name__ == "__main__":
    print("To run this example:")
    print("1. Start the API server: python main.py serve")
    print("2. Run this script: python examples/api_example.py")
    print("\nStarting demonstration...")
    main() 