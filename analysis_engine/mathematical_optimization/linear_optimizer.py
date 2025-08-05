"""
Linear Programming Optimizer for Azul

This module implements linear programming optimization for Azul move selection
and scoring maximization using PuLP.
"""

import pulp
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from core.azul_model import AzulState
from core import azul_utils as utils


class OptimizationObjective(Enum):
    """Different optimization objectives for the linear optimizer."""
    MAXIMIZE_SCORING = "maximize_scoring"
    MINIMIZE_PENALTY = "minimize_penalty"
    BALANCE_SCORING_PENALTY = "balance_scoring_penalty"
    MAXIMIZE_WALL_COMPLETION = "maximize_wall_completion"
    OPTIMIZE_RESOURCE_ALLOCATION = "optimize_resource_allocation"


@dataclass
class OptimizationResult:
    """Result of a linear programming optimization."""
    objective_value: float
    optimal_moves: List[Dict[str, Any]]
    constraint_violations: List[str]
    optimization_time: float
    solver_status: str
    confidence_score: float
    recommendations: List[str]


class AzulLinearOptimizer:
    """
    Linear Programming Optimizer for Azul move optimization.
    
    Uses PuLP to solve linear programming problems for:
    - Scoring maximization
    - Penalty minimization
    - Resource allocation optimization
    - Wall completion optimization
    """
    
    def __init__(self):
        """Initialize the linear optimizer."""
        self.solver_name = 'PULP_CBC_CMD'
        self.time_limit = 30  # seconds
        self.verbose = False
        
    def optimize_scoring(self, state: AzulState, player_id: int, 
                        objective: OptimizationObjective = OptimizationObjective.MAXIMIZE_SCORING) -> OptimizationResult:
        """
        Optimize scoring potential using linear programming.
        
        Args:
            state: Current Azul game state
            player_id: Player to optimize for
            objective: Optimization objective
            
        Returns:
            OptimizationResult with optimal moves and recommendations
        """
        try:
            # Create the optimization problem
            prob = pulp.LpProblem(f"Azul_Scoring_Optimization_{objective.value}", pulp.LpMaximize)
            
            # Get player state
            player = state.agents[player_id]
            
            # Create decision variables for different move types
            move_vars = self._create_move_variables(prob, state, player_id)
            
            # Add constraints
            self._add_scoring_constraints(prob, state, player_id, move_vars)
            
            # Set objective function
            objective_func = self._create_scoring_objective(prob, state, player_id, move_vars, objective)
            prob += objective_func
            
            # Solve the problem
            solver = pulp.PULP_CBC_CMD(timeLimit=self.time_limit, msg=0)
            prob.solve(solver)
            
            # Extract results
            optimal_moves = self._extract_optimal_moves(move_vars, state, player_id)
            recommendations = self._generate_recommendations(optimal_moves, state, player_id)
            
            return OptimizationResult(
                objective_value=pulp.value(prob.objective),
                optimal_moves=optimal_moves,
                constraint_violations=[],
                optimization_time=0.0,  # TODO: Add timing
                solver_status=pulp.LpStatus[prob.status],
                confidence_score=self._calculate_confidence_score(prob, optimal_moves),
                recommendations=recommendations
            )
            
        except Exception as e:
            return OptimizationResult(
                objective_value=0.0,
                optimal_moves=[],
                constraint_violations=[f"Optimization error: {str(e)}"],
                optimization_time=0.0,
                solver_status="ERROR",
                confidence_score=0.0,
                recommendations=["Optimization failed - using fallback strategy"]
            )
    
    def _create_move_variables(self, prob: pulp.LpProblem, state: AzulState, player_id: int) -> Dict[str, pulp.LpVariable]:
        """Create decision variables for different move types."""
        move_vars = {}
        
        # Variables for factory-to-pattern-line moves
        for factory_idx in range(len(state.factories)):
            for pattern_line in range(5):
                for tile_type in utils.Tile:
                    var_name = f"factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}"
                    move_vars[var_name] = pulp.LpVariable(var_name, 0, 1, pulp.LpBinary)
        
        # Variables for center-pool-to-pattern-line moves
        for pattern_line in range(5):
            for tile_type in utils.Tile:
                var_name = f"center_line_{pattern_line}_tile_{tile_type}"
                move_vars[var_name] = pulp.LpVariable(var_name, 0, 1, pulp.LpBinary)
        
        # Variables for wall placement
        for row in range(5):
            for col in range(5):
                for tile_type in utils.Tile:
                    var_name = f"wall_{row}_{col}_tile_{tile_type}"
                    move_vars[var_name] = pulp.LpVariable(var_name, 0, 1, pulp.LpBinary)
        
        return move_vars
    
    def _add_scoring_constraints(self, prob: pulp.LpProblem, state: AzulState, 
                                player_id: int, move_vars: Dict[str, pulp.LpVariable]):
        """Add constraints to the optimization problem."""
        player = state.agents[player_id]
        
        # Constraint 1: Only one move per factory/center pool
        for factory_idx in range(len(state.factories)):
            factory_moves = []
            for pattern_line in range(5):
                for tile_type in utils.Tile:
                    var_name = f"factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}"
                    if var_name in move_vars:
                        factory_moves.append(move_vars[var_name])
            if factory_moves:
                prob += pulp.lpSum(factory_moves) <= 1, f"factory_{factory_idx}_single_move"
        
        # Constraint 2: Pattern line capacity constraints
        for pattern_line in range(5):
            line_capacity = pattern_line + 1
            current_tiles = player.lines_number[pattern_line]
            available_space = line_capacity - current_tiles
            
            if available_space > 0:
                line_moves = []
                for tile_type in utils.Tile:
                    # Factory moves to this line
                    for factory_idx in range(len(state.factories)):
                        var_name = f"factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}"
                        if var_name in move_vars:
                            line_moves.append(move_vars[var_name])
                    
                    # Center pool moves to this line
                    var_name = f"center_line_{pattern_line}_tile_{tile_type}"
                    if var_name in move_vars:
                        line_moves.append(move_vars[var_name])
                
                if line_moves:
                    prob += pulp.lpSum(line_moves) <= available_space, f"line_{pattern_line}_capacity"
        
        # Constraint 3: Wall placement constraints
        for row in range(5):
            for col in range(5):
                # Only one tile type can be placed at each wall position
                wall_moves = []
                for tile_type in utils.Tile:
                    var_name = f"wall_{row}_{col}_tile_{tile_type}"
                    if var_name in move_vars:
                        wall_moves.append(move_vars[var_name])
                if wall_moves:
                    prob += pulp.lpSum(wall_moves) <= 1, f"wall_{row}_{col}_single_tile"
        
        # Constraint 4: Tile availability constraints
        for tile_type in utils.Tile:
            total_available = 0
            # Count available tiles in factories
            for factory_idx, factory in enumerate(state.factories):
                if hasattr(factory, 'tiles') and tile_type in factory.tiles:
                    total_available += factory.tiles[tile_type]
            
            # Count available tiles in center pool
            if hasattr(state.centre_pool, 'tiles') and tile_type in state.centre_pool.tiles:
                total_available += state.centre_pool.tiles[tile_type]
            
            # Constraint on total tiles used
            tile_usage = []
            for factory_idx in range(len(state.factories)):
                for pattern_line in range(5):
                    var_name = f"factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}"
                    if var_name in move_vars:
                        tile_usage.append(move_vars[var_name])
            
            for pattern_line in range(5):
                var_name = f"center_line_{pattern_line}_tile_{tile_type}"
                if var_name in move_vars:
                    tile_usage.append(move_vars[var_name])
            
            if tile_usage:
                prob += pulp.lpSum(tile_usage) <= total_available, f"tile_{tile_type}_availability"
    
    def _create_scoring_objective(self, prob: pulp.LpProblem, state: AzulState, 
                                 player_id: int, move_vars: Dict[str, pulp.LpVariable],
                                 objective: OptimizationObjective):
        """Create the objective function for scoring optimization."""
        player = state.agents[player_id]
        objective_terms = []
        
        # Scoring coefficients for different move types
        for pattern_line in range(5):
            for tile_type in utils.Tile:
                # Wall completion bonus
                row = pattern_line
                col = self._get_tile_column(tile_type, row)
                
                if 0 <= row < 5 and 0 <= col < 5:
                    # Check if this would complete a row, column, or set
                    row_completion_bonus = self._calculate_row_completion_bonus(player, row, col, tile_type)
                    col_completion_bonus = self._calculate_column_completion_bonus(player, row, col, tile_type)
                    set_completion_bonus = self._calculate_set_completion_bonus(player, row, col, tile_type)
                    
                    total_bonus = row_completion_bonus + col_completion_bonus + set_completion_bonus
                    
                    # Add to objective for factory moves
                    for factory_idx in range(len(state.factories)):
                        var_name = f"factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}"
                        if var_name in move_vars:
                            objective_terms.append(total_bonus * move_vars[var_name])
                    
                    # Add to objective for center pool moves
                    var_name = f"center_line_{pattern_line}_tile_{tile_type}"
                    if var_name in move_vars:
                        objective_terms.append(total_bonus * move_vars[var_name])
        
        # Penalty avoidance (negative terms)
        for pattern_line in range(5):
            penalty_weight = -1  # Negative weight to minimize penalties
            for tile_type in utils.Tile:
                # Factory moves that might lead to penalties
                for factory_idx in range(len(state.factories)):
                    var_name = f"factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}"
                    if var_name in move_vars:
                        objective_terms.append(penalty_weight * move_vars[var_name])
                
                # Center pool moves that might lead to penalties
                var_name = f"center_line_{pattern_line}_tile_{tile_type}"
                if var_name in move_vars:
                    objective_terms.append(penalty_weight * move_vars[var_name])
        
        return pulp.lpSum(objective_terms) if objective_terms else 0
    
    def _get_tile_column(self, tile_type: int, row: int) -> int:
        """Get the column for a tile type in a given row."""
        # This maps tile types to their correct columns based on Azul's wall pattern
        tile_to_col = {
            utils.Tile.BLUE: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4},
            utils.Tile.WHITE: {0: 4, 1: 0, 2: 1, 3: 2, 4: 3},
            utils.Tile.BLACK: {0: 3, 1: 4, 2: 0, 3: 1, 4: 2},
            utils.Tile.RED: {0: 2, 1: 3, 2: 4, 3: 0, 4: 1},
            utils.Tile.YELLOW: {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
        }
        return tile_to_col.get(tile_type, {}).get(row, 0)
    
    def _calculate_row_completion_bonus(self, player: AzulState.AgentState, row: int, col: int, tile_type: int) -> int:
        """Calculate bonus for completing a row."""
        # Check if placing this tile would complete the row
        row_tiles = [player.grid_state[row][c] for c in range(5)]
        row_tiles[col] = tile_type
        
        if all(tile != 0 for tile in row_tiles):
            return player.ROW_BONUS
        return 0
    
    def _calculate_column_completion_bonus(self, player: AzulState.AgentState, row: int, col: int, tile_type: int) -> int:
        """Calculate bonus for completing a column."""
        # Check if placing this tile would complete the column
        col_tiles = [player.grid_state[r][col] for r in range(5)]
        col_tiles[row] = tile_type
        
        if all(tile != 0 for tile in col_tiles):
            return player.COL_BONUS
        return 0
    
    def _calculate_set_completion_bonus(self, player: AzulState.AgentState, row: int, col: int, tile_type: int) -> int:
        """Calculate bonus for completing a set of 5 tiles of the same color."""
        # Count tiles of this type across the entire wall
        tile_count = 0
        for r in range(5):
            for c in range(5):
                if player.grid_state[r][c] == tile_type:
                    tile_count += 1
        
        # If this placement would complete the set
        if tile_count == 4:  # 4 existing + 1 new = 5
            return player.SET_BONUS
        return 0
    
    def _extract_optimal_moves(self, move_vars: Dict[str, pulp.LpVariable], 
                               state: AzulState, player_id: int) -> List[Dict[str, Any]]:
        """Extract optimal moves from the solved optimization problem."""
        optimal_moves = []
        
        for var_name, var in move_vars.items():
            if var.varValue == 1:  # This move was selected
                move_info = self._parse_move_variable(var_name, state, player_id)
                if move_info:
                    optimal_moves.append(move_info)
        
        return optimal_moves
    
    def _parse_move_variable(self, var_name: str, state: AzulState, player_id: int) -> Optional[Dict[str, Any]]:
        """Parse a move variable name into move information."""
        parts = var_name.split('_')
        
        if parts[0] == 'factory':
            # Format: factory_{factory_idx}_line_{pattern_line}_tile_{tile_type}
            factory_idx = int(parts[1])
            pattern_line = int(parts[3])
            tile_type = int(parts[5])
            
            return {
                'move_type': 'factory_to_pattern_line',
                'factory_idx': factory_idx,
                'pattern_line': pattern_line,
                'tile_type': tile_type,
                'source': 'factory',
                'destination': 'pattern_line'
            }
        
        elif parts[0] == 'center':
            # Format: center_line_{pattern_line}_tile_{tile_type}
            pattern_line = int(parts[2])
            tile_type = int(parts[4])
            
            return {
                'move_type': 'center_to_pattern_line',
                'pattern_line': pattern_line,
                'tile_type': tile_type,
                'source': 'center_pool',
                'destination': 'pattern_line'
            }
        
        elif parts[0] == 'wall':
            # Format: wall_{row}_{col}_tile_{tile_type}
            row = int(parts[1])
            col = int(parts[2])
            tile_type = int(parts[4])
            
            return {
                'move_type': 'wall_placement',
                'row': row,
                'col': col,
                'tile_type': tile_type,
                'source': 'pattern_line',
                'destination': 'wall'
            }
        
        return None
    
    def _calculate_confidence_score(self, prob: pulp.LpProblem, optimal_moves: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the optimization result."""
        if prob.status != pulp.LpStatusOptimal:
            return 0.0
        
        # Base confidence on objective value and number of moves
        objective_value = pulp.value(prob.objective)
        num_moves = len(optimal_moves)
        
        # Normalize confidence based on objective value and move count
        confidence = min(1.0, max(0.0, objective_value / 100.0))  # Normalize to 0-1
        
        # Adjust based on number of moves (more moves = higher confidence)
        if num_moves > 0:
            confidence *= min(1.0, num_moves / 5.0)
        
        return confidence
    
    def _generate_recommendations(self, optimal_moves: List[Dict[str, Any]], 
                                 state: AzulState, player_id: int) -> List[str]:
        """Generate strategic recommendations based on optimal moves."""
        recommendations = []
        
        if not optimal_moves:
            recommendations.append("No optimal moves found - consider defensive play")
            return recommendations
        
        # Analyze move patterns
        factory_moves = [m for m in optimal_moves if m['move_type'] == 'factory_to_pattern_line']
        center_moves = [m for m in optimal_moves if m['move_type'] == 'center_to_pattern_line']
        wall_moves = [m for m in optimal_moves if m['move_type'] == 'wall_placement']
        
        if factory_moves:
            recommendations.append(f"Focus on factory moves: {len(factory_moves)} optimal factory selections")
        
        if center_moves:
            recommendations.append(f"Consider center pool moves: {len(center_moves)} optimal center selections")
        
        if wall_moves:
            recommendations.append(f"Plan wall placements: {len(wall_moves)} optimal wall positions")
        
        # Strategic recommendations
        if len(optimal_moves) >= 3:
            recommendations.append("Multiple high-value moves available - prioritize scoring opportunities")
        elif len(optimal_moves) == 1:
            recommendations.append("Limited optimal moves - focus on this high-value play")
        
        return recommendations
    
    def optimize_resource_allocation(self, state: AzulState, player_id: int) -> OptimizationResult:
        """
        Optimize resource allocation across different move types.
        
        Args:
            state: Current Azul game state
            player_id: Player to optimize for
            
        Returns:
            OptimizationResult with resource allocation recommendations
        """
        return self.optimize_scoring(state, player_id, OptimizationObjective.OPTIMIZE_RESOURCE_ALLOCATION)
    
    def optimize_wall_completion(self, state: AzulState, player_id: int) -> OptimizationResult:
        """
        Optimize for wall completion bonuses.
        
        Args:
            state: Current Azul game state
            player_id: Player to optimize for
            
        Returns:
            OptimizationResult with wall completion strategies
        """
        return self.optimize_scoring(state, player_id, OptimizationObjective.MAXIMIZE_WALL_COMPLETION) 