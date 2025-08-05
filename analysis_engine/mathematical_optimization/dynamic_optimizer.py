import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import time
import heapq

from core.azul_model import AzulState
from core import azul_utils as utils
from .linear_optimizer import AzulLinearOptimizer, OptimizationObjective


class EndgamePhase(Enum):
    EARLY_GAME = "early_game"  # 0-3 rounds completed
    MID_GAME = "mid_game"      # 4-7 rounds completed
    LATE_GAME = "late_game"    # 8-10 rounds completed
    ENDGAME = "endgame"        # 11+ rounds completed


@dataclass
class EndgameState:
    """Represents a state in the dynamic programming evaluation"""
    state_hash: str
    player_id: int
    depth: int
    score: float
    moves_remaining: int
    wall_completion: float
    floor_line_penalty: int
    pattern_line_efficiency: float
    factory_control: float
    opponent_blocking_potential: float


@dataclass
class MultiTurnPlan:
    """Represents an optimal multi-turn move sequence"""
    total_expected_score: float
    move_sequence: List[Dict[str, Any]]
    confidence_score: float
    risk_assessment: Dict[str, float]
    alternative_plans: List[Dict[str, Any]]
    endgame_evaluation: Dict[str, float]


class AzulDynamicOptimizer:
    """
    Dynamic programming optimizer for Azul game analysis.
    
    Implements:
    - Endgame state evaluation using dynamic programming
    - Multi-turn planning with optimal move sequences
    - State caching and memoization
    - Risk assessment and alternative planning
    """
    
    def __init__(self, max_depth: int = 5, cache_size: int = 10000):
        self.max_depth = max_depth
        self.cache_size = cache_size
        self.state_cache = {}
        self.linear_optimizer = AzulLinearOptimizer()
        
        # Endgame evaluation weights
        self.endgame_weights = {
            'wall_completion': 0.3,
            'floor_line_penalty': -0.2,
            'pattern_line_efficiency': 0.25,
            'factory_control': 0.15,
            'opponent_blocking': -0.1
        }
        
        # Multi-turn planning parameters
        self.planning_params = {
            'max_branching_factor': 10,
            'min_confidence_threshold': 0.6,
            'risk_tolerance': 0.3
        }
    
    def evaluate_endgame(self, state: AzulState, player_id: int) -> Dict[str, float]:
        """
        Evaluate the current state for endgame optimization.
        
        Args:
            state: Current game state
            player_id: Player to evaluate for
            
        Returns:
            Dictionary with endgame evaluation metrics
        """
        start_time = time.time()
        
        # Determine game phase
        game_phase = self._determine_game_phase(state)
        
        # Calculate endgame metrics
        wall_completion = self._calculate_wall_completion_score(state, player_id)
        floor_line_penalty = self._calculate_floor_line_penalty(state, player_id)
        pattern_line_efficiency = self._calculate_pattern_line_efficiency(state, player_id)
        factory_control = self._calculate_factory_control(state, player_id)
        opponent_blocking = self._calculate_opponent_blocking_potential(state, player_id)
        
        # Calculate weighted endgame score
        endgame_score = (
            wall_completion * self.endgame_weights['wall_completion'] +
            floor_line_penalty * self.endgame_weights['floor_line_penalty'] +
            pattern_line_efficiency * self.endgame_weights['pattern_line_efficiency'] +
            factory_control * self.endgame_weights['factory_control'] +
            opponent_blocking * self.endgame_weights['opponent_blocking']
        )
        
        evaluation_time = max(time.time() - start_time, 0.001)  # Ensure minimum measurable time
        
        return {
            'endgame_score': endgame_score,
            'game_phase': game_phase.value,
            'wall_completion': wall_completion,
            'floor_line_penalty': floor_line_penalty,
            'pattern_line_efficiency': pattern_line_efficiency,
            'factory_control': factory_control,
            'opponent_blocking_potential': opponent_blocking,
            'evaluation_time': evaluation_time,
            'confidence': self._calculate_endgame_confidence(state, player_id)
        }
    
    def plan_optimal_sequence(self, state: AzulState, player_id: int, 
                            turns_ahead: int = 3) -> MultiTurnPlan:
        """
        Plan optimal move sequence for multiple turns ahead.
        
        Args:
            state: Current game state
            player_id: Player to plan for
            turns_ahead: Number of turns to plan ahead
            
        Returns:
            MultiTurnPlan with optimal sequence and alternatives
        """
        start_time = time.time()
        
        # Generate possible move sequences
        move_sequences = self._generate_move_sequences(state, player_id, turns_ahead)
        
        # Evaluate each sequence
        evaluated_plans = []
        for sequence in move_sequences:
            score, confidence, risk = self._evaluate_move_sequence(sequence, state, player_id)
            evaluated_plans.append({
                'sequence': sequence,
                'score': score,
                'confidence': confidence,
                'risk': risk
            })
        
        # Sort by expected value (score * confidence - risk)
        evaluated_plans.sort(key=lambda x: x['score'] * x['confidence'] - x['risk'], reverse=True)
        
        # Select best plan
        best_plan = evaluated_plans[0] if evaluated_plans else None
        
        # Generate alternative plans
        alternative_plans = evaluated_plans[1:4] if len(evaluated_plans) > 1 else []
        
        # Calculate overall confidence and risk
        total_confidence = self._calculate_plan_confidence(evaluated_plans)
        total_risk = self._calculate_plan_risk(evaluated_plans)
        
        planning_time = time.time() - start_time
        
        return MultiTurnPlan(
            total_expected_score=best_plan['score'] if best_plan else 0.0,
            move_sequence=best_plan['sequence'] if best_plan else [],
            confidence_score=total_confidence,
            risk_assessment={
                'overall_risk': total_risk,
                'execution_risk': self._calculate_execution_risk(best_plan),
                'opponent_interference_risk': self._calculate_opponent_interference_risk(state, player_id),
                'resource_scarcity_risk': self._calculate_resource_scarcity_risk(state, player_id)
            },
            alternative_plans=alternative_plans,
            endgame_evaluation=self.evaluate_endgame(state, player_id)
        )
    
    def _determine_game_phase(self, state: AzulState) -> EndgamePhase:
        """Determine the current game phase based on round number."""
        # Use round attribute if available, otherwise calculate from agent trace
        if hasattr(state, 'round') and state.round is not None:
            current_round = state.round
        elif hasattr(state, 'agents') and state.agents:
            # Get the first agent's trace to determine round
            agent = state.agents[0]
            if hasattr(agent, 'agent_trace') and agent.agent_trace:
                current_round = len(agent.agent_trace.actions)
            else:
                current_round = 0
        else:
            current_round = 0
        
        if current_round <= 3:
            return EndgamePhase.EARLY_GAME
        elif current_round <= 7:
            return EndgamePhase.MID_GAME
        elif current_round <= 10:
            return EndgamePhase.LATE_GAME
        else:
            return EndgamePhase.ENDGAME
    
    def _calculate_wall_completion_score(self, state: AzulState, player_id: int) -> float:
        """Calculate wall completion score for endgame evaluation."""
        agent_state = state.agents[player_id]
        grid_state = agent_state.grid_state
        
        # Count completed rows, columns, and sets
        completed_rows = sum(1 for row in range(5) if all(grid_state[row][col] == 1 for col in range(5)))
        completed_columns = sum(1 for col in range(5) if all(grid_state[row][col] == 1 for row in range(5)))
        
        # Count tiles placed
        total_tiles = sum(1 for row in range(5) for col in range(5) if grid_state[row][col] == 1)
        completion_percentage = total_tiles / 25.0
        
        # Count completed sets (all 5 tiles of same color)
        completed_sets = 0
        for tile_color in range(5):  # 5 tile colors
            tiles_of_color = sum(1 for row in range(5) for col in range(5) 
                               if grid_state[row][col] == 1 and agent_state.grid_scheme[row][tile_color] == col)
            if tiles_of_color >= 5:
                completed_sets += 1
        
        # Weighted score
        score = (
            completed_rows * 2.0 +
            completed_columns * 7.0 +
            completed_sets * 10.0 +
            completion_percentage * 50.0
        )
        
        return score
    
    def _calculate_floor_line_penalty(self, state: AzulState, player_id: int) -> int:
        """Calculate current floor line penalty."""
        agent_state = state.agents[player_id]
        floor_tiles = agent_state.floor_tiles
        
        # Calculate penalty based on floor line tiles
        penalty = 0
        for i, tile in enumerate(floor_tiles):
            penalty += (i + 1) * 1  # -1, -2, -3, etc.
        
        return penalty
    
    def _calculate_pattern_line_efficiency(self, state: AzulState, player_id: int) -> float:
        """Calculate pattern line efficiency score."""
        agent_state = state.agents[player_id]
        lines_number = agent_state.lines_number
        lines_tile = agent_state.lines_tile
        
        efficiency_score = 0.0
        
        for row_idx in range(5):
            if lines_tile[row_idx] != -1:  # Pattern line has tiles
                # Calculate how efficiently this pattern line is being used
                tiles_in_line = lines_number[row_idx]
                max_capacity = row_idx + 1
                efficiency = min(tiles_in_line / max_capacity, 1.0)  # Cap at 1.0
                
                # Bonus for near-completion
                if tiles_in_line == max_capacity - 1:
                    efficiency += 0.5
                
                efficiency_score += efficiency
        
        return efficiency_score / 5.0  # Normalize by number of pattern lines
    
    def _calculate_factory_control(self, state: AzulState, player_id: int) -> float:
        """Calculate factory control score."""
        # Analyze available tiles in factories
        available_tiles = []
        for factory in state.factories:
            if factory and hasattr(factory, 'tiles'):
                # Extract tiles from TileDisplay.tiles dictionary
                for tile_type, count in factory.tiles.items():
                    if count > 0:
                        available_tiles.extend([tile_type] * count)
        
        if not available_tiles:
            return 0.0
        
        # Calculate diversity and quantity of available tiles
        tile_counts = {}
        for tile in available_tiles:
            tile_counts[tile] = tile_counts.get(tile, 0) + 1
        
        # Score based on tile diversity and quantity
        diversity_score = len(tile_counts) / 5.0  # 5 colors
        quantity_score = min(sum(tile_counts.values()) / 20.0, 1.0)  # Normalize
        
        return (diversity_score + quantity_score) / 2.0
    
    def _calculate_opponent_blocking_potential(self, state: AzulState, player_id: int) -> float:
        """Calculate potential for opponent blocking."""
        blocking_potential = 0.0
        
        for other_player_id in range(len(state.agents)):
            if other_player_id != player_id:
                other_agent = state.agents[other_player_id]
                
                # Check if opponent can block key moves
                for row_idx in range(5):
                    if other_agent.lines_tile[row_idx] != -1:  # Pattern line has tiles
                        # Opponent has tiles in pattern line - potential blocking
                        blocking_potential += other_agent.lines_number[row_idx] * 0.1
        
        return min(blocking_potential, 1.0)
    
    def _calculate_endgame_confidence(self, state: AzulState, player_id: int) -> float:
        """Calculate confidence in endgame evaluation."""
        # Base confidence on game phase and available information
        game_phase = self._determine_game_phase(state)
        
        phase_confidence = {
            EndgamePhase.EARLY_GAME: 0.3,
            EndgamePhase.MID_GAME: 0.5,
            EndgamePhase.LATE_GAME: 0.7,
            EndgamePhase.ENDGAME: 0.9
        }
        
        base_confidence = phase_confidence[game_phase]
        
        # Adjust based on wall completion
        wall_completion = self._calculate_wall_completion_score(state, player_id)
        completion_bonus = min(wall_completion / 100.0, 0.2)
        
        return min(base_confidence + completion_bonus, 1.0)
    
    def _generate_move_sequences(self, state: AzulState, player_id: int, 
                               turns_ahead: int) -> List[List[Dict[str, Any]]]:
        """Generate possible move sequences for multi-turn planning."""
        sequences = []
        
        # Use BFS to explore move sequences
        queue = deque([([], state, 0)])  # (sequence, current_state, depth)
        
        while queue and len(sequences) < self.planning_params['max_branching_factor'] * 10:
            current_sequence, current_state, depth = queue.popleft()
            
            if depth >= turns_ahead:
                sequences.append(current_sequence)
                continue
            
            # Generate possible moves for current state
            possible_moves = self._generate_possible_moves(current_state, player_id)
            
            for move in possible_moves[:self.planning_params['max_branching_factor']]:
                # Apply move to create new state
                new_state = self._apply_move(current_state, move, player_id)
                if new_state:
                    new_sequence = current_sequence + [move]
                    queue.append((new_sequence, new_state, depth + 1))
        
        return sequences[:self.planning_params['max_branching_factor']]
    
    def _generate_possible_moves(self, state: AzulState, player_id: int) -> List[Dict[str, Any]]:
        """Generate possible moves for the current state."""
        moves = []
        
        # Generate moves for each factory
        for factory_idx, factory in enumerate(state.factories):
            if factory and hasattr(factory, 'tiles'):
                for color, count in factory.tiles.items():
                    if count > 0:
                        # Generate move to pattern line
                        for pattern_line_idx in range(5):
                            move = {
                                'type': 'factory_to_pattern',
                                'factory_idx': factory_idx,
                                'color': color,
                                'pattern_line_idx': pattern_line_idx,
                                'player_id': player_id
                            }
                            moves.append(move)
                        
                        # Generate move to floor line
                        move = {
                            'type': 'factory_to_floor',
                            'factory_idx': factory_idx,
                            'color': color,
                            'player_id': player_id
                        }
                        moves.append(move)
        
        return moves
    
    def _apply_move(self, state: AzulState, move: Dict[str, Any], player_id: int) -> Optional[AzulState]:
        """Apply a move to create a new state."""
        try:
            # Create a copy of the state
            new_state = AzulState(len(state.agents))
            
            # Copy agent states
            for i, agent in enumerate(state.agents):
                new_state.agents[i].score = agent.score
                new_state.agents[i].lines_number = agent.lines_number[:]
                new_state.agents[i].lines_tile = agent.lines_tile[:]
                new_state.agents[i].grid_state = agent.grid_state.copy()
                new_state.agents[i].floor = agent.floor[:]
                new_state.agents[i].floor_tiles = agent.floor_tiles[:]
                new_state.agents[i].number_of = agent.number_of.copy()
                new_state.agents[i].grid_scheme = agent.grid_scheme.copy()
            
            # Copy factories
            for i, factory in enumerate(state.factories):
                new_factory = new_state.TileDisplay()
                if hasattr(factory, 'tiles'):
                    for tile_type, count in factory.tiles.items():
                        if count > 0:
                            new_factory.AddTiles(count, tile_type)
                new_state.factories[i] = new_factory
            
            # Copy center pool
            new_state.centre_pool.tiles = state.centre_pool.tiles.copy()
            new_state.centre_pool.total = state.centre_pool.total
            
            # Apply the move
            if move['type'] == 'factory_to_pattern':
                factory_idx = move['factory_idx']
                color = move['color']
                pattern_line_idx = move['pattern_line_idx']
                
                # Remove tiles from factory TileDisplay
                tiles_to_remove = new_state.factories[factory_idx].tiles.get(color, 0)
                if tiles_to_remove > 0:
                    new_state.factories[factory_idx].RemoveTiles(tiles_to_remove, color)
                    
                    # Add tiles to pattern line
                    for _ in range(tiles_to_remove):
                        if new_state.agents[player_id].lines_number[pattern_line_idx] < pattern_line_idx + 1:
                            new_state.agents[player_id].AddToPatternLine(pattern_line_idx, 1, color)
            
            elif move['type'] == 'factory_to_floor':
                factory_idx = move['factory_idx']
                color = move['color']
                
                # Remove tiles from factory TileDisplay
                tiles_to_remove = new_state.factories[factory_idx].tiles.get(color, 0)
                if tiles_to_remove > 0:
                    new_state.factories[factory_idx].RemoveTiles(tiles_to_remove, color)
                    
                    # Add tiles to floor line
                    for _ in range(tiles_to_remove):
                        new_state.agents[player_id].AddToFloor([color])
            
            return new_state
            
        except Exception:
            return None
    
    def _evaluate_move_sequence(self, sequence: List[Dict[str, Any]], 
                               initial_state: AzulState, player_id: int) -> Tuple[float, float, float]:
        """Evaluate a move sequence for score, confidence, and risk."""
        if not sequence:
            return 0.0, 0.0, 0.0
        
        # Apply sequence to get final state
        current_state = initial_state
        for move in sequence:
            current_state = self._apply_move(current_state, move, player_id)
            if not current_state:
                return 0.0, 0.0, 1.0  # High risk if move application fails
        
        # Evaluate final state
        endgame_eval = self.evaluate_endgame(current_state, player_id)
        score = endgame_eval['endgame_score']
        confidence = endgame_eval['confidence']
        
        # Calculate risk based on sequence complexity and state changes
        risk = self._calculate_sequence_risk(sequence, initial_state, player_id)
        
        return score, confidence, risk
    
    def _calculate_sequence_risk(self, sequence: List[Dict[str, Any]], 
                               state: AzulState, player_id: int) -> float:
        """Calculate risk associated with a move sequence."""
        risk = 0.0
        
        # Risk increases with sequence length
        risk += len(sequence) * 0.05
        
        # Risk for floor line moves
        floor_moves = sum(1 for move in sequence if move['type'] == 'factory_to_floor')
        risk += floor_moves * 0.1
        
        # Risk for complex pattern line moves
        pattern_moves = sum(1 for move in sequence if move['type'] == 'factory_to_pattern')
        risk += pattern_moves * 0.02
        
        return min(risk, 1.0)
    
    def _calculate_plan_confidence(self, evaluated_plans: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for a plan."""
        if not evaluated_plans:
            return 0.0
        
        # Weighted average of individual confidences
        total_weight = 0.0
        weighted_sum = 0.0
        
        for i, plan in enumerate(evaluated_plans):
            weight = 1.0 / (i + 1)  # Decreasing weight for alternatives
            weighted_sum += plan['confidence'] * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_plan_risk(self, evaluated_plans: List[Dict[str, Any]]) -> float:
        """Calculate overall risk for a plan."""
        if not evaluated_plans:
            return 1.0
        
        # Average risk across all plans
        total_risk = sum(plan['risk'] for plan in evaluated_plans)
        return total_risk / len(evaluated_plans)
    
    def _calculate_execution_risk(self, plan: Optional[Dict[str, Any]]) -> float:
        """Calculate execution risk for a specific plan."""
        if not plan:
            return 1.0
        
        # Execution risk based on plan complexity
        sequence_length = len(plan['sequence'])
        return min(sequence_length * 0.1, 1.0)
    
    def _calculate_opponent_interference_risk(self, state: AzulState, player_id: int) -> float:
        """Calculate risk of opponent interference."""
        risk = 0.0
        
        # Check if opponents have similar goals
        for other_player_id in range(len(state.agents)):
            if other_player_id != player_id:
                other_agent = state.agents[other_player_id]
                
                # Risk if opponent has similar pattern line goals
                for row_idx in range(5):
                    if other_agent.lines_tile[row_idx] != -1:  # Pattern line has tiles
                        risk += 0.05
        
        return min(risk, 1.0)
    
    def _calculate_resource_scarcity_risk(self, state: AzulState, player_id: int) -> float:
        """Calculate risk due to resource scarcity."""
        # Count available tiles
        available_tiles = []
        for factory in state.factories:
            if factory and hasattr(factory, 'tiles'):
                for tile_type, count in factory.tiles.items():
                    if count > 0:
                        available_tiles.extend([tile_type] * count)
        
        if not available_tiles:
            return 1.0  # High risk if no tiles available
        
        # Risk based on tile diversity
        unique_tiles = len(set(available_tiles))
        diversity_risk = 1.0 - (unique_tiles / 5.0)  # 5 colors
        
        # Risk based on total tile quantity
        quantity_risk = max(0, 1.0 - (len(available_tiles) / 20.0))
        
        return (diversity_risk + quantity_risk) / 2.0 