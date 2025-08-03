"""
Move conversion utilities for the API.

This module contains functions for converting moves between frontend and engine formats,
and finding matching moves in legal move lists.
"""

from typing import Dict, Any, List, Optional


def convert_frontend_move_to_engine(move_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert frontend move format to engine move format."""
    # Frontend format: {sourceId, tileType, patternLineDest, numToPatternLine, numToFloorLine}
    # Engine format: FastMove(action_type, source_id, tile_type, pattern_line_dest, num_to_pattern_line, num_to_floor_line)
    
    print(f"DEBUG: convert_frontend_move_to_engine called with: {move_data}")
    
    # Handle both snake_case and camelCase field names
    source_id = move_data.get('source_id', move_data.get('sourceId', 0))
    tile_type = move_data.get('tile_type', move_data.get('tileType', 0))
    pattern_line_dest = move_data.get('pattern_line_dest', move_data.get('patternLineDest', -1))
    num_to_pattern_line = move_data.get('num_to_pattern_line', move_data.get('numToPatternLine', 0))
    num_to_floor_line = move_data.get('num_to_floor_line', move_data.get('numToFloorLine', 0))
    
    print(f"DEBUG: Extracted values - source_id: {source_id}, tile_type: {tile_type} (type: {type(tile_type)}), pattern_line_dest: {pattern_line_dest}")
    
    # Handle string tile types from frontend
    if isinstance(tile_type, str):
        # Map string tile types to integers
        tile_color_map = {
            'B': 0,  # Blue
            'Y': 1,  # Yellow  
            'R': 2,  # Red
            'K': 3,  # Black
            'W': 4   # White
        }
        tile_type = tile_color_map.get(tile_type.upper(), 0)
        print(f"DEBUG: Converted string tile_type '{move_data.get('tile_type', move_data.get('tileType', 0))}' to {tile_type}")
    
    # Ensure tile_type is an integer (convert from enum if needed)
    if hasattr(tile_type, 'value'):
        tile_type = tile_type.value
        print(f"DEBUG: Converted enum tile_type to value: {tile_type}")
    tile_type = int(tile_type)
    print(f"DEBUG: Final tile_type: {tile_type}")
    
    # Determine action type based on source_id
    # Factory moves (source_id >= 0) are action_type 1, center moves (source_id < 0) are action_type 2
    action_type = 1 if source_id >= 0 else 2
    
    result = {
        'action_type': action_type,
        'source_id': source_id,
        'tile_type': tile_type,
        'pattern_line_dest': pattern_line_dest,
        'num_to_pattern_line': num_to_pattern_line,
        'num_to_floor_line': num_to_floor_line
    }
    
    print(f"DEBUG: Returning engine move: {result}")
    return result


def find_matching_move(engine_move: Dict[str, Any], legal_moves: List) -> Optional[object]:
    """Find matching move in legal moves list."""
    print(f"DEBUG: Looking for match with engine move: {engine_move}")
    print(f"DEBUG: Engine move type: {type(engine_move)}")
    print(f"DEBUG: Engine move keys: {engine_move.keys()}")
    print(f"DEBUG: Engine move tile_type: {engine_move.get('tile_type')} (type: {type(engine_move.get('tile_type'))})")
    
    for i, move in enumerate(legal_moves):
        print(f"DEBUG: Checking legal move {i}: action_type={move.action_type}, source_id={move.source_id}, tile_type={move.tile_type} (type: {type(move.tile_type)}), pattern_line_dest={move.pattern_line_dest}, num_to_pattern_line={move.num_to_pattern_line}, num_to_floor_line={move.num_to_floor_line}")
        print(f"DEBUG: Move type: {type(move)}")
        
        # Check each field individually
        action_match = move.action_type == engine_move['action_type']
        source_match = move.source_id == engine_move['source_id']
        tile_match = move.tile_type == engine_move['tile_type']
        pattern_match = move.pattern_line_dest == engine_move['pattern_line_dest']
        num_pattern_match = move.num_to_pattern_line == engine_move['num_to_pattern_line']
        num_floor_match = move.num_to_floor_line == engine_move['num_to_floor_line']
        
        print(f"DEBUG: Matches - action: {action_match}, source: {source_match}, tile: {tile_match} (engine: {engine_move.get('tile_type')} vs legal: {move.tile_type}), pattern: {pattern_match}, num_pattern: {num_pattern_match}, num_floor: {num_floor_match}")
        
        if (action_match and source_match and tile_match and 
            pattern_match and num_pattern_match and num_floor_match):
            print(f"DEBUG: Found matching move at index {i}")
            return move
    
    print(f"DEBUG: No matching move found")
    return None


def get_engine_response(state, agent_id: int) -> Optional[Dict[str, Any]]:
    """Get engine response move for the given state."""
    try:
        from core.azul_mcts import AzulMCTS
        from .formatters import format_move
        
        mcts = AzulMCTS()
        result = mcts.search(state, agent_id, max_time=0.1, max_rollouts=50)
        
        if result and result.best_move:
            return {
                'move': format_move(result.best_move),
                'score': result.best_score,
                'search_time': result.search_time
            }
    except Exception as e:
        print(f"Engine response error: {e}")
    
    return None 