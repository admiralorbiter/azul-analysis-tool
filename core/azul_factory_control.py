"""
Azul Factory Control Analysis - Phase 2.4 Implementation

This module provides factory control analysis for Azul positions:
- Factory domination opportunities
- Disruption control strategies
- Timing control analysis
- Color control opportunities
- Strategic factory management

Integrates with existing pattern detection system for comprehensive analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState


@dataclass
class FactoryControlOpportunity:
    """Represents a factory control opportunity."""
    control_type: str  # "domination", "disruption", "timing", "color_control"
    factory_id: int
    strategic_value: float
    urgency_score: float
    urgency_level: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    risk_assessment: str  # "low", "medium", "high"
    move_suggestions: List[str]
    confidence: float
    description: str


class FactoryControlDetector:
    """
    Factory control opportunity detection.
    
    Features:
    - Factory domination detection
    - Disruption control analysis
    - Timing control assessment
    - Color control opportunities
    """
    
    def __init__(self):
        # Factory control thresholds
        self.domination_threshold = 0.7
        self.disruption_threshold = 0.6
        self.timing_threshold = 0.5
        self.color_control_threshold = 0.6
        
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
    
    def detect_opportunities(self, state: AzulState, player_id: int) -> List[FactoryControlOpportunity]:
        """
        Detect factory control opportunities in the current position.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            List of factory control opportunities
        """
        opportunities = []
        
        # Factory domination detection
        opportunities.extend(self._detect_factory_domination(state, player_id))
        
        # Disruption control detection
        opportunities.extend(self._detect_disruption_control(state, player_id))
        
        # Timing control detection
        opportunities.extend(self._detect_timing_control(state, player_id))
        
        # Color control detection
        opportunities.extend(self._detect_color_control(state, player_id))
        
        return opportunities
    
    def _detect_factory_domination(self, state: AzulState, player_id: int) -> List[FactoryControlOpportunity]:
        """Detect opportunities to dominate key factories."""
        opportunities = []
        
        for factory_id, factory in enumerate(state.factories):
            if factory.total == 0:  # Skip empty factories
                continue
            
            # Analyze factory tile distribution
            tile_distribution = self._analyze_factory_distribution(factory)
            
            # Check for domination opportunities
            if self._is_domination_opportunity(tile_distribution, state, player_id):
                strategic_value = self._calculate_domination_value(tile_distribution, state, player_id)
                urgency_score = self._calculate_domination_urgency(tile_distribution, state, player_id)
                
                opportunities.append(FactoryControlOpportunity(
                    control_type="domination",
                    factory_id=factory_id,
                    strategic_value=strategic_value,
                    urgency_score=urgency_score,
                    urgency_level=self._get_urgency_level(urgency_score),
                    risk_assessment=self._assess_domination_risk(tile_distribution, state, player_id),
                    move_suggestions=self._generate_domination_moves(factory_id, tile_distribution, state, player_id),
                    confidence=self._calculate_domination_confidence(tile_distribution, state, player_id),
                    description=f"Factory {factory_id} domination opportunity - {self._describe_domination_opportunity(tile_distribution)}"
                ))
        
        return opportunities
    
    def _detect_disruption_control(self, state: AzulState, player_id: int) -> List[FactoryControlOpportunity]:
        """Detect opportunities to disrupt opponent strategies through factory control."""
        opportunities = []
        
        for factory_id, factory in enumerate(state.factories):
            if factory.total == 0:
                continue
            
            # Analyze opponent threats
            opponent_threats = self._analyze_opponent_threats(state, player_id, factory_id)
            
            if self._is_disruption_opportunity(opponent_threats, factory):
                strategic_value = self._calculate_disruption_value(opponent_threats, factory)
                urgency_score = self._calculate_disruption_urgency(opponent_threats, factory)
                
                opportunities.append(FactoryControlOpportunity(
                    control_type="disruption",
                    factory_id=factory_id,
                    strategic_value=strategic_value,
                    urgency_score=urgency_score,
                    urgency_level=self._get_urgency_level(urgency_score),
                    risk_assessment=self._assess_disruption_risk(opponent_threats, factory),
                    move_suggestions=self._generate_disruption_moves(factory_id, opponent_threats, state, player_id),
                    confidence=self._calculate_disruption_confidence(opponent_threats, factory),
                    description=f"Factory {factory_id} disruption opportunity - {self._describe_disruption_opportunity(opponent_threats)}"
                ))
        
        return opportunities
    
    def _detect_timing_control(self, state: AzulState, player_id: int) -> List[FactoryControlOpportunity]:
        """Detect timing control opportunities in factory management."""
        opportunities = []
        
        # Analyze game phase and timing
        game_phase = self._assess_game_phase(state)
        timing_opportunities = self._analyze_timing_opportunities(state, player_id, game_phase)
        
        for factory_id, timing_opp in timing_opportunities.items():
            if timing_opp['value'] > self.timing_threshold:
                opportunities.append(FactoryControlOpportunity(
                    control_type="timing",
                    factory_id=factory_id,
                    strategic_value=timing_opp['value'],
                    urgency_score=timing_opp['urgency'],
                    urgency_level=self._get_urgency_level(timing_opp['urgency']),
                    risk_assessment=self._assess_timing_risk(timing_opp),
                    move_suggestions=self._generate_timing_moves(factory_id, timing_opp, state, player_id),
                    confidence=timing_opp['confidence'],
                    description=f"Factory {factory_id} timing control - {timing_opp['description']}"
                ))
        
        return opportunities
    
    def _detect_color_control(self, state: AzulState, player_id: int) -> List[FactoryControlOpportunity]:
        """Detect color control opportunities across factories."""
        opportunities = []
        
        # Analyze color distribution across factories
        color_analysis = self._analyze_color_distribution(state, player_id)
        
        for color, color_opp in color_analysis.items():
            if color_opp['control_value'] > self.color_control_threshold:
                # Find best factory for this color control
                best_factory = self._find_best_color_control_factory(state, color, color_opp)
                
                if best_factory is not None:
                    opportunities.append(FactoryControlOpportunity(
                        control_type="color_control",
                        factory_id=best_factory,
                        strategic_value=color_opp['control_value'],
                        urgency_score=color_opp['urgency'],
                        urgency_level=self._get_urgency_level(color_opp['urgency']),
                        risk_assessment=self._assess_color_control_risk(color_opp),
                        move_suggestions=self._generate_color_control_moves(best_factory, color, color_opp, state, player_id),
                        confidence=color_opp['confidence'],
                        description=f"Color control opportunity for {self.color_names[color]} - {color_opp['description']}"
                    ))
        
        return opportunities
    
    def _analyze_factory_distribution(self, factory) -> Dict[int, int]:
        """Analyze tile distribution in a factory."""
        return factory.tiles.copy()
    
    def _is_domination_opportunity(self, distribution: Dict[int, int], state: AzulState, player_id: int) -> bool:
        """Check if factory presents domination opportunity."""
        # Check if factory has high-value tiles for the player
        player_state = state.agents[player_id]
        
        for color, count in distribution.items():
            if count >= 2:  # Multiple tiles of same color
                # Check if player can use this color effectively
                if self._can_player_use_color_effectively(player_state, color):
                    return True
        
        return False
    
    def _can_player_use_color_effectively(self, player_state, color: int) -> bool:
        """Check if player can effectively use a color."""
        # Check pattern lines that can accept this color
        for pattern_line in range(5):
            if self._can_pattern_line_accept_color(player_state, pattern_line, color):
                return True
        
        # Check wall placement opportunities
        if self._has_wall_placement_for_color(player_state, color):
            return True
        
        return False
    
    def _can_pattern_line_accept_color(self, player_state, pattern_line: int, color: int) -> bool:
        """Check if pattern line can accept a color."""
        # Check if pattern line is not full
        if player_state.lines_number[pattern_line] >= pattern_line + 1:
            return False
        
        # Check if color matches the row
        wall_row = pattern_line
        wall_col = self._get_color_column(color)
        return wall_col == self._get_color_for_position(wall_row, wall_col)
    
    def _has_wall_placement_for_color(self, player_state, color: int) -> bool:
        """Check if player has wall placement opportunities for a color."""
        for row in range(5):
            for col in range(5):
                if self._get_color_for_position(row, col) == color:
                    if player_state.grid_state[row][col] == 0:  # Empty position
                        return True
        return False
    
    def _calculate_domination_value(self, distribution: Dict[int, int], state: AzulState, player_id: int) -> float:
        """Calculate strategic value of factory domination."""
        value = 0.0
        
        for color, count in distribution.items():
            if count >= 2:
                # Base value for multiple tiles
                value += count * 2.0
                
                # Bonus for colors player can use effectively
                if self._can_player_use_color_effectively(state.agents[player_id], color):
                    value += 3.0
        
        return min(value, 10.0)  # Cap at 10.0
    
    def _calculate_domination_urgency(self, distribution: Dict[int, int], state: AzulState, player_id: int) -> float:
        """Calculate urgency score for factory domination."""
        urgency = 0.0
        
        # Higher urgency for more tiles
        total_tiles = sum(distribution.values())
        urgency += min(total_tiles * 1.5, 5.0)
        
        # Higher urgency for colors player needs
        for color, count in distribution.items():
            if self._is_color_critical_for_player(state.agents[player_id], color):
                urgency += 2.0
        
        return min(urgency, 10.0)
    
    def _is_color_critical_for_player(self, player_state, color: int) -> bool:
        """Check if a color is critical for the player."""
        # Check if player is close to completing rows/columns with this color
        for row in range(5):
            if self._is_row_near_completion(player_state, row, color):
                return True
        
        for col in range(5):
            if self._is_column_near_completion(player_state, col, color):
                return True
        
        return False
    
    def _is_row_near_completion(self, player_state, row: int, color: int) -> bool:
        """Check if a row is near completion and needs this color."""
        filled_positions = 0
        needed_positions = 0
        
        for col in range(5):
            if player_state.grid_state[row][col] == 1:
                filled_positions += 1
            elif self._get_color_for_position(row, col) == color:
                needed_positions += 1
        
        return filled_positions >= 3 and needed_positions > 0
    
    def _is_column_near_completion(self, player_state, col: int, color: int) -> bool:
        """Check if a column is near completion and needs this color."""
        filled_positions = 0
        needed_positions = 0
        
        for row in range(5):
            if player_state.grid_state[row][col] == 1:
                filled_positions += 1
            elif self._get_color_for_position(row, col) == color:
                needed_positions += 1
        
        return filled_positions >= 3 and needed_positions > 0
    
    def _assess_domination_risk(self, distribution: Dict[int, int], state: AzulState, player_id: int) -> str:
        """Assess risk level for factory domination."""
        # Low risk if player can use tiles effectively
        if any(self._can_player_use_color_effectively(state.agents[player_id], color) 
               for color in distribution.keys()):
            return "low"
        
        # Medium risk if some tiles are useful
        useful_tiles = sum(1 for color in distribution.keys() 
                          if self._has_wall_placement_for_color(state.agents[player_id], color))
        
        if useful_tiles >= len(distribution) // 2:
            return "medium"
        
        return "high"
    
    def _generate_domination_moves(self, factory_id: int, distribution: Dict[int, int], 
                                 state: AzulState, player_id: int) -> List[str]:
        """Generate move suggestions for factory domination."""
        moves = []
        
        for color, count in distribution.items():
            if count >= 2:
                moves.append(f"Take {count} {self.color_names[color]} tiles from factory {factory_id}")
                
                # Suggest specific placement
                if self._can_player_use_color_effectively(state.agents[player_id], color):
                    placement = self._suggest_color_placement(state.agents[player_id], color)
                    if placement:
                        moves.append(f"Place {self.color_names[color]} tiles in {placement}")
        
        return moves
    
    def _suggest_color_placement(self, player_state, color: int) -> Optional[str]:
        """Suggest specific placement for a color."""
        # Check pattern lines first
        for pattern_line in range(5):
            if self._can_pattern_line_accept_color(player_state, pattern_line, color):
                return f"pattern line {pattern_line + 1}"
        
        # Check wall placement
        for row in range(5):
            for col in range(5):
                if (self._get_color_for_position(row, col) == color and 
                    player_state.grid_state[row][col] == 0):
                    return f"wall position ({row + 1}, {col + 1})"
        
        return None
    
    def _calculate_domination_confidence(self, distribution: Dict[int, int], state: AzulState, player_id: int) -> float:
        """Calculate confidence in domination opportunity."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for more tiles
        total_tiles = sum(distribution.values())
        confidence += min(total_tiles * 0.1, 0.3)
        
        # Higher confidence if player can use tiles effectively
        effective_colors = sum(1 for color in distribution.keys() 
                             if self._can_player_use_color_effectively(state.agents[player_id], color))
        
        if effective_colors > 0:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _describe_domination_opportunity(self, distribution: Dict[int, int]) -> str:
        """Generate human-readable description of domination opportunity."""
        color_descriptions = []
        for color, count in distribution.items():
            color_descriptions.append(f"{count} {self.color_names[color]}")
        
        return f"Multiple tiles available: {', '.join(color_descriptions)}"
    
    def _analyze_opponent_threats(self, state: AzulState, player_id: int, factory_id: int) -> Dict:
        """Analyze opponent threats for a specific factory."""
        threats = {}
        
        for opponent_id in range(len(state.agents)):
            if opponent_id == player_id:
                continue
            
            opponent_state = state.agents[opponent_id]
            factory = state.factories[factory_id]
            
            for color, count in factory.tiles.items():
                if count > 0 and self._is_color_critical_for_player(opponent_state, color):
                    threats[opponent_id] = threats.get(opponent_id, {})
                    threats[opponent_id][color] = threats[opponent_id].get(color, 0) + count
        
        return threats
    
    def _is_disruption_opportunity(self, opponent_threats: Dict, factory) -> bool:
        """Check if factory presents disruption opportunity."""
        return len(opponent_threats) > 0
    
    def _calculate_disruption_value(self, opponent_threats: Dict, factory) -> float:
        """Calculate strategic value of disruption opportunity."""
        value = 0.0
        
        for opponent_id, color_threats in opponent_threats.items():
            for color, count in color_threats.items():
                # Value based on how critical the color is for opponent
                value += count * 2.0
        
        return min(value, 10.0)
    
    def _calculate_disruption_urgency(self, opponent_threats: Dict, factory) -> float:
        """Calculate urgency score for disruption opportunity."""
        urgency = 0.0
        
        for opponent_id, color_threats in opponent_threats.items():
            for color, count in color_threats.items():
                urgency += count * 1.5
        
        return min(urgency, 10.0)
    
    def _assess_disruption_risk(self, opponent_threats: Dict, factory) -> str:
        """Assess risk level for disruption opportunity."""
        total_threats = sum(sum(color_threats.values()) for color_threats in opponent_threats.values())
        
        if total_threats >= 4:
            return "high"
        elif total_threats >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_disruption_moves(self, factory_id: int, opponent_threats: Dict, 
                                 state: AzulState, player_id: int) -> List[str]:
        """Generate move suggestions for disruption."""
        moves = []
        
        for opponent_id, color_threats in opponent_threats.items():
            for color, count in color_threats.items():
                moves.append(f"Take {self.color_names[color]} tiles from factory {factory_id} to disrupt opponent {opponent_id + 1}")
        
        return moves
    
    def _calculate_disruption_confidence(self, opponent_threats: Dict, factory) -> float:
        """Calculate confidence in disruption opportunity."""
        confidence = 0.6  # Base confidence for disruption
        
        # Higher confidence for more threats
        total_threats = sum(sum(color_threats.values()) for color_threats in opponent_threats.values())
        confidence += min(total_threats * 0.1, 0.3)
        
        return min(confidence, 1.0)
    
    def _describe_disruption_opportunity(self, opponent_threats: Dict) -> str:
        """Generate human-readable description of disruption opportunity."""
        descriptions = []
        for opponent_id, color_threats in opponent_threats.items():
            for color, count in color_threats.items():
                descriptions.append(f"opponent {opponent_id + 1} needs {self.color_names[color]}")
        
        return f"Disruption opportunity: {', '.join(descriptions)}"
    
    def _assess_game_phase(self, state: AzulState) -> str:
        """Assess current game phase."""
        total_tiles_remaining = sum(factory.total for factory in state.factories) + state.centre_pool.total
        
        if total_tiles_remaining > 80:
            return "early"
        elif total_tiles_remaining > 40:
            return "mid"
        else:
            return "late"
    
    def _analyze_timing_opportunities(self, state: AzulState, player_id: int, game_phase: str) -> Dict[int, Dict]:
        """Analyze timing control opportunities."""
        timing_opportunities = {}
        
        for factory_id, factory in enumerate(state.factories):
            if factory.total == 0:
                continue
            
            timing_value = self._calculate_timing_value(factory, state, player_id, game_phase)
            if timing_value > 0:
                timing_opportunities[factory_id] = {
                    'value': timing_value,
                    'urgency': self._calculate_timing_urgency(factory, game_phase),
                    'confidence': 0.7,
                    'description': self._describe_timing_opportunity(factory, game_phase)
                }
        
        return timing_opportunities
    
    def _calculate_timing_value(self, factory, state: AzulState, player_id: int, game_phase: str) -> float:
        """Calculate timing control value."""
        value = 0.0
        
        if game_phase == "early":
            # Early game: focus on setup
            value += factory.total * 0.5
        elif game_phase == "mid":
            # Mid game: focus on scoring
            value += factory.total * 1.0
        else:
            # Late game: focus on endgame
            value += factory.total * 1.5
        
        return min(value, 10.0)
    
    def _calculate_timing_urgency(self, factory, game_phase: str) -> float:
        """Calculate urgency for timing control."""
        urgency = factory.total * 0.5
        
        if game_phase == "late":
            urgency *= 1.5
        
        return min(urgency, 10.0)
    
    def _assess_timing_risk(self, timing_opp: Dict) -> str:
        """Assess risk for timing control."""
        if timing_opp['value'] > 7.0:
            return "low"
        elif timing_opp['value'] > 4.0:
            return "medium"
        else:
            return "high"
    
    def _generate_timing_moves(self, factory_id: int, timing_opp: Dict, state: AzulState, player_id: int) -> List[str]:
        """Generate move suggestions for timing control."""
        return [f"Control timing by taking tiles from factory {factory_id}"]
    
    def _describe_timing_opportunity(self, factory, game_phase: str) -> str:
        """Generate description of timing opportunity."""
        return f"Timing control in {game_phase} game phase with {factory.total} tiles"
    
    def _analyze_color_distribution(self, state: AzulState, player_id: int) -> Dict[int, Dict]:
        """Analyze color distribution across all factories."""
        color_analysis = {}
        
        for color in range(5):  # 5 colors
            color_count = 0
            factory_locations = []
            
            for factory_id, factory in enumerate(state.factories):
                color_count_in_factory = factory.tiles.get(color, 0)
                if color_count_in_factory > 0:
                    color_count += color_count_in_factory
                    factory_locations.append(factory_id)
            
            if color_count > 0:
                color_analysis[color] = {
                    'count': color_count,
                    'factories': factory_locations,
                    'control_value': self._calculate_color_control_value(color, color_count, state, player_id),
                    'urgency': self._calculate_color_control_urgency(color, color_count, state, player_id),
                    'confidence': 0.8,
                    'description': f"{color_count} {self.color_names[color]} tiles across {len(factory_locations)} factories"
                }
        
        return color_analysis
    
    def _calculate_color_control_value(self, color: int, count: int, state: AzulState, player_id: int) -> float:
        """Calculate color control value."""
        value = count * 1.0
        
        # Bonus if player needs this color
        if self._is_color_critical_for_player(state.agents[player_id], color):
            value += 3.0
        
        return min(value, 10.0)
    
    def _calculate_color_control_urgency(self, color: int, count: int, state: AzulState, player_id: int) -> float:
        """Calculate urgency for color control."""
        urgency = count * 0.5
        
        # Higher urgency if player needs this color
        if self._is_color_critical_for_player(state.agents[player_id], color):
            urgency += 2.0
        
        return min(urgency, 10.0)
    
    def _find_best_color_control_factory(self, state: AzulState, color: int, color_opp: Dict) -> Optional[int]:
        """Find the best factory for color control."""
        best_factory = None
        best_count = 0
        
        for factory_id in color_opp['factories']:
            factory = state.factories[factory_id]
            color_count = factory.tiles.get(color, 0)
            
            if color_count > best_count:
                best_count = color_count
                best_factory = factory_id
        
        return best_factory
    
    def _assess_color_control_risk(self, color_opp: Dict) -> str:
        """Assess risk for color control."""
        if color_opp['control_value'] > 7.0:
            return "low"
        elif color_opp['control_value'] > 4.0:
            return "medium"
        else:
            return "high"
    
    def _generate_color_control_moves(self, factory_id: int, color: int, color_opp: Dict, 
                                    state: AzulState, player_id: int) -> List[str]:
        """Generate move suggestions for color control."""
        moves = []
        
        factory = state.factories[factory_id]
        color_count = factory.tiles.get(color, 0)
        
        moves.append(f"Take {color_count} {self.color_names[color]} tiles from factory {factory_id}")
        
        # Suggest placement
        placement = self._suggest_color_placement(state.agents[player_id], color)
        if placement:
            moves.append(f"Place {self.color_names[color]} tiles in {placement}")
        
        return moves
    
    def _get_urgency_level(self, urgency_score: float) -> str:
        """Convert urgency score to urgency level."""
        if urgency_score >= self.critical_urgency:
            return "CRITICAL"
        elif urgency_score >= self.high_urgency:
            return "HIGH"
        elif urgency_score >= self.medium_urgency:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_color_column(self, color: int) -> int:
        """Get the column for a color on the wall."""
        return color
    
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