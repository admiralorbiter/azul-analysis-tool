#!/usr/bin/env python3
"""
Simple test for alpha-beta search.
"""

from core.azul_search import AzulAlphaBetaSearch
from core.azul_model import AzulState
from core.azul_move_generator import FastMoveGenerator

def test_search():
    """Test the search step by step."""
    print("=== Simple Search Test ===")
    
    # Create state
    state = AzulState(2)
    print(f"State created with {len(state.agents)} agents")
    
    # Generate moves
    move_generator = FastMoveGenerator()
    moves = move_generator.generate_moves_fast(state, 0)
    print(f"Generated {len(moves)} moves")
    
    if moves:
        print(f"First move: {moves[0].to_dict()}")
        
        # Try to apply the first move
        search_engine = AzulAlphaBetaSearch()
        new_state = search_engine._apply_move(state, moves[0], 0)
        
        if new_state is not None:
            print("Move applied successfully")
            
            # Try a depth-1 search
            result = search_engine.search(state, 0, max_depth=1, max_time=1.0)
            print(f"Search result: {result}")
            print(f"Best move: {result.best_move}")
            print(f"Nodes searched: {result.nodes_searched}")
        else:
            print("Failed to apply move")
    else:
        print("No moves generated")

if __name__ == "__main__":
    test_search() 