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
                        state.factories[i].tiles.update(tile_counts)
                    elif isinstance(factory, dict) and 'tiles' in factory:
                        # Old format: object with tiles
                        for tile_type_str, count in factory['tiles'].items():
                            tile_type = int(tile_type_str)
                            state.factories[i].tiles[tile_type] = count
        
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
                                                agent.grid_state[row][col] = -1
                    
                    # Convert floor tiles
                    if 'floor' in player:
                        floor_data = player['floor']
                        if isinstance(floor_data, list):
                            # Convert floor tile strings to tile types
                            floor_tiles = []
                            for tile in floor_data:
                                tile_type = convert_tile_string_to_type(tile)
                                floor_tiles.append(tile_type)
                            agent.floor_tiles = floor_tiles
        
        return state
        
    except Exception as e:
        return None


def convert_tile_string_to_type(tile_string):
    """Convert tile color string to tile type integer."""
    tile_mapping = {
        'blue': 0, 'B': 0, 'Blue': 0,
        'yellow': 1, 'Y': 1, 'Yellow': 1,
        'red': 2, 'R': 2, 'Red': 2,
        'black': 3, 'K': 3, 'Black': 3,
        'white': 4, 'W': 4, 'White': 4
    }
    
    result = tile_mapping.get(tile_string.lower(), -1)
    return result


def convert_json_to_azul_state(json_data):
    """Convert JSON game data to AzulState object."""
    try:
        from core.azul_model import AzulState
        
        # Create a new AzulState
        state = AzulState(2)  # 2-player game
        
        # Convert factories
        if 'factories' in json_data:
            for i, factory in enumerate(json_data['factories']):
                if i < len(state.factories):
                    # Clear existing tiles
                    state.factories[i].tiles.clear()
                    
                    # Add tiles from JSON format
                    if isinstance(factory, list):
                        # Array format: ["blue", "red", "yellow"]
                        tile_counts = {}
                        for tile in factory:
                            tile_type = convert_tile_string_to_type(tile)
                            tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
                        state.factories[i].tiles.update(tile_counts)
                    elif isinstance(factory, dict) and 'tiles' in factory:
                        # Object format: {"0": 2, "1": 1}
                        for tile_type_str, count in factory['tiles'].items():
                            tile_type = int(tile_type_str)
                            state.factories[i].tiles[tile_type] = count
        
        # Convert center pool
        if 'center' in json_data:
            state.centre_pool.tiles.clear()
            center_data = json_data['center']
            if isinstance(center_data, dict):
                # Dictionary format: {"0": 2, "1": 1}
                for tile_type_str, count in center_data.items():
                    tile_type = int(tile_type_str)
                    state.centre_pool.tiles[tile_type] = count
            elif isinstance(center_data, list):
                # List format: ["blue", "red", "yellow"]
                tile_counts = {}
                for tile in center_data:
                    tile_type = convert_tile_string_to_type(tile)
                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
                state.centre_pool.tiles.update(tile_counts)
        
        # Convert players/agents
        if 'players' in json_data:
            for i, player in enumerate(json_data['players']):
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
                                                agent.grid_state[row][col] = -1
                    
                    # Convert floor tiles
                    if 'floor' in player:
                        floor_data = player['floor']
                        if isinstance(floor_data, list):
                            # Convert floor tile strings to tile types
                            floor_tiles = []
                            for tile in floor_data:
                                tile_type = convert_tile_string_to_type(tile)
                                floor_tiles.append(tile_type)
                            agent.floor_tiles = floor_tiles
        
        return state
        
    except Exception as e:
        return None


def convert_azul_state_to_frontend(azul_state):
    """Convert AzulState object to frontend format."""
    try:
        frontend_state = {
            'factories': [],
            'center': {},
            'players': []
        }
        
        # Convert factories
        for factory in azul_state.factories:
            factory_tiles = []
            for tile_type, count in factory.tiles.items():
                tile_string = convert_tile_type_to_string(tile_type)
                factory_tiles.extend([tile_string] * count)
            frontend_state['factories'].append(factory_tiles)
        
        # Convert center pool
        for tile_type, count in azul_state.centre_pool.tiles.items():
            frontend_state['center'][str(tile_type)] = count
        
        # Convert players/agents
        for agent in azul_state.agents:
            player = {
                'pattern_lines': [],
                'wall': [],
                'floor': []
            }
            
            # Convert pattern lines
            for i in range(5):
                if agent.lines_tile[i] != -1:
                    tile_string = convert_tile_type_to_string(agent.lines_tile[i])
                    pattern_line = [tile_string] * agent.lines_number[i]
                    player['pattern_lines'].append(pattern_line)
                else:
                    player['pattern_lines'].append([])
            
            # Convert wall
            for row in range(5):
                wall_row = []
                for col in range(5):
                    if agent.grid_state[row][col] > 0:  # Only cells with actual tiles (value > 0)
                        tile_string = convert_tile_type_to_string(agent.grid_state[row][col])
                        wall_row.append(tile_string)
                    else:
                        wall_row.append(False)
                player['wall'].append(wall_row)
            
            # Convert floor tiles
            for tile_type in agent.floor_tiles:
                tile_string = convert_tile_type_to_string(tile_type)
                player['floor'].append(tile_string)
            
            frontend_state['players'].append(player)
        
        return frontend_state
        
    except Exception as e:
        return None


def convert_tile_type_to_string(tile_type):
    """Convert tile type integer to tile color string."""
    tile_mapping = {
        0: 'B',  # Blue
        1: 'Y',  # Yellow
        2: 'R',  # Red
        3: 'K',  # Black
        4: 'W'   # White
    }
    
    return tile_mapping.get(tile_type, 'unknown')


class StateConverter:
    """Utility class for state conversion operations."""
    
    @staticmethod
    def json_to_game_state(json_data):
        """Convert JSON data to game state."""
        return convert_json_to_azul_state(json_data)
    
    @staticmethod
    def game_state_to_json(azul_state):
        """Convert game state to JSON data."""
        return convert_azul_state_to_frontend(azul_state) 