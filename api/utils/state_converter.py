"""
State conversion utilities for the API.

This module contains functions for converting between frontend and engine state formats.
"""

from typing import Dict, Any


def convert_frontend_state_to_azul_state(frontend_state):
    """Convert frontend game state to AzulState object."""
    try:
        from core.azul_model import AzulState
        
        print(f"DEBUG: Starting frontend state conversion")
        print(f"DEBUG: Frontend state keys: {list(frontend_state.keys())}")
        
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
            print(f"DEBUG: Converting center pool: {frontend_state['center']}")
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
                print(f"DEBUG: Center pool converted: {center_data} -> {tile_counts}")
            print(f"DEBUG: Final center pool state: {dict(state.centre_pool.tiles)}")
        
        # Convert players/agents
        if 'players' in frontend_state:
            print(f"DEBUG: Converting players: {len(frontend_state['players'])} players")
            for i, player in enumerate(frontend_state['players']):
                if i < len(state.agents):
                    agent = state.agents[i]
                    print(f"DEBUG: Converting player {i}: {list(player.keys())}")
                    
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
                    elif 'floor' in player:
                        # Convert floor tile strings to tile types
                        floor_tiles = []
                        for tile_string in player['floor']:
                            tile_type = convert_tile_string_to_type(tile_string)
                            floor_tiles.append(tile_type)
                        agent.floor_tiles = floor_tiles
                        print(f"DEBUG: Player {i} floor tiles converted: {player['floor']} -> {floor_tiles}")
                    
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


def convert_azul_state_to_frontend(azul_state):
    """Convert AzulState object to frontend format."""
    try:
        print(f"DEBUG: Starting azul state to frontend conversion")
        print(f"DEBUG: Azul state center pool: {dict(azul_state.centre_pool.tiles)}")
        
        frontend_state = {
            'factories': [],
            'center': [],
            'players': [],
            'first_player_taken': azul_state.first_agent_taken,
            'next_first_agent': azul_state.next_first_agent
        }
        
        # Convert factories
        for i, factory in enumerate(azul_state.factories):
            factory_tiles = []
            for tile_type, count in factory.tiles.items():
                for _ in range(count):
                    # Convert tile type to color string
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    factory_tiles.append(tile_colors.get(tile_type, 'W'))
            frontend_state['factories'].append(factory_tiles)
            print(f"DEBUG: Factory {i} converted: {dict(factory.tiles)} -> {factory_tiles}")
        
        # Convert center pool
        center_tiles = []
        for tile_type, count in azul_state.centre_pool.tiles.items():
            for _ in range(count):
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                center_tiles.append(tile_colors.get(tile_type, 'W'))
        frontend_state['center'] = center_tiles
        print(f"DEBUG: Center pool converted: {dict(azul_state.centre_pool.tiles)} -> {center_tiles}")
        
        # Convert player states
        for agent in azul_state.agents:
            player = {
                'pattern_lines': [],
                'wall': [],
                'floor': []
            }
            
            # Convert pattern lines
            for i in range(5):
                line = []
                if agent.lines_tile[i] != -1:
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    tile_color = tile_colors.get(agent.lines_tile[i], 'W')
                    for _ in range(agent.lines_number[i]):
                        line.append(tile_color)
                player['pattern_lines'].append(line)
            
            # Convert wall
            for row in range(5):
                wall_row = []
                for col in range(5):
                    if agent.grid_state[row][col] != 0:
                        tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                        tile_color = tile_colors.get(agent.grid_state[row][col], 'W')
                        wall_row.append(tile_color)
                    else:
                        wall_row.append(False)
                player['wall'].append(wall_row)
            
            # Convert floor
            floor_tiles = []
            
            # Process floor occupancy and tiles together
            floor_index = 0
            tiles_index = 0
            
            for i, floor_occupied in enumerate(agent.floor):
                if floor_occupied == 1:  # Position is occupied
                    if i == 0 and agent.floor[0] == 1 and len(agent.floor_tiles) == 0:
                        # This is likely the first player marker (first position, no tiles yet)
                        floor_tiles.append('FP')
                    elif tiles_index < len(agent.floor_tiles):
                        # Regular tile
                        tile_type = agent.floor_tiles[tiles_index]
                        tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                        floor_tiles.append(tile_colors.get(tile_type, 'W'))
                        tiles_index += 1
                    else:
                        # This is the first player marker (occupied but no tile in floor_tiles)
                        floor_tiles.append('FP')
            
            player['floor'] = floor_tiles
            
            frontend_state['players'].append(player)
        
        print(f"DEBUG: Final frontend state center: {frontend_state['center']}")
        print(f"DEBUG: Final frontend state factories: {frontend_state['factories']}")
        
        return frontend_state
        
    except Exception as e:
        print(f"DEBUG: Error converting azul state to frontend: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return None 