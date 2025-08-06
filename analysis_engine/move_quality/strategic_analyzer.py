"""
Strategic Value Analyzer

This module provides strategic analysis for Azul moves, evaluating
long-term strategic considerations like wall development, factory control,
and endgame positioning.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from core import azul_utils as utils
from core.azul_model import AzulState
from .move_parser import ParsedMove, MoveType


@dataclass
class StrategicAnalysis:
    """Strategic analysis results for a move."""
    wall_development_value: float  # Value of wall development
    factory_control_value: float   # Value of factory control
    endgame_positioning_value: float  # Value of endgame positioning
    tempo_value: float  # Value of tempo control
    overall_strategic_value: float  # Combined strategic value
    strategic_insights: List[str]  # Strategic insights
    confidence_score: float  # Confidence in strategic assessment


class AzulStrategicAnalyzer:
    """
    Analyzes strategic value of Azul moves.
    
    Evaluates:
    - Wall development and structure
    - Factory control and tempo
    - Endgame positioning
    - Strategic opportunities and threats
    """
    
    def __init__(self):
        # Strategic scoring weights
        self.strategic_weights = {
            'wall_development': 0.35,
            'factory_control': 0.25,
            'endgame_positioning': 0.25,
            'tempo': 0.15
        }
        
        # Wall development scoring
        self.wall_completion_bonus = 10.0  # Bonus for completing wall sections
        self.wall_structure_bonus = 5.0     # Bonus for good wall structure
        self.color_diversity_bonus = 3.0    # Bonus for color diversity
        
        # Factory control scoring
        self.factory_control_bonus = 8.0    # Bonus for controlling factories
        self.tempo_bonus = 6.0              # Bonus for tempo control
        
        # Endgame scoring
        self.endgame_positioning_bonus = 12.0  # Bonus for endgame positioning
        self.row_completion_bonus = 15.0       # Bonus for row completion
        self.column_completion_bonus = 20.0    # Bonus for column completion
        
        # Color names for insights
        self.color_names = {
            utils.Tile.BLUE: "blue",
            utils.Tile.YELLOW: "yellow",
            utils.Tile.RED: "red",
            utils.Tile.BLACK: "black",
            utils.Tile.WHITE: "white"
        }
    
    def analyze_strategic_value(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> StrategicAnalysis:
        """
        Analyze the strategic value of a move.
        
        Args:
            state: Current game state
            player_id: Player making the move
            parsed_move: Parsed move to analyze
            
        Returns:
            StrategicAnalysis with detailed strategic assessment
        """
        # Analyze different strategic aspects
        wall_development = self._analyze_wall_development(state, player_id, parsed_move)
        factory_control = self._analyze_factory_control(state, player_id, parsed_move)
        endgame_positioning = self._analyze_endgame_positioning(state, player_id, parsed_move)
        tempo_value = self._analyze_tempo_control(state, player_id, parsed_move)
        
        # Calculate overall strategic value
        overall_value = (
            wall_development * self.strategic_weights['wall_development'] +
            factory_control * self.strategic_weights['factory_control'] +
            endgame_positioning * self.strategic_weights['endgame_positioning'] +
            tempo_value * self.strategic_weights['tempo']
        )
        
        # Generate strategic insights
        insights = self._generate_strategic_insights(
            wall_development, factory_control, endgame_positioning, tempo_value, parsed_move
        )
        
        # Calculate confidence score
        confidence = self._calculate_strategic_confidence(
            wall_development, factory_control, endgame_positioning, tempo_value
        )
        
        return StrategicAnalysis(
            wall_development_value=wall_development,
            factory_control_value=factory_control,
            endgame_positioning_value=endgame_positioning,
            tempo_value=tempo_value,
            overall_strategic_value=overall_value,
            strategic_insights=insights,
            confidence_score=confidence
        )
    
    def _analyze_wall_development(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> float:
        """Analyze wall development value of the move."""
        if parsed_move.move_type != MoveType.FACTORY_TO_WALL:
            return 0.0  # Only wall placements contribute to wall development
        
        player_state = state.agents[player_id]
        wall = player_state.wall
        row, col = parsed_move.target_position
        tile_color = parsed_move.tile_color
        
        # Check if this is a valid wall placement
        if not self._is_valid_wall_placement(wall, row, col, tile_color):
            return 0.0
        
        # Calculate wall development value
        value = 0.0
        
        # Base value for wall placement
        value += 5.0
        
        # Bonus for completing rows
        if self._would_complete_row(wall, row, col, tile_color):
            value += self.row_completion_bonus
        
        # Bonus for completing columns
        if self._would_complete_column(wall, row, col, tile_color):
            value += self.column_completion_bonus
        
        # Bonus for good wall structure
        value += self._calculate_wall_structure_bonus(wall, row, col, tile_color)
        
        # Bonus for color diversity
        value += self._calculate_color_diversity_bonus(wall, row, col, tile_color)
        
        return min(value, 100.0)  # Cap at 100
    
    def _analyze_factory_control(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> float:
        """Analyze factory control value of the move."""
        if parsed_move.move_type == MoveType.PASS:
            return 0.0
        
        factory_id = parsed_move.factory_id
        tile_color = parsed_move.tile_color
        
        # Calculate factory control value
        value = 0.0
        
        # Base value for taking tiles from factory
        value += 3.0
        
        # Bonus for taking specific colors that help opponents
        if self._is_denying_opponent_tiles(state, player_id, factory_id, tile_color):
            value += self.factory_control_bonus
        
        # Bonus for taking tiles that complete opponent patterns
        if self._is_blocking_opponent_patterns(state, player_id, factory_id, tile_color):
            value += self.factory_control_bonus * 0.5
        
        # Bonus for taking tiles that help your own patterns
        if self._helps_own_patterns(state, player_id, tile_color):
            value += self.factory_control_bonus * 0.3
        
        return min(value, 100.0)
    
    def _analyze_endgame_positioning(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> float:
        """Analyze endgame positioning value of the move."""
        # Calculate how many rounds are left
        rounds_left = self._estimate_rounds_left(state)
        
        if rounds_left <= 2:  # Endgame phase
            value = 0.0
            
            # Bonus for moves that complete wall sections
            if parsed_move.move_type == MoveType.FACTORY_TO_WALL:
                row, col = parsed_move.target_position
                if self._would_complete_wall_section(state, player_id, row, col, parsed_move.tile_color):
                    value += self.endgame_positioning_bonus
            
            # Bonus for moves that prevent opponent completions
            if self._prevents_opponent_completions(state, player_id, parsed_move):
                value += self.endgame_positioning_bonus * 0.8
            
            # Bonus for moves that set up final scoring
            if self._sets_up_final_scoring(state, player_id, parsed_move):
                value += self.endgame_positioning_bonus * 0.6
            
            return min(value, 100.0)
        else:
            # Not in endgame, minimal value
            return 5.0
    
    def _analyze_tempo_control(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> float:
        """Analyze tempo control value of the move."""
        value = 0.0
        
        # Base value for any move
        value += 2.0
        
        # Bonus for moves that force opponent responses
        if self._forces_opponent_response(state, player_id, parsed_move):
            value += self.tempo_bonus
        
        # Bonus for moves that maintain initiative
        if self._maintains_initiative(state, player_id, parsed_move):
            value += self.tempo_bonus * 0.5
        
        # Penalty for moves that give up initiative
        if self._gives_up_initiative(state, player_id, parsed_move):
            value -= self.tempo_bonus * 0.3
        
        return max(0.0, min(value, 100.0))
    
    def _is_valid_wall_placement(self, wall, row: int, col: int, tile_color: int) -> bool:
        """Check if a wall placement is valid."""
        # Check if position is empty
        if wall[row][col] != -1:
            return False
        
        # Check if color is valid for this position
        # In Azul, each position can only accept certain colors
        valid_colors = self._get_valid_colors_for_position(row, col)
        return tile_color in valid_colors
    
    def _get_valid_colors_for_position(self, row: int, col: int) -> List[int]:
        """Get valid colors for a wall position."""
        # Azul wall color restrictions
        color_restrictions = [
            [utils.Tile.BLUE, utils.Tile.YELLOW, utils.Tile.RED, utils.Tile.BLACK, utils.Tile.WHITE],
            [utils.Tile.WHITE, utils.Tile.BLUE, utils.Tile.YELLOW, utils.Tile.RED, utils.Tile.BLACK],
            [utils.Tile.BLACK, utils.Tile.WHITE, utils.Tile.BLUE, utils.Tile.YELLOW, utils.Tile.RED],
            [utils.Tile.RED, utils.Tile.BLACK, utils.Tile.WHITE, utils.Tile.BLUE, utils.Tile.YELLOW],
            [utils.Tile.YELLOW, utils.Tile.RED, utils.Tile.BLACK, utils.Tile.WHITE, utils.Tile.BLUE]
        ]
        
        return color_restrictions[row][col]
    
    def _would_complete_row(self, wall, row: int, col: int, tile_color: int) -> bool:
        """Check if placing tile would complete a row."""
        # Simulate placing the tile
        temp_wall = [row[:] for row in wall]
        temp_wall[row][col] = tile_color
        
        # Check if row is complete
        return all(cell != -1 for cell in temp_wall[row])
    
    def _would_complete_column(self, wall, row: int, col: int, tile_color: int) -> bool:
        """Check if placing tile would complete a column."""
        # Simulate placing the tile
        temp_wall = [row[:] for row in wall]
        temp_wall[row][col] = tile_color
        
        # Check if column is complete
        return all(temp_wall[r][col] != -1 for r in range(5))
    
    def _calculate_wall_structure_bonus(self, wall, row: int, col: int, tile_color: int) -> float:
        """Calculate bonus for good wall structure."""
        bonus = 0.0
        
        # Bonus for adjacent tiles
        adjacent_count = self._count_adjacent_tiles(wall, row, col)
        bonus += adjacent_count * 2.0
        
        # Bonus for creating patterns
        if self._creates_good_pattern(wall, row, col, tile_color):
            bonus += self.wall_structure_bonus
        
        return bonus
    
    def _calculate_color_diversity_bonus(self, wall, row: int, col: int, tile_color: int) -> float:
        """Calculate bonus for color diversity."""
        # Count different colors in the wall
        colors_in_wall = set()
        for r in range(5):
            for c in range(5):
                if wall[r][c] != -1:
                    colors_in_wall.add(wall[r][c])
        
        # Add the new color
        colors_in_wall.add(tile_color)
        
        # Bonus for more diverse colors
        return len(colors_in_wall) * self.color_diversity_bonus
    
    def _count_adjacent_tiles(self, wall, row: int, col: int) -> int:
        """Count adjacent tiles to a position."""
        count = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and wall[new_row][new_col] != -1:
                count += 1
        return count
    
    def _creates_good_pattern(self, wall, row: int, col: int, tile_color: int) -> bool:
        """Check if placing tile creates a good pattern."""
        # This is a simplified check - in a real implementation,
        # you would analyze various pattern types
        return self._count_adjacent_tiles(wall, row, col) >= 2
    
    def _is_denying_opponent_tiles(self, state: AzulState, player_id: int, factory_id: int, tile_color: int) -> bool:
        """Check if taking tiles denies opponents useful tiles."""
        # Simplified implementation
        # In a real implementation, you would analyze what tiles opponents need
        return True  # Placeholder
    
    def _is_blocking_opponent_patterns(self, state: AzulState, player_id: int, factory_id: int, tile_color: int) -> bool:
        """Check if taking tiles blocks opponent patterns."""
        # Simplified implementation
        return True  # Placeholder
    
    def _helps_own_patterns(self, state: AzulState, player_id: int, tile_color: int) -> bool:
        """Check if taking tiles helps own patterns."""
        # Simplified implementation
        return True  # Placeholder
    
    def _estimate_rounds_left(self, state: AzulState) -> int:
        """Estimate how many rounds are left in the game."""
        # Simplified implementation
        # In a real implementation, you would analyze bag contents and factory states
        return 5  # Placeholder
    
    def _would_complete_wall_section(self, state: AzulState, player_id: int, row: int, col: int, tile_color: int) -> bool:
        """Check if placing tile would complete a wall section."""
        # Simplified implementation
        return self._would_complete_row(state.agents[player_id].wall, row, col, tile_color) or \
               self._would_complete_column(state.agents[player_id].wall, row, col, tile_color)
    
    def _prevents_opponent_completions(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> bool:
        """Check if move prevents opponent completions."""
        # Simplified implementation
        return True  # Placeholder
    
    def _sets_up_final_scoring(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> bool:
        """Check if move sets up final scoring opportunities."""
        # Simplified implementation
        return True  # Placeholder
    
    def _forces_opponent_response(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> bool:
        """Check if move forces opponent to respond."""
        # Simplified implementation
        return True  # Placeholder
    
    def _maintains_initiative(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> bool:
        """Check if move maintains initiative."""
        # Simplified implementation
        return True  # Placeholder
    
    def _gives_up_initiative(self, state: AzulState, player_id: int, parsed_move: ParsedMove) -> bool:
        """Check if move gives up initiative."""
        # Simplified implementation
        return False  # Placeholder
    
    def _generate_strategic_insights(self, wall_development: float, factory_control: float,
                                   endgame_positioning: float, tempo_value: float,
                                   parsed_move: ParsedMove) -> List[str]:
        """Generate strategic insights from the analysis."""
        insights = []
        
        if wall_development > 20.0:
            insights.append("This move significantly improves wall development")
        
        if factory_control > 15.0:
            insights.append("This move provides good factory control")
        
        if endgame_positioning > 25.0:
            insights.append("This move has strong endgame positioning value")
        
        if tempo_value > 10.0:
            insights.append("This move maintains good tempo control")
        
        if parsed_move.move_type == MoveType.FACTORY_TO_WALL:
            insights.append("Wall placement contributes to long-term strategy")
        elif parsed_move.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            insights.append("Pattern line placement sets up future opportunities")
        elif parsed_move.move_type == MoveType.FACTORY_TO_FLOOR:
            insights.append("Floor placement may be strategically necessary")
        
        return insights
    
    def _calculate_strategic_confidence(self, wall_development: float, factory_control: float,
                                      endgame_positioning: float, tempo_value: float) -> float:
        """Calculate confidence in strategic assessment."""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on component values
        if wall_development > 0:
            confidence += 0.1
        
        if factory_control > 0:
            confidence += 0.1
        
        if endgame_positioning > 0:
            confidence += 0.1
        
        if tempo_value > 0:
            confidence += 0.1
        
        return min(confidence, 1.0) 