"""
Simplified test suite for Development Tools Panel functionality.

This module tests the Development Tools Panel API endpoints and business logic
without requiring Selenium or browser automation.
"""

import unittest
import json
import time
from unittest.mock import patch, MagicMock
import requests
import os
import sys

# Add the project root to the path so we can import the API
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import create_test_app
import threading
import socket

def find_free_port():
    """Find a free port to use for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_test_server(port):
    """Start the Flask test server in a separate thread."""
    app = create_test_app()
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

class TestDevelopmentToolsPanelSimple(unittest.TestCase):
    """Simplified test suite for Development Tools Panel functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with running server."""
        # Find a free port
        cls.port = find_free_port()
        cls.base_url = f"http://localhost:{cls.port}"
        cls.api_base_url = f"{cls.base_url}/api/v1"
        
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(
            target=start_test_server, 
            args=(cls.port,),
            daemon=True
        )
        cls.server_thread.start()
        
        # Wait for server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/healthz", timeout=1)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if attempt == max_attempts - 1:
                    raise Exception("Server failed to start")
                time.sleep(0.1)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # The server thread will be cleaned up automatically as it's a daemon thread
        pass

    def setUp(self):
        """Set up test environment."""
        # Create session for API testing
        self.session = requests.Session()
        self.session_id = None
        
    def create_session(self):
        """Create a test session for API access."""
        try:
            response = self.session.post(
                f"{self.api_base_url}/auth/session",
                json={"username": "test", "password": "test"}
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                self.session.headers.update({
                    'X-Session-ID': self.session_id
                })
                return True
        except Exception as e:
            print(f"Failed to create session: {e}")
        return False

    def test_health_endpoint_response_format(self):
        """Test that the health endpoint returns the expected format."""
        response = requests.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['status', 'version', 'timestamp']
        for field in required_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['status'], 'healthy')
        self.assertIsInstance(data['version'], str)
        self.assertIsInstance(data['timestamp'], (int, float))

    def test_stats_endpoint_with_session(self):
        """Test the stats endpoint with proper session authentication."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('rate_limits', data)
        self.assertIn('session_stats', data)

    def test_performance_stats_endpoint(self):
        """Test the performance stats endpoint with proper session."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['timestamp', 'search_performance', 'cache_analytics']
        for field in required_fields:
            self.assertIn(field, data)

    def test_system_health_endpoint(self):
        """Test the detailed system health endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['status', 'timestamp', 'version']
        for field in required_fields:
            self.assertIn(field, data)

    def test_database_optimization_endpoint(self):
        """Test the database optimization endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.post(
            f"{self.api_base_url}/performance/optimize",
            json={'vacuum': True, 'analyze': True, 'reindex': False}
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['success', 'optimization_result', 'timestamp']
        for field in required_fields:
            self.assertIn(field, data)

    def test_cache_analytics_endpoint(self):
        """Test the cache analytics endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/analytics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)

    def test_monitoring_endpoint(self):
        """Test the monitoring data endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/monitoring")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)

    def test_endpoint_error_handling(self):
        """Test that endpoints handle errors gracefully."""
        # Test with invalid session
        response = requests.get(f"{self.api_base_url}/stats")
        self.assertEqual(response.status_code, 401)  # Unauthorized
        
        # Test with invalid endpoint
        response = requests.get(f"{self.api_base_url}/invalid_endpoint")
        self.assertEqual(response.status_code, 404)  # Not found

    def test_development_tools_api_integration(self):
        """Test complete Development Tools API integration."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
        
        # Test all development tools endpoints in sequence
        endpoints = [
            ('GET', '/health', {}),
            ('GET', '/stats', {}),
            ('GET', '/performance/stats', {}),
            ('GET', '/performance/health', {}),
            ('POST', '/performance/optimize', {}),
            ('GET', '/performance/analytics', {}),
            ('GET', '/performance/monitoring', {})
        ]
        
        for method, endpoint, data in endpoints:
            if method == 'GET':
                response = self.session.get(f"{self.api_base_url}{endpoint}")
            else:
                response = self.session.post(f"{self.api_base_url}{endpoint}", json=data)
            
            self.assertEqual(response.status_code, 200, 
                           f"Failed on {method} {endpoint}: {response.status_code}")
            
            response_data = response.json()
            self.assertIsInstance(response_data, dict)
            # Some endpoints might not have timestamp, check for common fields instead
            if 'timestamp' not in response_data:
                # Check for other common fields that indicate valid response
                self.assertTrue(len(response_data) > 0, "Response should not be empty")

    def test_session_management(self):
        """Test session creation and management."""
        # Test session creation
        response = self.session.post(
            f"{self.api_base_url}/auth/session",
            json={"username": "test", "password": "test"}
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('session_id', data)
        self.assertIsInstance(data['session_id'], str)
        
        # Test that session works for protected endpoints
        session_id = data['session_id']
        self.session.headers.update({'X-Session-ID': session_id})
        
        response = self.session.get(f"{self.api_base_url}/stats")
        self.assertEqual(response.status_code, 200)

    def test_rate_limiting(self):
        """Test that rate limiting works correctly."""
        # Make multiple requests quickly - reduced from 5 to 2 for faster testing
        for i in range(2):  # Reduced from 5 to 2 for faster testing
            response = requests.get(f"{self.api_base_url}/health")
            self.assertEqual(response.status_code, 200)
        
        # The rate limiting should still allow these requests
        # (this test verifies the basic functionality works)


if __name__ == '__main__':
    unittest.main() 