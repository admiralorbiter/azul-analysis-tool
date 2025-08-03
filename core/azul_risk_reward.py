"""
Azul Risk/Reward Analysis - Phase 2.4 Implementation

This module provides risk/reward analysis for Azul positions:
- Floor line risk assessment
- Blocking risk evaluation
- Timing risk analysis
- Scoring risk calculation
- Comprehensive strategic decision analysis

Integrates with existing pattern detection system for comprehensive analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState


@dataclass
class RiskRewardScenario:
    """Represents a risk/reward scenario analysis."""
    scenario_type: str  # "floor_risk", "blocking_risk", "timing_risk", "scoring_risk"
    expected_value: float
    risk_level: str  # "low", "medium", "high"
    urgency_score: float
    confidence: float
    description: str
    move_suggestions: List[str]


class RiskRewardAnalyzer:
    """
    Risk/reward analysis for strategic decision making.
    
    Features:
    - Floor line risk assessment
    - Blocking risk evaluation
    - Timing risk analysis
    - Scoring risk calculation
    """
    
    def __init__(self):
        # Risk analysis thresholds
        self.floor_risk_threshold = 0.6
        self.blocking_risk_threshold = 0.5
        self.timing_risk_threshold = 0.7
        self.scoring_risk_threshold = 0.6
        
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
    
    def analyze_scenarios(self, state: AzulState, player_id: int) -> List[RiskRewardScenario]:
        """
        Analyze risk/reward scenarios for strategic decision making.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            List of risk/reward scenarios
        """
        scenarios = []
        
        # Floor line risk analysis
        scenarios.extend(self._analyze_floor_line_risks(state, player_id))
        
        # Blocking risk analysis
        scenarios.extend(self._analyze_blocking_risks(state, player_id))
        
        # Timing risk analysis
        scenarios.extend(self._analyze_timing_risks(state, player_id))
        
        # Scoring risk analysis
        scenarios.extend(self._analyze_scoring_risks(state, player_id))
        
        return scenarios
    
    def _analyze_floor_line_risks(self, state: AzulState, player_id: int) -> List[RiskRewardScenario]:
        """Analyze floor line risks and mitigation strategies."""
        scenarios = []
        
        player_state = state.agents[player_id]
        floor_tiles = len(player_state.floor_tiles)
        
        if floor_tiles > 0:
            # Calculate current penalty
            current_penalty = self._calculate_floor_penalty(floor_tiles)
            
            # Analyze potential future penalties
            future_penalty_risk = self._assess_future_floor_penalty_risk(player_state, state, player_id)
            
            # Calculate expected value (negative due to penalty)
            expected_value = -(current_penalty + future_penalty_risk)
            
            # Generate mitigation strategies
            mitigation_moves = self._generate_floor_mitigation_moves(state, player_id)
            
            scenarios.append(RiskRewardScenario(
                scenario_type="floor_risk",
                expected_value=expected_value,
                risk_level=self._assess_floor_risk_level(floor_tiles),
                urgency_score=self._calculate_floor_risk_urgency(floor_tiles, future_penalty_risk),
                confidence=self._calculate_floor_risk_confidence(floor_tiles, state, player_id),
                description=f"Floor line penalty: {current_penalty} points, future risk: {future_penalty_risk:.1f}",
                move_suggestions=mitigation_moves
            ))
        
        return scenarios
    
    def _analyze_blocking_risks(self, state: AzulState, player_id: int) -> List[RiskRewardScenario]:
        """Analyze blocking risks and opportunities."""
        scenarios = []
        
        # Analyze opponent blocking threats
        opponent_threats = self._analyze_opponent_blocking_threats(state, player_id)
        
        for threat in opponent_threats:
            if threat['severity'] > self.blocking_risk_threshold:
                scenarios.append(RiskRewardScenario(
                    scenario_type="blocking_risk",
                    expected_value=threat['mitigation_value'],
                    risk_level=threat['level'],
                    urgency_score=threat['urgency'],
                    confidence=threat['confidence'],
                    description=f"Blocking risk: {threat['description']}",
                    move_suggestions=threat['mitigation_moves']
                ))
        
        return scenarios
    
    def _analyze_timing_risks(self, state: AzulState, player_id: int) -> List[RiskRewardScenario]:
        """Analyze timing risks in strategic decisions."""
        scenarios = []
        
        # Analyze game phase timing
        game_phase = self._assess_game_phase(state)
        timing_risks = self._analyze_timing_risks_by_phase(state, player_id, game_phase)
        
        for risk in timing_risks:
            if risk['severity'] > self.timing_risk_threshold:
                scenarios.append(RiskRewardScenario(
                    scenario_type="timing_risk",
                    expected_value=risk['value'],
                    risk_level=risk['level'],
                    urgency_score=risk['urgency'],
                    confidence=risk['confidence'],
                    description=f"Timing risk: {risk['description']}",
                    move_suggestions=risk['mitigation_moves']
                ))
        
        return scenarios
    
    def _analyze_scoring_risks(self, state: AzulState, player_id: int) -> List[RiskRewardScenario]:
        """Analyze scoring risks and opportunities."""
        scenarios = []
        
        player_state = state.agents[player_id]
        
        # Analyze scoring opportunity risks
        scoring_risks = self._analyze_scoring_opportunity_risks(player_state, state, player_id)
        
        for risk in scoring_risks:
            if risk['severity'] > self.scoring_risk_threshold:
                scenarios.append(RiskRewardScenario(
                    scenario_type="scoring_risk",
                    expected_value=risk['value'],
                    risk_level=risk['level'],
                    urgency_score=risk['urgency'],
                    confidence=risk['confidence'],
                    description=f"Scoring risk: {risk['description']}",
                    move_suggestions=risk['mitigation_moves']
                ))
        
        return scenarios
    
    def _calculate_floor_penalty(self, floor_tiles: int) -> int:
        """Calculate floor line penalty."""
        penalties = [-1, -1, -2, -2, -2, -3, -3]
        
        if floor_tiles <= len(penalties):
            return penalties[floor_tiles - 1]
        else:
            return penalties[-1]
    
    def _assess_future_floor_penalty_risk(self, player_state, state: AzulState, player_id: int) -> float:
        """Assess risk of future floor line penalties."""
        risk = 0.0
        
        # Analyze pattern line overflow risk
        for pattern_line in range(5):
            current_tiles = player_state.lines_number[pattern_line]
            max_capacity = pattern_line + 1
            
            if current_tiles > 0:
                # Risk of overflow if taking more tiles
                overflow_risk = self._calculate_overflow_risk(current_tiles, max_capacity, state, player_id)
                risk += overflow_risk
        
        return risk
    
    def _calculate_overflow_risk(self, current_tiles: int, max_capacity: int, state: AzulState, player_id: int) -> float:
        """Calculate risk of pattern line overflow."""
        remaining_capacity = max_capacity - current_tiles
        
        if remaining_capacity <= 0:
            return 2.0  # High risk of overflow
        
        # Check available tiles that could cause overflow
        available_tiles = self._count_available_tiles_for_pattern_line(state, player_id)
        
        if available_tiles > remaining_capacity:
            return min((available_tiles - remaining_capacity) * 0.5, 2.0)
        
        return 0.0
    
    def _count_available_tiles_for_pattern_line(self, state: AzulState, player_id: int) -> int:
        """Count tiles available for pattern line placement."""
        total_available = 0
        
        # Count tiles in factories and center
        for factory in state.factories:
            total_available += factory.total
        
        total_available += state.centre_pool.total
        
        return total_available
    
    def _assess_floor_risk_level(self, floor_tiles: int) -> str:
        """Assess floor line risk level."""
        if floor_tiles >= 5:
            return "high"
        elif floor_tiles >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_floor_risk_urgency(self, floor_tiles: int, future_risk: float) -> float:
        """Calculate urgency for floor line risk."""
        urgency = floor_tiles * 1.0
        
        # Add urgency for future risk
        urgency += future_risk * 2.0
        
        return min(urgency, 10.0)
    
    def _calculate_floor_risk_confidence(self, floor_tiles: int, state: AzulState, player_id: int) -> float:
        """Calculate confidence in floor line risk assessment."""
        confidence = 0.7  # Base confidence
        
        # Higher confidence for more floor tiles
        if floor_tiles >= 3:
            confidence += 0.2
        
        # Higher confidence if pattern lines are near capacity
        player_state = state.agents[player_id]
        for pattern_line in range(5):
            if player_state.lines_number[pattern_line] >= pattern_line:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_floor_mitigation_moves(self, state: AzulState, player_id: int) -> List[str]:
        """Generate moves to mitigate floor line risk."""
        moves = []
        
        player_state = state.agents[player_id]
        
        # Suggest completing pattern lines
        for pattern_line in range(5):
            if player_state.lines_number[pattern_line] > 0:
                moves.append(f"Complete pattern line {pattern_line + 1} to reduce floor penalty")
        
        # Suggest wall placements
        moves.append("Place tiles on wall to avoid floor line penalties")
        
        # Suggest conservative tile taking
        moves.append("Take tiles conservatively to avoid overflow")
        
        return moves
    
    def _analyze_opponent_blocking_threats(self, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze opponent blocking threats."""
        threats = []
        
        for opponent_id in range(len(state.agents)):
            if opponent_id == player_id:
                continue
            
            opponent_state = state.agents[opponent_id]
            
            # Analyze opponent's near-complete rows/columns
            for row in range(5):
                if self._is_opponent_row_near_completion(opponent_state, row):
                    threat = self._analyze_row_blocking_threat(opponent_id, row, state, player_id)
                    if threat:
                        threats.append(threat)
            
            for col in range(5):
                if self._is_opponent_column_near_completion(opponent_state, col):
                    threat = self._analyze_column_blocking_threat(opponent_id, col, state, player_id)
                    if threat:
                        threats.append(threat)
        
        return threats
    
    def _is_opponent_row_near_completion(self, opponent_state, row: int) -> bool:
        """Check if opponent's row is near completion."""
        filled_positions = sum(opponent_state.grid_state[row])
        return filled_positions >= 3
    
    def _is_opponent_column_near_completion(self, opponent_state, col: int) -> bool:
        """Check if opponent's column is near completion."""
        filled_positions = sum(opponent_state.grid_state[row][col] for row in range(5))
        return filled_positions >= 3
    
    def _analyze_row_blocking_threat(self, opponent_id: int, row: int, state: AzulState, player_id: int) -> Optional[Dict]:
        """Analyze blocking threat for opponent's row completion."""
        # Find color needed for row completion
        needed_color = self._get_color_needed_for_row_completion(state.agents[opponent_id], row)
        
        if needed_color is None:
            return None
        
        # Check if we can block this color
        available_tiles = self._count_tiles_of_color(needed_color, state)
        
        if available_tiles > 0:
            return {
                'severity': 0.8,  # High severity for row completion
                'mitigation_value': 2.0,  # Value of blocking
                'level': 'high',
                'urgency': 8.0,
                'confidence': 0.9,
                'description': f"Opponent {opponent_id + 1} needs {self.color_names[needed_color]} for row {row + 1}",
                'mitigation_moves': [f"Take {self.color_names[needed_color]} tiles to block opponent {opponent_id + 1}"]
            }
        
        return None
    
    def _analyze_column_blocking_threat(self, opponent_id: int, col: int, state: AzulState, player_id: int) -> Optional[Dict]:
        """Analyze blocking threat for opponent's column completion."""
        # Find color needed for column completion
        needed_color = self._get_color_needed_for_column_completion(state.agents[opponent_id], col)
        
        if needed_color is None:
            return None
        
        # Check if we can block this color
        available_tiles = self._count_tiles_of_color(needed_color, state)
        
        if available_tiles > 0:
            return {
                'severity': 0.7,  # Medium severity for column completion
                'mitigation_value': 1.5,  # Value of blocking
                'level': 'medium',
                'urgency': 6.0,
                'confidence': 0.8,
                'description': f"Opponent {opponent_id + 1} needs {self.color_names[needed_color]} for column {col + 1}",
                'mitigation_moves': [f"Take {self.color_names[needed_color]} tiles to block opponent {opponent_id + 1}"]
            }
        
        return None
    
    def _get_color_needed_for_row_completion(self, opponent_state, row: int) -> Optional[int]:
        """Get color needed for opponent's row completion."""
        for col in range(5):
            if opponent_state.grid_state[row][col] == 0:  # Empty position
                return self._get_color_for_position(row, col)
        return None
    
    def _get_color_needed_for_column_completion(self, opponent_state, col: int) -> Optional[int]:
        """Get color needed for opponent's column completion."""
        for row in range(5):
            if opponent_state.grid_state[row][col] == 0:  # Empty position
                return self._get_color_for_position(row, col)
        return None
    
    def _count_tiles_of_color(self, color: int, state: AzulState) -> int:
        """Count tiles of a specific color available."""
        count = 0
        
        # Count in factories
        for factory in state.factories:
            count += factory.count(color)
        
        # Count in center
        count += state.center.count(color)
        
        return count
    
    def _assess_game_phase(self, state: AzulState) -> str:
        """Assess current game phase."""
        total_tiles_remaining = sum(factory.total for factory in state.factories)
        
        if total_tiles_remaining > 80:
            return "early"
        elif total_tiles_remaining > 40:
            return "mid"
        else:
            return "late"
    
    def _analyze_timing_risks_by_phase(self, state: AzulState, player_id: int, game_phase: str) -> List[Dict]:
        """Analyze timing risks based on game phase."""
        risks = []
        
        if game_phase == "early":
            # Early game timing risks
            risks.extend(self._analyze_early_game_timing_risks(state, player_id))
        elif game_phase == "mid":
            # Mid game timing risks
            risks.extend(self._analyze_mid_game_timing_risks(state, player_id))
        else:
            # Late game timing risks
            risks.extend(self._analyze_late_game_timing_risks(state, player_id))
        
        return risks
    
    def _analyze_early_game_timing_risks(self, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze early game timing risks."""
        risks = []
        
        # Risk of falling behind in setup
        setup_risk = self._assess_setup_timing_risk(state, player_id)
        
        if setup_risk > 0:
            risks.append({
                'severity': setup_risk,
                'value': -setup_risk,
                'level': 'medium',
                'urgency': 5.0,
                'confidence': 0.7,
                'description': "Risk of falling behind in early setup",
                'mitigation_moves': ["Focus on efficient tile placement", "Build foundation for scoring"]
            })
        
        return risks
    
    def _analyze_mid_game_timing_risks(self, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze mid game timing risks."""
        risks = []
        
        # Risk of missing scoring opportunities
        scoring_timing_risk = self._assess_scoring_timing_risk(state, player_id)
        
        if scoring_timing_risk > 0:
            risks.append({
                'severity': scoring_timing_risk,
                'value': -scoring_timing_risk,
                'level': 'high',
                'urgency': 7.0,
                'confidence': 0.8,
                'description': "Risk of missing mid-game scoring opportunities",
                'mitigation_moves': ["Prioritize high-scoring moves", "Complete partial rows/columns"]
            })
        
        return risks
    
    def _analyze_late_game_timing_risks(self, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze late game timing risks."""
        risks = []
        
        # Risk of endgame tile scarcity
        endgame_timing_risk = self._assess_endgame_timing_risk(state, player_id)
        
        if endgame_timing_risk > 0:
            risks.append({
                'severity': endgame_timing_risk,
                'value': -endgame_timing_risk,
                'level': 'high',
                'urgency': 9.0,
                'confidence': 0.9,
                'description': "Risk of tile scarcity in endgame",
                'mitigation_moves': ["Conserve critical tiles", "Complete high-priority placements"]
            })
        
        return risks
    
    def _assess_setup_timing_risk(self, state: AzulState, player_id: int) -> float:
        """Assess risk of falling behind in early setup."""
        player_state = state.agents[player_id]
        
        # Risk based on wall completion progress
        total_wall_tiles = sum(sum(row) for row in player_state.grid_state)
        
        if total_wall_tiles < 5:
            return 0.8  # High risk if very few tiles placed
        elif total_wall_tiles < 10:
            return 0.4  # Medium risk
        else:
            return 0.0  # Low risk
    
    def _assess_scoring_timing_risk(self, state: AzulState, player_id: int) -> float:
        """Assess risk of missing scoring opportunities."""
        player_state = state.agents[player_id]
        
        # Risk based on near-complete rows/columns
        near_complete_count = 0
        
        for row in range(5):
            if sum(player_state.grid_state[row]) >= 3:
                near_complete_count += 1
        
        for col in range(5):
            if sum(player_state.grid_state[row][col] for row in range(5)) >= 3:
                near_complete_count += 1
        
        if near_complete_count >= 3:
            return 0.9  # High risk if many near-complete lines
        elif near_complete_count >= 1:
            return 0.5  # Medium risk
        else:
            return 0.0  # Low risk
    
    def _assess_endgame_timing_risk(self, state: AzulState, player_id: int) -> float:
        """Assess risk of tile scarcity in endgame."""
        remaining_tiles = sum(factory.total for factory in state.factories) + state.centre_pool.total
        
        if remaining_tiles <= 10:
            return 0.9  # High risk if very few tiles remain
        elif remaining_tiles <= 20:
            return 0.6  # Medium risk
        else:
            return 0.0  # Low risk
    
    def _analyze_scoring_opportunity_risks(self, player_state, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze risks in scoring opportunities."""
        risks = []
        
        # Analyze wall completion risks
        wall_completion_risks = self._analyze_wall_completion_risks(player_state, state, player_id)
        risks.extend(wall_completion_risks)
        
        # Analyze pattern line overflow risks
        pattern_line_risks = self._analyze_pattern_line_overflow_risks(player_state, state, player_id)
        risks.extend(pattern_line_risks)
        
        return risks
    
    def _analyze_wall_completion_risks(self, player_state, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze risks in wall completion opportunities."""
        risks = []
        
        # Analyze row completion risks
        for row in range(5):
            filled_positions = sum(player_state.grid_state[row])
            if filled_positions >= 3:  # Near completion
                risk = self._analyze_row_completion_risk(player_state, row, state, player_id)
                if risk:
                    risks.append(risk)
        
        # Analyze column completion risks
        for col in range(5):
            filled_positions = sum(player_state.grid_state[row][col] for row in range(5))
            if filled_positions >= 3:  # Near completion
                risk = self._analyze_column_completion_risk(player_state, col, state, player_id)
                if risk:
                    risks.append(risk)
        
        return risks
    
    def _analyze_row_completion_risk(self, player_state, row: int, state: AzulState, player_id: int) -> Optional[Dict]:
        """Analyze risk in row completion opportunity."""
        needed_positions = []
        
        for col in range(5):
            if player_state.grid_state[row][col] == 0:  # Empty position
                needed_positions.append((row, col))
        
        if len(needed_positions) == 0:
            return None
        
        # Check tile availability
        available_tiles = self._count_available_tiles_for_positions(needed_positions, state)
        
        if available_tiles < len(needed_positions):
            return {
                'severity': 0.8,
                'value': -2.0,  # Negative value due to risk
                'level': 'high',
                'urgency': 7.0,
                'confidence': 0.8,
                'description': f"Row {row + 1} completion at risk - insufficient tiles",
                'mitigation_moves': ["Prioritize available tiles", "Consider alternative strategies"]
            }
        
        return None
    
    def _analyze_column_completion_risk(self, player_state, col: int, state: AzulState, player_id: int) -> Optional[Dict]:
        """Analyze risk in column completion opportunity."""
        needed_positions = []
        
        for row in range(5):
            if player_state.grid_state[row][col] == 0:  # Empty position
                needed_positions.append((row, col))
        
        if len(needed_positions) == 0:
            return None
        
        # Check tile availability
        available_tiles = self._count_available_tiles_for_positions(needed_positions, state)
        
        if available_tiles < len(needed_positions):
            return {
                'severity': 0.7,
                'value': -1.5,  # Negative value due to risk
                'level': 'medium',
                'urgency': 6.0,
                'confidence': 0.7,
                'description': f"Column {col + 1} completion at risk - insufficient tiles",
                'mitigation_moves': ["Prioritize available tiles", "Consider alternative strategies"]
            }
        
        return None
    
    def _count_available_tiles_for_positions(self, positions: List[Tuple[int, int]], state: AzulState) -> int:
        """Count tiles available for specific positions."""
        available_tiles = 0
        
        for row, col in positions:
            color = self._get_color_for_position(row, col)
            available_tiles += self._count_tiles_of_color(color, state)
        
        return available_tiles
    
    def _analyze_pattern_line_overflow_risks(self, player_state, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze risks of pattern line overflow."""
        risks = []
        
        for pattern_line in range(5):
            current_tiles = player_state.lines_number[pattern_line]
            max_capacity = pattern_line + 1
            
            if current_tiles > 0:
                overflow_risk = self._calculate_pattern_line_overflow_risk(current_tiles, max_capacity, state, player_id)
                
                if overflow_risk > 0:
                    risks.append({
                        'severity': overflow_risk,
                        'value': -overflow_risk,
                        'level': 'high' if overflow_risk > 0.5 else 'medium',
                        'urgency': overflow_risk * 8.0,
                        'confidence': 0.9,
                        'description': f"Pattern line {pattern_line + 1} overflow risk",
                        'mitigation_moves': ["Complete pattern line", "Take tiles conservatively"]
                    })
        
        return risks
    
    def _calculate_pattern_line_overflow_risk(self, current_tiles: int, max_capacity: int, state: AzulState, player_id: int) -> float:
        """Calculate risk of pattern line overflow."""
        remaining_capacity = max_capacity - current_tiles
        
        if remaining_capacity <= 0:
            return 1.0  # Certain overflow
        
        # Check if taking more tiles would cause overflow
        available_tiles = self._count_available_tiles_for_pattern_line(state, player_id)
        
        if available_tiles > remaining_capacity:
            return min((available_tiles - remaining_capacity) / available_tiles, 1.0)
        
        return 0.0
    
    def _get_color_for_position(self, row: int, col: int) -> int:
        """Get the color that should be placed at a wall position."""
        # Azul wall color pattern
        wall_colors = [
            [0, 1, 2, 3, 4],  # Row 0: Blue, Yellow, Red, Black, White
            [1, 2, 3, 4, 0],  # Row 1: Yellow, Red, Black, White, Blue
            [2, 3, 4, 0, 1],  # Row 2: Red, Black, White, Blue, Yellow
            [3, 4, 0, 1, 2],  # Row 3: Black, White, Blue, Yellow, Red
            [4, 0, 1, 2, 3]   # Row 4: White, Blue, Yellow, Red, Black
        ]
        return wall_colors[row][col] 