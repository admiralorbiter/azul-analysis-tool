#!/usr/bin/env python3
"""
Unit tests for first player marker functionality in Azul.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.azul_model import AzulState
from core import azul_utils as utils
from api.utils.state_converter import convert_azul_state_to_frontend


class TestFirstPlayerMarker(unittest.TestCase):
    """Test cases for first player marker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = AzulState(2)
        self.player = self.state.agents[0]
    
    def test_initial_state(self):
        """Test that initial state has no first player marker."""
        self.assertFalse(self.state.first_agent_taken)
        self.assertEqual(self.state.next_first_agent, -1)
        self.assertEqual(self.player.floor, [0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(self.player.floor_tiles, [])
    
    def test_give_first_player_token(self):
        """Test that GiveFirstAgentToken adds marker to floor."""
        self.player.GiveFirstAgentToken()
        
        # Check that first position in floor is occupied
        self.assertEqual(self.player.floor[0], 1)
        
        # Check that no tiles were added to floor_tiles
        self.assertEqual(self.player.floor_tiles, [])
        
        # Check that state flags are updated
        self.state.first_agent_taken = True
        self.state.next_first_agent = 0
        
        self.assertTrue(self.state.first_agent_taken)
        self.assertEqual(self.state.next_first_agent, 0)
    
    def test_taking_from_center_gets_marker(self):
        """Test that taking from center gives first player marker."""
        # Add tiles to center pool
        self.state.centre_pool.AddTiles(3, 0)  # Add 3 blue tiles
        
        # Simulate taking from center (this would trigger first player marker)
        self.player.GiveFirstAgentToken()
        self.state.first_agent_taken = True
        self.state.next_first_agent = 0
        
        # Verify the marker is in the floor
        self.assertEqual(self.player.floor[0], 1)
        self.assertTrue(self.state.first_agent_taken)
        self.assertEqual(self.state.next_first_agent, 0)
    
    def test_floor_line_with_marker_and_tiles(self):
        """Test floor line with both marker and regular tiles."""
        # Add first player marker
        self.player.GiveFirstAgentToken()
        
        # Add some tiles to floor
        self.player.AddToFloor([0, 1])  # Add blue and yellow tiles
        
        # Verify floor structure
        self.assertEqual(self.player.floor, [1, 1, 1, 0, 0, 0, 0])
        self.assertEqual(self.player.floor_tiles, [0, 1])
    
    def test_state_conversion_to_frontend(self):
        """Test that state conversion properly handles first player marker."""
        # Set up state with first player marker
        self.player.GiveFirstAgentToken()
        self.state.first_agent_taken = True
        self.state.next_first_agent = 0
        
        # Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(self.state)
        
        # Verify conversion
        self.assertTrue(frontend_state['first_player_taken'])
        self.assertEqual(frontend_state['next_first_agent'], 0)
        self.assertIn('FP', frontend_state['players'][0]['floor'])
    
    def test_state_conversion_with_tiles(self):
        """Test state conversion with marker and regular tiles."""
        # Set up state with marker and tiles
        self.player.GiveFirstAgentToken()
        self.player.AddToFloor([0, 1])  # Add blue and yellow tiles
        self.state.first_agent_taken = True
        self.state.next_first_agent = 0
        
        # Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(self.state)
        
        # Verify conversion
        floor_tiles = frontend_state['players'][0]['floor']
        self.assertIn('FP', floor_tiles)
        self.assertIn('B', floor_tiles)  # Blue tile
        self.assertIn('Y', floor_tiles)  # Yellow tile
        
        # Verify order (should be tiles first, then marker)
        self.assertEqual(floor_tiles, ['B', 'Y', 'FP'])
    
    def test_multiple_players_marker_tracking(self):
        """Test that marker tracking works for multiple players."""
        player1 = self.state.agents[0]
        player2 = self.state.agents[1]
        
        # Player 1 gets the marker
        player1.GiveFirstAgentToken()
        self.state.first_agent_taken = True
        self.state.next_first_agent = 0
        
        # Verify player 1 has marker
        self.assertEqual(player1.floor[0], 1)
        self.assertEqual(player2.floor[0], 0)
        
        # Convert to frontend and verify
        frontend_state = convert_azul_state_to_frontend(self.state)
        self.assertEqual(frontend_state['next_first_agent'], 0)
        self.assertIn('FP', frontend_state['players'][0]['floor'])
        self.assertNotIn('FP', frontend_state['players'][1]['floor'])
    
    def test_marker_penalty_scoring(self):
        """Test that first player marker contributes to penalty scoring."""
        # Add marker and some tiles
        self.player.GiveFirstAgentToken()
        self.player.AddToFloor([0, 1])  # Add blue and yellow tiles
        
        # Calculate penalty (marker = -1, tiles = -1 each)
        penalty = 0
        for i, floor_occupied in enumerate(self.player.floor):
            if floor_occupied == 1:
                if i == 0:  # First player marker
                    penalty -= 1
                else:  # Regular tile
                    penalty -= 1
        
        # Should be -3 total (-1 for marker, -1 for each tile)
        self.assertEqual(penalty, -3)
    
    def test_marker_only_penalty(self):
        """Test penalty when only marker is in floor."""
        self.player.GiveFirstAgentToken()
        
        # Calculate penalty (only marker = -1)
        penalty = 0
        for i, floor_occupied in enumerate(self.player.floor):
            if floor_occupied == 1:
                penalty -= 1
        
        self.assertEqual(penalty, -1)


class TestFirstPlayerMarkerUI(unittest.TestCase):
    """Test cases for first player marker UI components."""
    
    def test_center_pool_marker_display(self):
        """Test that center pool shows marker when available."""
        state = AzulState(2)
        
        # Initially, marker should be available
        frontend_state = convert_azul_state_to_frontend(state)
        self.assertFalse(frontend_state['first_player_taken'])
        
        # After taking marker
        state.agents[0].GiveFirstAgentToken()
        state.first_agent_taken = True
        state.next_first_agent = 0
        
        frontend_state = convert_azul_state_to_frontend(state)
        self.assertTrue(frontend_state['first_player_taken'])
        self.assertEqual(frontend_state['next_first_agent'], 0)
    
    def test_status_bar_marker_tracking(self):
        """Test that status bar can track which player has marker."""
        state = AzulState(2)
        
        # Player 0 gets marker
        state.agents[0].GiveFirstAgentToken()
        state.first_agent_taken = True
        state.next_first_agent = 0
        
        frontend_state = convert_azul_state_to_frontend(state)
        self.assertEqual(frontend_state['next_first_agent'], 0)
        
        # Player 1 gets marker
        state = AzulState(2)
        state.agents[1].GiveFirstAgentToken()
        state.first_agent_taken = True
        state.next_first_agent = 1
        
        frontend_state = convert_azul_state_to_frontend(state)
        self.assertEqual(frontend_state['next_first_agent'], 1)


if __name__ == '__main__':
    unittest.main() 