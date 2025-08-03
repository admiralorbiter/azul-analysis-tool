"""
Test suite for Azul Pattern Detection Engine (R2.1)

Tests the tile blocking detection functionality with various scenarios.
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.azul_patterns import AzulPatternDetector, BlockingOpportunity, PatternDetection
from core.azul_model import AzulState
from core import azul_utils as utils


class TestPatternDetection(unittest.TestCase):
    """Test cases for pattern detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = AzulPatternDetector()
        
    def test_detector_initialization(self):
        """Test that the pattern detector initializes correctly."""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.blocking_urgency_threshold, 0.7)
        self.assertEqual(self.detector.pattern_confidence_threshold, 0.8)
        self.assertIn(utils.Tile.BLUE, self.detector.color_names)
        self.assertIn(utils.Tile.RED, self.detector.color_names)
        
    def test_empty_position_no_patterns(self):
        """Test that an empty position has no blocking patterns."""
        # Create a fresh game state
        state = AzulState(2)  # 2-player game
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find no patterns
        self.assertEqual(patterns.total_patterns, 0)
        self.assertEqual(len(patterns.blocking_opportunities), 0)
        self.assertEqual(patterns.confidence_score, 0.0)
        
    def test_simple_blocking_opportunity(self):
        """Test detection of a simple blocking opportunity."""
        # Create a state where opponent has tiles in pattern line
        state = AzulState(2)
        
        # Set up opponent with blue tiles in pattern line 0 (needs 1 more)
        opponent = state.agents[1]
        opponent.lines_number[0] = 1  # 1 tile in pattern line 0
        opponent.lines_tile[0] = utils.Tile.BLUE  # Blue tiles
        opponent.grid_state[0][utils.Tile.BLUE] = 0  # Not on wall yet
        
        # Add blue tiles to factory for blocking
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find blocking opportunity
        self.assertEqual(patterns.total_patterns, 1)
        self.assertEqual(len(patterns.blocking_opportunities), 1)
        
        opportunity = patterns.blocking_opportunities[0]
        self.assertEqual(opportunity.target_player, 1)
        self.assertEqual(opportunity.target_pattern_line, 0)
        self.assertEqual(opportunity.target_color, utils.Tile.BLUE)
        # Check that blocking tiles are available (may include center pool)
        self.assertGreater(opportunity.blocking_tiles_available, 0)
        self.assertIn(0, opportunity.blocking_factories)
        
    def test_blocking_urgency_calculation(self):
        """Test urgency calculation for blocking opportunities."""
        # Create a state with opponent close to completing pattern line
        state = AzulState(2)
        
        # Set up opponent with 3 blue tiles in pattern line 2 (capacity 3, needs 0 more)
        opponent = state.agents[1]
        opponent.lines_number[2] = 3  # 3 tiles in pattern line 2
        opponent.lines_tile[2] = utils.Tile.BLUE
        opponent.grid_state[2][utils.Tile.BLUE] = 0  # Not on wall yet
        
        # Add blue tiles to factory
        state.factories[0].tiles[utils.Tile.BLUE] = 1
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find high urgency opportunity
        self.assertEqual(patterns.total_patterns, 1)
        opportunity = patterns.blocking_opportunities[0]
        self.assertGreaterEqual(opportunity.urgency_score, 0.8)  # High urgency
        
    def test_no_blocking_when_color_on_wall(self):
        """Test that no blocking is suggested when color is already on wall."""
        state = AzulState(2)
        
        # Set up opponent with blue tiles in pattern line
        opponent = state.agents[1]
        opponent.lines_number[0] = 1
        opponent.lines_tile[0] = utils.Tile.BLUE
        opponent.grid_state[0][utils.Tile.BLUE] = 1  # Already on wall!
        
        # Add blue tiles to factory
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find no blocking opportunities
        self.assertEqual(patterns.total_patterns, 0)
        self.assertEqual(len(patterns.blocking_opportunities), 0)
        
    def test_no_blocking_when_no_tiles_available(self):
        """Test that no blocking is suggested when no tiles are available."""
        state = AzulState(2)
        
        # Set up opponent with blue tiles in pattern line
        opponent = state.agents[1]
        opponent.lines_number[0] = 1
        opponent.lines_tile[0] = utils.Tile.BLUE
        opponent.grid_state[0][utils.Tile.BLUE] = 0
        
        # Clear all blue tiles from factories and center
        for factory in state.factories:
            if utils.Tile.BLUE in factory.tiles:
                factory.tiles[utils.Tile.BLUE] = 0
        if utils.Tile.BLUE in state.centre_pool.tiles:
            state.centre_pool.tiles[utils.Tile.BLUE] = 0
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find no blocking opportunities
        self.assertEqual(patterns.total_patterns, 0)
        self.assertEqual(len(patterns.blocking_opportunities), 0)
        
    def test_blocking_from_center_pool(self):
        """Test blocking opportunities from center pool."""
        state = AzulState(2)
        
        # Set up opponent with red tiles in pattern line
        opponent = state.agents[1]
        opponent.lines_number[1] = 1  # 1 tile in pattern line 1
        opponent.lines_tile[1] = utils.Tile.RED
        opponent.grid_state[1][utils.Tile.RED] = 0
        
        # Add red tiles to center pool
        state.centre_pool.tiles[utils.Tile.RED] = 3
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find blocking opportunity
        self.assertEqual(patterns.total_patterns, 1)
        opportunity = patterns.blocking_opportunities[0]
        self.assertEqual(opportunity.target_color, utils.Tile.RED)
        self.assertEqual(opportunity.blocking_tiles_available, 3)
        self.assertTrue(opportunity.blocking_center)
        self.assertEqual(len(opportunity.blocking_factories), 0)
        
    def test_multiple_blocking_opportunities(self):
        """Test detection of multiple blocking opportunities."""
        state = AzulState(2)
        
        # Set up opponent with multiple pattern lines
        opponent = state.agents[1]
        
        # Pattern line 0: 1 blue tile (needs 0 more)
        opponent.lines_number[0] = 1
        opponent.lines_tile[0] = utils.Tile.BLUE
        opponent.grid_state[0][utils.Tile.BLUE] = 0
        
        # Pattern line 2: 2 red tiles (needs 1 more)
        opponent.lines_number[2] = 2
        opponent.lines_tile[2] = utils.Tile.RED
        opponent.grid_state[2][utils.Tile.RED] = 0
        
        # Add tiles to factories
        state.factories[0].tiles[utils.Tile.BLUE] = 1
        state.factories[1].tiles[utils.Tile.RED] = 2
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should find 2 blocking opportunities
        self.assertEqual(patterns.total_patterns, 2)
        self.assertEqual(len(patterns.blocking_opportunities), 2)
        
        # Sort by urgency (should be sorted automatically)
        opportunities = patterns.blocking_opportunities
        self.assertGreaterEqual(opportunities[0].urgency_score, opportunities[1].urgency_score)
        
    def test_move_suggestions_generation(self):
        """Test generation of move suggestions for blocking."""
        state = AzulState(2)
        
        # Set up blocking opportunity
        opponent = state.agents[1]
        opponent.lines_number[0] = 1
        opponent.lines_tile[0] = utils.Tile.BLUE
        opponent.grid_state[0][utils.Tile.BLUE] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 3
        
        # Get move suggestions
        patterns = self.detector.detect_patterns(state, 0)
        suggestions = self.detector.get_blocking_move_suggestions(
            state, 0, patterns.blocking_opportunities
        )
        
        # Should have suggestions
        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['type'], 'blocking')
        self.assertEqual(suggestion['target_opponent'], 1)
        self.assertEqual(suggestion['target_color'], utils.Tile.BLUE)
        self.assertIn('suggested_action', suggestion)
        
    def test_urgency_threshold_filtering(self):
        """Test that low urgency opportunities are filtered out."""
        # Create a detector with higher threshold
        detector = AzulPatternDetector()
        detector.blocking_urgency_threshold = 0.9  # Very high threshold
        
        state = AzulState(2)
        
        # Set up opponent with few tiles (low urgency)
        opponent = state.agents[1]
        opponent.lines_number[0] = 1  # Only 1 tile in pattern line 0
        opponent.lines_tile[0] = utils.Tile.BLUE
        opponent.grid_state[0][utils.Tile.BLUE] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 4  # Many tiles available
        
        # Detect patterns
        patterns = detector.detect_patterns(state, 0)
        
        # Should find no patterns due to high threshold
        self.assertEqual(patterns.total_patterns, 0)
        
    def test_color_name_mapping(self):
        """Test color name mapping for display."""
        self.assertEqual(self.detector.color_names[utils.Tile.BLUE], "blue")
        self.assertEqual(self.detector.color_names[utils.Tile.RED], "red")
        self.assertEqual(self.detector.color_names[utils.Tile.YELLOW], "yellow")
        self.assertEqual(self.detector.color_names[utils.Tile.BLACK], "black")
        self.assertEqual(self.detector.color_names[utils.Tile.WHITE], "white")
        
    def test_confidence_calculation(self):
        """Test pattern confidence calculation."""
        # Create multiple high-urgency opportunities
        state = AzulState(2)
        
        # Set up multiple opponents with high-urgency opportunities
        for player_id in [1]:  # Just opponent 1 for simplicity
            opponent = state.agents[player_id]
            for line in range(3):
                opponent.lines_number[line] = line + 1  # Close to completion
                opponent.lines_tile[line] = line  # Different colors
                opponent.grid_state[line][line] = 0  # Not on wall
                
                # Add tiles to factory
                state.factories[0].tiles[line] = 1
        
        # Detect patterns
        patterns = self.detector.detect_patterns(state, 0)
        
        # Should have high confidence with multiple high-urgency patterns
        self.assertGreater(patterns.total_patterns, 0)
        self.assertGreater(patterns.confidence_score, 0.5)
        
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with invalid player ID
        state = AzulState(2)
        patterns = self.detector.detect_patterns(state, 999)  # Invalid player
        self.assertEqual(patterns.total_patterns, 0)
        
        # Test with None state (should handle gracefully)
        try:
            patterns = self.detector.detect_patterns(None, 0)
            self.assertEqual(patterns.total_patterns, 0)
        except Exception as e:
            self.fail(f"Should handle None state gracefully: {e}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 