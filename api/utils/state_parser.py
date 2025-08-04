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
        else:
            # Try to load from dynamic position database
            try:
                from .position_loader import position_loader
                state = position_loader.create_position(fen_string)
                if state is not None:
                    print(f"DEBUG: Successfully loaded position '{fen_string}' from database")
                    return state
                else:
                    print(f"DEBUG: Position '{fen_string}' not found in database")
            except Exception as e:
                print(f"DEBUG: Error loading position '{fen_string}' from database: {e}")
            
            # Fallback to initial state if position not found
            print("DEBUG: Falling back to initial state")
            if _initial_game_state is None:
                random.seed(42)
                _initial_game_state = AzulState(2)
                random.seed()
            return _initial_game_state
            
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