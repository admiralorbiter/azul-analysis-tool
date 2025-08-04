"""
Batch Neural Evaluator

This module provides GPU-optimized batch inference for multiple Azul states,
with support for memory optimization, performance monitoring, and device selection.
"""

import torch
import torch.nn as nn
import time
import psutil
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np

from core.azul_model import AzulState
from neural.azul_net import AzulNet, AzulTensorEncoder, create_azul_net
from neural.move_encoding import MoveEncoder
from neural.policy_mapping import PolicyMapper, SelectionMethod


@dataclass
class BatchConfig:
    """Configuration for batch inference system."""
    
    # Batch parameters
    default_batch_size: int = 32
    max_batch_size: int = 128
    min_batch_size: int = 1
    
    # Memory parameters
    max_memory_usage: float = 0.8  # Maximum GPU memory usage (80%)
    enable_memory_optimization: bool = True
    enable_mixed_precision: bool = True
    
    # Performance parameters
    enable_async_processing: bool = True
    enable_performance_monitoring: bool = True
    
    # Device parameters
    auto_device_selection: bool = True
    preferred_device: str = "auto"  # "auto", "cuda", "cpu"
    
    # Fallback parameters
    enable_cpu_fallback: bool = True
    cpu_fallback_threshold: float = 0.1  # Use CPU if GPU is 10% slower


class BatchNeuralEvaluator:
    """
    GPU-optimized batch inference system for neural Azul evaluation.
    
    This class provides efficient batch processing of multiple game states,
    with automatic device selection, memory optimization, and performance monitoring.
    """
    
    def __init__(self, model: AzulNet, encoder: AzulTensorEncoder, 
                 config: Optional[BatchConfig] = None):
        """Initialize the batch evaluator."""
        self.model = model
        self.encoder = encoder
        self.config = config or BatchConfig()
        
        # Initialize components
        self.move_encoder = MoveEncoder()
        self.policy_mapper = PolicyMapper()
        
        # Performance tracking
        self._inference_times: List[float] = []
        self._memory_usage: List[float] = []
        self._batch_sizes: List[int] = []
        
        # Device setup
        self.device = self._setup_device()
        self.model.to(self.device)
        
        # Memory optimization
        if self.config.enable_mixed_precision and self.device.type == 'cuda':
            self.scaler = torch.cuda.amp.GradScaler()
        
        # Batch size optimization
        self._optimal_batch_size = self._find_optimal_batch_size()
    
    def _setup_device(self) -> torch.device:
        """Setup the optimal device for inference."""
        if self.config.auto_device_selection:
            if torch.cuda.is_available():
                # Check GPU memory and performance
                gpu_memory = torch.cuda.get_device_properties(0).total_memory
                if gpu_memory > 4e9:  # 4GB minimum for batch processing
                    return torch.device('cuda')
            return torch.device('cpu')
        elif self.config.preferred_device == "cuda" and torch.cuda.is_available():
            return torch.device('cuda')
        else:
            return torch.device('cpu')
    
    def _find_optimal_batch_size(self) -> int:
        """Find the optimal batch size for the current device."""
        if self.device.type == 'cpu':
            return min(self.config.default_batch_size, 16)
        
        # Test different batch sizes
        test_sizes = [1, 4, 8, 16, 32, 64, 128]
        best_size = self.config.default_batch_size
        best_throughput = 0
        
        # Create dummy states for testing
        dummy_states = self._create_dummy_states(max(test_sizes))
        
        for batch_size in test_sizes:
            if batch_size > len(dummy_states):
                continue
                
            try:
                start_time = time.time()
                self._evaluate_batch_internal(dummy_states[:batch_size], [0] * batch_size)
                end_time = time.time()
                
                throughput = batch_size / (end_time - start_time)
                if throughput > best_throughput:
                    best_throughput = throughput
                    best_size = batch_size
                    
            except RuntimeError as e:
                if "out of memory" in str(e):
                    break
                continue
        
        return best_size
    
    def _create_dummy_states(self, count: int) -> List[AzulState]:
        """Create dummy states for batch size testing."""
        # This is a simplified version - in practice, you'd create proper game states
        from core.azul_model import AzulState
        from core.azul_utils import Tile
        
        dummy_states = []
        for _ in range(count):
            # Create a minimal valid state for testing (2-player game)
            state = AzulState(2)
            dummy_states.append(state)
        
        return dummy_states
    
    def evaluate_batch(self, states: List[AzulState], agent_ids: List[int]) -> List[float]:
        """
        Evaluate a batch of states using the neural network.
        
        Args:
            states: List of Azul game states
            agent_ids: List of agent IDs corresponding to states
            
        Returns:
            List of evaluation scores
        """
        if len(states) != len(agent_ids):
            raise ValueError("States and agent_ids must have the same length")
        
        if len(states) == 0:
            raise ValueError("States list cannot be empty")
        
        start_time = time.time()
        
        # Process in optimal batch sizes
        results = []
        for i in range(0, len(states), self._optimal_batch_size):
            batch_states = states[i:i + self._optimal_batch_size]
            batch_agent_ids = agent_ids[i:i + self._optimal_batch_size]
            
            batch_results = self._evaluate_batch_internal(batch_states, batch_agent_ids)
            results.extend(batch_results)
        
        # Record performance metrics
        end_time = time.time()
        self._inference_times.append(end_time - start_time)
        self._batch_sizes.append(len(states))
        
        if self.device.type == 'cuda':
            memory_used = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
            self._memory_usage.append(memory_used)
        
        return results
    
    def _evaluate_batch_internal(self, states: List[AzulState], agent_ids: List[int]) -> List[float]:
        """Internal batch evaluation with GPU optimization."""
        # Encode states
        state_tensors = []
        for state, agent_id in zip(states, agent_ids):
            tensor = self.encoder.encode_state(state, agent_id)
            state_tensors.append(tensor)
        
        # Stack into batch
        batch_tensor = torch.stack(state_tensors).to(self.device)
        
        # Run inference with mixed precision if available
        with torch.no_grad():
            if self.config.enable_mixed_precision and self.device.type == 'cuda':
                with torch.cuda.amp.autocast():
                    _, values = self.model(batch_tensor)
            else:
                _, values = self.model(batch_tensor)
        
        # Convert to list of scores
        scores = values.cpu().numpy().flatten().tolist()
        return scores
    
    def get_policy_batch(self, states: List[AzulState], agent_ids: List[int]) -> List[torch.Tensor]:
        """
        Get policy outputs for a batch of states.
        
        Args:
            states: List of Azul game states
            agent_ids: List of agent IDs corresponding to states
            
        Returns:
            List of policy tensors
        """
        if len(states) != len(agent_ids):
            raise ValueError("States and agent_ids must have the same length")
        
        if len(states) == 0:
            raise ValueError("States list cannot be empty")
        
        # Encode states
        state_tensors = []
        for state, agent_id in zip(states, agent_ids):
            tensor = self.encoder.encode_state(state, agent_id)
            state_tensors.append(tensor)
        
        # Stack into batch
        batch_tensor = torch.stack(state_tensors).to(self.device)
        
        # Run inference
        with torch.no_grad():
            if self.config.enable_mixed_precision and self.device.type == 'cuda':
                with torch.cuda.amp.autocast():
                    policies, _ = self.model(batch_tensor)
            else:
                policies, _ = self.model(batch_tensor)
        
        # Split into individual policies
        policy_list = []
        for i in range(policies.shape[0]):
            policy_list.append(policies[i].cpu())
        
        return policy_list
    
    def select_moves_batch(self, states: List[AzulState], agent_ids: List[int],
                          legal_moves_list: List[List], 
                          method: SelectionMethod = SelectionMethod.STOCHASTIC,
                          temperature: float = 1.0) -> List[Optional[Any]]:
        """
        Select moves for a batch of states using neural policy.
        
        Args:
            states: List of Azul game states
            agent_ids: List of agent IDs
            legal_moves_list: List of legal moves for each state
            method: Selection method
            temperature: Temperature for stochastic methods
            
        Returns:
            List of selected moves
        """
        # Get policy outputs
        policies = self.get_policy_batch(states, agent_ids)
        
        # Select moves for each state
        selected_moves = []
        for i, (policy, legal_moves) in enumerate(zip(policies, legal_moves_list)):
            move = self.policy_mapper.select_move(
                policy, legal_moves, method, temperature
            )
            selected_moves.append(move)
        
        return selected_moves
    
    def optimize_batch_size(self) -> int:
        """Find and return the optimal batch size for current setup."""
        self._optimal_batch_size = self._find_optimal_batch_size()
        return self._optimal_batch_size
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self._inference_times:
            return {}
        
        stats = {
            'avg_inference_time': np.mean(self._inference_times),
            'avg_batch_size': np.mean(self._batch_sizes),
            'total_inferences': len(self._inference_times),
            'optimal_batch_size': self._optimal_batch_size,
            'device': str(self.device),
        }
        
        if self._memory_usage:
            stats['avg_memory_usage'] = np.mean(self._memory_usage)
            stats['max_memory_usage'] = np.max(self._memory_usage)
        
        # Calculate throughput
        total_time = sum(self._inference_times)
        total_states = sum(self._batch_sizes)
        stats['throughput_states_per_second'] = total_states / total_time if total_time > 0 else 0
        
        return stats
    
    def clear_performance_stats(self):
        """Clear performance statistics."""
        self._inference_times.clear()
        self._memory_usage.clear()
        self._batch_sizes.clear()
    
    def get_memory_info(self) -> Dict[str, float]:
        """Get current memory usage information."""
        info = {}
        
        if self.device.type == 'cuda':
            info['gpu_memory_allocated'] = torch.cuda.memory_allocated() / 1e9  # GB
            info['gpu_memory_cached'] = torch.cuda.memory_reserved() / 1e9  # GB
            info['gpu_memory_max'] = torch.cuda.max_memory_allocated() / 1e9  # GB
        
        # CPU memory
        process = psutil.Process()
        info['cpu_memory_used'] = process.memory_info().rss / 1e9  # GB
        info['cpu_memory_percent'] = process.memory_percent()
        
        return info


def create_batch_evaluator(model: Optional[AzulNet] = None,
                          encoder: Optional[AzulTensorEncoder] = None,
                          config: Optional[BatchConfig] = None) -> BatchNeuralEvaluator:
    """Create a batch neural evaluator with optional model and encoder."""
    if model is None or encoder is None:
        model, encoder = create_azul_net(device="cpu")  # Will be moved to optimal device
    
    return BatchNeuralEvaluator(model, encoder, config)


def test_batch_evaluator():
    """Test the batch evaluator functionality."""
    print("Testing Batch Neural Evaluator...")
    
    # Create evaluator
    config = BatchConfig(default_batch_size=8, enable_performance_monitoring=True)
    evaluator = create_batch_evaluator(config=config)
    
    print(f"Device: {evaluator.device}")
    print(f"Optimal batch size: {evaluator._optimal_batch_size}")
    
    # Create test states (simplified)
    from core.azul_model import AzulState
    test_states = [AzulState(2) for _ in range(16)]
    test_agent_ids = [0] * 16
    
    # Test batch evaluation
    print("\nTesting batch evaluation...")
    start_time = time.time()
    scores = evaluator.evaluate_batch(test_states, test_agent_ids)
    end_time = time.time()
    
    print(f"Evaluated {len(scores)} states in {end_time - start_time:.3f}s")
    print(f"Average score: {np.mean(scores):.3f}")
    
    # Test performance stats
    stats = evaluator.get_performance_stats()
    print(f"\nPerformance stats: {stats}")
    
    # Test memory info
    memory_info = evaluator.get_memory_info()
    print(f"Memory info: {memory_info}")
    
    print("Batch evaluator test completed!")


if __name__ == "__main__":
    test_batch_evaluator() 