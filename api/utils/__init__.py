"""
API Utilities Package

This package contains utility functions used by the API endpoints including
state parsing, move conversion, and formatting utilities.
"""

# Import all utilities for easy access
from .state_parser import (
    parse_fen_string,
    state_to_fen,
    update_current_game_state,
    _current_game_state,
    _initial_game_state,
    _current_editable_game_state
)

from .move_converter import (
    convert_frontend_move_to_engine,
    find_matching_move,
    get_engine_response
)

from .state_converter import (
    convert_frontend_state_to_azul_state,
    convert_tile_string_to_type,
    convert_azul_state_to_frontend
)

from .formatters import (
    format_move
)

from .performance import (
    get_process_resources,
    get_system_resources
)

# Export all utilities
__all__ = [
    # State parsing utilities
    'parse_fen_string',
    'state_to_fen', 
    'update_current_game_state',
    '_current_game_state',
    '_initial_game_state',
    '_current_editable_game_state',
    
    # Move conversion utilities
    'convert_frontend_move_to_engine',
    'find_matching_move',
    'get_engine_response',
    
    # State conversion utilities
    'convert_frontend_state_to_azul_state',
    'convert_tile_string_to_type',
    'convert_azul_state_to_frontend',
    
    # Formatting utilities
    'format_move',
    
    # Performance utilities
    'get_process_resources',
    'get_system_resources',
] 