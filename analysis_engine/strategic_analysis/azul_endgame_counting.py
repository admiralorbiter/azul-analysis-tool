"""
Azul Endgame Counting Analysis - Phase 2.4 Implementation

This module provides endgame counting analysis for Azul positions:
- Tile conservation scenarios
- Scoring potential optimization
- Move sequence optimization
- Endgame risk assessment
- Precise tile counting and planning

Integrates with existing pattern detection system for comprehensive analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from core import azul_utils as utils
from core.azul_model import AzulState


@dataclass
class EndgameScenario:
    """Represents an endgame scenario analysis."""
    scenario_type: str  # "conservation", "optimization", "blocking", "timing"
    remaining_tiles: Dict[str, int]  # Color -> count
    scoring_potential: float
    optimal_sequence: List[str]
    risk_level: str  # "low", "medium", "high"
    urgency_score: float
    confidence: float
    description: str


class EndgameCountingDetector:
    """
    Endgame scenario analysis with precise counting.
    
    Features:
    - Tile conservation analysis
    - Scoring potential calculation
    - Move sequence optimization
    - Endgame risk assessment
    """
    
    def __init__(self):
        # Endgame analysis thresholds
        self.conservation_threshold = 0.6
        self.optimization_threshold = 0.7
        self.blocking_threshold = 0.5
        self.timing_threshold = 0.6
        
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
    
    def analyze_scenarios(self, state: AzulState, player_id: int) -> List[EndgameScenario]:
        """
        Analyze endgame scenarios with precise counting.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            List of endgame scenarios
        """
        scenarios = []
        
        # Tile conservation analysis
        scenarios.extend(self._analyze_tile_conservation(state, player_id))
        
        # Scoring potential calculation
        scenarios.extend(self._analyze_scoring_potential(state, player_id))
        
        # Move sequence optimization
        scenarios.extend(self._analyze_move_sequences(state, player_id))
        
        # Endgame risk assessment
        scenarios.extend(self._analyze_endgame_risks(state, player_id))
        
        return scenarios
    
    def _analyze_tile_conservation(self, state: AzulState, player_id: int) -> List[EndgameScenario]:
        """Analyze tile conservation strategies."""
        scenarios = []
        
        # Count remaining tiles
        remaining_tiles = self._count_remaining_tiles(state)
        
        # Analyze conservation opportunities
        if self._is_conservation_opportunity(remaining_tiles, state, player_id):
            scoring_potential = self._calculate_conservation_potential(remaining_tiles, state, player_id)
            optimal_sequence = self._generate_conservation_sequence(remaining_tiles, state, player_id)
            urgency_score = self._calculate_conservation_urgency(remaining_tiles, state, player_id)
            
            scenarios.append(EndgameScenario(
                scenario_type="conservation",
                remaining_tiles=remaining_tiles,
                scoring_potential=scoring_potential,
                optimal_sequence=optimal_sequence,
                risk_level=self._assess_conservation_risk(remaining_tiles, state, player_id),
                urgency_score=urgency_score,
                confidence=self._calculate_conservation_confidence(remaining_tiles, state, player_id),
                description="Tile conservation opportunity detected"
            ))
        
        return scenarios
    
    def _analyze_scoring_potential(self, state: AzulState, player_id: int) -> List[EndgameScenario]:
        """Analyze scoring potential in endgame."""
        scenarios = []
        
        player_state = state.agents[player_id]
        
        # Analyze wall completion opportunities
        wall_opportunities = self._analyze_wall_completion_opportunities(player_state, state, player_id)
        
        for opportunity in wall_opportunities:
            if opportunity['potential'] > self.optimization_threshold:
                scenarios.append(EndgameScenario(
                    scenario_type="optimization",
                    remaining_tiles=self._count_remaining_tiles(state),
                    scoring_potential=opportunity['potential'],
                    optimal_sequence=opportunity['sequence'],
                    risk_level=self._assess_optimization_risk(opportunity),
                    urgency_score=opportunity['urgency'],
                    confidence=opportunity['confidence'],
                    description=f"Scoring optimization: {opportunity['description']}"
                ))
        
        return scenarios
    
    def _analyze_move_sequences(self, state: AzulState, player_id: int) -> List[EndgameScenario]:
        """Analyze optimal move sequences for endgame."""
        scenarios = []
        
        # Generate optimal move sequences
        move_sequences = self._generate_optimal_move_sequences(state, player_id)
        
        for sequence in move_sequences:
            if sequence['value'] > self.timing_threshold:
                scenarios.append(EndgameScenario(
                    scenario_type="timing",
                    remaining_tiles=self._count_remaining_tiles(state),
                    scoring_potential=sequence['value'],
                    optimal_sequence=sequence['moves'],
                    risk_level=self._assess_sequence_risk(sequence),
                    urgency_score=sequence['urgency'],
                    confidence=sequence['confidence'],
                    description=f"Optimal move sequence: {sequence['description']}"
                ))
        
        return scenarios
    
    def _analyze_endgame_risks(self, state: AzulState, player_id: int) -> List[EndgameScenario]:
        """Analyze endgame risks and mitigation strategies."""
        scenarios = []
        
        # Analyze floor line risks
        floor_risks = self._analyze_floor_line_risks(state, player_id)
        
        for risk in floor_risks:
            if risk['severity'] > self.blocking_threshold:
                scenarios.append(EndgameScenario(
                    scenario_type="blocking",
                    remaining_tiles=self._count_remaining_tiles(state),
                    scoring_potential=risk['mitigation_value'],
                    optimal_sequence=risk['mitigation_sequence'],
                    risk_level=risk['level'],
                    urgency_score=risk['urgency'],
                    confidence=risk['confidence'],
                    description=f"Endgame risk mitigation: {risk['description']}"
                ))
        
        return scenarios
    
    def _count_remaining_tiles(self, state: AzulState) -> Dict[str, int]:
        """Count remaining tiles by color."""
        remaining_tiles = {}
        
        # Count tiles in factories
        for factory in state.factories:
            for color, count in factory.tiles.items():
                if count > 0:
                    color_name = self.color_names[color]
                    remaining_tiles[color_name] = remaining_tiles.get(color_name, 0) + count
        
        # Count tiles in center
        for color, count in state.centre_pool.tiles.items():
            if count > 0:
                color_name = self.color_names[color]
                remaining_tiles[color_name] = remaining_tiles.get(color_name, 0) + count
        
        return remaining_tiles
    
    def _is_conservation_opportunity(self, remaining_tiles: Dict[str, int], state: AzulState, player_id: int) -> bool:
        """Check if there's a tile conservation opportunity."""
        total_remaining = sum(remaining_tiles.values())
        
        # Conservation opportunity if few tiles remain
        if total_remaining <= 20:
            return True
        
        # Conservation opportunity if critical colors are scarce
        player_state = state.agents[player_id]
        critical_colors = self._identify_critical_colors(player_state)
        
        for color_name, count in remaining_tiles.items():
            if color_name in critical_colors and count <= 3:
                return True
        
        return False
    
    def _identify_critical_colors(self, player_state) -> List[str]:
        """Identify colors critical for the player's position."""
        critical_colors = []
        
        # Check for near-complete rows/columns
        for row in range(5):
            if self._is_row_near_completion(player_state, row):
                color = self._get_color_for_row_completion(player_state, row)
                if color is not None:
                    critical_colors.append(self.color_names[color])
        
        for col in range(5):
            if self._is_column_near_completion(player_state, col):
                color = self._get_color_for_column_completion(player_state, col)
                if color is not None:
                    critical_colors.append(self.color_names[color])
        
        return critical_colors
    
    def _is_row_near_completion(self, player_state, row: int) -> bool:
        """Check if a row is near completion."""
        filled_positions = sum(player_state.grid_state[row])
        return filled_positions >= 3
    
    def _is_column_near_completion(self, player_state, col: int) -> bool:
        """Check if a column is near completion."""
        filled_positions = sum(player_state.grid_state[row][col] for row in range(5))
        return filled_positions >= 3
    
    def _get_color_for_row_completion(self, player_state, row: int) -> Optional[int]:
        """Get the color needed to complete a row."""
        for col in range(5):
            if player_state.grid_state[row][col] == 0:  # Empty position
                return self._get_color_for_position(row, col)
        return None
    
    def _get_color_for_column_completion(self, player_state, col: int) -> Optional[int]:
        """Get the color needed to complete a column."""
        for row in range(5):
            if player_state.grid_state[row][col] == 0:  # Empty position
                return self._get_color_for_position(row, col)
        return None
    
    def _calculate_conservation_potential(self, remaining_tiles: Dict[str, int], state: AzulState, player_id: int) -> float:
        """Calculate scoring potential from conservation strategy."""
        potential = 0.0
        
        player_state = state.agents[player_id]
        critical_colors = self._identify_critical_colors(player_state)
        
        for color_name, count in remaining_tiles.items():
            if color_name in critical_colors:
                # Higher potential for critical colors
                potential += count * 3.0
            else:
                # Lower potential for non-critical colors
                potential += count * 1.0
        
        return min(potential, 15.0)  # Cap at 15.0
    
    def _generate_conservation_sequence(self, remaining_tiles: Dict[str, int], state: AzulState, player_id: int) -> List[str]:
        """Generate optimal conservation move sequence."""
        sequence = []
        
        player_state = state.agents[player_id]
        critical_colors = self._identify_critical_colors(player_state)
        
        # Prioritize critical colors
        for color_name in critical_colors:
            if color_name in remaining_tiles and remaining_tiles[color_name] > 0:
                sequence.append(f"Conserve {remaining_tiles[color_name]} {color_name} tiles")
        
        # Add other colors
        for color_name, count in remaining_tiles.items():
            if color_name not in critical_colors and count > 0:
                sequence.append(f"Use {count} {color_name} tiles efficiently")
        
        return sequence
    
    def _calculate_conservation_urgency(self, remaining_tiles: Dict[str, int], state: AzulState, player_id: int) -> float:
        """Calculate urgency for conservation strategy."""
        urgency = 0.0
        
        total_remaining = sum(remaining_tiles.values())
        
        # Higher urgency for fewer remaining tiles
        if total_remaining <= 10:
            urgency += 5.0
        elif total_remaining <= 20:
            urgency += 3.0
        elif total_remaining <= 30:
            urgency += 1.0
        
        # Higher urgency for critical colors
        player_state = state.agents[player_id]
        critical_colors = self._identify_critical_colors(player_state)
        
        for color_name in critical_colors:
            if color_name in remaining_tiles and remaining_tiles[color_name] <= 2:
                urgency += 2.0
        
        return min(urgency, 10.0)
    
    def _assess_conservation_risk(self, remaining_tiles: Dict[str, int], state: AzulState, player_id: int) -> str:
        """Assess risk level for conservation strategy."""
        total_remaining = sum(remaining_tiles.values())
        
        if total_remaining <= 10:
            return "high"
        elif total_remaining <= 20:
            return "medium"
        else:
            return "low"
    
    def _calculate_conservation_confidence(self, remaining_tiles: Dict[str, int], state: AzulState, player_id: int) -> float:
        """Calculate confidence in conservation strategy."""
        confidence = 0.6  # Base confidence
        
        # Higher confidence for fewer tiles (more predictable)
        total_remaining = sum(remaining_tiles.values())
        if total_remaining <= 15:
            confidence += 0.3
        elif total_remaining <= 25:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _analyze_wall_completion_opportunities(self, player_state, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze wall completion opportunities."""
        opportunities = []
        
        # Analyze row completion opportunities
        for row in range(5):
            filled_positions = sum(player_state.grid_state[row])
            if filled_positions >= 3:  # Near completion
                opportunity = self._analyze_row_completion_opportunity(player_state, row, state, player_id)
                if opportunity:
                    opportunities.append(opportunity)
        
        # Analyze column completion opportunities
        for col in range(5):
            filled_positions = sum(player_state.grid_state[row][col] for row in range(5))
            if filled_positions >= 3:  # Near completion
                opportunity = self._analyze_column_completion_opportunity(player_state, col, state, player_id)
                if opportunity:
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _analyze_row_completion_opportunity(self, player_state, row: int, state: AzulState, player_id: int) -> Optional[Dict]:
        """Analyze row completion opportunity."""
        needed_positions = []
        
        for col in range(5):
            if player_state.grid_state[row][col] == 0:  # Empty position
                needed_positions.append((row, col))
        
        if len(needed_positions) == 0:
            return None
        
        # Calculate potential
        potential = len(needed_positions) * 2.0  # Base points for completion
        
        # Check if tiles are available
        available_tiles = self._count_available_tiles_for_positions(needed_positions, state)
        
        if available_tiles > 0:
            return {
                'potential': potential,
                'sequence': self._generate_row_completion_sequence(row, needed_positions, state, player_id),
                'urgency': self._calculate_completion_urgency(needed_positions, available_tiles),
                'confidence': 0.8,
                'description': f"Row {row + 1} completion opportunity"
            }
        
        return None
    
    def _analyze_column_completion_opportunity(self, player_state, col: int, state: AzulState, player_id: int) -> Optional[Dict]:
        """Analyze column completion opportunity."""
        needed_positions = []
        
        for row in range(5):
            if player_state.grid_state[row][col] == 0:  # Empty position
                needed_positions.append((row, col))
        
        if len(needed_positions) == 0:
            return None
        
        # Calculate potential
        potential = len(needed_positions) * 2.0  # Base points for completion
        
        # Check if tiles are available
        available_tiles = self._count_available_tiles_for_positions(needed_positions, state)
        
        if available_tiles > 0:
            return {
                'potential': potential,
                'sequence': self._generate_column_completion_sequence(col, needed_positions, state, player_id),
                'urgency': self._calculate_completion_urgency(needed_positions, available_tiles),
                'confidence': 0.8,
                'description': f"Column {col + 1} completion opportunity"
            }
        
        return None
    
    def _count_available_tiles_for_positions(self, positions: List[Tuple[int, int]], state: AzulState) -> int:
        """Count tiles available for specific positions."""
        available_tiles = 0
        
        for row, col in positions:
            color = self._get_color_for_position(row, col)
            available_tiles += self._count_tiles_of_color(color, state)
        
        return available_tiles
    
    def _count_tiles_of_color(self, color: int, state: AzulState) -> int:
        """Count tiles of a specific color available."""
        count = 0
        
        # Count in factories
        for factory in state.factories:
            count += factory.count(color)
        
        # Count in center
        count += state.center.count(color)
        
        return count
    
    def _generate_row_completion_sequence(self, row: int, needed_positions: List[Tuple[int, int]], 
                                        state: AzulState, player_id: int) -> List[str]:
        """Generate sequence for row completion."""
        sequence = []
        
        for row_pos, col_pos in needed_positions:
            color = self._get_color_for_position(row_pos, col_pos)
            color_name = self.color_names[color]
            sequence.append(f"Place {color_name} tile at position ({row_pos + 1}, {col_pos + 1})")
        
        return sequence
    
    def _generate_column_completion_sequence(self, col: int, needed_positions: List[Tuple[int, int]], 
                                           state: AzulState, player_id: int) -> List[str]:
        """Generate sequence for column completion."""
        sequence = []
        
        for row_pos, col_pos in needed_positions:
            color = self._get_color_for_position(row_pos, col_pos)
            color_name = self.color_names[color]
            sequence.append(f"Place {color_name} tile at position ({row_pos + 1}, {col_pos + 1})")
        
        return sequence
    
    def _calculate_completion_urgency(self, needed_positions: List[Tuple[int, int]], available_tiles: int) -> float:
        """Calculate urgency for completion opportunity."""
        urgency = len(needed_positions) * 1.0
        
        # Higher urgency if tiles are scarce
        if available_tiles <= len(needed_positions):
            urgency += 3.0
        
        return min(urgency, 10.0)
    
    def _assess_optimization_risk(self, opportunity: Dict) -> str:
        """Assess risk for optimization opportunity."""
        if opportunity['potential'] > 8.0:
            return "low"
        elif opportunity['potential'] > 5.0:
            return "medium"
        else:
            return "high"
    
    def _generate_optimal_move_sequences(self, state: AzulState, player_id: int) -> List[Dict]:
        """Generate optimal move sequences for endgame."""
        sequences = []
        
        # Generate different sequence strategies
        sequences.append(self._generate_conservative_sequence(state, player_id))
        sequences.append(self._generate_aggressive_sequence(state, player_id))
        sequences.append(self._generate_balanced_sequence(state, player_id))
        
        return [seq for seq in sequences if seq is not None]
    
    def _generate_conservative_sequence(self, state: AzulState, player_id: int) -> Optional[Dict]:
        """Generate conservative move sequence."""
        player_state = state.agents[player_id]
        remaining_tiles = self._count_remaining_tiles(state)
        
        # Focus on safe, high-probability moves
        moves = []
        value = 0.0
        
        for color_name, count in remaining_tiles.items():
            if count > 0:
                moves.append(f"Take {color_name} tiles conservatively")
                value += count * 0.5
        
        if moves:
            return {
                'value': value,
                'moves': moves,
                'urgency': 3.0,
                'confidence': 0.9,
                'description': "Conservative endgame strategy"
            }
        
        return None
    
    def _generate_aggressive_sequence(self, state: AzulState, player_id: int) -> Optional[Dict]:
        """Generate aggressive move sequence."""
        player_state = state.agents[player_id]
        critical_colors = self._identify_critical_colors(player_state)
        
        moves = []
        value = 0.0
        
        for color_name in critical_colors:
            moves.append(f"Prioritize {color_name} tiles aggressively")
            value += 3.0
        
        if moves:
            return {
                'value': value,
                'moves': moves,
                'urgency': 7.0,
                'confidence': 0.7,
                'description': "Aggressive endgame strategy"
            }
        
        return None
    
    def _generate_balanced_sequence(self, state: AzulState, player_id: int) -> Optional[Dict]:
        """Generate balanced move sequence."""
        moves = ["Balance scoring and tile conservation"]
        
        return {
            'value': 5.0,
            'moves': moves,
            'urgency': 5.0,
            'confidence': 0.8,
            'description': "Balanced endgame strategy"
        }
    
    def _assess_sequence_risk(self, sequence: Dict) -> str:
        """Assess risk for move sequence."""
        if sequence['confidence'] > 0.8:
            return "low"
        elif sequence['confidence'] > 0.6:
            return "medium"
        else:
            return "high"
    
    def _analyze_floor_line_risks(self, state: AzulState, player_id: int) -> List[Dict]:
        """Analyze floor line risks in endgame."""
        risks = []
        
        player_state = state.agents[player_id]
        floor_tiles = len(player_state.floor_tiles)
        
        if floor_tiles > 0:
            # Calculate penalty
            penalty = self._calculate_floor_penalty(floor_tiles)
            
            # Generate mitigation sequence
            mitigation_sequence = self._generate_floor_mitigation_sequence(state, player_id)
            
            risks.append({
                'severity': floor_tiles / 7.0,  # Normalize to 0-1
                'mitigation_value': -penalty,  # Negative because it's a penalty
                'mitigation_sequence': mitigation_sequence,
                'level': self._assess_floor_risk_level(floor_tiles),
                'urgency': self._calculate_floor_risk_urgency(floor_tiles),
                'confidence': 0.9,
                'description': f"Floor line penalty: {penalty} points"
            })
        
        return risks
    
    def _calculate_floor_penalty(self, floor_tiles: int) -> int:
        """Calculate floor line penalty."""
        penalties = [-1, -1, -2, -2, -2, -3, -3]
        
        if floor_tiles <= len(penalties):
            return penalties[floor_tiles - 1]
        else:
            return penalties[-1]
    
    def _generate_floor_mitigation_sequence(self, state: AzulState, player_id: int) -> List[str]:
        """Generate sequence to mitigate floor line penalty."""
        return ["Complete pattern lines to avoid floor line penalties"]
    
    def _assess_floor_risk_level(self, floor_tiles: int) -> str:
        """Assess floor line risk level."""
        if floor_tiles >= 5:
            return "high"
        elif floor_tiles >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_floor_risk_urgency(self, floor_tiles: int) -> float:
        """Calculate urgency for floor line risk."""
        return min(floor_tiles * 1.5, 10.0)
    
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