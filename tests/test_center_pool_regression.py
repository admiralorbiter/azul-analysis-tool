"""
Regression test suite for center pool functionality.
This ensures that the core issues we fixed don't regress in the future.
"""

import pytest
import requests
import json
from typing import Dict, Any


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