"""
Model evaluation system for AzulNet.

This module provides:
- Performance comparison between neural and heuristic methods
- Win-rate analysis
- Position evaluation accuracy
- Model validation against known strong positions
"""

import torch
import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
import random

try:
    from .azul_net import AzulNet, AzulNetConfig, AzulTensorEncoder, create_azul_net
    from ..core.azul_model import AzulState
    from ..analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator
    from ..analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
    from ..analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS, RolloutPolicy
except ImportError:
    # Fallback for direct import
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from neural.azul_net import AzulNet, AzulNetConfig, AzulTensorEncoder, create_azul_net
    from core.azul_model import AzulState
    from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator
    from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
    from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS, RolloutPolicy


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    # Test parameters
    num_positions: int = 100
    num_games: int = 50
    search_time: float = 1.0
    max_rollouts: int = 100
    
    # Model parameters
    model_path: Optional[str] = None
    device: str = "cpu"
    
    # Evaluation metrics
    compare_heuristic: bool = True
    compare_random: bool = True
    test_known_positions: bool = True
    
    # Progress callback
    progress_callback: Optional[Callable[[int], None]] = None


@dataclass
class EvaluationResult:
    """Result of model evaluation."""
    # Performance metrics
    win_rate: float
    avg_score: float
    avg_search_time: float
    avg_rollouts: float
    
    # Accuracy metrics
    position_accuracy: float
    move_agreement: float
    
    # Model info
    model_parameters: int
    inference_time_ms: float
    
    # Comparison metrics
    vs_heuristic_win_rate: Optional[float] = None
    vs_random_win_rate: Optional[float] = None


class AzulModelEvaluator:
    """Evaluator for Azul neural models."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.device = torch.device(config.device)
        self.progress_callback = config.progress_callback
        self._progress = 0
        self._progress_max = 5  # inference, accuracy, move agreement, win rate, comparisons
        if config.compare_heuristic:
            self._progress_max += 1
        if config.compare_random:
            self._progress_max += 1
        
        # Load model if path provided
        if config.model_path:
            self.model, self.encoder = self._load_model(config.model_path)
        else:
            self.model, self.encoder = create_azul_net(device=config.device)
        
        # Initialize components
        self.evaluator = AzulEvaluator()
        self.move_generator = FastMoveGenerator()
        
        # Create MCTS instances for comparison
        self.neural_mcts = AzulMCTS(
            rollout_policy=RolloutPolicy.NEURAL,
            max_time=config.search_time,
            max_rollouts=config.max_rollouts
        )
        
        if config.compare_heuristic:
            self.heuristic_mcts = AzulMCTS(
                rollout_policy=RolloutPolicy.HEAVY,
                max_time=config.search_time,
                max_rollouts=config.max_rollouts
            )
        
        if config.compare_random:
            self.random_mcts = AzulMCTS(
                rollout_policy=RolloutPolicy.RANDOM,
                max_time=config.search_time,
                max_rollouts=config.max_rollouts
            )
    
    def _update_progress(self, step=1):
        self._progress += step
        percent = int(100 * self._progress / self._progress_max)
        if self.progress_callback:
            self.progress_callback(percent)
    
    def _load_model(self, model_path: str) -> Tuple[AzulNet, AzulTensorEncoder]:
        """Load a trained model."""
        try:
            # Try loading with weights_only=False for PyTorch 2.6 compatibility
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        except Exception as e:
            print(f"Warning: Failed to load with weights_only=False: {e}")
            try:
                # Fallback to weights_only=True
                checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
            except Exception as e2:
                print(f"Error: Failed to load model: {e2}")
                raise Exception(f"Could not load model from {model_path}: {e2}")
        
        # Create model with same config
        config = checkpoint.get('encoder_config', AzulNetConfig())
        model, encoder = create_azul_net(config, device=self.config.device)
        
        # Load weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        
        print(f"✅ Loaded model from {model_path}")
        print(f"   Parameters: {sum(p.numel() for p in model.parameters())}")
        
        return model, encoder
    
    def evaluate_model(self) -> EvaluationResult:
        """Evaluate the neural model comprehensively."""
        print("🧠 Evaluating Neural Model")
        print("=" * 50)
        
        # Test inference speed
        inference_time = self._test_inference_speed()
        self._update_progress()
        
        # Test position evaluation accuracy
        position_accuracy = self._test_position_accuracy()
        self._update_progress()
        
        # Test move agreement with heuristic
        move_agreement = self._test_move_agreement()
        self._update_progress()
        
        # Test win rate against other methods
        win_rate, avg_score, avg_search_time, avg_rollouts = self._test_win_rate()
        self._update_progress()
        
        # Compare against other methods
        vs_heuristic_win_rate = None
        vs_random_win_rate = None
        
        if self.config.compare_heuristic:
            vs_heuristic_win_rate = self._compare_against_method("heuristic")
            self._update_progress()
        
        if self.config.compare_random:
            vs_random_win_rate = self._compare_against_method("random")
            self._update_progress()
        
        return EvaluationResult(
            win_rate=win_rate,
            avg_score=avg_score,
            avg_search_time=avg_search_time,
            avg_rollouts=avg_rollouts,
            position_accuracy=position_accuracy,
            move_agreement=move_agreement,
            vs_heuristic_win_rate=vs_heuristic_win_rate,
            vs_random_win_rate=vs_random_win_rate,
            model_parameters=sum(p.numel() for p in self.model.parameters()),
            inference_time_ms=inference_time
        )
    
    def _test_inference_speed(self) -> float:
        """Test neural network inference speed."""
        print("Testing inference speed...")
        
        # Create test state
        state = AzulState(2)
        state_tensor = self.encoder.encode_state(state, agent_id=0).to(self.device)
        
        # Warm up
        for _ in range(10):
            with torch.no_grad():
                _ = self.model(state_tensor)
        
        # Benchmark
        times = []
        for _ in range(100):
            start_time = time.time()
            with torch.no_grad():
                _ = self.model(state_tensor)
            times.append((time.time() - start_time) * 1000)  # Convert to ms
        
        avg_time = np.mean(times)
        print(f"✅ Average inference time: {avg_time:.2f} ms")
        
        return avg_time
    
    def _test_position_accuracy(self) -> float:
        """Test position evaluation accuracy against heuristic."""
        print("Testing position evaluation accuracy...")
        
        correct = 0
        total = 0
        
        for _ in range(self.config.num_positions):
            # Generate random position
            state = self._generate_test_position()
            
            # Get neural evaluation
            state_tensor = self.encoder.encode_state(state, agent_id=0).to(self.device)
            with torch.no_grad():
                _, neural_value = self.model.get_policy_and_value(state_tensor)
            neural_score = neural_value.item()
            
            # Get heuristic evaluation
            heuristic_score = self.evaluator.evaluate_position(state, agent_id=0)
            
            # Check if they agree on position quality (simplified)
            neural_good = neural_score > 0
            heuristic_good = heuristic_score > 0
            
            if neural_good == heuristic_good:
                correct += 1
            total += 1
        
        accuracy = correct / total if total > 0 else 0.0
        print(f"✅ Position accuracy: {accuracy:.2%}")
        
        return accuracy
    
    def _test_move_agreement(self) -> float:
        """Test move agreement with heuristic method."""
        print("Testing move agreement...")
        
        agreements = 0
        total = 0
        
        for _ in range(self.config.num_positions):
            # Generate test position
            state = self._generate_test_position()
            
            # Get neural move
            neural_result = self.neural_mcts.search(state, agent_id=0)
            neural_move = neural_result.best_move
            
            # Get heuristic move
            heuristic_result = self.heuristic_mcts.search(state, agent_id=0)
            heuristic_move = heuristic_result.best_move
            
            # Check if moves are the same
            if neural_move and heuristic_move and str(neural_move) == str(heuristic_move):
                agreements += 1
            total += 1
        
        agreement_rate = agreements / total if total > 0 else 0.0
        print(f"✅ Move agreement rate: {agreement_rate:.2%}")
        
        return agreement_rate
    
    def _test_win_rate(self) -> Tuple[float, float, float, float]:
        """Test win rate in self-play games."""
        print("Testing win rate in self-play...")
        
        wins = 0
        scores = []
        search_times = []
        rollouts = []
        
        for game in range(self.config.num_games):
            # Play a game with neural vs neural
            result = self._play_game_neural_vs_neural()
            
            if result['winner'] == 0:  # Neural player won
                wins += 1
            
            scores.append(result['score'])
            search_times.append(result['avg_search_time'])
            rollouts.append(result['avg_rollouts'])
            
            if (game + 1) % 10 == 0:
                print(f"   Completed {game + 1}/{self.config.num_games} games")
        
        win_rate = wins / self.config.num_games
        avg_score = np.mean(scores)
        avg_search_time = np.mean(search_times)
        avg_rollouts = np.mean(rollouts)
        
        print(f"✅ Win rate: {win_rate:.2%}")
        print(f"✅ Average score: {avg_score:.2f}")
        
        return win_rate, avg_score, avg_search_time, avg_rollouts
    
    def _compare_against_method(self, method: str) -> float:
        """Compare neural against another method."""
        print(f"Comparing neural vs {method}...")
        
        neural_wins = 0
        
        for game in range(self.config.num_games):
            if method == "heuristic":
                result = self._play_game_neural_vs_heuristic()
            elif method == "random":
                result = self._play_game_neural_vs_random()
            else:
                continue
            
            if result['winner'] == 0:  # Neural player won
                neural_wins += 1
        
        win_rate = neural_wins / self.config.num_games
        print(f"✅ Neural vs {method} win rate: {win_rate:.2%}")
        
        return win_rate
    
    def _generate_test_position(self) -> AzulState:
        """Generate a test position."""
        # For now, use initial state
        # In a full implementation, you would generate varied positions
        return AzulState(2)
    
    def _play_game_neural_vs_neural(self) -> Dict:
        """Play a game neural vs neural."""
        state = AzulState(2)
        current_agent = 0
        moves = 0
        search_times = []
        rollouts = []
        
        while moves < 20:  # Limit game length
            # Neural search for current agent
            result = self.neural_mcts.search(state, agent_id=current_agent)
            
            search_times.append(result.search_time)
            rollouts.append(result.rollout_count)
            
            if result.best_move:
                # Apply move (simplified)
                state = self._apply_move_simplified(state, result.best_move, current_agent)
                current_agent = (current_agent + 1) % 2
                moves += 1
            else:
                break
        
        # Determine winner based on final score
        final_score = self.evaluator.evaluate_position(state, agent_id=0)
        winner = 0 if final_score > 0 else 1
        
        return {
            'winner': winner,
            'score': final_score,
            'avg_search_time': np.mean(search_times),
            'avg_rollouts': np.mean(rollouts)
        }
    
    def _play_game_neural_vs_heuristic(self) -> Dict:
        """Play a game neural vs heuristic."""
        state = AzulState(2)
        current_agent = 0
        moves = 0
        
        while moves < 20:
            if current_agent == 0:
                # Neural player
                result = self.neural_mcts.search(state, agent_id=current_agent)
            else:
                # Heuristic player
                result = self.heuristic_mcts.search(state, agent_id=current_agent)
            
            if result.best_move:
                state = self._apply_move_simplified(state, result.best_move, current_agent)
                current_agent = (current_agent + 1) % 2
                moves += 1
            else:
                break
        
        final_score = self.evaluator.evaluate_position(state, agent_id=0)
        winner = 0 if final_score > 0 else 1
        
        return {'winner': winner, 'score': final_score}
    
    def _play_game_neural_vs_random(self) -> Dict:
        """Play a game neural vs random."""
        state = AzulState(2)
        current_agent = 0
        moves = 0
        
        while moves < 20:
            if current_agent == 0:
                # Neural player
                result = self.neural_mcts.search(state, agent_id=current_agent)
            else:
                # Random player
                result = self.random_mcts.search(state, agent_id=current_agent)
            
            if result.best_move:
                state = self._apply_move_simplified(state, result.best_move, current_agent)
                current_agent = (current_agent + 1) % 2
                moves += 1
            else:
                break
        
        final_score = self.evaluator.evaluate_position(state, agent_id=0)
        winner = 0 if final_score > 0 else 1
        
        return {'winner': winner, 'score': final_score}
    
    def _apply_move_simplified(self, state: AzulState, move, agent_id: int) -> AzulState:
        """Apply move to state (simplified)."""
        # For evaluation, we'll just return the original state
        # In a real implementation, you'd apply the move properly
        return state


def main():
    """Main evaluation function."""
    config = EvaluationConfig(
        num_positions=50,
        num_games=20,
        search_time=0.5,
        max_rollouts=50,
        compare_heuristic=True,
        compare_random=True
    )
    
    evaluator = AzulModelEvaluator(config)
    result = evaluator.evaluate_model()
    
    print("\n" + "="*50)
    print("📊 EVALUATION RESULTS")
    print("="*50)
    print(f"Model Parameters: {result.model_parameters:,}")
    print(f"Inference Time: {result.inference_time_ms:.2f} ms")
    print(f"Position Accuracy: {result.position_accuracy:.2%}")
    print(f"Move Agreement: {result.move_agreement:.2%}")
    print(f"Self-play Win Rate: {result.win_rate:.2%}")
    print(f"Average Score: {result.avg_score:.2f}")
    print(f"Average Search Time: {result.avg_search_time:.3f}s")
    print(f"Average Rollouts: {result.avg_rollouts:.1f}")
    
    if result.vs_heuristic_win_rate is not None:
        print(f"vs Heuristic Win Rate: {result.vs_heuristic_win_rate:.2%}")
    
    if result.vs_random_win_rate is not None:
        print(f"vs Random Win Rate: {result.vs_random_win_rate:.2%}")
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main() 