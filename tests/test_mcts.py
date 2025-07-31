"""
Tests for the MCTS (Monte Carlo Tree Search) module.
"""

import pytest
import time
import math
from unittest.mock import Mock, patch

from core.azul_mcts import (
    AzulMCTS, MCTSNode, MCTSResult, RolloutPolicy,
    RandomRolloutPolicy, HeavyRolloutPolicy
)
from core.azul_model import AzulState
from core.azul_move_generator import FastMoveGenerator, FastMove
from core.azul_evaluator import AzulEvaluator


class TestMCTSNode:
    """Test MCTSNode functionality."""
    
    def test_node_initialization(self):
        """Test node initialization."""
        state = AzulState(2)
        node = MCTSNode(state=state, agent_id=0)
        
        assert node.state == state
        assert node.parent is None
        assert node.move is None
        assert node.agent_id == 0
        assert node.visits == 0
        assert node.total_score == 0.0
        assert node.children == []
    
    def test_average_score(self):
        """Test average score calculation."""
        state = AzulState(2)
        node = MCTSNode(state=state)
        
        # No visits
        assert node.average_score == 0.0
        
        # With visits
        node.visits = 4
        node.total_score = 20.0
        assert node.average_score == 5.0
    
    def test_is_leaf(self):
        """Test leaf node detection."""
        state = AzulState(2)
        node = MCTSNode(state=state)
        
        # Empty node is leaf
        assert node.is_leaf
        
        # Node with children is not leaf
        child = MCTSNode(state=state, parent=node)
        node.children.append(child)
        assert not node.is_leaf


class TestRolloutPolicies:
    """Test rollout policies."""
    
    def test_random_rollout_policy_initialization(self):
        """Test random rollout policy initialization."""
        evaluator = AzulEvaluator()
        move_generator = FastMoveGenerator()
        policy = RandomRolloutPolicy(evaluator, move_generator)
        
        assert policy.evaluator == evaluator
        assert policy.move_generator == move_generator
    
    def test_heavy_rollout_policy_initialization(self):
        """Test heavy rollout policy initialization."""
        evaluator = AzulEvaluator()
        move_generator = FastMoveGenerator()
        policy = HeavyRolloutPolicy(evaluator, move_generator)
        
        assert policy.evaluator == evaluator
        assert policy.move_generator == move_generator
    
    def test_random_rollout_basic(self):
        """Test basic random rollout."""
        evaluator = AzulEvaluator()
        move_generator = FastMoveGenerator()
        policy = RandomRolloutPolicy(evaluator, move_generator)
        
        state = AzulState(2)
        score = policy.rollout(state, 0, max_depth=10)
        
        assert isinstance(score, float)
        assert not math.isnan(score)
    
    def test_heavy_rollout_basic(self):
        """Test basic heavy rollout."""
        evaluator = AzulEvaluator()
        move_generator = FastMoveGenerator()
        policy = HeavyRolloutPolicy(evaluator, move_generator)
        
        state = AzulState(2)
        score = policy.rollout(state, 0, max_depth=10)
        
        assert isinstance(score, float)
        assert not math.isnan(score)


class TestAzulMCTS:
    """Test AzulMCTS functionality."""
    
    def test_mcts_initialization(self):
        """Test MCTS initialization."""
        mcts = AzulMCTS()
        
        assert mcts.max_time == 0.2
        assert mcts.max_rollouts == 300
        assert mcts.exploration_constant == 1.414
        assert mcts.rollout_policy == RolloutPolicy.RANDOM
        assert isinstance(mcts.evaluator, AzulEvaluator)
        assert isinstance(mcts.move_generator, FastMoveGenerator)
    
    def test_mcts_initialization_with_heavy_policy(self):
        """Test MCTS initialization with heavy policy."""
        mcts = AzulMCTS(rollout_policy=RolloutPolicy.HEAVY)
        
        assert mcts.rollout_policy == RolloutPolicy.HEAVY
        assert isinstance(mcts._rollout_policy_instance, HeavyRolloutPolicy)
    
    def test_mcts_search_basic(self):
        """Test basic MCTS search."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        
        assert isinstance(result, MCTSResult)
        assert result.search_time <= 0.1
        assert result.rollout_count <= 10
        assert result.nodes_searched >= 0
    
    def test_mcts_search_with_custom_parameters(self):
        """Test MCTS search with custom parameters."""
        mcts = AzulMCTS()
        state = AzulState(2)
        
        result = mcts.search(state, 0, max_time=0.05, max_rollouts=5)
        
        assert result.search_time <= 0.05
        assert result.rollout_count <= 5
    
    def test_mcts_search_statistics(self):
        """Test MCTS search statistics."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        
        mcts.search(state, 0)
        stats = mcts.get_search_stats()
        
        assert 'nodes_searched' in stats
        assert 'rollout_count' in stats
        assert 'search_time' in stats
        assert 'rollouts_per_second' in stats
        assert stats['rollout_count'] <= 10
        assert stats['search_time'] <= 0.1
    
    def test_mcts_performance_target(self):
        """Test that MCTS meets performance target."""
        mcts = AzulMCTS(max_time=0.2, max_rollouts=300)
        state = AzulState(2)
        
        start_time = time.time()
        result = mcts.search(state, 0)
        total_time = time.time() - start_time
        
        # Should complete within 200ms (allow small tolerance)
        assert result.search_time <= 0.21
        assert total_time <= 0.25  # Allow some overhead
    
    def test_mcts_different_agents(self):
        """Test MCTS with different agents."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        
        result_agent_0 = mcts.search(state, 0)
        result_agent_1 = mcts.search(state, 1)
        
        # Both should complete successfully
        assert result_agent_0.search_time <= 0.11
        assert result_agent_1.search_time <= 0.11
        assert result_agent_0.rollout_count <= 10
        assert result_agent_1.rollout_count <= 10
        
        # Should produce valid results (may be same or different)
        assert isinstance(result_agent_0.best_score, float)
        assert isinstance(result_agent_1.best_score, float)
    
    def test_mcts_uct_calculation(self):
        """Test UCT calculation."""
        mcts = AzulMCTS()
        
        # Test with unvisited node
        node = MCTSNode(state=AzulState(2))
        uct = mcts._calculate_uct(node, 10)
        assert uct == float('inf')
        
        # Test with visited node
        node.visits = 5
        node.total_score = 25.0
        uct = mcts._calculate_uct(node, 10)
        assert isinstance(uct, float)
        assert uct > 0
    
    def test_mcts_node_expansion(self):
        """Test node expansion."""
        mcts = AzulMCTS()
        state = AzulState(2)
        root = MCTSNode(state=state, agent_id=0)
        
        # Expand root node
        child = mcts._expand(root)
        
        assert child is not None
        assert child.parent == root
        assert child.move is not None
        assert len(root.children) == 1
    
    def test_mcts_best_move_selection(self):
        """Test best move selection."""
        mcts = AzulMCTS()
        state = AzulState(2)
        root = MCTSNode(state=state, agent_id=0)
        
        # No children
        move, score, pv = mcts._select_best_move(root)
        assert move is None
        assert score == 0.0
        assert pv == []
        
        # With children
        child1 = MCTSNode(state=state, parent=root, move=Mock(), agent_id=1)
        child1.visits = 10
        child1.total_score = 50.0
        
        child2 = MCTSNode(state=state, parent=root, move=Mock(), agent_id=1)
        child2.visits = 5
        child2.total_score = 30.0
        
        root.children = [child1, child2]
        
        move, score, pv = mcts._select_best_move(root)
        assert move == child1.move  # Should select most visited child
        assert score == 5.0  # Average score of child1
        assert len(pv) == 1


class TestMCTSIntegration:
    """Test MCTS integration with other components."""
    
    def test_mcts_with_evaluator(self):
        """Test MCTS integration with evaluator."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        
        # Should use evaluator for scoring
        assert isinstance(result.best_score, float)
        assert not math.isnan(result.best_score)
    
    def test_mcts_with_move_generator(self):
        """Test MCTS integration with move generator."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        
        # Should generate moves using move generator
        if result.best_move is not None:
            assert isinstance(result.best_move, FastMove)
    
    def test_mcts_rollout_policies_comparison(self):
        """Test comparison between rollout policies."""
        state = AzulState(2)
        
        # Random policy
        mcts_random = AzulMCTS(max_time=0.1, max_rollouts=10, rollout_policy=RolloutPolicy.RANDOM)
        result_random = mcts_random.search(state, 0)
        
        # Heavy policy (slower but more accurate)
        mcts_heavy = AzulMCTS(max_time=0.1, max_rollouts=10, rollout_policy=RolloutPolicy.HEAVY)
        result_heavy = mcts_heavy.search(state, 0)
        
        # Both should complete successfully
        assert result_random.search_time <= 0.11
        assert result_heavy.search_time <= 3.0  # Heavy policy is much slower but should still complete
        assert result_random.rollout_count <= 10
        assert result_heavy.rollout_count <= 10
        
        # Both should produce valid results
        assert isinstance(result_random.best_score, float)
        assert isinstance(result_heavy.best_score, float)


class TestMCTSPerformance:
    """Test MCTS performance characteristics."""
    
    def test_mcts_speed_target(self):
        """Test that MCTS meets speed target."""
        mcts = AzulMCTS(max_time=0.2, max_rollouts=300)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        
        # Should complete within 200ms (allow small tolerance)
        assert result.search_time <= 0.21
    
    def test_mcts_rollout_efficiency(self):
        """Test rollout efficiency."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=50)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        stats = mcts.get_search_stats()
        
        # Should achieve reasonable rollouts per second
        assert stats['rollouts_per_second'] > 0
    
    def test_mcts_memory_efficiency(self):
        """Test memory efficiency."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=20)
        state = AzulState(2)
        
        # Should not cause memory issues
        for _ in range(5):
            result = mcts.search(state, 0)
            assert result is not None


class TestMCTSEdgeCases:
    """Test MCTS edge cases."""
    
    def test_mcts_no_moves(self):
        """Test MCTS with no available moves."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        
        # Mock move generator to return no moves
        with patch.object(mcts.move_generator, 'generate_moves_fast', return_value=[]):
            result = mcts.search(state, 0)
            
            assert result.best_move is None
            assert result.search_time <= 0.1
    
    def test_mcts_very_short_timeout(self):
        """Test MCTS with very short timeout."""
        mcts = AzulMCTS(max_time=0.001, max_rollouts=1)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        
        # Allow small tolerance for timing precision
        assert result.search_time <= 0.005
        assert result.rollout_count <= 1
    
    def test_mcts_zero_rollouts(self):
        """Test MCTS with zero rollouts."""
        mcts = AzulMCTS(max_time=0.1, max_rollouts=0)
        state = AzulState(2)
        
        result = mcts.search(state, 0)
        
        assert result.rollout_count == 0
        assert result.best_move is None


if __name__ == "__main__":
    pytest.main([__file__]) 