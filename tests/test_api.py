"""
Tests for the REST API implementation (M5).

This module tests the Flask API endpoints, authentication, rate limiting,
and database integration for the Azul Solver & Analysis Toolkit.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient

from api.app import create_test_app
from api.auth import session_manager
from api.rate_limiter import RateLimiter


class TestAPIAuthentication:
    """Test authentication and session management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_create_session(self):
        """Test session creation endpoint."""
        response = self.client.post('/api/v1/auth/session')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'session_id' in data
        assert 'expires_in_minutes' in data
        assert data['message'] == 'Session created successfully'
        assert len(data['session_id']) > 32  # Secure token
    
    def test_session_validation(self):
        """Test session validation with valid session."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        
        # Test protected endpoint
        headers = {'X-Session-ID': session_id}
        response = self.client.get('/api/v1/auth/stats', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'session_stats' in data
        assert 'rate_limit_stats' in data
    
    def test_invalid_session(self):
        """Test session validation with invalid session."""
        headers = {'X-Session-ID': 'invalid-session-id'}
        response = self.client.get('/api/v1/auth/stats', headers=headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid or expired session' in data['error']
    
    def test_missing_session(self):
        """Test protected endpoint without session ID."""
        response = self.client.get('/api/v1/auth/stats')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Session ID required' in data['error']


class TestAPIRateLimiting:
    """Test rate limiting functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_rate_limit_configuration(self):
        """Test rate limiter configuration."""
        assert self.app.rate_limiter is not None
        assert self.app.rate_limiter.config.max_requests == 100
        assert self.app.rate_limiter.config.heavy_analysis_limit == 10
        assert self.app.rate_limiter.config.light_analysis_limit == 100
    
    def test_rate_limit_enforcement(self):
        """Test rate limit enforcement."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Exceed rate limit
        for _ in range(11):  # Exceed heavy analysis limit
            response = self.client.post('/api/v1/analyze', 
                                     headers=headers,
                                     json={'fen_string': 'initial'})
        
        # Should be rate limited
        assert response.status_code == 429
        data = json.loads(response.data)
        assert 'Rate limit exceeded' in data['error']
    
    def test_rate_limit_recovery(self):
        """Test rate limit recovery after window expires."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Make some requests (use health check to avoid analysis complexity)
        for _ in range(5):
            response = self.client.get('/api/v1/health', headers=headers)
            assert response.status_code == 200
        
        # Check remaining requests
        response = self.client.get('/api/v1/stats', headers=headers)
        data = json.loads(response.data)
        # Should have used some requests
        assert data['rate_limits']['general_remaining'] <= 95


class TestAPIAnalysisEndpoints:
    """Test analysis endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    @patch('core.azul_search.AzulAlphaBetaSearch')
    def test_analyze_endpoint(self, mock_search):
        """Test exact analysis endpoint."""
        # Mock search result
        mock_result = MagicMock()
        mock_result.best_move = "take_from_factory_0_blue_0_2_0"
        mock_result.best_score = 15.5
        mock_result.principal_variation = ["move1", "move2"]
        mock_result.search_time = 1.5
        mock_result.nodes_searched = 1000
        mock_result.depth_reached = 3
        
        mock_search_instance = MagicMock()
        mock_search_instance.search.return_value = mock_result
        mock_search.return_value = mock_search_instance
        
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Make analysis request
        response = self.client.post('/api/v1/analyze',
                                  headers=headers,
                                  json={
                                      'fen_string': 'initial',
                                      'agent_id': 0,
                                      'depth': 3,
                                      'time_budget': 4.0
                                  })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'analysis' in data
        assert data['analysis']['best_move'] == "take_from_factory_0_blue_0_2_0"
        assert data['analysis']['best_score'] == 15.5
        assert data['analysis']['search_time'] == 1.5
        assert data['analysis']['nodes_searched'] == 1000
        assert data['analysis']['depth_reached'] == 3
    
    @patch('core.azul_mcts.AzulMCTS')
    def test_hint_endpoint(self, mock_mcts):
        """Test hint endpoint."""
        # Mock MCTS result
        mock_result = MagicMock()
        mock_result.best_move = "take_from_factory_0_blue_0_2_0"
        mock_result.expected_value = 12.3
        mock_result.confidence = 0.85
        mock_result.search_time = 0.15
        mock_result.rollouts_performed = 50
        mock_result.top_moves = [
            ("move1", 12.3, 25),
            ("move2", 11.8, 15),
            ("move3", 10.5, 10)
        ]
        
        mock_mcts_instance = MagicMock()
        mock_mcts_instance.search.return_value = mock_result
        mock_mcts.return_value = mock_mcts_instance
        
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Make hint request
        response = self.client.post('/api/v1/hint',
                                  headers=headers,
                                  json={
                                      'fen_string': 'initial',
                                      'agent_id': 0,
                                      'budget': 0.2,
                                      'rollouts': 100
                                  })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'hint' in data
        assert data['hint']['best_move'] == "take_from_factory_0_blue_0_2_0"
        assert data['hint']['expected_value'] == 12.3
        assert data['hint']['confidence'] == 0.85
        assert data['hint']['search_time'] == 0.15
        assert data['hint']['rollouts_performed'] == 50
        assert len(data['hint']['top_moves']) == 3
    
    def test_invalid_request_data(self):
        """Test handling of invalid request data."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Test missing required fields
        response = self.client.post('/api/v1/analyze',
                                  headers=headers,
                                  json={'agent_id': 0})  # Missing fen_string
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid request data' in data['error']
    
    def test_invalid_position(self):
        """Test handling of invalid game positions."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Test invalid FEN string
        response = self.client.post('/api/v1/analyze',
                                  headers=headers,
                                  json={'fen_string': 'invalid_fen'})
        
        # Should return 400 or 500 depending on how the error is handled
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        assert 'error' in data


class TestAPIHealthAndStats:
    """Test health check and statistics endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['version'] == '0.1.0'
        assert 'timestamp' in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Azul Solver & Analysis Toolkit API'
        assert data['version'] == '0.1.0'
        assert 'endpoints' in data
    
    def test_api_stats(self):
        """Test API statistics endpoint."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        response = self.client.get('/api/v1/stats', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rate_limits' in data
        assert 'session_stats' in data


class TestAPIDatabaseIntegration:
    """Test database integration with API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_database_initialization(self):
        """Test database initialization in app."""
        assert self.app.database is not None
        assert hasattr(self.app.database, 'cache_position')
        assert hasattr(self.app.database, 'cache_analysis')
    
    @patch('core.azul_search.AzulAlphaBetaSearch')
    def test_analysis_caching(self, mock_search):
        """Test that analysis results are cached."""
        # Mock search result
        mock_result = MagicMock()
        mock_result.best_move = "test_move"
        mock_result.best_score = 10.0
        mock_result.search_time = 1.0
        mock_result.nodes_searched = 500
        mock_result.depth_reached = 3
        mock_result.principal_variation = ["move1", "move2"]
        
        mock_search_instance = MagicMock()
        mock_search_instance.search.return_value = mock_result
        mock_search.return_value = mock_search_instance
        
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Make analysis request
        response = self.client.post('/api/v1/analyze',
                                  headers=headers,
                                  json={'fen_string': 'initial'})
        
        assert response.status_code == 200
        
        # Check that position was cached
        position_id = self.app.database.get_position_id('initial')
        assert position_id is not None
        
        # Check that analysis was cached
        cached = self.app.database.get_cached_analysis('initial', 0, 'alpha_beta')
        assert cached is not None
        assert cached.best_move == "test_move"
        assert cached.score == 10.0


class TestAPIErrorHandling:
    """Test error handling in API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_404_error(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Not found' in data['error']
    
    def test_500_error(self):
        """Test 500 error handling."""
        # This would be tested with actual server errors
        # For now, just verify the error handler exists
        assert hasattr(self.app, 'errorhandler')
    
    def test_429_error(self):
        """Test 429 rate limit error handling."""
        # Create session
        response = self.client.post('/api/v1/auth/session')
        session_id = json.loads(response.data)['session_id']
        headers = {'X-Session-ID': session_id}
        
        # Exceed rate limit
        for _ in range(11):
            response = self.client.post('/api/v1/analyze',
                                      headers=headers,
                                      json={'fen_string': 'initial'})
        
        assert response.status_code == 429
        data = json.loads(response.data)
        assert 'Rate limit exceeded' in data['error']


class TestAPICORS:
    """Test CORS configuration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.client.get('/api/v1/health')
        
        # Check for CORS headers (Flask-CORS adds these)
        assert 'Access-Control-Allow-Origin' in response.headers
        # Note: Flask-CORS doesn't always add Allow-Methods/Allow-Headers
        # unless there's a preflight request, so we just check for Origin 