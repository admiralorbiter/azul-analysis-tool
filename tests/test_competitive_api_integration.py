"""
Test suite for Competitive Research API Integration

Tests the API endpoints for all competitive research features including:
- Pattern detection API endpoints
- Scoring optimization API endpoints  
- Floor line patterns API endpoints
- Board validation API endpoints
- Position library API endpoints
- Error handling and edge cases
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.app import create_test_app
from core.azul_model import AzulState
from core import azul_utils as utils


class TestCompetitiveAPIIntegration(unittest.TestCase):
    """Test cases for competitive research API integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
        
        # Create a basic game state for testing
        self.test_state = AzulState(2)
        
        # Set up a state with pattern detection opportunities
        self.pattern_state = AzulState(2)
        # Set up opponent with blue tiles in pattern line
        self.pattern_state.agents[1].lines_tile[0] = utils.Tile.BLUE
        self.pattern_state.agents[1].lines_number[0] = 1
        self.pattern_state.agents[1].grid_state[0][utils.Tile.BLUE] = 0
        # Add blue tiles to factory for blocking
        self.pattern_state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        # Set up a state with scoring optimization opportunities
        self.scoring_state = AzulState(2)
        # Set up wall with 4 tiles in row 0
        self.scoring_state.agents[0].grid_state[0] = [1, 1, 1, 1, 0]
        
        # Set up a state with floor line opportunities
        self.floor_state = AzulState(2)
        self.floor_state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.RED]
    
    def test_pattern_detection_api_endpoint(self):
        """Test the pattern detection API endpoint."""
        # Convert state to FEN string for API
        fen_string = "test_blocking_position"  # Use a known test position
        
        response = self.client.post('/api/v1/detect-patterns', 
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0,
                                      'urgency_threshold': 0.7
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('total_patterns', data)
        self.assertIn('blocking_opportunities', data)
        self.assertIn('confidence_score', data)
        self.assertIsInstance(data['total_patterns'], int)
        self.assertIsInstance(data['blocking_opportunities'], list)
        self.assertIsInstance(data['confidence_score'], float)
    
    def test_pattern_detection_api_invalid_state(self):
        """Test pattern detection API with invalid state."""
        response = self.client.post('/api/v1/detect-patterns',
                                  json={
                                      'fen_string': 'invalid_fen',
                                      'current_player': 0
                                  })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_pattern_detection_api_missing_parameters(self):
        """Test pattern detection API with missing parameters."""
        response = self.client.post('/api/v1/detect-patterns',
                                  json={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_scoring_optimization_api_endpoint(self):
        """Test the scoring optimization API endpoint."""
        fen_string = "simple_row_completion"  # Use a known test position
        
        response = self.client.post('/api/v1/detect-scoring-optimization',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('total_opportunities', data)
        self.assertIn('wall_completion_opportunities', data)
        self.assertIn('pattern_line_opportunities', data)
        self.assertIn('floor_line_opportunities', data)
        self.assertIn('multiplier_opportunities', data)
        self.assertIn('confidence_score', data)
    
    def test_scoring_optimization_api_no_opportunities(self):
        """Test scoring optimization API with no opportunities."""
        fen_string = "initial"  # Use initial position with no opportunities
        
        response = self.client.post('/api/v1/detect-scoring-optimization',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_opportunities'], 0)
        self.assertEqual(data['confidence_score'], 0.0)
    
    def test_floor_line_patterns_api_endpoint(self):
        """Test the floor line patterns API endpoint."""
        fen_string = "critical_floor_risk"  # Use a known test position
        
        response = self.client.post('/api/v1/detect-floor-line-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('total_opportunities', data)
        self.assertIn('risk_mitigation_opportunities', data)
        self.assertIn('timing_optimization_opportunities', data)
        self.assertIn('trade_off_opportunities', data)
        self.assertIn('endgame_management_opportunities', data)
        self.assertIn('blocking_opportunities', data)
        self.assertIn('efficiency_opportunities', data)
        self.assertIn('confidence_score', data)
    
    def test_floor_line_patterns_api_no_floor_tiles(self):
        """Test floor line patterns API with no floor tiles."""
        fen_string = "initial"  # Use initial position with no floor tiles
        
        response = self.client.post('/api/v1/detect-floor-line-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_opportunities'], 0)
        self.assertEqual(data['confidence_score'], 0.0)
    
    def test_pattern_line_validation_api_endpoint(self):
        """Test the pattern line validation API endpoint."""
        response = self.client.post('/api/v1/validate-pattern-line-edit',
                                  json={
                                      'current_color': -1,
                                      'new_color': utils.Tile.BLUE,
                                      'current_count': 0,
                                      'new_count': 1,
                                      'line_index': 0
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('valid', data)
        self.assertTrue(data['valid'])
    
    def test_pattern_line_validation_api_invalid_placement(self):
        """Test pattern line validation API with invalid placement."""
        response = self.client.post('/api/v1/validate-pattern-line-edit',
                                  json={
                                      'current_color': utils.Tile.BLUE,
                                      'new_color': utils.Tile.RED,
                                      'current_count': 1,
                                      'new_count': 2,
                                      'line_index': 0
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('valid', data)
        self.assertFalse(data['valid'])
        self.assertIn('error', data)
    
    def test_board_state_validation_api_endpoint(self):
        """Test the board state validation API endpoint."""
        state_dict = self.test_state.to_dict()
        
        response = self.client.post('/api/v1/validate-board-state',
                                  json={
                                      'game_state': state_dict,
                                      'validation_type': 'complete'
                                  })
        
        # This endpoint requires authentication, so expect 401
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_position_library_api_endpoint(self):
        """Test the position library API endpoint."""
        response = self.client.get('/api/v1/positions/search')
        
        # This endpoint requires authentication, so expect 401
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_position_library_api_filtered(self):
        """Test the position library API with filters."""
        response = self.client.get('/api/v1/positions/search?category=opening&difficulty=beginner')
        
        # This endpoint requires authentication, so expect 401
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_position_library_api_search(self):
        """Test the position library API with search."""
        response = self.client.get('/api/v1/positions/search?search=aggressive')
        
        # This endpoint requires authentication, so expect 401
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_position_load_api_endpoint(self):
        """Test the position load API endpoint."""
        # Create a test position with required position_id
        test_position = {
            'position_id': 'test_position_1',
            'category': 'opening',
            'difficulty': 'beginner'
        }
        
        response = self.client.post('/api/v1/positions/load',
                                  json=test_position)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('success', data)
        self.assertTrue(data['success'])
    
    def test_position_save_api_endpoint(self):
        """Test the position save API endpoint."""
        position_data = {
            'name': 'Test Save Position',
            'category': 'midgame',
            'difficulty': 'intermediate',
            'state': self.test_state.to_dict(),
            'description': 'Test position for saving'
        }
        
        response = self.client.post('/api/v1/positions/save',
                                  json=position_data)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('success', data)
        self.assertTrue(data['success'])
    
    def test_api_error_handling_malformed_json(self):
        """Test API error handling with malformed JSON."""
        response = self.client.post('/api/v1/detect-patterns',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_api_error_handling_missing_content_type(self):
        """Test API error handling with missing content type."""
        response = self.client.post('/api/v1/detect-patterns',
                                  data='{"test": "data"}')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_api_error_handling_invalid_player_id(self):
        """Test API error handling with invalid player ID."""
        state_dict = self.test_state.to_dict()
        
        response = self.client.post('/api/v1/detect-patterns',
                                  json={
                                      'state': state_dict,
                                      'player_id': 999  # Invalid player ID
                                  })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_api_concurrent_requests(self):
        """Test API handling of concurrent requests."""
        import threading
        import time

        fen_string = "test_blocking_position"  # Use a known test position
        results = []
        errors = []

        def make_request():
            try:
                response = self.client.post('/api/v1/detect-patterns',
                                          json={
                                              'fen_string': fen_string,
                                              'current_player': 0
                                          })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Start multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)
        for status_code in results:
            self.assertEqual(status_code, 200)
    
    def test_api_performance_pattern_detection(self):
        """Test pattern detection API performance."""
        import time

        fen_string = "test_blocking_position"  # Use a known test position

        start_time = time.time()
        response = self.client.post('/api/v1/detect-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.2)  # Should complete within 200ms
    
    def test_api_performance_scoring_optimization(self):
        """Test scoring optimization API performance."""
        import time

        fen_string = "simple_row_completion"  # Use a known test position

        start_time = time.time()
        response = self.client.post('/api/v1/detect-scoring-optimization',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.2)  # Should complete within 200ms
    
    def test_api_performance_floor_line_patterns(self):
        """Test floor line patterns API performance."""
        import time

        fen_string = "critical_floor_risk"  # Use a known test position

        start_time = time.time()
        response = self.client.post('/api/v1/detect-floor-line-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.2)  # Should complete within 200ms
    
    def test_api_rate_limiting(self):
        """Test API rate limiting (if implemented)."""
        # Make multiple rapid requests
        fen_string = "test_blocking_position"  # Use a known test position

        for _ in range(10):
            response = self.client.post('/api/v1/detect-patterns',
                                      json={
                                          'fen_string': fen_string,
                                          'current_player': 0
                                      })
            # All requests should succeed (rate limiting not implemented yet)
            self.assertEqual(response.status_code, 200)
    
    def test_api_cors_headers(self):
        """Test that API endpoints include CORS headers."""
        response = self.client.get('/api/v1/positions')
        
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
    
    def test_api_content_type_headers(self):
        """Test that API endpoints return correct content type."""
        response = self.client.get('/api/v1/positions')
        
        self.assertEqual(response.content_type, 'application/json')


if __name__ == '__main__':
    unittest.main() 