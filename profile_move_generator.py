#!/usr/bin/env python3
"""
Profile script for A3 - Move Generator

This script uses cProfile to identify performance bottlenecks
in the move generator and provides detailed analysis.
"""

import cProfile
import pstats
import io
import time
from core.azul_move_generator import AzulMoveGenerator, FastMoveGenerator
from core.azul_model import AzulState
from core import azul_utils as utils


def create_profiling_states():
    """Create states for profiling."""
    states = []
    
    # Initial state (most complex)
    states.append(("Initial", AzulState(2)))
    
    # Mid-game state
    mid_state = AzulState(2)
    mid_state.agents[0].lines_number[0] = 1
    mid_state.agents[0].lines_tile[0] = utils.Tile.BLUE
    states.append(("Mid-game", mid_state))
    
    # Late-game state (simplest)
    late_state = AzulState(2)
    for i in range(3):
        late_state.agents[0].lines_number[i] = i + 1
        late_state.agents[0].lines_tile[i] = utils.Tile.BLUE
    states.append(("Late-game", late_state))
    
    return states


def profile_generator(generator, state, agent_id, num_runs=1000):
    """Profile a single generator on a single state."""
    pr = cProfile.Profile()
    pr.enable()
    
    # Run the generator multiple times
    for _ in range(num_runs):
        if hasattr(generator, 'generate_moves_fast'):
            moves = generator.generate_moves_fast(state, agent_id)
        else:
            moves = generator.generate_moves(state, agent_id)
    
    pr.disable()
    
    # Get stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    return s.getvalue(), len(moves)


def profile_specific_functions():
    """Profile specific functions to identify bottlenecks."""
    print("🔍 Profiling Specific Functions")
    print("=" * 50)
    
    state = AzulState(2)
    generator = AzulMoveGenerator()
    agent_state = state.agents[0]
    
    # Profile pattern line validation
    print("\n📊 Pattern Line Validation:")
    pr = cProfile.Profile()
    pr.enable()
    
    for _ in range(10000):
        for pattern_line in range(5):
            for tile_type in utils.Tile:
                generator._can_place_in_pattern_line(agent_state, pattern_line, tile_type)
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    print(s.getvalue())
    
    # Profile move creation
    print("\n📊 Move Creation:")
    pr = cProfile.Profile()
    pr.enable()
    
    for _ in range(1000):
        move = generator._generate_pattern_line_moves(
            agent_state, utils.Tile.BLUE, 4, 0, utils.Action.TAKE_FROM_FACTORY
        )
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    print(s.getvalue())


def main():
    """Run comprehensive profiling."""
    print("🎯 A3 - Move Generator Performance Profiling")
    print("=" * 50)
    
    # Create generators
    regular_generator = AzulMoveGenerator()
    fast_generator = FastMoveGenerator()
    
    # Create test states
    test_states = create_profiling_states()
    
    print(f"\nTesting {len(test_states)} different game states...")
    print(f"Running 1000 iterations per test...")
    
    for state_name, state in test_states:
        print(f"\n📊 {state_name} State:")
        print("-" * 30)
        
        # Profile regular generator
        print(f"Regular Generator:")
        regular_stats, regular_moves = profile_generator(regular_generator, state, 0)
        print(regular_stats)
        print(f"Moves generated: {regular_moves}")
        
        # Profile fast generator
        print(f"Fast Generator:")
        fast_stats, fast_moves = profile_generator(fast_generator, state, 0)
        print(fast_stats)
        print(f"Moves generated: {fast_moves}")
    
    # Profile specific functions
    profile_specific_functions()


if __name__ == "__main__":
    main() 