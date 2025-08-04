"""
Azul Pattern Detection Engine - Phase 2 Implementation

This module provides pattern recognition for Azul positions, starting with:
- Tile blocking detection
- Pattern visualization
- Pattern-based move suggestions
- Success probability indicators

Future patterns to be added:
- Floor line optimization
- Scoring multiplier setups
- Color completion timing
- Factory control positions
- End-game tile counting
- Opponent disruption opportunities
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from core import azul_utils as utils
from core.azul_model import AzulState


@dataclass
class BlockingOpportunity:
    """Represents a tile blocking opportunity."""
    target_player: int
    target_pattern_line: int
    target_color: int
    blocking_tiles_available: int
    blocking_factories: List[int]
    blocking_center: bool
    urgency_score: float
    description: str


@dataclass
class PatternDetection:
    """Container for pattern detection results."""
    blocking_opportunities: List[BlockingOpportunity]
    total_patterns: int
    confidence_score: float


class AzulPatternDetector:
    """
    Detects tactical patterns in Azul positions.
    
    Features:
    - Tile blocking detection
    - Pattern visualization
    - Pattern-based move suggestions
    - Success probability indicators
    """
    
    def __init__(self):
        # Pattern detection thresholds
        self.blocking_urgency_threshold = 0.7
        self.pattern_confidence_threshold = 0.8
        
        # Color mapping for readability
        self.color_names = {
            utils.Tile.BLUE: "blue",
            utils.Tile.YELLOW: "yellow", 
            utils.Tile.RED: "red",
            utils.Tile.BLACK: "black",
            utils.Tile.WHITE: "white"
        }
    
    def detect_patterns(self, state: AzulState, current_player: int) -> PatternDetection:
        """
        Detect all tactical patterns in the current position.
        
        Args:
            state: Current game state
            current_player: Player to analyze for
            
        Returns:
            PatternDetection with all found patterns
        """
        blocking_opportunities = self._detect_blocking_opportunities(state, current_player)
        
        total_patterns = len(blocking_opportunities)
        confidence_score = self._calculate_pattern_confidence(blocking_opportunities)
        
        return PatternDetection(
            blocking_opportunities=blocking_opportunities,
            total_patterns=total_patterns,
            confidence_score=confidence_score
        )
    
    def _detect_blocking_opportunities(self, state: AzulState, current_player: int) -> List[BlockingOpportunity]:
        """
        Detect opportunities to block opponents from completing pattern lines.
        
        Args:
            state: Current game state
            current_player: Player to analyze for
            
        Returns:
            List of blocking opportunities
        """
        opportunities = []
        
        # Handle None state gracefully
        if state is None:
            return opportunities
        
        # Analyze each opponent
        for opponent_id in range(len(state.agents)):
            if opponent_id == current_player:
                continue
                
            opponent_state = state.agents[opponent_id]
            opponent_opportunities = self._analyze_opponent_blocking(
                state, current_player, opponent_id, opponent_state
            )
            opportunities.extend(opponent_opportunities)
        
        # Sort by urgency (most urgent first)
        opportunities.sort(key=lambda x: x.urgency_score, reverse=True)
        
        return opportunities
    
    def _analyze_opponent_blocking(self, state: AzulState, current_player: int, 
                                 opponent_id: int, opponent_state) -> List[BlockingOpportunity]:
        """
        Analyze blocking opportunities against a specific opponent.
        
        Args:
            state: Current game state
            current_player: Player to analyze for
            opponent_id: Opponent to analyze
            opponent_state: Opponent's board state
            
        Returns:
            List of blocking opportunities against this opponent
        """
        opportunities = []
        
        # Check each pattern line of the opponent
        for pattern_line in range(5):
            blocking_opp = self._analyze_pattern_line_blocking(
                state, current_player, opponent_id, opponent_state, pattern_line
            )
            if blocking_opp:
                opportunities.append(blocking_opp)
        
        return opportunities
    
    def _analyze_pattern_line_blocking(self, state: AzulState, current_player: int,
                                     opponent_id: int, opponent_state, pattern_line: int) -> Optional[BlockingOpportunity]:
        """
        Analyze blocking opportunities for a specific pattern line.
        
        Args:
            state: Current game state
            current_player: Player to analyze for
            opponent_id: Opponent to analyze
            opponent_state: Opponent's board state
            pattern_line: Pattern line to analyze (0-4)
            
        Returns:
            BlockingOpportunity if blocking is possible and valuable
        """
        # Get pattern line info
        line_tiles = opponent_state.lines_number[pattern_line]
        line_color = opponent_state.lines_tile[pattern_line]
        line_capacity = pattern_line + 1
        
        # Skip if pattern line is empty
        if line_tiles == 0:
            return None
        
        # Skip if no color is set in the pattern line
        if line_color == -1:
            return None
        
        # Check if this color is already completed on the wall
        if self._is_color_completed_on_wall_row(opponent_state, pattern_line, line_color):
            return None
        
        # Calculate how many tiles opponent needs
        tiles_needed = line_capacity - line_tiles
        
        # Check if we can block by taking tiles from factories/center
        blocking_tiles_available = self._count_blocking_tiles_available(
            state, line_color, current_player
        )
        
        if blocking_tiles_available == 0:
            return None
        
        # Calculate urgency score
        urgency_score = self._calculate_blocking_urgency(
            tiles_needed, blocking_tiles_available, line_tiles, line_capacity
        )
        
        # For full pattern lines, still consider blocking if tiles are available
        if tiles_needed == 0 and line_tiles > 0:
            # High urgency for full pattern lines
            urgency_score = max(urgency_score, 0.8)
        
        # Boost urgency for high completion scenarios
        if tiles_needed <= 1 and line_tiles >= line_capacity * 0.6:
            # High urgency when opponent is close to completion
            urgency_score = max(urgency_score, 0.8)
        
        # Only return if urgency is above threshold
        if urgency_score < self.blocking_urgency_threshold:
            return None
        
        # Find which factories/center have blocking tiles
        blocking_factories = self._find_blocking_factories(state, line_color)
        blocking_center = self._has_blocking_tiles_in_center(state, line_color)
        
        # Generate description
        description = self._generate_blocking_description(
            opponent_id, pattern_line, line_color, tiles_needed, 
            blocking_tiles_available, urgency_score
        )
        
        return BlockingOpportunity(
            target_player=opponent_id,
            target_pattern_line=pattern_line,
            target_color=line_color,
            blocking_tiles_available=blocking_tiles_available,
            blocking_factories=blocking_factories,
            blocking_center=blocking_center,
            urgency_score=urgency_score,
            description=description
        )
    
    def _is_color_completed_on_wall_row(self, agent_state, row: int, color: int) -> bool:
        """
        Check if a color is already completed on a wall row.
        
        Args:
            agent_state: Agent's board state
            row: Wall row to check (0-4)
            color: Color to check
            
        Returns:
            True if color is already on the wall in this row
        """
        # Check if the color is already placed on the wall in this row
        return agent_state.grid_state[row][color] == 1
    
    def _count_blocking_tiles_available(self, state: AzulState, color: int, current_player: int) -> int:
        """
        Count how many tiles of a specific color are available for blocking.
        
        Args:
            state: Current game state
            color: Color to count
            current_player: Current player ID
            
        Returns:
            Number of blocking tiles available
        """
        total_available = 0
        
        # Count tiles in factories
        for factory_id, factory in enumerate(state.factories):
            if color in factory.tiles and factory.tiles[color] > 0:
                total_available += factory.tiles[color]
        
        # Count tiles in center pool
        if color in state.centre_pool.tiles and state.centre_pool.tiles[color] > 0:
            total_available += state.centre_pool.tiles[color]
        
        return total_available
    
    def _find_blocking_factories(self, state: AzulState, color: int) -> List[int]:
        """
        Find factories that contain blocking tiles.
        
        Args:
            state: Current game state
            color: Color to look for
            
        Returns:
            List of factory IDs that contain the color
        """
        blocking_factories = []
        
        for factory_id, factory in enumerate(state.factories):
            if color in factory.tiles and factory.tiles[color] > 0:
                blocking_factories.append(factory_id)
        
        return blocking_factories
    
    def _has_blocking_tiles_in_center(self, state: AzulState, color: int) -> bool:
        """
        Check if center pool has blocking tiles.
        
        Args:
            state: Current game state
            color: Color to check
            
        Returns:
            True if center pool has tiles of this color
        """
        return color in state.centre_pool.tiles and state.centre_pool.tiles[color] > 0
    
    def _calculate_blocking_urgency(self, tiles_needed: int, tiles_available: int, 
                                  current_tiles: int, line_capacity: int) -> float:
        """
        Calculate how urgent it is to block this pattern line.
        
        Args:
            tiles_needed: How many tiles opponent needs
            tiles_available: How many tiles we can block with
            current_tiles: How many tiles opponent already has
            line_capacity: Total capacity of the pattern line
            
        Returns:
            Urgency score between 0.0 and 1.0
        """
        # Base urgency: more tiles needed = higher urgency
        base_urgency = tiles_needed / line_capacity
        
        # Completion urgency: closer to completion = higher urgency
        completion_ratio = current_tiles / line_capacity
        completion_urgency = completion_ratio ** 2  # Quadratic scaling
        
        # Availability urgency: fewer tiles available = higher urgency
        # Normalize based on tiles needed vs available
        if tiles_needed > 0:
            availability_ratio = min(tiles_available / tiles_needed, 2.0)  # Cap at 2x needed
            availability_urgency = 1.0 - (availability_ratio / 2.0)  # Normalize to 0-1
        else:
            availability_urgency = 0.0
        
        availability_urgency = max(0.0, min(1.0, availability_urgency))
        
        # Combine factors with weights
        urgency = (base_urgency * 0.3 + completion_urgency * 0.5 + availability_urgency * 0.2)
        
        return min(1.0, urgency)
    
    def _generate_blocking_description(self, opponent_id: int, pattern_line: int, 
                                    color: int, tiles_needed: int, tiles_available: int, 
                                    urgency_score: float) -> str:
        """
        Generate a human-readable description of the blocking opportunity.
        
        Args:
            opponent_id: Opponent being blocked
            pattern_line: Pattern line being blocked
            color: Color being blocked
            tiles_needed: Tiles opponent needs
            tiles_available: Tiles we can block with
            urgency_score: Calculated urgency score
            
        Returns:
            Human-readable description
        """
        color_name = self.color_names.get(color, f"color {color}")
        urgency_level = "HIGH" if urgency_score > 0.8 else "MEDIUM" if urgency_score > 0.6 else "LOW"
        
        description = (
            f"Block opponent {opponent_id + 1}'s {color_name} tiles on pattern line {pattern_line + 1}. "
            f"They need {tiles_needed} more tiles to complete the line. "
            f"You can block with {tiles_available} available tiles. "
            f"Urgency: {urgency_level} ({urgency_score:.2f})"
        )
        
        return description
    
    def _calculate_pattern_confidence(self, blocking_opportunities: List[BlockingOpportunity]) -> float:
        """
        Calculate overall confidence in pattern detection.
        
        Args:
            blocking_opportunities: List of detected blocking opportunities
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not blocking_opportunities:
            return 0.0
        
        # Average urgency of detected patterns
        avg_urgency = sum(opp.urgency_score for opp in blocking_opportunities) / len(blocking_opportunities)
        
        # More patterns = higher confidence (up to a point)
        pattern_count_factor = min(1.0, len(blocking_opportunities) / 5.0)
        
        # Combine factors
        confidence = (avg_urgency * 0.7 + pattern_count_factor * 0.3)
        
        return min(1.0, confidence)
    
    def get_blocking_move_suggestions(self, state: AzulState, current_player: int, 
                                    blocking_opportunities: List[BlockingOpportunity]) -> List[Dict]:
        """
        Generate specific move suggestions for blocking opportunities.
        
        Args:
            state: Current game state
            current_player: Current player ID
            blocking_opportunities: List of blocking opportunities
            
        Returns:
            List of move suggestions with details
        """
        suggestions = []
        
        for opportunity in blocking_opportunities:
            # Find best factory to take from
            best_factory = self._find_best_blocking_factory(state, opportunity)
            
            if best_factory is not None:
                suggestion = {
                    'type': 'blocking',
                    'target_opponent': opportunity.target_player,
                    'target_color': opportunity.target_color,
                    'target_pattern_line': opportunity.target_pattern_line,
                    'urgency_score': opportunity.urgency_score,
                    'description': opportunity.description,
                    'suggested_action': {
                        'action_type': 1,  # TAKE_FROM_FACTORY
                        'source_id': best_factory,
                        'tile_type': opportunity.target_color,
                        'pattern_line_dest': -1,  # To floor line
                        'num_to_pattern_line': 0,
                        'num_to_floor_line': min(opportunity.blocking_tiles_available, 4)
                    }
                }
                suggestions.append(suggestion)
        
        # Sort by urgency
        suggestions.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return suggestions
    
    def _find_best_blocking_factory(self, state: AzulState, opportunity: BlockingOpportunity) -> Optional[int]:
        """
        Find the best factory to take blocking tiles from.
        
        Args:
            state: Current game state
            opportunity: Blocking opportunity
            
        Returns:
            Best factory ID, or None if no good option
        """
        best_factory = None
        max_tiles = 0
        
        for factory_id in opportunity.blocking_factories:
            factory = state.factories[factory_id]
            tiles_available = factory.tiles.get(opportunity.target_color, 0)
            
            if tiles_available > max_tiles:
                max_tiles = tiles_available
                best_factory = factory_id
        
        return best_factory 