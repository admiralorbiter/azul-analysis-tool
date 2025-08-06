"""
Azul Move Parser

This module provides parsing functionality for Azul move strings,
converting them into structured data for move quality assessment.

Move format examples:
- "factory_0_tile_blue_pattern_line_1" - Take blue tile from factory 0 to pattern line 1
- "factory_2_tile_red_floor" - Take red tile from factory 2 to floor
- "factory_1_tile_yellow_wall_2_3" - Take yellow tile from factory 1 to wall position (2,3)
"""

import re
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum
from core import azul_utils as utils


class MoveType(Enum):
    """Types of moves in Azul."""
    FACTORY_TO_PATTERN_LINE = "factory_to_pattern_line"
    FACTORY_TO_FLOOR = "factory_to_floor"
    FACTORY_TO_WALL = "factory_to_wall"
    PASS = "pass"


@dataclass
class ParsedMove:
    """Structured representation of a parsed move."""
    move_type: MoveType
    factory_id: Optional[int]
    tile_color: Optional[int]
    target_type: str  # "pattern_line", "floor", "wall"
    target_position: Optional[Tuple[int, int]]  # For wall placements
    pattern_line_id: Optional[int]  # For pattern line placements
    original_string: str
    is_valid: bool
    validation_errors: List[str]


class AzulMoveParser:
    """
    Parser for Azul move strings.
    
    Converts move strings like "factory_0_tile_blue_pattern_line_1"
    into structured ParsedMove objects for analysis.
    """
    
    def __init__(self):
        # Color mapping
        self.color_map = {
            'blue': utils.Tile.BLUE,
            'yellow': utils.Tile.YELLOW,
            'red': utils.Tile.RED,
            'black': utils.Tile.BLACK,
            'white': utils.Tile.WHITE
        }
        
        # Reverse color mapping for validation
        self.reverse_color_map = {v: k for k, v in self.color_map.items()}
        
        # Move patterns
        self.move_patterns = {
            # factory_0_tile_blue_pattern_line_1
            'factory_to_pattern_line': re.compile(
                r'factory_(\d+)_tile_(\w+)_pattern_line_(\d+)'
            ),
            # factory_2_tile_red_floor
            'factory_to_floor': re.compile(
                r'factory_(\d+)_tile_(\w+)_floor'
            ),
            # factory_1_tile_yellow_wall_2_3
            'factory_to_wall': re.compile(
                r'factory_(\d+)_tile_(\w+)_wall_(\d+)_(\d+)'
            ),
            # pass
            'pass': re.compile(r'pass')
        }
    
    def parse_move(self, move_key: str) -> ParsedMove:
        """
        Parse a move key string into a structured ParsedMove object.
        
        Args:
            move_key: String representation of the move
            
        Returns:
            ParsedMove with structured move data
        """
        # Try to match each pattern
        for move_type, pattern in self.move_patterns.items():
            match = pattern.match(move_key)
            if match:
                return self._parse_matched_move(move_type, match, move_key)
        
        # If no pattern matches, return invalid move
        return ParsedMove(
            move_type=MoveType.PASS,
            factory_id=None,
            tile_color=None,
            target_type="unknown",
            target_position=None,
            pattern_line_id=None,
            original_string=move_key,
            is_valid=False,
            validation_errors=[f"Unknown move format: {move_key}"]
        )
    
    def _parse_matched_move(self, move_type: str, match, original_string: str) -> ParsedMove:
        """Parse a move that matched a pattern."""
        validation_errors = []
        
        if move_type == 'factory_to_pattern_line':
            factory_id = int(match.group(1))
            tile_color_str = match.group(2)
            pattern_line_id = int(match.group(3))
            
            # Validate factory ID
            if not (0 <= factory_id <= 8):  # Assuming 9 factories (0-8)
                validation_errors.append(f"Invalid factory ID: {factory_id}")
            
            # Validate tile color
            tile_color = self._validate_tile_color(tile_color_str)
            if tile_color is None:
                validation_errors.append(f"Invalid tile color: {tile_color_str}")
            
            # Validate pattern line ID
            if not (0 <= pattern_line_id <= 4):  # 5 pattern lines (0-4)
                validation_errors.append(f"Invalid pattern line ID: {pattern_line_id}")
            
            is_valid = len(validation_errors) == 0
            
            return ParsedMove(
                move_type=MoveType.FACTORY_TO_PATTERN_LINE,
                factory_id=factory_id,
                tile_color=tile_color,
                target_type="pattern_line",
                target_position=None,
                pattern_line_id=pattern_line_id,
                original_string=original_string,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
        
        elif move_type == 'factory_to_floor':
            factory_id = int(match.group(1))
            tile_color_str = match.group(2)
            
            # Validate factory ID
            if not (0 <= factory_id <= 8):
                validation_errors.append(f"Invalid factory ID: {factory_id}")
            
            # Validate tile color
            tile_color = self._validate_tile_color(tile_color_str)
            if tile_color is None:
                validation_errors.append(f"Invalid tile color: {tile_color_str}")
            
            is_valid = len(validation_errors) == 0
            
            return ParsedMove(
                move_type=MoveType.FACTORY_TO_FLOOR,
                factory_id=factory_id,
                tile_color=tile_color,
                target_type="floor",
                target_position=None,
                pattern_line_id=None,
                original_string=original_string,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
        
        elif move_type == 'factory_to_wall':
            factory_id = int(match.group(1))
            tile_color_str = match.group(2)
            wall_row = int(match.group(3))
            wall_col = int(match.group(4))
            
            # Validate factory ID
            if not (0 <= factory_id <= 8):
                validation_errors.append(f"Invalid factory ID: {factory_id}")
            
            # Validate tile color
            tile_color = self._validate_tile_color(tile_color_str)
            if tile_color is None:
                validation_errors.append(f"Invalid tile color: {tile_color_str}")
            
            # Validate wall position
            if not (0 <= wall_row <= 4) or not (0 <= wall_col <= 4):
                validation_errors.append(f"Invalid wall position: ({wall_row}, {wall_col})")
            
            is_valid = len(validation_errors) == 0
            
            return ParsedMove(
                move_type=MoveType.FACTORY_TO_WALL,
                factory_id=factory_id,
                tile_color=tile_color,
                target_type="wall",
                target_position=(wall_row, wall_col),
                pattern_line_id=None,
                original_string=original_string,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
        
        elif move_type == 'pass':
            return ParsedMove(
                move_type=MoveType.PASS,
                factory_id=None,
                tile_color=None,
                target_type="pass",
                target_position=None,
                pattern_line_id=None,
                original_string=original_string,
                is_valid=True,
                validation_errors=[]
            )
        
        else:
            return ParsedMove(
                move_type=MoveType.PASS,
                factory_id=None,
                tile_color=None,
                target_type="unknown",
                target_position=None,
                pattern_line_id=None,
                original_string=original_string,
                is_valid=False,
                validation_errors=[f"Unknown move type: {move_type}"]
            )
    
    def _validate_tile_color(self, color_str: str) -> Optional[int]:
        """Validate and convert tile color string to integer."""
        color_str_lower = color_str.lower()
        return self.color_map.get(color_str_lower)
    
    def generate_move_key(self, parsed_move: ParsedMove) -> str:
        """Generate a move key string from a parsed move."""
        if not parsed_move.is_valid:
            return parsed_move.original_string
        
        if parsed_move.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            color_name = self.reverse_color_map.get(parsed_move.tile_color, "unknown")
            return f"factory_{parsed_move.factory_id}_tile_{color_name}_pattern_line_{parsed_move.pattern_line_id}"
        
        elif parsed_move.move_type == MoveType.FACTORY_TO_FLOOR:
            color_name = self.reverse_color_map.get(parsed_move.tile_color, "unknown")
            return f"factory_{parsed_move.factory_id}_tile_{color_name}_floor"
        
        elif parsed_move.move_type == MoveType.FACTORY_TO_WALL:
            color_name = self.reverse_color_map.get(parsed_move.tile_color, "unknown")
            row, col = parsed_move.target_position
            return f"factory_{parsed_move.factory_id}_tile_{color_name}_wall_{row}_{col}"
        
        elif parsed_move.move_type == MoveType.PASS:
            return "pass"
        
        else:
            return parsed_move.original_string
    
    def get_move_description(self, parsed_move: ParsedMove) -> str:
        """Get a human-readable description of the move."""
        if not parsed_move.is_valid:
            return f"Invalid move: {', '.join(parsed_move.validation_errors)}"
        
        if parsed_move.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            color_name = self.reverse_color_map.get(parsed_move.tile_color, "unknown")
            return f"Take {color_name} tile from factory {parsed_move.factory_id} to pattern line {parsed_move.pattern_line_id}"
        
        elif parsed_move.move_type == MoveType.FACTORY_TO_FLOOR:
            color_name = self.reverse_color_map.get(parsed_move.tile_color, "unknown")
            return f"Take {color_name} tile from factory {parsed_move.factory_id} to floor"
        
        elif parsed_move.move_type == MoveType.FACTORY_TO_WALL:
            color_name = self.reverse_color_map.get(parsed_move.tile_color, "unknown")
            row, col = parsed_move.target_position
            return f"Take {color_name} tile from factory {parsed_move.factory_id} to wall position ({row}, {col})"
        
        elif parsed_move.move_type == MoveType.PASS:
            return "Pass turn"
        
        else:
            return f"Unknown move type: {parsed_move.move_type}"
    
    def validate_move_for_state(self, parsed_move: ParsedMove, state) -> List[str]:
        """
        Validate a move against a specific game state.
        
        Args:
            parsed_move: The parsed move to validate
            state: The current game state
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not parsed_move.is_valid:
            errors.extend(parsed_move.validation_errors)
            return errors
        
        # TODO: Add state-specific validation
        # This would check things like:
        # - Factory has the specified tile color
        # - Pattern line can accept the tile
        # - Wall position is valid and empty
        # - Player has enough tiles in hand
        
        return errors 