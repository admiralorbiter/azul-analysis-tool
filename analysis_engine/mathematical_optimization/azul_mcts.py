"""
Monte Carlo Tree Search (MCTS) implementation for Azul.

This module provides:
- UCT (Upper Confidence Bound for Trees) algorithm
- Pluggable rollout policies (random, heavy playout)
- Fast hint generation with < 200ms target
- Integration with existing evaluator and move generator
- Database caching for position analysis
"""

import math
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Callable
from enum import Enum

from core.azul_model import AzulState, AzulGameRule
from .azul_move_generator import FastMoveGenerator, FastMove
from .azul_evaluator import AzulEvaluator
from core.azul_database import AzulDatabase, CachedAnalysis

# Optional neural imports - temporarily disabled for testing
NEURAL_AVAILABLE = False

try:
    from neural.azul_net import create_azul_net, AzulNeuralRolloutPolicy
    NEURAL_AVAILABLE = True
except ImportError:
    # Neural components not available
    pass


class RolloutPolicy(Enum):
    """Available rollout policies for MCTS."""
    RANDOM = "random"
    HEAVY = "heavy"
    NEURAL = "neural"


@dataclass
class MCTSNode:
    """Node in the MCTS tree."""
    state: AzulState
    parent: Optional['MCTSNode'] = None
    move: Optional[FastMove] = None
    agent_id: int = 0
    
    # UCT statistics
    visits: int = 0
    total_score: float = 0.0
    
    # Children
    children: List['MCTSNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    @property
    def average_score(self) -> float:
        """Average score of this node."""
        return self.total_score / self.visits if self.visits > 0 else 0.0
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0
    
    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        # Simplified terminal check - can be enhanced
        return False  # TODO: Implement proper terminal check


@dataclass
class MCTSResult:
    """Result of MCTS search."""
    best_move: Optional[FastMove]
    best_score: float
    principal_variation: List[FastMove]
    nodes_searched: int
    search_time: float
    rollout_count: int
    average_rollout_depth: float


class RolloutPolicyBase:
    """Base class for rollout policies."""
    
    def __init__(self, evaluator: AzulEvaluator, move_generator: FastMoveGenerator):
        self.evaluator = evaluator
        self.move_generator = move_generator
    
    def rollout(self, state: AzulState, agent_id: int, max_depth: int = 50) -> float:
        """Perform a rollout from the given state."""
        raise NotImplementedError


class RandomRolloutPolicy(RolloutPolicyBase):
    """Random rollout policy."""
    
    def rollout(self, state: AzulState, agent_id: int, max_depth: int = 50) -> float:
        """Perform a random rollout."""
        current_state = state
        current_agent = agent_id
        depth = 0
        
        while depth < max_depth:
            # Check for terminal state
            if self._is_terminal(current_state):
                return self._evaluate_terminal(current_state, agent_id)
            
            # Generate moves
            moves = self.move_generator.generate_moves_fast(current_state, current_agent)
            if not moves:
                return self._evaluate_terminal(current_state, agent_id)
            
            # Select random move
            move = random.choice(moves)
            
            # Apply move
            new_state = self._apply_move(current_state, move, current_agent)
            if new_state is None:
                return self._evaluate_terminal(current_state, agent_id)
            
            current_state = new_state
            current_agent = self._get_next_agent(current_agent, current_state)
            depth += 1
        
        # Return evaluation if we reached max depth
        return self.evaluator.evaluate_position(current_state, agent_id)
    
    def _is_terminal(self, state: AzulState) -> bool:
        """Check if state is terminal."""
        # Simplified - can be enhanced
        return False
    
    def _evaluate_terminal(self, state: AzulState, agent_id: int) -> float:
        """Evaluate terminal state."""
        return self.evaluator.evaluate_position(state, agent_id)
    
    def _apply_move(self, state: AzulState, move: FastMove, agent_id: int) -> Optional[AzulState]:
        """Apply move to state."""
        try:
            new_state = state.clone()
            game_rule = AzulGameRule(len(new_state.agents))
            
            # Initialize agent traces
            for agent in new_state.agents:
                agent.agent_trace.StartRound()
            
            # Convert FastMove to tuple format
            move_tuple = (
                move.source_id,
                move.tile_type,
                move.pattern_line_dest,
                move.num_to_pattern_line,
                move.num_to_floor_line
            )
            
            # Apply move
            successor = game_rule.generateSuccessor(new_state, move_tuple, agent_id)
            return successor
        except Exception:
            return None
    
    def _get_next_agent(self, agent_id: int, state: AzulState) -> int:
        """Get next agent ID."""
        return (agent_id + 1) % len(state.agents)


class HeavyRolloutPolicy(RolloutPolicyBase):
    """Heavy playout policy using heuristic evaluation."""
    
    def rollout(self, state: AzulState, agent_id: int, max_depth: int = 50) -> float:
        """Perform a heavy playout using heuristic evaluation."""
        current_state = state
        current_agent = agent_id
        depth = 0
        
        while depth < max_depth:
            # Check for terminal state
            if self._is_terminal(current_state):
                return self._evaluate_terminal(current_state, agent_id)
            
            # Generate moves
            moves = self.move_generator.generate_moves_fast(current_state, current_agent)
            if not moves:
                return self._evaluate_terminal(current_state, agent_id)
            
            # Select best move using heuristic evaluation
            best_move = self._select_best_move(current_state, moves, current_agent)
            
            # Apply move
            new_state = self._apply_move(current_state, best_move, current_agent)
            if new_state is None:
                return self._evaluate_terminal(current_state, agent_id)
            
            current_state = new_state
            current_agent = self._get_next_agent(current_agent, current_state)
            depth += 1
        
        # Return evaluation if we reached max depth
        return self.evaluator.evaluate_position(current_state, agent_id)
    
    def _select_best_move(self, state: AzulState, moves: List[FastMove], agent_id: int) -> FastMove:
        """Select best move using heuristic evaluation."""
        best_move = moves[0]
        best_score = float('-inf')
        
        for move in moves:
            # Create temporary state to evaluate move
            temp_state = self._apply_move(state, move, agent_id)
            if temp_state is None:
                continue
            
            # Evaluate position
            score = self.evaluator.evaluate_position(temp_state, agent_id)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _is_terminal(self, state: AzulState) -> bool:
        """Check if state is terminal."""
        return False
    
    def _evaluate_terminal(self, state: AzulState, agent_id: int) -> float:
        """Evaluate terminal state."""
        return self.evaluator.evaluate_position(state, agent_id)
    
    def _apply_move(self, state: AzulState, move: FastMove, agent_id: int) -> Optional[AzulState]:
        """Apply move to state."""
        try:
            new_state = state.clone()
            game_rule = AzulGameRule(len(new_state.agents))
            
            # Initialize agent traces
            for agent in new_state.agents:
                agent.agent_trace.StartRound()
            
            # Convert FastMove to tuple format
            move_tuple = (
                move.source_id,
                move.tile_type,
                move.pattern_line_dest,
                move.num_to_pattern_line,
                move.num_to_floor_line
            )
            
            # Apply move
            successor = game_rule.generateSuccessor(new_state, move_tuple, agent_id)
            return successor
        except Exception:
            return None
    
    def _get_next_agent(self, agent_id: int, state: AzulState) -> int:
        """Get next agent ID."""
        return (agent_id + 1) % len(state.agents)


class AzulMCTS:
    """Monte Carlo Tree Search implementation for Azul."""
    
    def __init__(self, 
                 max_time: float = 0.2,
                 max_rollouts: int = 300,
                 exploration_constant: float = 1.414,
                 rollout_policy: RolloutPolicy = RolloutPolicy.RANDOM,
                 database: Optional[AzulDatabase] = None):
        """
        Initialize MCTS.
        
        Args:
            max_time: Maximum search time in seconds
            max_rollouts: Maximum number of rollouts
            exploration_constant: UCT exploration constant
            rollout_policy: Rollout policy to use
            database: Optional database for caching
        """
        self.max_time = max_time
        self.max_rollouts = max_rollouts
        self.exploration_constant = exploration_constant
        self.rollout_policy_enum = rollout_policy  # Keep the enum for tests
        self.database = database
        
        # Initialize components
        self.evaluator = AzulEvaluator()
        self.move_generator = FastMoveGenerator()
        
        # Create rollout policy
        if rollout_policy == RolloutPolicy.RANDOM:
            self._rollout_policy_instance = RandomRolloutPolicy(self.evaluator, self.move_generator)
        elif rollout_policy == RolloutPolicy.HEAVY:
            self._rollout_policy_instance = HeavyRolloutPolicy(self.evaluator, self.move_generator)
        elif rollout_policy == RolloutPolicy.NEURAL:
            if not NEURAL_AVAILABLE:
                raise ValueError(
                    "Neural rollout policy requires PyTorch. Install torch and torchvision (see requirements.txt) or enable the 'neural' extras."
                )
            # Create neural model and policy
            model, encoder = create_azul_net(device="cpu")
            self._rollout_policy_instance = AzulNeuralRolloutPolicy(
                model, encoder, self.evaluator, self.move_generator, device="cpu"
            )
        else:
            raise ValueError(f"Unknown rollout policy: {rollout_policy}")
        
        # Search statistics
        self.nodes_searched = 0
        self.rollout_count = 0
        self.search_start_time = 0.0
    
    def search(self, state: AzulState, agent_id: int, 
               max_time: Optional[float] = None,
               max_rollouts: Optional[int] = None,
               fen_string: Optional[str] = None) -> MCTSResult:
        """
        Perform MCTS search with optional database caching.
        
        Args:
            state: Current game state
            agent_id: Agent to search for
            max_time: Maximum search time (overrides instance default)
            max_rollouts: Maximum rollouts (overrides instance default)
            fen_string: Optional FEN string for caching
            
        Returns:
            MCTSResult with best move and statistics
        """
        if max_time is None:
            max_time = self.max_time
        if max_rollouts is None:
            max_rollouts = self.max_rollouts
        
        # Check cache first if database is available
        if self.database and fen_string:
            cached = self.database.get_cached_analysis(fen_string, agent_id, 'mcts')
            if cached:
                # Convert cached move string back to FastMove
                best_move = None
                if cached.best_move:
                    try:
                        best_move = FastMove.from_string(cached.best_move)
                    except:
                        pass  # If conversion fails, we'll do a fresh search
                
                if best_move is not None:
                    # Update performance stats for cache hit
                    self.database.update_performance_stats(
                        'mcts', cached.search_time, cached.nodes_searched, 
                        cached.rollout_count, cache_hit=True
                    )
                    
                    return MCTSResult(
                        best_move=best_move,
                        best_score=cached.score,
                        principal_variation=[],  # TODO: Convert cached PV
                        nodes_searched=cached.nodes_searched,
                        search_time=cached.search_time,
                        rollout_count=cached.rollout_count,
                        average_rollout_depth=0.0
                    )
        
        # Reset statistics
        self.nodes_searched = 0
        self.rollout_count = 0
        self.search_start_time = time.time()
        
        # Create root node
        root = MCTSNode(state=state, agent_id=agent_id)
        self.nodes_searched = 1  # Count root node
        
        # Perform MCTS iterations
        while (time.time() - self.search_start_time < max_time and 
               self.rollout_count < max_rollouts):
            
            # Selection and expansion
            node = self._select_and_expand(root)
            
            # Simulation
            score = self._rollout_policy_instance.rollout(node.state, node.agent_id)
            self.rollout_count += 1
            
            # Backpropagation
            self._backpropagate(node, score)
        
        # Select best move
        best_move, best_score, pv = self._select_best_move(root)
        
        search_time = time.time() - self.search_start_time
        
        # Cache result if database is available
        if self.database and fen_string:
            position_id = self.database.cache_position(fen_string, len(state.agents))
            self.database.cache_analysis(position_id, agent_id, 'mcts', {
                'best_move': str(best_move) if best_move else '',
                'best_score': best_score,
                'search_time': search_time,
                'nodes_searched': self.nodes_searched,
                'rollout_count': self.rollout_count,
                'principal_variation': [str(move) for move in pv]
            })
            
            # Update performance stats for cache miss
            self.database.update_performance_stats(
                'mcts', search_time, self.nodes_searched, 
                self.rollout_count, cache_hit=False
            )
        
        return MCTSResult(
            best_move=best_move,
            best_score=best_score,
            principal_variation=pv,
            nodes_searched=self.nodes_searched,
            search_time=search_time,
            rollout_count=self.rollout_count,
            average_rollout_depth=0.0  # TODO: Track rollout depth
        )
    
    def _select_and_expand(self, root: MCTSNode) -> MCTSNode:
        """Select a node using UCT and expand it."""
        current = root
        
        # Selection phase
        while not current.is_leaf and not current.is_terminal:
            if len(current.children) < len(self._get_moves(current.state, current.agent_id)):
                # Expand
                return self._expand(current)
            else:
                # Select best child using UCT
                current = self._select_best_child(current)
        
        # Expansion phase
        if not current.is_terminal:
            return self._expand(current)
        
        return current
    
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand a node by adding a child."""
        moves = self._get_moves(node.state, node.agent_id)
        existing_moves = {child.move for child in node.children}
        
        # Find a move that hasn't been explored
        for move in moves:
            if move not in existing_moves:
                # Create new state
                new_state = self._apply_move(node.state, move, node.agent_id)
                if new_state is None:
                    continue
                
                # Create child node
                child = MCTSNode(
                    state=new_state,
                    parent=node,
                    move=move,
                    agent_id=self._get_next_agent(node.agent_id, new_state)
                )
                
                node.children.append(child)
                self.nodes_searched += 1  # Track new node creation
                return child
        
        # If all moves are explored, return the node itself
        return node
    
    def _select_best_child(self, node: MCTSNode) -> MCTSNode:
        """Select best child using UCT formula."""
        best_child = node.children[0]
        best_uct = self._calculate_uct(best_child, node.visits)
        
        for child in node.children[1:]:
            uct = self._calculate_uct(child, node.visits)
            if uct > best_uct:
                best_uct = uct
                best_child = child
        
        return best_child
    
    def _calculate_uct(self, node: MCTSNode, parent_visits: int) -> float:
        """Calculate UCT value for a node."""
        if node.visits == 0:
            return float('inf')
        
        exploitation = node.average_score
        exploration = self.exploration_constant * math.sqrt(math.log(parent_visits) / node.visits)
        
        return exploitation + exploration
    
    def _backpropagate(self, node: MCTSNode, score: float):
        """Backpropagate score up the tree."""
        current = node
        while current is not None:
            current.visits += 1
            current.total_score += score
            current = current.parent
    
    def _select_best_move(self, root: MCTSNode) -> tuple[Optional[FastMove], float, List[FastMove]]:
        """Select best move from root node."""
        if not root.children:
            return None, 0.0, []
        
        # Select child with most visits
        best_child = max(root.children, key=lambda c: c.visits)
        
        # Build principal variation
        pv = [best_child.move] if best_child.move else []
        
        return best_child.move, best_child.average_score, pv
    
    def _get_moves(self, state: AzulState, agent_id: int) -> List[FastMove]:
        """Get legal moves for the current state."""
        return self.move_generator.generate_moves_fast(state, agent_id)
    
    def _apply_move(self, state: AzulState, move: FastMove, agent_id: int) -> Optional[AzulState]:
        """Apply move to state."""
        try:
            new_state = state.clone()
            game_rule = AzulGameRule(len(new_state.agents))
            
            # Initialize agent traces
            for agent in new_state.agents:
                agent.agent_trace.StartRound()
            
            # Convert FastMove to tuple format
            move_tuple = (
                move.source_id,
                move.tile_type,
                move.pattern_line_dest,
                move.num_to_pattern_line,
                move.num_to_floor_line
            )
            
            # Apply move
            successor = game_rule.generateSuccessor(new_state, move_tuple, agent_id)
            return successor
        except Exception:
            return None
    
    def _get_next_agent(self, agent_id: int, state: AzulState) -> int:
        """Get next agent ID."""
        return (agent_id + 1) % len(state.agents)
    
    @property
    def rollout_policy(self) -> RolloutPolicy:
        """Get the rollout policy enum for testing."""
        return self.rollout_policy_enum
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        return {
            'nodes_searched': self.nodes_searched,
            'rollout_count': self.rollout_count,
            'search_time': time.time() - self.search_start_time if self.search_start_time > 0 else 0.0,
            'rollouts_per_second': self.rollout_count / max(0.001, time.time() - self.search_start_time)
        } 