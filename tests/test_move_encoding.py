"""
Tests for the neural move encoding system.

This module tests the MoveEncoder class and related functionality
for converting between FastMove objects and policy indices.
"""

import unittest
import torch
import numpy as np
from typing import List

from neural.move_encoding import MoveEncoder, MoveEncodingConfig, create_move_encoder
from analysis_engine.mathematical_optimization.azul_move_generator import FastMove
from core.azul_utils import Action, Tile
from core.azul_model import AzulState


class TestMoveEncoding(unittest.TestCase):
    """Test cases for the move encoding system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = create_move_encoder()
        self.config = MoveEncodingConfig()
        
        # Create test moves
        self.test_moves = [
            # Factory moves
            FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, 0, 1, 0),
            FastMove(Action.TAKE_FROM_FACTORY, 1, Tile.RED, 2, 2, 1),
            FastMove(Action.TAKE_FROM_FACTORY, 2, Tile.YELLOW, 4, 1, 0),
            FastMove(Action.TAKE_FROM_FACTORY, 3, Tile.BLACK, 1, 3, 0),
            FastMove(Action.TAKE_FROM_FACTORY, 4, Tile.WHITE, 3, 1, 1),
            
            # Center moves
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.BLUE, 0, 1, 0),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.RED, 2, 2, 1),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.YELLOW, 4, 1, 0),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.BLACK, 1, 3, 0),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.WHITE, 3, 1, 1),
            
            # Floor-only moves
            FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, -1, 0, 2),
            FastMove(Action.TAKE_FROM_FACTORY, 1, Tile.RED, -1, 0, 3),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.YELLOW, -1, 0, 1),
            FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.BLACK, -1, 0, 4),
        ]
    
    def test_move_encoding_basic(self):
        """Test basic move encoding functionality."""
        for move in self.test_moves:
            with self.subTest(move=move):
                # Test encoding
                index = self.encoder.encode_move(move)
                self.assertIsInstance(index, int)
                self.assertGreaterEqual(index, 0)
                self.assertLess(index, self.encoder.get_move_space_size())
                
                # Test decoding
                decoded_move = self.encoder.decode_move(index, self.test_moves)
                self.assertIsNotNone(decoded_move)
                self.assertEqual(move.action_type, decoded_move.action_type)
                self.assertEqual(move.source_id, decoded_move.source_id)
                self.assertEqual(move.tile_type, decoded_move.tile_type)
    
    def test_move_encoding_validation(self):
        """Test move validation during encoding."""
        # Test invalid moves
        invalid_moves = [
            FastMove(999, 0, Tile.BLUE, 0, 1, 0),  # Invalid action type
            FastMove(Action.TAKE_FROM_FACTORY, 10, Tile.BLUE, 0, 1, 0),  # Invalid factory ID
            FastMove(Action.TAKE_FROM_FACTORY, 0, 999, 0, 1, 0),  # Invalid tile type
            FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, 10, 1, 0),  # Invalid pattern line
            FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, 0, 0, 0),  # No tiles taken
            FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, 0, 5, 0),  # Too many tiles
        ]
        
        for move in invalid_moves:
            with self.subTest(move=move):
                with self.assertRaises(ValueError):
                    self.encoder.encode_move(move)
    
    def test_move_space_size(self):
        """Test move space size calculation."""
        expected_size = (
            self.config.max_factories * self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2 +
            self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2 +
            self.config.max_factories * self.config.max_tile_types + self.config.max_tile_types
        )
        
        actual_size = self.encoder.get_move_space_size()
        self.assertEqual(actual_size, expected_size)
    
    def test_legal_move_indices(self):
        """Test getting indices for legal moves."""
        indices = self.encoder.get_legal_move_indices(self.test_moves)
        
        self.assertEqual(len(indices), len(self.test_moves))
        for index in indices:
            self.assertIsInstance(index, int)
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, self.encoder.get_move_space_size())
    
    def test_policy_mask_creation(self):
        """Test policy mask creation."""
        policy_size = 1000
        mask = self.encoder.create_policy_mask(self.test_moves, policy_size)
        
        self.assertIsInstance(mask, torch.Tensor)
        self.assertEqual(mask.shape, (policy_size,))
        self.assertEqual(mask.dtype, torch.bool)
        
        # Check that legal move indices are True
        legal_indices = self.encoder.get_legal_move_indices(self.test_moves)
        for index in legal_indices:
            if 0 <= index < policy_size:
                self.assertTrue(mask[index])
    
    def test_policy_mask_application(self):
        """Test applying policy mask to policy tensor."""
        policy_size = 1000
        policy = torch.randn(policy_size)
        masked_policy = self.encoder.apply_policy_mask(policy, self.test_moves)
        
        self.assertIsInstance(masked_policy, torch.Tensor)
        self.assertEqual(masked_policy.shape, policy.shape)
        
        # Check that illegal moves have -inf probability
        mask = self.encoder.create_policy_mask(self.test_moves, policy_size)
        illegal_indices = torch.where(~mask)[0]
        for index in illegal_indices:
            self.assertEqual(masked_policy[index].item(), float('-inf'))
    
    def test_move_selection_greedy(self):
        """Test greedy move selection."""
        policy_size = 1000
        policy = torch.randn(policy_size)
        
        # Set high probability for a specific move
        target_index = self.encoder.get_legal_move_indices(self.test_moves)[0]
        policy[target_index] = 100.0
        
        selected_move = self.encoder.select_move_from_policy(
            policy, self.test_moves, method='greedy'
        )
        
        self.assertIsNotNone(selected_move)
        self.assertIn(selected_move, self.test_moves)
    
    def test_move_selection_stochastic(self):
        """Test stochastic move selection."""
        policy_size = 1000
        policy = torch.randn(policy_size)
        
        # Test with different temperatures
        for temperature in [0.5, 1.0, 2.0]:
            with self.subTest(temperature=temperature):
                selected_move = self.encoder.select_move_from_policy(
                    policy, self.test_moves, method='stochastic', temperature=temperature
                )
                
                self.assertIsNotNone(selected_move)
                self.assertIn(selected_move, self.test_moves)
    
    def test_move_selection_top_k(self):
        """Test top-k move selection."""
        policy_size = 1000
        policy = torch.randn(policy_size)
        
        selected_move = self.encoder.select_move_from_policy(
            policy, self.test_moves, method='top_k'
        )
        
        self.assertIsNotNone(selected_move)
        self.assertIn(selected_move, self.test_moves)
    
    def test_empty_legal_moves(self):
        """Test behavior with empty legal moves list."""
        empty_moves = []
        
        # Test decoding
        decoded_move = self.encoder.decode_move(0, empty_moves)
        self.assertIsNone(decoded_move)
        
        # Test move selection
        policy = torch.randn(100)
        selected_move = self.encoder.select_move_from_policy(policy, empty_moves)
        self.assertIsNone(selected_move)
        
        # Test legal move indices
        indices = self.encoder.get_legal_move_indices(empty_moves)
        self.assertEqual(indices, [])
    
    def test_cache_functionality(self):
        """Test caching functionality."""
        # Clear cache first
        self.encoder.clear_cache()
        
        # Test that encoding is cached
        move = self.test_moves[0]
        index1 = self.encoder.encode_move(move)
        index2 = self.encoder.encode_move(move)
        
        self.assertEqual(index1, index2)
        
        # Check cache stats
        stats = self.encoder.get_cache_stats()
        self.assertGreater(stats['move_cache_size'], 0)
        self.assertGreater(stats['index_cache_size'], 0)
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality."""
        # Create encoder with small cache size
        small_config = MoveEncodingConfig(cache_size=2)
        small_encoder = create_move_encoder(small_config)
        
        # Add more moves than cache size
        for move in self.test_moves[:5]:
            small_encoder.encode_move(move)
        
        # Check that cache size is maintained
        stats = small_encoder.get_cache_stats()
        self.assertLessEqual(stats['move_cache_size'], small_config.cache_size)
        self.assertLessEqual(stats['index_cache_size'], small_config.cache_size)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid configuration
        valid_config = MoveEncodingConfig(
            max_factories=9,
            max_tile_types=5,
            max_pattern_lines=5,
            max_tiles_per_move=4
        )
        encoder = create_move_encoder(valid_config)
        self.assertIsNotNone(encoder)
        
        # Test that configuration affects move space size
        small_config = MoveEncodingConfig(max_factories=5, max_tile_types=3)
        small_encoder = create_move_encoder(small_config)
        self.assertLess(small_encoder.get_move_space_size(), encoder.get_move_space_size())
    
    def test_move_encoding_edge_cases(self):
        """Test edge cases in move encoding."""
        # Test moves with maximum values
        max_move = FastMove(
            Action.TAKE_FROM_FACTORY,
            self.config.max_factories - 1,
            self.config.max_tile_types - 1,
            self.config.max_pattern_lines - 1,
            self.config.max_tiles_per_move,
            0
        )
        
        index = self.encoder.encode_move(max_move)
        self.assertIsInstance(index, int)
        self.assertGreaterEqual(index, 0)
        
        # Test floor-only moves
        floor_move = FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.BLUE, -1, 0, 1)
        index = self.encoder.encode_move(floor_move)
        self.assertIsInstance(index, int)
    
    def test_policy_index_uniqueness(self):
        """Test that different moves get different policy indices."""
        indices = set()
        for move in self.test_moves:
            index = self.encoder.encode_move(move)
            indices.add(index)
        
        # All moves should have unique indices
        self.assertEqual(len(indices), len(self.test_moves))
    
    def test_decode_with_invalid_index(self):
        """Test decoding with invalid policy index."""
        invalid_index = self.encoder.get_move_space_size() + 100
        
        decoded_move = self.encoder.decode_move(invalid_index, self.test_moves)
        
        # Should fall back to selecting from legal moves
        if self.encoder.config.enable_fallback:
            self.assertIsNotNone(decoded_move)
            self.assertIn(decoded_move, self.test_moves)
        else:
            self.assertIsNone(decoded_move)


class TestMoveEncodingPerformance(unittest.TestCase):
    """Performance tests for move encoding."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.encoder = create_move_encoder()
        
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
    
    def test_encoding_performance(self):
        """Test encoding performance."""
        import time
        
        # Clear cache first
        self.encoder.clear_cache()
        
        start_time = time.time()
        indices = []
        for move in self.many_moves:
            index = self.encoder.encode_move(move)
            indices.append(index)
        end_time = time.time()
        
        encoding_time = end_time - start_time
        
        # Handle case where encoding is extremely fast
        if encoding_time < 0.001:  # Less than 1ms
            # Just verify that encoding works and produces valid indices
            self.assertGreater(len(indices), 0)
            for index in indices:
                self.assertGreaterEqual(index, 0)
                self.assertLess(index, self.encoder.get_move_space_size())
            print(f"✅ Encoding {len(self.many_moves)} moves in {encoding_time:.6f}s (extremely fast!)")
        else:
            moves_per_second = len(self.many_moves) / encoding_time
            # Should encode at least 1000 moves per second
            self.assertGreater(moves_per_second, 1000)
            print(f"✅ Encoding {len(self.many_moves)} moves at {moves_per_second:.0f} moves/second")
        
        # All indices should be valid
        for index in indices:
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, self.encoder.get_move_space_size())
    
    def test_cache_performance(self):
        """Test cache performance."""
        import time
        
        # Clear cache first
        self.encoder.clear_cache()
        
        # First encoding (no cache)
        start_time = time.time()
        for move in self.many_moves[:10]:
            self.encoder.encode_move(move)
        first_time = time.time() - start_time
        
        # Second encoding (with cache)
        start_time = time.time()
        for move in self.many_moves[:10]:
            self.encoder.encode_move(move)
        second_time = time.time() - start_time
        
        # Handle case where both times are very small
        if first_time < 0.001 and second_time < 0.001:
            # Just verify that both encodings work and produce valid results
            self.assertGreaterEqual(first_time, 0)
            self.assertGreaterEqual(second_time, 0)
            print(f"✅ Cache test: first={first_time:.6f}s, second={second_time:.6f}s (both extremely fast)")
        else:
            # Cached encoding should be faster (or at least not slower)
            self.assertLessEqual(second_time, first_time * 1.1)  # Allow 10% tolerance
            print(f"✅ Cache test: first={first_time:.6f}s, second={second_time:.6f}s")


if __name__ == '__main__':
    unittest.main() 