"""
Azul Heuristic Evaluator - A4 Implementation

This module provides fast heuristic evaluation for Azul positions with:
- Immediate score calculation
- Pattern potential estimation
- Penalty estimation
- O(1) performance target
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from core import azul_utils as utils
from core.azul_model import AzulState


class AzulEvaluator:
    """
    Fast heuristic evaluator for Azul positions.
    
    Features:
    - Immediate score calculation
    - Pattern potential estimation
    - Penalty estimation
    - O(1) performance target
    """
    
    def __init__(self):
        # Pre-compute scoring tables for efficiency
        self._init_scoring_tables()
    
    def _init_scoring_tables(self):
        """Initialize pre-computed scoring tables."""
        # Pattern line completion bonuses
        self._pattern_completion_bonuses = {
            1: 1,   # 1 tile in pattern line = 1 point
            2: 3,   # 2 tiles = 3 points
            3: 6,   # 3 tiles = 6 points
            4: 10,  # 4 tiles = 10 points
            5: 15   # 5 tiles = 15 points
        }
        
        # Floor penalty scores
        self._floor_penalties = [-1, -1, -2, -2, -2, -3, -3]
        
        # Grid completion bonuses
        self._row_bonus = 2
        self._col_bonus = 7
        self._set_bonus = 10
    
    def evaluate_position(self, state: AzulState, agent_id: int) -> float:
        """
        Evaluate a position for the given agent.
        
        Args:
            state: Current game state
            agent_id: Agent to evaluate for
            
        Returns:
            Heuristic score (higher is better for the agent)
        """
        agent_state = state.agents[agent_id]
        
        # Calculate immediate score
        immediate_score = self._calculate_immediate_score(agent_state)
        
        # Calculate pattern potential
        pattern_potential = self._calculate_pattern_potential(agent_state)
        
        # Calculate penalty estimation
        penalty_estimation = self._calculate_penalty_estimation(agent_state)
        
        # Calculate endgame bonuses
        endgame_bonuses = self._calculate_endgame_bonuses(agent_state)
        
        # Combine all components
        total_score = immediate_score + pattern_potential + penalty_estimation + endgame_bonuses
        
        return total_score
    
    def _calculate_immediate_score(self, agent_state) -> float:
        """Calculate immediate score from completed tiles and bonuses."""
        score = 0.0
        
        # Score from completed pattern lines
        for pattern_line in range(agent_state.GRID_SIZE):
            if agent_state.lines_number[pattern_line] == pattern_line + 1:
                # Pattern line is full, score it
                score += float(self._pattern_completion_bonuses[pattern_line + 1])
        
        # Score from floor penalties
        floor_tiles = len(agent_state.floor_tiles)
        if floor_tiles > 0:
            score += float(sum(self._floor_penalties[:floor_tiles]))
        
        return score
    
    def _calculate_pattern_potential(self, agent_state) -> float:
        """Calculate potential score from pattern lines that can be completed."""
        potential = 0
        
        for pattern_line in range(agent_state.GRID_SIZE):
            tiles_in_line = agent_state.lines_number[pattern_line]
            if tiles_in_line > 0:
                # Estimate potential based on how close to completion
                completion_ratio = tiles_in_line / (pattern_line + 1)
                potential += completion_ratio * self._pattern_completion_bonuses[pattern_line + 1] * 0.5
        
        return potential
    
    def _calculate_penalty_estimation(self, agent_state) -> float:
        """Estimate future penalties based on current state."""
        penalty_estimation = 0
        
        # Estimate penalties from floor tiles
        floor_tiles = len(agent_state.floor_tiles)
        if floor_tiles > 0:
            # Assume some additional floor tiles will be added
            estimated_additional_floor = min(2, 7 - floor_tiles)  # Conservative estimate
            penalty_estimation += sum(self._floor_penalties[floor_tiles:floor_tiles + estimated_additional_floor])
        
        return penalty_estimation
    
    def _calculate_endgame_bonuses(self, agent_state) -> float:
        """Calculate endgame bonuses for completed rows, columns, and sets."""
        bonuses = 0
        
        # Check for completed rows
        completed_rows = self._count_completed_rows(agent_state)
        bonuses += completed_rows * self._row_bonus
        
        # Check for completed columns
        completed_cols = self._count_completed_columns(agent_state)
        bonuses += completed_cols * self._col_bonus
        
        # Check for completed sets
        completed_sets = self._count_completed_sets(agent_state)
        bonuses += completed_sets * self._set_bonus
        
        return bonuses
    
    def _count_completed_rows(self, agent_state) -> int:
        """Count completed rows in the grid."""
        completed = 0
        
        for row in range(agent_state.GRID_SIZE):
            # Use faster method: check if all elements are 1
            if np.all(agent_state.grid_state[row]):
                completed += 1
        
        return completed
    
    def _count_completed_columns(self, agent_state) -> int:
        """Count completed columns in the grid."""
        completed = 0
        
        for col in range(agent_state.GRID_SIZE):
            # Use faster method: check if all elements are 1
            if np.all(agent_state.grid_state[:, col]):
                completed += 1
        
        return completed
    
    def _count_completed_sets(self, agent_state) -> int:
        """Count completed sets (all tiles of one color)."""
        completed = 0
        
        for tile_type in utils.Tile:
            if agent_state.number_of.get(tile_type, 0) >= 5:
                completed += 1
        
        return completed
    
    def evaluate_move(self, state: AzulState, agent_id: int, move) -> float:
        """
        Evaluate a specific move by simulating its execution.
        
        Args:
            state: Current game state
            agent_id: Agent to evaluate for
            move: Move to evaluate
            
        Returns:
            Score after executing the move
        """
        # Get current score
        current_score = self.evaluate_position(state, agent_id)
        
        # Calculate move impact (simplified - just add pattern line potential)
        move_bonus = 0.0
        
        if move.pattern_line_dest >= 0:
            # Add potential score for pattern line placement
            pattern_line = move.pattern_line_dest
            tiles_in_line = state.agents[agent_id].lines_number[pattern_line]
            new_tiles = tiles_in_line + move.num_to_pattern_line
            
            if new_tiles <= pattern_line + 1:  # Valid placement
                # Estimate potential score
                completion_ratio = new_tiles / (pattern_line + 1)
                move_bonus += completion_ratio * self._pattern_completion_bonuses[pattern_line + 1] * 0.3
        
        if move.num_to_floor_line > 0:
            # Penalty for floor tiles
            move_bonus -= move.num_to_floor_line * 1.0
        
        return current_score + move_bonus
    
    def get_move_scores(self, state: AzulState, agent_id: int, moves: List) -> List[float]:
        """
        Get scores for a list of moves.
        
        Args:
            state: Current game state
            agent_id: Agent to evaluate for
            moves: List of moves to evaluate
            
        Returns:
            List of scores corresponding to the moves
        """
        scores = []
        for move in moves:
            score = self.evaluate_move(state, agent_id, move)
            scores.append(score)
        
        return scores
    
    def rank_moves(self, state: AzulState, agent_id: int, moves: List) -> List[Tuple[float, int]]:
        """
        Rank moves by their heuristic scores.
        
        Args:
            state: Current game state
            agent_id: Agent to evaluate for
            moves: List of moves to rank
            
        Returns:
            List of (score, move_index) tuples, sorted by score (descending)
        """
        scores = self.get_move_scores(state, agent_id, moves)
        ranked_moves = [(score, i) for i, score in enumerate(scores)]
        ranked_moves.sort(reverse=True)  # Higher scores first
        
        return ranked_moves
    
    def get_best_move(self, state: AzulState, agent_id: int, moves: List) -> Optional[int]:
        """
        Get the index of the best move according to heuristic evaluation.
        
        Args:
            state: Current game state
            agent_id: Agent to evaluate for
            moves: List of moves to evaluate
            
        Returns:
            Index of the best move, or None if no moves provided
        """
        if not moves:
            return None
        
        ranked_moves = self.rank_moves(state, agent_id, moves)
        return ranked_moves[0][1]  # Return index of best move
    
    def get_position_features(self, state: AzulState, agent_id: int) -> Dict[str, float]:
        """
        Extract position features for analysis.
        
        Args:
            state: Current game state
            agent_id: Agent to evaluate for
            
        Returns:
            Dictionary of position features
        """
        agent_state = state.agents[agent_id]
        
        features = {
            'immediate_score': self._calculate_immediate_score(agent_state),
            'pattern_potential': self._calculate_pattern_potential(agent_state),
            'penalty_estimation': self._calculate_penalty_estimation(agent_state),
            'endgame_bonuses': self._calculate_endgame_bonuses(agent_state),
            'completed_rows': self._count_completed_rows(agent_state),
            'completed_columns': self._count_completed_columns(agent_state),
            'completed_sets': self._count_completed_sets(agent_state),
            'floor_tiles': len(agent_state.floor_tiles),
            'pattern_line_tiles': sum(agent_state.lines_number),
            'grid_tiles': np.sum(agent_state.grid_state)
        }
        
        return features 