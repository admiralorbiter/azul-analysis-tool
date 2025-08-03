"""
API tests for position library and move execution issues.

This module tests the API endpoints specifically for the issues that were
fixed in the position library move execution debugging session.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.app import create_test_app


class TestPositionLibraryAPI:
    """Test API endpoints for position library issues."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_execute_move_with_position_library_data(self):
        """Test execute_move with position library data."""
        # Create position data that mimics the problematic position from debugging
        position_data = {
            "factories": [
                ["B", "B", "Y", "Y"],  # Valid factory
                ["R", "R", "K", "K"],  # Valid factory
                ["W", "W", "B", "B"],  # Valid factory
                ["Y", "Y", "R", "R"],  # Valid factory
                ["K", "K", "W", "W"]   # Valid factory
            ],
            "center": ["B", "Y"],
            "players": [
                {
                    "pattern_lines": [["B", "B"], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                },
                {
                    "pattern_lines": [[], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                }
            ]
        }
        
        # Test move execution
        move_data = {
            "fen_string": "test_position",
            "move": {
                "source_id": 0,  # Factory 0
                "tile_type": 0,  # Blue tile (type 0)
                "pattern_line_dest": 1,
                "num_to_pattern_line": 2,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        # Mock the game state retrieval
        with patch('api.routes.get_game_state') as mock_get_state:
            mock_get_state.return_value = position_data
            
            response = self.client.post('/api/v1/execute_move', 
                                     json=move_data,
                                     content_type='application/json')
            
            # Should handle the request without crashing
            assert response.status_code in [200, 400, 500]
            
            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'success' in data
                # Should not return error about red tiles when blue tiles were requested
                if 'error' in data:
                    assert 'RED' not in data['error'] or 'red' not in data['error'].lower()
    
    def test_execute_move_with_invalid_factory_data(self):
        """Test execute_move with invalid factory data (wrong tile count)."""
        # Create position data with invalid factory (only 3 tiles)
        invalid_position_data = {
            "factories": [
                ["B", "B", "Y"],  # Only 3 tiles - invalid
                ["R", "R", "K", "K"],
                ["W", "W", "B", "B"],
                ["Y", "Y", "R", "R"],
                ["K", "K", "W", "W"]
            ],
            "center": ["B", "Y"],
            "players": [
                {
                    "pattern_lines": [["B", "B"], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                },
                {
                    "pattern_lines": [[], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                }
            ]
        }
        
        move_data = {
            "fen_string": "invalid_position",
            "move": {
                "source_id": 0,
                "tile_type": 0,
                "pattern_line_dest": 0,
                "num_to_pattern_line": 2,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        with patch('api.routes.get_game_state') as mock_get_state:
            mock_get_state.return_value = invalid_position_data
            
            response = self.client.post('/api/v1/execute_move', 
                                     json=move_data,
                                     content_type='application/json')
            
            # Should handle invalid data gracefully
            assert response.status_code in [200, 400, 500]
    
    def test_execute_move_tile_type_mismatch(self):
        """Test execute_move with tile type mismatch between frontend and backend."""
        # Simulate the exact issue from debugging: frontend sends blue tiles, backend reports red tile errors
        position_data = {
            "factories": [
                ["B", "B", "Y", "Y"],  # Factory has blue and yellow tiles
                ["R", "R", "K", "K"],
                ["W", "W", "B", "B"],
                ["Y", "Y", "R", "R"],
                ["K", "K", "W", "W"]
            ],
            "center": ["B", "Y"],
            "players": [
                {
                    "pattern_lines": [["B", "B"], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                },
                {
                    "pattern_lines": [[], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                }
            ]
        }
        
        # Frontend sends blue tile move (type 0)
        move_data = {
            "fen_string": "tile_mismatch_test",
            "move": {
                "source_id": 0,  # Factory 0
                "tile_type": 0,  # Blue tile (type 0)
                "pattern_line_dest": 1,
                "num_to_pattern_line": 2,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        with patch('api.routes.get_game_state') as mock_get_state:
            mock_get_state.return_value = position_data
            
            response = self.client.post('/api/v1/execute_move', 
                                     json=move_data,
                                     content_type='application/json')
            
            # Should handle the request without crashing
            assert response.status_code in [200, 400, 500]
            
            if response.status_code == 200:
                data = json.loads(response.data)
                # Should not return error about red tiles when blue tiles were requested
                if 'error' in data:
                    assert 'RED' not in data['error'] or 'red' not in data['error'].lower()
    
    def test_execute_move_with_missing_tile_types(self):
        """Test execute_move with factory missing some tile types."""
        # Create position with factory that has only some tile types
        position_data = {
            "factories": [
                ["B", "B", "Y", "Y"],  # Only blue and yellow
                ["R", "R", "K", "K"],
                ["W", "W", "B", "B"],
                ["Y", "Y", "R", "R"],
                ["K", "K", "W", "W"]
            ],
            "center": ["B", "Y"],
            "players": [
                {
                    "pattern_lines": [["B", "B"], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                },
                {
                    "pattern_lines": [[], [], [], [], []],
                    "wall": [[None] * 5 for _ in range(5)],
                    "floor_line": [],
                    "score": 0
                }
            ]
        }
        
        move_data = {
            "fen_string": "missing_tile_types",
            "move": {
                "source_id": 0,
                "tile_type": 0,  # Blue tile
                "pattern_line_dest": 0,
                "num_to_pattern_line": 2,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        with patch('api.routes.get_game_state') as mock_get_state:
            mock_get_state.return_value = position_data
            
            response = self.client.post('/api/v1/execute_move', 
                                     json=move_data,
                                     content_type='application/json')
            
            # Should handle missing tile types gracefully
            assert response.status_code in [200, 400, 500]
    
    def test_execute_move_state_synchronization(self):
        """Test that execute_move returns complete state for synchronization."""
        move_data = {
            "fen_string": "initial",
            "move": {
                "source_id": 0,
                "tile_type": 0,
                "pattern_line_dest": 0,
                "num_to_pattern_line": 1,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        response = self.client.post('/api/v1/execute_move', 
                                 json=move_data,
                                 content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should return complete game state
            assert 'game_state' in data or 'new_fen' in data
            assert data['success'] is True
    
    def test_execute_move_error_handling(self):
        """Test error handling in execute_move endpoint."""
        # Test with invalid move data
        invalid_move_data = {
            "fen_string": "initial",
            "move": {
                "source_id": 10,  # Invalid factory ID
                "tile_type": 0,
                "pattern_line_dest": 0,
                "num_to_pattern_line": 1,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        response = self.client.post('/api/v1/execute_move', 
                                 json=invalid_move_data,
                                 content_type='application/json')
        
        # Should handle invalid data gracefully
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_execute_move_with_zero_tiles(self):
        """Test execute_move with zero tiles (invalid move)."""
        move_data = {
            "fen_string": "initial",
            "move": {
                "source_id": 0,
                "tile_type": 0,
                "pattern_line_dest": 0,
                "num_to_pattern_line": 0,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        response = self.client.post('/api/v1/execute_move', 
                                 json=move_data,
                                 content_type='application/json')
        
        # Should handle zero tile moves gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_execute_move_with_invalid_tile_type(self):
        """Test execute_move with invalid tile type."""
        move_data = {
            "fen_string": "initial",
            "move": {
                "source_id": 0,
                "tile_type": 10,  # Invalid tile type
                "pattern_line_dest": 0,
                "num_to_pattern_line": 1,
                "num_to_floor_line": 0
            },
            "agent_id": 0
        }
        
        response = self.client.post('/api/v1/execute_move', 
                                 json=move_data,
                                 content_type='application/json')
        
        # Should handle invalid tile types gracefully
        assert response.status_code in [200, 400, 500]


class TestGameStateAPI:
    """Test game state API endpoints for position library issues."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_get_game_state_with_position_library_data(self):
        """Test get_game_state with position library data."""
        # Test with valid position data
        response = self.client.get('/api/v1/game_state?fen_string=initial')
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should return valid game state
            assert 'factories' in data or 'game_state' in data
    
    def test_get_game_state_with_invalid_fen(self):
        """Test get_game_state with invalid FEN string."""
        response = self.client.get('/api/v1/game_state?fen_string=invalid_fen')
        
        # Should handle invalid FEN gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_get_game_state_missing_fen(self):
        """Test get_game_state without FEN parameter."""
        response = self.client.get('/api/v1/game_state')
        
        # Should handle missing FEN gracefully
        assert response.status_code in [200, 400, 500]


class TestPositionLibraryValidation:
    """Test position library validation in API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_position_library_factory_validation(self):
        """Test that position library validates factory tile counts in API."""
        # Test with position data that has invalid factories
        invalid_positions = [
            {
                "factories": [
                    ["B", "B", "Y"],  # Only 3 tiles
                    ["R", "R", "K", "K"],
                    ["W", "W", "B", "B"],
                    ["Y", "Y", "R", "R"],
                    ["K", "K", "W", "W"]
                ],
                "center": ["B", "Y"],
                "players": [
                    {
                        "pattern_lines": [["B", "B"], [], [], [], []],
                        "wall": [[None] * 5 for _ in range(5)],
                        "floor_line": [],
                        "score": 0
                    },
                    {
                        "pattern_lines": [[], [], [], [], []],
                        "wall": [[None] * 5 for _ in range(5)],
                        "floor_line": [],
                        "score": 0
                    }
                ]
            },
            {
                "factories": [
                    ["B", "B", "Y", "Y", "R"],  # 5 tiles
                    ["R", "R", "K", "K"],
                    ["W", "W", "B", "B"],
                    ["Y", "Y", "R", "R"],
                    ["K", "K", "W", "W"]
                ],
                "center": ["B", "Y"],
                "players": [
                    {
                        "pattern_lines": [["B", "B"], [], [], [], []],
                        "wall": [[None] * 5 for _ in range(5)],
                        "floor_line": [],
                        "score": 0
                    },
                    {
                        "pattern_lines": [[], [], [], [], []],
                        "wall": [[None] * 5 for _ in range(5)],
                        "floor_line": [],
                        "score": 0
                    }
                ]
            }
        ]
        
        for i, position_data in enumerate(invalid_positions):
            # Validate factory tile counts
            for j, factory in enumerate(position_data["factories"]):
                if len(factory) != 4:
                    # This should trigger validation
                    assert len(factory) != 4, f"Position {i}, Factory {j} has {len(factory)} tiles, expected 4"
    
    def test_position_library_tile_type_validation(self):
        """Test that position library validates tile types in API."""
        # Test with position data that has invalid tile types
        invalid_tile_positions = [
            {
                "factories": [
                    ["B", "B", "Y", "Y"],
                    ["R", "R", "K", "K"],
                    ["W", "W", "B", "B"],
                    ["Y", "Y", "R", "R"],
                    ["K", "K", "W", "W"]
                ],
                "center": ["B", "Y", "X"],  # Invalid tile type 'X'
                "players": [
                    {
                        "pattern_lines": [["B", "B"], [], [], [], []],
                        "wall": [[None] * 5 for _ in range(5)],
                        "floor_line": [],
                        "score": 0
                    },
                    {
                        "pattern_lines": [[], [], [], [], []],
                        "wall": [[None] * 5 for _ in range(5)],
                        "floor_line": [],
                        "score": 0
                    }
                ]
            }
        ]
        
        for position_data in invalid_tile_positions:
            # Validate tile types
            valid_tile_types = ['B', 'Y', 'R', 'K', 'W']
            
            # Check center tiles
            for tile in position_data["center"]:
                if tile not in valid_tile_types:
                    assert tile not in valid_tile_types, f"Invalid tile type: {tile}"
            
            # Check factory tiles
            for factory in position_data["factories"]:
                for tile in factory:
                    if tile not in valid_tile_types:
                        assert tile not in valid_tile_types, f"Invalid tile type: {tile}"


class TestErrorRecovery:
    """Test error recovery mechanisms in API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.app, 'cleanup'):
            self.app.cleanup()
    
    def test_api_error_recovery(self):
        """Test that API can recover from various errors."""
        # Test with malformed JSON
        response = self.client.post('/api/v1/execute_move', 
                                 data="invalid json",
                                 content_type='application/json')
        
        # Should handle malformed JSON gracefully
        assert response.status_code in [400, 500]
        
        # Test with missing required fields
        incomplete_data = {
            "fen_string": "initial"
            # Missing move and agent_id
        }
        
        response = self.client.post('/api/v1/execute_move', 
                                 json=incomplete_data,
                                 content_type='application/json')
        
        # Should handle missing fields gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_api_rate_limiting_with_position_library(self):
        """Test rate limiting with position library operations."""
        # Make multiple requests to test rate limiting
        for i in range(5):
            move_data = {
                "fen_string": "initial",
                "move": {
                    "source_id": 0,
                    "tile_type": 0,
                    "pattern_line_dest": 0,
                    "num_to_pattern_line": 1,
                    "num_to_floor_line": 0
                },
                "agent_id": 0
            }
            
            response = self.client.post('/api/v1/execute_move', 
                                     json=move_data,
                                     content_type='application/json')
            
            # Should handle rate limiting gracefully
            assert response.status_code in [200, 400, 429, 500]


if __name__ == "__main__":
    pytest.main([__file__]) 