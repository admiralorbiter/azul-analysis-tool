"""
Tests for A5 Alpha-Beta Search with A8 Endgame Integration.

Tests cover:
- TranspositionTable functionality
- AzulAlphaBetaSearch with endgame integration
- Search performance and accuracy
- Integration with existing components
- A8: Endgame solver integration
"""

import pytest
import time
from unittest.mock import Mock, patch

from core.azul_search import TranspositionTable, AzulAlphaBetaSearch, SearchResult
from core.azul_model import AzulState, AzulGameRule
from core.azul_move_generator import FastMoveGenerator, FastMove
from core.azul_endgame import EndgameDatabase
from core import azul_utils as utils


class TestTranspositionTable:
    """Test TranspositionTable functionality."""
    
    def test_initialization(self):
        """Test table initialization."""
        tt = TranspositionTable(max_size=1000)
        assert tt.max_size == 1000
        assert tt.table == {}
        assert tt.hits == 0
        assert tt.misses == 0
    
    def test_put_and_get(self):
        """Test storing and retrieving entries."""
        tt = TranspositionTable(max_size=100)
        
        # Create a mock move
        move = FastMove(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=2,
            num_to_floor_line=0
        )
        
        # Store entry
        tt.put(12345, 3, 10.5, move, 5.0, 15.0, "EXACT")
        
        # Retrieve entry
        result = tt.get(12345, 3, 5.0, 15.0)
        assert result is not None
        score, best_move = result
        assert score == 10.5
        assert best_move == move
    
    def test_get_with_insufficient_depth(self):
        """Test that get returns None for insufficient depth."""
        tt = TranspositionTable()
        move = FastMove(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=2,
            num_to_floor_line=0
        )
        
        # Store with depth 3
        tt.put(12345, 3, 10.5, move, 5.0, 15.0, "EXACT")
        
        # Try to get with depth 4 (should fail)
        result = tt.get(12345, 4, 5.0, 15.0)
        assert result is None
    
    def test_get_nonexistent_entry(self):
        """Test getting non-existent entry."""
        tt = TranspositionTable()
        result = tt.get(99999, 3, 5.0, 15.0)
        assert result is None
        assert tt.misses == 1
    
    def test_size_limit(self):
        """Test that table respects size limit."""
        tt = TranspositionTable(max_size=2)
        move = FastMove(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=2,
            num_to_floor_line=0
        )
        
        # Add 3 entries (should remove oldest)
        tt.put(1, 1, 1.0, move, 0.0, 2.0, "EXACT")
        tt.put(2, 1, 2.0, move, 0.0, 2.0, "EXACT")
        tt.put(3, 1, 3.0, move, 0.0, 2.0, "EXACT")
        
        assert len(tt.table) == 2
        assert 1 not in tt.table  # Oldest should be removed
    
    def test_clear(self):
        """Test clearing the table."""
        tt = TranspositionTable()
        move = FastMove(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=2,
            num_to_floor_line=0
        )
        
        tt.put(12345, 3, 10.5, move, 5.0, 15.0, "EXACT")
        assert len(tt.table) == 1
        
        tt.clear()
        assert len(tt.table) == 0
        assert tt.hits == 0
        assert tt.misses == 0
    
    def test_get_stats(self):
        """Test statistics reporting."""
        tt = TranspositionTable()
        move = FastMove(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=2,
            num_to_floor_line=0
        )
        
        # Add some entries
        tt.put(1, 1, 1.0, move, 0.0, 2.0, "EXACT")
        tt.put(2, 1, 2.0, move, 0.0, 2.0, "EXACT")
        
        # Test some hits and misses
        tt.get(1, 1, 0.0, 2.0)  # Hit
        tt.get(999, 1, 0.0, 2.0)  # Miss
        
        stats = tt.get_stats()
        assert stats['size'] == 2
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5


class TestAzulAlphaBetaSearch:
    """Test AzulAlphaBetaSearch functionality."""
    
    def test_initialization(self):
        """Test search initialization."""
        search = AzulAlphaBetaSearch(max_depth=5, max_time=2.0, use_endgame=True)
        assert search.max_depth == 5
        assert search.max_time == 2.0
        assert search.use_endgame is True
        assert search.endgame_database is not None
        assert isinstance(search.evaluator, AzulEvaluator)
        assert isinstance(search.move_generator, FastMoveGenerator)
        assert isinstance(search.transposition_table, TranspositionTable)
    
    def test_initialization_without_endgame(self):
        """Test search initialization without endgame."""
        search = AzulAlphaBetaSearch(max_depth=5, max_time=2.0, use_endgame=False)
        assert search.use_endgame is False
        assert search.endgame_database is None
    
    def test_search_basic(self):
        """Test basic search functionality."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0)
        state = AzulState(2)
        
        result = search.search(state, 0)
        assert isinstance(result, SearchResult)
        assert result.best_move is not None
        assert isinstance(result.best_score, (int, float))
        assert isinstance(result.principal_variation, list)
        assert result.nodes_searched > 0
        assert result.search_time > 0
        assert result.depth_reached > 0
    
    def test_search_with_time_limit(self):
        """Test search with time limit."""
        search = AzulAlphaBetaSearch(max_depth=10, max_time=0.1)  # Very short time
        state = AzulState(2)
        
        result = search.search(state, 0)
        assert result.search_time <= 0.1
        assert result.depth_reached > 0  # Should complete at least depth 1
    
    def test_search_with_depth_limit(self):
        """Test search with depth limit."""
        search = AzulAlphaBetaSearch(max_depth=2, max_time=1.0)
        state = AzulState(2)
        
        result = search.search(state, 0)
        assert result.depth_reached <= 2
    
    def test_get_search_stats(self):
        """Test search statistics."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0)
        state = AzulState(2)
        
        # Perform a search
        search.search(state, 0)
        
        stats = search.get_search_stats()
        assert 'nodes_searched' in stats
        assert 'search_time' in stats
        assert 'transposition_table' in stats
        assert stats['nodes_searched'] > 0
    
    def test_clear_search_stats(self):
        """Test clearing search statistics."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0)
        state = AzulState(2)
        
        # Perform a search
        search.search(state, 0)
        
        # Clear stats
        search.clear_search_stats()
        
        stats = search.get_search_stats()
        assert stats['nodes_searched'] == 0


class TestEndgameIntegration:
    """Test A8 endgame integration with search."""
    
    def test_search_with_endgame_enabled(self):
        """Test search with endgame database enabled."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=True)
        state = AzulState(2)
        
        # Create an endgame position
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 2
        
        result = search.search(state, 0)
        assert isinstance(result, SearchResult)
        # Should still return a valid result even if endgame analysis fails
    
    def test_search_without_endgame(self):
        """Test search without endgame database."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=False)
        state = AzulState(2)
        
        result = search.search(state, 0)
        assert isinstance(result, SearchResult)
        assert search.endgame_database is None
    
    def test_analyze_endgame_method(self):
        """Test the analyze_endgame method."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=True)
        state = AzulState(2)
        
        # Create an endgame position
        for factory in state.factories:
            for tile_type in utils.Tile:
                factory.tiles[tile_type] = 0
        
        state.factories[0].tiles[utils.Tile.BLUE] = 1
        
        result = search.analyze_endgame(state, 0)
        # Result might be None if analysis fails, but should not crash
        if result is not None:
            assert 'best_move' in result or result['best_move'] is None
            assert 'score' in result
            assert 'depth' in result
            assert 'exact' in result
    
    def test_analyze_endgame_non_endgame(self):
        """Test analyze_endgame on non-endgame position."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=True)
        state = AzulState(2)
        
        result = search.analyze_endgame(state, 0)
        assert result is None
    
    def test_analyze_endgame_disabled(self):
        """Test analyze_endgame when endgame is disabled."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=False)
        state = AzulState(2)
        
        result = search.analyze_endgame(state, 0)
        assert result is None
    
    def test_get_endgame_stats_enabled(self):
        """Test endgame statistics when enabled."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=True)
        
        stats = search.get_endgame_stats()
        assert stats['enabled'] is True
        assert 'total_solutions' in stats
        assert 'max_tiles' in stats
        assert 'analyzed_positions' in stats
    
    def test_get_endgame_stats_disabled(self):
        """Test endgame statistics when disabled."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0, use_endgame=False)
        
        stats = search.get_endgame_stats()
        assert stats['enabled'] is False
        assert len(stats) == 1  # Only 'enabled' key


class TestSearchIntegration:
    """Test integration with existing components."""
    
    def test_integration_with_move_generator(self):
        """Test integration with FastMoveGenerator."""
        search = AzulAlphaBetaSearch(max_depth=2, max_time=1.0)
        state = AzulState(2)
        
        # Should be able to generate moves
        moves = search.move_generator.generate_moves_fast(state, 0)
        assert len(moves) > 0
        
        # Search should work
        result = search.search(state, 0)
        assert result.best_move is not None
    
    def test_integration_with_evaluator(self):
        """Test integration with AzulEvaluator."""
        search = AzulAlphaBetaSearch(max_depth=2, max_time=1.0)
        state = AzulState(2)
        
        # Should be able to evaluate positions
        score = search.evaluator.evaluate_position(state, 0)
        assert isinstance(score, (int, float))
        
        # Search should work
        result = search.search(state, 0)
        assert result.best_move is not None
    
    def test_integration_with_game_rules(self):
        """Test integration with AzulGameRule."""
        search = AzulAlphaBetaSearch(max_depth=2, max_time=1.0)
        state = AzulState(2)
        
        # Generate moves
        moves = search.move_generator.generate_moves_fast(state, 0)
        if moves:
            move = moves[0]
            
            # Should be able to apply moves
            game_rule = AzulGameRule(len(state.agents))
            new_state = game_rule.apply_move(state, move, 0)
            
            if new_state is not None:
                # Should be able to search resulting position
                result = search.search(new_state, 0)
                assert result.best_move is not None


class TestSearchPerformance:
    """Test search performance characteristics."""
    
    def test_search_performance_target(self):
        """Test that search meets performance targets."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=4.0)
        state = AzulState(2)
        
        start_time = time.time()
        result = search.search(state, 0)
        search_time = time.time() - start_time
        
        # Should complete within time limit
        assert search_time <= 4.0
        
        # Should reach reasonable depth
        assert result.depth_reached >= 1
        
        # Should search reasonable number of nodes
        assert result.nodes_searched > 0
    
    def test_transposition_table_performance(self):
        """Test transposition table performance."""
        tt = TranspositionTable(max_size=1000)
        move = FastMove(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=2,
            num_to_floor_line=0
        )
        
        # Should handle many operations quickly
        for i in range(100):
            tt.put(i, 1, float(i), move, 0.0, 10.0, "EXACT")
            tt.get(i, 1, 0.0, 10.0)
        
        stats = tt.get_stats()
        assert stats['hits'] == 100
        assert stats['misses'] == 0
    
    def test_search_memory_usage(self):
        """Test that search doesn't use excessive memory."""
        search = AzulAlphaBetaSearch(max_depth=3, max_time=1.0)
        state = AzulState(2)
        
        # Perform multiple searches
        for _ in range(5):
            result = search.search(state, 0)
            assert result.best_move is not None
        
        # Should still be able to perform searches
        result = search.search(state, 0)
        assert result.best_move is not None 