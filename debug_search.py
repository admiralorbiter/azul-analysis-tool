#!/usr/bin/env python3
"""
Debug script for alpha-beta search.
"""

from core.azul_search import AzulAlphaBetaSearch
from core.azul_model import AzulState
from core.azul_move_generator import FastMoveGenerator

def debug_search():
    """Debug the search functionality."""
    print("=== Debug Search ===")
    
    # Create initial state
    state = AzulState(2)
    print(f"Initial state created with {len(state.agents)} agents")
    
    # Check if factories have tiles
    print(f"Factories: {len(state.factories)}")
    for i, factory in enumerate(state.factories):
        print(f"  Factory {i}: {factory.tiles}")
    
    # Check center pool
    print(f"Center pool: {state.centre_pool.tiles}")
    
    # Generate moves
    move_generator = FastMoveGenerator()
    moves = move_generator.generate_moves_fast(state, 0)
    print(f"Generated {len(moves)} moves for agent 0")
    
    if moves:
        print("First few moves:")
        for i, move in enumerate(moves[:3]):
            print(f"  Move {i}: {move.to_dict()}")
    
    # Try search
    search_engine = AzulAlphaBetaSearch(max_depth=2, max_time=1.0)
    result = search_engine.search(state, 0, max_depth=2, max_time=1.0)
    
    print(f"Search result: {result}")
    print(f"Best move: {result.best_move}")
    print(f"Best score: {result.best_score}")
    print(f"Nodes searched: {result.nodes_searched}")
    print(f"Depth reached: {result.depth_reached}")

if __name__ == "__main__":
    debug_search() 