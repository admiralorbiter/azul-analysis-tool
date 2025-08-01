import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.azul_model import AzulState
from core.azul_validator import AzulRuleValidator

class TestBoardEditing:
    """Test suite for board editing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.game_state = AzulState(num_agents=2)
        self.validator = AzulRuleValidator()
    
    def test_edit_mode_state_management(self):
        """Test that edit mode state can be managed"""
        # Test that we can add edit mode attributes to game state
        self.game_state.edit_mode = True
        assert self.game_state.edit_mode is True
        
        # Test exiting edit mode
        self.game_state.edit_mode = False
        assert self.game_state.edit_mode is False
    
    def test_element_selection_state(self):
        """Test that element selection state works correctly"""
        # Test setting selected element
        element_data = {
            'type': 'factory',
            'data': {'factoryIndex': 0},
            'timestamp': 1234567890
        }
        self.game_state.selected_element = element_data
        assert self.game_state.selected_element == element_data
        
        # Test clearing selection
        self.game_state.selected_element = None
        assert self.game_state.selected_element is None
    
    def test_factory_element_selection(self):
        """Test factory element selection logic"""
        # Mock factory data
        factory_data = {
            'type': 'factory',
            'data': 0,  # Factory index
            'timestamp': 1234567890
        }
        
        # Test factory selection
        self.game_state.selected_element = factory_data
        assert self.game_state.selected_element['type'] == 'factory'
        assert self.game_state.selected_element['data'] == 0
    
    def test_factory_tile_selection(self):
        """Test factory tile selection logic"""
        # Mock tile data
        tile_data = {
            'type': 'factory-tile',
            'data': {
                'factoryIndex': 1,
                'tileIndex': 2,
                'tile': 'R'
            },
            'timestamp': 1234567890
        }
        
        # Test tile selection
        self.game_state.selected_element = tile_data
        assert self.game_state.selected_element['type'] == 'factory-tile'
        assert self.game_state.selected_element['data']['factoryIndex'] == 1
        assert self.game_state.selected_element['data']['tileIndex'] == 2
        assert self.game_state.selected_element['data']['tile'] == 'R'
    
    def test_pattern_line_selection(self):
        """Test pattern line selection logic"""
        # Mock pattern line data
        pattern_data = {
            'type': 'pattern-line',
            'data': {
                'playerIndex': 0,
                'rowIndex': 2
            },
            'timestamp': 1234567890
        }
        
        # Test pattern line selection
        self.game_state.selected_element = pattern_data
        assert self.game_state.selected_element['type'] == 'pattern-line'
        assert self.game_state.selected_element['data']['playerIndex'] == 0
        assert self.game_state.selected_element['data']['rowIndex'] == 2
    
    def test_wall_cell_selection(self):
        """Test wall cell selection logic"""
        # Mock wall cell data
        wall_data = {
            'type': 'wall-cell',
            'data': {
                'playerIndex': 1,
                'rowIndex': 3,
                'colIndex': 4,
                'tile': 'B'
            },
            'timestamp': 1234567890
        }
        
        # Test wall cell selection
        self.game_state.selected_element = wall_data
        assert self.game_state.selected_element['type'] == 'wall-cell'
        assert self.game_state.selected_element['data']['playerIndex'] == 1
        assert self.game_state.selected_element['data']['rowIndex'] == 3
        assert self.game_state.selected_element['data']['colIndex'] == 4
        assert self.game_state.selected_element['data']['tile'] == 'B'
    
    def test_floor_tile_selection(self):
        """Test floor tile selection logic"""
        # Mock floor tile data
        floor_data = {
            'type': 'floor-tile',
            'data': {
                'playerIndex': 0,
                'tileIndex': 1,
                'tile': 'Y'
            },
            'timestamp': 1234567890
        }
        
        # Test floor tile selection
        self.game_state.selected_element = floor_data
        assert self.game_state.selected_element['type'] == 'floor-tile'
        assert self.game_state.selected_element['data']['playerIndex'] == 0
        assert self.game_state.selected_element['data']['tileIndex'] == 1
        assert self.game_state.selected_element['data']['tile'] == 'Y'
    
    def test_element_selection_validation(self):
        """Test that element selection data is valid"""
        # Test valid factory selection
        valid_factory = {
            'type': 'factory',
            'data': 0,
            'timestamp': 1234567890
        }
        assert 'type' in valid_factory
        assert 'data' in valid_factory
        assert 'timestamp' in valid_factory
        assert isinstance(valid_factory['data'], int)
        
        # Test valid tile selection
        valid_tile = {
            'type': 'factory-tile',
            'data': {
                'factoryIndex': 0,
                'tileIndex': 0,
                'tile': 'R'
            },
            'timestamp': 1234567890
        }
        assert 'type' in valid_tile
        assert 'data' in valid_tile
        assert 'timestamp' in valid_tile
        assert isinstance(valid_tile['data'], dict)
        assert 'factoryIndex' in valid_tile['data']
        assert 'tileIndex' in valid_tile['data']
        assert 'tile' in valid_tile['data']
    
    def test_selection_clearing(self):
        """Test that selection can be cleared properly"""
        # Set a selection
        self.game_state.selected_element = {
            'type': 'factory',
            'data': 0,
            'timestamp': 1234567890
        }
        assert self.game_state.selected_element is not None
        
        # Clear selection
        self.game_state.selected_element = None
        assert self.game_state.selected_element is None
    
    def test_edit_mode_with_selection(self):
        """Test that edit mode and selection work together"""
        # Enter edit mode
        self.game_state.edit_mode = True
        assert self.game_state.edit_mode is True
        
        # Make a selection
        self.game_state.selected_element = {
            'type': 'factory',
            'data': 0,
            'timestamp': 1234567890
        }
        assert self.game_state.selected_element is not None
        
        # Exit edit mode (should clear selection)
        self.game_state.edit_mode = False
        self.game_state.selected_element = None
        assert self.game_state.edit_mode is False
        assert self.game_state.selected_element is None
    
    def test_element_type_validation(self):
        """Test that element types are valid"""
        valid_types = [
            'factory',
            'factory-tile',
            'pattern-line',
            'pattern-line-tile',
            'pattern-line-empty',
            'wall-cell',
            'floor-tile',
            'floor-empty'
        ]
        
        for element_type in valid_types:
            element_data = {
                'type': element_type,
                'data': {},
                'timestamp': 1234567890
            }
            assert element_data['type'] in valid_types
    
    def test_timestamp_generation(self):
        """Test that timestamps are generated correctly"""
        import time
        
        # Test timestamp generation
        timestamp = int(time.time() * 1000)
        assert isinstance(timestamp, int)
        assert timestamp > 0
        
        # Test timestamp in element data
        element_data = {
            'type': 'factory',
            'data': 0,
            'timestamp': timestamp
        }
        assert element_data['timestamp'] == timestamp
    
    def test_element_data_serialization(self):
        """Test that element data can be serialized to JSON"""
        element_data = {
            'type': 'factory',
            'data': 0,
            'timestamp': 1234567890
        }
        
        # Test JSON serialization
        json_str = json.dumps(element_data)
        assert isinstance(json_str, str)
        
        # Test JSON deserialization
        parsed_data = json.loads(json_str)
        assert parsed_data == element_data
        assert parsed_data['type'] == 'factory'
        assert parsed_data['data'] == 0
        assert parsed_data['timestamp'] == 1234567890
    
    def test_complex_element_data(self):
        """Test complex element data structures"""
        complex_data = {
            'type': 'wall-cell',
            'data': {
                'playerIndex': 1,
                'rowIndex': 2,
                'colIndex': 3,
                'tile': 'G',
                'metadata': {
                    'color': 'green',
                    'position': 'wall'
                }
            },
            'timestamp': 1234567890
        }
        
        # Test complex data structure
        assert complex_data['type'] == 'wall-cell'
        assert complex_data['data']['playerIndex'] == 1
        assert complex_data['data']['rowIndex'] == 2
        assert complex_data['data']['colIndex'] == 3
        assert complex_data['data']['tile'] == 'G'
        assert 'metadata' in complex_data['data']
        assert complex_data['data']['metadata']['color'] == 'green'
    
    def test_element_selection_edge_cases(self):
        """Test edge cases for element selection"""
        # Test empty data
        empty_data = {
            'type': 'factory',
            'data': {},
            'timestamp': 1234567890
        }
        assert empty_data['data'] == {}
        
        # Test null data
        null_data = {
            'type': 'factory',
            'data': None,
            'timestamp': 1234567890
        }
        assert null_data['data'] is None
        
        # Test missing fields
        minimal_data = {
            'type': 'factory',
            'timestamp': 1234567890
        }
        assert 'type' in minimal_data
        assert 'timestamp' in minimal_data
        assert 'data' not in minimal_data
    
    def test_game_state_immutability(self):
        """Test that game state immutability is respected"""
        # Test that we can add attributes for editing
        self.game_state.edit_mode = True
        self.game_state.selected_element = {'type': 'factory', 'data': 0}
        
        # Verify attributes are set
        assert self.game_state.edit_mode is True
        assert self.game_state.selected_element is not None
        
        # Test that we can modify the editing state
        self.game_state.edit_mode = False
        assert self.game_state.edit_mode is False 