"""
Neural Model Evaluation Framework

This module provides comprehensive evaluation of neural models against heuristic baselines,
including performance metrics, accuracy analysis, and comparative studies.
"""

import torch
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import os

from core.azul_model import AzulState
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator
from analysis_engine.mathematical_optimization.azul_move_generator import AzulMoveGenerator
from neural.azul_net import AzulNet, AzulTensorEncoder, create_azul_net
from neural.batch_evaluator import BatchNeuralEvaluator, BatchConfig
from neural.policy_mapping import PolicyMapper, SelectionMethod


class EvaluationMetric(Enum):
    """Enumeration of evaluation metrics."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    MEAN_SQUARED_ERROR = "mse"
    MEAN_ABSOLUTE_ERROR = "mae"
    CORRELATION = "correlation"
    AGREEMENT_RATE = "agreement_rate"


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    
    # Test parameters
    num_test_positions: int = 1000
    max_depth_per_position: int = 10
    num_simulations_per_position: int = 100
    
    # Evaluation metrics
    metrics: List[EvaluationMetric] = None
    
    # Performance parameters
    batch_size: int = 32
    enable_gpu: bool = True
    
    # Comparison parameters
    compare_with_heuristic: bool = True
    compare_with_random: bool = True
    compare_with_mcts: bool = True
    
    # Output parameters
    save_results: bool = True
    results_file: str = "neural_evaluation_results.json"
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = [
                EvaluationMetric.ACCURACY,
                EvaluationMetric.AGREEMENT_RATE,
                EvaluationMetric.CORRELATION,
                EvaluationMetric.MEAN_ABSOLUTE_ERROR
            ]


class NeuralModelEvaluator:
    """
    Comprehensive neural model evaluation system.
    
    This class provides evaluation of neural models against various baselines,
    including heuristic evaluation, random play, and MCTS-based approaches.
    """
    
    def __init__(self, model: AzulNet, encoder: AzulTensorEncoder,
                 config: Optional[EvaluationConfig] = None):
        """Initialize the neural model evaluator."""
        self.model = model
        self.encoder = encoder
        self.config = config or EvaluationConfig()
        
        # Initialize components
        self.evaluator = AzulEvaluator()
        self.move_generator = AzulMoveGenerator()
        self.policy_mapper = PolicyMapper()
        
        # Setup batch evaluator
        batch_config = BatchConfig(
            default_batch_size=self.config.batch_size,
            enable_performance_monitoring=True
        )
        self.batch_evaluator = BatchNeuralEvaluator(model, encoder, batch_config)
        
        # Results storage
        self.evaluation_results: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
    
    def evaluate_model(self, test_positions: Optional[List[AzulState]] = None) -> Dict[str, Any]:
        """
        Comprehensive model evaluation against multiple baselines.
        
        Args:
            test_positions: List of test positions (generated if None)
            
        Returns:
            Comprehensive evaluation results
        """
        print("Starting comprehensive neural model evaluation...")
        
        # Generate test positions if not provided
        if test_positions is None:
            test_positions = self._generate_test_positions()
        
        print(f"Evaluating {len(test_positions)} test positions...")
        
        # Evaluate neural model
        neural_results = self._evaluate_neural_model(test_positions)
        
        # Compare with baselines
        comparison_results = {}
        
        if self.config.compare_with_heuristic:
            heuristic_results = self._evaluate_heuristic_baseline(test_positions)
            comparison_results['heuristic'] = self._compare_models(neural_results, heuristic_results)
        
        if self.config.compare_with_random:
            random_results = self._evaluate_random_baseline(test_positions)
            comparison_results['random'] = self._compare_models(neural_results, random_results)
        
        if self.config.compare_with_mcts:
            mcts_results = self._evaluate_mcts_baseline(test_positions)
            comparison_results['mcts'] = self._compare_models(neural_results, mcts_results)
        
        # Compile results
        self.evaluation_results = {
            'neural_model': neural_results,
            'comparisons': comparison_results,
            'test_positions_count': len(test_positions),
            'evaluation_config': self.config.__dict__,
            'timestamp': time.time()
        }
        
        # Save results if requested
        if self.config.save_results:
            self._save_results()
        
        return self.evaluation_results
    
    def _generate_test_positions(self) -> List[AzulState]:
        """Generate diverse test positions for evaluation."""
        print("Generating test positions...")
        
        test_positions = []
        for i in range(self.config.num_test_positions):
            # Create a random game state (2-player game)
            state = AzulState(2)
            
            # Simulate some moves to create interesting positions
            num_moves = np.random.randint(5, 20)
            for _ in range(num_moves):
                legal_moves = self.move_generator.generate_moves(state, 0)
                if not legal_moves:
                    break
                
                # Random move selection for position generation
                move = np.random.choice(legal_moves)
                state = self._apply_move(state, move)
            
            test_positions.append(state)
        
        print(f"Generated {len(test_positions)} test positions")
        return test_positions
    
    def _evaluate_neural_model(self, test_positions: List[AzulState]) -> Dict[str, Any]:
        """Evaluate the neural model on test positions."""
        print("Evaluating neural model...")
        
        results = {
            'evaluations': [],
            'move_selections': [],
            'policy_confidence': [],
            'inference_times': []
        }
        
        # Process in batches
        for i in range(0, len(test_positions), self.config.batch_size):
            batch_positions = test_positions[i:i + self.config.batch_size]
            batch_agent_ids = [0] * len(batch_positions)
            
            # Get neural evaluations
            start_time = time.time()
            neural_scores = self.batch_evaluator.evaluate_batch(batch_positions, batch_agent_ids)
            end_time = time.time()
            
            # Get policy outputs
            policies = self.batch_evaluator.get_policy_batch(batch_positions, batch_agent_ids)
            
            # Evaluate move selection for each position
            for j, (position, policy, score) in enumerate(zip(batch_positions, policies, neural_scores)):
                legal_moves = self.move_generator.generate_moves(position, 0)
                
                if legal_moves:
                    # Select move using neural policy
                    selected_move = self.policy_mapper.select_move(
                        policy, legal_moves, SelectionMethod.GREEDY
                    )
                    
                    # Calculate policy confidence - policy is already a single tensor for this position
                    confidence = self.policy_mapper.get_move_confidence(
                        policy, selected_move, legal_moves
                    )
                    
                    results['move_selections'].append(selected_move)
                    results['policy_confidence'].append(confidence)
                else:
                    results['move_selections'].append(None)
                    results['policy_confidence'].append(0.0)
                
                results['evaluations'].append(score)
                results['inference_times'].append((end_time - start_time) / len(batch_positions))
        
        # Calculate metrics
        results['metrics'] = self._calculate_metrics(results)
        
        print(f"Neural model evaluation completed: {len(results['evaluations'])} positions")
        return results
    
    def _evaluate_heuristic_baseline(self, test_positions: List[AzulState]) -> Dict[str, Any]:
        """Evaluate heuristic baseline on test positions."""
        print("Evaluating heuristic baseline...")
        
        results = {
            'evaluations': [],
            'move_selections': [],
            'evaluation_times': []
        }
        
        for position in test_positions:
            start_time = time.time()
            
            # Get heuristic evaluation
            heuristic_score = self.evaluator.evaluate_position(position, 0)
            
            # Get heuristic move selection
            legal_moves = self.move_generator.generate_moves(position, 0)
            if legal_moves:
                # Select best move based on heuristic evaluation
                best_move = None
                best_score = float('-inf')
                
                for move in legal_moves:
                    # Simulate move and evaluate
                    new_state = self._apply_move(position, move)
                    move_score = self.evaluator.evaluate_position(new_state, 0)
                    
                    if move_score > best_score:
                        best_score = move_score
                        best_move = move
                
                results['move_selections'].append(best_move)
            else:
                results['move_selections'].append(None)
            
            end_time = time.time()
            results['evaluations'].append(heuristic_score)
            results['evaluation_times'].append(end_time - start_time)
        
        print(f"Heuristic baseline evaluation completed: {len(results['evaluations'])} positions")
        return results
    
    def _evaluate_random_baseline(self, test_positions: List[AzulState]) -> Dict[str, Any]:
        """Evaluate random baseline on test positions."""
        print("Evaluating random baseline...")
        
        results = {
            'evaluations': [],
            'move_selections': [],
            'evaluation_times': []
        }
        
        for position in test_positions:
            start_time = time.time()
            
            # Random evaluation (simplified)
            random_score = np.random.normal(0, 1)
            
            # Random move selection
            legal_moves = self.move_generator.generate_moves(position, 0)
            if legal_moves:
                random_move = np.random.choice(legal_moves)
                results['move_selections'].append(random_move)
            else:
                results['move_selections'].append(None)
            
            end_time = time.time()
            results['evaluations'].append(random_score)
            results['evaluation_times'].append(end_time - start_time)
        
        print(f"Random baseline evaluation completed: {len(results['evaluations'])} positions")
        return results
    
    def _evaluate_mcts_baseline(self, test_positions: List[AzulState]) -> Dict[str, Any]:
        """Evaluate MCTS baseline on test positions."""
        print("Evaluating MCTS baseline...")
        
        results = {
            'evaluations': [],
            'move_selections': [],
            'evaluation_times': []
        }
        
        for position in test_positions:
            start_time = time.time()
            
            # Simplified MCTS evaluation (using heuristic evaluator)
            mcts_score = self.evaluator.evaluate_position(position, 0)
            
            # Simplified MCTS move selection
            legal_moves = self.move_generator.generate_moves(position, 0)
            if legal_moves:
                # Use heuristic-based move selection as MCTS approximation
                best_move = None
                best_score = float('-inf')
                
                for move in legal_moves:
                    new_state = self._apply_move(position, move)
                    move_score = self.evaluator.evaluate_position(new_state, 0)
                    
                    if move_score > best_score:
                        best_score = move_score
                        best_move = move
                
                results['move_selections'].append(best_move)
            else:
                results['move_selections'].append(None)
            
            end_time = time.time()
            results['evaluations'].append(mcts_score)
            results['evaluation_times'].append(end_time - start_time)
        
        print(f"MCTS baseline evaluation completed: {len(results['evaluations'])} positions")
        return results
    
    def _compare_models(self, neural_results: Dict[str, Any], 
                       baseline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare neural model with baseline."""
        comparison = {}
        
        # Compare evaluations
        neural_scores = np.array(neural_results['evaluations'])
        baseline_scores = np.array(baseline_results['evaluations'])
        
        # Correlation
        if len(neural_scores) > 1 and len(baseline_scores) > 1:
            correlation = np.corrcoef(neural_scores, baseline_scores)[0, 1]
            comparison['correlation'] = correlation if not np.isnan(correlation) else 0.0
        
        # Agreement rate (for move selections)
        if 'move_selections' in neural_results and 'move_selections' in baseline_results:
            agreement_count = 0
            total_count = 0
            
            for neural_move, baseline_move in zip(neural_results['move_selections'], 
                                                baseline_results['move_selections']):
                if neural_move is not None and baseline_move is not None:
                    if neural_move == baseline_move:
                        agreement_count += 1
                    total_count += 1
            
            if total_count > 0:
                comparison['agreement_rate'] = agreement_count / total_count
            else:
                comparison['agreement_rate'] = 0.0
        
        # Performance comparison
        neural_time = np.mean(neural_results.get('inference_times', [0]))
        baseline_time = np.mean(baseline_results.get('evaluation_times', [0]))
        
        if baseline_time > 0:
            comparison['speedup_factor'] = baseline_time / neural_time
        else:
            comparison['speedup_factor'] = 1.0
        
        return comparison
    
    def _calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        metrics = {}
        
        evaluations = np.array(results['evaluations'])
        
        if len(evaluations) > 0:
            metrics['mean_evaluation'] = np.mean(evaluations)
            metrics['std_evaluation'] = np.std(evaluations)
            metrics['min_evaluation'] = np.min(evaluations)
            metrics['max_evaluation'] = np.max(evaluations)
        
        if 'policy_confidence' in results:
            confidences = np.array(results['policy_confidence'])
            if len(confidences) > 0:
                metrics['mean_confidence'] = np.mean(confidences)
                metrics['std_confidence'] = np.std(confidences)
        
        if 'inference_times' in results:
            times = np.array(results['inference_times'])
            if len(times) > 0:
                metrics['mean_inference_time'] = np.mean(times)
                metrics['total_inference_time'] = np.sum(times)
        
        return metrics
    
    def _apply_move(self, state: AzulState, move) -> AzulState:
        """Apply a move to a state and return new state."""
        # This is a simplified version - in practice, you'd use proper move application
        return state  # Placeholder
    
    def _save_results(self):
        """Save evaluation results to file."""
        if not self.config.save_results:
            return
        
        # Convert numpy arrays to lists for JSON serialization
        results_copy = self._convert_results_for_json(self.evaluation_results)
        
        with open(self.config.results_file, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        print(f"Evaluation results saved to {self.config.results_file}")
    
    def _convert_results_for_json(self, obj):
        """Convert numpy arrays and other non-serializable objects for JSON."""
        if isinstance(obj, dict):
            return {k: self._convert_results_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_results_for_json(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif hasattr(obj, 'to_dict'):  # Handle Move objects
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):  # Handle other objects
            return str(obj)
        else:
            return obj
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of model performance."""
        if not self.evaluation_results:
            return {}
        
        summary = {
            'total_positions_evaluated': self.evaluation_results.get('test_positions_count', 0),
            'neural_model_metrics': self.evaluation_results.get('neural_model', {}).get('metrics', {}),
            'comparison_summary': {}
        }
        
        # Summarize comparisons
        comparisons = self.evaluation_results.get('comparisons', {})
        for baseline_name, comparison in comparisons.items():
            summary['comparison_summary'][baseline_name] = {
                'correlation': comparison.get('correlation', 0.0),
                'agreement_rate': comparison.get('agreement_rate', 0.0),
                'speedup_factor': comparison.get('speedup_factor', 1.0)
            }
        
        return summary


def create_model_evaluator(model: Optional[AzulNet] = None,
                          encoder: Optional[AzulTensorEncoder] = None,
                          config: Optional[EvaluationConfig] = None) -> NeuralModelEvaluator:
    """Create a neural model evaluator."""
    if model is None or encoder is None:
        model, encoder = create_azul_net()
    
    return NeuralModelEvaluator(model, encoder, config)


def test_model_evaluation():
    """Test the model evaluation framework."""
    print("Testing Neural Model Evaluation Framework...")
    
    # Create evaluator
    config = EvaluationConfig(
        num_test_positions=10,  # Small number for testing
        batch_size=4,
        enable_gpu=False  # Use CPU for testing
    )
    evaluator = create_model_evaluator(config=config)
    
    # Run evaluation
    results = evaluator.evaluate_model()
    
    # Print summary
    summary = evaluator.get_performance_summary()
    print(f"\nEvaluation Summary: {summary}")
    
    print("Model evaluation test completed!")


if __name__ == "__main__":
    test_model_evaluation() 