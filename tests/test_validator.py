"""
Tests for the Azul Rule Validator.

This module tests the comprehensive rule validation system
to ensure all Azul game rules are properly enforced.
"""

import sys
from pathlib import Path
import pytest
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.azul_validator import AzulRuleValidator, ValidationResult, ValidationSeverity
from core.azul_model import AzulState, AzulGameRule
from core.azul_utils import Tile, Action


class TestValidationResult:
    """Test the ValidationResult dataclass."""
    
    def test_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.severity == ValidationSeverity.ERROR
    
    def test_initialization_with_errors(self):
        """Test ValidationResult with errors."""
        result = ValidationResult(is_valid=False, errors=["Test error"])
        assert result.is_valid is False
        assert result.errors == ["Test error"]
        assert result.warnings == []


class TestAzulRuleValidator:
    """Test the AzulRuleValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AzulRuleValidator()
        self.state = AzulState(2)
    
    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.game_rule is not None
        assert isinstance(self.validator.game_rule, AzulGameRule)
    
    def test_validate_action_structure_valid(self):
        """Test validation of valid action structure."""
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        assert self.validator._validate_action_structure(action) is True
    
    def test_validate_action_structure_invalid(self):
        """Test validation of invalid action structure."""
        action = {'action_type': Action.TAKE_FROM_FACTORY}  # Missing tile_grab
        assert self.validator._validate_action_structure(action) is False
    
    def test_validate_factory_action_valid(self):
        """Test validation of valid factory action."""
        # Set up factory with tiles
        self.state.factories[0].AddTiles(2, Tile.BLUE)
        
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_factory_action(self.state, action, result)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_factory_action_invalid_factory(self):
        """Test validation of action with invalid factory ID."""
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 10,  # Invalid factory ID
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_factory_action(self.state, action, result)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Invalid factory ID" in result.errors[0]
    
    def test_validate_factory_action_empty_factory(self):
        """Test validation of action on empty factory."""
        # Create a state with empty factories
        empty_state = AzulState(2)
        # Clear all factories
        for factory in empty_state.factories:
            factory.total = 0
            for tile in factory.tiles:
                factory.tiles[tile] = 0
        
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_factory_action(empty_state, action, result)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "has no tiles" in result.errors[0]
    
    def test_validate_factory_action_tile_not_available(self):
        """Test validation of action with unavailable tile type."""
        # Create a state and clear factory 0, then add only red tiles
        test_state = AzulState(2)
        test_state.factories[0].total = 0
        for tile in test_state.factories[0].tiles:
            test_state.factories[0].tiles[tile] = 0
        test_state.factories[0].AddTiles(2, Tile.RED)
        
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,  # Blue not available
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_factory_action(test_state, action, result)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "not available" in result.errors[0]
    
    def test_validate_centre_action_valid(self):
        """Test validation of valid centre action."""
        # Set up centre pool with tiles
        self.state.centre_pool.AddTiles(3, Tile.BLUE)
        
        action = {
            'action_type': Action.TAKE_FROM_CENTRE,
            'tile_grab': {
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_centre_action(self.state, action, result)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_centre_action_empty_pool(self):
        """Test validation of action on empty centre pool."""
        action = {
            'action_type': Action.TAKE_FROM_CENTRE,
            'tile_grab': {
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_centre_action(self.state, action, result)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "has no tiles" in result.errors[0]
    
    def test_validate_placement_valid(self):
        """Test validation of valid tile placement."""
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_placement(self.state, action, result)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_placement_invalid_pattern_line(self):
        """Test validation of placement with invalid pattern line."""
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 10,  # Invalid pattern line
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = ValidationResult(is_valid=True)
        self.validator._validate_placement(self.state, action, result)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Invalid pattern line" in result.errors[0]
    
    def test_is_valid_pattern_line_placement_valid(self):
        """Test valid pattern line placement."""
        agent = self.state.agents[0]
        # Pattern line 0 should accept blue tiles
        assert self.validator._is_valid_pattern_line_placement(agent, 0, Tile.BLUE) is True
    
    def test_is_valid_pattern_line_placement_wall_conflict(self):
        """Test pattern line placement with wall conflict."""
        agent = self.state.agents[0]
        # Place a blue tile in the wall at row 0, col 0 (where blue tiles go)
        agent.grid_state[0][0] = 1  # 1 indicates a tile is present
        
        # Pattern line 0 should not accept blue tiles now
        assert self.validator._is_valid_pattern_line_placement(agent, 0, Tile.BLUE) is False
    
    def test_is_valid_pattern_line_placement_different_tile_type(self):
        """Test pattern line placement with different tile type."""
        agent = self.state.agents[0]
        # Set pattern line 0 to have red tiles
        agent.lines_tile[0] = Tile.RED
        agent.lines_number[0] = 2
        
        # Pattern line 0 should not accept blue tiles now
        assert self.validator._is_valid_pattern_line_placement(agent, 0, Tile.BLUE) is False
    
    def test_validate_move_complete_valid(self):
        """Test complete move validation with valid move."""
        # Set up factory with tiles
        self.state.factories[0].AddTiles(2, Tile.BLUE)
        
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = self.validator.validate_move(self.state, action, 0)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_move_invalid_action_type(self):
        """Test move validation with invalid action type."""
        action = {
            'action_type': 999,  # Invalid action type
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = self.validator.validate_move(self.state, action, 0)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Unknown action type" in result.errors[0]
    
    def test_validate_state_transition_tile_conservation(self):
        """Test state transition validation with tile conservation."""
        old_state = AzulState(2)
        new_state = AzulState(2)
        
        # Add tiles to old state
        old_state.factories[0].AddTiles(2, Tile.BLUE)
        old_state.centre_pool.AddTiles(1, Tile.RED)
        
        # Add tiles to new state (simulating a move)
        new_state.factories[0].AddTiles(1, Tile.BLUE)  # One tile taken
        new_state.centre_pool.AddTiles(1, Tile.RED)
        new_state.agents[0].lines_tile[0] = Tile.BLUE
        new_state.agents[0].lines_number[0] = 1  # One tile placed
        
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 1,
                'num_to_floor_line': 0
            }
        }
        
        result = self.validator.validate_state_transition(old_state, new_state, action)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_state_transition_tile_conservation_violation(self):
        """Test state transition validation with tile conservation violation."""
        old_state = AzulState(2)
        new_state = AzulState(2)
        
        # Add tiles to old state
        old_state.factories[0].AddTiles(2, Tile.BLUE)
        
        # Don't add tiles to new state (simulating tile loss)
        
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        result = self.validator.validate_state_transition(old_state, new_state, action)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Tile conservation violated" in result.errors[0]
    
    def test_validate_scoring_valid(self):
        """Test scoring validation with valid scores."""
        # Set up agent with some completed tiles
        agent = self.state.agents[0]
        agent.grid_state[0][0] = Tile.BLUE  # Complete first tile
        agent.score = 1  # Set a valid score
        
        result = self.validator.validate_scoring(self.state)
        # This should pass as the score calculation is reasonable
        assert result.is_valid is True
    
    def test_validate_end_game_not_ended(self):
        """Test end game validation when game should not end."""
        result = self.validator.validate_end_game(self.state)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_end_game_should_end(self):
        """Test end game validation when game should end."""
        # Complete a horizontal line
        agent = self.state.agents[0]
        for col in range(5):
            agent.grid_state[0][col] = Tile.BLUE
        
        result = self.validator.validate_end_game(self.state)
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestValidationEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AzulRuleValidator()
        self.state = AzulState(2)
    
    def test_validate_move_exception_handling(self):
        """Test that exceptions in move validation are caught."""
        # Create an action that will cause an exception
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': None  # This will cause an exception
        }
        
        result = self.validator.validate_move(self.state, action, 0)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Validation error" in result.errors[0]
    
    def test_validate_state_transition_exception_handling(self):
        """Test that exceptions in state transition validation are caught."""
        old_state = AzulState(2)
        new_state = AzulState(2)
        action = {}
        
        # This should not raise an exception
        result = self.validator.validate_state_transition(old_state, new_state, action)
        assert isinstance(result, ValidationResult)
    
    def test_validate_scoring_exception_handling(self):
        """Test that exceptions in scoring validation are caught."""
        # Create a state that might cause scoring calculation issues
        self.state.agents[0].score = -999  # Unrealistic score
        
        result = self.validator.validate_scoring(self.state)
        assert isinstance(result, ValidationResult)
    
    def test_validate_end_game_exception_handling(self):
        """Test that exceptions in end game validation are caught."""
        # This should not raise an exception
        result = self.validator.validate_end_game(self.state)
        assert isinstance(result, ValidationResult)


class TestValidationIntegration:
    """Test integration scenarios with multiple validation checks."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AzulRuleValidator()
        self.state = AzulState(2)
    
    def test_complete_game_validation_flow(self):
        """Test a complete game validation flow."""
        # Set up initial state with a specific factory configuration
        test_state = AzulState(2)
        # Clear factory 0 and add only blue tiles
        test_state.factories[0].total = 0
        for tile in test_state.factories[0].tiles:
            test_state.factories[0].tiles[tile] = 0
        test_state.factories[0].AddTiles(2, Tile.BLUE)
        
        # Create a valid move
        action = {
            'action_type': Action.TAKE_FROM_FACTORY,
            'tile_grab': {
                'factory_id': 0,
                'tile_type': Tile.BLUE,
                'pattern_line_dest': 0,
                'num_to_pattern_line': 2,
                'num_to_floor_line': 0
            }
        }
        
        # Validate the move
        move_result = self.validator.validate_move(test_state, action, 0)
        assert move_result.is_valid is True
        
        # Create a new state (simulating the move)
        new_state = AzulState(2)
        # Clear factory 0 and add remaining tiles
        new_state.factories[0].total = 0
        for tile in new_state.factories[0].tiles:
            new_state.factories[0].tiles[tile] = 0
        # No tiles remaining in factory
        new_state.agents[0].lines_tile[0] = Tile.BLUE
        new_state.agents[0].lines_number[0] = 2
        
        # Validate the state transition
        transition_result = self.validator.validate_state_transition(test_state, new_state, action)
        assert transition_result.is_valid is True
        
        # Validate scoring
        scoring_result = self.validator.validate_scoring(new_state)
        assert scoring_result.is_valid is True
        
        # Validate end game
        end_game_result = self.validator.validate_end_game(new_state)
        assert end_game_result.is_valid is True 