#!/usr/bin/env python3
"""Debug session creation issue."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_creation():
    try:
        from api.app import create_test_app
        import json
        
        print("Creating test app...")
        app = create_test_app()
        print(f"App created: {app}")
        
        print("Creating test client...")
        client = app.test_client()
        print(f"Client created: {client}")
        
        print("Making POST request to /api/v1/auth/session...")
        response = client.post('/api/v1/auth/session')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        print(f"Response content type: {response.content_type}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.data)
                print(f"JSON data: {data}")
                session_id = data.get('session_id')
                print(f"Session ID: {session_id}")
                
                if session_id:
                    print("✅ Session creation successful!")
                    return session_id
                else:
                    print("❌ No session_id in response")
                    return None
            except Exception as e:
                print(f"❌ JSON parsing error: {e}")
                return None
        else:
            print(f"❌ HTTP error: {response.status_code}")
            try:
                error_data = response.data.decode('utf-8')
                print(f"Error data: {error_data}")
            except:
                print("Could not decode error data")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if 'app' in locals() and hasattr(app, 'cleanup'):
            app.cleanup()

if __name__ == "__main__":
    test_session_creation()