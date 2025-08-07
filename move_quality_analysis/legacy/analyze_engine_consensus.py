#!/usr/bin/env python3
"""
Engine Consensus Analysis

This script analyzes positions using multiple engines to identify high-quality moves
based on engine agreement. When multiple engines agree on a move, it's likely to be good.
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from core.azul_model import AzulState
from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS, RolloutPolicy
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator

@dataclass
class EngineConsensus:
    """Results from multi-engine consensus analysis."""
    position_fen: str
    best_moves: Dict[str, Any]  # Engine -> move
    scores: Dict[str, float]     # Engine -> score
    consensus_move: Optional[Any]
    consensus_score: float
    agreement_level: float  # 0.0 to 1.0
    confidence: float

class EngineConsensusAnalyzer:
    """Analyzes positions using multiple engines to find consensus."""
    
    def __init__(self):
        # Initialize all engines
        self.alpha_beta = AzulAlphaBetaSearch(max_time=2.0)
        self.mcts = AzulMCTS(max_time=0.2, max_rollouts=100)
        self.neural_mcts = AzulMCTS(
            max_time=0.2, 
            max_rollouts=100,
            rollout_policy=RolloutPolicy.NEURAL
        )
        self.evaluator = AzulEvaluator()
    
    def analyze_consensus(self, state: AzulState, agent_id: int = 0) -> EngineConsensus:
        """Analyze position with all engines and find consensus."""
        
        # Analyze with each engine
        ab_result = self._analyze_alpha_beta(state, agent_id)
        mcts_result = self._analyze_mcts(state, agent_id)
        neural_result = self._analyze_neural(state, agent_id)
        
        # Collect results
        best_moves = {}
        scores = {}
        
        if ab_result:
            best_moves['alpha_beta'] = ab_result.best_move
            scores['alpha_beta'] = ab_result.best_score
        
        if mcts_result:
            best_moves['mcts'] = mcts_result.best_move
            scores['mcts'] = mcts_result.best_score
        
        if neural_result:
            best_moves['neural'] = neural_result.best_move
            scores['neural'] = neural_result.best_score
        
        # Find consensus
        consensus_move, agreement_level = self._find_consensus(best_moves)
        consensus_score = self._calculate_consensus_score(scores)
        confidence = self._calculate_confidence(scores, agreement_level)
        
        return EngineConsensus(
            position_fen=state.to_fen_string(),
            best_moves=best_moves,
            scores=scores,
            consensus_move=consensus_move,
            consensus_score=consensus_score,
            agreement_level=agreement_level,
            confidence=confidence
        )
    
    def _analyze_alpha_beta(self, state: AzulState, agent_id: int):
        """Analyze with Alpha-Beta search."""
        try:
            return self.alpha_beta.search(state, agent_id, max_depth=3, max_time=2.0)
        except Exception as e:
            print(f"Alpha-Beta analysis failed: {e}")
            return None
    
    def _analyze_mcts(self, state: AzulState, agent_id: int):
        """Analyze with MCTS."""
        try:
            return self.mcts.search(state, agent_id)
        except Exception as e:
            print(f"MCTS analysis failed: {e}")
            return None
    
    def _analyze_neural(self, state: AzulState, agent_id: int):
        """Analyze with Neural MCTS."""
        try:
            return self.neural_mcts.search(state, agent_id)
        except Exception as e:
            print(f"Neural MCTS analysis failed: {e}")
            return None
    
    def _find_consensus(self, best_moves: Dict[str, Any]) -> tuple[Optional[Any], float]:
        """Find consensus move and agreement level."""
        if not best_moves:
            return None, 0.0
        
        # Count votes for each move
        move_votes = {}
        for engine, move in best_moves.items():
            move_str = str(move) if move else None
            if move_str:
                move_votes[move_str] = move_votes.get(move_str, 0) + 1
        
        if not move_votes:
            return None, 0.0
        
        # Find most voted move
        consensus_move_str = max(move_votes, key=move_votes.get)
        votes = move_votes[consensus_move_str]
        total_engines = len(best_moves)
        
        # Convert back to move object
        consensus_move = None
        for engine, move in best_moves.items():
            if str(move) == consensus_move_str:
                consensus_move = move
                break
        
        agreement_level = votes / total_engines
        return consensus_move, agreement_level
    
    def _calculate_consensus_score(self, scores: Dict[str, float]) -> float:
        """Calculate consensus score from engine scores."""
        if not scores:
            return 0.0
        
        # Weighted average based on agreement
        total_score = sum(scores.values())
        return total_score / len(scores)
    
    def _calculate_confidence(self, scores: Dict[str, float], agreement_level: float) -> float:
        """Calculate confidence in the consensus."""
        if not scores:
            return 0.0
        
        # Base confidence on agreement level and score consistency
        score_variance = self._calculate_score_variance(scores)
        consistency_factor = 1.0 - min(score_variance, 1.0)
        
        # Combine agreement and consistency
        confidence = (agreement_level * 0.7) + (consistency_factor * 0.3)
        return min(confidence, 1.0)
    
    def _calculate_score_variance(self, scores: Dict[str, float]) -> float:
        """Calculate variance in scores."""
        if len(scores) < 2:
            return 0.0
        
        values = list(scores.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return min(variance / 10.0, 1.0)  # Normalize to 0-1

def main():
    """Example usage of engine consensus analysis."""
    analyzer = EngineConsensusAnalyzer()
    
    # Create a test position
    from core.azul_model import AzulState
    state = AzulState()
    
    # Analyze consensus
    consensus = analyzer.analyze_consensus(state)
    
    print("Engine Consensus Analysis Results:")
    print(f"Position: {consensus.position_fen[:50]}...")
    print(f"Consensus Move: {consensus.consensus_move}")
    print(f"Consensus Score: {consensus.consensus_score:.2f}")
    print(f"Agreement Level: {consensus.agreement_level:.2f}")
    print(f"Confidence: {consensus.confidence:.2f}")
    print(f"Engine Scores: {consensus.scores}")

if __name__ == "__main__":
    main()
