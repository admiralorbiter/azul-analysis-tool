#!/usr/bin/env python3
"""
Benchmark script for A3 - Move Generator

This script tests the performance of the move generator and provides
detailed timing information to help optimize the implementation.
"""

import time
import statistics
from core.azul_move_generator import AzulMoveGenerator, FastMoveGenerator, OptimizedMoveGenerator
from core.azul_model import AzulState
from core import azul_utils as utils


def create_test_states():
    """Create various test states for benchmarking."""
    states = []
    
    # Initial state
    states.append(AzulState(2))
    
    # Mid-game state with some pattern lines filled
    mid_state = AzulState(2)
    mid_state.agents[0].lines_number[0] = 1
    mid_state.agents[0].lines_tile[0] = utils.Tile.BLUE
    mid_state.agents[0].lines_number[1] = 2
    mid_state.agents[0].lines_tile[1] = utils.Tile.RED
    states.append(mid_state)
    
    # Late-game state with many pattern lines filled
    late_state = AzulState(2)
    for i in range(3):
        late_state.agents[0].lines_number[i] = i + 1
        late_state.agents[0].lines_tile[i] = utils.Tile.BLUE
    states.append(late_state)
    
    return states


def benchmark_generator(generator, state, agent_id, num_runs=1000):
    """Benchmark a single generator on a single state."""
    # Warm up
    for _ in range(10):
        if hasattr(generator, 'generate_moves_fast'):
            generator.generate_moves_fast(state, agent_id)
        else:
            generator.generate_moves(state, agent_id)
    
    # Benchmark
    times = []
    for _ in range(num_runs):
        start_time = time.perf_counter()
        if hasattr(generator, 'generate_moves_fast'):
            moves = generator.generate_moves_fast(state, agent_id)
        else:
            moves = generator.generate_moves(state, agent_id)
        end_time = time.perf_counter()
        
        times.append((end_time - start_time) * 1_000_000)  # Convert to microseconds
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'std': statistics.stdev(times) if len(times) > 1 else 0,
        'num_moves': len(moves) if 'moves' in locals() else 0
    }


def main():
    """Run comprehensive benchmarks."""
    print("🎯 A3 - Move Generator Performance Benchmark")
    print("=" * 50)
    
    # Create generators
    regular_generator = AzulMoveGenerator()
    fast_generator = FastMoveGenerator()
    optimized_generator = OptimizedMoveGenerator()
    
    # Create test states
    test_states = create_test_states()
    
    print(f"\nTesting {len(test_states)} different game states...")
    print(f"Running 1000 iterations per test...")
    
    results = {}
    
    for state_name, state in enumerate(test_states):
        print(f"\n📊 {state_name} State:")
        print("-" * 30)
        
        # Benchmark regular generator
        regular_results = benchmark_generator(regular_generator, state, 0)
        print(f"Regular Generator:")
        print(f"  Mean: {regular_results['mean']:.2f}µs")
        print(f"  Median: {regular_results['median']:.2f}µs")
        print(f"  Min: {regular_results['min']:.2f}µs")
        print(f"  Max: {regular_results['max']:.2f}µs")
        print(f"  Std: {regular_results['std']:.2f}µs")
        print(f"  Moves: {regular_results['num_moves']}")
        
        # Benchmark fast generator
        fast_results = benchmark_generator(fast_generator, state, 0)
        print(f"Fast Generator:")
        print(f"  Mean: {fast_results['mean']:.2f}µs")
        print(f"  Median: {fast_results['median']:.2f}µs")
        print(f"  Min: {fast_results['min']:.2f}µs")
        print(f"  Max: {fast_results['max']:.2f}µs")
        print(f"  Std: {fast_results['std']:.2f}µs")
        print(f"  Moves: {fast_results['num_moves']}")
        
        # Benchmark optimized generator
        optimized_results = benchmark_generator(optimized_generator, state, 0)
        print(f"Optimized Generator:")
        print(f"  Mean: {optimized_results['mean']:.2f}µs")
        print(f"  Median: {optimized_results['median']:.2f}µs")
        print(f"  Min: {optimized_results['min']:.2f}µs")
        print(f"  Max: {optimized_results['max']:.2f}µs")
        print(f"  Std: {optimized_results['std']:.2f}µs")
        print(f"  Moves: {optimized_results['num_moves']}")
        
        # Calculate improvements
        fast_improvement = ((regular_results['mean'] - fast_results['mean']) / regular_results['mean']) * 100
        optimized_improvement = ((regular_results['mean'] - optimized_results['mean']) / regular_results['mean']) * 100
        print(f"  Fast improvement: {fast_improvement:.1f}%")
        print(f"  Optimized improvement: {optimized_improvement:.1f}%")
        
        results[state_name] = {
            'regular': regular_results,
            'fast': fast_results,
            'optimized': optimized_results,
            'fast_improvement': fast_improvement,
            'optimized_improvement': optimized_improvement
        }
    
    # Summary
    print(f"\n📈 Summary:")
    print("=" * 50)
    
    avg_fast_improvement = statistics.mean([r['fast_improvement'] for r in results.values()])
    avg_optimized_improvement = statistics.mean([r['optimized_improvement'] for r in results.values()])
    print(f"Average fast improvement: {avg_fast_improvement:.1f}%")
    print(f"Average optimized improvement: {avg_optimized_improvement:.1f}%")
    
    # Check performance targets
    target_met = True
    for state_name, result in results.items():
        if result['optimized']['mean'] > 50.0:  # Target
            print(f"❌ {state_name}: {result['optimized']['mean']:.2f}µs (target: ≤50µs)")
            target_met = False
        else:
            print(f"✅ {state_name}: {result['optimized']['mean']:.2f}µs (target: ≤50µs)")
    
    if target_met:
        print(f"\n🎉 All performance targets met!")
    else:
        print(f"\n⚠️  Some performance targets not met. Consider further optimization.")
    
    return results


if __name__ == "__main__":
    main() 