#!/usr/bin/env python3
"""
Debug script to test MCTS functionality.
"""

import time
from core.azul_mcts import AzulMCTS, RolloutPolicy
from core.azul_model import AzulState
from core.azul_evaluator import AzulEvaluator

def test_mcts():
    print("Testing MCTS...")
    
    # Create initial state
    state = AzulState(2)
    print(f"Initial state created with {len(state.agents)} agents")
    
    # Test evaluator
    evaluator = AzulEvaluator()
    initial_score = evaluator.evaluate_position(state, 0)
    print(f"Initial position score: {initial_score}")
    
    # Test MCTS with short time
    print("Running MCTS with 0.5s time limit...")
    start_time = time.time()
    
    mcts = AzulMCTS(max_time=0.5, max_rollouts=50)
    result = mcts.search(state, 0)
    
    elapsed = time.time() - start_time
    print(f"MCTS completed in {elapsed:.3f}s")
    print(f"Best move: {result.best_move}")
    print(f"Best score: {result.best_score}")
    print(f"Rollouts completed: {result.rollout_count}")
    print(f"Search time: {result.search_time:.3f}s")
    print(f"Nodes searched: {result.nodes_searched}")

if __name__ == "__main__":
    test_mcts() 