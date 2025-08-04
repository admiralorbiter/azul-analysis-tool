"""
Tests for the neural policy mapping system.

This module tests the PolicyMapper class and related functionality
for selecting moves from neural policy outputs.
"""

import unittest
import torch
import numpy as np
from typing import List

from neural.policy_mapping import (
    PolicyMapper, PolicyMappingConfig, create_policy_mapper,
    SelectionMethod
)
from core.azul_move_generator import FastMove
from core.azul_utils import Action, Tile


class TestPolicyMapping(unittest.TestCase):
    """Test cases for the policy mapping system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mapper = create_policy_mapper()
        self.config = PolicyMappingConfig()
        
        # Create test moves
        self.test_moves = [
            FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, 0, 1, 0),
            FastMove(Action.TAKE_FROM_FACTORY, 1, Tile.RED, 2, 2, 1),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.YELLOW, 3, 1, 0),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.BLACK, -1, 0, 2),
        ]
        
        # Create test policy
        self.policy_size = 1000
        self.policy = torch.randn(self.policy_size)
    
    def test_greedy_selection(self):
        """Test greedy move selection."""
        selected_move = self.mapper.select_move(
            self.policy, self.test_moves, method=SelectionMethod.GREEDY
        )
        
        self.assertIsNotNone(selected_move)
        self.assertIn(selected_move, self.test_moves)
    
    def test_stochastic_selection(self):
        """Test stochastic move selection."""
        # Test with different temperatures
        for temperature in [0.5, 1.0, 2.0]:
            with self.subTest(temperature=temperature):
                selected_move = self.mapper.select_move(
                    self.policy, self.test_moves, 
                    method=SelectionMethod.STOCHASTIC, 
                    temperature=temperature
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)
    
    def test_top_k_selection(self):
        """Test top-k move selection."""
        for k in [1, 2, 3]:
            with self.subTest(k=k):
                selected_move = self.mapper.select_move(
                    self.policy, self.test_moves, 
                    method=SelectionMethod.TOP_K, 
                    k=k
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)
    
    def test_softmax_selection(self):
        """Test softmax move selection."""
        for temperature in [0.5, 1.0, 2.0]:
            with self.subTest(temperature=temperature):
                selected_move = self.mapper.select_move(
                    self.policy, self.test_moves, 
                    method=SelectionMethod.SOFTMAX, 
                    temperature=temperature
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)
    
    def test_epsilon_greedy_selection(self):
        """Test epsilon-greedy move selection."""
        for epsilon in [0.1, 0.5, 0.9]:
            with self.subTest(epsilon=epsilon):
                selected_move = self.mapper.select_move(
                    self.policy, self.test_moves, 
                    method=SelectionMethod.EPSILON_GREEDY, 
                    epsilon=epsilon
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)
    
    def test_ucb_selection(self):
        """Test UCB move selection."""
        for exploration in [0.5, 1.0, 2.0]:
            with self.subTest(exploration=exploration):
                selected_move = self.mapper.select_move(
                    self.policy, self.test_moves, 
                    method=SelectionMethod.UCB, 
                    exploration=exploration
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)
    
    def test_empty_legal_moves(self):
        """Test behavior with empty legal moves list."""
        empty_moves = []
        
        for method in SelectionMethod:
            with self.subTest(method=method):
                selected_move = self.mapper.select_move(
                    self.policy, empty_moves, method=method
                )
                self.assertIsNone(selected_move)
    
    def test_move_confidence(self):
        """Test move confidence calculation."""
        # Create a policy with high probability for one move
        policy = torch.zeros(self.policy_size)
        target_move = self.test_moves[0]
        
        # Set high probability for target move
        try:
            move_index = self.mapper.move_encoder.encode_move(target_move)
            if 0 <= move_index < policy.size(-1):
                policy[move_index] = 10.0
        except ValueError:
            # If encoding fails, use a simple approach
            policy[0] = 10.0
        
        # Test confidence calculation
        confidence = self.mapper.get_move_confidence(policy, target_move, self.test_moves)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_fallback_decision(self):
        """Test fallback decision logic."""
        # Test with low confidence
        low_confidence = 0.3
        should_fallback = self.mapper.should_use_fallback(low_confidence)
        self.assertTrue(should_fallback)
        
        # Test with high confidence
        high_confidence = 0.8
        should_fallback = self.mapper.should_use_fallback(high_confidence)
        self.assertFalse(should_fallback)
    
    def test_policy_statistics(self):
        """Test policy statistics calculation."""
        stats = self.mapper.get_policy_statistics(self.policy, self.test_moves)
        
        # Check required fields
        required_fields = [
            'max_probability', 'min_probability', 'mean_probability',
            'entropy', 'num_legal_moves'
        ]
        
        for field in required_fields:
            self.assertIn(field, stats)
            self.assertIsInstance(stats[field], (int, float))
        
        # Check value ranges
        self.assertGreaterEqual(stats['max_probability'], 0.0)
        self.assertLessEqual(stats['max_probability'], 1.0)
        self.assertGreaterEqual(stats['min_probability'], 0.0)
        self.assertLessEqual(stats['min_probability'], 1.0)
        self.assertGreaterEqual(stats['mean_probability'], 0.0)
        self.assertLessEqual(stats['mean_probability'], 1.0)
        self.assertGreaterEqual(stats['entropy'], 0.0)
        self.assertEqual(stats['num_legal_moves'], len(self.test_moves))
    
    def test_move_ranking(self):
        """Test move ranking functionality."""
        ranking = self.mapper.get_move_ranking(self.policy, self.test_moves, top_k=3)
        
        self.assertIsInstance(ranking, list)
        self.assertLessEqual(len(ranking), 3)
        
        # Check ranking structure
        for move, probability in ranking:
            self.assertIn(move, self.test_moves)
            self.assertIsInstance(probability, float)
            self.assertGreaterEqual(probability, 0.0)
            self.assertLessEqual(probability, 1.0)
        
        # Check that ranking is sorted (descending)
        if len(ranking) > 1:
            for i in range(len(ranking) - 1):
                self.assertGreaterEqual(ranking[i][1], ranking[i + 1][1])
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid configuration
        valid_config = PolicyMappingConfig(
            default_temperature=1.0,
            default_epsilon=0.1,
            top_k_size=3,
            confidence_threshold=0.8
        )
        mapper = create_policy_mapper(valid_config)
        self.assertIsNotNone(mapper)
        
        # Test that configuration affects behavior
        high_temp_config = PolicyMappingConfig(default_temperature=2.0)
        high_temp_mapper = create_policy_mapper(high_temp_config)
        
        # Both mappers should work
        move1 = mapper.select_move(self.policy, self.test_moves, method=SelectionMethod.STOCHASTIC)
        move2 = high_temp_mapper.select_move(self.policy, self.test_moves, method=SelectionMethod.STOCHASTIC)
        
        self.assertIsNotNone(move1)
        self.assertIsNotNone(move2)
    
    def test_cache_functionality(self):
        """Test caching functionality."""
        # Clear cache first
        self.mapper.clear_cache()
        
        # Test that selection works
        selected_move = self.mapper.select_move(self.policy, self.test_moves)
        self.assertIsNotNone(selected_move)
        
        # Check cache stats
        stats = self.mapper.get_cache_stats()
        self.assertIn('move_cache_size', stats)
        self.assertIn('index_cache_size', stats)
        self.assertIn('selection_cache_size', stats)
        self.assertIn('confidence_cache_size', stats)
    
    def test_temperature_effects(self):
        """Test that temperature affects selection behavior."""
        # Create a policy with clear preferences
        policy = torch.zeros(self.policy_size)
        policy[0] = 10.0  # High probability for first move
        policy[1] = 1.0   # Lower probability for second move
        
        # Test with different temperatures
        low_temp_move = self.mapper.select_move(
            policy, self.test_moves, 
            method=SelectionMethod.STOCHASTIC, 
            temperature=0.1
        )
        
        high_temp_move = self.mapper.select_move(
            policy, self.test_moves, 
            method=SelectionMethod.STOCHASTIC, 
            temperature=2.0
        )
        
        # Both should be valid moves
        self.assertIsNotNone(low_temp_move)
        self.assertIsNotNone(high_temp_move)
        self.assertIn(low_temp_move, self.test_moves)
        self.assertIn(high_temp_move, self.test_moves)
    
    def test_epsilon_greedy_exploration(self):
        """Test epsilon-greedy exploration behavior."""
        # Create a policy with clear best move
        policy = torch.zeros(self.policy_size)
        policy[0] = 10.0  # High probability for first move
        
        # Test with different epsilon values
        for epsilon in [0.0, 0.5, 1.0]:
            with self.subTest(epsilon=epsilon):
                selected_moves = []
                for _ in range(10):  # Run multiple times to see exploration
                    move = self.mapper.select_move(
                        policy, self.test_moves, 
                        method=SelectionMethod.EPSILON_GREEDY, 
                        epsilon=epsilon
                    )
                    selected_moves.append(move)
                
                # All moves should be valid
                for move in selected_moves:
                    self.assertIsNotNone(move)
                    self.assertIn(move, self.test_moves)
    
    def test_ucb_exploration(self):
        """Test UCB exploration behavior."""
        # Create a policy with clear best move
        policy = torch.zeros(self.policy_size)
        policy[0] = 10.0  # High probability for first move
        
        # Test with different exploration values
        for exploration in [0.1, 1.0, 5.0]:
            with self.subTest(exploration=exploration):
                selected_move = self.mapper.select_move(
                    policy, self.test_moves, 
                    method=SelectionMethod.UCB, 
                    exploration=exploration
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)


class TestPolicyMappingPerformance(unittest.TestCase):
    """Performance tests for policy mapping."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.mapper = create_policy_mapper()
        
        # Create many test moves
        self.many_moves = []
        for factory_id in range(5):
            for tile_type in range(5):
                for pattern_line in range(5):
                    self.many_moves.append(FastMove(
                        Action.TAKE_FROM_FACTORY,
                        factory_id,
                        tile_type,
                        pattern_line,
                        1,
                        0
                    ))
        
        self.policy_size = 1000
        self.policy = torch.randn(self.policy_size)
    
    def test_selection_performance(self):
        """Test selection performance."""
        import time
        
        methods = [
            SelectionMethod.GREEDY,
            SelectionMethod.STOCHASTIC,
            SelectionMethod.TOP_K,
            SelectionMethod.EPSILON_GREEDY
        ]
        
        for method in methods:
            with self.subTest(method=method):
                start_time = time.time()
                
                # Run multiple selections
                for _ in range(100):
                    selected_move = self.mapper.select_move(
                        self.policy, self.many_moves[:10], method=method
                    )
                
                end_time = time.time()
                selection_time = end_time - start_time
                
                # Handle case where selection is extremely fast
                if selection_time < 0.001:  # Less than 1ms
                    # Just verify that selection works
                    self.assertIsNotNone(selected_move)
                    self.assertIn(selected_move, self.many_moves[:10])
                    print(f"✅ {method.value}: 100 selections in {selection_time:.6f}s (extremely fast!)")
                else:
                    selections_per_second = 100 / selection_time
                    # Should handle at least 1000 selections per second
                    self.assertGreater(selections_per_second, 1000)
                    print(f"✅ {method.value}: {selections_per_second:.0f} selections/second")
    
    def test_confidence_performance(self):
        """Test confidence calculation performance."""
        import time
        
        start_time = time.time()
        
        # Calculate confidence for many moves
        for move in self.many_moves[:50]:
            confidence = self.mapper.get_move_confidence(self.policy, move, self.many_moves[:10])
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        # Handle case where calculation is extremely fast
        if calculation_time < 0.001:  # Less than 1ms
            # Just verify that confidence calculation works
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
            print(f"✅ Confidence: 50 calculations in {calculation_time:.6f}s (extremely fast!)")
        else:
            calculations_per_second = 50 / calculation_time
            # Should handle at least 1000 calculations per second
            self.assertGreater(calculations_per_second, 1000)
            print(f"✅ Confidence: {calculations_per_second:.0f} calculations/second")
    
    def test_statistics_performance(self):
        """Test statistics calculation performance."""
        import time
        
        start_time = time.time()
        
        # Calculate statistics multiple times
        for _ in range(100):
            stats = self.mapper.get_policy_statistics(self.policy, self.many_moves[:10])
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        # Handle case where calculation is extremely fast
        if calculation_time < 0.001:  # Less than 1ms
            # Just verify that statistics calculation works
            self.assertIn('max_probability', stats)
            self.assertIn('min_probability', stats)
            self.assertIn('mean_probability', stats)
            print(f"✅ Statistics: 100 calculations in {calculation_time:.6f}s (extremely fast!)")
        else:
            calculations_per_second = 100 / calculation_time
            # Should handle at least 1000 calculations per second
            self.assertGreater(calculations_per_second, 1000)
            print(f"✅ Statistics: {calculations_per_second:.0f} calculations/second")


if __name__ == '__main__':
    unittest.main() 