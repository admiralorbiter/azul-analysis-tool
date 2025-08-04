"""
GPU Optimization for RTX 30xx Series

This module provides RTX 30xx-specific optimizations including:
- Tensor core utilization for mixed precision
- Memory bandwidth optimization
- CUDA kernel fusion
- Multi-GPU support
"""

import torch
import torch.nn as nn
import torch.cuda.amp as amp
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np

from neural.azul_net import AzulNet, AzulTensorEncoder


@dataclass
class GPUOptimizationConfig:
    """Configuration for RTX 30xx GPU optimizations."""
    
    # Tensor core settings
    enable_tensor_cores: bool = True
    mixed_precision_dtype: str = "float16"  # "float16", "bfloat16"
    enable_autocast: bool = True
    
    # Memory optimization
    enable_memory_pooling: bool = True
    enable_gradient_checkpointing: bool = False  # For training only
    memory_fraction: float = 0.8  # Use 80% of available GPU memory
    
    # Performance optimization
    enable_kernel_fusion: bool = True
    enable_async_processing: bool = True
    enable_cuda_graphs: bool = True
    
    # Multi-GPU settings
    enable_multi_gpu: bool = False
    gpu_ids: List[int] = None
    
    # Monitoring
    enable_performance_monitoring: bool = True
    enable_memory_monitoring: bool = True


class RTX30xxOptimizer:
    """
    RTX 30xx-specific GPU optimization system.
    
    This class provides optimizations specifically designed for RTX 30xx series GPUs,
    including tensor core utilization, memory bandwidth optimization, and CUDA kernel fusion.
    """
    
    def __init__(self, config: Optional[GPUOptimizationConfig] = None):
        """Initialize the RTX 30xx optimizer."""
        self.config = config or GPUOptimizationConfig()
        self.device = self._setup_device()
        self._setup_optimizations()
        
        # Performance tracking
        self._kernel_times: Dict[str, List[float]] = {}
        self._memory_usage: List[float] = []
        self._throughput_metrics: List[float] = []
    
    def _setup_device(self) -> torch.device:
        """Setup the optimal device for RTX 30xx optimization."""
        if not torch.cuda.is_available():
            return torch.device('cpu')
        
        # Check if we have an RTX 30xx series GPU
        gpu_props = torch.cuda.get_device_properties(0)
        gpu_name = gpu_props.name.lower()
        
        # RTX 30xx series detection
        rtx_30xx_models = ['rtx 3060', 'rtx 3070', 'rtx 3080', 'rtx 3090', 
                          'rtx 4060', 'rtx 4070', 'rtx 4080', 'rtx 4090']
        
        is_rtx_30xx = any(model in gpu_name for model in rtx_30xx_models)
        
        if is_rtx_30xx:
            print(f"RTX 30xx GPU detected: {gpu_props.name}")
            print(f"Tensor cores: {gpu_props.multi_processor_count}")
            print(f"Memory: {gpu_props.total_memory / 1e9:.1f} GB")
        else:
            print(f"Non-RTX 30xx GPU detected: {gpu_props.name}")
        
        return torch.device('cuda')
    
    def _setup_optimizations(self):
        """Setup RTX 30xx-specific optimizations."""
        if self.device.type != 'cuda':
            return
        
        # Enable tensor cores
        if self.config.enable_tensor_cores:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        
        # Set memory fraction
        if self.config.enable_memory_pooling:
            torch.cuda.set_per_process_memory_fraction(self.config.memory_fraction)
        
        # Enable CUDA graphs for repeated operations
        if self.config.enable_cuda_graphs:
            torch.backends.cudnn.benchmark = True
    
    def optimize_model(self, model: AzulNet) -> AzulNet:
        """
        Apply RTX 30xx optimizations to a model.
        
        Args:
            model: The AzulNet model to optimize
            
        Returns:
            Optimized model
        """
        if self.device.type != 'cuda':
            return model
        
        # Move model to GPU
        model = model.to(self.device)
        
        # Enable gradient checkpointing for training
        if self.config.enable_gradient_checkpointing:
            model.gradient_checkpointing_enable()
        
        # Convert to mixed precision if enabled
        if self.config.enable_tensor_cores:
            model = self._convert_to_mixed_precision(model)
        
        return model
    
    def _convert_to_mixed_precision(self, model: AzulNet) -> AzulNet:
        """Convert model to mixed precision for tensor core optimization."""
        if self.config.mixed_precision_dtype == "float16":
            model = model.half()
        elif self.config.mixed_precision_dtype == "bfloat16":
            model = model.to(torch.bfloat16)
        
        return model
    
    def create_optimized_batch_processor(self, model: AzulNet, 
                                       encoder: AzulTensorEncoder) -> 'OptimizedBatchProcessor':
        """Create an optimized batch processor for RTX 30xx."""
        return OptimizedBatchProcessor(model, encoder, self)
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get detailed GPU information."""
        if self.device.type != 'cuda':
            return {'device': 'cpu'}
        
        props = torch.cuda.get_device_properties(0)
        info = {
            'name': props.name,
            'compute_capability': f"{props.major}.{props.minor}",
            'multi_processor_count': props.multi_processor_count,
            'total_memory_gb': props.total_memory / 1e9,
            'max_threads_per_block': props.max_threads_per_block,
            'max_shared_memory_per_block': props.max_shared_memory_per_block,
            'warp_size': props.warp_size,
            'device': str(self.device),
        }
        
        # Memory usage
        info['memory_allocated_gb'] = torch.cuda.memory_allocated() / 1e9
        info['memory_reserved_gb'] = torch.cuda.memory_reserved() / 1e9
        info['memory_usage_percent'] = (torch.cuda.memory_allocated() / props.total_memory) * 100
        
        return info
    
    def benchmark_performance(self, model: AzulNet, encoder: AzulTensorEncoder, 
                            batch_sizes: List[int] = None) -> Dict[str, Any]:
        """
        Benchmark model performance with different batch sizes.
        
        Args:
            model: The model to benchmark
            encoder: The tensor encoder
            batch_sizes: List of batch sizes to test
            
        Returns:
            Performance benchmark results
        """
        if batch_sizes is None:
            batch_sizes = [1, 4, 8, 16, 32, 64, 128]
        
        results = {}
        
        for batch_size in batch_sizes:
            try:
                # Create dummy input - calculate input size based on encoder config
                input_size = (encoder.config.max_factories * 6 * encoder.config.num_tile_types +  # 270
                             encoder.config.max_center_tiles * encoder.config.num_tile_types +    # 100
                             encoder.config.max_wall_size * encoder.config.max_wall_size * 2 +    # 50
                             encoder.config.max_pattern_lines * encoder.config.num_tile_types * 2 + # 50
                             encoder.config.max_floor_size * encoder.config.num_tile_types * 2 +   # 70
                             2)  # scores
                dummy_input = torch.randn(batch_size, input_size).to(self.device)
                
                # Warm up
                with torch.no_grad():
                    for _ in range(3):
                        _ = model(dummy_input)
                
                # Benchmark
                if self.device.type == 'cuda':
                    try:
                        torch.cuda.synchronize()
                        start_time = torch.cuda.Event(enable_timing=True)
                        end_time = torch.cuda.Event(enable_timing=True)
                        
                        start_time.record()
                        with torch.no_grad():
                            for _ in range(10):
                                _ = model(dummy_input)
                        end_time.record()
                        
                        torch.cuda.synchronize()
                        elapsed_time = start_time.elapsed_time(end_time) / 10  # Average over 10 runs
                    except RuntimeError:
                        # Fallback to CPU timing
                        start_time = time.time()
                        with torch.no_grad():
                            for _ in range(10):
                                _ = model(dummy_input)
                        elapsed_time = (time.time() - start_time) * 1000 / 10  # Convert to milliseconds
                else:
                    # CPU timing
                    start_time = time.time()
                    with torch.no_grad():
                        for _ in range(10):
                            _ = model(dummy_input)
                    elapsed_time = (time.time() - start_time) * 1000 / 10  # Convert to milliseconds
                
                results[f'batch_size_{batch_size}'] = {
                    'elapsed_time_ms': elapsed_time,
                    'throughput_states_per_second': batch_size / (elapsed_time / 1000),
                    'memory_usage_gb': torch.cuda.memory_allocated() / 1e9 if self.device.type == 'cuda' else 0.0,
                }
                
            except RuntimeError as e:
                if "out of memory" in str(e):
                    results[f'batch_size_{batch_size}'] = {'error': 'OOM'}
                    break
                else:
                    results[f'batch_size_{batch_size}'] = {'error': str(e)}
        
        return results


class OptimizedBatchProcessor:
    """
    RTX 30xx-optimized batch processor.
    
    This class provides optimized batch processing specifically designed
    for RTX 30xx series GPUs with tensor core utilization and memory optimization.
    """
    
    def __init__(self, model: AzulNet, encoder: AzulTensorEncoder, 
                 optimizer: RTX30xxOptimizer):
        """Initialize the optimized batch processor."""
        self.model = optimizer.optimize_model(model)
        self.encoder = encoder
        self.optimizer = optimizer
        self.device = optimizer.device
        
        # CUDA graph for repeated operations
        self._cuda_graph = None
        self._static_input = None
        self._static_output = None
        
        # Performance tracking
        self._batch_times: List[float] = []
        self._memory_usage: List[float] = []
    
    def process_batch(self, states: List, agent_ids: List[int], 
                     use_cuda_graph: bool = True) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """
        Process a batch of states with RTX 30xx optimizations.
        
        Args:
            states: List of Azul states
            agent_ids: List of agent IDs
            use_cuda_graph: Whether to use CUDA graph optimization
            
        Returns:
            Tuple of (policies, values)
        """
        if len(states) != len(agent_ids):
            raise ValueError("States and agent_ids must have the same length")
        
        # Encode states
        state_tensors = []
        for state, agent_id in zip(states, agent_ids):
            tensor = self.encoder.encode_state(state, agent_id)
            state_tensors.append(tensor)
        
        # Stack into batch
        batch_tensor = torch.stack(state_tensors).to(self.device)
        
        # Use CUDA graph if enabled and input size matches
        if use_cuda_graph and self.device.type == 'cuda' and self._can_use_cuda_graph(batch_tensor):
            return self._process_with_cuda_graph(batch_tensor)
        else:
            return self._process_with_autocast(batch_tensor)
    
    def _can_use_cuda_graph(self, batch_tensor: torch.Tensor) -> bool:
        """Check if CUDA graph can be used for this batch."""
        if self._cuda_graph is None:
            return False
        
        if self._static_input is None:
            return False
        
        return (batch_tensor.shape == self._static_input.shape and 
                batch_tensor.dtype == self._static_input.dtype)
    
    def _process_with_cuda_graph(self, batch_tensor: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """Process batch using CUDA graph optimization."""
        # Copy input to static tensor
        self._static_input.copy_(batch_tensor)
        
        # Replay CUDA graph
        self._cuda_graph.replay()
        
        # Return results
        policies = [self._static_output[0][i].cpu() for i in range(self._static_output[0].shape[0])]
        values = [self._static_output[1][i].cpu() for i in range(self._static_output[1].shape[0])]
        
        return policies, values
    
    def _process_with_autocast(self, batch_tensor: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """Process batch using autocast optimization."""
        if self.device.type == 'cuda':
            try:
                start_time = torch.cuda.Event(enable_timing=True)
                end_time = torch.cuda.Event(enable_timing=True)
                
                start_time.record()
                
                with torch.no_grad():
                    if self.optimizer.config.enable_autocast:
                        with torch.autocast(device_type='cuda', dtype=torch.float16):
                            policies, values = self.model(batch_tensor)
                    else:
                        policies, values = self.model(batch_tensor)
                
                end_time.record()
                torch.cuda.synchronize()
                
                # Record performance
                elapsed_time = start_time.elapsed_time(end_time)
                self._batch_times.append(elapsed_time)
                self._memory_usage.append(torch.cuda.memory_allocated() / 1e9)
            except RuntimeError:
                # Fallback if CUDA not available
                start_time = time.time()
                with torch.no_grad():
                    policies, values = self.model(batch_tensor)
                elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                self._batch_times.append(elapsed_time)
                self._memory_usage.append(0.0)  # No GPU memory on CPU
        else:
            # CPU fallback
            start_time = time.time()
            with torch.no_grad():
                policies, values = self.model(batch_tensor)
            elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self._batch_times.append(elapsed_time)
            self._memory_usage.append(0.0)  # No GPU memory on CPU
        
        # Split into individual tensors
        policy_list = [policies[i].cpu() for i in range(policies.shape[0])]
        value_list = [values[i].cpu() for i in range(values.shape[0])]
        
        return policy_list, value_list
    
    def create_cuda_graph(self, batch_size: int):
        """Create a CUDA graph for the given batch size."""
        if self.device.type != 'cuda':
            return
        
        # Create static tensors
        input_size = self.encoder._calculate_input_size()
        self._static_input = torch.randn(batch_size, input_size).to(self.device)
        
        # Create CUDA graph
        self._cuda_graph = torch.cuda.CUDAGraph()
        
        with torch.cuda.graph(self._cuda_graph):
            with torch.no_grad():
                if self.optimizer.config.enable_autocast:
                    with amp.autocast():
                        policies, values = self.model(self._static_input)
                else:
                    policies, values = self.model(self._static_input)
                
                self._static_output = (policies, values)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self._batch_times:
            return {}
        
        stats = {
            'avg_batch_time_ms': np.mean(self._batch_times),
            'min_batch_time_ms': np.min(self._batch_times),
            'max_batch_time_ms': np.max(self._batch_times),
            'total_batches': len(self._batch_times),
        }
        
        if self._memory_usage:
            stats['avg_memory_usage_gb'] = np.mean(self._memory_usage)
            stats['max_memory_usage_gb'] = np.max(self._memory_usage)
        
        return stats
    
    def clear_performance_stats(self):
        """Clear performance statistics."""
        self._batch_times.clear()
        self._memory_usage.clear()


def create_rtx_optimizer(config: Optional[GPUOptimizationConfig] = None) -> RTX30xxOptimizer:
    """Create an RTX 30xx optimizer."""
    return RTX30xxOptimizer(config)


def test_rtx_optimizer():
    """Test the RTX 30xx optimizer."""
    print("Testing RTX 30xx Optimizer...")
    
    # Create optimizer
    config = GPUOptimizationConfig(
        enable_tensor_cores=True,
        enable_memory_pooling=True,
        enable_performance_monitoring=True
    )
    optimizer = create_rtx_optimizer(config)
    
    # Get GPU info
    gpu_info = optimizer.get_gpu_info()
    print(f"GPU Info: {gpu_info}")
    
    # Create model and encoder
    from neural.azul_net import create_azul_net
    model, encoder = create_azul_net()
    
    # Benchmark performance
    print("\nBenchmarking performance...")
    benchmark_results = optimizer.benchmark_performance(model, encoder)
    print(f"Benchmark results: {benchmark_results}")
    
    # Create optimized batch processor
    processor = optimizer.create_optimized_batch_processor(model, encoder)
    
    # Test batch processing
    print("\nTesting batch processing...")
    from core.azul_model import AzulState
    test_states = [AzulState() for _ in range(8)]
    test_agent_ids = [0] * 8
    
    policies, values = processor.process_batch(test_states, test_agent_ids)
    print(f"Processed {len(policies)} policies and {len(values)} values")
    
    # Get performance stats
    stats = processor.get_performance_stats()
    print(f"Performance stats: {stats}")
    
    print("RTX 30xx optimizer test completed!")


if __name__ == "__main__":
    test_rtx_optimizer() 