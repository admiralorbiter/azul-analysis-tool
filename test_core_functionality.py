#!/usr/bin/env python3
"""
Quick test script to verify core API functionality works.
This helps us ensure the essential features are working before proceeding to UI.
"""

import json
import tempfile
import os
from api.app import create_test_app


def test_basic_api_functionality():
    """Test basic API endpoints work."""
    print("🧪 Testing Core API Functionality...")
    
    # Create test app
    app = create_test_app()
    
    with app.test_client() as client:
        print("\n1. Testing session creation...")
        response = client.post('/api/v1/auth/session')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            session_id = data.get('session_id')
            print(f"   Session ID: {session_id[:20]}..." if session_id else "   No session ID!")
            
            if session_id:
                headers = {'X-Session-ID': session_id}
                
                print("\n2. Testing health endpoint...")
                response = client.get('/api/v1/health', headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"   Health: {data.get('status')}")
                
                print("\n3. Testing API info endpoint...")
                response = client.get('/api')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"   API Name: {data.get('name')}")
                    print(f"   Endpoints: {len(data.get('endpoints', {}))}")
                
                print("\n4. Testing database functionality...")
                if hasattr(app, 'database') and app.database:
                    # Test basic database operations
                    try:
                        position_id = app.database.cache_position("test_pos", 2)
                        print(f"   Position cached: ID {position_id}")
                        
                        # Test analysis caching
                        analysis_result = {
                            'best_move': 'test_move',
                            'best_score': 5.0,
                            'search_time': 0.1,
                            'nodes_searched': 100,
                            'rollout_count': 20
                        }
                        analysis_id = app.database.cache_analysis(position_id, 0, 'mcts', analysis_result)
                        print(f"   Analysis cached: ID {analysis_id}")
                        
                        # Test retrieval
                        cached = app.database.get_cached_analysis("test_pos", 0, 'mcts')
                        if cached:
                            print(f"   Analysis retrieved: {cached.best_move}")
                        else:
                            print("   ⚠️  Analysis retrieval failed")
                            
                    except Exception as e:
                        print(f"   ⚠️  Database error: {e}")
                else:
                    print("   ⚠️  No database available")
                
                print("\n5. Testing performance API...")
                try:
                    response = client.get('/api/v1/performance/stats', headers=headers)
                    print(f"   Performance stats: {response.status_code}")
                    
                    response = client.get('/api/v1/performance/health', headers=headers)
                    print(f"   Performance health: {response.status_code}")
                    
                except Exception as e:
                    print(f"   ⚠️  Performance API error: {e}")
                
            else:
                print("   ❌ Session creation failed - no session ID")
        else:
            print("   ❌ Session creation failed")
    
    # Cleanup
    if hasattr(app, 'cleanup'):
        app.cleanup()
    
    print("\n✅ Core functionality test completed!")


if __name__ == "__main__":
    test_basic_api_functionality()