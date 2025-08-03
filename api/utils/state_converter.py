"""
State conversion utilities for the API.

This module contains functions for converting between frontend and engine state formats.
"""

from typing import Dict, Any


def convert_frontend_state_to_azul_state(frontend_state):
    """Convert frontend game state to AzulState object."""
    try:
        from core.azul_model import AzulState
        
        # Create a new AzulState
        state = AzulState(2)  # 2-player game
        
        # Convert factories
        if 'factories' in frontend_state:
            print(f"DEBUG: Converting factories from frontend state: {frontend_state['factories']}")
            for i, factory in enumerate(frontend_state['factories']):
                if i < len(state.factories):
                    # Clear existing tiles
                    state.factories[i].tiles.clear()
                    
                    # Add tiles from frontend format
                    if isinstance(factory, list):
                        # New format: array of tile strings
                        tile_counts = {}
                        for tile in factory:
                            tile_type = convert_tile_string_to_type(tile)
                            tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
                            print(f"DEBUG: Converting tile '{tile}' to type {tile_type}")
                        state.factories[i].tiles.update(tile_counts)
                        print(f"DEBUG: Factory {i} converted from list format: {factory} -> {tile_counts}")
                        print(f"DEBUG: Factory {i} final state: {dict(state.factories[i].tiles)}")
                    elif isinstance(factory, dict) and 'tiles' in factory:
                        # Old format: object with tiles
                        for tile_type_str, count in factory['tiles'].items():
                            tile_type = int(tile_type_str)
                            state.factories[i].tiles[tile_type] = count
                        print(f"DEBUG: Factory {i} converted from dict format: {factory} -> {dict(state.factories[i].tiles)}")
                    else:
                        print(f"DEBUG: Factory {i} has unknown format: {factory}")
        
        # Convert center pool
        if 'center' in frontend_state:
            state.centre_pool.tiles.clear()
            center_data = frontend_state['center']
            if isinstance(center_data, dict):
                # Dictionary format: {"0": 2, "1": 1} (tile_type: count)
                for tile_type_str, count in center_data.items():
                    tile_type = int(tile_type_str)
                    state.centre_pool.tiles[tile_type] = count
            elif isinstance(center_data, list):
                # List format: ["B", "B", "Y"] (array of tile strings)
                tile_counts = {}
                for tile in center_data:
                    tile_type = convert_tile_string_to_type(tile)
                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
                state.centre_pool.tiles.update(tile_counts)
        
        # Convert players/agents
        if 'players' in frontend_state:
            for i, player in enumerate(frontend_state['players']):
                if i < len(state.agents):
                    agent = state.agents[i]
                    
                    # Convert pattern lines
                    if 'pattern_lines' in player:
                        for j, pattern_line in enumerate(player['pattern_lines']):
                            if j < len(agent.lines_tile):
                                if isinstance(pattern_line, list) and len(pattern_line) > 0:
                                    # Get tile type from first tile in pattern line
                                    tile_type = convert_tile_string_to_type(pattern_line[0])
                                    agent.lines_tile[j] = tile_type
                                    agent.lines_number[j] = len(pattern_line)
                                else:
                                    agent.lines_tile[j] = -1
                                    agent.lines_number[j] = 0
                    
                    # Convert wall
                    if 'wall' in player:
                        wall_data = player['wall']
                        if isinstance(wall_data, list) and len(wall_data) == 5:
                            for row in range(5):
                                if row < len(agent.grid_state) and len(wall_data[row]) == 5:
                                    for col in range(5):
                                        if col < len(agent.grid_state[row]):
                                            # wall_data[row][col] should be False (empty) or tile color string (has tile)
                                            if wall_data[row][col] and wall_data[row][col] is not False:
                                                # Convert tile color string to tile type
                                                tile_type = convert_tile_string_to_type(wall_data[row][col])
                                                agent.grid_state[row][col] = tile_type
                                            else:
                                                agent.grid_state[row][col] = 0  # Empty
                    
                    # Convert floor tiles
                    if 'floor_tiles' in player:
                        agent.floor_tiles = player['floor_tiles']
                    
                    # Convert score
                    if 'score' in player:
                        agent.score = player['score']
        
        print(f"DEBUG: State conversion completed successfully")
        print(f"DEBUG: Final factory contents:")
        for i, factory in enumerate(state.factories):
            print(f"  Factory {i}: {dict(factory.tiles)}")
        print(f"DEBUG: Final center pool: {dict(state.centre_pool.tiles)}")
        
        return state
        
    except Exception as e:
        print(f"DEBUG: Error converting frontend state: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return None


def convert_tile_string_to_type(tile_string):
    """Convert tile string (B, Y, R, K, W) to tile type integer."""
    tile_map = {
        'B': 0,  # Blue
        'Y': 1,  # Yellow
        'R': 2,  # Red
        'K': 3,  # Black
        'W': 4   # White
    }
    result = tile_map.get(tile_string.upper(), 0)
    print(f"DEBUG: convert_tile_string_to_type('{tile_string}') -> {result}")
    return result 