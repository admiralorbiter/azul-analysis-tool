"""
Neural Policy Mapping Algorithms

This module provides advanced algorithms for mapping neural policy outputs
to actual moves, including temperature scaling, exploration strategies,
and confidence estimation.
"""

import torch
import numpy as np
from typing import List, Optional, Dict, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from core.azul_move_generator import FastMove
from core.azul_model import AzulState
from neural.move_encoding import MoveEncoder


class SelectionMethod(Enum):
    """Enumeration of move selection methods."""
    GREEDY = "greedy"
    STOCHASTIC = "stochastic"
    TOP_K = "top_k"
    SOFTMAX = "softmax"
    EPSILON_GREEDY = "epsilon_greedy"
    UCB = "ucb"


@dataclass
class PolicyMappingConfig:
    """Configuration for policy mapping algorithms."""
    
    # Selection parameters
    default_temperature: float = 1.0
    default_epsilon: float = 0.1
    top_k_size: int = 3
    ucb_exploration: float = 1.0
    
    # Confidence parameters
    confidence_threshold: float = 0.8
    enable_confidence_estimation: bool = True
    
    # Fallback parameters
    enable_heuristic_fallback: bool = True
    fallback_threshold: float = 0.5
    
    # Performance parameters
    enable_caching: bool = True
    cache_size: int = 1000


class PolicyMapper:
    """
    Advanced policy mapping system for neural move selection.
    
    This class provides sophisticated algorithms for selecting moves
    from neural policy outputs, with support for exploration,
    confidence estimation, and fallback mechanisms.
    """
    
    def __init__(self, config: Optional[PolicyMappingConfig] = None):
        """Initialize the policy mapper."""
        self.config = config or PolicyMappingConfig()
        self.move_encoder = MoveEncoder()
        self._selection_cache: Dict[int, FastMove] = {}
        self._confidence_cache: Dict[int, float] = {}
    
    def select_move(self, policy: torch.Tensor, legal_moves: List[FastMove], 
                   method: SelectionMethod = SelectionMethod.STOCHASTIC,
                   temperature: Optional[float] = None,
                   **kwargs) -> Optional[FastMove]:
        """
        Select a move from policy probabilities.
        
        Args:
            policy: Policy tensor from neural network
            legal_moves: List of legal moves
            method: Selection method to use
            temperature: Temperature for stochastic methods
            **kwargs: Additional parameters for specific methods
            
        Returns:
            Selected move, or None if no valid move
        """
        if not legal_moves:
            return None
        
        # Apply policy mask
        masked_policy = self.move_encoder.apply_policy_mask(policy, legal_moves)
        
        # Use appropriate selection method
        if method == SelectionMethod.GREEDY:
            return self._select_greedy(masked_policy, legal_moves)
        elif method == SelectionMethod.STOCHASTIC:
            temp = temperature or self.config.default_temperature
            return self._select_stochastic(masked_policy, legal_moves, temp)
        elif method == SelectionMethod.TOP_K:
            k = kwargs.get('k', self.config.top_k_size)
            return self._select_top_k(masked_policy, legal_moves, k)
        elif method == SelectionMethod.SOFTMAX:
            temp = temperature or self.config.default_temperature
            return self._select_softmax(masked_policy, legal_moves, temp)
        elif method == SelectionMethod.EPSILON_GREEDY:
            epsilon = kwargs.get('epsilon', self.config.default_epsilon)
            return self._select_epsilon_greedy(masked_policy, legal_moves, epsilon)
        elif method == SelectionMethod.UCB:
            exploration = kwargs.get('exploration', self.config.ucb_exploration)
            return self._select_ucb(masked_policy, legal_moves, exploration)
        else:
            raise ValueError(f"Unknown selection method: {method}")
    
    def _select_greedy(self, masked_policy: torch.Tensor, legal_moves: List[FastMove]) -> Optional[FastMove]:
        """Select move with highest probability."""
        max_index = torch.argmax(masked_policy).item()
        return self.move_encoder.decode_move(max_index, legal_moves)
    
    def _select_stochastic(self, masked_policy: torch.Tensor, legal_moves: List[FastMove], 
                          temperature: float) -> Optional[FastMove]:
        """Select move using temperature-scaled sampling."""
        if temperature > 0:
            # Apply temperature scaling
            scaled_policy = masked_policy / temperature
            
            # Handle invalid values (inf, nan, negative)
            if torch.isnan(scaled_policy).any() or torch.isinf(scaled_policy).any() or (scaled_policy < 0).any():
                # Fallback to uniform distribution
                probs = torch.ones_like(scaled_policy) / len(legal_moves)
            else:
                # Convert to probabilities
                probs = torch.softmax(scaled_policy, dim=-1)
            
            # Sample from distribution
            move_index = torch.multinomial(probs, 1).item()
            return self.move_encoder.decode_move(move_index, legal_moves)
        else:
            # Greedy selection
            return self._select_greedy(masked_policy, legal_moves)
    
    def _select_top_k(self, masked_policy: torch.Tensor, legal_moves: List[FastMove], k: int) -> Optional[FastMove]:
        """Select from top K moves."""
        k = min(k, len(legal_moves))
        if k <= 0:
            return None
        
        top_k_values, top_k_indices = torch.topk(masked_policy, k)
        
        # Select randomly from top K
        selected_index = top_k_indices[torch.randint(0, k, (1,))].item()
        return self.move_encoder.decode_move(selected_index, legal_moves)
    
    def _select_softmax(self, masked_policy: torch.Tensor, legal_moves: List[FastMove], 
                       temperature: float) -> Optional[FastMove]:
        """Select move using softmax sampling."""
        # Apply softmax with temperature
        scaled_policy = masked_policy / temperature
        
        # Handle invalid values (inf, nan, negative)
        if torch.isnan(scaled_policy).any() or torch.isinf(scaled_policy).any() or (scaled_policy < 0).any():
            # Fallback to uniform distribution
            probs = torch.ones_like(scaled_policy) / len(legal_moves)
        else:
            probs = torch.softmax(scaled_policy, dim=-1)
        
        # Sample from distribution
        move_index = torch.multinomial(probs, 1).item()
        return self.move_encoder.decode_move(move_index, legal_moves)
    
    def _select_epsilon_greedy(self, masked_policy: torch.Tensor, legal_moves: List[FastMove], 
                              epsilon: float) -> Optional[FastMove]:
        """Select move using epsilon-greedy strategy."""
        if np.random.random() < epsilon:
            # Exploration: select random legal move
            random_index = np.random.randint(0, len(legal_moves))
            return legal_moves[random_index]
        else:
            # Exploitation: select best move
            return self._select_greedy(masked_policy, legal_moves)
    
    def _select_ucb(self, masked_policy: torch.Tensor, legal_moves: List[FastMove], 
                   exploration: float) -> Optional[FastMove]:
        """Select move using Upper Confidence Bound (UCB) strategy."""
        # UCB score = policy value + exploration bonus
        ucb_scores = masked_policy + exploration * torch.sqrt(torch.log(torch.tensor(len(legal_moves))))
        
        max_index = torch.argmax(ucb_scores).item()
        return self.move_encoder.decode_move(max_index, legal_moves)
    
    def get_move_confidence(self, policy: torch.Tensor, selected_move: FastMove, 
                          legal_moves: List[FastMove]) -> float:
        """
        Calculate confidence in the selected move.
        
        Args:
            policy: Policy tensor from neural network
            selected_move: The selected move
            legal_moves: List of legal moves
            
        Returns:
            Confidence score between 0 and 1
        """
        if not self.config.enable_confidence_estimation:
            return 1.0
        
        # Get policy index for selected move
        try:
            move_index = self.move_encoder.encode_move(selected_move)
            if 0 <= move_index < policy.size(-1):
                # Get probability of selected move
                move_prob = torch.softmax(policy, dim=-1)[move_index].item()
                
                # Calculate confidence based on probability and alternatives
                masked_policy = self.move_encoder.apply_policy_mask(policy, legal_moves)
                max_prob = torch.max(torch.softmax(masked_policy, dim=-1)).item()
                
                # Confidence is relative to best possible move
                confidence = move_prob / max_prob if max_prob > 0 else 0.0
                return min(confidence, 1.0)
            else:
                return 0.0
        except (ValueError, IndexError):
            return 0.0
    
    def should_use_fallback(self, confidence: float) -> bool:
        """Determine if heuristic fallback should be used."""
        return (self.config.enable_heuristic_fallback and 
                confidence < self.config.fallback_threshold)
    
    def get_policy_statistics(self, policy: torch.Tensor, legal_moves: List[FastMove]) -> Dict:
        """
        Get statistics about the policy distribution.
        
        Args:
            policy: Policy tensor from neural network
            legal_moves: List of legal moves
            
        Returns:
            Dictionary with policy statistics
        """
        masked_policy = self.move_encoder.apply_policy_mask(policy, legal_moves)
        probs = torch.softmax(masked_policy, dim=-1)
        
        # Get legal move probabilities
        legal_indices = self.move_encoder.get_legal_move_indices(legal_moves)
        legal_probs = [probs[idx].item() for idx in legal_indices if 0 <= idx < probs.size(-1)]
        
        if not legal_probs:
            return {
                'max_probability': 0.0,
                'min_probability': 0.0,
                'mean_probability': 0.0,
                'entropy': 0.0,
                'num_legal_moves': 0
            }
        
        return {
            'max_probability': max(legal_probs),
            'min_probability': min(legal_probs),
            'mean_probability': np.mean(legal_probs),
            'entropy': -sum(p * np.log(p + 1e-10) for p in legal_probs),
            'num_legal_moves': len(legal_moves)
        }
    
    def get_move_ranking(self, policy: torch.Tensor, legal_moves: List[FastMove], 
                        top_k: int = 5) -> List[Tuple[FastMove, float]]:
        """
        Get ranked list of moves with their probabilities.
        
        Args:
            policy: Policy tensor from neural network
            legal_moves: List of legal moves
            top_k: Number of top moves to return
            
        Returns:
            List of (move, probability) tuples, sorted by probability
        """
        masked_policy = self.move_encoder.apply_policy_mask(policy, legal_moves)
        probs = torch.softmax(masked_policy, dim=-1)
        
        # Get probabilities for legal moves
        move_probs = []
        for move in legal_moves:
            try:
                index = self.move_encoder.encode_move(move)
                if 0 <= index < probs.size(-1):
                    prob = probs[index].item()
                    move_probs.append((move, prob))
            except ValueError:
                continue
        
        # Sort by probability (descending)
        move_probs.sort(key=lambda x: x[1], reverse=True)
        
        return move_probs[:top_k]
    
    def clear_cache(self):
        """Clear all caches."""
        self._selection_cache.clear()
        self._confidence_cache.clear()
        self.move_encoder.clear_cache()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        stats = self.move_encoder.get_cache_stats()
        stats.update({
            'selection_cache_size': len(self._selection_cache),
            'confidence_cache_size': len(self._confidence_cache)
        })
        return stats


def create_policy_mapper(config: Optional[PolicyMappingConfig] = None) -> PolicyMapper:
    """
    Create a policy mapper with the given configuration.
    
    Args:
        config: Configuration for the policy mapper
        
    Returns:
        Configured PolicyMapper instance
    """
    return PolicyMapper(config)


def test_policy_mapping():
    """Test the policy mapping system."""
    mapper = create_policy_mapper()
    
    # Create test policy and moves
    policy_size = 1000
    policy = torch.randn(policy_size)
    
    test_moves = [
        FastMove(1, 0, 0, 0, 1, 0),  # Factory move
        FastMove(2, -1, 1, 2, 2, 1),  # Center move
        FastMove(1, 1, 2, 4, 1, 0),   # Factory move
    ]
    
    print("Testing policy mapping...")
    
    # Test different selection methods
    methods = [
        SelectionMethod.GREEDY,
        SelectionMethod.STOCHASTIC,
        SelectionMethod.TOP_K,
        SelectionMethod.EPSILON_GREEDY
    ]
    
    for method in methods:
        selected_move = mapper.select_move(policy, test_moves, method=method)
        confidence = mapper.get_move_confidence(policy, selected_move, test_moves)
        stats = mapper.get_policy_statistics(policy, test_moves)
        
        print(f"{method.value}: {selected_move} (confidence: {confidence:.3f})")
        print(f"  Stats: {stats}")
    
    # Test move ranking
    ranking = mapper.get_move_ranking(policy, test_moves, top_k=3)
    print(f"Top moves: {ranking}")
    
    print(f"Cache stats: {mapper.get_cache_stats()}")


if __name__ == "__main__":
    test_policy_mapping() 