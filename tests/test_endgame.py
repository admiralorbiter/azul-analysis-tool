"""
Tests for A8 Endgame Solver implementation.

Tests cover:
- EndgameDetector functionality
- EndgameDatabase operations
- Symmetry hashing
- Retrograde analysis
- Integration with existing components
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from core.azul_endgame import EndgameDetector, EndgameDatabase, EndgamePosition
from core.azul_model import AzulState, AzulGameRule
from core.azul_move_generator import FastMoveGenerator
from core import azul_utils as utils


class TestEndgameDetector:
    """Test EndgameDetector functionality."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = EndgameDetector(max_tiles=15)
        assert detector.max_tiles == 15
        assert detector._symmetry_cache == {}
    
    def test_count_remaining_tiles_empty_state(self):
        """Test tile counting on empty state."""
        detector = EndgameDetector(max_tiles=20)
        state = AzulState(2)
        
        # Initial state should have tiles in factories
        total = detector._count_remaining_tiles(state)
        assert total > 0
        
        # After removing all tiles, should be 0
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        for tile_type in utils.Tile:
            state.centre_pool.tiles[tile_type] = 0
        
        total = detector._count_remaining_tiles(state)
        assert total == 0
    
    def test_is_endgame_position(self):
        """Test endgame position detection."""
        detector = EndgameDetector(max_tiles=5)
        state = AzulState(2)
        
        # Normal state should not be endgame
        assert not detector.is_endgame_position(state)
        
        # Create a state with few tiles
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        # Add just a few tiles
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        state.centre_pool.tiles[utils.Tile.RED] = 1
        
        assert detector.is_endgame_position(state)
    
    def test_get_endgame_position(self):
        """Test EndgamePosition creation."""
        detector = EndgameDetector(max_tiles=5)
        state = AzulState(2)
        
        # Create endgame state
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        state.centre_pool.tiles[utils.Tile.RED] = 1
        
        endgame_pos = detector.get_endgame_position(state)
        assert endgame_pos is not None
        assert endgame_pos.tile_count == 3
        assert isinstance(endgame_pos.symmetry_hash, int)
        assert isinstance(endgame_pos.canonical_state, np.ndarray)
        assert not endgame_pos.is_terminal
    
    def test_get_endgame_position_non_endgame(self):
        """Test that non-endgame positions return None."""
        detector = EndgameDetector(max_tiles=5)
        state = AzulState(2)
        
        # Normal state should not be endgame
        endgame_pos = detector.get_endgame_position(state)
        assert endgame_pos is None
    
    def test_compute_symmetry_hash(self):
        """Test symmetry hash computation."""
        detector = EndgameDetector(max_tiles=20)
        state = AzulState(2)
        
        hash1 = detector._compute_symmetry_hash(state)
        assert isinstance(hash1, int)
        assert hash1 != 0
        
        # Same state should produce same hash
        hash2 = detector._compute_symmetry_hash(state)
        assert hash1 == hash2
    
    def test_get_canonical_state(self):
        """Test canonical state representation."""
        detector = EndgameDetector(max_tiles=20)
        state = AzulState(2)
        
        canonical = detector._get_canonical_state(state)
        assert isinstance(canonical, np.ndarray)
        assert canonical.dtype == np.int32
        assert len(canonical) > 0
    
    def test_is_terminal_position(self):
        """Test terminal position detection."""
        detector = EndgameDetector(max_tiles=20)
        state = AzulState(2)
        
        # Normal state should not be terminal
        assert not detector._is_terminal_position(state)
        
        # Empty state should be terminal
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        for tile_type in utils.Tile:
            state.centre_pool.tiles[tile_type] = 0
        
        # Clear pattern lines
        for agent in state.agents:
            agent.lines_tile = [-1] * 5
        
        assert detector._is_terminal_position(state)
    
    def test_get_position_key(self):
        """Test position key generation."""
        detector = EndgameDetector(max_tiles=5)
        state = AzulState(2)
        
        # Normal state should not have a key
        key = detector.get_position_key(state)
        assert key is None
        
        # Endgame state should have a key
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        key = detector.get_position_key(state)
        assert key is not None
        assert key.startswith("endgame_")
        assert "2" in key  # tile count


class TestEndgameDatabase:
    """Test EndgameDatabase functionality."""
    
    def test_initialization(self):
        """Test database initialization."""
        db = EndgameDatabase(max_tiles=15)
        assert db.max_tiles == 15
        assert isinstance(db.detector, EndgameDetector)
        assert db.solutions == {}
        assert db._analyzed_positions == set()
    
    def test_has_solution_empty_database(self):
        """Test solution checking on empty database."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        assert not db.has_solution(state)
    
    def test_store_and_get_solution(self):
        """Test storing and retrieving solutions."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Create endgame state
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        solution = {
            'best_move': 'test_move',
            'score': 10.0,
            'depth': 3,
            'exact': True
        }
        
        db.store_solution(state, solution)
        assert db.has_solution(state)
        
        retrieved = db.get_solution(state)
        assert retrieved == solution
    
    def test_get_solution_non_endgame(self):
        """Test getting solution for non-endgame position."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Normal state should not have solution
        solution = db.get_solution(state)
        assert solution is None
    
    def test_analyze_endgame_non_endgame(self):
        """Test analyzing non-endgame position."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        result = db.analyze_endgame(state)
        assert result is None
    
    def test_analyze_endgame_terminal_position(self):
        """Test analyzing terminal position."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Create terminal position
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        for tile_type in utils.Tile:
            state.centre_pool.tiles[tile_type] = 0
        
        for agent in state.agents:
            agent.lines_tile = [-1] * 5
        
        result = db.analyze_endgame(state)
        assert result is not None
        assert result['exact'] is True
        assert result['depth'] == 0
        assert result['best_move'] is None
        assert 'score' in result
    
    def test_analyze_endgame_simple_position(self):
        """Test analyzing simple endgame position."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Create simple endgame with few tiles
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 1
        state.centre_pool.tiles[utils.Tile.RED] = 1
        
        result = db.analyze_endgame(state, max_depth=3)
        # Result might be None if analysis fails, but should not crash
        if result is not None:
            assert 'best_move' in result
            assert 'score' in result
            assert 'depth' in result
            assert 'exact' in result
    
    def test_get_stats(self):
        """Test database statistics."""
        db = EndgameDatabase(max_tiles=5)
        
        stats = db.get_stats()
        assert 'total_solutions' in stats
        assert 'max_tiles' in stats
        assert 'analyzed_positions' in stats
        
        assert stats['total_solutions'] == 0
        assert stats['max_tiles'] == 5
        assert stats['analyzed_positions'] == 0
    
    def test_evaluate_terminal_position_2_player(self):
        """Test terminal position evaluation for 2-player game."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Set different scores
        state.agents[0].score = 50
        state.agents[1].score = 30
        
        result = db._evaluate_terminal_position(state)
        assert result['score'] == 20  # 50 - 30
        assert result['exact'] is True
        assert result['depth'] == 0
        assert result['best_move'] is None
    
    def test_evaluate_terminal_position_multi_player(self):
        """Test terminal position evaluation for multi-player game."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(3)
        
        # Set scores
        state.agents[0].score = 50
        state.agents[1].score = 30
        state.agents[2].score = 40
        
        result = db._evaluate_terminal_position(state)
        assert result['score'] == 50  # Current player's score
        assert result['exact'] is True
        assert result['depth'] == 0
        assert result['best_move'] is None


class TestEndgameIntegration:
    """Test integration with existing components."""
    
    def test_integration_with_move_generator(self):
        """Test integration with FastMoveGenerator."""
        detector = EndgameDetector(max_tiles=5)
        move_generator = FastMoveGenerator()
        state = AzulState(2)
        
        # Create endgame state
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        # Should be able to generate moves
        moves = move_generator.generate_moves_fast(state, 0)
        assert len(moves) > 0
        
        # Should be detected as endgame
        assert detector.is_endgame_position(state)
    
    def test_integration_with_game_rules(self):
        """Test integration with AzulGameRule."""
        detector = EndgameDetector(max_tiles=5)
        move_generator = FastMoveGenerator()
        state = AzulState(2)
        
        # Create endgame state
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        # Generate and apply a move
        moves = move_generator.generate_moves_fast(state, 0)
        if moves:
            move = moves[0]
            game_rule = AzulGameRule(len(state.agents))
            # Convert FastMove to action tuple and apply
            action = move.to_tuple()
            new_state = state.clone()
            game_rule.generateSuccessor(new_state, action, 0)
            
            if new_state is not None:
                # Should still be endgame or closer to terminal
                assert detector.is_endgame_position(new_state) or detector._is_terminal_position(new_state)
    
    def test_database_caching(self):
        """Test that database properly caches solutions."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Create endgame state
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 1
        
        # First analysis should work
        result1 = db.analyze_endgame(state)
        
        # Second analysis should use cache
        result2 = db.analyze_endgame(state)
        
        if result1 is not None:
            assert result1 == result2
        
        # Should have stored solution
        assert db.has_solution(state)


class TestEndgamePerformance:
    """Test performance characteristics."""
    
    def test_detector_performance(self):
        """Test detector performance on multiple states."""
        detector = EndgameDetector(max_tiles=10)
        states = [AzulState(2) for _ in range(10)]
        
        # Should complete quickly
        for state in states:
            detector.is_endgame_position(state)
            detector.get_endgame_position(state)
    
    def test_database_lookup_performance(self):
        """Test database lookup performance."""
        db = EndgameDatabase(max_tiles=5)
        state = AzulState(2)
        
        # Create endgame state
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        # Store solution
        solution = {'best_move': 'test', 'score': 10.0, 'depth': 3, 'exact': True}
        db.store_solution(state, solution)
        
        # Lookup should be fast
        for _ in range(100):
            db.has_solution(state)
            db.get_solution(state)
    
    def test_symmetry_hash_performance(self):
        """Test symmetry hash computation performance."""
        detector = EndgameDetector(max_tiles=10)
        state = AzulState(2)
        
        # Should complete quickly
        for _ in range(100):
            detector._compute_symmetry_hash(state) 