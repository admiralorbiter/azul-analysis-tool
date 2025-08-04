"""
State parsing utilities for the API.

This module contains functions for parsing FEN strings and converting
game states to and from FEN format.
"""

import random
import copy
import hashlib
import json
import time
from typing import Optional

# Global state variables (moved from routes.py)
_current_game_state = None
_initial_game_state = None
_current_editable_game_state = None


def parse_fen_string(fen_string: str):
    """Parse FEN string to create game state."""
    global _current_game_state, _initial_game_state, _current_editable_game_state
    from core.azul_model import AzulState
    
    print(f"DEBUG: parse_fen_string called with: {fen_string}")
    print(f"DEBUG: _initial_game_state is None: {_initial_game_state is None}")
    print(f"DEBUG: _current_game_state is None: {_current_game_state is None}")
    print(f"DEBUG: _current_editable_game_state is None: {_current_editable_game_state is None}")
    
    try:
        if fen_string.lower() in ["initial", "start"]:
            # Use a consistent initial state with fixed seed for reproducibility
            if _initial_game_state is None:
                print("DEBUG: Creating initial game state")
                # Set a fixed seed to ensure consistent initial state
                random.seed(42)
                _initial_game_state = AzulState(2)  # 2-player starting position
                print(f"DEBUG: Initial game state created: {_initial_game_state is not None}")
                # Reset seed to random
                random.seed()
                # Initialize current state from initial state
                print("DEBUG: About to create current game state from initial")
                _current_game_state = copy.deepcopy(_initial_game_state)
                print(f"DEBUG: Current game state created: {_current_game_state is not None}")
            
            # Always return the current game state (which starts as a copy of initial)
            print(f"DEBUG: Returning current game state: {_current_game_state is not None}")
            if _current_game_state is None:
                print("DEBUG: ERROR - _current_game_state is None!")
                return None
            return _current_game_state
        elif fen_string.startswith("state_"):
            # This is a state identifier - check if we have an editable game state
            if _current_editable_game_state is not None:
                print("DEBUG: Using editable game state for custom state identifier")
                # Convert the frontend state back to an AzulState object
                try:
                    from .state_converter import convert_frontend_state_to_azul_state
                    converted_state = convert_frontend_state_to_azul_state(_current_editable_game_state)
                    if converted_state is not None:
                        print("DEBUG: Successfully converted frontend state to AzulState. Setting as _current_game_state.")
                        _current_game_state = converted_state  # IMPORTANT: Update _current_game_state
                        return _current_game_state
                    else:
                        print("DEBUG: Failed to convert frontend state, falling back to current state")
                except Exception as e:
                    print(f"DEBUG: Error converting frontend state: {e}")
                
                # Fall back to current game state if conversion fails
                if _current_game_state is None:
                    # Fall back to initial state if no current state
                    if _initial_game_state is None:
                        random.seed(42)
                        _initial_game_state = AzulState(2)
                        random.seed()
                    _current_game_state = copy.deepcopy(_initial_game_state)
                return _current_game_state
            else:
                # No editable state, use current game state
                if _current_game_state is None:
                    # If we don't have a current state, create from initial state
                    if _initial_game_state is None:
                        print("DEBUG: Creating initial game state for state_ identifier")
                        random.seed(42)
                        _initial_game_state = AzulState(2)
                        random.seed()
                    _current_game_state = copy.deepcopy(_initial_game_state)
                return _current_game_state
        elif fen_string.lower() == "saved":
            # Handle 'saved' as equivalent to 'initial' for now
            # In the future, this could load from a saved state file
            print("DEBUG: Handling 'saved' FEN string as 'initial'")
            if _initial_game_state is None:
                print("DEBUG: Creating initial game state for saved")
                random.seed(42)
                _initial_game_state = AzulState(2)
                random.seed()
                _current_game_state = copy.deepcopy(_initial_game_state)
            return _current_game_state
        elif fen_string == "test_blocking_position":
            # Handle test blocking position - create a state with blocking opportunities
            print("DEBUG: Creating test blocking position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up a blocking scenario: Player 1 has blue tiles in pattern line 0
            # Player 0 (current player) can block by taking blue tiles
            test_state.agents[1].lines_tile[0] = 0  # Blue tiles in pattern line 0
            test_state.agents[1].lines_number[0] = 1  # 1 blue tile
            
            # Add blue tiles to factories for blocking
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add some blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "simple_blue_blocking":
            # Create simple blue blocking test position
            print("DEBUG: Creating simple blue blocking position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up simple blue blocking position
            # Player 2 has blue tiles in pattern line 0, needs 0 more tiles
            test_state.agents[1].lines_number[0] = 1  # 1 blue tile in line 0
            test_state.agents[1].lines_tile[0] = 0   # Blue color
            test_state.agents[1].grid_state[0][0] = 0  # Blue not on wall yet
            
            # Add blue tiles to factories
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            test_state.factories[2].tiles[0] = 1  # 1 blue tile in factory 2
            test_state.factories[3].tiles[0] = 1  # 1 blue tile in factory 3
            test_state.factories[4].tiles[0] = 1  # 1 blue tile in factory 4
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "high_urgency_red_blocking":
            # Create high urgency red blocking test position
            print("DEBUG: Creating high urgency red blocking position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up high urgency red blocking position
            # Player 2 has red tiles in pattern line 2, needs 1 more tile
            test_state.agents[1].lines_number[2] = 2  # 2 red tiles in line 2
            test_state.agents[1].lines_tile[2] = 2   # Red color
            test_state.agents[1].grid_state[2][2] = 0  # Red not on wall yet
            
            # Add red tiles to factories
            test_state.factories[0].tiles[2] = 1  # 1 red tile in factory 0
            test_state.factories[1].tiles[2] = 3  # 3 red tiles in factory 1
            test_state.factories[2].tiles[2] = 1  # 1 red tile in factory 2
            test_state.factories[3].tiles[2] = 1  # 1 red tile in factory 3
            test_state.factories[4].tiles[2] = 1  # 1 red tile in factory 4
            
            # Add red tiles to center pool
            test_state.centre_pool.tiles[2] = 2  # 2 red tiles in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "simple_row_completion":
            # Create simple row completion test position
            print("DEBUG: Creating simple row completion position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up simple row completion position
            # Player 0 has 4 tiles in row 0, needs 1 more to complete
            test_state.agents[0].grid_state[0][0] = 1  # Blue tile at (0,0)
            test_state.agents[0].grid_state[0][1] = 1  # Yellow tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Red tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Black tile at (0,3)
            # Missing white tile at (0,4) - this is the opportunity
            
            # Add white tiles to factories for completion
            test_state.factories[0].tiles[4] = 2  # 2 white tiles in factory 0
            test_state.factories[1].tiles[4] = 1  # 1 white tile in factory 1
            test_state.factories[2].tiles[4] = 1  # 1 white tile in factory 2
            
            # Add white tiles to center pool
            test_state.centre_pool.tiles[4] = 1  # 1 white tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "simple_column_completion":
            # Create simple column completion test position
            print("DEBUG: Creating simple column completion position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up simple column completion position
            # Player 0 has 4 tiles in column 0, needs 1 more to complete
            test_state.agents[0].grid_state[0][0] = 1  # Blue tile at (0,0)
            test_state.agents[0].grid_state[1][0] = 1  # Yellow tile at (1,0)
            test_state.agents[0].grid_state[2][0] = 1  # Red tile at (2,0)
            test_state.agents[0].grid_state[3][0] = 1  # Black tile at (3,0)
            # Missing white tile at (4,0) - this is the opportunity
            
            # Add white tiles to factories for completion
            test_state.factories[0].tiles[4] = 2  # 2 white tiles in factory 0
            test_state.factories[1].tiles[4] = 1  # 1 white tile in factory 1
            test_state.factories[2].tiles[4] = 1  # 1 white tile in factory 2
            
            # Add white tiles to center pool
            test_state.centre_pool.tiles[4] = 1  # 1 white tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "color_set_completion":
            # Create color set completion test position
            print("DEBUG: Creating color set completion position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up color set completion position (blue tiles)
            # Player 0 has 4 blue tiles, needs 1 more to complete set
            test_state.agents[0].grid_state[0][0] = 1  # Blue at (0,0)
            test_state.agents[0].grid_state[1][1] = 1  # Blue at (1,1)
            test_state.agents[0].grid_state[2][2] = 1  # Blue at (2,2)
            test_state.agents[0].grid_state[3][3] = 1  # Blue at (3,3)
            # Missing blue tile at (4,4) - this is the opportunity
            
            # Add blue tiles to factories for completion
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            test_state.factories[2].tiles[0] = 1  # 1 blue tile in factory 2
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "pattern_line_optimization":
            # Create pattern line optimization test position
            print("DEBUG: Creating pattern line optimization position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up pattern line optimization position
            # Player 0 has 2 tiles in pattern line 2 (capacity 3), needs 1 more
            test_state.agents[0].lines_number[2] = 2  # 2 tiles in line 2
            test_state.agents[0].lines_tile[2] = 0   # Blue color
            
            # Add blue tiles to factories for completion
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "floor_line_optimization":
            # Create floor line optimization test position
            print("DEBUG: Creating floor line optimization position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up floor line optimization position
            # Player 0 has 3 tiles in floor line (penalty -4)
            test_state.agents[0].floor_tiles = [0, 1, 2]  # 3 tiles in floor
            
            # Add tiles to factories for wall placement
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "multiplier_setup":
            # Create multiplier setup test position
            print("DEBUG: Creating multiplier setup position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up multiplier setup position
            # Player 0 has 4 tiles in row 0 and 4 tiles in column 0
            # Placing at (0,0) would complete both row and column
            test_state.agents[0].grid_state[0][1] = 1  # Tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Tile at (0,3)
            test_state.agents[0].grid_state[0][4] = 1  # Tile at (0,4)
            test_state.agents[0].grid_state[1][0] = 1  # Tile at (1,0)
            test_state.agents[0].grid_state[2][0] = 1  # Tile at (2,0)
            test_state.agents[0].grid_state[3][0] = 1  # Tile at (3,0)
            test_state.agents[0].grid_state[4][0] = 1  # Tile at (4,0)
            # Missing tile at (0,0) - this would complete both row and column
            
            # Add blue tiles to factories (blue goes at (0,0))
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        # Floor Line Management Test Positions
        elif fen_string == "critical_floor_risk":
            # Create critical floor risk test position
            print("DEBUG: Creating critical floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up critical floor risk position - Player 0 has 6 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2, 3, 4, 5]  # 6 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            test_state.factories[2].tiles[2] = 2  # 2 red tiles in factory 2
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            test_state.centre_pool.tiles[2] = 1  # 1 red tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "high_floor_risk":
            # Create high floor risk test position
            print("DEBUG: Creating high floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up high floor risk position - Player 0 has 4 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2, 3]  # 4 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            test_state.factories[2].tiles[2] = 2  # 2 red tiles in factory 2
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            test_state.centre_pool.tiles[2] = 1  # 1 red tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "moderate_floor_risk":
            # Create moderate floor risk test position
            print("DEBUG: Creating moderate floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up moderate floor risk position - Player 0 has 2 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1]  # 2 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "low_floor_risk":
            # Create low floor risk test position
            print("DEBUG: Creating low floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up low floor risk position - Player 0 has 1 tile on floor line
            test_state.agents[0].floor_tiles = [0]  # 1 tile on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "timing_optimization":
            # Create timing optimization test position
            print("DEBUG: Creating timing optimization position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up timing optimization position
            # Player 0 has 3 tiles in pattern line 1 (capacity 2), needs to place 1 tile
            test_state.agents[0].lines_number[1] = 1  # 1 tile in line 1
            test_state.agents[0].lines_tile[1] = 0   # Blue color
            
            # Add blue tiles to factories for completion
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "trade_offs":
            # Create trade-offs test position
            print("DEBUG: Creating trade-offs position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up trade-offs position
            # Player 0 has 2 tiles in pattern line 3 (capacity 4), needs 2 more
            # But also has 1 tile in pattern line 0 (capacity 1), needs 0 more
            test_state.agents[0].lines_number[3] = 2  # 2 tiles in line 3
            test_state.agents[0].lines_tile[3] = 0   # Blue color
            test_state.agents[0].lines_number[0] = 1  # 1 tile in line 0
            test_state.agents[0].lines_tile[0] = 1   # Yellow color
            
            # Add blue and yellow tiles to factories
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[0].tiles[1] = 2  # 2 yellow tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            test_state.factories[1].tiles[1] = 1  # 1 yellow tile in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "endgame_management":
            # Create endgame management test position
            print("DEBUG: Creating endgame management position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up endgame management position
            # Player 0 has 4 tiles in row 0 and 4 tiles in column 0
            # Placing at (0,0) would complete both row and column
            test_state.agents[0].grid_state[0][1] = 1  # Tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Tile at (0,3)
            test_state.agents[0].grid_state[0][4] = 1  # Tile at (0,4)
            test_state.agents[0].grid_state[1][0] = 1  # Tile at (1,0)
            test_state.agents[0].grid_state[2][0] = 1  # Tile at (2,0)
            test_state.agents[0].grid_state[3][0] = 1  # Tile at (3,0)
            test_state.agents[0].grid_state[4][0] = 1  # Tile at (4,0)
            # Missing tile at (0,0) - this would complete both row and column
            
            # Add blue tiles to factories (blue goes at (0,0))
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "efficiency_opportunities":
            # Create efficiency opportunities test position
            print("DEBUG: Creating efficiency opportunities position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up efficiency opportunities position
            # Player 0 has 2 tiles in pattern line 2 (capacity 3), needs 1 more
            test_state.agents[0].lines_number[2] = 2  # 2 tiles in line 2
            test_state.agents[0].lines_tile[2] = 0   # Blue color
            
            # Add blue tiles to factories for completion
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        else:
            # Unknown FEN string - raise ValueError
            print(f"DEBUG: Unknown FEN string: {fen_string}")
            raise ValueError(f"Unknown FEN string: {fen_string}")
            
    except Exception as e:
        print(f"DEBUG: Error parsing FEN string '{fen_string}': {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return None


def update_current_game_state(new_state):
    """Update the current game state."""
    global _current_game_state
    _current_game_state = new_state


def state_to_fen(state) -> str:
    """Convert game state to FEN string."""
    global _current_game_state
    
    # If this is the current game state, return a unique identifier
    if state is _current_game_state:
        # Generate a unique state identifier based on the state's content
        # This is a simple hash-based approach for now
        try:
            # Create a hash of the state's key components using JSON instead of pickle
            state_data = {
                'factories': [(i, dict(factory.tiles)) for i, factory in enumerate(state.factories)],
                'center': dict(state.centre_pool.tiles),
                'agents': [
                    {
                        'lines_tile': agent.lines_tile,
                        'lines_number': agent.lines_number,
                        'grid_state': agent.grid_state,
                        'floor_tiles': agent.floor_tiles,
                        'score': agent.score
                    }
                    for agent in state.agents
                ],
                'current_player': getattr(state, 'current_player', state.first_agent)
            }
            
            # Create a hash of the state data using JSON
            state_json = json.dumps(state_data, sort_keys=True)
            state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
            
            return f"state_{state_hash}"
        except Exception as e:
            # Fallback to a simple timestamp-based identifier if serialization fails
            timestamp = int(time.time() * 1000) % 1000000
            return f"state_{timestamp}"
    
    # For other states, return "initial" for backward compatibility
    return "initial" 