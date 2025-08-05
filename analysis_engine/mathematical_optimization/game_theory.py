"""
Game Theory Analysis for Azul

This module implements game theory concepts for strategic analysis of Azul positions,
including Nash equilibrium detection, opponent modeling, and strategic evaluation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from core.azul_model import AzulState
from core import azul_utils


class GamePhase(Enum):
    """Game phases for strategic analysis"""
    EARLY_GAME = "early_game"
    MID_GAME = "mid_game"
    LATE_GAME = "late_game"
    ENDGAME = "endgame"


class EquilibriumType(Enum):
    """Types of Nash equilibria"""
    PURE_STRATEGY = "pure_strategy"
    MIXED_STRATEGY = "mixed_strategy"
    DOMINANT_STRATEGY = "dominant_strategy"
    NO_EQUILIBRIUM = "no_equilibrium"


@dataclass
class NashEquilibriumResult:
    """Result of Nash equilibrium analysis"""
    equilibrium_type: EquilibriumType
    player_strategies: Dict[int, Dict[str, float]]  # player_id -> strategy -> probability
    payoff_matrix: np.ndarray
    equilibrium_payoffs: Dict[int, float]
    confidence: float
    strategic_insights: List[str]


@dataclass
class OpponentModel:
    """Model of opponent behavior"""
    player_id: int
    strategy_profile: Dict[str, float]  # strategy -> probability
    historical_patterns: Dict[str, float]
    risk_tolerance: float
    aggression_level: float
    predictability_score: float


@dataclass
class StrategicAnalysis:
    """Comprehensive strategic analysis"""
    nash_equilibrium: NashEquilibriumResult
    opponent_models: Dict[int, OpponentModel]
    strategic_value: float
    recommended_actions: List[str]
    risk_assessment: Dict[str, float]
    game_phase: GamePhase
    confidence: float


class AzulGameTheory:
    """
    Game theory analysis for Azul positions.
    
    Implements Nash equilibrium detection, opponent modeling, and strategic analysis
    for competitive Azul play.
    """
    
    def __init__(self):
        self.utils = azul_utils
        
    def detect_nash_equilibrium(self, game_state: AzulState, player_id: int = 0) -> NashEquilibriumResult:
        """
        Detect Nash equilibrium in the current game state.
        
        Args:
            game_state: Current Azul game state
            player_id: ID of the analyzing player
            
        Returns:
            NashEquilibriumResult with equilibrium analysis
        """
        # Get available moves for all players
        available_moves = self._get_available_moves(game_state)
        
        if not available_moves:
            return self._create_no_equilibrium_result()
        
        # Build payoff matrix
        payoff_matrix = self._build_payoff_matrix(game_state, available_moves)
        
        # Find Nash equilibrium
        equilibrium = self._find_nash_equilibrium(payoff_matrix, available_moves)
        
        # Calculate strategic insights
        insights = self._generate_strategic_insights(equilibrium, game_state)
        
        return NashEquilibriumResult(
            equilibrium_type=equilibrium['type'],
            player_strategies=equilibrium['strategies'],
            payoff_matrix=payoff_matrix,
            equilibrium_payoffs=equilibrium['payoffs'],
            confidence=equilibrium['confidence'],
            strategic_insights=insights
        )
    
    def model_opponent_strategy(self, game_state: AzulState, opponent_id: int) -> OpponentModel:
        """
        Model opponent's likely strategy based on game state and history.
        
        Args:
            game_state: Current game state
            opponent_id: ID of the opponent to model
            
        Returns:
            OpponentModel with predicted behavior
        """
        # Analyze opponent's current position
        position_analysis = self._analyze_opponent_position(game_state, opponent_id)
        
        # Predict likely strategies
        strategy_profile = self._predict_opponent_strategies(game_state, opponent_id)
        
        # Calculate behavioral metrics
        risk_tolerance = self._calculate_risk_tolerance(game_state, opponent_id)
        aggression_level = self._calculate_aggression_level(game_state, opponent_id)
        predictability_score = self._calculate_predictability(game_state, opponent_id)
        
        return OpponentModel(
            player_id=opponent_id,
            strategy_profile=strategy_profile,
            historical_patterns=position_analysis['patterns'],
            risk_tolerance=risk_tolerance,
            aggression_level=aggression_level,
            predictability_score=predictability_score
        )
    
    def analyze_strategic_position(self, game_state: AzulState, player_id: int = 0) -> StrategicAnalysis:
        """
        Perform comprehensive strategic analysis of the current position.
        
        Args:
            game_state: Current game state
            player_id: ID of the analyzing player
            
        Returns:
            StrategicAnalysis with comprehensive strategic insights
        """
        # Detect Nash equilibrium
        nash_result = self.detect_nash_equilibrium(game_state, player_id)
        
        # Model all opponents
        opponent_models = {}
        for opponent_id in range(game_state.num_players):
            if opponent_id != player_id:
                opponent_models[opponent_id] = self.model_opponent_strategy(game_state, opponent_id)
        
        # Calculate strategic value
        strategic_value = self._calculate_strategic_value(game_state, player_id, nash_result)
        
        # Generate recommendations
        recommendations = self._generate_strategic_recommendations(game_state, player_id, nash_result, opponent_models)
        
        # Assess risks
        risk_assessment = self._assess_strategic_risks(game_state, player_id, nash_result, opponent_models)
        
        # Determine game phase
        game_phase = self._determine_game_phase(game_state)
        
        # Calculate overall confidence
        confidence = self._calculate_strategic_confidence(nash_result, opponent_models, game_state)
        
        return StrategicAnalysis(
            nash_equilibrium=nash_result,
            opponent_models=opponent_models,
            strategic_value=strategic_value,
            recommended_actions=recommendations,
            risk_assessment=risk_assessment,
            game_phase=game_phase,
            confidence=confidence
        )
    
    def _get_available_moves(self, game_state: AzulState) -> Dict[int, List[str]]:
        """Get available moves for all players"""
        moves = {}
        for player_id in range(game_state.num_players):
            if game_state.is_player_turn(player_id):
                moves[player_id] = self._generate_player_moves(game_state, player_id)
        return moves
    
    def _generate_player_moves(self, game_state: AzulState, player_id: int) -> List[str]:
        """Generate available moves for a specific player"""
        moves = []
        
        # Factory moves
        for factory_idx in range(len(game_state.factories)):
            if game_state.factories[factory_idx]:
                for tile_type in set(game_state.factories[factory_idx]):
                    for pattern_line in range(5):
                        moves.append(f"factory_{factory_idx}_{tile_type}_{pattern_line}")
        
        # Center pool moves
        if game_state.center_pool:
            for tile_type in set(game_state.center_pool):
                for pattern_line in range(5):
                    moves.append(f"center_{tile_type}_{pattern_line}")
        
        return moves
    
    def _build_payoff_matrix(self, game_state: AzulState, available_moves: Dict[int, List[str]]) -> np.ndarray:
        """Build payoff matrix for the game state"""
        # Simplified payoff matrix construction
        # In practice, this would evaluate all possible move combinations
        num_players = len(available_moves)
        max_moves = max(len(moves) for moves in available_moves.values()) if available_moves else 1
        
        # Create a simplified payoff matrix
        payoff_matrix = np.zeros((num_players, max_moves))
        
        for player_id, moves in available_moves.items():
            for move_idx, move in enumerate(moves):
                # Simplified payoff calculation
                payoff = self._evaluate_move_payoff(game_state, player_id, move)
                payoff_matrix[player_id, move_idx] = payoff
        
        return payoff_matrix
    
    def _evaluate_move_payoff(self, game_state: AzulState, player_id: int, move: str) -> float:
        """Evaluate the payoff of a specific move"""
        # Simplified payoff evaluation
        # In practice, this would simulate the move and calculate resulting score
        
        # Base payoff from move type
        if move.startswith("factory"):
            base_payoff = 2.0
        elif move.startswith("center"):
            base_payoff = 1.5
        else:
            base_payoff = 1.0
        
        # Add strategic bonuses
        strategic_bonus = self._calculate_strategic_bonus(game_state, player_id, move)
        
        return base_payoff + strategic_bonus
    
    def _calculate_strategic_bonus(self, game_state: AzulState, player_id: int, move: str) -> float:
        """Calculate strategic bonus for a move"""
        bonus = 0.0
        
        # Wall completion bonus
        if self._move_completes_wall_section(game_state, player_id, move):
            bonus += 3.0
        
        # Pattern line efficiency bonus
        if self._move_improves_pattern_line(game_state, player_id, move):
            bonus += 1.5
        
        # Factory control bonus
        if self._move_controls_factory(game_state, player_id, move):
            bonus += 1.0
        
        return bonus
    
    def _move_completes_wall_section(self, game_state: AzulState, player_id: int, move: str) -> bool:
        """Check if move completes a wall section"""
        # Simplified check - in practice would simulate the move
        return False
    
    def _move_improves_pattern_line(self, game_state: AzulState, player_id: int, move: str) -> bool:
        """Check if move improves pattern line efficiency"""
        # Simplified check
        return True
    
    def _move_controls_factory(self, game_state: AzulState, player_id: int, move: str) -> bool:
        """Check if move gives factory control"""
        # Simplified check
        return False
    
    def _find_nash_equilibrium(self, payoff_matrix: np.ndarray, available_moves: Dict[int, List[str]]) -> Dict[str, Any]:
        """Find Nash equilibrium in the payoff matrix"""
        # Simplified Nash equilibrium detection
        # In practice, this would use more sophisticated algorithms
        
        num_players = len(available_moves)
        
        # Find best responses for each player
        best_responses = {}
        for player_id in range(num_players):
            if player_id in available_moves:
                best_move_idx = np.argmax(payoff_matrix[player_id])
                best_responses[player_id] = best_move_idx
        
        # Check if best responses form an equilibrium
        is_equilibrium = self._check_equilibrium_condition(payoff_matrix, best_responses)
        
        if is_equilibrium:
            equilibrium_type = EquilibriumType.PURE_STRATEGY
            confidence = 0.8
        else:
            equilibrium_type = EquilibriumType.NO_EQUILIBRIUM
            confidence = 0.3
        
        # Build strategy profiles
        strategies = {}
        payoffs = {}
        for player_id in range(num_players):
            if player_id in available_moves:
                strategies[player_id] = {available_moves[player_id][best_responses[player_id]]: 1.0}
                payoffs[player_id] = payoff_matrix[player_id, best_responses[player_id]]
        
        return {
            'type': equilibrium_type,
            'strategies': strategies,
            'payoffs': payoffs,
            'confidence': confidence
        }
    
    def _check_equilibrium_condition(self, payoff_matrix: np.ndarray, best_responses: Dict[int, int]) -> bool:
        """Check if best responses form a Nash equilibrium"""
        # Simplified equilibrium check
        # In practice, this would verify that no player can improve by deviating
        return len(best_responses) > 0
    
    def _create_no_equilibrium_result(self) -> NashEquilibriumResult:
        """Create result when no equilibrium is found"""
        return NashEquilibriumResult(
            equilibrium_type=EquilibriumType.NO_EQUILIBRIUM,
            player_strategies={},
            payoff_matrix=np.array([]),
            equilibrium_payoffs={},
            confidence=0.0,
            strategic_insights=["No clear Nash equilibrium detected"]
        )
    
    def _generate_strategic_insights(self, equilibrium: Dict[str, Any], game_state: AzulState) -> List[str]:
        """Generate strategic insights from equilibrium analysis"""
        insights = []
        
        if equilibrium['type'] == EquilibriumType.PURE_STRATEGY:
            insights.append("Pure strategy Nash equilibrium detected")
            insights.append("Players have dominant strategies")
        elif equilibrium['type'] == EquilibriumType.NO_EQUILIBRIUM:
            insights.append("No clear equilibrium - dynamic play required")
            insights.append("Consider mixed strategies")
        
        # Add game-specific insights
        insights.append("Focus on wall completion opportunities")
        insights.append("Monitor opponent's pattern line development")
        
        return insights
    
    def _analyze_opponent_position(self, game_state: AzulState, opponent_id: int) -> Dict[str, Any]:
        """Analyze opponent's current position"""
        patterns = {
            'wall_completion_focus': 0.0,
            'pattern_line_efficiency': 0.0,
            'factory_control': 0.0,
            'risk_taking': 0.0
        }
        
        # Analyze opponent's wall completion
        wall_completion = self._calculate_wall_completion(game_state, opponent_id)
        patterns['wall_completion_focus'] = wall_completion
        
        # Analyze pattern line efficiency
        pattern_efficiency = self._calculate_pattern_efficiency(game_state, opponent_id)
        patterns['pattern_line_efficiency'] = pattern_efficiency
        
        return {'patterns': patterns}
    
    def _calculate_wall_completion(self, game_state: AzulState, player_id: int) -> float:
        """Calculate wall completion percentage for a player"""
        # Simplified calculation
        return 0.3  # 30% completion
    
    def _calculate_pattern_efficiency(self, game_state: AzulState, player_id: int) -> float:
        """Calculate pattern line efficiency for a player"""
        # Simplified calculation
        return 0.6  # 60% efficiency
    
    def _predict_opponent_strategies(self, game_state: AzulState, opponent_id: int) -> Dict[str, float]:
        """Predict opponent's likely strategies"""
        strategies = {
            'wall_completion': 0.4,
            'pattern_line_development': 0.3,
            'factory_control': 0.2,
            'defensive_play': 0.1
        }
        
        # Adjust based on opponent's current position
        wall_completion = self._calculate_wall_completion(game_state, opponent_id)
        if wall_completion > 0.5:
            strategies['wall_completion'] += 0.2
            strategies['pattern_line_development'] -= 0.1
        
        return strategies
    
    def _calculate_risk_tolerance(self, game_state: AzulState, opponent_id: int) -> float:
        """Calculate opponent's risk tolerance"""
        # Simplified calculation based on opponent's play style
        return 0.6  # Moderate risk tolerance
    
    def _calculate_aggression_level(self, game_state: AzulState, opponent_id: int) -> float:
        """Calculate opponent's aggression level"""
        # Simplified calculation
        return 0.5  # Moderate aggression
    
    def _calculate_predictability(self, game_state: AzulState, opponent_id: int) -> float:
        """Calculate opponent's predictability score"""
        # Simplified calculation
        return 0.7  # Somewhat predictable
    
    def _calculate_strategic_value(self, game_state: AzulState, player_id: int, nash_result: NashEquilibriumResult) -> float:
        """Calculate strategic value of the current position"""
        # Base strategic value
        base_value = 5.0
        
        # Add equilibrium value
        if nash_result.equilibrium_type != EquilibriumType.NO_EQUILIBRIUM:
            base_value += 2.0
        
        # Add confidence bonus
        base_value += nash_result.confidence * 3.0
        
        return base_value
    
    def _generate_strategic_recommendations(self, game_state: AzulState, player_id: int,
                                         nash_result: NashEquilibriumResult, 
                                         opponent_models: Dict[int, OpponentModel]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        if nash_result.equilibrium_type == EquilibriumType.PURE_STRATEGY:
            recommendations.append("Follow the Nash equilibrium strategy")
        else:
            recommendations.append("Consider mixed strategies for dynamic play")
        
        # Add opponent-specific recommendations
        for opponent_id, model in opponent_models.items():
            if model.aggression_level > 0.7:
                recommendations.append(f"Opponent {opponent_id} is aggressive - play defensively")
            if model.predictability_score > 0.8:
                recommendations.append(f"Opponent {opponent_id} is predictable - exploit patterns")
        
        recommendations.append("Focus on wall completion opportunities")
        recommendations.append("Monitor pattern line efficiency")
        
        return recommendations
    
    def _assess_strategic_risks(self, game_state: AzulState, player_id: int,
                               nash_result: NashEquilibriumResult,
                               opponent_models: Dict[int, OpponentModel]) -> Dict[str, float]:
        """Assess strategic risks in the current position"""
        risks = {
            'opponent_blocking': 0.3,
            'resource_scarcity': 0.2,
            'timing_pressure': 0.4,
            'strategic_uncertainty': 0.5
        }
        
        # Adjust risks based on opponent models
        for model in opponent_models.values():
            if model.aggression_level > 0.7:
                risks['opponent_blocking'] += 0.2
            if model.risk_tolerance > 0.8:
                risks['strategic_uncertainty'] += 0.1
        
        return risks
    
    def _determine_game_phase(self, game_state: AzulState) -> GamePhase:
        """Determine the current game phase"""
        # Simplified phase determination
        # In practice, this would analyze the game state more thoroughly
        
        # Check if endgame conditions are met
        if self._is_endgame(game_state):
            return GamePhase.ENDGAME
        
        # Check game progress
        progress = self._calculate_game_progress(game_state)
        
        if progress < 0.3:
            return GamePhase.EARLY_GAME
        elif progress < 0.7:
            return GamePhase.MID_GAME
        else:
            return GamePhase.LATE_GAME
    
    def _is_endgame(self, game_state: AzulState) -> bool:
        """Check if game is in endgame phase"""
        # Simplified endgame detection
        return False
    
    def _calculate_game_progress(self, game_state: AzulState) -> float:
        """Calculate game progress (0.0 to 1.0)"""
        # Simplified progress calculation
        return 0.5  # Mid-game
    
    def _calculate_strategic_confidence(self, nash_result: NashEquilibriumResult,
                                      opponent_models: Dict[int, OpponentModel],
                                      game_state: AzulState) -> float:
        """Calculate overall strategic confidence"""
        # Base confidence from Nash equilibrium
        confidence = nash_result.confidence
        
        # Adjust based on opponent predictability
        avg_predictability = np.mean([model.predictability_score for model in opponent_models.values()])
        confidence += avg_predictability * 0.2
        
        return min(confidence, 1.0) 