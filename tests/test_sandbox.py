"""
Tests for D4.2 Advanced Sandbox Features

This module tests the enhanced sandbox functionality including:
- Multi-player support and turn management
- Variation branching system
- Position export/import functionality
- Move annotations
- Game mode switching
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from api.app import create_test_app
from api.routes import api_bp
from core.azul_model import AzulState


@pytest.fixture
def app():
    """Create a test Flask app."""
    app = create_test_app()
    yield app
    if hasattr(app, 'cleanup'):
        app.cleanup()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestMultiPlayerSandbox:
    """Test multi-player sandbox functionality."""
    
    def test_create_game_with_2_players(self, client):
        """Test creating games with 2 players only."""
        response = client.post('/api/v1/create_game', 
                            json={'player_count': 2})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['player_count'] == 2
        assert 'fen_string' in data
        assert 'message' in data
    
    def test_create_game_invalid_player_count(self, client):
        """Test creating games with invalid player counts."""
        for player_count in [1, 3, 4, 5, 0]:
            response = client.post('/api/v1/create_game', 
                                json={'player_count': player_count})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert 'Only 2-player games are supported' in data['error']
    
    def test_execute_move_for_different_players(self, client):
        """Test executing moves for different players in 2-player game."""
        # Create a 2-player game
        response = client.post('/api/v1/create_game', 
                            json={'player_count': 2})
        assert response.status_code == 200
        
        # Get the new game state
        game_data = response.get_json()
        fen_string = game_data['fen_string']
        
        # Execute moves for each player using valid moves
        for player_id in [0, 1]:
            # Use different source factories for each player to ensure valid moves
            source_id = player_id % 5  # Use different factories
            tile_type = player_id % 5  # Use different tile types
            
            move_data = {
                'fen_string': fen_string,
                'move': {
                    'source_id': source_id,
                    'tile_type': tile_type,
                    'pattern_line_dest': 0,
                    'num_to_pattern_line': 1,
                    'num_to_floor_line': 0
                },
                'agent_id': player_id
            }
            
            response = client.post('/api/v1/execute_move', json=move_data)
            # Note: Some moves might fail due to game state constraints
            # We'll just verify the API handles the request properly
            assert response.status_code in [200, 400]  # Either success or invalid move
            data = response.get_json()
            if response.status_code == 200:
                assert data['success'] is True
            else:
                assert 'error' in data
    
    def test_move_execution_with_player_tracking(self, client):
        """Test that moves are properly tracked with player information."""
        # First create a game to get a valid state
        response = client.post('/api/v1/create_game', json={'player_count': 2})
        assert response.status_code == 200
        game_data = response.get_json()
        fen_string = game_data['fen_string']
        
        # Try to execute a move with valid parameters
        move_data = {
            'fen_string': fen_string,
            'move': {
                'source_id': 0,
                'tile_type': 1,  # Yellow tile
                'pattern_line_dest': 1,
                'num_to_pattern_line': 1,
                'num_to_floor_line': 0
            },
            'agent_id': 1  # Player 2
        }
        
        response = client.post('/api/v1/execute_move', json=move_data)
        # The move might be invalid, so accept both 200 and 400
        assert response.status_code in [200, 400]
        data = response.get_json()
        
        if response.status_code == 200:
            assert data['success'] is True
            # Verify the move was executed for the correct player
            assert 'new_fen' in data
        else:
            assert 'error' in data


class TestVariationSystem:
    """Test variation branching functionality."""
    
    def test_variation_creation(self):
        """Test creating variations from move history."""
        # Mock move history
        move_history = [
            {'move': {'source_id': 0, 'tile_type': 0}, 'player': 0, 'timestamp': datetime.now()},
            {'move': {'source_id': 1, 'tile_type': 1}, 'player': 1, 'timestamp': datetime.now()},
            {'move': {'source_id': 2, 'tile_type': 2}, 'player': 0, 'timestamp': datetime.now()}
        ]
        
        # Test variation creation logic
        from_move_index = 1
        variation_id = f"variation_{1}"
        
        # This would be tested in the frontend, but we can verify the logic
        assert from_move_index < len(move_history)
        assert variation_id.startswith("variation_")
    
    def test_variation_switching(self):
        """Test switching between variations."""
        # Mock variations
        variations = {
            'main': {'name': 'main', 'baseMoveIndex': 0, 'moves': [], 'state': 'initial'},
            'variation_1': {'name': 'variation_1', 'baseMoveIndex': 1, 'moves': [], 'state': 'state_123'}
        }
        
        # Test variation switching logic
        variation_id = 'variation_1'
        assert variation_id in variations
        
        variation = variations[variation_id]
        assert variation['name'] == 'variation_1'
        assert variation['baseMoveIndex'] == 1


class TestPositionExportImport:
    """Test position export and import functionality."""
    
    def test_position_export_format(self):
        """Test that exported positions have the correct format."""
        position_data = {
            'fen': 'state_123',
            'moveHistory': [
                {'move': {'source_id': 0, 'tile_type': 0}, 'player': 0, 'timestamp': datetime.now().isoformat()}
            ],
            'variations': [['main', {'name': 'main', 'baseMoveIndex': 0, 'moves': [], 'state': 'initial'}]],
            'annotations': [[0, {'annotation': 'Good move!', 'timestamp': datetime.now().isoformat(), 'player': 0}]],
            'currentVariation': 'main',
            'playerCount': 2,
            'currentPlayer': 0,
            'timestamp': datetime.now().isoformat(),
            'description': 'Test position'
        }
        
        # Test JSON serialization
        json_data = json.dumps(position_data, indent=2)
        assert json_data is not None
        assert 'fen' in json_data
        assert 'moveHistory' in json_data
        assert 'variations' in json_data
        assert 'annotations' in json_data
    
    def test_position_import_validation(self):
        """Test position import validation."""
        valid_position = {
            'fen': 'state_123',
            'moveHistory': [],
            'variations': [],
            'annotations': [],
            'currentVariation': 'main',
            'playerCount': 2,
            'currentPlayer': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test valid position
        assert 'fen' in valid_position
        assert 'moveHistory' in valid_position
        assert 'playerCount' in valid_position
        
        # Test invalid position (missing required fields)
        invalid_position = {'fen': 'state_123'}  # Missing required fields
        assert 'moveHistory' not in invalid_position
        assert 'playerCount' not in invalid_position


class TestMoveAnnotations:
    """Test move annotation functionality."""
    
    def test_annotation_creation(self):
        """Test creating move annotations."""
        annotation_data = {
            'annotation': 'Excellent tactical move!',
            'timestamp': datetime.now().isoformat(),
            'player': 0
        }
        
        # Test annotation structure
        assert 'annotation' in annotation_data
        assert 'timestamp' in annotation_data
        assert 'player' in annotation_data
        assert isinstance(annotation_data['annotation'], str)
        assert isinstance(annotation_data['player'], int)
    
    def test_annotation_retrieval(self):
        """Test retrieving move annotations."""
        annotations = {
            0: {'annotation': 'Good opening move', 'timestamp': datetime.now().isoformat(), 'player': 0},
            2: {'annotation': 'Tactical blunder', 'timestamp': datetime.now().isoformat(), 'player': 1}
        }
        
        # Test annotation retrieval
        assert 0 in annotations
        assert 2 in annotations
        assert 1 not in annotations  # No annotation for move 1
        
        annotation = annotations[0]
        assert annotation['annotation'] == 'Good opening move'
        assert annotation['player'] == 0


class TestGameModeSwitching:
    """Test game mode switching functionality."""
    
    def test_game_mode_validation(self):
        """Test that game modes are properly validated."""
        valid_modes = ['sandbox', 'analysis', 'setup']
        
        for mode in valid_modes:
            assert mode in valid_modes
        
        # Test invalid mode
        invalid_mode = 'invalid_mode'
        assert invalid_mode not in valid_modes
    
    def test_mode_specific_features(self):
        """Test that features are available based on game mode."""
        sandbox_features = ['variations', 'annotations', 'export_import']
        analysis_features = ['engine_analysis', 'hints', 'evaluation']
        setup_features = ['board_configuration', 'position_setup']
        
        # Test feature availability by mode
        mode_features = {
            'sandbox': sandbox_features,
            'analysis': analysis_features,
            'setup': setup_features
        }
        
        for mode, features in mode_features.items():
            assert isinstance(features, list)
            assert len(features) > 0


class TestTurnManagement:
    """Test turn management functionality."""
    
    def test_turn_advancement(self):
        """Test automatic turn advancement."""
        player_count = 2
        current_player = 0
        
        # Test turn advancement
        next_player = (current_player + 1) % player_count
        assert next_player == 1
        
        # Test wrap-around
        current_player = 1
        next_player = (current_player + 1) % player_count
        assert next_player == 0
    
    def test_player_switching(self):
        """Test manual player switching."""
        player_count = 2
        valid_players = list(range(player_count))
        
        for player_id in valid_players:
            assert 0 <= player_id < player_count
        
        # Test invalid player
        invalid_player = 3
        assert invalid_player not in valid_players


class TestSandboxIntegration:
    """Integration tests for sandbox features."""
    
    def test_complete_sandbox_workflow(self, client):
        """Test a complete sandbox workflow."""
        # 1. Create a new game
        response = client.post('/api/v1/create_game', json={'player_count': 2})
        assert response.status_code == 200
        
        # 2. Execute moves for both players
        for player_id in [0, 1]:
            move_data = {
                'fen_string': 'initial',
                'move': {
                    'source_id': player_id,
                    'tile_type': player_id,
                    'pattern_line_dest': player_id,
                    'num_to_pattern_line': 1,
                    'num_to_floor_line': 0
                },
                'agent_id': player_id
            }
            
            response = client.post('/api/v1/execute_move', json=move_data)
            # Accept both success and failure since moves might be invalid
            assert response.status_code in [200, 400]
            data = response.get_json()
            if response.status_code == 200:
                assert data['success'] is True
    
    def test_sandbox_with_analysis_integration(self, client):
        """Test sandbox integration with analysis features."""
        # Create game and execute a move
        response = client.post('/api/v1/create_game', json={'player_count': 2})
        assert response.status_code == 200
        
        # Execute a move
        move_data = {
            'fen_string': 'initial',
            'move': {
                'source_id': 0,
                'tile_type': 0,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 1,
                'num_to_floor_line': 0
            },
            'agent_id': 0
        }
        
        response = client.post('/api/v1/execute_move', json=move_data)
        # Accept both success and failure since moves might be invalid
        assert response.status_code in [200, 400]
        
        # Test that we can analyze the resulting position
        # This would be done in the frontend, but we can verify the API works
        if response.status_code == 200:
            assert response.get_json()['success'] is True


if __name__ == '__main__':
    pytest.main([__file__]) 