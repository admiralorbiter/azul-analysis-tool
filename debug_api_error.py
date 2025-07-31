#!/usr/bin/env python3
"""Debug script to test the failing API endpoint."""

import json
import requests
from api.app import create_test_app

def test_analyze_endpoint():
    """Test the analyze endpoint to see the actual error."""
    app = create_test_app()
    client = app.test_client()
    
    # Create session
    response = client.post('/api/v1/auth/session')
    session_id = json.loads(response.data)['session_id']
    auth_headers = {'X-Session-ID': session_id}
    
    # Test analyze endpoint
    analyze_data = {
        'fen_string': 'initial',
        'agent_id': 0,
        'depth': 2,
        'time_budget': 1.0
    }
    
    response = client.post('/api/v1/analyze', json=analyze_data, headers=auth_headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data.decode()}")
    
    if response.status_code != 200:
        print(f"Error: {response.get_json()}")

if __name__ == "__main__":
    test_analyze_endpoint() 