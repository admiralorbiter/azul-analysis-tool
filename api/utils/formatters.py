"""
Formatting utilities for the API.

This module contains functions for formatting moves and other data for display.
"""


def format_move(move):
    """Format a move for display."""
    if move is None:
        return "None"
    
    try:
        # Convert tile type to color name
        tile_colors = {0: 'blue', 1: 'yellow', 2: 'red', 3: 'black', 4: 'white'}
        tile_color = tile_colors.get(move.tile_type, f'tile_{move.tile_type}')
        
        # Format as string for tests
        if move.action_type == 1:  # Factory move
            return f"take_from_factory_{move.source_id}_{tile_color}_{move.pattern_line_dest}_{move.num_to_pattern_line}_{move.num_to_floor_line}"
        else:  # Center move
            return f"take_from_center_{move.source_id}_{tile_color}_{move.pattern_line_dest}_{move.num_to_pattern_line}_{move.num_to_floor_line}"
    except Exception as e:
        # Fallback if move formatting fails
        return f"move_{getattr(move, 'source_id', '?')}_{getattr(move, 'tile_type', '?')}" 