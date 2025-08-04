"""
Neural Move Encoding System

This module provides comprehensive move encoding for neural policy mapping.
It handles the conversion between FastMove objects and policy indices,
with support for dynamic move spaces and validation.
"""

import torch
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import numpy as np

from core.azul_move_generator import FastMove
from core.azul_utils import Action, Tile
from core.azul_model import AzulState


@dataclass
class MoveEncodingConfig:
    """Configuration for move encoding system."""
    
    # Move space parameters
    max_factories: int = 9
    max_tile_types: int = 5
    max_pattern_lines: int = 5
    max_tiles_per_move: int = 4  # Maximum tiles that can be taken in one move
    
    # Encoding parameters
    use_dynamic_encoding: bool = True  # Adjust encoding based on legal moves
    enable_validation: bool = True  # Validate moves during encoding/decoding
    enable_fallback: bool = True  # Enable fallback for invalid moves
    
    # Performance parameters
    cache_size: int = 1000  # Size of move encoding cache
    enable_caching: bool = True  # Enable move encoding caching


class MoveEncoder:
    """
    Comprehensive move encoding system for neural policy mapping.
    
    This class handles the conversion between FastMove objects and policy indices,
    with support for dynamic move spaces, validation, and caching.
    """
    
    def __init__(self, config: Optional[MoveEncodingConfig] = None):
        """Initialize the move encoder."""
        self.config = config or MoveEncodingConfig()
        self._move_cache: Dict[int, int] = {}  # move_hash -> policy_index
        self._index_cache: Dict[int, FastMove] = {}  # policy_index -> move
        self._legal_moves_cache: Dict[int, List[FastMove]] = {}  # state_hash -> legal_moves
        
        # Pre-compute move space size
        self._total_move_space = self._calculate_move_space_size()
        
        # Initialize encoding tables
        self._init_encoding_tables()
    
    def _calculate_move_space_size(self) -> int:
        """Calculate the total size of the move space."""
        # Factory moves: 9 factories × 5 tile types × 6 pattern lines × 2 (pattern/floor) = 540
        factory_moves = self.config.max_factories * self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2
        
        # Center moves: 5 tile types × 6 pattern lines × 2 (pattern/floor) = 60
        center_moves = self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2
        
        # Floor-only moves: 9 factories × 5 tile types + 5 center tile types = 50
        floor_only_moves = self.config.max_factories * self.config.max_tile_types + self.config.max_tile_types
        
        return factory_moves + center_moves + floor_only_moves
    
    def _init_encoding_tables(self):
        """Initialize encoding tables for fast lookup."""
        self._action_type_offsets = {
            Action.TAKE_FROM_FACTORY: 0,
            Action.TAKE_FROM_CENTRE: self.config.max_factories * self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2
        }
        
        self._tile_type_offsets = {}
        for tile_type in range(self.config.max_tile_types):
            self._tile_type_offsets[tile_type] = tile_type * (self.config.max_pattern_lines + 1) * 2
        
        self._pattern_line_offsets = {}
        for pattern_line in range(self.config.max_pattern_lines + 1):  # +1 for floor-only
            self._pattern_line_offsets[pattern_line] = pattern_line * 2
    
    def encode_move(self, move: FastMove) -> int:
        """
        Encode a FastMove to a policy index.
        
        Args:
            move: The FastMove to encode
            
        Returns:
            Policy index for the move
            
        Raises:
            ValueError: If move is invalid or cannot be encoded
        """
        if self.config.enable_validation and not self._validate_move(move):
            raise ValueError(f"Invalid move: {move}")
        
        # Try cache first
        move_hash = hash(move)
        if self.config.enable_caching and move_hash in self._move_cache:
            return self._move_cache[move_hash]
        
        # Calculate policy index
        policy_index = self._calculate_policy_index(move)
        
        # Cache result
        if self.config.enable_caching:
            self._move_cache[move_hash] = policy_index
            self._index_cache[policy_index] = move
            
            # Maintain cache size
            if len(self._move_cache) > self.config.cache_size:
                self._cleanup_cache()
        
        return policy_index
    
    def decode_move(self, policy_index: int, legal_moves: List[FastMove]) -> Optional[FastMove]:
        """
        Decode a policy index to a FastMove.
        
        Args:
            policy_index: The policy index to decode
            legal_moves: List of legal moves in the current position
            
        Returns:
            The decoded FastMove, or None if invalid
        """
        if not legal_moves:
            return None
        
        # Try cache first
        if self.config.enable_caching and policy_index in self._index_cache:
            cached_move = self._index_cache[policy_index]
            if cached_move in legal_moves:
                return cached_move
        
        # Try to decode using the policy index
        try:
            decoded_move = self._decode_policy_index(policy_index)
            if decoded_move in legal_moves:
                return decoded_move
        except (ValueError, IndexError):
            pass
        
        # Fallback: select from legal moves based on policy index
        if self.config.enable_fallback and legal_moves:
            # Use policy index to select from legal moves
            move_index = policy_index % len(legal_moves)
            return legal_moves[move_index]
        
        return None
    
    def get_move_space_size(self) -> int:
        """Get the total size of the move space."""
        return self._total_move_space
    
    def get_legal_move_indices(self, legal_moves: List[FastMove]) -> List[int]:
        """
        Get policy indices for all legal moves.
        
        Args:
            legal_moves: List of legal moves
            
        Returns:
            List of policy indices for legal moves
        """
        indices = []
        for move in legal_moves:
            try:
                index = self.encode_move(move)
                indices.append(index)
            except ValueError:
                # Skip invalid moves
                continue
        return indices
    
    def create_policy_mask(self, legal_moves: List[FastMove], policy_size: int) -> torch.Tensor:
        """
        Create a policy mask for legal moves.
        
        Args:
            legal_moves: List of legal moves
            policy_size: Size of the policy output
            
        Returns:
            Boolean tensor mask for legal moves
        """
        mask = torch.zeros(policy_size, dtype=torch.bool)
        legal_indices = self.get_legal_move_indices(legal_moves)
        
        for index in legal_indices:
            if 0 <= index < policy_size:
                mask[index] = True
        
        return mask
    
    def apply_policy_mask(self, policy: torch.Tensor, legal_moves: List[FastMove]) -> torch.Tensor:
        """
        Apply policy mask to zero out illegal moves.
        
        Args:
            policy: Policy tensor from neural network
            legal_moves: List of legal moves
            
        Returns:
            Masked policy tensor
        """
        mask = self.create_policy_mask(legal_moves, policy.size(-1))
        masked_policy = policy.clone()
        masked_policy[~mask] = float('-inf')
        return masked_policy
    
    def select_move_from_policy(self, policy: torch.Tensor, legal_moves: List[FastMove], 
                              temperature: float = 1.0, method: str = 'greedy') -> Optional[FastMove]:
        """
        Select a move from policy probabilities.
        
        Args:
            policy: Policy tensor from neural network
            legal_moves: List of legal moves
            temperature: Temperature for sampling (lower = more greedy)
            method: Selection method ('greedy', 'stochastic', 'top_k')
            
        Returns:
            Selected move, or None if no valid move
        """
        if not legal_moves:
            return None
        
        # Apply mask to policy
        masked_policy = self.apply_policy_mask(policy, legal_moves)
        
        if method == 'greedy':
            # Select highest probability legal move
            max_index = torch.argmax(masked_policy).item()
            return self.decode_move(max_index, legal_moves)
        
        elif method == 'stochastic':
            # Sample from policy distribution
            if temperature > 0:
                # Apply temperature scaling
                scaled_policy = masked_policy / temperature
                # Convert to probabilities
                probs = torch.softmax(scaled_policy, dim=-1)
                # Sample from distribution
                move_index = torch.multinomial(probs, 1).item()
                return self.decode_move(move_index, legal_moves)
            else:
                # Greedy selection
                max_index = torch.argmax(masked_policy).item()
                return self.decode_move(max_index, legal_moves)
        
        elif method == 'top_k':
            # Select from top K legal moves
            k = min(3, len(legal_moves))  # Top 3 moves
            top_k_values, top_k_indices = torch.topk(masked_policy, k)
            
            # Select randomly from top K
            if k > 0:
                selected_index = top_k_indices[torch.randint(0, k, (1,))].item()
                return self.decode_move(selected_index, legal_moves)
        
        return None
    
    def _calculate_policy_index(self, move: FastMove) -> int:
        """Calculate policy index for a move."""
        # Base offset for action type
        base_offset = self._action_type_offsets.get(move.action_type, 0)
        
        # Add offset for source (factory or center)
        if move.action_type == Action.TAKE_FROM_FACTORY:
            source_offset = move.source_id * self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2
        else:  # TAKE_FROM_CENTRE
            source_offset = 0
        
        # Add offset for tile type
        tile_offset = self._tile_type_offsets.get(move.tile_type, 0)
        
        # Add offset for pattern line destination
        pattern_offset = self._pattern_line_offsets.get(move.pattern_line_dest, 0)
        
        # Add offset for move type (pattern line vs floor)
        move_type_offset = 0 if move.num_to_pattern_line > 0 else 1
        
        # Calculate final index
        index = base_offset + source_offset + tile_offset + pattern_offset + move_type_offset
        
        return index
    
    def _decode_policy_index(self, policy_index: int) -> FastMove:
        """Decode policy index to move (approximate)."""
        # This is a simplified decoding - in practice, you'd need the full state context
        # to decode accurately, so this is mainly for caching and fallback
        
        # Determine action type
        if policy_index < self._action_type_offsets[Action.TAKE_FROM_CENTRE]:
            action_type = Action.TAKE_FROM_FACTORY
            base_offset = 0
        else:
            action_type = Action.TAKE_FROM_CENTRE
            base_offset = self._action_type_offsets[Action.TAKE_FROM_CENTRE]
        
        # Calculate remaining index
        remaining_index = policy_index - base_offset
        
        # Decode components (simplified)
        if action_type == Action.TAKE_FROM_FACTORY:
            source_id = remaining_index // (self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2)
            remaining_index %= (self.config.max_tile_types * (self.config.max_pattern_lines + 1) * 2)
        else:
            source_id = -1  # Center
        
        tile_type = remaining_index // ((self.config.max_pattern_lines + 1) * 2)
        remaining_index %= ((self.config.max_pattern_lines + 1) * 2)
        
        pattern_line_dest = remaining_index // 2
        move_type = remaining_index % 2
        
        # Set move parameters
        if move_type == 0:  # Pattern line move
            num_to_pattern_line = 1
            num_to_floor_line = 0
        else:  # Floor-only move
            num_to_pattern_line = 0
            num_to_floor_line = 1
        
        return FastMove(
            action_type=action_type,
            source_id=source_id,
            tile_type=tile_type,
            pattern_line_dest=pattern_line_dest,
            num_to_pattern_line=num_to_pattern_line,
            num_to_floor_line=num_to_floor_line
        )
    
    def _validate_move(self, move: FastMove) -> bool:
        """Validate a move for encoding."""
        # Check action type
        if move.action_type not in [Action.TAKE_FROM_FACTORY, Action.TAKE_FROM_CENTRE]:
            return False
        
        # Check source ID
        if move.action_type == Action.TAKE_FROM_FACTORY:
            if not (0 <= move.source_id < self.config.max_factories):
                return False
        else:  # TAKE_FROM_CENTRE
            if move.source_id != -1:
                return False
        
        # Check tile type
        if not (0 <= move.tile_type < self.config.max_tile_types):
            return False
        
        # Check pattern line destination
        if not (-1 <= move.pattern_line_dest < self.config.max_pattern_lines):
            return False
        
        # Check tile counts
        if not (0 <= move.num_to_pattern_line <= self.config.max_tiles_per_move):
            return False
        if not (0 <= move.num_to_floor_line <= self.config.max_tiles_per_move):
            return False
        
        # Check total tiles
        total_tiles = move.num_to_pattern_line + move.num_to_floor_line
        if total_tiles == 0 or total_tiles > self.config.max_tiles_per_move:
            return False
        
        return True
    
    def _cleanup_cache(self):
        """Clean up cache to maintain size limit."""
        if len(self._move_cache) > self.config.cache_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._move_cache.keys())[:len(self._move_cache) - self.config.cache_size]
            for key in keys_to_remove:
                del self._move_cache[key]
            
            # Also clean up index cache
            indices_to_remove = list(self._index_cache.keys())[:len(self._index_cache) - self.config.cache_size]
            for index in indices_to_remove:
                del self._index_cache[index]
    
    def clear_cache(self):
        """Clear all caches."""
        self._move_cache.clear()
        self._index_cache.clear()
        self._legal_moves_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'move_cache_size': len(self._move_cache),
            'index_cache_size': len(self._index_cache),
            'legal_moves_cache_size': len(self._legal_moves_cache),
            'total_move_space': self._total_move_space
        }


def create_move_encoder(config: Optional[MoveEncodingConfig] = None) -> MoveEncoder:
    """
    Create a move encoder with the given configuration.
    
    Args:
        config: Configuration for the move encoder
        
    Returns:
        Configured MoveEncoder instance
    """
    return MoveEncoder(config)


def test_move_encoding():
    """Test the move encoding system."""
    encoder = create_move_encoder()
    
    # Test move encoding
    test_moves = [
        FastMove(Action.TAKE_FROM_FACTORY, 0, Tile.BLUE, 0, 1, 0),
        FastMove(Action.TAKE_FROM_FACTORY, 1, Tile.RED, 2, 2, 1),
        FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.YELLOW, 3, 1, 0),
        FastMove(Action.TAKE_FROM_CENTRE, -1, Tile.BLACK, -1, 0, 2),
    ]
    
    print("Testing move encoding...")
    for move in test_moves:
        try:
            index = encoder.encode_move(move)
            decoded_move = encoder.decode_move(index, test_moves)
            print(f"Move: {move} -> Index: {index} -> Decoded: {decoded_move}")
        except ValueError as e:
            print(f"Invalid move: {move} - {e}")
    
    print(f"Move space size: {encoder.get_move_space_size()}")
    print(f"Cache stats: {encoder.get_cache_stats()}")


if __name__ == "__main__":
    test_move_encoding() 