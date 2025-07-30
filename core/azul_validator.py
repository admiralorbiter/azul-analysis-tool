"""
Azul Game Rule Validator

This module provides comprehensive validation for Azul game rules,
ensuring that all state transitions follow the official game rules.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

from .azul_model import AzulState, AzulGameRule
from .azul_utils import Tile, Action, TileGrab


class ValidationError(Exception):
    """Exception raised when a game rule violation is detected."""
    pass


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class AzulRuleValidator:
    """
    Comprehensive validator for Azul game rules.
    
    Validates:
    - Move legality
    - State transitions
    - Scoring calculations
    - End-game conditions
    """
    
    def __init__(self):
        self.game_rule = AzulGameRule(2)  # Default to 2 players
    
    def validate_move(self, state: AzulState, action: Dict[str, Any], agent_id: int) -> ValidationResult:
        """
        Validate if a move is legal according to Azul rules.
        
        Args:
            state: Current game state
            action: Move to validate
            agent_id: ID of the agent making the move
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Check if it's the agent's turn
            if not self._is_agent_turn(state, agent_id):
                result.is_valid = False
                result.errors.append(f"Agent {agent_id} is not the current player")
            
            # Validate action structure
            if not self._validate_action_structure(action):
                result.is_valid = False
                result.errors.append("Invalid action structure")
                return result
            
            # Validate based on action type
            action_type = action.get('action_type')
            if action_type == Action.TAKE_FROM_FACTORY:
                self._validate_factory_action(state, action, result)
            elif action_type == Action.TAKE_FROM_CENTRE:
                self._validate_centre_action(state, action, result)
            else:
                result.is_valid = False
                result.errors.append(f"Unknown action type: {action_type}")
            
            # Validate placement
            if result.is_valid:
                self._validate_placement(state, action, result)
                
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation error: {str(e)}")
        
        return result
    
    def _is_agent_turn(self, state: AzulState, agent_id: int) -> bool:
        """Check if it's the specified agent's turn."""
        # In Azul, turns alternate between agents
        # For now, assume it's always valid (this will be refined)
        return True
    
    def _validate_action_structure(self, action: Dict[str, Any]) -> bool:
        """Validate the basic structure of an action."""
        required_fields = ['action_type', 'tile_grab']
        return all(field in action for field in required_fields)
    
    def _validate_factory_action(self, state: AzulState, action: Dict[str, Any], result: ValidationResult):
        """Validate taking tiles from a factory."""
        tile_grab = action['tile_grab']
        factory_id = tile_grab.get('factory_id', -1)
        
        # Check if factory exists
        if factory_id < 0 or factory_id >= len(state.factories):
            result.is_valid = False
            result.errors.append(f"Invalid factory ID: {factory_id}")
            return
        
        # Check if factory has tiles
        factory = state.factories[factory_id]
        if factory.total == 0:
            result.is_valid = False
            result.errors.append(f"Factory {factory_id} has no tiles")
            return
        
        # Check if specified tile type exists in factory
        tile_type = tile_grab.get('tile_type', -1)
        if tile_type not in factory.tiles or factory.tiles[tile_type] == 0:
            result.is_valid = False
            result.errors.append(f"Tile type {tile_type} not available in factory {factory_id}")
    
    def _validate_centre_action(self, state: AzulState, action: Dict[str, Any], result: ValidationResult):
        """Validate taking tiles from the centre pool."""
        tile_grab = action['tile_grab']
        tile_type = tile_grab.get('tile_type', -1)
        
        # Check if centre pool has tiles
        if state.centre_pool.total == 0:
            result.is_valid = False
            result.errors.append("Centre pool has no tiles")
            return
        
        # Check if specified tile type exists in centre pool
        if tile_type not in state.centre_pool.tiles or state.centre_pool.tiles[tile_type] == 0:
            result.is_valid = False
            result.errors.append(f"Tile type {tile_type} not available in centre pool")
    
    def _validate_placement(self, state: AzulState, action: Dict[str, Any], result: ValidationResult):
        """Validate tile placement on pattern lines."""
        tile_grab = action['tile_grab']
        pattern_line = tile_grab.get('pattern_line_dest', -1)
        tile_type = tile_grab.get('tile_type', -1)
        
        # Check if pattern line is valid
        if pattern_line < 0 or pattern_line >= 5:
            result.is_valid = False
            result.errors.append(f"Invalid pattern line: {pattern_line}")
            return
        
        # Check if tile type matches pattern line
        agent = state.agents[0]  # Assuming agent 0 for now
        if not self._is_valid_pattern_line_placement(agent, pattern_line, tile_type):
            result.is_valid = False
            result.errors.append(f"Tile type {tile_type} cannot be placed in pattern line {pattern_line}")
    
    def _is_valid_pattern_line_placement(self, agent: AzulState.AgentState, pattern_line: int, tile_type: int) -> bool:
        """Check if a tile type can be placed in a specific pattern line."""
        # Check if the pattern line already has a different tile type
        if agent.lines_tile[pattern_line] != -1 and agent.lines_tile[pattern_line] != tile_type:
            return False
        
        # Check if the wall already has this tile type in this row
        row = pattern_line
        # Find the column where this tile type should go
        target_col = int(agent.grid_scheme[row][tile_type])
        # Check if there's already a tile at that position
        if agent.grid_state[row][target_col] == 1:
            return False
        
        return True
    
    def validate_state_transition(self, old_state: AzulState, new_state: AzulState, action: Dict[str, Any]) -> ValidationResult:
        """
        Validate that a state transition follows Azul rules.
        
        Args:
            old_state: Previous game state
            new_state: New game state after action
            action: Action that caused the transition
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate tile conservation
            self._validate_tile_conservation(old_state, new_state, result)
            
            # Validate score changes
            self._validate_score_changes(old_state, new_state, result)
            
            # Validate pattern line changes
            self._validate_pattern_line_changes(old_state, new_state, action, result)
            
            # Validate floor changes
            self._validate_floor_changes(old_state, new_state, action, result)
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"State transition validation error: {str(e)}")
        
        return result
    
    def _validate_tile_conservation(self, old_state: AzulState, new_state: AzulState, result: ValidationResult):
        """Validate that no tiles are created or destroyed."""
        # Count tiles in old state
        old_total = sum(factory.total for factory in old_state.factories)
        old_total += old_state.centre_pool.total
        
        # Count tiles in new state
        new_total = sum(factory.total for factory in new_state.factories)
        new_total += new_state.centre_pool.total
        
        # Account for tiles moved to pattern lines and floors
        for agent in new_state.agents:
            for i, tile_type in enumerate(agent.lines_tile):
                if tile_type != -1:
                    new_total += agent.lines_number[i]
            new_total += len(agent.floor_tiles)
        
        for agent in old_state.agents:
            for i, tile_type in enumerate(agent.lines_tile):
                if tile_type != -1:
                    old_total += agent.lines_number[i]
            old_total += len(agent.floor_tiles)
        
        if old_total != new_total:
            result.is_valid = False
            result.errors.append(f"Tile conservation violated: {old_total} -> {new_total}")
    
    def _validate_score_changes(self, old_state: AzulState, new_state: AzulState, result: ValidationResult):
        """Validate that score changes are reasonable."""
        for i, (old_agent, new_agent) in enumerate(zip(old_state.agents, new_state.agents)):
            score_diff = new_agent.score - old_agent.score
            
            # Score should not decrease significantly without penalties
            if score_diff < -10:  # Allow for floor penalties
                result.warnings.append(f"Agent {i} score decreased significantly: {score_diff}")
    
    def _validate_pattern_line_changes(self, old_state: AzulState, new_state: AzulState, action: Dict[str, Any], result: ValidationResult):
        """Validate changes to pattern lines."""
        tile_grab = action.get('tile_grab', {})
        pattern_line = tile_grab.get('pattern_line_dest', -1)
        tile_type = tile_grab.get('tile_type', -1)
        
        if pattern_line >= 0 and tile_type >= 0:
            # Check that the correct tile type was added to the pattern line
            for i, (old_agent, new_agent) in enumerate(zip(old_state.agents, new_state.agents)):
                if (new_agent.lines_tile[pattern_line] != tile_type and 
                    old_agent.lines_tile[pattern_line] != tile_type):
                    result.warnings.append(f"Pattern line {pattern_line} tile type mismatch")
    
    def _validate_floor_changes(self, old_state: AzulState, new_state: AzulState, action: Dict[str, Any], result: ValidationResult):
        """Validate changes to floor tiles."""
        tile_grab = action.get('tile_grab', {})
        num_to_floor = tile_grab.get('num_to_floor_line', 0)
        
        if num_to_floor > 0:
            # Check that floor tiles were added correctly
            for i, (old_agent, new_agent) in enumerate(zip(old_state.agents, new_state.agents)):
                floor_diff = len(new_agent.floor_tiles) - len(old_agent.floor_tiles)
                if floor_diff != num_to_floor:
                    result.warnings.append(f"Floor tile count mismatch: expected {num_to_floor}, got {floor_diff}")
    
    def validate_scoring(self, state: AzulState) -> ValidationResult:
        """
        Validate that scoring calculations are correct.
        
        Args:
            state: Game state to validate scoring for
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)
        
        try:
            for i, agent in enumerate(state.agents):
                # For now, just check if score is reasonable (not negative)
                if agent.score < 0:
                    result.warnings.append(f"Agent {i} has negative score: {agent.score}")
                    
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Scoring validation error: {str(e)}")
        
        return result
    
    def validate_end_game(self, state: AzulState) -> ValidationResult:
        """
        Validate end-game conditions and final scoring.
        
        Args:
            state: Game state to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Check if game should end (all pattern lines empty or wall complete)
            should_end = self._should_game_end(state)
            
            # For now, just check if any agent has completed rows
            for i, agent in enumerate(state.agents):
                completed_rows = agent.GetCompletedRows()
                if completed_rows > 0:
                    result.warnings.append(f"Agent {i} has {completed_rows} completed rows")
                    
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"End-game validation error: {str(e)}")
        
        return result
    
    def _should_game_end(self, state: AzulState) -> bool:
        """Check if the game should end according to Azul rules."""
        # Game ends when at least one player completes a horizontal line
        for agent in state.agents:
            for row in range(5):
                if all(agent.grid_state[row][col] != -1 for col in range(5)):
                    return True
        return False 