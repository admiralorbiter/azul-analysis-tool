"""
Tests for Batch Neural Inference System

This module provides comprehensive tests for the batch inference system,
including GPU optimization, memory management, and performance monitoring.
"""

import unittest
import torch
import numpy as np
import time
from typing import List, Dict, Any

from neural.batch_evaluator import BatchNeuralEvaluator, BatchConfig, create_batch_evaluator
from neural.gpu_optimizer import RTX30xxOptimizer, GPUOptimizationConfig, create_rtx_optimizer
from neural.model_evaluation import NeuralModelEvaluator, EvaluationConfig, create_model_evaluator
from neural.azul_net import create_azul_net
from core.azul_model import AzulState


class TestBatchInference(unittest.TestCase):
    """Test cases for batch inference system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create model and encoder
        self.model, self.encoder = create_azul_net()
        
        # Create batch config
        self.batch_config = BatchConfig(
            default_batch_size=8,
            enable_performance_monitoring=True,
            enable_memory_optimization=True
        )
        
        # Create batch evaluator
        self.batch_evaluator = create_batch_evaluator(
            self.model, self.encoder, self.batch_config
        )
    
    def test_batch_evaluator_creation(self):
        """Test batch evaluator creation."""
        self.assertIsNotNone(self.batch_evaluator)
        self.assertIsNotNone(self.batch_evaluator.model)
        self.assertIsNotNone(self.batch_evaluator.encoder)
        self.assertEqual(self.batch_evaluator.config.default_batch_size, 8)
    
    def test_device_selection(self):
        """Test automatic device selection."""
        device = self.batch_evaluator.device
        self.assertIsInstance(device, torch.device)
        
        # Should select CPU if no GPU available, or CUDA if available
        if torch.cuda.is_available():
            self.assertIn(device.type, ['cuda', 'cpu'])
        else:
            self.assertEqual(device.type, 'cpu')
    
    def test_optimal_batch_size_detection(self):
        """Test optimal batch size detection."""
        optimal_size = self.batch_evaluator._optimal_batch_size
        self.assertIsInstance(optimal_size, int)
        self.assertGreater(optimal_size, 0)
        self.assertLessEqual(optimal_size, self.batch_config.max_batch_size)
    
    def test_batch_evaluation(self):
        """Test batch evaluation functionality."""
        # Create test states
        test_states = [AzulState(2) for _ in range(16)]
        test_agent_ids = [0] * 16
        
        # Run batch evaluation
        scores = self.batch_evaluator.evaluate_batch(test_states, test_agent_ids)
        
        # Check results
        self.assertEqual(len(scores), 16)
        self.assertIsInstance(scores[0], (int, float))
        
        # Check that all scores are finite
        for score in scores:
            self.assertTrue(np.isfinite(score))
    
    def test_policy_batch_processing(self):
        """Test policy batch processing."""
        # Create test states
        test_states = [AzulState(2) for _ in range(8)]
        test_agent_ids = [0] * 8
        
        # Get policy outputs
        policies = self.batch_evaluator.get_policy_batch(test_states, test_agent_ids)
        
        # Check results
        self.assertEqual(len(policies), 8)
        for policy in policies:
            self.assertIsInstance(policy, torch.Tensor)
            # Policy can be 1D or 2D depending on the model output
            self.assertIn(policy.dim(), [1, 2])
    
    def test_move_selection_batch(self):
        """Test batch move selection."""
        from core.azul_move_generator import AzulMoveGenerator
        from neural.policy_mapping import SelectionMethod
        
        move_generator = AzulMoveGenerator()
        
        # Create test states
        test_states = [AzulState(2) for _ in range(4)]
        test_agent_ids = [0] * 4
        
        # Get legal moves for each state
        legal_moves_list = []
        for state in test_states:
            legal_moves = move_generator.generate_moves(state, 0)
            legal_moves_list.append(legal_moves)
        
        # Select moves using neural policy
        selected_moves = self.batch_evaluator.select_moves_batch(
            test_states, test_agent_ids, legal_moves_list,
            method=SelectionMethod.GREEDY
        )
        
        # Check results
        self.assertEqual(len(selected_moves), 4)
        for i, move in enumerate(selected_moves):
            if legal_moves_list[i]:  # If there are legal moves
                self.assertIsNotNone(move)
            else:
                self.assertIsNone(move)
    
    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        # Run some evaluations
        test_states = [AzulState(2) for _ in range(8)]
        test_agent_ids = [0] * 8
        
        self.batch_evaluator.evaluate_batch(test_states, test_agent_ids)
        
        # Get performance stats
        stats = self.batch_evaluator.get_performance_stats()
        
        # Check that stats are available
        self.assertIsInstance(stats, dict)
        if stats:  # If stats are available
            self.assertIn('total_inferences', stats)
            self.assertIn('optimal_batch_size', stats)
            self.assertIn('device', stats)
    
    def test_memory_monitoring(self):
        """Test memory monitoring functionality."""
        memory_info = self.batch_evaluator.get_memory_info()
        
        # Check memory info structure
        self.assertIsInstance(memory_info, dict)
        self.assertIn('cpu_memory_used', memory_info)
        self.assertIn('cpu_memory_percent', memory_info)
        
        if self.batch_evaluator.device.type == 'cuda':
            self.assertIn('gpu_memory_allocated', memory_info)
    
    def test_batch_size_optimization(self):
        """Test batch size optimization."""
        original_size = self.batch_evaluator._optimal_batch_size
        
        # Optimize batch size
        new_size = self.batch_evaluator.optimize_batch_size()
        
        # Check that optimization worked
        self.assertIsInstance(new_size, int)
        self.assertGreater(new_size, 0)
        self.assertLessEqual(new_size, self.batch_config.max_batch_size)
        
        # Check that optimal size was updated
        self.assertEqual(self.batch_evaluator._optimal_batch_size, new_size)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with mismatched states and agent_ids
        test_states = [AzulState(2) for _ in range(4)]
        test_agent_ids = [0, 1]  # Mismatched length
        
        with self.assertRaises(ValueError):
            self.batch_evaluator.evaluate_batch(test_states, test_agent_ids)
        
        # Test with empty states list
        with self.assertRaises(ValueError):
            self.batch_evaluator.evaluate_batch([], [])
    
    def test_mixed_precision(self):
        """Test mixed precision functionality."""
        if self.batch_evaluator.device.type == 'cuda':
            # Test that mixed precision is enabled
            self.assertTrue(self.batch_evaluator.config.enable_mixed_precision)
            
            # Test batch evaluation with mixed precision
            test_states = [AzulState(2) for _ in range(4)]
            test_agent_ids = [0] * 4
            
            scores = self.batch_evaluator.evaluate_batch(test_states, test_agent_ids)
            self.assertEqual(len(scores), 4)


class TestRTXOptimizer(unittest.TestCase):
    """Test cases for RTX 30xx optimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create optimizer config
        self.optimizer_config = GPUOptimizationConfig(
            enable_tensor_cores=True,
            enable_memory_pooling=True,
            enable_performance_monitoring=True
        )
        
        # Create optimizer
        self.optimizer = create_rtx_optimizer(self.optimizer_config)
        
        # Create model and encoder
        self.model, self.encoder = create_azul_net()
    
    def test_optimizer_creation(self):
        """Test RTX optimizer creation."""
        self.assertIsNotNone(self.optimizer)
        self.assertIsNotNone(self.optimizer.config)
        self.assertEqual(self.optimizer.config.enable_tensor_cores, True)
    
    def test_device_setup(self):
        """Test device setup."""
        device = self.optimizer.device
        self.assertIsInstance(device, torch.device)
        
        # Should be CUDA if available, CPU otherwise
        if torch.cuda.is_available():
            self.assertIn(device.type, ['cuda', 'cpu'])
        else:
            self.assertEqual(device.type, 'cpu')
    
    def test_gpu_info(self):
        """Test GPU information retrieval."""
        gpu_info = self.optimizer.get_gpu_info()
        self.assertIsInstance(gpu_info, dict)
        
        if self.optimizer.device.type == 'cuda':
            self.assertIn('name', gpu_info)
            self.assertIn('total_memory_gb', gpu_info)
            self.assertIn('memory_allocated_gb', gpu_info)
        else:
            self.assertEqual(gpu_info['device'], 'cpu')
    
    def test_model_optimization(self):
        """Test model optimization."""
        # Optimize model
        optimized_model = self.optimizer.optimize_model(self.model)
        
        # Check that model is on correct device
        self.assertEqual(next(optimized_model.parameters()).device, self.optimizer.device)
        
        # Check mixed precision conversion if enabled and on GPU
        if self.optimizer.config.enable_tensor_cores and self.optimizer.device.type == 'cuda':
            if self.optimizer.config.mixed_precision_dtype == "float16":
                # Check that model is in half precision
                for param in optimized_model.parameters():
                    self.assertEqual(param.dtype, torch.float16)
    
    def test_batch_processor_creation(self):
        """Test optimized batch processor creation."""
        processor = self.optimizer.create_optimized_batch_processor(self.model, self.encoder)
        
        self.assertIsNotNone(processor)
        self.assertIsNotNone(processor.model)
        self.assertIsNotNone(processor.encoder)
        self.assertEqual(processor.device, self.optimizer.device)
    
    def test_batch_processing(self):
        """Test optimized batch processing."""
        processor = self.optimizer.create_optimized_batch_processor(self.model, self.encoder)
        
        # Create test states
        test_states = [AzulState(2) for _ in range(4)]
        test_agent_ids = [0] * 4
        
        # Process batch
        policies, values = processor.process_batch(test_states, test_agent_ids)
        
        # Check results
        self.assertEqual(len(policies), 4)
        self.assertEqual(len(values), 4)
        
        for policy, value in zip(policies, values):
            self.assertIsInstance(policy, torch.Tensor)
            self.assertIsInstance(value, torch.Tensor)
    
    def test_performance_benchmarking(self):
        """Test performance benchmarking."""
        # Run benchmark
        benchmark_results = self.optimizer.benchmark_performance(self.model, self.encoder)
        
        # Check results structure
        self.assertIsInstance(benchmark_results, dict)
        
        # Check that we have results for at least one batch size
        self.assertGreater(len(benchmark_results), 0)
        
        for batch_size, result in benchmark_results.items():
            if 'error' not in result:
                self.assertIn('elapsed_time_ms', result)
                self.assertIn('throughput_states_per_second', result)
                self.assertIn('memory_usage_gb', result)
    
    def test_cuda_graph_creation(self):
        """Test CUDA graph creation."""
        if self.optimizer.device.type == 'cuda':
            processor = self.optimizer.create_optimized_batch_processor(self.model, self.encoder)
            
            # Create CUDA graph
            processor.create_cuda_graph(4)
            
            # Check that CUDA graph was created
            self.assertIsNotNone(processor._cuda_graph)
            self.assertIsNotNone(processor._static_input)
            self.assertIsNotNone(processor._static_output)
    
    def test_performance_stats(self):
        """Test performance statistics."""
        processor = self.optimizer.create_optimized_batch_processor(self.model, self.encoder)
        
        # Run some processing
        test_states = [AzulState(2) for _ in range(4)]
        test_agent_ids = [0] * 4
        
        processor.process_batch(test_states, test_agent_ids)
        
        # Get performance stats
        stats = processor.get_performance_stats()
        
        # Check stats structure
        if stats:  # If stats are available
            self.assertIn('total_batches', stats)
            self.assertIn('avg_batch_time_ms', stats)
    
    def test_memory_optimization(self):
        """Test memory optimization features."""
        # Check that memory optimization is enabled
        self.assertTrue(self.optimizer.config.enable_memory_pooling)
        
        if self.optimizer.device.type == 'cuda':
            # Check memory fraction setting
            self.assertEqual(self.optimizer.config.memory_fraction, 0.8)


class TestModelEvaluation(unittest.TestCase):
    """Test cases for model evaluation framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create evaluation config
        self.eval_config = EvaluationConfig(
            num_test_positions=10,
            batch_size=4,
            enable_gpu=False  # Use CPU for testing
        )
        
        # Create model evaluator
        self.evaluator = create_model_evaluator(config=self.eval_config)
    
    def test_evaluator_creation(self):
        """Test model evaluator creation."""
        self.assertIsNotNone(self.evaluator)
        self.assertIsNotNone(self.evaluator.model)
        self.assertIsNotNone(self.evaluator.encoder)
        self.assertEqual(self.evaluator.config.num_test_positions, 10)
    
    def test_test_position_generation(self):
        """Test test position generation."""
        positions = self.evaluator._generate_test_positions()
        
        # Check results
        self.assertEqual(len(positions), 10)
        for position in positions:
            self.assertIsInstance(position, AzulState)
    
    def test_neural_model_evaluation(self):
        """Test neural model evaluation."""
        # Create test positions
        test_positions = [AzulState(2) for _ in range(4)]
        
        # Evaluate neural model
        results = self.evaluator._evaluate_neural_model(test_positions)
        
        # Check results structure
        self.assertIn('evaluations', results)
        self.assertIn('move_selections', results)
        self.assertIn('policy_confidence', results)
        self.assertIn('inference_times', results)
        self.assertIn('metrics', results)
        
        # Check results
        self.assertEqual(len(results['evaluations']), 4)
        self.assertEqual(len(results['move_selections']), 4)
        self.assertEqual(len(results['policy_confidence']), 4)
    
    def test_heuristic_baseline_evaluation(self):
        """Test heuristic baseline evaluation."""
        # Create test positions
        test_positions = [AzulState(2) for _ in range(4)]
        
        # Evaluate heuristic baseline
        results = self.evaluator._evaluate_heuristic_baseline(test_positions)
        
        # Check results structure
        self.assertIn('evaluations', results)
        self.assertIn('move_selections', results)
        self.assertIn('evaluation_times', results)
        
        # Check results
        self.assertEqual(len(results['evaluations']), 4)
        self.assertEqual(len(results['move_selections']), 4)
    
    def test_model_comparison(self):
        """Test model comparison functionality."""
        # Create mock results
        neural_results = {
            'evaluations': [0.1, 0.2, 0.3, 0.4],
            'move_selections': [None, None, None, None],
            'inference_times': [0.001, 0.001, 0.001, 0.001]
        }
        
        baseline_results = {
            'evaluations': [0.15, 0.25, 0.35, 0.45],
            'move_selections': [None, None, None, None],
            'evaluation_times': [0.01, 0.01, 0.01, 0.01]
        }
        
        # Compare models
        comparison = self.evaluator._compare_models(neural_results, baseline_results)
        
        # Check comparison results
        self.assertIn('correlation', comparison)
        self.assertIn('agreement_rate', comparison)
        self.assertIn('speedup_factor', comparison)
        
        # Check that correlation is reasonable
        self.assertGreaterEqual(comparison['correlation'], -1.0)
        self.assertLessEqual(comparison['correlation'], 1.0)
    
    def test_metrics_calculation(self):
        """Test metrics calculation."""
        # Create mock results
        results = {
            'evaluations': [0.1, 0.2, 0.3, 0.4],
            'policy_confidence': [0.8, 0.9, 0.7, 0.6],
            'inference_times': [0.001, 0.002, 0.001, 0.002]
        }
        
        # Calculate metrics
        metrics = self.evaluator._calculate_metrics(results)
        
        # Check metrics
        self.assertIn('mean_evaluation', metrics)
        self.assertIn('std_evaluation', metrics)
        self.assertIn('mean_confidence', metrics)
        self.assertIn('mean_inference_time', metrics)
        
        # Check that metrics are reasonable
        self.assertGreater(metrics['mean_evaluation'], 0)
        self.assertGreater(metrics['mean_confidence'], 0)
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        # Create mock evaluation results
        self.evaluator.evaluation_results = {
            'test_positions_count': 10,
            'neural_model': {
                'metrics': {
                    'mean_evaluation': 0.5,
                    'mean_confidence': 0.8
                }
            },
            'comparisons': {
                'heuristic': {
                    'correlation': 0.7,
                    'agreement_rate': 0.6,
                    'speedup_factor': 2.0
                }
            }
        }
        
        # Get performance summary
        summary = self.evaluator.get_performance_summary()
        
        # Check summary structure
        self.assertIn('total_positions_evaluated', summary)
        self.assertIn('neural_model_metrics', summary)
        self.assertIn('comparison_summary', summary)
        
        # Check values
        self.assertEqual(summary['total_positions_evaluated'], 10)
        self.assertEqual(summary['neural_model_metrics']['mean_evaluation'], 0.5)


def run_batch_inference_tests():
    """Run all batch inference tests."""
    print("Running Batch Inference Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestBatchInference))
    test_suite.addTest(unittest.makeSuite(TestRTXOptimizer))
    test_suite.addTest(unittest.makeSuite(TestModelEvaluation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_batch_inference_tests()
    exit(0 if success else 1) 