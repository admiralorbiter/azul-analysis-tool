"""
Test suite for backend center pool logic.
This ensures that the core game mechanics for center pool functionality
work correctly at the backend level.
"""

import pytest
import sys
import os

# Add the project root to the path so we can import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.azul_model import AzulState
from core.azul_model import AzulGameRule
# MoveGenerator doesn't exist, using game_rule.getLegalActions instead
from core.azul_utils import Tile, Action, TileGrab
from api.utils.state_converter import convert_azul_state_to_frontend


class TestBackendCenterPoolLogic:
    """Test backend center pool logic and game mechanics."""
    
    def setup_method(self):
        """Set up a fresh game state for each test."""
        self.state = AzulState(2)
        self.game_rule = AzulGameRule(2)
    
    def create_factory_move(self, factory_index, tile_type, num_to_pattern_line, num_to_floor_line, pattern_line_dest=0):
        """Helper method to create a factory move."""
        # Adjust pattern line capacity - line 0 can only hold 1 tile, line 1 can hold 2, etc.
        max_pattern_line_capacity = pattern_line_dest + 1
        if num_to_pattern_line > max_pattern_line_capacity:
            # Move excess tiles to floor line
            excess = num_to_pattern_line - max_pattern_line_capacity
            num_to_pattern_line = max_pattern_line_capacity
            num_to_floor_line += excess
        
        tile_grab = TileGrab()
        tile_grab.tile_type = tile_type
        tile_grab.number = num_to_pattern_line + num_to_floor_line
        tile_grab.pattern_line_dest = pattern_line_dest
        tile_grab.num_to_pattern_line = num_to_pattern_line
        tile_grab.num_to_floor_line = num_to_floor_line
        
        return (Action.TAKE_FROM_FACTORY, factory_index, tile_grab)
    
    def create_center_move(self, tile_type, num_to_pattern_line, num_to_floor_line, pattern_line_dest=0):
        """Helper method to create a center move."""
        # Adjust pattern line capacity - line 0 can only hold 1 tile, line 1 can hold 2, etc.
        max_pattern_line_capacity = pattern_line_dest + 1
        if num_to_pattern_line > max_pattern_line_capacity:
            # Move excess tiles to floor line
            excess = num_to_pattern_line - max_pattern_line_capacity
            num_to_pattern_line = max_pattern_line_capacity
            num_to_floor_line += excess
        
        tile_grab = TileGrab()
        tile_grab.tile_type = tile_type
        tile_grab.number = num_to_pattern_line + num_to_floor_line
        tile_grab.pattern_line_dest = pattern_line_dest
        tile_grab.num_to_pattern_line = num_to_pattern_line
        tile_grab.num_to_floor_line = num_to_floor_line
        
        return (Action.TAKE_FROM_CENTRE, -1, tile_grab)
    
    def test_initial_center_pool_state(self):
        """Test that initial center pool is empty."""
        assert self.state.centre_pool.total == 0, "Initial center pool should be empty"
        assert self.state.first_agent_taken is False, "Initial first player marker should be False"
    
    def test_factory_move_puts_remaining_tiles_in_center(self):
        """Test that taking tiles from factory puts remaining tiles in center."""
        # Find a factory with tiles
        factory_with_tiles = None
        factory_index = None
        
        for i, factory in enumerate(self.state.factories):
            if factory.total > 0:
                factory_with_tiles = factory
                factory_index = i
                break
        
        assert factory_with_tiles is not None, "Should have at least one factory with tiles"
        
        # Get the tile type and count
        tile_type = None
        tile_count = 0
        
        for tile_type_enum, count in factory_with_tiles.tiles.items():
            if count > 0:
                tile_type = tile_type_enum
                tile_count = count
                break
        
        assert tile_type is not None, "Should have at least one tile type"
        assert tile_count > 0, "Should have at least one tile"
        
        # Take some tiles, leaving some behind
        tiles_to_take = max(1, min(tile_count - 1, 2))  # Take at least 1 tile, leave at least 1 tile behind
        
        # Create a move
        move = self.create_factory_move(factory_index, tile_type, tiles_to_take, 0)
        
        # Execute the move
        new_state = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # Check that center pool now has the remaining tiles
        remaining_tiles = tile_count - tiles_to_take
        center_tiles_of_type = new_state.centre_pool.tiles.get(tile_type, 0)
        
        assert center_tiles_of_type == remaining_tiles, f"Center should have {remaining_tiles} tiles of type {tile_type}"
        assert new_state.first_agent_taken is False, "First player marker should still be False"
    
    def test_taking_from_center_sets_first_player_marker(self):
        """Test that taking from center pool sets the first player marker."""
        # First, put some tiles in the center by taking from a factory
        factory_with_tiles = None
        factory_index = None
        
        for i, factory in enumerate(self.state.factories):
            if factory.total > 0:
                factory_with_tiles = factory
                factory_index = i
                break
        
        # Get tile type
        tile_type = None
        for tile_type_enum, count in factory_with_tiles.tiles.items():
            if count > 0:
                tile_type = tile_type_enum
                break
        
        # Take some tiles from factory, leaving some in center
        move = self.create_factory_move(factory_index, tile_type, 1, 0)
        state_with_center = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # Verify center has tiles and first player marker is still False
        assert state_with_center.centre_pool.total > 0, "Center should have tiles"
        assert state_with_center.first_agent_taken is False, "First player marker should still be False"
        
        # Now take from center - this should set first player marker to True
        # Find what tiles are actually in the center pool
        center_tile_type = None
        for tile_type_enum, count in state_with_center.centre_pool.tiles.items():
            if count > 0:
                center_tile_type = tile_type_enum
                break
        
        assert center_tile_type is not None, "Center pool should have tiles"
        center_move = self.create_center_move(center_tile_type, 0, 1, -1)  # Put in floor line
        final_state = self.game_rule.generateSuccessor(state_with_center, center_move, 0)
        
        assert final_state.first_agent_taken is True, "First player marker should be True after taking from center"
    
    def test_center_pool_tile_removal(self):
        """Test that tiles are properly removed from center pool."""
        # Put tiles in center
        factory_with_tiles = None
        factory_index = None
        
        for i, factory in enumerate(self.state.factories):
            if factory.total > 0:
                factory_with_tiles = factory
                factory_index = i
                break
        
        tile_type = None
        for tile_type_enum, count in factory_with_tiles.tiles.items():
            if count > 0:
                tile_type = tile_type_enum
                break
        
        # Take tiles from factory to put in center
        move = self.create_factory_move(factory_index, tile_type, 1, 0)
        state_with_center = self.game_rule.generateSuccessor(self.state, move, 0)
        
        initial_center_count = state_with_center.centre_pool.total
        assert initial_center_count > 0, "Center should have tiles"
        
        # Take a tile from center
        # Find what tiles are actually in the center pool
        center_tile_type = None
        for tile_type_enum, count in state_with_center.centre_pool.tiles.items():
            if count > 0:
                center_tile_type = tile_type_enum
                break
        
        assert center_tile_type is not None, "Center pool should have tiles"
        center_move = self.create_center_move(center_tile_type, 0, 1, -1)  # Put in floor line
        final_state = self.game_rule.generateSuccessor(state_with_center, center_move, 0)
        
        # Check that center has one fewer tile
        final_center_count = final_state.centre_pool.total
        assert final_center_count == initial_center_count - 1, "Center should have one fewer tile"
    
    def test_center_pool_becomes_empty(self):
        """Test that center pool becomes empty after taking all tiles."""
        # Put tiles in center
        factory_with_tiles = None
        factory_index = None
        
        for i, factory in enumerate(self.state.factories):
            if factory.total > 0:
                factory_with_tiles = factory
                factory_index = i
                break
        
        tile_type = None
        for tile_type_enum, count in factory_with_tiles.tiles.items():
            if count > 0:
                tile_type = tile_type_enum
                break
        
        # Take tiles from factory to put in center
        move = self.create_factory_move(factory_index, tile_type, 1, 0)
        state_with_center = self.game_rule.generateSuccessor(self.state, move, 0)
        
                # Count total tiles in center pool
        total_center_tiles = state_with_center.centre_pool.total

        # Take all tiles from center
        current_state = state_with_center
        for i in range(total_center_tiles):
            # Find what tiles are actually in the center pool
            center_tile_type = None
            for tile_type_enum, count in current_state.centre_pool.tiles.items():
                if count > 0:
                    center_tile_type = tile_type_enum
                    break
            
            assert center_tile_type is not None, "Center pool should have tiles"
            center_move = self.create_center_move(center_tile_type, 0, 1, -1)  # Put in floor line
            current_state = self.game_rule.generateSuccessor(current_state, center_move, 0)
        
        # Verify center is now empty
        assert current_state.centre_pool.total == 0, "Center pool should be empty after taking all tiles"
    
    def test_center_pool_with_multiple_tile_types(self):
        """Test center pool with multiple different tile types."""
        # Take tiles from multiple factories to put different colors in center
        center_tiles = {}
        
        for i, factory in enumerate(self.state.factories[:2]):  # Use first 2 factories
            if factory.total > 0:
                tile_type = None
                for tile_type_enum, count in factory.tiles.items():
                    if count > 0:
                        tile_type = tile_type_enum
                        break
                
                if tile_type is not None:
                    # Put all tiles in floor line to avoid pattern line conflicts
                    move = self.create_factory_move(i, tile_type, 0, 1, -1)  # Put in floor line
                    self.state = self.game_rule.generateSuccessor(self.state, move, 0)
                    center_tiles[tile_type] = center_tiles.get(tile_type, 0) + 1
        
        # Verify center has multiple tile types
        assert len(center_tiles) > 0, "Center should have tiles"
        
                # Take all tiles from center pool
        while self.state.centre_pool.total > 0:
            # Find what tiles are actually in the center pool
            center_tile_type = None
            for tile_type_enum, count_in_center in self.state.centre_pool.tiles.items():
                if count_in_center > 0:
                    center_tile_type = tile_type_enum
                    break

            assert center_tile_type is not None, "Center pool should have tiles"
            center_move = self.create_center_move(center_tile_type, 0, 1, -1)  # Put in floor line
            self.state = self.game_rule.generateSuccessor(self.state, center_move, 0)
        
        # Verify center is empty and first player marker is True
        assert self.state.centre_pool.total == 0, "Center should be empty"
        assert self.state.first_agent_taken is True, "First player marker should be True"
    
    def test_center_pool_move_validation(self):
        """Test that center pool moves are properly validated."""
        # Try to take from empty center pool
        empty_center_move = self.create_center_move(Tile.BLUE, 1, 0, 0)
        
        # This should fail or be invalid
        legal_moves = self.game_rule.getLegalActions(self.state, 0)
        
        # Check that no center moves are legal when center is empty
        center_moves = [move for move in legal_moves if move[0] == 2]  # action_type == 2 for center
        assert len(center_moves) == 0, "Should not be able to take from empty center"
    
    def test_center_pool_with_remaining_factory_tiles(self):
        """Test that remaining factory tiles go to center after taking some tiles."""
        # Find a factory with multiple tiles of the same type
        factory_with_multiple_tiles = None
        factory_index = None
        tile_type = None
        
        for i, factory in enumerate(self.state.factories):
            for tile_type_enum, count in factory.tiles.items():
                if count > 1:  # Need multiple tiles of same type
                    factory_with_multiple_tiles = factory
                    factory_index = i
                    tile_type = tile_type_enum
                    break
            if factory_with_multiple_tiles is not None:
                break
        
        if factory_with_multiple_tiles is None:
            pytest.skip("No factory with multiple tiles of same type found")
        
        tile_count = factory_with_multiple_tiles.tiles[tile_type]
        tiles_to_take = tile_count - 1  # Leave 1 tile behind
        
        # Take some tiles from factory
        move = self.create_factory_move(factory_index, tile_type, tiles_to_take, 0)
        new_state = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # Check that the remaining tile is in center
        remaining_tiles = tile_count - tiles_to_take
        center_tiles_of_type = new_state.centre_pool.tiles.get(tile_type, 0)
        
        assert center_tiles_of_type == remaining_tiles, f"Center should have {remaining_tiles} tiles of type {tile_type}"
    
    def test_center_pool_state_consistency(self):
        """Test that center pool state is consistent across operations."""
        # Put tiles in center
        factory_with_tiles = None
        factory_index = None
        
        for i, factory in enumerate(self.state.factories):
            if factory.total > 0:
                factory_with_tiles = factory
                factory_index = i
                break
        
        tile_type = None
        for tile_type_enum, count in factory_with_tiles.tiles.items():
            if count > 0:
                tile_type = tile_type_enum
                break
        
        # Take tiles from factory
        move = self.create_factory_move(factory_index, tile_type, 1, 0)
        state_with_center = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # Verify center state is consistent
        center_total = state_with_center.centre_pool.total
        center_tiles_sum = sum(state_with_center.centre_pool.tiles.values())
        
        assert center_total == center_tiles_sum, "Center total should equal sum of individual tile counts"
        assert center_total > 0, "Center should have tiles"
    
    def test_first_player_marker_persistence(self):
        """Test that first player marker persists after taking from center."""
        # Put tiles in center
        factory_with_tiles = None
        factory_index = None
        
        for i, factory in enumerate(self.state.factories):
            if factory.total > 0:
                factory_with_tiles = factory
                factory_index = i
                break
        
        tile_type = None
        for tile_type_enum, count in factory_with_tiles.tiles.items():
            if count > 0:
                tile_type = tile_type_enum
                break
        
        # Take tiles from factory to put in center
        move = self.create_factory_move(factory_index, tile_type, 1, 0)
        state_with_center = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # Take from center multiple times
        current_state = state_with_center
        for i in range(3):  # Take 3 times
            if current_state.centre_pool.total > 0:
                # Find what tiles are actually in the center pool
                center_tile_type = None
                for tile_type_enum, count in current_state.centre_pool.tiles.items():
                    if count > 0:
                        center_tile_type = tile_type_enum
                        break
                
                assert center_tile_type is not None, "Center pool should have tiles"
                center_move = self.create_center_move(center_tile_type, 0, 1, -1)  # Put in floor line
                current_state = self.game_rule.generateSuccessor(current_state, center_move, 0)
                
                # First player marker should be True after first take from center
                if i == 0:
                    assert current_state.first_agent_taken is True, "First player marker should be True after first take from center"
                else:
                    assert current_state.first_agent_taken is True, "First player marker should remain True"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])


class TestDataFormatCompatibility:
    """Test that frontend can handle backend data formats correctly."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state = AzulState(2)
        self.game_rule = AzulGameRule(2)
    
    def test_center_pool_format_compatibility(self):
        """Test that frontend can handle both array and dictionary center pool formats."""
        # Test 1: Backend sends dictionary format (what actually happens)
        backend_state = AzulState(2)
        backend_state.centre_pool.tiles = {Tile.BLUE: 2, Tile.YELLOW: 1}
        
        # Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(backend_state)
        
        # Verify backend sends dictionary format
        assert isinstance(frontend_state['center'], dict), "Backend should send center as dictionary"
        assert frontend_state['center'] == {"0": 2, "1": 1}, "Center should be in dictionary format"
        
        # Test 2: Frontend should be able to handle this format
        center_data = frontend_state['center']
        
        # Simulate frontend conversion logic (like in CenterPool.js)
        def convert_center_to_array(center_dict):
            """Convert center dictionary to array for display."""
            if not center_dict:
                return []
            
            if isinstance(center_dict, list):
                return center_dict
            
            tiles_array = []
            color_map = {'0': 'B', '1': 'Y', '2': 'R', '3': 'K', '4': 'W'}
            
            for tile_type, count in center_dict.items():
                color = color_map.get(tile_type)
                if color and count > 0:
                    for _ in range(count):
                        tiles_array.append(color)
            
            return tiles_array
        
        # Test the conversion
        display_array = convert_center_to_array(center_data)
        assert display_array == ['B', 'B', 'Y'], "Should convert to display array correctly"
        assert len(display_array) == 3, "Should have correct number of tiles"
    
    def test_factory_move_to_center_data_flow(self):
        """Test the complete data flow from factory move to center display."""
        # 1. Set up factory with tiles
        factory_index = 0
        self.state.factories[factory_index].tiles = {Tile.BLUE: 2, Tile.YELLOW: 1, Tile.RED: 1}
        
        # 2. Execute factory move (take blue tiles)
        tile_grab = TileGrab()
        tile_grab.tile_type = Tile.BLUE
        tile_grab.number = 2
        tile_grab.pattern_line_dest = 0
        tile_grab.num_to_pattern_line = 1
        tile_grab.num_to_floor_line = 1
        
        move = (Action.TAKE_FROM_FACTORY, factory_index, tile_grab)
        new_state = self.game_rule.generateSuccessor(self.state, move, 0)
        
        # 3. Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(new_state)
        
        # 4. Verify backend logic worked
        assert new_state.centre_pool.tiles.get(Tile.YELLOW, 0) == 1, "Yellow tile should be in center"
        assert new_state.centre_pool.tiles.get(Tile.RED, 0) == 1, "Red tile should be in center"
        
        # 5. Verify frontend format
        assert isinstance(frontend_state['center'], dict), "Frontend should receive dictionary"
        assert frontend_state['center'].get('1', 0) == 1, "Yellow tile count should be 1"
        assert frontend_state['center'].get('2', 0) == 1, "Red tile count should be 1"
        
        # 6. Test frontend can render this
        center_data = frontend_state['center']
        display_array = self._convert_center_to_array(center_data)
        assert 'Y' in display_array, "Should display yellow tile"
        assert 'R' in display_array, "Should display red tile"
        assert len(display_array) == 2, "Should have 2 tiles in display"
    
    def test_empty_center_pool_handling(self):
        """Test that empty center pool is handled correctly."""
        # Backend empty center
        backend_state = AzulState(2)
        frontend_state = convert_azul_state_to_frontend(backend_state)
        
        # Test both formats
        center_data = frontend_state['center']
        
        # Dictionary format
        if isinstance(center_data, dict):
            display_array = self._convert_center_to_array(center_data)
            assert display_array == [], "Empty center should convert to empty array"
        
        # Array format (if backend ever sends this)
        elif isinstance(center_data, list):
            assert center_data == [], "Empty center should be empty array"
    
    def test_center_pool_with_first_player_marker(self):
        """Test center pool format when first player marker is present."""
        # Set up state with center tiles and first player marker
        backend_state = AzulState(2)
        backend_state.centre_pool.tiles = {Tile.BLUE: 1}
        backend_state.first_agent_taken = True
        backend_state.next_first_agent = 0
        
        frontend_state = convert_azul_state_to_frontend(backend_state)
        
        # Verify format
        assert isinstance(frontend_state['center'], dict), "Center should be dictionary"
        assert frontend_state['center'].get('0', 0) == 1, "Should have blue tile"
        # Note: first_player_taken is not included in convert_azul_state_to_frontend
        # It's handled separately in the API response
    
    def test_frontend_component_data_handling(self):
        """Test that frontend components can handle backend data formats."""
        # Simulate the data that frontend components receive
        mock_game_state = {
            'center': {"0": 2, "1": 1},  # Backend format
            'factories': [['B', 'B', 'Y'], []],  # Array format
            'first_player_taken': False
        }
        
        # Test CenterPool component logic
        def simulate_center_pool_logic(game_state):
            """Simulate the logic from CenterPool.js getTilesArray()."""
            center = game_state.get('center', [])
            
            if not center:
                return []
            
            if isinstance(center, list):
                return center
            
            # Handle dictionary format
            if isinstance(center, dict):
                tiles_array = []
                color_map = {'0': 'B', '1': 'Y', '2': 'R', '3': 'K', '4': 'W'}
                
                for tile_type, count in center.items():
                    color = color_map.get(tile_type)
                    if color and count > 0:
                        for _ in range(count):
                            tiles_array.append(color)
                
                return tiles_array
            
            return []
        
        # Test the logic
        display_tiles = simulate_center_pool_logic(mock_game_state)
        assert display_tiles == ['B', 'B', 'Y'], "Should convert dictionary to array"
        assert len(display_tiles) == 3, "Should have correct tile count"
    
    def test_use_analysis_hook_data_handling(self):
        """Test that useAnalysis hook can handle backend data formats."""
        # Simulate the data that useAnalysis hook receives
        mock_game_state = {
            'center': {"0": 2, "1": 1},
            'factories': [['B', 'B', 'Y'], []],
            'first_player_taken': False
        }
        
        # Test applyMoveLocally logic for center pool updates
        def simulate_apply_move_locally(game_state, factory_index, tile_color, num_to_pattern_line, num_to_floor_line):
            """Simulate the center pool update logic from applyMoveLocally."""
            new_state = game_state.copy()
            center_pool = new_state.get('center', {})
            
            # Handle center pool as dictionary format
            if isinstance(center_pool, dict):
                tile_type = self._get_tile_type(tile_color)
                tile_type_str = str(tile_type)
                current_count = center_pool.get(tile_type_str, 0)
                tiles_to_remove = num_to_pattern_line + num_to_floor_line
                new_count = max(0, current_count - tiles_to_remove)
                
                if new_count == 0:
                    center_pool.pop(tile_type_str, None)
                else:
                    center_pool[tile_type_str] = new_count
            else:
                # Handle array format
                tiles_to_remove = num_to_pattern_line + num_to_floor_line
                removed = 0
                for i in range(len(center_pool) - 1, -1, -1):
                    if center_pool[i] == tile_color and removed < tiles_to_remove:
                        center_pool.pop(i)
                        removed += 1
            
            return new_state
        
        # Test the logic
        updated_state = simulate_apply_move_locally(mock_game_state, 0, 'B', 1, 0)
        center_pool = updated_state['center']
        
        # Should have removed 1 blue tile (2-1=1)
        assert center_pool.get('0', 0) == 1, "Should have 1 blue tile remaining"
        assert center_pool.get('1', 0) == 1, "Should still have 1 yellow tile"
    
    def _convert_center_to_array(self, center_data):
        """Helper method to convert center data to array format."""
        if not center_data:
            return []
        
        if isinstance(center_data, list):
            return center_data
        
        tiles_array = []
        color_map = {'0': 'B', '1': 'Y', '2': 'R', '3': 'K', '4': 'W'}
        
        for tile_type, count in center_data.items():
            color = color_map.get(tile_type)
            if color and count > 0:
                for _ in range(count):
                    tiles_array.append(color)
        
        return tiles_array
    
    def _get_tile_type(self, tile_color):
        """Helper method to get tile type from color."""
        color_to_type = {'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4}
        return color_to_type.get(tile_color, 0)


class TestFrontendBackendContract:
    """Test the contract between frontend expectations and backend outputs."""
    
    def test_backend_center_pool_contract(self):
        """Test that backend always sends center pool in expected format."""
        state = AzulState(2)
        
        # Add some tiles to center
        state.centre_pool.tiles = {Tile.BLUE: 2, Tile.YELLOW: 1}
        
        # Convert to frontend format
        frontend_state = convert_azul_state_to_frontend(state)
        
        # Contract: Backend should always send center as dictionary
        assert isinstance(frontend_state['center'], dict), "Backend must send center as dictionary"
        
        # Contract: Dictionary keys should be strings
        for key in frontend_state['center'].keys():
            assert isinstance(key, str), "Center dictionary keys must be strings"
        
        # Contract: Dictionary values should be integers
        for value in frontend_state['center'].values():
            assert isinstance(value, int), "Center dictionary values must be integers"
    
    def test_frontend_center_pool_contract(self):
        """Test that frontend can handle the backend's center pool format."""
        # Simulate backend output
        backend_center = {"0": 2, "1": 1, "2": 0, "3": 1}
        
        # Frontend contract: Should be able to convert to display array
        def frontend_conversion_logic(center_dict):
            """Frontend must be able to convert backend format to display format."""
            if not isinstance(center_dict, dict):
                raise ValueError("Frontend expects center to be dictionary from backend")
            
            tiles_array = []
            color_map = {'0': 'B', '1': 'Y', '2': 'R', '3': 'K', '4': 'W'}
            
            for tile_type, count in center_dict.items():
                if not isinstance(tile_type, str):
                    raise ValueError("Frontend expects tile type keys to be strings")
                if not isinstance(count, int):
                    raise ValueError("Frontend expects tile counts to be integers")
                
                color = color_map.get(tile_type)
                if color and count > 0:
                    for _ in range(count):
                        tiles_array.append(color)
            
            return tiles_array
        
        # Test the contract
        display_array = frontend_conversion_logic(backend_center)
        assert display_array == ['B', 'B', 'Y', 'K'], "Should convert correctly"
        assert len(display_array) == 4, "Should have correct total tiles"
    
    def test_data_format_regression_prevention(self):
        """Test to prevent future data format regressions."""
        # This test documents the expected data formats
        expected_formats = {
            'center': 'dict',  # Backend sends dictionary
            'factories': 'list',  # Backend sends array of arrays
            'players': 'list'  # Backend sends array of player objects
        }
        
        # Test with actual backend conversion
        state = AzulState(2)
        frontend_state = convert_azul_state_to_frontend(state)
        
        # Verify each field has expected type
        for field, expected_type in expected_formats.items():
            assert field in frontend_state, f"Field '{field}' should exist"
            
            if expected_type == 'dict':
                assert isinstance(frontend_state[field], dict), f"'{field}' should be dictionary"
            elif expected_type == 'list':
                assert isinstance(frontend_state[field], list), f"'{field}' should be list" 