#!/usr/bin/env python3
"""
Enhanced Move Generator - Comprehensive Move Generation System

This module generates all possible moves for Azul positions with:
- Complete move coverage (factory and center pool moves)
- Move validation and filtering
- Move prioritization by likelihood and strategic value
- Move clustering for similar moves
- Integration with existing move generation systems
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import time
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import numpy as np

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_move_generator import AzulMoveGenerator

class MoveType(Enum):
    """Types of moves in Azul."""
    FACTORY_TO_PATTERN = "factory_to_pattern"
    FACTORY_TO_FLOOR = "factory_to_floor"
    CENTER_TO_PATTERN = "center_to_pattern"
    CENTER_TO_FLOOR = "center_to_floor"

class MovePriority(Enum):
    """Move priority levels for filtering and ordering."""
    CRITICAL = 1      # Must-analyze moves (high strategic value)
    HIGH = 2          # Important moves (good strategic value)
    MEDIUM = 3        # Standard moves (moderate strategic value)
    LOW = 4           # Low priority moves (limited strategic value)
    MINIMAL = 5       # Minimal priority (unlikely to be good)

@dataclass
class GeneratedMove:
    """A generated move with metadata."""
    move_type: MoveType
    factory_id: Optional[int] = None
    color: int = 0
    count: int = 1
    target_line: int = -1
    priority: MovePriority = MovePriority.MEDIUM
    strategic_value: float = 0.0
    likelihood: float = 0.0
    validation_score: float = 0.0
    move_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.move_data is None:
            self.move_data = {
                'move_type': self.move_type.value,
                'factory_id': self.factory_id,
                'color': self.color,
                'count': self.count,
                'target_line': self.target_line
            }

class EnhancedMoveGenerator:
    """Enhanced move generator with comprehensive move coverage."""
    
    def __init__(self, max_moves_per_position: int = 200, enable_filtering: bool = True):
        self.max_moves_per_position = max_moves_per_position
        self.enable_filtering = enable_filtering
        
        # Initialize existing move generator
        self.move_generator = AzulMoveGenerator()
        
        # Move generation counters
        self.total_moves_generated = 0
        self.valid_moves_generated = 0
        self.filtered_moves = 0
    
    def generate_all_moves(self, state: AzulState, player_id: int = 0) -> List[GeneratedMove]:
        """Generate all possible moves for a position."""
        moves = []
        
        # Generate factory moves
        factory_moves = self._generate_factory_moves(state, player_id)
        moves.extend(factory_moves)
        
        # Generate center pool moves
        center_moves = self._generate_center_moves(state, player_id)
        moves.extend(center_moves)
        
        # Validate and filter moves
        if self.enable_filtering:
            moves = self._filter_moves(moves, state, player_id)
        
        # Prioritize moves
        moves = self._prioritize_moves(moves, state, player_id)
        
        # Limit to max moves per position
        if len(moves) > self.max_moves_per_position:
            moves = moves[:self.max_moves_per_position]
        
        self.total_moves_generated += len(moves)
        self.valid_moves_generated += len(moves)
        
        return moves
    
    def _generate_factory_moves(self, state: AzulState, player_id: int) -> List[GeneratedMove]:
        """Generate all possible factory moves."""
        moves = []
        
        # Iterate through all factories
        for factory_id in range(len(state.factories)):
            factory = state.factories[factory_id]
            
            # Check if factory has tiles
            if factory.total == 0:
                continue
            
            # Generate moves for each color in the factory
            for color, count in factory.tiles.items():
                if count == 0:
                    continue
                
                # Generate pattern line moves for ALL possible tile counts
                for tile_count in range(1, count + 1):  # ✅ 1, 2, 3, ..., count
                    for target_line in range(5):
                        if self._is_valid_pattern_line_move(state, player_id, color, target_line):
                            move = GeneratedMove(
                                move_type=MoveType.FACTORY_TO_PATTERN,
                                factory_id=factory_id,
                                color=color,
                                count=tile_count,  # ✅ Use partial counts
                                target_line=target_line,
                                priority=self._calculate_move_priority(state, player_id, color, target_line, count),
                                strategic_value=self._calculate_strategic_value(state, player_id, color, target_line),
                                likelihood=self._calculate_move_likelihood(state, player_id, color, target_line, count),
                                validation_score=self._validate_move(state, player_id, color, target_line, count)
                            )
                            moves.append(move)
                
                # Generate floor moves
                move = GeneratedMove(
                    move_type=MoveType.FACTORY_TO_FLOOR,
                    factory_id=factory_id,
                    color=color,
                    count=count,
                    target_line=-1,
                    priority=MovePriority.LOW,  # Floor moves are generally low priority
                    strategic_value=0.0,
                    likelihood=0.1,
                    validation_score=1.0  # Always valid
                )
                moves.append(move)
        
        return moves
    
    def _generate_center_moves(self, state: AzulState, player_id: int) -> List[GeneratedMove]:
        """Generate all possible center pool moves."""
        moves = []
        
        center_pool = state.centre_pool
        
        # Check if center pool has tiles
        if center_pool.total == 0:
            return moves
        
        # Generate moves for each color in the center pool
        for color, count in center_pool.tiles.items():
            if count == 0:
                continue
            
            # Generate pattern line moves
            for target_line in range(5):
                if self._is_valid_pattern_line_move(state, player_id, color, target_line):
                    move = GeneratedMove(
                        move_type=MoveType.CENTER_TO_PATTERN,
                        factory_id=None,
                        color=color,
                        count=count,
                        target_line=target_line,
                        priority=self._calculate_move_priority(state, player_id, color, target_line, count),
                        strategic_value=self._calculate_strategic_value(state, player_id, color, target_line),
                        likelihood=self._calculate_move_likelihood(state, player_id, color, target_line, count),
                        validation_score=self._validate_move(state, player_id, color, target_line, count)
                    )
                    moves.append(move)
            
            # Generate floor moves
            move = GeneratedMove(
                move_type=MoveType.CENTER_TO_FLOOR,
                factory_id=None,
                color=color,
                count=count,
                target_line=-1,
                priority=MovePriority.LOW,
                strategic_value=0.0,
                likelihood=0.1,
                validation_score=1.0
            )
            moves.append(move)
        
        return moves
    
    def _is_valid_pattern_line_move(self, state: AzulState, player_id: int, color: int, target_line: int) -> bool:
        """Check if a pattern line move is valid."""
        player = state.agents[player_id]
        
        # Check if the pattern line is already full
        if player.lines_number[target_line] >= target_line + 1:
            return False
        
        # Check if the wall already has this color in this row
        wall_row = target_line
        wall_col = self._get_wall_column_for_color(color)
        
        if player.grid_state[wall_row][wall_col] == 1:
            return False
        
        # Check if the pattern line already has a different color
        if player.lines_tile[target_line] != -1 and player.lines_tile[target_line] != color:
            return False
        
        return True
    
    def _get_wall_column_for_color(self, color: int) -> int:
        """Get the wall column for a given color."""
        # This mapping should match the wall layout
        color_to_col = {
            0: 0,  # Blue
            1: 1,  # White
            2: 2,  # Black
            3: 3,  # Red
            4: 4   # Yellow
        }
        return color_to_col.get(color, 0)
    
    def _calculate_move_priority(self, state: AzulState, player_id: int, color: int, target_line: int, count: int) -> MovePriority:
        """Calculate the priority of a move."""
        player = state.agents[player_id]
        
        # Check if this would complete a pattern line
        current_count = player.lines_number[target_line]
        if current_count + count >= target_line + 1:
            return MovePriority.CRITICAL
        
        # Check if this would help complete a wall row or column
        wall_row = target_line
        wall_col = self._get_wall_column_for_color(color)
        
        # Check row completion potential
        row_tiles = sum(player.grid_state[wall_row])
        if row_tiles >= 4:  # Close to completing a row
            return MovePriority.HIGH
        
        # Check column completion potential
        col_tiles = sum(player.grid_state[i][wall_col] for i in range(5))
        if col_tiles >= 4:  # Close to completing a column
            return MovePriority.HIGH
        
        # Check if this is a blocking move
        if self._is_blocking_move(state, player_id, color, target_line):
            return MovePriority.HIGH
        
        # Check if this is a scoring move
        if self._is_scoring_move(state, player_id, color, target_line):
            return MovePriority.MEDIUM
        
        return MovePriority.LOW
    
    def _is_blocking_move(self, state: AzulState, player_id: int, color: int, target_line: int) -> bool:
        """Check if a move would block opponent opportunities."""
        # This is a simplified check - in practice, you'd analyze opponent positions
        return False
    
    def _is_scoring_move(self, state: AzulState, player_id: int, color: int, target_line: int) -> bool:
        """Check if a move would create scoring opportunities."""
        player = state.agents[player_id]
        wall_row = target_line
        wall_col = self._get_wall_column_for_color(color)
        
        # Check if this would create a row or column bonus
        if wall_row == 0 or wall_row == 4:  # Edge rows
            return True
        if wall_col == 0 or wall_col == 4:  # Edge columns
            return True
        
        return False
    
    def _calculate_strategic_value(self, state: AzulState, player_id: int, color: int, target_line: int) -> float:
        """Calculate the strategic value of a move."""
        value = 0.0
        
        # Base value for pattern line completion
        player = state.agents[player_id]
        current_count = player.lines_number[target_line]
        if current_count > 0:
            value += 20.0
        
        # Value for wall placement
        wall_row = target_line
        wall_col = self._get_wall_column_for_color(color)
        
        # Check row completion potential
        row_tiles = sum(player.grid_state[wall_row])
        value += row_tiles * 5.0
        
        # Check column completion potential
        col_tiles = sum(player.grid_state[i][wall_col] for i in range(5))
        value += col_tiles * 5.0
        
        # Bonus for edge positions (easier to complete)
        if wall_row in [0, 4] or wall_col in [0, 4]:
            value += 10.0
        
        return min(value, 100.0)
    
    def _calculate_move_likelihood(self, state: AzulState, player_id: int, color: int, target_line: int, count: int) -> float:
        """Calculate the likelihood of a move being chosen."""
        likelihood = 0.5  # Base likelihood
        
        # Increase likelihood for moves that complete pattern lines
        player = state.agents[player_id]
        current_count = player.lines_number[target_line]
        if current_count + count >= target_line + 1:
            likelihood += 0.3
        
        # Increase likelihood for moves that help complete wall rows/columns
        wall_row = target_line
        wall_col = self._get_wall_column_for_color(color)
        row_tiles = sum(player.grid_state[wall_row])
        col_tiles = sum(player.grid_state[i][wall_col] for i in range(5))
        
        if row_tiles >= 3 or col_tiles >= 3:
            likelihood += 0.2
        
        # Decrease likelihood for floor moves
        if target_line == -1:
            likelihood *= 0.5
        
        return min(likelihood, 1.0)
    
    def _validate_move(self, state: AzulState, player_id: int, color: int, target_line: int, count: int) -> float:
        """Validate a move and return a score."""
        if not self._is_valid_pattern_line_move(state, player_id, color, target_line):
            return 0.0
        
        # Check if the move makes strategic sense
        player = state.agents[player_id]
        wall_row = target_line
        wall_col = self._get_wall_column_for_color(color)
        
        # Check if this would create isolated tiles
        if self._would_create_isolated_tile(player, wall_row, wall_col):
            return 0.5
        
        return 1.0
    
    def _would_create_isolated_tile(self, player, wall_row: int, wall_col: int) -> bool:
        """Check if placing a tile would create an isolated tile."""
        # This is a simplified check - in practice, you'd analyze the wall structure
        return False
    
    def _filter_moves(self, moves: List[GeneratedMove], state: AzulState, player_id: int) -> List[GeneratedMove]:
        """Filter moves based on various criteria."""
        filtered_moves = []
        
        for move in moves:
            # Filter out moves with very low validation scores
            if move.validation_score < 0.1:
                continue
            
            # Filter out moves with very low strategic value
            if move.strategic_value < 5.0:
                continue
            
            # Filter out moves with very low likelihood
            if move.likelihood < 0.05:
                continue
            
            filtered_moves.append(move)
        
        self.filtered_moves += len(moves) - len(filtered_moves)
        return filtered_moves
    
    def _prioritize_moves(self, moves: List[GeneratedMove], state: AzulState, player_id: int) -> List[GeneratedMove]:
        """Prioritize moves by strategic value and likelihood."""
        # Sort by priority first, then by strategic value
        moves.sort(key=lambda m: (m.priority.value, -m.strategic_value, -m.likelihood))
        return moves
    
    def cluster_similar_moves(self, moves: List[GeneratedMove]) -> List[List[GeneratedMove]]:
        """Cluster similar moves together."""
        clusters = []
        used_moves = set()
        
        for i, move in enumerate(moves):
            if i in used_moves:
                continue
            
            cluster = [move]
            used_moves.add(i)
            
            # Find similar moves
            for j, other_move in enumerate(moves[i+1:], i+1):
                if j in used_moves:
                    continue
                
                if self._are_moves_similar(move, other_move):
                    cluster.append(other_move)
                    used_moves.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def _are_moves_similar(self, move1: GeneratedMove, move2: GeneratedMove) -> bool:
        """Check if two moves are similar."""
        # Moves are similar if they have the same color and target line
        return (move1.color == move2.color and 
                move1.target_line == move2.target_line and
                move1.move_type == move2.move_type)
    
    def generate_move_summary(self, moves: List[GeneratedMove]) -> Dict[str, Any]:
        """Generate a summary of generated moves."""
        if not moves:
            return {"error": "No moves generated"}
        
        # Count moves by type
        type_counts = {}
        for move_type in MoveType:
            type_counts[move_type.value] = len([m for m in moves if m.move_type == move_type])
        
        # Count moves by priority
        priority_counts = {}
        for priority in MovePriority:
            priority_counts[priority.name] = len([m for m in moves if m.priority == priority])
        
        # Calculate statistics
        strategic_values = [m.strategic_value for m in moves]
        likelihoods = [m.likelihood for m in moves]
        validation_scores = [m.validation_score for m in moves]
        
        summary = {
            "total_moves": len(moves),
            "type_distribution": type_counts,
            "priority_distribution": priority_counts,
            "strategic_value_stats": {
                "mean": sum(strategic_values) / len(strategic_values),
                "median": sorted(strategic_values)[len(strategic_values)//2],
                "min": min(strategic_values),
                "max": max(strategic_values)
            },
            "likelihood_stats": {
                "mean": sum(likelihoods) / len(likelihoods),
                "median": sorted(likelihoods)[len(likelihoods)//2],
                "min": min(likelihoods),
                "max": max(likelihoods)
            },
            "validation_stats": {
                "mean": sum(validation_scores) / len(validation_scores),
                "median": sorted(validation_scores)[len(validation_scores)//2],
                "min": min(validation_scores),
                "max": max(validation_scores)
            },
            "filtered_moves": self.filtered_moves,
            "filtering_rate": self.filtered_moves / max(1, self.total_moves_generated)
        }
        
        return summary

def main():
    """Main function for testing move generation."""
    # Create a sample game state
    state = AzulState(2)  # 2-player game
    
    # Initialize move generator
    generator = EnhancedMoveGenerator(max_moves_per_position=100, enable_filtering=True)
    
    # Generate moves
    moves = generator.generate_all_moves(state, 0)
    
    # Generate summary
    summary = generator.generate_move_summary(moves)
    print(json.dumps(summary, indent=2))
    
    # Cluster moves
    clusters = generator.cluster_similar_moves(moves)
    print(f"Generated {len(clusters)} move clusters")
    
    # Save moves to file for testing
    moves_data = [asdict(move) for move in moves]
    with open("../data/generated_moves.json", 'w') as f:
        json.dump(moves_data, f, indent=2)

if __name__ == "__main__":
    main() 