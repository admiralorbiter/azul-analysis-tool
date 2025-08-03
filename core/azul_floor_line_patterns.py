"""
Azul Floor Line Management Pattern Detection - Phase 2.3 Implementation

This module provides floor line management pattern recognition for Azul positions:
- Floor line risk assessment and mitigation
- Strategic floor line timing patterns
- Floor line vs wall placement trade-offs
- Endgame floor line management
- Floor line blocking opportunities
- Floor line efficiency patterns

Integrates with existing pattern detection system for comprehensive analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState


@dataclass
class FloorLineOpportunity:
    """Represents a floor line management opportunity."""
    opportunity_type: str  # "risk_mitigation", "timing_optimization", "trade_off", "endgame_management", "blocking", "efficiency"
    target_position: Optional[Tuple[int, int]]  # Row, column for wall placement (if applicable)
    target_color: Optional[int]  # Color needed for placement (if applicable)
    current_floor_tiles: int  # Current tiles on floor line
    potential_penalty: int  # Current or potential floor line penalty
    penalty_reduction: int  # Points saved by taking action
    urgency_score: float  # 0-10 urgency rating
    risk_assessment: str  # "low", "medium", "high", "critical"
    description: str  # Human-readable description
    move_suggestions: List[Dict]  # Specific move recommendations
    strategic_value: float  # Strategic importance beyond immediate points


@dataclass
class FloorLinePatternDetection:
    """Container for floor line pattern detection results."""
    risk_mitigation_opportunities: List[FloorLineOpportunity]
    timing_optimization_opportunities: List[FloorLineOpportunity]
    trade_off_opportunities: List[FloorLineOpportunity]
    endgame_management_opportunities: List[FloorLineOpportunity]
    blocking_opportunities: List[FloorLineOpportunity]
    efficiency_opportunities: List[FloorLineOpportunity]
    total_opportunities: int
    total_penalty_risk: int
    confidence_score: float


class AzulFloorLinePatternDetector:
    """
    Detects floor line management patterns in Azul positions.
    
    Features:
    - Floor line risk assessment and mitigation
    - Strategic floor line timing patterns
    - Floor line vs wall placement trade-offs
    - Endgame floor line management
    - Floor line blocking opportunities
    - Floor line efficiency patterns
    """
    
    def __init__(self):
        # Floor line penalties
        self.floor_penalties = [-1, -1, -2, -2, -2, -3, -3]
        
        # Urgency thresholds
        self.critical_urgency = 9.0
        self.high_urgency = 7.0
        self.medium_urgency = 4.0
        self.low_urgency = 1.0
        
        # Risk thresholds
        self.critical_risk_threshold = 6  # 6+ tiles on floor
        self.high_risk_threshold = 4      # 4-5 tiles on floor
        self.medium_risk_threshold = 2    # 2-3 tiles on floor
        
        # Color mapping for readability
        self.color_names = {
            utils.Tile.BLUE: "blue",
            utils.Tile.YELLOW: "yellow", 
            utils.Tile.RED: "red",
            utils.Tile.BLACK: "black",
            utils.Tile.WHITE: "white"
        }
    
    def detect_floor_line_patterns(self, state: AzulState, player_id: int) -> FloorLinePatternDetection:
        """
        Detect all floor line management patterns in the current position.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            FloorLinePatternDetection with all found patterns
        """
        risk_mitigation = self._detect_risk_mitigation_opportunities(state, player_id)
        timing_optimization = self._detect_timing_optimization_opportunities(state, player_id)
        trade_offs = self._detect_trade_off_opportunities(state, player_id)
        endgame_management = self._detect_endgame_management_opportunities(state, player_id)
        blocking_opportunities = self._detect_floor_line_blocking_opportunities(state, player_id)
        efficiency_opportunities = self._detect_efficiency_opportunities(state, player_id)
        
        total_opportunities = (len(risk_mitigation) + len(timing_optimization) + 
                             len(trade_offs) + len(endgame_management) + 
                             len(blocking_opportunities) + len(efficiency_opportunities))
        
        total_penalty_risk = self._calculate_total_penalty_risk(state, player_id)
        confidence_score = self._calculate_pattern_confidence(
            risk_mitigation + timing_optimization + trade_offs + 
            endgame_management + blocking_opportunities + efficiency_opportunities
        )
        
        return FloorLinePatternDetection(
            risk_mitigation_opportunities=risk_mitigation,
            timing_optimization_opportunities=timing_optimization,
            trade_off_opportunities=trade_offs,
            endgame_management_opportunities=endgame_management,
            blocking_opportunities=blocking_opportunities,
            efficiency_opportunities=efficiency_opportunities,
            total_opportunities=total_opportunities,
            total_penalty_risk=total_penalty_risk,
            confidence_score=confidence_score
        )
    
    def _detect_risk_mitigation_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        """Detect opportunities to mitigate floor line risk."""
        opportunities = []
        player_state = state.agents[player_id]
        
        current_floor_tiles = len(player_state.floor_tiles)
        if current_floor_tiles == 0:
            return opportunities
        
        current_penalty = sum(self.floor_penalties[:current_floor_tiles])
        
        # Assess risk level
        risk_level = self._assess_floor_line_risk(current_floor_tiles)
        
        # Look for wall placement opportunities to reduce floor line
        for row in range(player_state.GRID_SIZE):
            for col in range(player_state.GRID_SIZE):
                if player_state.grid_state[row][col] == 0:  # Empty position
                    color_needed = self._get_color_for_position(row, col)
                    tiles_available = self._count_tiles_available(state, color_needed, player_id)
                    
                    if tiles_available > 0:
                        penalty_reduction = self._calculate_penalty_reduction_potential(
                            player_state, row, col, color_needed
                        )
                        
                        urgency = self._calculate_risk_mitigation_urgency(
                            current_penalty=current_penalty,
                            penalty_reduction=penalty_reduction,
                            risk_level=risk_level,
                            tiles_available=tiles_available
                        )
                        
                        opportunities.append(FloorLineOpportunity(
                            opportunity_type="risk_mitigation",
                            target_position=(row, col),
                            target_color=color_needed,
                            current_floor_tiles=current_floor_tiles,
                            potential_penalty=current_penalty,
                            penalty_reduction=penalty_reduction,
                            urgency_score=urgency,
                            risk_assessment=risk_level,
                            description=f"Place {self.color_names.get(color_needed, f'color {color_needed}')} tile on wall to reduce floor penalty by {penalty_reduction} points",
                            move_suggestions=self._generate_risk_mitigation_moves(state, player_id, color_needed),
                            strategic_value=self._calculate_risk_mitigation_strategic_value(current_floor_tiles, penalty_reduction)
                        ))
        
        return opportunities
    
    def _detect_timing_optimization_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        """Detect opportunities for optimal floor line timing."""
        opportunities = []
        player_state = state.agents[player_id]
        
        # Analyze game phase and floor line timing
        game_phase = self._assess_game_phase(state)
        current_floor_tiles = len(player_state.floor_tiles)
        
        # Early game: Avoid floor line unless necessary
        if game_phase == "early" and current_floor_tiles > 0:
            urgency = self._calculate_timing_urgency(game_phase, current_floor_tiles, "avoid")
            opportunities.append(FloorLineOpportunity(
                opportunity_type="timing_optimization",
                target_position=None,
                target_color=None,
                current_floor_tiles=current_floor_tiles,
                potential_penalty=sum(self.floor_penalties[:current_floor_tiles]),
                penalty_reduction=0,
                urgency_score=urgency,
                risk_assessment=self._assess_floor_line_risk(current_floor_tiles),
                description="Early game floor line tiles should be cleared when possible",
                move_suggestions=self._generate_timing_optimization_moves(state, player_id),
                strategic_value=self._calculate_timing_strategic_value(game_phase, current_floor_tiles)
            ))
        
        # Mid game: Strategic floor line management
        elif game_phase == "mid" and current_floor_tiles >= 3:
            urgency = self._calculate_timing_urgency(game_phase, current_floor_tiles, "manage")
            opportunities.append(FloorLineOpportunity(
                opportunity_type="timing_optimization",
                target_position=None,
                target_color=None,
                current_floor_tiles=current_floor_tiles,
                potential_penalty=sum(self.floor_penalties[:current_floor_tiles]),
                penalty_reduction=0,
                urgency_score=urgency,
                risk_assessment=self._assess_floor_line_risk(current_floor_tiles),
                description="Mid game: Prioritize clearing floor line to avoid endgame penalties",
                move_suggestions=self._generate_timing_optimization_moves(state, player_id),
                strategic_value=self._calculate_timing_strategic_value(game_phase, current_floor_tiles)
            ))
        
        return opportunities
    
    def _detect_trade_off_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        """Detect floor line vs wall placement trade-offs."""
        opportunities = []
        player_state = state.agents[player_id]
        
        # Analyze situations where taking floor line might be strategically beneficial
        for row in range(player_state.GRID_SIZE):
            for col in range(player_state.GRID_SIZE):
                if player_state.grid_state[row][col] == 0:  # Empty position
                    color_needed = self._get_color_for_position(row, col)
                    tiles_available = self._count_tiles_available(state, color_needed, player_id)
                    
                    if tiles_available > 0:
                        # Check if this position enables valuable wall completion
                        wall_completion_value = self._calculate_wall_completion_value(player_state, row, col, color_needed)
                        
                        if wall_completion_value > 5:  # Significant wall completion value
                            current_floor_tiles = len(player_state.floor_tiles)
                            floor_penalty = sum(self.floor_penalties[:current_floor_tiles + 1])  # +1 for new tile
                            
                            net_value = wall_completion_value - floor_penalty
                            
                            if net_value > 0:  # Positive trade-off
                                urgency = self._calculate_trade_off_urgency(wall_completion_value, floor_penalty, tiles_available)
                                
                                opportunities.append(FloorLineOpportunity(
                                    opportunity_type="trade_off",
                                    target_position=(row, col),
                                    target_color=color_needed,
                                    current_floor_tiles=current_floor_tiles,
                                    potential_penalty=floor_penalty,
                                    penalty_reduction=-floor_penalty,  # Negative because we're accepting penalty
                                    urgency_score=urgency,
                                    risk_assessment=self._assess_floor_line_risk(current_floor_tiles + 1),
                                    description=f"Accept {floor_penalty} floor penalty for {wall_completion_value} wall completion value (net +{net_value})",
                                    move_suggestions=self._generate_trade_off_moves(state, player_id, color_needed),
                                    strategic_value=net_value
                                ))
        
        return opportunities
    
    def _detect_endgame_management_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        """Detect endgame floor line management opportunities."""
        opportunities = []
        player_state = state.agents[player_id]
        
        game_phase = self._assess_game_phase(state)
        if game_phase != "endgame":
            return opportunities
        
        current_floor_tiles = len(player_state.floor_tiles)
        current_penalty = sum(self.floor_penalties[:current_floor_tiles])
        
        # Endgame: Minimize floor line penalties
        if current_floor_tiles > 0:
            urgency = self._calculate_endgame_urgency(current_floor_tiles, current_penalty)
            
            opportunities.append(FloorLineOpportunity(
                opportunity_type="endgame_management",
                target_position=None,
                target_color=None,
                current_floor_tiles=current_floor_tiles,
                potential_penalty=current_penalty,
                penalty_reduction=0,
                urgency_score=urgency,
                risk_assessment=self._assess_floor_line_risk(current_floor_tiles),
                description=f"Endgame: Clear {current_floor_tiles} floor tiles to avoid {current_penalty} penalty",
                move_suggestions=self._generate_endgame_management_moves(state, player_id),
                strategic_value=self._calculate_endgame_strategic_value(current_floor_tiles, current_penalty)
            ))
        
        return opportunities
    
    def _detect_floor_line_blocking_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        """Detect opportunities to use floor line for blocking opponents."""
        opportunities = []
        
        # Analyze opponent states for blocking opportunities
        for opponent_id in range(len(state.agents)):
            if opponent_id == player_id:
                continue
            
            opponent_state = state.agents[opponent_id]
            
            # Check if opponent has valuable pattern lines that could be blocked
            for pattern_line in range(5):
                if opponent_state.lines_number[pattern_line] > 0:
                    color_in_line = opponent_state.lines_tile[pattern_line]
                    tiles_needed = pattern_line + 1 - opponent_state.lines_number[pattern_line]
                    
                    if tiles_needed <= 2:  # Close to completion
                        tiles_available = self._count_tiles_available(state, color_in_line, player_id)
                        
                        if tiles_available > 0:
                            urgency = self._calculate_blocking_urgency(tiles_needed, tiles_available)
                            
                            opportunities.append(FloorLineOpportunity(
                                opportunity_type="blocking",
                                target_position=None,
                                target_color=color_in_line,
                                current_floor_tiles=len(state.agents[player_id].floor_tiles),
                                potential_penalty=sum(self.floor_penalties[:len(state.agents[player_id].floor_tiles) + 1]),
                                penalty_reduction=0,
                                urgency_score=urgency,
                                risk_assessment="medium",
                                description=f"Block opponent's {self.color_names.get(color_in_line, f'color {color_in_line}')} pattern line completion",
                                move_suggestions=self._generate_blocking_moves(state, player_id, color_in_line),
                                strategic_value=self._calculate_blocking_strategic_value(tiles_needed, tiles_available)
                            ))
        
        return opportunities
    
    def _detect_efficiency_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        """Detect floor line efficiency optimization opportunities."""
        opportunities = []
        player_state = state.agents[player_id]
        
        # Analyze floor line efficiency patterns
        current_floor_tiles = len(player_state.floor_tiles)
        
        if current_floor_tiles > 0:
            # Check for opportunities to clear floor line efficiently
            for row in range(player_state.GRID_SIZE):
                for col in range(player_state.GRID_SIZE):
                    if player_state.grid_state[row][col] == 0:  # Empty position
                        color_needed = self._get_color_for_position(row, col)
                        tiles_available = self._count_tiles_available(state, color_needed, player_id)
                        
                        if tiles_available > 0:
                            efficiency_value = self._calculate_efficiency_value(player_state, row, col, color_needed)
                            
                            if efficiency_value > 0:
                                urgency = self._calculate_efficiency_urgency(efficiency_value, tiles_available)
                                
                                opportunities.append(FloorLineOpportunity(
                                    opportunity_type="efficiency",
                                    target_position=(row, col),
                                    target_color=color_needed,
                                    current_floor_tiles=current_floor_tiles,
                                    potential_penalty=sum(self.floor_penalties[:current_floor_tiles]),
                                    penalty_reduction=efficiency_value,
                                    urgency_score=urgency,
                                    risk_assessment=self._assess_floor_line_risk(current_floor_tiles),
                                    description=f"Efficient floor line clearing with {efficiency_value} bonus value",
                                    move_suggestions=self._generate_efficiency_moves(state, player_id, color_needed),
                                    strategic_value=efficiency_value
                                ))
        
        return opportunities
    
    # Helper methods
    def _assess_floor_line_risk(self, floor_tiles: int) -> str:
        """Assess the risk level of current floor line state."""
        if floor_tiles >= self.critical_risk_threshold:
            return "critical"
        elif floor_tiles >= self.high_risk_threshold:
            return "high"
        elif floor_tiles >= self.medium_risk_threshold:
            return "medium"
        else:
            return "low"
    
    def _assess_game_phase(self, state: AzulState) -> str:
        """Assess the current game phase."""
        total_tiles_placed = sum(
            sum(1 for row in agent.grid_state for cell in row if cell != 0)
            for agent in state.agents
        )
        
        if total_tiles_placed < 20:
            return "early"
        elif total_tiles_placed < 60:
            return "mid"
        else:
            return "endgame"
    
    def _get_color_for_position(self, row: int, col: int) -> int:
        """Get the color that should be placed at a specific wall position."""
        # Azul wall color pattern
        colors = [
            [utils.Tile.BLUE, utils.Tile.YELLOW, utils.Tile.RED, utils.Tile.BLACK, utils.Tile.WHITE],
            [utils.Tile.WHITE, utils.Tile.BLUE, utils.Tile.YELLOW, utils.Tile.RED, utils.Tile.BLACK],
            [utils.Tile.BLACK, utils.Tile.WHITE, utils.Tile.BLUE, utils.Tile.YELLOW, utils.Tile.RED],
            [utils.Tile.RED, utils.Tile.BLACK, utils.Tile.WHITE, utils.Tile.BLUE, utils.Tile.YELLOW],
            [utils.Tile.YELLOW, utils.Tile.RED, utils.Tile.BLACK, utils.Tile.WHITE, utils.Tile.BLUE]
        ]
        return colors[row][col]
    
    def _count_tiles_available(self, state: AzulState, color: int, player_id: int) -> int:
        """Count tiles of a specific color available to the player."""
        total_available = 0
        
        # Count in factories
        for factory in state.factories:
            if color in factory.tiles:
                total_available += factory.tiles[color]
        
        # Count in center pool
        if color in state.centre_pool.tiles:
            total_available += state.centre_pool.tiles[color]
        
        return total_available
    
    def _calculate_penalty_reduction_potential(self, player_state, row: int, col: int, color: int) -> int:
        """Calculate potential penalty reduction from placing a tile."""
        current_floor_tiles = len(player_state.floor_tiles)
        current_penalty = sum(self.floor_penalties[:current_floor_tiles])
        
        # Simulate placing tile on wall (removing from floor)
        new_floor_tiles = max(0, current_floor_tiles - 1)
        new_penalty = sum(self.floor_penalties[:new_floor_tiles])
        
        # Return the absolute value of points saved (penalty reduction)
        return abs(current_penalty - new_penalty)
    
    def _calculate_risk_mitigation_urgency(self, current_penalty: int, penalty_reduction: int, 
                                         risk_level: str, tiles_available: int) -> float:
        """Calculate urgency for risk mitigation opportunities."""
        # Base urgency on absolute penalty value and risk level
        base_urgency = abs(current_penalty) / 5.0  # Normalize to 0-1 scale
        
        # Adjust for risk level
        risk_multiplier = {"critical": 2.0, "high": 1.5, "medium": 1.2, "low": 1.0}
        base_urgency *= risk_multiplier.get(risk_level, 1.0)
        
        # Adjust for tile availability
        if tiles_available > 0:
            base_urgency *= min(1.0, tiles_available / 3.0)  # Diminishing returns
        
        return min(10.0, base_urgency * 10.0)  # Scale to 0-10
    
    def _calculate_timing_urgency(self, game_phase: str, floor_tiles: int, action_type: str) -> float:
        """Calculate urgency for timing optimization opportunities."""
        if game_phase == "early":
            return min(10.0, floor_tiles * 2.0)  # Higher urgency for early game floor tiles
        elif game_phase == "mid":
            return min(10.0, floor_tiles * 1.5)  # Medium urgency for mid game
        else:  # endgame
            return min(10.0, floor_tiles * 3.0)  # Highest urgency for endgame
    
    def _calculate_trade_off_urgency(self, wall_value: int, floor_penalty: int, tiles_available: int) -> float:
        """Calculate urgency for trade-off opportunities."""
        net_value = wall_value - floor_penalty
        if net_value <= 0:
            return 0.0
        
        base_urgency = net_value / 10.0
        if tiles_available > 0:
            base_urgency *= min(1.0, tiles_available / 2.0)
        
        return min(10.0, base_urgency * 10.0)
    
    def _calculate_endgame_urgency(self, floor_tiles: int, penalty: int) -> float:
        """Calculate urgency for endgame management opportunities."""
        return min(10.0, (floor_tiles + abs(penalty)) * 1.5)
    
    def _calculate_blocking_urgency(self, tiles_needed: int, tiles_available: int) -> float:
        """Calculate urgency for blocking opportunities."""
        if tiles_needed <= 0 or tiles_available <= 0:
            return 0.0
        
        # Higher urgency when opponent is close to completion
        completion_urgency = (3 - tiles_needed) / 3.0  # 1.0 when 1 tile needed, 0.0 when 3+ needed
        
        # Higher urgency when we have tiles available
        availability_urgency = min(1.0, tiles_available / 2.0)
        
        return min(10.0, (completion_urgency + availability_urgency) * 5.0)
    
    def _calculate_efficiency_urgency(self, efficiency_value: int, tiles_available: int) -> float:
        """Calculate urgency for efficiency opportunities."""
        if efficiency_value <= 0 or tiles_available <= 0:
            return 0.0
        
        base_urgency = efficiency_value / 10.0
        if tiles_available > 0:
            base_urgency *= min(1.0, tiles_available / 2.0)
        
        return min(10.0, base_urgency * 10.0)
    
    def _calculate_wall_completion_value(self, player_state, row: int, col: int, color: int) -> int:
        """Calculate the value of completing a wall position."""
        # Simulate placing the tile
        original_value = player_state.grid_state[row][col]
        player_state.grid_state[row][col] = color
        
        # Calculate completion bonuses
        row_completion = self._check_row_completion(player_state, row)
        col_completion = self._check_column_completion(player_state, col)
        color_completion = self._check_color_completion(player_state, color)
        
        # Restore original state
        player_state.grid_state[row][col] = original_value
        
        return row_completion + col_completion + color_completion
    
    def _check_row_completion(self, player_state, row: int) -> int:
        """Check if a row is completed and return bonus value."""
        if all(cell != 0 for cell in player_state.grid_state[row]):
            return 2  # Row completion bonus
        return 0
    
    def _check_column_completion(self, player_state, col: int) -> int:
        """Check if a column is completed and return bonus value."""
        if all(player_state.grid_state[row][col] != 0 for row in range(5)):
            return 7  # Column completion bonus
        return 0
    
    def _check_color_completion(self, player_state, color: int) -> int:
        """Check if a color set is completed and return bonus value."""
        color_count = sum(1 for row in player_state.grid_state for cell in row if cell == color)
        if color_count == 5:
            return 10  # Color set completion bonus
        return 0
    
    def _calculate_efficiency_value(self, player_state, row: int, col: int, color: int) -> int:
        """Calculate the efficiency value of a wall placement."""
        # This would include factors like:
        # - Pattern line completion bonuses
        # - Wall completion bonuses
        # - Strategic positioning value
        # For now, return a simple heuristic
        return 2  # Base efficiency value
    
    def _calculate_total_penalty_risk(self, state: AzulState, player_id: int) -> int:
        """Calculate total penalty risk across all players."""
        total_risk = 0
        for agent in state.agents:
            floor_tiles = len(agent.floor_tiles)
            total_risk += abs(sum(self.floor_penalties[:floor_tiles]))
        return total_risk
    
    def _calculate_pattern_confidence(self, opportunities: List[FloorLineOpportunity]) -> float:
        """Calculate confidence score for pattern detection."""
        if not opportunities:
            return 0.0
        
        # Average urgency scores as confidence indicator
        avg_urgency = sum(opp.urgency_score for opp in opportunities) / len(opportunities)
        return min(1.0, avg_urgency / 10.0)
    
    # Strategic value calculations
    def _calculate_risk_mitigation_strategic_value(self, floor_tiles: int, penalty_reduction: int) -> float:
        """Calculate strategic value of risk mitigation."""
        return penalty_reduction * (1 + floor_tiles * 0.2)  # Higher value for more floor tiles
    
    def _calculate_timing_strategic_value(self, game_phase: str, floor_tiles: int) -> float:
        """Calculate strategic value of timing optimization."""
        phase_multiplier = {"early": 1.5, "mid": 1.0, "endgame": 2.0}
        return floor_tiles * phase_multiplier.get(game_phase, 1.0)
    
    def _calculate_endgame_strategic_value(self, floor_tiles: int, penalty: int) -> float:
        """Calculate strategic value of endgame management."""
        return penalty * 2.0  # Higher strategic value in endgame
    
    def _calculate_blocking_strategic_value(self, tiles_needed: int, tiles_available: int) -> float:
        """Calculate strategic value of blocking opportunities."""
        return (3 - tiles_needed) * tiles_available  # Higher value when opponent is close to completion
    
    # Move generation methods
    def _generate_risk_mitigation_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate moves for risk mitigation."""
        moves = []
        tiles_available = self._count_tiles_available(state, color, player_id)
        
        if tiles_available > 0:
            moves.append({
                "type": "wall_placement",
                "color": color,
                "description": f"Place {self.color_names.get(color, f'color {color}')} tile on wall to reduce floor penalty",
                "priority": "high"
            })
        
        return moves
    
    def _generate_timing_optimization_moves(self, state: AzulState, player_id: int) -> List[Dict]:
        """Generate moves for timing optimization."""
        return [{
            "type": "floor_line_clearance",
            "description": "Prioritize clearing floor line tiles",
            "priority": "medium"
        }]
    
    def _generate_trade_off_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate moves for trade-off opportunities."""
        return [{
            "type": "strategic_floor_acceptance",
            "color": color,
            "description": f"Accept floor penalty for significant wall completion value",
            "priority": "high"
        }]
    
    def _generate_endgame_management_moves(self, state: AzulState, player_id: int) -> List[Dict]:
        """Generate moves for endgame management."""
        return [{
            "type": "endgame_floor_clearance",
            "description": "Clear floor line to minimize endgame penalties",
            "priority": "critical"
        }]
    
    def _generate_blocking_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate moves for blocking opportunities."""
        return [{
            "type": "opponent_blocking",
            "color": color,
            "description": f"Take {self.color_names.get(color, f'color {color}')} tiles to block opponent completion",
            "priority": "high"
        }]
    
    def _generate_efficiency_moves(self, state: AzulState, player_id: int, color: int) -> List[Dict]:
        """Generate moves for efficiency opportunities."""
        return [{
            "type": "efficient_placement",
            "color": color,
            "description": f"Place {self.color_names.get(color, f'color {color}')} tile efficiently",
            "priority": "medium"
        }] 