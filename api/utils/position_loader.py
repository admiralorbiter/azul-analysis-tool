"""
Dynamic Position Loader for API
Loads positions from a shared database instead of hardcoding them
"""

import json
import os
from typing import Optional, Dict, Any
from core.azul_model import AzulState
import random

class PositionLoader:
    def __init__(self):
        self.positions_cache = {}
        self.positions_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'positions.json')
        self._load_positions()
    
    def _load_positions(self):
        """Load positions from the positions database"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    self.positions_cache = json.load(f)
                print(f"Loaded {len(self.positions_cache)} positions from database")
            else:
                print("No positions database found, using fallback positions")
                self._create_fallback_positions()
        except Exception as e:
            print(f"Error loading positions: {e}")
            self._create_fallback_positions()
    
    def _create_fallback_positions(self):
        """Create fallback positions for basic functionality"""
        self.positions_cache = {
            "simple_blue_blocking": {
                "description": "Simple blue blocking test position",
                "setup": {
                    "player_1_lines": {"0": {"color": 0, "count": 1}},
                    "factories": {"0": {"0": 2}, "1": {"0": 1}},
                    "center_pool": {"0": 1}
                }
            },
            "high_value_column_completion": {
                "description": "High value column completion test position",
                "setup": {
                    "player_0_wall": {"0,2": 1, "1,2": 1, "2,2": 1, "3,2": 1},
                    "factories": {"0": {"2": 2}, "1": {"2": 1}},
                    "center_pool": {"2": 1}
                }
            }
        }
    
    def create_position(self, fen_string: str) -> Optional[AzulState]:
        """Create a game state from a position identifier"""
        if fen_string not in self.positions_cache:
            print(f"Position '{fen_string}' not found in database")
            return None
        
        position_data = self.positions_cache[fen_string]
        print(f"Creating position: {position_data.get('description', fen_string)}")
        
        # Create base state
        random.seed(42)  # Use fixed seed for reproducibility
        state = AzulState(2)
        
        # Apply position setup
        setup = position_data.get('setup', {})
        
        # Set up player pattern lines
        for player_key, lines in setup.get('player_lines', {}).items():
            player_idx = int(player_key)
            for line_idx, line_data in lines.items():
                line_idx = int(line_idx)
                state.agents[player_idx].lines_number[line_idx] = line_data['count']
                state.agents[player_idx].lines_tile[line_idx] = line_data['color']
        
        # Set up wall tiles
        for player_key, wall_tiles in setup.get('player_wall', {}).items():
            player_idx = int(player_key)
            for pos_str, color in wall_tiles.items():
                row, col = map(int, pos_str.split(','))
                state.agents[player_idx].grid_state[row][col] = 1
        
        # Set up factories
        for factory_idx, tiles in setup.get('factories', {}).items():
            factory_idx = int(factory_idx)
            for color, count in tiles.items():
                color = int(color)
                state.factories[factory_idx].tiles[color] = count
        
        # Set up center pool
        for color, count in setup.get('center_pool', {}).items():
            color = int(color)
            state.centre_pool.tiles[color] = count
        
        random.seed()  # Reset seed
        return state
    
    def list_positions(self) -> Dict[str, str]:
        """List all available positions"""
        return {name: pos.get('description', name) for name, pos in self.positions_cache.items()}

# Global instance
position_loader = PositionLoader() 