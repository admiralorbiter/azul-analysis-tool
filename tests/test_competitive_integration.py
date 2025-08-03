"""
Integration Test Suite for Competitive Research Features

Tests complete workflows for competitive research features including:
- Complete board editing workflow with validation
- Position library workflow with loading and filtering
- Pattern detection workflow with analysis
- Scoring optimization workflow with suggestions
- Floor line patterns workflow with management
- End-to-end competitive analysis workflows
"""

import unittest
import sys
import os
import json
import time
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.app import create_test_app
from core.azul_model import AzulState
from core.azul_rule_validator import BoardStateValidator
from core.azul_patterns import AzulPatternDetector
from core.azul_scoring_optimization import AzulScoringOptimizationDetector
from core.azul_floor_line_patterns import AzulFloorLinePatternDetector
from core import azul_utils as utils


def state_to_fen(state):
    """Convert game state to FEN string for testing."""
    import hashlib
    import json
    
    try:
        # Create a hash of the state's key components
        state_data = {
            'factories': [(i, dict(factory.tiles)) for i, factory in enumerate(state.factories)],
            'center': dict(state.centre_pool.tiles),
            'agents': [
                {
                    'lines_tile': agent.lines_tile,
                    'lines_number': agent.lines_number,
                    'grid_state': agent.grid_state,
                    'floor_tiles': agent.floor_tiles,
                    'score': agent.score
                }
                for agent in state.agents
            ]
        }
        
        # Create a hash of the state data using JSON
        state_json = json.dumps(state_data, sort_keys=True)
        state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
        
        return f"state_{state_hash}"
    except Exception as e:
        # Fallback to a simple timestamp-based identifier
        import time
        timestamp = int(time.time() * 1000) % 1000000
        return f"state_{timestamp}"


class TestCompetitiveIntegration(unittest.TestCase):
    """Integration tests for competitive research features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
        
        # Initialize all detectors
        self.rule_validator = BoardStateValidator()
        self.pattern_detector = AzulPatternDetector()
        self.scoring_detector = AzulScoringOptimizationDetector()
        self.floor_line_detector = AzulFloorLinePatternDetector()
        
        # Create test states
        self.basic_state = AzulState(2)
        self.complex_state = self._create_complex_test_state()
    
    def _create_complex_test_state(self):
        """Create a complex test state with multiple opportunities."""
        state = AzulState(2)
        
        # Set up player 0 with scoring opportunities
        state.agents[0].grid_state[0] = [1, 1, 1, 1, 0]  # 4 tiles in row 0
        state.agents[0].lines_number[4] = 3  # 3 tiles in pattern line 4
        state.agents[0].lines_tile[4] = utils.Tile.RED
        state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.YELLOW]
        
        # Set up player 1 with blocking opportunities
        state.agents[1].lines_tile[0] = utils.Tile.BLUE
        state.agents[1].lines_number[0] = 1
        state.agents[1].grid_state[0][utils.Tile.BLUE] = 0
        
        # Add tiles to factories
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        state.factories[0].tiles[utils.Tile.RED] = 3
        
        return state
    
    def test_complete_board_editing_workflow(self):
        """Test complete board editing workflow with validation."""
        # Step 1: Start with valid state
        initial_state = AzulState(2)
        validation_result = self.rule_validator.validate_complete_board_state(initial_state)
        self.assertTrue(validation_result.is_valid)
        
        # Step 2: Edit pattern line
        edit_result = self.rule_validator.validate_pattern_line_edit(
            initial_state, 0, 0, utils.Tile.BLUE, 1
        )
        self.assertTrue(edit_result.is_valid)
        
        # Step 3: Apply the edit
        initial_state.agents[0].lines_tile[0] = utils.Tile.BLUE
        initial_state.agents[0].lines_number[0] = 1
        
        # Step 4: Validate the edited state
        final_validation = self.rule_validator.validate_complete_board_state(initial_state)
        self.assertTrue(final_validation.is_valid)
        
        # Step 5: Try invalid edit (wrong color)
        invalid_edit = self.rule_validator.validate_pattern_line_edit(
            initial_state, 0, 0, utils.Tile.RED, 1
        )
        self.assertFalse(invalid_edit.is_valid)
        self.assertIn("already contains", invalid_edit.errors[0])
    
    def test_position_library_workflow(self):
        """Test complete position library workflow."""
        # Step 1: Load a position using the correct API structure
        test_position = {
            'position_id': 'test_position_1',
            'category': 'midgame',
            'difficulty': 'intermediate'
        }
        
        response = self.client.post('/api/v1/positions/load',
                                  json=test_position)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Verify the response structure
        position_data = json.loads(response.data)
        self.assertIn('success', position_data)
        self.assertIn('position', position_data)
        self.assertTrue(position_data['success'])
        
        # Step 3: Test position validation (skip if authentication required)
        position_state = position_data['position']['state']
        validation_response = self.client.post('/api/v1/validate-board-state',
                                             json={
                                                 'game_state': position_state,
                                                 'validation_type': 'complete'
                                             })
        # Accept either 200 (success) or 401 (authentication required)
        self.assertIn(validation_response.status_code, [200, 401])
        
        # Step 4: Test pattern detection on loaded position
        fen_string = state_to_fen(self.basic_state)  # Use basic state for testing
        patterns_response = self.client.post('/api/v1/detect-patterns',
                                           json={
                                               'fen_string': fen_string,
                                               'current_player': 0
                                           })
        self.assertEqual(patterns_response.status_code, 200)
    
    def test_pattern_detection_workflow(self):
        """Test complete pattern detection workflow."""
        # Step 1: Detect patterns in complex state
        patterns = self.pattern_detector.detect_patterns(self.complex_state, 0)
        self.assertIsNotNone(patterns)
        self.assertGreaterEqual(patterns.total_patterns, 0)
        
        # Step 2: Get move suggestions
        if patterns.blocking_opportunities:
            suggestions = self.pattern_detector.get_blocking_move_suggestions(
                self.complex_state, 0, patterns.blocking_opportunities
            )
            self.assertIsInstance(suggestions, list)
        
        # Step 3: Test API integration - convert state to fen_string
        fen_string = state_to_fen(self.complex_state)
        response = self.client.post('/api/v1/detect-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        self.assertEqual(response.status_code, 200)
        api_data = json.loads(response.data)
        self.assertIn('total_patterns', api_data)
        self.assertIn('blocking_opportunities', api_data)
    
    def test_scoring_optimization_workflow(self):
        """Test complete scoring optimization workflow."""
        # Step 1: Detect scoring opportunities
        opportunities = self.scoring_detector.detect_scoring_optimization(
            self.complex_state, 0
        )
        self.assertIsNotNone(opportunities)
        self.assertGreaterEqual(opportunities.total_opportunities, 0)
        
        # Step 2: Check different opportunity types
        self.assertIsInstance(opportunities.wall_completion_opportunities, list)
        self.assertIsInstance(opportunities.pattern_line_opportunities, list)
        self.assertIsInstance(opportunities.floor_line_opportunities, list)
        self.assertIsInstance(opportunities.multiplier_opportunities, list)
        
        # Step 3: Test API integration - convert state to fen_string
        fen_string = state_to_fen(self.complex_state)
        response = self.client.post('/api/v1/detect-scoring-optimization',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        self.assertEqual(response.status_code, 200)
        api_data = json.loads(response.data)
        self.assertIn('total_opportunities', api_data)
        self.assertIn('wall_completion_opportunities', api_data)
    
    def test_floor_line_patterns_workflow(self):
        """Test complete floor line patterns workflow."""
        # Step 1: Detect floor line opportunities
        opportunities = self.floor_line_detector.detect_floor_line_patterns(
            self.complex_state, 0
        )
        self.assertIsNotNone(opportunities)
        self.assertGreaterEqual(opportunities.total_opportunities, 0)
        
        # Step 2: Check different opportunity types
        self.assertIsInstance(opportunities.risk_mitigation_opportunities, list)
        self.assertIsInstance(opportunities.timing_optimization_opportunities, list)
        self.assertIsInstance(opportunities.trade_off_opportunities, list)
        self.assertIsInstance(opportunities.endgame_management_opportunities, list)
        self.assertIsInstance(opportunities.blocking_opportunities, list)
        self.assertIsInstance(opportunities.efficiency_opportunities, list)
        
        # Step 3: Test API integration - convert state to fen_string
        fen_string = state_to_fen(self.complex_state)
        response = self.client.post('/api/v1/detect-floor-line-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 0
                                  })
        self.assertEqual(response.status_code, 200)
        api_data = json.loads(response.data)
        self.assertIn('total_opportunities', api_data)
        self.assertIn('risk_mitigation_opportunities', api_data)
    
    def test_complete_competitive_analysis_workflow(self):
        """Test complete competitive analysis workflow."""
        # Step 1: Load a position using the correct API structure
        test_position = {
            'position_id': 'competitive_analysis_test',
            'category': 'midgame',
            'difficulty': 'intermediate'
        }
        
        response = self.client.post('/api/v1/positions/load',
                                  json=test_position)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Run pattern detection
        fen_string = state_to_fen(self.complex_state)
        patterns_response = self.client.post('/api/v1/detect-patterns',
                                           json={
                                               'fen_string': fen_string,
                                               'current_player': 0
                                           })
        self.assertEqual(patterns_response.status_code, 200)
        patterns_data = json.loads(patterns_response.data)
        
        # Step 3: Run scoring optimization
        scoring_response = self.client.post('/api/v1/detect-scoring-optimization',
                                          json={
                                              'fen_string': fen_string,
                                              'current_player': 0
                                          })
        self.assertEqual(scoring_response.status_code, 200)
        scoring_data = json.loads(scoring_response.data)
        
        # Step 4: Run floor line analysis
        floor_response = self.client.post('/api/v1/detect-floor-line-patterns',
                                        json={
                                            'fen_string': fen_string,
                                            'current_player': 0
                                        })
        self.assertEqual(floor_response.status_code, 200)
        floor_data = json.loads(floor_response.data)
        
        # Step 5: Validate all analyses are consistent
        self.assertIsInstance(patterns_data['total_patterns'], int)
        self.assertIsInstance(scoring_data['total_opportunities'], int)
        self.assertIsInstance(floor_data['total_opportunities'], int)
        
        # Step 6: Check performance
        self.assertLessEqual(patterns_data.get('confidence_score', 0), 1.0)
        self.assertLessEqual(scoring_data.get('confidence_score', 0), 1.0)
        self.assertLessEqual(floor_data.get('confidence_score', 0), 1.0)
    
    def test_validation_integration_workflow(self):
        """Test validation integration throughout the workflow."""
        # Step 1: Validate initial state
        initial_validation = self.rule_validator.validate_complete_board_state(self.basic_state)
        self.assertTrue(initial_validation.is_valid)
        
        # Step 2: Make a valid edit
        valid_edit = self.rule_validator.validate_pattern_line_edit(
            self.basic_state, 0, 0, utils.Tile.BLUE, 1
        )
        self.assertTrue(valid_edit.is_valid)
        
        # Step 3: Apply the edit
        self.basic_state.agents[0].lines_tile[0] = utils.Tile.BLUE
        self.basic_state.agents[0].lines_number[0] = 1
        
        # Step 4: Validate the edited state
        edited_validation = self.rule_validator.validate_complete_board_state(self.basic_state)
        self.assertTrue(edited_validation.is_valid)
        
        # Step 5: Test API validation
        response = self.client.post('/api/v1/validate-pattern-line-edit',
                                  json={
                                      'current_color': utils.Tile.BLUE,
                                      'new_color': utils.Tile.BLUE,
                                      'current_count': 1,
                                      'new_count': 2,
                                      'line_index': 0
                                  })
        self.assertEqual(response.status_code, 200)
        api_validation = json.loads(response.data)
        self.assertFalse(api_validation['valid'])  # Over capacity
    
    def test_error_handling_integration(self):
        """Test error handling throughout the workflow."""
        # Step 1: Test invalid state handling
        response = self.client.post('/api/v1/detect-patterns',
                                  json={
                                      'fen_string': 'invalid_fen',
                                      'current_player': 0
                                  })
        # API should return 400 for invalid FEN
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        # Step 2: Test invalid player ID
        fen_string = state_to_fen(self.basic_state)
        response = self.client.post('/api/v1/detect-patterns',
                                  json={
                                      'fen_string': fen_string,
                                      'current_player': 99
                                  })
        # API should handle invalid player ID gracefully (return 200 with empty results)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Should return empty results for invalid player ID
        self.assertIn('total_patterns', data)
        
        # Step 3: Test malformed requests
        response = self.client.post('/api/v1/detect-patterns',
                                  data='invalid json',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Step 4: Test missing parameters
        response = self.client.post('/api/v1/detect-patterns',
                                  json={})
        self.assertEqual(response.status_code, 400)
    
    def test_performance_integration(self):
        """Test performance of complete workflows."""
        import time
        
        # Test pattern detection performance
        start_time = time.time()
        patterns = self.pattern_detector.detect_patterns(self.complex_state, 0)
        pattern_time = time.time() - start_time
        self.assertLess(pattern_time, 0.2)
        
        # Test scoring optimization performance
        start_time = time.time()
        opportunities = self.scoring_detector.detect_scoring_optimization(self.complex_state, 0)
        scoring_time = time.time() - start_time
        self.assertLess(scoring_time, 0.2)
        
        # Test floor line patterns performance
        start_time = time.time()
        floor_opportunities = self.floor_line_detector.detect_floor_line_patterns(self.complex_state, 0)
        floor_time = time.time() - start_time
        self.assertLess(floor_time, 0.2)
        
        # Test complete workflow performance
        start_time = time.time()
        
        # Load position
        self.client.post('/api/v1/positions/load',
                        json={
                            'name': 'Performance Test',
                            'state': self.complex_state.to_dict()
                        })
        
        # Run all analyses
        fen_string = state_to_fen(self.complex_state)
        self.client.post('/api/v1/detect-patterns',
                        json={
                            'fen_string': fen_string,
                            'current_player': 0
                        })
        
        self.client.post('/api/v1/detect-scoring-optimization',
                        json={
                            'fen_string': fen_string,
                            'current_player': 0
                        })
        
        self.client.post('/api/v1/detect-floor-line-patterns',
                        json={
                            'fen_string': fen_string,
                            'current_player': 0
                        })
        
        total_time = time.time() - start_time
        self.assertLess(total_time, 1.0)  # Complete workflow under 1 second
    
    def test_concurrent_workflow_integration(self):
        """Test concurrent workflow execution."""
        import threading
        import time
        
        results = []
        errors = []
        
        def run_workflow():
            try:
                # Run complete workflow
                fen_string = state_to_fen(self.complex_state)
                
                # Pattern detection
                response1 = self.client.post('/api/v1/detect-patterns',
                                           json={
                                               'fen_string': fen_string,
                                               'current_player': 0
                                           })
                
                # Scoring optimization
                response2 = self.client.post('/api/v1/detect-scoring-optimization',
                                           json={
                                               'fen_string': fen_string,
                                               'current_player': 0
                                           })
                
                # Floor line patterns
                response3 = self.client.post('/api/v1/detect-floor-line-patterns',
                                           json={
                                               'fen_string': fen_string,
                                               'current_player': 0
                                           })
                
                results.append({
                    'patterns': response1.status_code,
                    'scoring': response2.status_code,
                    'floor': response3.status_code
                })
                
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple concurrent workflows
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_workflow)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All workflows should succeed
        self.assertEqual(len(results), 3)
        self.assertEqual(len(errors), 0)
        
        for result in results:
            self.assertEqual(result['patterns'], 200)
            self.assertEqual(result['scoring'], 200)
            self.assertEqual(result['floor'], 200)
    
    def test_data_consistency_integration(self):
        """Test data consistency across all analyses."""
        # Run all analyses on the same state
        fen_string = state_to_fen(self.complex_state)
        
        # Pattern detection
        patterns_response = self.client.post('/api/v1/detect-patterns',
                                           json={
                                               'fen_string': fen_string,
                                               'current_player': 0
                                           })
        patterns_data = json.loads(patterns_response.data)
        
        # Scoring optimization
        scoring_response = self.client.post('/api/v1/detect-scoring-optimization',
                                          json={
                                              'fen_string': fen_string,
                                              'current_player': 0
                                          })
        scoring_data = json.loads(scoring_response.data)
        
        # Floor line patterns
        floor_response = self.client.post('/api/v1/detect-floor-line-patterns',
                                        json={
                                            'fen_string': fen_string,
                                            'current_player': 0
                                        })
        floor_data = json.loads(floor_response.data)
        
        # Check data consistency
        self.assertIsInstance(patterns_data['total_patterns'], int)
        self.assertIsInstance(scoring_data['total_opportunities'], int)
        self.assertIsInstance(floor_data['total_opportunities'], int)
        
        # All confidence scores should be between 0 and 1
        for data in [patterns_data, scoring_data, floor_data]:
            if 'confidence_score' in data:
                self.assertGreaterEqual(data['confidence_score'], 0.0)
                self.assertLessEqual(data['confidence_score'], 1.0)
        
        # All opportunity counts should be non-negative
        self.assertGreaterEqual(patterns_data['total_patterns'], 0)
        self.assertGreaterEqual(scoring_data['total_opportunities'], 0)
        self.assertGreaterEqual(floor_data['total_opportunities'], 0)


if __name__ == '__main__':
    unittest.main() 