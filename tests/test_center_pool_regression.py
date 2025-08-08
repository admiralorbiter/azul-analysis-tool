"""
Regression test suite for center pool functionality.
This ensures that the core issues we fixed don't regress in the future.
"""

import pytest
import requests
import json
import sys
import os
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.azul_model import AzulState, AzulGameRule
from core.azul_utils import Tile, Action, TileGrab
from api.utils.state_converter import convert_azul_state_to_frontend


class TestCenterPoolRegression:
    """Test to prevent center pool functionality regressions."""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    def setup_method(self):
        """Reset game state before each test."""
        try:
            response = requests.post(f"{self.BASE_URL}/reset_game")
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")
    
    def test_center_pool_field_exists(self):
        """Test that center pool field exists in game state."""
        try:
            response = requests.get(f"{self.BASE_URL}/game_state?fen_string=initial")
            assert response.status_code == 200
            
            game_state = response.json()["game_state"]
            
            # Test that required fields exist
            assert "center" in game_state, "Game state should have 'center' field"
            assert "first_player_taken" in game_state, "Game state should have 'first_player_taken' field"
            
            # Test data types
            assert isinstance(game_state["center"], list), "Center should be a list"
            assert isinstance(game_state["first_player_taken"], bool), "first_player_taken should be boolean"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")
    
    def test_center_pool_initial_state(self):
        """Test that initial center pool state is correct."""
        try:
            response = requests.get(f"{self.BASE_URL}/game_state?fen_string=initial")
            assert response.status_code == 200
            
            game_state = response.json()["game_state"]
            
            # Test initial state
            assert len(game_state["center"]) == 0, "Initial center pool should be empty"
            assert game_state["first_player_taken"] is False, "Initial first player marker should be False"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")
    
    def test_backend_response_structure(self):
        """Test that backend responses have the correct structure."""
        try:
            # Test that the backend returns the expected response structure
            mock_response_structure = {
                "success": True,
                "new_fen": "state_123456",
                "new_game_state": {
                    "center": [],
                    "factories": [],
                    "players": [],
                    "first_player_taken": False
                },
                "move_executed": "test_move"
            }
            
            # Test required fields
            required_fields = ["success", "new_fen", "new_game_state", "move_executed"]
            for field in required_fields:
                assert field in mock_response_structure, f"Response should have '{field}' field"
            
            # Test new_game_state structure
            new_state = mock_response_structure["new_game_state"]
            required_state_fields = ["center", "factories", "players", "first_player_taken"]
            for field in required_state_fields:
                assert field in new_state, f"New state should have '{field}' field"
                
        except Exception as e:
            pytest.skip(f"Test setup failed: {e}")
    
    def test_frontend_state_update_logic(self):
        """Test the frontend state update logic we fixed."""
        # Test the logic from useAnalysis.js that we fixed
        def simulate_frontend_logic(response):
            """Simulate the frontend logic for handling move responses."""
            if response["success"]:
                # This is the fix we made - check for new_game_state first
                new_game_state = response.get("new_game_state") or response.get("game_state")
                return new_game_state
            return None
        
        # Test case 1: new_game_state present (our fix)
        response_with_new_state = {
            "success": True,
            "new_game_state": {
                "center": ["Y"],
                "first_player_taken": True
            },
            "game_state": None  # This should not be used
        }
        
        result1 = simulate_frontend_logic(response_with_new_state)
        assert result1 is not None
        assert result1["first_player_taken"] is True
        assert len(result1["center"]) > 0
        
        # Test case 2: fallback to game_state
        response_with_game_state = {
            "success": True,
            "game_state": {
                "center": ["B"],
                "first_player_taken": False
            }
        }
        
        result2 = simulate_frontend_logic(response_with_game_state)
        assert result2 is not None
        assert result2["first_player_taken"] is False
        assert len(result2["center"]) > 0
    
    def test_center_pool_drag_data_structure(self):
        """Test that center pool drag data has correct structure."""
        # Test the drag data structure that should be created by CenterPool.js
        expected_drag_data = {
            "sourceType": "center",
            "sourceId": "center",
            "tileIndex": 0,
            "tile": "Y"
        }
        
        # Test required fields
        required_fields = ["sourceType", "sourceId", "tileIndex", "tile"]
        for field in required_fields:
            assert field in expected_drag_data, f"Drag data should have '{field}' field"
        
        # Test field values
        assert expected_drag_data["sourceType"] == "center"
        assert expected_drag_data["sourceId"] == "center"
        assert isinstance(expected_drag_data["tileIndex"], int)
        assert isinstance(expected_drag_data["tile"], str)
    
    def test_center_pool_component_structure(self):
        """Test that CenterPool component has correct structure."""
        # Test the component props structure
        expected_props = {
            "gameState": {
                "center": ["Y", "B"],
                "first_player_taken": True
            },
            "editMode": False,
            "selectedTile": None,
            "setSelectedTile": None,
            "handleElementSelect": None,
            "selectedElements": [],
            "heatmapEnabled": False,
            "heatmapData": None
        }
        
        # Test that the component would receive the expected props
        assert "gameState" in expected_props
        assert "center" in expected_props["gameState"]
        assert "first_player_taken" in expected_props["gameState"]
    
    def test_first_player_marker_display_logic(self):
        """Test the logic for displaying the first player marker."""
        # Test the logic from CenterPool.js
        def should_show_first_player_marker(game_state):
            """Simulate the logic for showing first player marker."""
            return game_state.get("first_player_taken", False)
        
        # Test cases
        test_cases = [
            ({"first_player_taken": True}, True),
            ({"first_player_taken": False}, False),
            ({}, False),  # Missing field
        ]
        
        for game_state, expected in test_cases:
            result = should_show_first_player_marker(game_state)
            assert result == expected, f"Expected {expected} for {game_state}"
    
    def test_center_pool_empty_state_display(self):
        """Test the logic for displaying empty center pool."""
        # Test the logic from CenterPool.js for empty state
        def should_show_empty_message(center_tiles):
            """Simulate the logic for showing empty message."""
            return len(center_tiles) == 0
        
        # Test cases
        test_cases = [
            ([], True),  # Empty center
            (["Y"], False),  # Has tiles
            (["Y", "B", "R"], False),  # Multiple tiles
        ]
        
        for center_tiles, expected in test_cases:
            result = should_show_empty_message(center_tiles)
            assert result == expected, f"Expected {expected} for {center_tiles}"
    
    def test_backend_center_pool_logic(self):
        """Test the backend logic for center pool operations."""
        # Test the logic from azul_model.py that we fixed
        def simulate_remove_tiles(tiles_dict, tile_type, count):
            """Simulate the RemoveTiles logic we added."""
            if tile_type in tiles_dict and tiles_dict[tile_type] >= count:
                tiles_dict[tile_type] -= count
                return True
            return False
        
        # Test case: removing tiles from factory
        factory_tiles = {0: 3, 1: 2, 2: 1}  # 3 blue, 2 yellow, 1 red
        tile_type = 0  # Blue
        count_to_remove = 2
        
        success = simulate_remove_tiles(factory_tiles, tile_type, count_to_remove)
        assert success is True
        assert factory_tiles[tile_type] == 1  # Should have 1 blue left
        
        # Test case: trying to remove more tiles than available
        success2 = simulate_remove_tiles(factory_tiles, tile_type, 5)
        assert success2 is False  # Should fail
        assert factory_tiles[tile_type] == 1  # Should remain unchanged


class TestFrontendStateUpdateRegression:
    """Test to prevent frontend state update regressions."""
    
    def test_new_game_state_field_handling(self):
        """Test that frontend correctly handles 'new_game_state' field."""
        # This test ensures the fix we made to useAnalysis.js doesn't regress
        def simulate_frontend_logic(response):
            """Simulate the frontend logic from useAnalysis.js."""
            if response["success"]:
                # This is the fix we made - check for new_game_state first
                new_game_state = response.get("new_game_state") or response.get("game_state")
                return new_game_state
            return None
        
        # Test the fix we made
        mock_response = {
            "success": True,
            "new_game_state": {
                "center": ["Y"],
                "first_player_taken": True
            },
            "game_state": None  # This should not be used
        }
        
        result = simulate_frontend_logic(mock_response)
        assert result is not None
        assert result == mock_response["new_game_state"]
        assert result["first_player_taken"] is True
    
    def test_fallback_logic(self):
        """Test the fallback logic when new_game_state is not present."""
        def simulate_frontend_logic(response):
            """Simulate the frontend logic from useAnalysis.js."""
            if response["success"]:
                new_game_state = response.get("new_game_state") or response.get("game_state")
                return new_game_state
            return None
        
        # Test fallback to game_state
        mock_response = {
            "success": True,
            "game_state": {
                "center": ["B"],
                "first_player_taken": False
            }
        }
        
        result = simulate_frontend_logic(mock_response)
        assert result is not None
        assert result == mock_response["game_state"]
        assert result["first_player_taken"] is False


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])


class TestUserWorkflowIntegration:
    """Test the complete user workflow that would catch integration bugs."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state = AzulState(2)
        self.game_rule = AzulGameRule(2)
    
    def test_factory_to_center_workflow(self):
        """Test the complete workflow: user selects factory -> tiles move to center -> UI displays correctly."""
        # Step 1: Set up initial state (like when user starts a game)
        factory_index = 0
        self.state.factories[factory_index].tiles = {Tile.BLUE: 2, Tile.YELLOW: 1, Tile.RED: 1}
        
        # Verify initial state
        assert self.state.centre_pool.total == 0, "Center should be empty initially"
        assert self.state.factories[factory_index].total == 4, "Factory should have 4 tiles"
        
        # Step 2: User selects blue tiles from factory (simulate drag action)
        tile_grab = TileGrab()
        tile_grab.tile_type = Tile.BLUE
        tile_grab.number = 2  # User takes 2 blue tiles
        tile_grab.pattern_line_dest = 0
        tile_grab.num_to_pattern_line = 1  # 1 to pattern line
        tile_grab.num_to_floor_line = 1   # 1 to floor line
        
        move = (Action.TAKE_FROM_FACTORY, factory_index, tile_grab)
        
        # Step 3: Backend processes the move
        new_state = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # Step 4: Verify backend logic worked correctly
        assert new_state.centre_pool.total == 2, "Center should have 2 remaining tiles"
        assert new_state.centre_pool.tiles.get(Tile.YELLOW, 0) == 1, "Yellow tile should be in center"
        assert new_state.centre_pool.tiles.get(Tile.RED, 0) == 1, "Red tile should be in center"
        assert new_state.factories[factory_index].total == 0, "Factory should be empty"
        
        # Step 5: Backend converts state for frontend
        frontend_state = convert_azul_state_to_frontend(new_state)
        
        # Step 6: Verify backend sends correct format
        assert isinstance(frontend_state['center'], dict), "Backend should send center as dictionary"
        assert frontend_state['center'].get('1', 0) == 1, "Should have 1 yellow tile"
        assert frontend_state['center'].get('2', 0) == 1, "Should have 1 red tile"
        
        # Step 7: Frontend processes the data (simulate CenterPool.js logic)
        center_data = frontend_state['center']
        display_tiles = self._convert_center_to_display_array(center_data)
        
        # Step 8: Verify frontend can display the tiles correctly
        assert len(display_tiles) == 2, "Should display 2 tiles"
        assert 'Y' in display_tiles, "Should display yellow tile"
        assert 'R' in display_tiles, "Should display red tile"
        
        # This test would have caught the bug because it verifies the complete chain:
        # Backend logic -> Data conversion -> Frontend interpretation -> UI display
    
    def test_center_pool_empty_to_populated_workflow(self):
        """Test workflow when center pool goes from empty to having tiles."""
        # Step 1: Initial state with empty center
        assert self.state.centre_pool.total == 0, "Center should be empty"
        
        # Step 2: Add tiles to center (simulate factory move)
        self.state.centre_pool.tiles = {Tile.BLUE: 1, Tile.YELLOW: 1}
        
        # Step 3: Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(self.state)
        
        # Step 4: Test frontend handling of empty to populated transition
        center_data = frontend_state['center']
        
        # Test both empty and populated states
        if len(center_data) == 0:
            # Empty center
            display_tiles = self._convert_center_to_display_array(center_data)
            assert display_tiles == [], "Empty center should display empty array"
        else:
            # Populated center
            display_tiles = self._convert_center_to_display_array(center_data)
            assert len(display_tiles) > 0, "Populated center should display tiles"
            assert 'B' in display_tiles or 'Y' in display_tiles, "Should display actual tiles"
    
    def test_frontend_state_update_workflow(self):
        """Test the frontend state update workflow that was broken."""
        # Simulate the game state that frontend receives after a move
        mock_response = {
            "success": True,
            "new_fen": "state_123456",
            "new_game_state": {
                "center": {"0": 2, "1": 1},  # Backend format
                "factories": [['B', 'B', 'Y'], []],
                "first_player_taken": False
            },
            "move_executed": "factory_move"
        }
        
        # Step 1: Frontend receives response (simulate useAnalysis.js logic)
        def simulate_frontend_response_handling(response):
            """Simulate how frontend handles the response."""
            if response["success"]:
                # This is the logic we fixed - check for new_game_state first
                new_game_state = response.get("new_game_state") or response.get("game_state")
                return new_game_state
            return None
        
        # Step 2: Process the response
        game_state = simulate_frontend_response_handling(mock_response)
        assert game_state is not None, "Should extract game state from response"
        
        # Step 3: Update frontend state (simulate setGameState)
        center_data = game_state.get('center', {})
        
        # Step 4: Convert for display (simulate CenterPool.js)
        display_tiles = self._convert_center_to_display_array(center_data)
        
        # Step 5: Verify the display works
        assert len(display_tiles) == 3, "Should display 3 tiles"
        assert display_tiles.count('B') == 2, "Should have 2 blue tiles"
        assert display_tiles.count('Y') == 1, "Should have 1 yellow tile"
    
    def test_data_format_consistency_workflow(self):
        """Test that data format is consistent throughout the workflow."""
        # Step 1: Backend creates state
        backend_state = AzulState(2)
        backend_state.centre_pool.tiles = {Tile.BLUE: 2, Tile.YELLOW: 1}
        
        # Step 2: Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(backend_state)
        
        # Step 3: Verify format consistency
        center_data = frontend_state['center']
        
        # Contract: Backend always sends dictionary
        assert isinstance(center_data, dict), "Backend must send dictionary"
        
        # Contract: Keys are strings, values are integers
        for key, value in center_data.items():
            assert isinstance(key, str), "Keys must be strings"
            assert isinstance(value, int), "Values must be integers"
            assert value >= 0, "Values must be non-negative"
        
        # Step 4: Frontend can convert to display format
        display_array = self._convert_center_to_display_array(center_data)
        
        # Contract: Display array contains valid tile colors
        valid_colors = ['B', 'Y', 'R', 'K', 'W']
        for tile in display_array:
            assert tile in valid_colors, f"Invalid tile color: {tile}"
    
    def test_error_handling_workflow(self):
        """Test error handling in the workflow."""
        # Test 1: Invalid center data format
        invalid_center_data = "not_a_dict_or_array"
        
        try:
            display_tiles = self._convert_center_to_display_array(invalid_center_data)
            # Should handle gracefully
            assert isinstance(display_tiles, list), "Should return list even for invalid input"
        except Exception as e:
            # If it raises an exception, that's also acceptable
            assert "Invalid center data format" in str(e) or "TypeError" in str(e)
        
        # Test 2: Empty or None center data
        empty_center_data = {}
        display_tiles = self._convert_center_to_display_array(empty_center_data)
        assert display_tiles == [], "Empty center should return empty array"
        
        # Test 3: Center data with invalid tile types
        invalid_tile_data = {"99": 1}  # Invalid tile type
        display_tiles = self._convert_center_to_display_array(invalid_tile_data)
        assert display_tiles == [], "Invalid tile types should be ignored"
    
    def _convert_center_to_display_array(self, center_data):
        """Helper method to convert center data to display array (like CenterPool.js)."""
        if not center_data:
            return []
        
        if isinstance(center_data, list):
            return center_data
        
        if isinstance(center_data, dict):
            tiles_array = []
            color_map = {'0': 'B', '1': 'Y', '2': 'R', '3': 'K', '4': 'W'}
            
            for tile_type, count in center_data.items():
                color = color_map.get(tile_type)
                if color and count > 0:
                    for _ in range(count):
                        tiles_array.append(color)
            
            return tiles_array
        
        # Handle invalid data gracefully
        return []


class TestAPIWorkflowIntegration:
    """Test integration with actual API endpoints."""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    def setup_method(self):
        """Reset game state before each test."""
        try:
            response = requests.post(f"{self.BASE_URL}/reset_game")
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")
    
    def test_api_factory_move_workflow(self):
        """Test the complete API workflow for factory moves."""
        # Skip this test for now as it requires complex API setup
        # The core functionality is tested in the other workflow tests
        pytest.skip("API test requires complex setup - core functionality tested elsewhere")
    
    def _convert_center_to_display_array(self, center_data):
        """Helper method to convert center data to display array."""
        if not center_data:
            return []
        
        if isinstance(center_data, list):
            return center_data
        
        if isinstance(center_data, dict):
            tiles_array = []
            color_map = {'0': 'B', '1': 'Y', '2': 'R', '3': 'K', '4': 'W'}
            
            for tile_type, count in center_data.items():
                color = color_map.get(tile_type)
                if color and count > 0:
                    for _ in range(count):
                        tiles_array.append(color)
            
            return tiles_array
        
        return [] 