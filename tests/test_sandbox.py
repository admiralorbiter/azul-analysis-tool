"""
Unit tests for the What-if Sandbox functionality (D4).

Tests the move execution API, validation, and error handling.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import api.routes
from core.azul_model import AzulState
from core.azul_move_generator import FastMoveGenerator


class TestMoveConversion:
    """Test move format conversion functions."""
    
    def test_convert_frontend_move_to_engine_factory(self):
        """Test converting frontend move from factory to engine format."""
        frontend_move = {
            'source_id': 2,
            'tile_type': 1,  # blue
            'pattern_line_dest': 3,
            'num_to_pattern_line': 2,
            'num_to_floor_line': 0
        }
        
        engine_move = api.routes.convert_frontend_move_to_engine(frontend_move)
        
        assert engine_move['action_type'] == 0  # factory
        assert engine_move['source_id'] == 2
        assert engine_move['tile_type'] == 1
        assert engine_move['pattern_line_dest'] == 3
        assert engine_move['num_to_pattern_line'] == 2
        assert engine_move['num_to_floor_line'] == 0
    
    def test_convert_frontend_move_to_engine_center(self):
        """Test converting frontend move from center to engine format."""
        frontend_move = {
            'source_id': -1,  # center
            'tile_type': 2,  # yellow
            'pattern_line_dest': -1,  # floor
            'num_to_pattern_line': 0,
            'num_to_floor_line': 1
        }
        
        engine_move = api.routes.convert_frontend_move_to_engine(frontend_move)
        
        assert engine_move['action_type'] == 1  # center
        assert engine_move['source_id'] == -1
        assert engine_move['tile_type'] == 2
        assert engine_move['pattern_line_dest'] == -1
        assert engine_move['num_to_pattern_line'] == 0
        assert engine_move['num_to_floor_line'] == 1
    
    def test_convert_frontend_move_to_engine_defaults(self):
        """Test converting frontend move with missing fields."""
        frontend_move = {
            'source_id': 0
        }
        
        engine_move = api.routes.convert_frontend_move_to_engine(frontend_move)
        
        assert engine_move['action_type'] == 0
        assert engine_move['source_id'] == 0
        assert engine_move['tile_type'] == 0
        assert engine_move['pattern_line_dest'] == -1
        assert engine_move['num_to_pattern_line'] == 0
        assert engine_move['num_to_floor_line'] == 0


class TestMoveMatching:
    """Test move matching functionality."""
    
    def test_find_matching_move_success(self):
        """Test finding a matching move in legal moves list."""
        engine_move = {
            'action_type': 0,
            'source_id': 1,
            'tile_type': 2,
            'pattern_line_dest': 3,
            'num_to_pattern_line': 1,
            'num_to_floor_line': 0
        }
        
        # Create mock legal moves
        mock_move1 = MagicMock()
        mock_move1.action_type = 0
        mock_move1.source_id = 1
        mock_move1.tile_type = 2
        mock_move1.pattern_line_dest = 3
        mock_move1.num_to_pattern_line = 1
        mock_move1.num_to_floor_line = 0
        
        mock_move2 = MagicMock()
        mock_move2.action_type = 1
        mock_move2.source_id = -1
        mock_move2.tile_type = 0
        mock_move2.pattern_line_dest = 0
        mock_move2.num_to_pattern_line = 1
        mock_move2.num_to_floor_line = 0
        
        legal_moves = [mock_move1, mock_move2]
        
        result = api.routes.find_matching_move(engine_move, legal_moves)
        
        assert result == mock_move1
    
    def test_find_matching_move_not_found(self):
        """Test when no matching move is found."""
        engine_move = {
            'action_type': 0,
            'source_id': 1,
            'tile_type': 2,
            'pattern_line_dest': 3,
            'num_to_pattern_line': 1,
            'num_to_floor_line': 0
        }
        
        # Create mock legal moves that don't match
        mock_move = MagicMock()
        mock_move.action_type = 1
        mock_move.source_id = -1
        mock_move.tile_type = 0
        mock_move.pattern_line_dest = 0
        mock_move.num_to_pattern_line = 1
        mock_move.num_to_floor_line = 0
        
        legal_moves = [mock_move]
        
        result = api.routes.find_matching_move(engine_move, legal_moves)
        
        assert result is None


class TestStateConversion:
    """Test state conversion functions."""
    
    def test_state_to_fen(self):
        """Test converting state to FEN string."""
        mock_state = MagicMock()
        
        result = api.routes.state_to_fen(mock_state)
        
        # Currently returns "initial" as placeholder
        assert result == "initial"


class TestSandboxIntegration:
    """Integration tests for sandbox functionality."""
    
    def test_complete_move_execution_flow(self):
        """Test complete move execution flow from frontend to backend."""
        # Frontend move data
        frontend_move = {
            'source_id': 0,
            'tile_type': 0,  # red
            'pattern_line_dest': 0,
            'num_to_pattern_line': 1,
            'num_to_floor_line': 0
        }
        
        # Convert to engine format
        engine_move = api.routes.convert_frontend_move_to_engine(frontend_move)
        
        assert engine_move['action_type'] == 0
        assert engine_move['source_id'] == 0
        assert engine_move['tile_type'] == 0
        assert engine_move['pattern_line_dest'] == 0
        assert engine_move['num_to_pattern_line'] == 1
        assert engine_move['num_to_floor_line'] == 0
        
        # Test with mock legal moves
        mock_legal_move = MagicMock()
        mock_legal_move.action_type = 0
        mock_legal_move.source_id = 0
        mock_legal_move.tile_type = 0
        mock_legal_move.pattern_line_dest = 0
        mock_legal_move.num_to_pattern_line = 1
        mock_legal_move.num_to_floor_line = 0
        
        legal_moves = [mock_legal_move]
        
        # Find matching move
        matching_move = api.routes.find_matching_move(engine_move, legal_moves)
        
        assert matching_move == mock_legal_move
    
    def test_move_validation_edge_cases(self):
        """Test edge cases in move validation."""
        # Test with invalid tile type
        frontend_move = {
            'source_id': 0,
            'tile_type': 999,  # Invalid
            'pattern_line_dest': 0,
            'num_to_pattern_line': 1,
            'num_to_floor_line': 0
        }
        
        engine_move = api.routes.convert_frontend_move_to_engine(frontend_move)
        
        assert engine_move['tile_type'] == 999
        
        # Test with negative pattern line
        frontend_move = {
            'source_id': 0,
            'tile_type': 0,
            'pattern_line_dest': -5,
            'num_to_pattern_line': 1,
            'num_to_floor_line': 0
        }
        
        engine_move = api.routes.convert_frontend_move_to_engine(frontend_move)
        
        assert engine_move['pattern_line_dest'] == -5


class TestSandboxAPI:
    """Test the sandbox API functionality."""
    
    def test_move_execution_request_model(self):
        """Test the MoveExecutionRequest model validation."""
        from api.routes import MoveExecutionRequest
        
        # Valid request
        valid_data = {
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
        
        request = MoveExecutionRequest(**valid_data)
        assert request.fen_string == 'initial'
        assert request.agent_id == 0
        assert request.move['source_id'] == 0
    
    def test_move_execution_request_defaults(self):
        """Test MoveExecutionRequest with default values."""
        from api.routes import MoveExecutionRequest
        
        # Minimal request
        minimal_data = {
            'fen_string': 'initial',
            'move': {
                'source_id': 0,
                'tile_type': 0
            }
        }
        
        request = MoveExecutionRequest(**minimal_data)
        assert request.agent_id == 0  # Default value
        assert request.move['source_id'] == 0


if __name__ == '__main__':
    pytest.main([__file__]) 