"""
Azul Alpha-Beta Search - A5 Implementation with A8 Endgame Integration

This module provides alpha-beta search for Azul with:
- Iterative deepening with transposition tables
- Move ordering heuristics (wall-completion >> penalty-free >> others)
- Performance target: depth-3 < 4s
- Integration with existing evaluator and move generator
- A8: Endgame solver integration for exact solutions
"""

import time
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState, AzulGameRule
from .azul_evaluator import AzulEvaluator
from .azul_move_generator import FastMoveGenerator, FastMove
from .azul_endgame import EndgameDatabase


@dataclass
class SearchResult:
    """Result of a search operation."""
    best_move: Optional[FastMove]
    best_score: float
    principal_variation: List[FastMove]
    nodes_searched: int
    search_time: float
    depth_reached: int
    alpha: float
    beta: float


class TranspositionTable:
    """Transposition table for caching search results."""
    
    def __init__(self, max_size: int = 1000000):
        self.max_size = max_size
        self.table: Dict[int, Dict] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, hash_key: int, depth: int, alpha: float, beta: float) -> Optional[Tuple[float, FastMove]]:
        """Get cached result if available and valid."""
        if hash_key in self.table:
            entry = self.table[hash_key]
            if entry['depth'] >= depth:
                self.hits += 1
                return entry['score'], entry['best_move']
        self.misses += 1
        return None
    
    def put(self, hash_key: int, depth: int, score: float, best_move: FastMove, 
            alpha: float, beta: float, node_type: str):
        """Store search result in transposition table."""
        if len(self.table) >= self.max_size:
            # Simple replacement: remove oldest entry
            oldest_key = next(iter(self.table))
            del self.table[oldest_key]
        
        self.table[hash_key] = {
            'depth': depth,
            'score': score,
            'best_move': best_move,
            'alpha': alpha,
            'beta': beta,
            'node_type': node_type  # EXACT, LOWER_BOUND, UPPER_BOUND
        }
    
    def clear(self):
        """Clear the transposition table."""
        self.table.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get transposition table statistics."""
        return {
            'size': len(self.table),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }


class AzulAlphaBetaSearch:
    """
    Alpha-beta search implementation for Azul.
    
    Features:
    - Iterative deepening
    - Transposition table
    - Move ordering heuristics
    - Time management
    - Performance monitoring
    """
    
    def __init__(self, max_depth: int = 10, max_time: float = 4.0, use_endgame: bool = True):
        self.max_depth = max_depth
        self.max_time = max_time
        self.use_endgame = use_endgame
        self.evaluator = AzulEvaluator()
        self.move_generator = FastMoveGenerator()
        self.transposition_table = TranspositionTable()
        self.endgame_database = EndgameDatabase(max_tiles=20) if use_endgame else None
        # Don't initialize game_rules here - we'll create it when needed
        
        # Search statistics
        self.nodes_searched = 0
        self.search_start_time = 0
        self.killer_moves: List[List[FastMove]] = [[] for _ in range(max_depth)]
        self.history_table: Dict[Tuple[int, int], int] = {}  # (move_hash, depth) -> count
    
    def search(self, state: AzulState, agent_id: int, max_depth: Optional[int] = None, 
               max_time: Optional[float] = None) -> SearchResult:
        """
        Perform iterative deepening alpha-beta search.
        
        Args:
            state: Current game state
            agent_id: Agent to search for
            max_depth: Maximum search depth (overrides instance default)
            max_time: Maximum search time in seconds (overrides instance default)
            
        Returns:
            SearchResult with best move and principal variation
        """
        if max_depth is None:
            max_depth = self.max_depth
        if max_time is None:
            max_time = self.max_time
        
        # Reset search statistics
        self.nodes_searched = 0
        self.search_start_time = time.time()
        self.max_time = max_time  # Update the instance max_time
        self.transposition_table.clear()
        
        # Initialize result
        best_move = None
        best_score = float('-inf')
        principal_variation = []
        depth_reached = 0
        
        # Iterative deepening
        for depth in range(1, max_depth + 1):
            # Check time limit
            if time.time() - self.search_start_time > max_time:
                break
            
            # Perform search at current depth
            result = self._alpha_beta_search(state, agent_id, depth, float('-inf'), float('inf'), True)
            
            if result is not None:
                best_move = result['best_move']
                best_score = result['score']
                principal_variation = result['pv']
                depth_reached = depth
                
                # Early termination if we found a winning move
                if best_score > 1000:
                    break
            else:
                # Time limit exceeded during search
                break
        
        search_time = time.time() - self.search_start_time
        
        return SearchResult(
            best_move=best_move,
            best_score=best_score,
            principal_variation=principal_variation,
            nodes_searched=self.nodes_searched,
            search_time=search_time,
            depth_reached=depth_reached,
            alpha=float('-inf'),
            beta=float('inf')
        )
    
    def _alpha_beta_search(self, state: AzulState, agent_id: int, depth: int, 
                          alpha: float, beta: float, is_maximizing: bool) -> Optional[Dict]:
        """
        Recursive alpha-beta search implementation.
        
        Args:
            state: Current game state
            agent_id: Agent to search for
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            is_maximizing: True if maximizing player's turn
            
        Returns:
            Dictionary with search result or None if time limit exceeded
        """
        # Check time limit
        if time.time() - self.search_start_time > self.max_time:
            return None
        
        # Check for game end (simplified)
        if self._is_game_end(state):
            return self._evaluate_terminal_state(state, agent_id)
        
        # A8: Check for endgame database solution
        if self.use_endgame and self.endgame_database and self.endgame_database.has_solution(state):
            endgame_solution = self.endgame_database.get_solution(state)
            if endgame_solution and endgame_solution.get('exact', False):
                return {
                    'best_move': endgame_solution['best_move'],
                    'score': endgame_solution['score'],
                    'pv': [endgame_solution['best_move']] if endgame_solution['best_move'] else [],
                    'exact': True
                }
        
        # Check transposition table
        hash_key = state.get_zobrist_hash()
        tt_result = self.transposition_table.get(hash_key, depth, alpha, beta)
        if tt_result is not None:
            score, best_move = tt_result
            return {
                'score': score,
                'best_move': best_move,
                'pv': [best_move] if best_move else []
            }
        
        # If we've reached the search depth limit, evaluate the position
        if depth == 0:
            return self._evaluate_position(state, agent_id)
        
        # Generate moves
        moves = self.move_generator.generate_moves_fast(state, agent_id)
        if not moves:
            return self._evaluate_terminal_state(state, agent_id)
        
        # Order moves for better pruning
        ordered_moves = self._order_moves(state, agent_id, moves, depth)
        
        best_move = None
        best_score = float('-inf') if is_maximizing else float('inf')
        principal_variation = []
        
        # Search each move
        valid_moves_searched = 0
        for move in ordered_moves:
            # Check time limit more frequently
            if time.time() - self.search_start_time > self.max_time:
                return None
            
            # Apply move
            new_state = self._apply_move(state, move, agent_id)
            if new_state is None:
                continue
            
            valid_moves_searched += 1
            
            # Recursive search
            result = self._alpha_beta_search(
                new_state, 
                self._get_next_agent(agent_id, state), 
                depth - 1, 
                alpha, 
                beta, 
                not is_maximizing
            )
            
            if result is None:  # Time limit exceeded
                return None
            
            score = result['score']
            
            # Update best move
            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                    principal_variation = [move] + result['pv']
                    alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    principal_variation = [move] + result['pv']
                    beta = min(beta, score)
            
            # Alpha-beta pruning
            if alpha >= beta:
                # Store killer move
                if depth < len(self.killer_moves):
                    if move not in self.killer_moves[depth]:
                        self.killer_moves[depth].insert(0, move)
                        if len(self.killer_moves[depth]) > 2:
                            self.killer_moves[depth] = self.killer_moves[depth][:2]
                break
        
        # If no valid moves were found, evaluate the current position
        if valid_moves_searched == 0:
            return self._evaluate_position(state, agent_id)
        
        # Update node count
        self.nodes_searched += 1
        
        # Store in transposition table
        node_type = 'EXACT'
        if best_score <= alpha:
            node_type = 'UPPER_BOUND'
        elif best_score >= beta:
            node_type = 'LOWER_BOUND'
        
        self.transposition_table.put(hash_key, depth, best_score, best_move, alpha, beta, node_type)
        
        return {
            'score': best_score,
            'best_move': best_move,
            'pv': principal_variation
        }
    
    def _evaluate_terminal_state(self, state: AzulState, agent_id: int) -> Dict:
        """Evaluate terminal state (game end)."""
        # Calculate final scores
        scores = []
        for i, agent in enumerate(state.agents):
            agent.EndOfGameScore()
            scores.append(agent.score)
        
        # Return relative score for the agent
        agent_score = scores[agent_id]
        opponent_score = max(scores[i] for i in range(len(scores)) if i != agent_id)
        
        return {
            'score': agent_score - opponent_score,
            'best_move': None,
            'pv': []
        }
    
    def _is_game_end(self, state: AzulState) -> bool:
        """Check if the game has ended (simplified version)."""
        # Check if any player has completed a row
        for agent in state.agents:
            completed_rows = agent.GetCompletedRows()
            if completed_rows > 0:
                return True
        return False
    
    def _evaluate_position(self, state: AzulState, agent_id: int) -> Dict:
        """Evaluate a non-terminal position using the heuristic evaluator."""
        score = self.evaluator.evaluate_position(state, agent_id)
        return {
            'score': score,
            'best_move': None,
            'pv': []
        }
    
    def _order_moves(self, state: AzulState, agent_id: int, moves: List[FastMove], depth: int) -> List[FastMove]:
        """Order moves for better alpha-beta pruning."""
        if not moves:
            return moves
        
        # Score moves for ordering
        move_scores = []
        for i, move in enumerate(moves):
            score = self._score_move_for_ordering(state, agent_id, move, depth)
            move_scores.append((score, i, move))
        
        # Sort by score (descending)
        move_scores.sort(reverse=True)
        
        return [move for _, _, move in move_scores]
    
    def _score_move_for_ordering(self, state: AzulState, agent_id: int, move: FastMove, depth: int) -> float:
        """Score a move for ordering purposes."""
        score = 0.0
        
        # Prioritize wall-completion moves
        if move.pattern_line_dest >= 0:
            agent_state = state.agents[agent_id]
            pattern_line = move.pattern_line_dest
            tiles_in_line = agent_state.lines_number[pattern_line]
            tiles_needed = pattern_line + 1
            
            if tiles_in_line + move.num_to_pattern_line >= tiles_needed:
                score += 1000  # High priority for completion
        
        # Prioritize penalty-free moves
        if move.num_to_floor_line == 0:
            score += 100
        
        # Use history heuristic
        move_hash = hash(move)
        history_score = self.history_table.get((move_hash, depth), 0)
        score += history_score
        
        # Use killer move heuristic
        if depth < len(self.killer_moves) and move in self.killer_moves[depth]:
            score += 50
        
        return score
    
    def _apply_move(self, state: AzulState, move: FastMove, agent_id: int) -> Optional[AzulState]:
        """Apply a move to the state and return new state."""
        try:
            # Convert FastMove to action tuple
            action = move.to_tuple()
            
            # Create game rules and apply move
            new_state = state.clone()
            
            # Initialize agent traces if needed
            for agent in new_state.agents:
                if not hasattr(agent, 'agent_trace') or agent.agent_trace is None:
                    agent.agent_trace = utils.AgentTrace(agent.id)
                if len(agent.agent_trace.actions) == 0:
                    agent.agent_trace.StartRound()
            
            game_rules = AzulGameRule(len(state.agents))
            game_rules.generateSuccessor(new_state, action, agent_id)
            
            return new_state
        except Exception as e:
            # Move was invalid, skip it
            return None
    
    def _get_next_agent(self, current_agent: int, state: AzulState) -> int:
        """Get the next agent to play."""
        # Simple round-robin for now
        return (current_agent + 1) % len(state.agents)
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        tt_stats = self.transposition_table.get_stats()
        
        return {
            'nodes_searched': self.nodes_searched,
            'search_time': time.time() - self.search_start_time if self.search_start_time > 0 else 0,
            'nodes_per_second': self.nodes_searched / max(0.001, time.time() - self.search_start_time),
            'transposition_table': tt_stats,
            'killer_moves': [len(killers) for killers in self.killer_moves],
            'history_table_size': len(self.history_table)
        }
    
    def clear_search_stats(self):
        """Clear search statistics."""
        self.nodes_searched = 0
        self.search_start_time = 0
        self.killer_moves = [[] for _ in range(self.max_depth)]
        self.history_table.clear()
        self.transposition_table.clear()
    
    def analyze_endgame(self, state: AzulState, agent_id: int) -> Optional[Dict]:
        """
        Analyze an endgame position using the endgame database.
        
        Args:
            state: Current game state
            agent_id: Agent to analyze for
            
        Returns:
            Endgame solution dict or None if not an endgame position
        """
        if not self.use_endgame or not self.endgame_database:
            return None
        
        return self.endgame_database.analyze_endgame(state, max_depth=10)
    
    def get_endgame_stats(self) -> Dict:
        """Get endgame database statistics."""
        if not self.use_endgame or not self.endgame_database:
            return {'enabled': False}
        
        stats = self.endgame_database.get_stats()
        stats['enabled'] = True
        return stats 