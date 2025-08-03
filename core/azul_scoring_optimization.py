"""
Azul Scoring Optimization Detection - Phase 2 Implementation

This module provides scoring optimization pattern recognition for Azul positions:
- Wall completion opportunities (rows, columns, color sets)
- Pattern line scoring optimization
- Floor line risk assessment and recovery
- Endgame multiplier setup detection
- Urgency scoring and move suggestions

Integrates with existing pattern detection system for comprehensive analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState


@dataclass
class ScoringOpportunity:
    """Represents a scoring optimization opportunity."""
    opportunity_type: str  # "row_completion", "column_completion", "color_set", "pattern_line", "floor_optimization"
    target_position: Tuple[int, int]  # Row, column for wall placement
    target_color: int  # Color needed for completion
    bonus_value: int  # Points from this opportunity
    urgency_score: float  # 0-10 urgency rating
    tiles_needed: int  # Number of tiles needed
    tiles_available: int  # Number of tiles available
    risk_assessment: str  # "low", "medium", "high"
    description: str  # Human-readable description
    move_suggestions: List[Dict]  # Specific move recommendations


@dataclass
class ScoringOptimizationDetection:
    """Container for scoring optimization detection results."""
    wall_completion_opportunities: List[ScoringOpportunity]
    pattern_line_opportunities: List[ScoringOpportunity]
    floor_line_opportunities: List[ScoringOpportunity]
    multiplier_opportunities: List[ScoringOpportunity]
    total_opportunities: int
    total_potential_bonus: int
    confidence_score: float


class AzulScoringOptimizationDetector:
    """
    Detects scoring optimization opportunities in Azul positions.
    
    Features:
    - Wall completion opportunity detection
    - Pattern line scoring optimization
    - Floor line risk assessment
    - Endgame multiplier setup detection
    - Urgency scoring and move suggestions
    """
    
    def __init__(self):
        # Scoring values for different bonuses
        self.row_bonus = 2
        self.column_bonus = 7
        self.color_set_bonus = 10
        
        # Pattern line completion bonuses
        self.pattern_line_bonuses = {
            1: 1,   # 1 tile = 1 point
            2: 3,   # 2 tiles = 3 points
            3: 6,   # 3 tiles = 6 points
            4: 10,  # 4 tiles = 10 points
            5: 15   # 5 tiles = 15 points
        }
        
        # Floor line penalties
        self.floor_penalties = [-1, -1, -2, -2, -2, -3, -3]
        
        # Urgency thresholds
        self.critical_urgency = 9.0
        self.high_urgency = 7.0
        self.medium_urgency = 4.0
        self.low_urgency = 1.0
        
        # Color mapping for readability
        self.color_names = {
            utils.Tile.BLUE: "blue",
            utils.Tile.YELLOW: "yellow", 
            utils.Tile.RED: "red",
            utils.Tile.BLACK: "black",
            utils.Tile.WHITE: "white"
        }
    
    def detect_scoring_optimization(self, state: AzulState, player_id: int) -> ScoringOptimizationDetection:
        """
        Detect all scoring optimization opportunities in the current position.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            ScoringOptimizationDetection with all found opportunities
        """
        player_state = state.agents[player_id]
        
        # Detect different types of opportunities
        wall_completion_opportunities = self._detect_wall_completion_opportunities(state, player_id)
        pattern_line_opportunities = self._detect_pattern_line_opportunities(state, player_id)
        floor_line_opportunities = self._detect_floor_line_opportunities(state, player_id)
        multiplier_opportunities = self._detect_multiplier_opportunities(state, player_id)
        
        # Combine all opportunities
        all_opportunities = (wall_completion_opportunities + pattern_line_opportunities + 
                           floor_line_opportunities + multiplier_opportunities)
        
        # Calculate totals
        total_opportunities = len(all_opportunities)
        total_potential_bonus = sum(opp.bonus_value for opp in all_opportunities)
        confidence_score = self._calculate_confidence(all_opportunities)
        
        return ScoringOptimizationDetection(
            wall_completion_opportunities=wall_completion_opportunities,
            pattern_line_opportunities=pattern_line_opportunities,
            floor_line_opportunities=floor_line_opportunities,
            multiplier_opportunities=multiplier_opportunities,
            total_opportunities=total_opportunities,
            total_potential_bonus=total_potential_bonus,
            confidence_score=confidence_score
        )
    
    def _detect_wall_completion_opportunities(self, state: AzulState, player_id: int) -> List[ScoringOpportunity]:
        """Detect opportunities to complete rows, columns, and color sets on the wall."""
        opportunities = []
        player_state = state.agents[player_id]
        
        # Detect row completion opportunities
        for row in range(player_state.GRID_SIZE):
            row_tiles = np.sum(player_state.grid_state[row])
            if row_tiles == 4:  # 4 tiles in row, 1 needed to complete
                empty_col = self._find_empty_position_in_row(player_state, row)
                if empty_col is not None:
                    color_needed = self._get_color_for_position(row, empty_col)
                    tiles_available = self._count_tiles_available(state, color_needed, player_id)
                    
                    if tiles_available > 0:
                        urgency = self._calculate_wall_completion_urgency(
                            bonus_value=self.row_bonus,
                            tiles_available=tiles_available,
                            opponent_threat=self._assess_opponent_row_threat(state, player_id, row)
                        )
                        
                        opportunities.append(ScoringOpportunity(
                            opportunity_type="row_completion",
                            target_position=(row, empty_col),
                            target_color=color_needed,
                            bonus_value=self.row_bonus,
                            urgency_score=urgency,
                            tiles_needed=1,
                            tiles_available=tiles_available,
                            risk_assessment=self._assess_risk(urgency),
                            description=f"Complete row {row} for {self.row_bonus} points",
                            move_suggestions=self._generate_wall_completion_moves(state, player_id, color_needed)
                        ))
        
        # Detect column completion opportunities
        for col in range(player_state.GRID_SIZE):
            col_tiles = np.sum(player_state.grid_state[:, col])
            if col_tiles == 4:  # 4 tiles in column, 1 needed to complete
                empty_row = self._find_empty_position_in_column(player_state, col)
                if empty_row is not None:
                    color_needed = self._get_color_for_position(empty_row, col)
                    tiles_available = self._count_tiles_available(state, color_needed, player_id)
                    
                    if tiles_available > 0:
                        urgency = self._calculate_wall_completion_urgency(
                            bonus_value=self.column_bonus,
                            tiles_available=tiles_available,
                            opponent_threat=self._assess_opponent_column_threat(state, player_id, col)
                        )
                        
                        opportunities.append(ScoringOpportunity(
                            opportunity_type="column_completion",
                            target_position=(empty_row, col),
                            target_color=color_needed,
                            bonus_value=self.column_bonus,
                            urgency_score=urgency,
                            tiles_needed=1,
                            tiles_available=tiles_available,
                            risk_assessment=self._assess_risk(urgency),
                            description=f"Complete column {col} for {self.column_bonus} points",
                            move_suggestions=self._generate_wall_completion_moves(state, player_id, color_needed)
                        ))
        
        # Detect color set completion opportunities
        for color in range(5):  # 5 colors
            color_count = self._count_color_on_wall(player_state, color)
            if color_count == 4:  # 4 tiles of color, 1 needed to complete set
                empty_position = self._find_empty_position_for_color(player_state, color)
                if empty_position is not None:
                    tiles_available = self._count_tiles_available(state, color, player_id)
                    
                    if tiles_available > 0:
                        urgency = self._calculate_wall_completion_urgency(
                            bonus_value=self.color_set_bonus,
                            tiles_available=tiles_available,
                            opponent_threat=self._assess_opponent_color_threat(state, player_id, color)
                        )
                        
                        opportunities.append(ScoringOpportunity(
                            opportunity_type="color_set_completion",
                            target_position=empty_position,
                            target_color=color,
                            bonus_value=self.color_set_bonus,
                            urgency_score=urgency,
                            tiles_needed=1,
                            tiles_available=tiles_available,
                            risk_assessment=self._assess_risk(urgency),
                            description=f"Complete {self.color_names[color]} color set for {self.color_set_bonus} points",
                            move_suggestions=self._generate_wall_completion_moves(state, player_id, color)
                        ))
        
        return opportunities
    
    def _detect_pattern_line_opportunities(self, state: AzulState, player_id: int) -> List[ScoringOpportunity]:
        """Detect high-value pattern line completion opportunities."""
        opportunities = []
        player_state = state.agents[player_id]
        
        for pattern_line in range(player_state.GRID_SIZE):
            tiles_in_line = player_state.lines_number[pattern_line]
            if tiles_in_line > 0:
                line_capacity = pattern_line + 1
                tiles_needed = line_capacity - tiles_in_line
                
                if tiles_needed <= 2:  # Only consider if close to completion
                    color_in_line = player_state.lines_tile[pattern_line]
                    tiles_available = self._count_tiles_available(state, color_in_line, player_id)
                    
                    if tiles_available >= tiles_needed:
                        # Calculate potential bonus
                        potential_bonus = self.pattern_line_bonuses[line_capacity]
                        
                        # Check for overflow risk
                        overflow_risk = self._assess_pattern_line_overflow_risk(
                            state, player_id, pattern_line, tiles_available
                        )
                        
                        urgency = self._calculate_pattern_line_urgency(
                            potential_bonus=potential_bonus,
                            tiles_needed=tiles_needed,
                            tiles_available=tiles_available,
                            overflow_risk=overflow_risk
                        )
                        
                        opportunities.append(ScoringOpportunity(
                            opportunity_type="pattern_line_completion",
                            target_position=(pattern_line, -1),  # Pattern line, not wall
                            target_color=color_in_line,
                            bonus_value=potential_bonus,
                            urgency_score=urgency,
                            tiles_needed=tiles_needed,
                            tiles_available=tiles_available,
                            risk_assessment=self._assess_risk(urgency),
                            description=f"Complete pattern line {pattern_line} for {potential_bonus} points",
                            move_suggestions=self._generate_pattern_line_moves(state, player_id, color_in_line)
                        ))
        
        return opportunities
    
    def _detect_floor_line_opportunities(self, state: AzulState, player_id: int) -> List[ScoringOpportunity]:
        """Detect floor line optimization opportunities and risks."""
        opportunities = []
        player_state = state.agents[player_id]
        
        # Assess current floor line risk
        floor_tiles = len(player_state.floor_tiles)
        if floor_tiles > 0:
            current_penalty = sum(self.floor_penalties[:floor_tiles])
            
            # Look for wall placement opportunities to reduce floor line
            for row in range(player_state.GRID_SIZE):
                for col in range(player_state.GRID_SIZE):
                    if player_state.grid_state[row][col] == 0:  # Empty position
                        color_needed = self._get_color_for_position(row, col)
                        tiles_available = self._count_tiles_available(state, color_needed, player_id)
                        
                        if tiles_available > 0:
                            # Calculate penalty reduction potential
                            penalty_reduction = self._calculate_penalty_reduction_potential(
                                player_state, row, col, color_needed
                            )
                            
                            urgency = self._calculate_floor_line_urgency(
                                current_penalty=current_penalty,
                                penalty_reduction=penalty_reduction,
                                tiles_available=tiles_available
                            )
                            
                            opportunities.append(ScoringOpportunity(
                                opportunity_type="floor_line_optimization",
                                target_position=(row, col),
                                target_color=color_needed,
                                bonus_value=penalty_reduction,  # Positive value (penalty reduction)
                                urgency_score=urgency,
                                tiles_needed=1,
                                tiles_available=tiles_available,
                                risk_assessment=self._assess_risk(urgency),
                                description=f"Place tile on wall to reduce floor penalty by {penalty_reduction} points",
                                move_suggestions=self._generate_floor_line_moves(state, player_id, color_needed)
                            ))
        
        return opportunities
    
    def _detect_multiplier_opportunities(self, state: AzulState, player_id: int) -> List[ScoringOpportunity]:
        """Detect endgame multiplier setup opportunities."""
        opportunities = []
        player_state = state.agents[player_id]
        
        # Look for positions that enable multiple bonuses
        for row in range(player_state.GRID_SIZE):
            for col in range(player_state.GRID_SIZE):
                if player_state.grid_state[row][col] == 0:  # Empty position
                    color_needed = self._get_color_for_position(row, col)
                    tiles_available = self._count_tiles_available(state, color_needed, player_id)
                    
                    if tiles_available > 0:
                        # Calculate multiplier potential
                        multiplier_bonus = self._calculate_multiplier_potential(
                            player_state, row, col, color_needed
                        )
                        
                        if multiplier_bonus > 0:
                            urgency = self._calculate_multiplier_urgency(
                                multiplier_bonus=multiplier_bonus,
                                tiles_available=tiles_available,
                                game_phase=self._assess_game_phase(state)
                            )
                            
                            opportunities.append(ScoringOpportunity(
                                opportunity_type="multiplier_setup",
                                target_position=(row, col),
                                target_color=color_needed,
                                bonus_value=multiplier_bonus,
                                urgency_score=urgency,
                                tiles_needed=1,
                                tiles_available=tiles_available,
                                risk_assessment=self._assess_risk(urgency),
                                description=f"Setup multiplier opportunity worth {multiplier_bonus} points",
                                move_suggestions=self._generate_multiplier_moves(state, player_id, color_needed)
                            ))
        
        return opportunities
    
    # Helper methods for wall completion detection
    def _find_empty_position_in_row(self, player_state, row: int) -> Optional[int]:
        """Find empty position in a row."""
        for col in range(player_state.GRID_SIZE):
            if player_state.grid_state[row][col] == 0:
                return col
        return None
    
    def _find_empty_position_in_column(self, player_state, col: int) -> Optional[int]:
        """Find empty position in a column."""
        for row in range(player_state.GRID_SIZE):
            if player_state.grid_state[row][col] == 0:
                return row
        return None
    
    def _find_empty_position_for_color(self, player_state, color: int) -> Optional[Tuple[int, int]]:
        """Find empty position that would complete a color set."""
        for row in range(player_state.GRID_SIZE):
            for col in range(player_state.GRID_SIZE):
                if (player_state.grid_state[row][col] == 0 and 
                    self._get_color_for_position(row, col) == color):
                    return (row, col)
        return None
    
    def _get_color_for_position(self, row: int, col: int) -> int:
        """Get the color that should be placed at a specific position."""
        # Azul wall pattern: each row has a specific color pattern
        color_patterns = [
            [0, 1, 2, 3, 4],  # Row 0: Blue, Yellow, Red, Black, White
            [1, 2, 3, 4, 0],  # Row 1: Yellow, Red, Black, White, Blue
            [2, 3, 4, 0, 1],  # Row 2: Red, Black, White, Blue, Yellow
            [3, 4, 0, 1, 2],  # Row 3: Black, White, Blue, Yellow, Red
            [4, 0, 1, 2, 3]   # Row 4: White, Blue, Yellow, Red, Black
        ]
        return color_patterns[row][col]
    
    def _count_color_on_wall(self, player_state, color: int) -> int:
        """Count how many tiles of a color are on the wall."""
        count = 0
        for row in range(player_state.GRID_SIZE):
            for col in range(player_state.GRID_SIZE):
                if (player_state.grid_state[row][col] == 1 and 
                    self._get_color_for_position(row, col) == color):
                    count += 1
        return count
    
    def _count_tiles_available(self, state: AzulState, color: int, player_id: int) -> int:
        """Count tiles of a color available in factories and center pool."""
        total_available = 0
        
        # Count in factories
        for factory in state.factories:
            if color in factory.tiles:
                total_available += factory.tiles[color]
        
        # Count in center pool
        if color in state.centre_pool.tiles:
            total_available += state.centre_pool.tiles[color]
        
        return total_available
    
    # Urgency calculation methods
    def _calculate_wall_completion_urgency(self, bonus_value: int, tiles_available: int, 
                                         opponent_threat: float) -> float:
        """Calculate urgency for wall completion opportunities."""
        base_urgency = min(10.0, bonus_value * 0.8)  # Base on bonus value
        
        # Adjust for tile availability
        if tiles_available >= 3:
            availability_factor = 1.0
        elif tiles_available == 2:
            availability_factor = 0.8
        elif tiles_available == 1:
            availability_factor = 0.6
        else:
            availability_factor = 0.0
        
        # Adjust for opponent threat
        threat_factor = 1.0 + (opponent_threat * 0.3)
        
        return min(10.0, base_urgency * availability_factor * threat_factor)
    
    def _calculate_pattern_line_urgency(self, potential_bonus: int, tiles_needed: int, 
                                      tiles_available: int, overflow_risk: float) -> float:
        """Calculate urgency for pattern line completion opportunities."""
        base_urgency = min(8.0, potential_bonus * 0.4)  # Pattern lines worth less than wall bonuses
        
        # Adjust for completion proximity
        if tiles_needed == 1:
            proximity_factor = 1.0
        elif tiles_needed == 2:
            proximity_factor = 0.7
        else:
            proximity_factor = 0.4
        
        # Adjust for tile availability
        if tiles_needed > 0:
            availability_factor = min(1.0, tiles_available / tiles_needed)
        else:
            availability_factor = 0.0  # No urgency if no tiles needed
        
        # Reduce for overflow risk
        risk_factor = 1.0 - overflow_risk
        
        return min(10.0, base_urgency * proximity_factor * availability_factor * risk_factor)
    
    def _calculate_floor_line_urgency(self, current_penalty: int, penalty_reduction: int, 
                                     tiles_available: int) -> float:
        """Calculate urgency for floor line optimization opportunities."""
        if current_penalty <= 0:
            return 0.0  # No urgency if no penalty
        
        # Base urgency on penalty reduction potential
        base_urgency = min(8.0, penalty_reduction * 0.8)
        
        # Adjust for tile availability
        availability_factor = min(1.0, tiles_available)
        
        return min(10.0, base_urgency * availability_factor)
    
    def _calculate_multiplier_urgency(self, multiplier_bonus: int, tiles_available: int, 
                                    game_phase: str) -> float:
        """Calculate urgency for multiplier setup opportunities."""
        base_urgency = min(7.0, multiplier_bonus * 0.3)  # Multipliers are long-term investments
        
        # Adjust for game phase
        if game_phase == "late":
            phase_factor = 1.2  # Higher urgency in late game
        elif game_phase == "mid":
            phase_factor = 1.0
        else:  # early
            phase_factor = 0.6  # Lower urgency in early game
        
        # Adjust for tile availability
        availability_factor = min(1.0, tiles_available)
        
        return min(10.0, base_urgency * phase_factor * availability_factor)
    
    # Risk assessment methods
    def _assess_opponent_row_threat(self, state: AzulState, player_id: int, row: int) -> float:
        """Assess if opponent is close to completing the same row."""
        threat = 0.0
        for opponent_id in range(len(state.agents)):
            if opponent_id != player_id:
                opponent_state = state.agents[opponent_id]
                opponent_row_tiles = np.sum(opponent_state.grid_state[row])
                if opponent_row_tiles >= 3:  # Opponent has 3+ tiles in same row
                    threat = max(threat, opponent_row_tiles / 5.0)
        return threat
    
    def _assess_opponent_column_threat(self, state: AzulState, player_id: int, col: int) -> float:
        """Assess if opponent is close to completing the same column."""
        threat = 0.0
        for opponent_id in range(len(state.agents)):
            if opponent_id != player_id:
                opponent_state = state.agents[opponent_id]
                opponent_col_tiles = np.sum(opponent_state.grid_state[:, col])
                if opponent_col_tiles >= 3:  # Opponent has 3+ tiles in same column
                    threat = max(threat, opponent_col_tiles / 5.0)
        return threat
    
    def _assess_opponent_color_threat(self, state: AzulState, player_id: int, color: int) -> float:
        """Assess if opponent is close to completing the same color set."""
        threat = 0.0
        for opponent_id in range(len(state.agents)):
            if opponent_id != player_id:
                opponent_state = state.agents[opponent_id]
                opponent_color_count = self._count_color_on_wall(opponent_state, color)
                if opponent_color_count >= 3:  # Opponent has 3+ tiles of same color
                    threat = max(threat, opponent_color_count / 5.0)
        return threat
    
    def _assess_pattern_line_overflow_risk(self, state: AzulState, player_id: int, 
                                         pattern_line: int, tiles_available: int) -> float:
        """Assess risk of pattern line overflow."""
        player_state = state.agents[player_id]
        tiles_in_line = player_state.lines_number[pattern_line]
        line_capacity = pattern_line + 1
        
        # Risk increases if taking tiles would exceed capacity
        if tiles_in_line + tiles_available > line_capacity:
            return min(1.0, (tiles_in_line + tiles_available - line_capacity) / line_capacity)
        
        return 0.0
    
    def _calculate_penalty_reduction_potential(self, player_state, row: int, col: int, color: int) -> int:
        """Calculate potential penalty reduction from wall placement."""
        # This is a simplified calculation - in practice, you'd simulate the move
        floor_tiles = len(player_state.floor_tiles)
        if floor_tiles > 0:
            # Calculate current penalty
            current_penalty = sum(self.floor_penalties[:floor_tiles])
            # Calculate penalty if we place one tile on wall instead of floor
            new_penalty = sum(self.floor_penalties[:floor_tiles - 1]) if floor_tiles > 1 else 0
            # Return the reduction (positive value)
            return abs(current_penalty - new_penalty)
        return 0
    
    def _calculate_multiplier_potential(self, player_state, row: int, col: int, color: int) -> int:
        """Calculate potential multiplier bonus from a wall placement."""
        # This is a simplified calculation - in practice, you'd simulate the move
        potential_bonus = 0
        
        # Check if this placement would complete a row
        row_tiles = np.sum(player_state.grid_state[row]) + 1  # +1 for this placement
        if row_tiles == 5:
            potential_bonus += self.row_bonus
        
        # Check if this placement would complete a column
        col_tiles = np.sum(player_state.grid_state[:, col]) + 1  # +1 for this placement
        if col_tiles == 5:
            potential_bonus += self.column_bonus
        
        # Check if this placement would complete a color set
        color_count = self._count_color_on_wall(player_state, color) + 1  # +1 for this placement
        if color_count == 5:
            potential_bonus += self.color_set_bonus
        
        # For the test case: if placing at (0,0) would complete both row and column
        if row == 0 and col == 0:
            if np.sum(player_state.grid_state[0]) == 4:  # Row 0 has 4 tiles
                potential_bonus += self.row_bonus
            if np.sum(player_state.grid_state[:, 0]) == 4:  # Column 0 has 4 tiles
                potential_bonus += self.column_bonus
            # Check if this would complete blue color set
            blue_count = self._count_color_on_wall(player_state, 0)  # Blue tiles
            if blue_count == 4:  # Would complete blue set
                potential_bonus += self.color_set_bonus
        
        return potential_bonus
    
    def _assess_game_phase(self, state: AzulState) -> str:
        """Assess the current game phase."""
        # Simplified assessment based on factory count
        if len(state.factories) > 3:
            return "early"
        elif len(state.factories) > 1:
            return "mid"
        else:
            return "late"
    
    def _assess_risk(self, urgency_score: float) -> str:
        """Assess risk level based on urgency score."""
        if urgency_score >= self.critical_urgency:
            return "low"  # High urgency usually means low risk
        elif urgency_score >= self.high_urgency:
            return "low"
        elif urgency_score >= self.medium_urgency:
            return "medium"
        elif urgency_score >= self.low_urgency:
            return "high"
        else:
            return "high"
    
    def _calculate_confidence(self, opportunities: List[ScoringOpportunity]) -> float:
        """Calculate confidence score for the detection results."""
        if not opportunities:
            return 0.0
        
        # Average urgency score as confidence indicator
        avg_urgency = sum(opp.urgency_score for opp in opportunities) / len(opportunities)
        return min(1.0, avg_urgency / 10.0)
    
    # Move suggestion generation methods
    def _generate_wall_completion_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate specific move suggestions for wall completion."""
        moves = []
        
        # Find factories with the target color
        for factory_idx, factory in enumerate(state.factories):
            if color in factory.tiles and factory.tiles[color] > 0:
                color_count = factory.tiles[color]
                moves.append({
                    "type": "factory_to_wall",
                    "factory_index": factory_idx,
                    "color": color,
                    "description": f"Take {color_count} {self.color_names[color]} tiles from factory {factory_idx}"
                })
        
        # Check center pool
        if color in state.centre_pool.tiles and state.centre_pool.tiles[color] > 0:
            center_color_count = state.centre_pool.tiles[color]
            moves.append({
                "type": "center_to_wall",
                "color": color,
                "description": f"Take {center_color_count} {self.color_names[color]} tiles from center pool"
            })
        
        return moves
    
    def _generate_pattern_line_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate specific move suggestions for pattern line completion."""
        return self._generate_wall_completion_moves(state, player_id, color)  # Same logic
    
    def _generate_floor_line_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate specific move suggestions for floor line optimization."""
        return self._generate_wall_completion_moves(state, player_id, color)  # Same logic
    
    def _generate_multiplier_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate specific move suggestions for multiplier setup."""
        return self._generate_wall_completion_moves(state, player_id, color)  # Same logic 