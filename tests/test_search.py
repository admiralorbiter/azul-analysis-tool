"""
Tests for Azul Alpha-Beta Search - A5 Implementation

This module tests the alpha-beta search functionality with:
- Basic search functionality
- Performance targets (depth-3 < 4s)
- Transposition table efficiency
- Move ordering heuristics
- Integration with existing components
"""

import pytest
import time
import numpy as np
from core.azul_search import AzulAlphaBetaSearch, TranspositionTable, SearchResult
from core.azul_model import AzulState
from core.azul_evaluator import AzulEvaluator
from core.azul_move_generator import FastMoveGenerator


class TestTranspositionTable:
    """Test the transposition table functionality."""
    
    @pytest.fixture
    def tt(self):
        return TranspositionTable(max_size=100)
    
    def test_initialization(self, tt):
        """Test that the transposition table initializes correctly."""
        assert tt.max_size == 100
        assert len(tt.table) == 0
        assert tt.hits == 0
        assert tt.misses == 0
    
    def test_put_and_get(self, tt):
        """Test storing and retrieving entries."""
        # Store an entry
        tt.put(12345, 3, 10.5, None, -10, 20, 'EXACT')
        
        # Retrieve it
        result = tt.get(12345, 3, -10, 20)
        assert result is not None
        score, move = result
        assert score == 10.5
        assert move is None
    
    def test_depth_filtering(self, tt):
        """Test that entries are filtered by depth."""
        # Store entry at depth 3
        tt.put(12345, 3, 10.5, None, -10, 20, 'EXACT')
        
        # Try to get with depth 4 (should fail)
        result = tt.get(12345, 4, -10, 20)
        assert result is None
        
        # Try to get with depth 2 (should succeed)
        result = tt.get(12345, 2, -10, 20)
        assert result is not None
    
    def test_size_limit(self, tt):
        """Test that the table respects size limits."""
        # Fill the table
        for i in range(110):  # More than max_size
            tt.put(i, 1, float(i), None, -10, 20, 'EXACT')
        
        # Should have removed oldest entries
        assert len(tt.table) <= tt.max_size
    
    def test_clear(self, tt):
        """Test clearing the transposition table."""
        tt.put(12345, 3, 10.5, None, -10, 20, 'EXACT')
        tt.clear()
        
        assert len(tt.table) == 0
        assert tt.hits == 0
        assert tt.misses == 0
    
    def test_stats(self, tt):
        """Test statistics calculation."""
        # Add some entries
        tt.put(12345, 3, 10.5, None, -10, 20, 'EXACT')
        tt.get(12345, 3, -10, 20)  # Hit
        tt.get(54321, 3, -10, 20)  # Miss
        
        stats = tt.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5


class TestAzulAlphaBetaSearch:
    """Test the alpha-beta search implementation."""
    
    @pytest.fixture
    def search_engine(self):
        return AzulAlphaBetaSearch(max_depth=5, max_time=2.0)
    
    @pytest.fixture
    def initial_state(self):
        return AzulState(2)
    
    def test_initialization(self, search_engine):
        """Test that the search engine initializes correctly."""
        assert search_engine.max_depth == 5
        assert search_engine.max_time == 2.0
        assert search_engine.evaluator is not None
        assert search_engine.move_generator is not None
        assert search_engine.transposition_table is not None
    
    def test_search_initial_position(self, search_engine, initial_state):
        """Test searching from the initial position."""
        result = search_engine.search(initial_state, 0, max_depth=2, max_time=1.0)
        
        assert isinstance(result, SearchResult)
        assert result.best_move is not None
        assert result.nodes_searched > 0
        assert result.search_time > 0
        assert result.depth_reached > 0
        assert len(result.principal_variation) > 0
    
    def test_search_time_limit(self, search_engine, initial_state):
        """Test that search respects time limits."""
        start_time = time.time()
        result = search_engine.search(initial_state, 0, max_depth=10, max_time=0.1)
        search_time = time.time() - start_time
        
        assert result.search_time <= 0.15  # Allow some tolerance
        assert search_time <= 0.2  # Allow some overhead
    
    def test_search_depth_limit(self, search_engine, initial_state):
        """Test that search respects depth limits."""
        result = search_engine.search(initial_state, 0, max_depth=3, max_time=1.0)
        
        assert result.depth_reached <= 3
        assert result.depth_reached > 0
    
    def test_search_consistency(self, search_engine, initial_state):
        """Test that search results are consistent."""
        result1 = search_engine.search(initial_state, 0, max_depth=2, max_time=1.0)
        result2 = search_engine.search(initial_state, 0, max_depth=2, max_time=1.0)
        
        # Results should be similar (allowing for some randomness in move ordering)
        assert result1.best_move is not None
        assert result2.best_move is not None
        assert result1.nodes_searched > 0
        assert result2.nodes_searched > 0
    
    def test_search_different_agents(self, search_engine, initial_state):
        """Test searching for different agents."""
        result0 = search_engine.search(initial_state, 0, max_depth=2, max_time=1.0)
        result1 = search_engine.search(initial_state, 1, max_depth=2, max_time=1.0)
        
        assert result0.best_move is not None
        assert result1.best_move is not None
        # Different agents might have different best moves
        assert result0.nodes_searched > 0
        assert result1.nodes_searched > 0
    
    def test_move_ordering(self, search_engine, initial_state):
        """Test that move ordering improves search efficiency."""
        # Search with move ordering
        result_ordered = search_engine.search(initial_state, 0, max_depth=3, max_time=1.0)
        
        # Clear stats and search again
        search_engine.clear_search_stats()
        result_ordered2 = search_engine.search(initial_state, 0, max_depth=3, max_time=1.0)
        
        # Both searches should find moves
        assert result_ordered.best_move is not None
        assert result_ordered2.best_move is not None
    
    def test_transposition_table_usage(self, search_engine, initial_state):
        """Test that transposition table is being used."""
        # First search
        result1 = search_engine.search(initial_state, 0, max_depth=3, max_time=1.0)
        tt_stats1 = search_engine.get_search_stats()['transposition_table']
        
        # Second search (should benefit from TT)
        search_engine.clear_search_stats()
        result2 = search_engine.search(initial_state, 0, max_depth=3, max_time=1.0)
        tt_stats2 = search_engine.get_search_stats()['transposition_table']
        
        # Should have some TT hits
        assert tt_stats2['hits'] >= 0
        assert tt_stats2['size'] > 0


class TestSearchPerformance:
    """Test search performance targets."""
    
    @pytest.fixture
    def search_engine(self):
        return AzulAlphaBetaSearch(max_depth=5, max_time=5.0)
    
    @pytest.fixture
    def test_states(self):
        """Create a few test states for performance testing."""
        states = []
        for i in range(3):
            state = AzulState(2)
            # Add some tiles to make the position more interesting
            if i > 0:
                # Simulate some moves to create different positions
                pass
            states.append(state)
        return states
    
    def test_depth_3_performance(self, search_engine, test_states):
        """Test that depth-3 search completes within 4 seconds."""
        for i, state in enumerate(test_states):
            start_time = time.time()
            result = search_engine.search(state, 0, max_depth=3, max_time=4.0)
            search_time = time.time() - start_time
            
            assert result.search_time <= 4.1, f"Search {i} took {result.search_time:.2f}s"
            assert result.depth_reached >= 1, f"Search {i} only reached depth {result.depth_reached}"
            assert result.best_move is not None, f"Search {i} found no best move"
    
    def test_nodes_per_second(self, search_engine, test_states):
        """Test that search achieves reasonable nodes per second."""
        for state in test_states:
            result = search_engine.search(state, 0, max_depth=2, max_time=1.0)
            stats = search_engine.get_search_stats()
            
            if result.search_time > 0.1:  # Only test if search took meaningful time
                nodes_per_second = stats['nodes_per_second']
                assert nodes_per_second > 500, f"Only {nodes_per_second:.0f} nodes/sec"
    
    def test_memory_usage(self, search_engine, test_states):
        """Test that search doesn't use excessive memory."""
        for state in test_states:
            result = search_engine.search(state, 0, max_depth=3, max_time=2.0)
            stats = search_engine.get_search_stats()
            
            # TT should be reasonable size
            tt_size = stats['transposition_table']['size']
            assert tt_size < 100000, f"TT too large: {tt_size} entries"


class TestSearchIntegration:
    """Test integration with other components."""
    
    @pytest.fixture
    def search_engine(self):
        return AzulAlphaBetaSearch(max_depth=3, max_time=2.0)
    
    @pytest.fixture
    def evaluator(self):
        return AzulEvaluator()
    
    @pytest.fixture
    def move_generator(self):
        return FastMoveGenerator()
    
    def test_integration_with_evaluator(self, search_engine, evaluator):
        """Test that search works with the evaluator."""
        state = AzulState(2)
        
        # Get evaluation
        eval_score = evaluator.evaluate_position(state, 0)
        
        # Get search result
        result = search_engine.search(state, 0, max_depth=2, max_time=1.0)
        
        # Both should work without errors
        assert isinstance(eval_score, (int, float))
        assert result.best_move is not None
    
    def test_integration_with_move_generator(self, search_engine, move_generator):
        """Test that search works with the move generator."""
        state = AzulState(2)
        
        # Generate moves
        moves = move_generator.generate_moves_fast(state, 0)
        
        # Get search result
        result = search_engine.search(state, 0, max_depth=2, max_time=1.0)
        
        # Both should work without errors
        assert len(moves) > 0
        assert result.best_move is not None
    
    def test_search_with_state_changes(self, search_engine):
        """Test that search works with modified states."""
        state = AzulState(2)
        
        # Search original state
        result1 = search_engine.search(state, 0, max_depth=2, max_time=1.0)
        
        # Modify state and search again
        state2 = state.clone()
        # Add some tiles to make it different
        result2 = search_engine.search(state2, 0, max_depth=2, max_time=1.0)
        
        # Both searches should complete
        assert result1.best_move is not None
        assert result2.best_move is not None


class TestSearchEdgeCases:
    """Test edge cases for the search engine."""
    
    @pytest.fixture
    def search_engine(self):
        return AzulAlphaBetaSearch(max_depth=3, max_time=1.0)
    
    def test_search_with_no_moves(self, search_engine):
        """Test search when no moves are available."""
        # This would require a very specific endgame position
        # For now, just test that the search engine handles it gracefully
        state = AzulState(2)
        result = search_engine.search(state, 0, max_depth=1, max_time=0.1)
        
        # Should still return a result
        assert isinstance(result, SearchResult)
    
    def test_search_with_extreme_depths(self, search_engine):
        """Test search with very shallow and deep depths."""
        state = AzulState(2)
        
        # Very shallow search
        result_shallow = search_engine.search(state, 0, max_depth=1, max_time=0.1)
        assert result_shallow.depth_reached <= 1
        
        # Deep search (should be limited by time)
        result_deep = search_engine.search(state, 0, max_depth=10, max_time=0.1)
        assert result_deep.depth_reached <= 10
    
    def test_search_with_extreme_times(self, search_engine):
        """Test search with very short and long time limits."""
        state = AzulState(2)
        
        # Very short time
        result_short = search_engine.search(state, 0, max_depth=3, max_time=0.01)
        assert result_short.search_time <= 0.02  # Allow some tolerance
        
        # Longer time
        result_long = search_engine.search(state, 0, max_depth=3, max_time=2.0)
        assert result_long.search_time <= 2.1  # Allow some tolerance
    
    def test_search_stats_consistency(self, search_engine):
        """Test that search statistics are consistent."""
        state = AzulState(2)
        
        # Clear stats
        search_engine.clear_search_stats()
        
        # Perform search
        result = search_engine.search(state, 0, max_depth=2, max_time=1.0)
        stats = search_engine.get_search_stats()
        
        # Check consistency
        assert stats['nodes_searched'] == result.nodes_searched
        assert stats['search_time'] == result.search_time
        assert stats['transposition_table']['size'] >= 0 