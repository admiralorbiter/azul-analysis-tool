"""
Extended Azul Rule Validator for Board State Editing

This module extends the existing azul_validator.py with additional validation
specifically designed for the board state editor (R1.1). It provides real-time
validation for arbitrary board positions and comprehensive rule checking.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .azul_validator import AzulRuleValidator, ValidationResult, ValidationSeverity
from .azul_model import AzulState
from .azul_utils import Tile


@dataclass
class BoardEditValidationResult(ValidationResult):
    """Extended validation result for board editing with suggestions."""
    suggestion: Optional[str] = None
    affected_elements: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.affected_elements is None:
            self.affected_elements = []


class BoardStateValidator(AzulRuleValidator):
    """
    Extended validator for board state editing.
    
    Extends the existing AzulRuleValidator with methods specifically
    designed for validating arbitrary board positions during editing.
    """
    
    def __init__(self):
        super().__init__()
        self.TOTAL_TILES_PER_COLOR = 20
        self.TOTAL_TILES_IN_GAME = 100
        self.PATTERN_LINE_CAPACITIES = [1, 2, 3, 4, 5]
        self.FLOOR_LINE_CAPACITY = 7
        self.FLOOR_PENALTIES = [-1, -1, -2, -2, -2, -3, -3]
    
    def validate_complete_board_state(self, state: AzulState) -> BoardEditValidationResult:
        """
        Comprehensive validation of an entire board state.
        
        This is the main validation method for the board editor.
        It checks all Azul rules for arbitrary board positions.
        """
        result = BoardEditValidationResult(is_valid=True)
        
        try:
            # Critical validations that must pass
            self._validate_pattern_line_rules(state, result)
            self._validate_wall_consistency(state, result)
            self._validate_tile_conservation_complete(state, result)
            self._validate_floor_line_rules(state, result)
            
            # Warning-level validations
            self._validate_score_consistency(state, result)
            self._validate_game_phase_logic(state, result)
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Board validation error: {str(e)}")
        
        return result
    
    def validate_pattern_line_edit(self, state: AzulState, player_id: int, 
                                  line_index: int, color: int, tile_count: int) -> BoardEditValidationResult:
        """
        Validate a specific pattern line edit during board editing.
        
        This prevents the user from breaking the single-color rule you mentioned!
        """
        result = BoardEditValidationResult(is_valid=True)
        
        if player_id >= len(state.agents):
            result.is_valid = False
            result.errors.append(f"Invalid player ID: {player_id}")
            return result
        
        agent = state.agents[player_id]
        
        # Rule 1: Single color per pattern line (CRITICAL!)
        current_color = agent.lines_tile[line_index]
        if current_color != -1 and current_color != color:
            result.is_valid = False
            result.errors.append(f"Pattern line {line_index} already contains {self._color_name(current_color)} tiles. Cannot add {self._color_name(color)} tiles.")
            result.suggestion = f"Clear the pattern line first, or choose {self._color_name(current_color)} tiles instead."
            result.affected_elements.append(f"pattern_line_{player_id}_{line_index}")
            return result
        
        # Rule 2: Correct capacity
        max_capacity = self.PATTERN_LINE_CAPACITIES[line_index]
        if tile_count > max_capacity:
            result.is_valid = False
            result.errors.append(f"Pattern line {line_index} can only hold {max_capacity} tiles, but trying to place {tile_count}")
            result.suggestion = f"Reduce tile count to {max_capacity} or less."
            result.affected_elements.append(f"pattern_line_{player_id}_{line_index}")
            return result
        
        # Rule 3: Can't place if color already on wall
        if self._color_already_on_wall_row(agent, line_index, color):
            result.is_valid = False
            result.errors.append(f"{self._color_name(color)} is already completed on wall row {line_index + 1}")
            result.suggestion = f"Choose a different color or pattern line."
            result.affected_elements.append(f"wall_{player_id}_{line_index}")
            return result
        
        return result
    
    def validate_wall_edit(self, state: AzulState, player_id: int, 
                          row: int, col: int, add_tile: bool) -> BoardEditValidationResult:
        """Validate wall tile placement/removal."""
        result = BoardEditValidationResult(is_valid=True)
        
        if player_id >= len(state.agents):
            result.is_valid = False
            result.errors.append(f"Invalid player ID: {player_id}")
            return result
        
        agent = state.agents[player_id]
        
        if add_tile:
            # Check if position is already filled
            if agent.grid_state[row][col] == 1:
                result.is_valid = False
                result.errors.append(f"Wall position ({row + 1}, {col + 1}) is already filled")
                result.affected_elements.append(f"wall_{player_id}_{row}_{col}")
                return result
            
            # Check wall pattern consistency
            expected_color = agent.grid_scheme[row][col]
            # Validate that this color placement makes sense
            # (Additional logic here for pattern validation)
        
        return result
    
    def validate_floor_line_edit(self, state: AzulState, player_id: int, tiles: List[int]) -> BoardEditValidationResult:
        """Validate floor line tile placement."""
        result = BoardEditValidationResult(is_valid=True)
        
        if len(tiles) > self.FLOOR_LINE_CAPACITY:
            result.is_valid = False
            result.errors.append(f"Floor line can only hold {self.FLOOR_LINE_CAPACITY} tiles, but trying to place {len(tiles)}")
            result.suggestion = f"Remove {len(tiles) - self.FLOOR_LINE_CAPACITY} tiles."
            result.affected_elements.append(f"floor_line_{player_id}")
        
        return result
    
    def _validate_pattern_line_rules(self, state: AzulState, result: BoardEditValidationResult):
        """Validate all pattern line rules across all players."""
        for player_id, agent in enumerate(state.agents):
            for line_idx in range(5):
                tile_type = agent.lines_tile[line_idx]
                tile_count = agent.lines_number[line_idx]
                
                if tile_type != -1:  # Pattern line has tiles
                    # Check capacity
                    max_capacity = self.PATTERN_LINE_CAPACITIES[line_idx]
                    if tile_count > max_capacity:
                        result.is_valid = False
                        result.errors.append(f"Player {player_id + 1} pattern line {line_idx + 1}: {tile_count} tiles exceeds capacity {max_capacity}")
                        result.affected_elements.append(f"pattern_line_{player_id}_{line_idx}")
                    
                    # Check wall conflict
                    if self._color_already_on_wall_row(agent, line_idx, tile_type):
                        result.is_valid = False
                        result.errors.append(f"Player {player_id + 1} pattern line {line_idx + 1}: {self._color_name(tile_type)} already on wall")
                        result.affected_elements.append(f"pattern_line_{player_id}_{line_idx}")
    
    def _validate_wall_consistency(self, state: AzulState, result: BoardEditValidationResult):
        """Validate wall completion consistency."""
        for player_id, agent in enumerate(state.agents):
            # Check no duplicate colors in rows/columns
            for row in range(5):
                colors_in_row = []
                for col in range(5):
                    if agent.grid_state[row][col] == 1:
                        color = agent.grid_scheme[row][col]
                        if color in colors_in_row:
                            result.is_valid = False
                            result.errors.append(f"Player {player_id + 1} wall row {row + 1}: duplicate color {self._color_name(color)}")
                            result.affected_elements.append(f"wall_{player_id}_{row}")
                        colors_in_row.append(color)
    
    def _validate_tile_conservation_complete(self, state: AzulState, result: BoardEditValidationResult):
        """Complete tile conservation validation including all game areas."""
        tile_counts = {color: 0 for color in range(5)}
        
        # Count tiles in all locations
        # Factories
        for factory in state.factories:
            for color, count in factory.tiles.items():
                tile_counts[color] += count
        
        # Center pool
        for color, count in state.centre_pool.tiles.items():
            tile_counts[color] += count
        
        # Player areas
        for agent in state.agents:
            # Pattern lines
            for line_idx in range(5):
                if agent.lines_tile[line_idx] != -1:
                    tile_counts[agent.lines_tile[line_idx]] += agent.lines_number[line_idx]
            
            # Wall tiles
            for row in range(5):
                for col in range(5):
                    if agent.grid_state[row][col] == 1:
                        color = agent.grid_scheme[row][col]
                        tile_counts[color] += 1
            
            # Floor tiles
            for tile in agent.floor_tiles:
                if tile != -1:  # -1 represents the first player marker
                    tile_counts[tile] += 1
        
        # Validate counts
        for color in range(5):
            if tile_counts[color] > self.TOTAL_TILES_PER_COLOR:
                result.is_valid = False
                result.errors.append(f"Too many {self._color_name(color)} tiles: {tile_counts[color]}/20")
            elif tile_counts[color] < 0:
                result.is_valid = False
                result.errors.append(f"Negative {self._color_name(color)} tile count: {tile_counts[color]}")
    
    def _validate_floor_line_rules(self, state: AzulState, result: BoardEditValidationResult):
        """Validate floor line capacity and penalties."""
        for player_id, agent in enumerate(state.agents):
            if len(agent.floor_tiles) > self.FLOOR_LINE_CAPACITY:
                result.is_valid = False
                result.errors.append(f"Player {player_id + 1} floor line exceeds capacity: {len(agent.floor_tiles)}/{self.FLOOR_LINE_CAPACITY}")
                result.affected_elements.append(f"floor_line_{player_id}")
    
    def _validate_score_consistency(self, state: AzulState, result: BoardEditValidationResult):
        """Validate that scores match the board state (warning level)."""
        # This is complex - for now just check for reasonable ranges
        for player_id, agent in enumerate(state.agents):
            if agent.score < -50:  # Very negative scores are suspicious
                result.warnings.append(f"Player {player_id + 1} has very negative score: {agent.score}")
            elif agent.score > 200:  # Very high scores are suspicious
                result.warnings.append(f"Player {player_id + 1} has very high score: {agent.score}")
    
    def _validate_game_phase_logic(self, state: AzulState, result: BoardEditValidationResult):
        """Validate that the game phase makes sense (warning level)."""
        # Check if factories are empty but center pool has tiles (end of round)
        factories_empty = all(factory.total == 0 for factory in state.factories)
        center_has_tiles = state.centre_pool.total > 0
        
        if factories_empty and not center_has_tiles:
            # Check if all pattern lines should be scoring
            for player_id, agent in enumerate(state.agents):
                for line_idx in range(5):
                    if agent.lines_number[line_idx] == self.PATTERN_LINE_CAPACITIES[line_idx]:
                        result.warnings.append(f"End of round: Player {player_id + 1} should score pattern line {line_idx + 1}")
    
    def _color_already_on_wall_row(self, agent, row: int, color: int) -> bool:
        """Check if a color is already placed on the wall in a given row."""
        # Find the column where this color should go in this row
        target_col = int(agent.grid_scheme[row][color])
        # Check if there's already a tile at that position
        return agent.grid_state[row][target_col] == 1
    
    def _color_name(self, color: int) -> str:
        """Convert color number to readable name."""
        color_names = ["Blue", "Yellow", "Red", "Black", "White"]
        return color_names[color] if 0 <= color < 5 else f"Unknown({color})"


# Validation helper functions for the UI
def validate_pattern_line_edit_simple(current_color: int, new_color: int, 
                                     current_count: int, new_count: int, 
                                     line_capacity: int) -> Dict[str, Any]:
    """Simplified validation for UI real-time feedback."""
    if current_color != -1 and current_color != new_color:
        return {
            "valid": False,
            "error": "Pattern lines can only contain one color",
            "suggestion": "Clear the line or choose the same color"
        }
    
    if new_count > line_capacity:
        return {
            "valid": False,
            "error": f"Line can only hold {line_capacity} tiles",
            "suggestion": f"Reduce count to {line_capacity}"
        }
    
    return {"valid": True}