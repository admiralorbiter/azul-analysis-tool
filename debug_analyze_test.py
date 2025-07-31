import json
import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.app import create_test_app
from unittest.mock import patch, MagicMock

def debug_analyze_endpoint():
    """Debug the analyze endpoint to see what's causing the 500 error."""
    try:
        print("Creating test app...")
        app = create_test_app()
        client = app.test_client()
        
        print("Creating session...")
        # Create session
        response = client.post('/api/v1/auth/session')
        print(f"Session response: {response.status_code}")
        print(f"Session data: {response.data.decode()}")
        
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        print("Making analysis request...")
        # Make analysis request
        response = client.post('/api/v1/analyze',
                              headers=headers,
                              json={
                                  'fen_string': 'initial',
                                  'agent_id': 0,
                                  'depth': 3,
                                  'time_budget': 4.0
                              })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data.decode()}")
        
        if hasattr(app, 'cleanup'):
            app.cleanup()
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_analyze_endpoint() 