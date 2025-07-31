"""
Tests for Azul Heuristic Evaluator - A4 Implementation

This module tests the heuristic evaluation functionality including:
- Immediate score calculation
- Pattern potential estimation
- Penalty estimation
- Move evaluation and ranking
- Performance targets
"""

import pytest
import time
import numpy as np
from core.azul_evaluator import AzulEvaluator
from core.azul_model import AzulState
from core.azul_move_generator import AzulMoveGenerator, Move
from core import azul_utils as utils


class TestAzulEvaluator:
    """Test the Azul heuristic evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        return AzulEvaluator()
    
    @pytest.fixture
    def initial_state(self):
        return AzulState(2)
    
    @pytest.fixture
    def move_generator(self):
        return AzulMoveGenerator()
    
    def test_initialization(self, evaluator):
        """Test that the evaluator initializes correctly."""
        assert hasattr(evaluator, '_pattern_completion_bonuses')
        assert hasattr(evaluator, '_floor_penalties')
        assert hasattr(evaluator, '_row_bonus')
        assert hasattr(evaluator, '_col_bonus')
        assert hasattr(evaluator, '_set_bonus')
        
        # Check scoring tables
        assert evaluator._pattern_completion_bonuses[1] == 1
        assert evaluator._pattern_completion_bonuses[5] == 15
        assert len(evaluator._floor_penalties) == 7
        assert evaluator._row_bonus == 2
        assert evaluator._col_bonus == 7
        assert evaluator._set_bonus == 10
    
    def test_evaluate_initial_position(self, evaluator, initial_state):
        """Test evaluation of initial position."""
        score = evaluator.evaluate_position(initial_state, 0)
        
        # Initial position should have zero immediate score
        assert score == 0.0
    
    def test_immediate_score_calculation(self, evaluator, initial_state):
        """Test immediate score calculation."""
        agent_state = initial_state.agents[0]
        
        # Add some tiles to pattern lines
        agent_state.lines_number[0] = 1  # 1 tile in first pattern line
        agent_state.lines_tile[0] = utils.Tile.BLUE
        
        score = evaluator._calculate_immediate_score(agent_state)
        assert score == 1  # 1 point for 1 tile in pattern line
        
        # Add more tiles to complete the pattern line
        agent_state.lines_number[0] = 1  # 1 tile in first pattern line (should score 1)
        score = evaluator._calculate_immediate_score(agent_state)
        assert score == 1
    
    def test_floor_penalty_calculation(self, evaluator, initial_state):
        """Test floor penalty calculation."""
        agent_state = initial_state.agents[0]
        
        # Add floor tiles
        agent_state.floor_tiles = [utils.Tile.BLUE, utils.Tile.RED]
        
        score = evaluator._calculate_immediate_score(agent_state)
        assert score == -2  # -1 for first tile, -1 for second tile
    
    def test_pattern_potential_calculation(self, evaluator, initial_state):
        """Test pattern potential calculation."""
        agent_state = initial_state.agents[0]
        
        # Add tiles to pattern lines
        agent_state.lines_number[0] = 1  # 1 tile in first pattern line (needs 1 total)
        agent_state.lines_tile[0] = utils.Tile.BLUE
        
        potential = evaluator._calculate_pattern_potential(agent_state)
        # Should be 1/1 * 1 * 0.5 = 0.5
        assert potential == 0.5
        
        # Add more tiles
        agent_state.lines_number[1] = 2  # 2 tiles in second pattern line (needs 2 total)
        agent_state.lines_tile[1] = utils.Tile.RED
        
        potential = evaluator._calculate_pattern_potential(agent_state)
        # Should be 0.5 + (2/2 * 3 * 0.5) = 0.5 + 1.5 = 2.0
        assert potential == 2.0
    
    def test_penalty_estimation(self, evaluator, initial_state):
        """Test penalty estimation."""
        agent_state = initial_state.agents[0]
        
        # No floor tiles initially
        penalty = evaluator._calculate_penalty_estimation(agent_state)
        assert penalty == 0
        
        # Add some floor tiles
        agent_state.floor_tiles = [utils.Tile.BLUE, utils.Tile.RED]
        penalty = evaluator._calculate_penalty_estimation(agent_state)
        # Should estimate additional penalties for future floor tiles
        assert penalty < 0
    
    def test_endgame_bonuses(self, evaluator, initial_state):
        """Test endgame bonus calculation."""
        agent_state = initial_state.agents[0]
        
        # No completed rows/columns/sets initially
        bonuses = evaluator._calculate_endgame_bonuses(agent_state)
        assert bonuses == 0
        
        # Add a completed row
        agent_state.grid_state[0] = np.ones(5)  # Complete first row
        bonuses = evaluator._calculate_endgame_bonuses(agent_state)
        assert bonuses == evaluator._row_bonus  # 2 points for completed row
        
        # Add a completed column
        agent_state.grid_state[:, 0] = np.ones(5)  # Complete first column
        bonuses = evaluator._calculate_endgame_bonuses(agent_state)
        assert bonuses == evaluator._row_bonus + evaluator._col_bonus  # 2 + 7 = 9 points
    
    def test_completed_rows_counting(self, evaluator, initial_state):
        """Test counting of completed rows."""
        agent_state = initial_state.agents[0]
        
        # No completed rows initially
        completed = evaluator._count_completed_rows(agent_state)
        assert completed == 0
        
        # Complete first row
        agent_state.grid_state[0] = np.ones(5)
        completed = evaluator._count_completed_rows(agent_state)
        assert completed == 1
        
        # Complete second row
        agent_state.grid_state[1] = np.ones(5)
        completed = evaluator._count_completed_rows(agent_state)
        assert completed == 2
    
    def test_completed_columns_counting(self, evaluator, initial_state):
        """Test counting of completed columns."""
        agent_state = initial_state.agents[0]
        
        # No completed columns initially
        completed = evaluator._count_completed_columns(agent_state)
        assert completed == 0
        
        # Complete first column
        agent_state.grid_state[:, 0] = np.ones(5)
        completed = evaluator._count_completed_columns(agent_state)
        assert completed == 1
        
        # Complete second column
        agent_state.grid_state[:, 1] = np.ones(5)
        completed = evaluator._count_completed_columns(agent_state)
        assert completed == 2
    
    def test_completed_sets_counting(self, evaluator, initial_state):
        """Test counting of completed sets."""
        agent_state = initial_state.agents[0]
        
        # No completed sets initially
        completed = evaluator._count_completed_sets(agent_state)
        assert completed == 0
        
        # Add a completed set
        agent_state.number_of[utils.Tile.BLUE] = 5
        completed = evaluator._count_completed_sets(agent_state)
        assert completed == 1
        
        # Add another completed set
        agent_state.number_of[utils.Tile.RED] = 5
        completed = evaluator._count_completed_sets(agent_state)
        assert completed == 2
    
    def test_move_evaluation(self, evaluator, initial_state):
        """Test move evaluation."""
        # Create a simple move
        move = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=0,
            num_to_pattern_line=1,
            num_to_floor_line=0
        )
        
        score = evaluator.evaluate_move(initial_state, 0, move)
        assert isinstance(score, float)
    
    def test_move_ranking(self, evaluator, initial_state, move_generator):
        """Test move ranking functionality."""
        # Generate moves
        moves = move_generator.generate_moves(initial_state, 0)
        
        if len(moves) > 0:
            # Get move scores
            scores = evaluator.get_move_scores(initial_state, 0, moves)
            assert len(scores) == len(moves)
            
            # Debug: print first few scores and their types
            print(f"First 3 scores: {scores[:3]}")
            print(f"Score types: {[type(score) for score in scores[:3]]}")
            
            # Check for non-float values
            non_float_scores = [(i, score, type(score)) for i, score in enumerate(scores) if not isinstance(score, float)]
            if non_float_scores:
                print(f"Non-float scores found: {non_float_scores[:5]}")
            
            assert all(isinstance(score, float) for score in scores)
            
            # Rank moves
            ranked = evaluator.rank_moves(initial_state, 0, moves)
            assert len(ranked) == len(moves)
            assert ranked[0][0] >= ranked[-1][0]  # First should have higher score
            
            # Get best move
            best_index = evaluator.get_best_move(initial_state, 0, moves)
            assert best_index is not None
            assert 0 <= best_index < len(moves)
    
    def test_position_features(self, evaluator, initial_state):
        """Test position feature extraction."""
        features = evaluator.get_position_features(initial_state, 0)
        
        expected_features = [
            'immediate_score', 'pattern_potential', 'penalty_estimation',
            'endgame_bonuses', 'completed_rows', 'completed_columns',
            'completed_sets', 'floor_tiles', 'pattern_line_tiles', 'grid_tiles'
        ]
        
        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], (int, float))
    
    def test_evaluation_consistency(self, evaluator, initial_state):
        """Test that evaluation is consistent for the same position."""
        score1 = evaluator.evaluate_position(initial_state, 0)
        score2 = evaluator.evaluate_position(initial_state, 0)
        assert score1 == score2
    
    def test_evaluation_different_agents(self, evaluator, initial_state):
        """Test evaluation for different agents."""
        score0 = evaluator.evaluate_position(initial_state, 0)
        score1 = evaluator.evaluate_position(initial_state, 1)
        
        # Both agents should have same score in initial position
        assert score0 == score1


class TestEvaluatorPerformance:
    """Test performance of the evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        return AzulEvaluator()
    
    @pytest.fixture
    def test_states(self):
        """Create test states for performance testing."""
        states = []
        for i in range(3):
            state = AzulState(2)
            # Add some tiles to make the position more interesting
            agent = state.agents[0]
            agent.lines_number[0] = 1
            agent.lines_tile[0] = utils.Tile.BLUE
            agent.floor_tiles = [utils.Tile.RED]
            states.append(state)
        return states
    
    def test_evaluation_performance(self, evaluator, test_states):
        """Test that evaluation meets performance target (O(1))."""
        for state_name, state in enumerate(test_states):
            # Warm up
            for _ in range(10):
                evaluator.evaluate_position(state, 0)
            
            # Benchmark
            start_time = time.perf_counter()
            for _ in range(1000):
                score = evaluator.evaluate_position(state, 0)
            end_time = time.perf_counter()
            
            avg_time = (end_time - start_time) / 1000 * 1_000_000  # Convert to microseconds
            
            print(f"State {state_name}: {avg_time:.2f}µs per evaluation")
            
            # Should be very fast (O(1) target)
            assert avg_time < 100.0, f"Evaluation exceeded 100µs target: {avg_time:.2f}µs"
    
    def test_move_evaluation_performance(self, evaluator, test_states):
        """Test move evaluation performance."""
        from core.azul_move_generator import AzulMoveGenerator
        
        move_generator = AzulMoveGenerator()
        
        for state_name, state in enumerate(test_states):
            moves = move_generator.generate_moves(state, 0)
            
            if len(moves) > 0:
                # Warm up
                for _ in range(10):
                    evaluator.get_move_scores(state, 0, moves[:5])  # Test with first 5 moves
                
                # Benchmark
                start_time = time.perf_counter()
                for _ in range(100):
                    scores = evaluator.get_move_scores(state, 0, moves[:5])
                end_time = time.perf_counter()
                
                avg_time = (end_time - start_time) / 100 * 1_000_000  # Convert to microseconds
                
                print(f"State {state_name}: {avg_time:.2f}µs per move evaluation batch")
                
                # Should be reasonably fast
                assert avg_time < 1500.0, f"Move evaluation exceeded 1500µs target: {avg_time:.2f}µs"


class TestEvaluatorIntegration:
    """Test integration with other components."""
    
    @pytest.fixture
    def evaluator(self):
        return AzulEvaluator()
    
    @pytest.fixture
    def move_generator(self):
        return AzulMoveGenerator()
    
    def test_integration_with_move_generator(self, evaluator, move_generator):
        """Test integration with move generator."""
        state = AzulState(2)
        moves = move_generator.generate_moves(state, 0)
        
        if len(moves) > 0:
            # Should be able to evaluate all moves
            scores = evaluator.get_move_scores(state, 0, moves)
            assert len(scores) == len(moves)
            
            # Should be able to rank moves
            ranked = evaluator.rank_moves(state, 0, moves)
            assert len(ranked) == len(moves)
            
            # Should be able to find best move
            best_index = evaluator.get_best_move(state, 0, moves)
            assert best_index is not None
    
    def test_evaluation_with_state_changes(self, evaluator, move_generator):
        """Test evaluation with state changes."""
        state = AzulState(2)
        
        # Evaluate initial position
        initial_score = evaluator.evaluate_position(state, 0)
        
        # Make a move and evaluate
        moves = move_generator.generate_moves(state, 0)
        if len(moves) > 0:
            move = moves[0]
            move_score = evaluator.evaluate_move(state, 0, move)
            
            # Scores should be different (move changes position)
            assert move_score != initial_score


class TestEvaluatorEdgeCases:
    """Test edge cases for the evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        return AzulEvaluator()
    
    def test_empty_move_list(self, evaluator):
        """Test evaluation with empty move list."""
        state = AzulState(2)
        empty_moves = []
        
        scores = evaluator.get_move_scores(state, 0, empty_moves)
        assert scores == []
        
        ranked = evaluator.rank_moves(state, 0, empty_moves)
        assert ranked == []
        
        best = evaluator.get_best_move(state, 0, empty_moves)
        assert best is None
    
    def test_extreme_positions(self, evaluator):
        """Test evaluation of extreme positions."""
        state = AzulState(2)
        agent = state.agents[0]
        
        # Test with many floor tiles
        agent.floor_tiles = [utils.Tile.BLUE] * 7
        score = evaluator.evaluate_position(state, 0)
        assert score < 0  # Should be negative due to penalties
        
        # Test with completed grid
        agent.grid_state = np.ones((5, 5))
        score = evaluator.evaluate_position(state, 0)
        # Should have significant bonuses
        assert score > 0
    
    def test_invalid_agent_id(self, evaluator):
        """Test evaluation with invalid agent ID."""
        state = AzulState(2)
        
        # Should handle invalid agent ID gracefully
        with pytest.raises(IndexError):
            evaluator.evaluate_position(state, 999)  # Invalid agent ID 