#!/usr/bin/env python3
"""
Build Move Quality Database

This script analyzes positions using multiple engines to build a comprehensive
database of what constitutes "good" moves in Azul.

Uses consensus between Alpha-Beta, MCTS, and Neural MCTS to identify high-quality moves.
"""

import json
import time
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS, RolloutPolicy
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator
from core.azul_database import AzulDatabase

@dataclass
class MoveQualityData:
    """Data structure for move quality information."""
    position_fen: str
    move_data: Dict[str, Any]
    alpha_beta_score: Optional[float]
    mcts_score: Optional[float]
    neural_score: Optional[float]
    consensus_score: float
    quality_tier: str
    strategic_reasoning: str
    tactical_factors: List[str]
    risk_assessment: str
    created_at: float

class MoveQualityDatabaseBuilder:
    """Builds a comprehensive database of move quality data."""
    
    def __init__(self, db_path: str = "data/move_quality.db"):
        self.db_path = db_path
        self.database = AzulDatabase()
        
        # Initialize engines
        self.alpha_beta = AzulAlphaBetaSearch(max_time=2.0)
        self.mcts = AzulMCTS(max_time=0.2, max_rollouts=100)
        self.neural_mcts = AzulMCTS(
            max_time=0.2, 
            max_rollouts=100,
            rollout_policy=RolloutPolicy.NEURAL
        )
        self.evaluator = AzulEvaluator()
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the move quality database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS move_quality_data (
                    id INTEGER PRIMARY KEY,
                    position_fen TEXT NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON
                    alpha_beta_score REAL,
                    mcts_score REAL,
                    neural_score REAL,
                    consensus_score REAL NOT NULL,
                    quality_tier TEXT NOT NULL,
                    strategic_reasoning TEXT,
                    tactical_factors TEXT,  -- JSON array
                    risk_assessment TEXT,
                    created_at REAL NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_move_quality_position ON move_quality_data(position_fen);
                CREATE INDEX IF NOT EXISTS idx_move_quality_tier ON move_quality_data(quality_tier);
                CREATE INDEX IF NOT EXISTS idx_move_quality_consensus ON move_quality_data(consensus_score DESC);
                CREATE INDEX IF NOT EXISTS idx_move_quality_created ON move_quality_data(created_at DESC);
            """)
    
    def analyze_position_consensus(self, state: AzulState, agent_id: int = 0) -> MoveQualityData:
        """Analyze a position using all three engines and find consensus."""
        
        # Get legal moves
        moves = self._get_legal_moves(state, agent_id)
        if not moves:
            return None
        
        # Analyze with each engine
        alpha_beta_result = self._analyze_alpha_beta(state, agent_id)
        mcts_result = self._analyze_mcts(state, agent_id)
        neural_result = self._analyze_neural(state, agent_id)
        
        # Find consensus move
        consensus_move = self._find_consensus_move(
            moves, alpha_beta_result, mcts_result, neural_result
        )
        
        # Calculate consensus score
        consensus_score = self._calculate_consensus_score(
            consensus_move, alpha_beta_result, mcts_result, neural_result
        )
        
        # Determine quality tier
        quality_tier = self._determine_quality_tier(consensus_score)
        
        # Generate strategic reasoning
        strategic_reasoning = self._generate_strategic_reasoning(
            consensus_move, state, agent_id
        )
        
        # Identify tactical factors
        tactical_factors = self._identify_tactical_factors(
            consensus_move, state, agent_id
        )
        
        # Assess risk
        risk_assessment = self._assess_risk(consensus_move, state, agent_id)
        
        return MoveQualityData(
            position_fen=state.to_fen_string(),
            move_data=consensus_move.__dict__ if consensus_move else {},
            alpha_beta_score=alpha_beta_result.best_score if alpha_beta_result else None,
            mcts_score=mcts_result.best_score if mcts_result else None,
            neural_score=neural_result.best_score if neural_result else None,
            consensus_score=consensus_score,
            quality_tier=quality_tier,
            strategic_reasoning=strategic_reasoning,
            tactical_factors=tactical_factors,
            risk_assessment=risk_assessment,
            created_at=time.time()
        )
    
    def _get_legal_moves(self, state: AzulState, agent_id: int) -> List:
        """Get legal moves for the current state."""
        from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
        generator = FastMoveGenerator()
        return generator.generate_moves_fast(state, agent_id)
    
    def _analyze_alpha_beta(self, state: AzulState, agent_id: int):
        """Analyze position with Alpha-Beta search."""
        try:
            return self.alpha_beta.search(state, agent_id, max_depth=3, max_time=2.0)
        except Exception as e:
            print(f"Alpha-Beta analysis failed: {e}")
            return None
    
    def _analyze_mcts(self, state: AzulState, agent_id: int):
        """Analyze position with MCTS."""
        try:
            return self.mcts.search(state, agent_id)
        except Exception as e:
            print(f"MCTS analysis failed: {e}")
            return None
    
    def _analyze_neural(self, state: AzulState, agent_id: int):
        """Analyze position with Neural MCTS."""
        try:
            return self.neural_mcts.search(state, agent_id)
        except Exception as e:
            print(f"Neural MCTS analysis failed: {e}")
            return None
    
    def _find_consensus_move(self, moves, ab_result, mcts_result, neural_result):
        """Find the move that has the most agreement between engines."""
        move_scores = {}
        
        # Score moves based on engine preferences
        if ab_result and ab_result.best_move:
            move_scores[str(ab_result.best_move)] = move_scores.get(str(ab_result.best_move), 0) + 1
        
        if mcts_result and mcts_result.best_move:
            move_scores[str(mcts_result.best_move)] = move_scores.get(str(mcts_result.best_move), 0) + 1
        
        if neural_result and neural_result.best_move:
            move_scores[str(neural_result.best_move)] = move_scores.get(str(neural_result.best_move), 0) + 1
        
        # Return move with highest consensus
        if move_scores:
            best_move_str = max(move_scores, key=move_scores.get)
            # Convert back to move object
            for move in moves:
                if str(move) == best_move_str:
                    return move
        
        # Fallback to first move if no consensus
        return moves[0] if moves else None
    
    def _calculate_consensus_score(self, move, ab_result, mcts_result, neural_result) -> float:
        """Calculate a consensus score based on engine agreement."""
        scores = []
        
        if ab_result:
            scores.append(ab_result.best_score)
        if mcts_result:
            scores.append(mcts_result.best_score)
        if neural_result:
            scores.append(neural_result.best_score)
        
        if not scores:
            return 0.0
        
        # Calculate weighted average (more engines = higher confidence)
        return sum(scores) / len(scores) * (len(scores) / 3.0)
    
    def _determine_quality_tier(self, consensus_score: float) -> str:
        """Determine quality tier based on consensus score."""
        if consensus_score >= 8.0:
            return "!!"  # Brilliant
        elif consensus_score >= 5.0:
            return "!"   # Excellent
        elif consensus_score >= 2.0:
            return "="   # Good
        elif consensus_score >= -2.0:
            return "?!"  # Dubious
        else:
            return "?"   # Poor
    
    def _generate_strategic_reasoning(self, move, state: AzulState, agent_id: int) -> str:
        """Generate strategic reasoning for the move."""
        if not move:
            return "No legal moves available"
        
        # Analyze the move's strategic implications
        reasoning = []
        
        # Check for blocking opportunities
        if self._is_blocking_move(move, state, agent_id):
            reasoning.append("Blocks opponent's scoring opportunity")
        
        # Check for scoring opportunities
        if self._is_scoring_move(move, state, agent_id):
            reasoning.append("Creates scoring opportunity")
        
        # Check for floor line management
        if self._is_floor_line_move(move, state, agent_id):
            reasoning.append("Manages floor line penalties")
        
        # Check for wall completion
        if self._is_wall_completion_move(move, state, agent_id):
            reasoning.append("Advances wall completion")
        
        if not reasoning:
            reasoning.append("Standard tactical move")
        
        return "; ".join(reasoning)
    
    def _identify_tactical_factors(self, move, state: AzulState, agent_id: int) -> List[str]:
        """Identify tactical factors for the move."""
        factors = []
        
        # Add tactical analysis based on move characteristics
        if move and hasattr(move, 'tile_type'):
            factors.append(f"Tile type: {move.tile_type}")
        
        if move and hasattr(move, 'pattern_line_dest'):
            factors.append(f"Pattern line: {move.pattern_line_dest}")
        
        if move and hasattr(move, 'num_to_floor_line'):
            if move.num_to_floor_line > 0:
                factors.append(f"Floor line tiles: {move.num_to_floor_line}")
        
        return factors
    
    def _assess_risk(self, move, state: AzulState, agent_id: int) -> str:
        """Assess the risk level of the move."""
        if not move:
            return "No risk (no moves available)"
        
        risk_factors = []
        
        # Check for floor line risk
        if hasattr(move, 'num_to_floor_line') and move.num_to_floor_line > 2:
            risk_factors.append("High floor line penalty")
        
        # Check for pattern line overflow risk
        if hasattr(move, 'pattern_line_dest') and move.pattern_line_dest >= 0:
            # This would need more sophisticated analysis
            pass
        
        if not risk_factors:
            return "Low risk"
        elif len(risk_factors) == 1:
            return f"Medium risk: {risk_factors[0]}"
        else:
            return f"High risk: {'; '.join(risk_factors)}"
    
    def _is_blocking_move(self, move, state: AzulState, agent_id: int) -> bool:
        """Check if move blocks opponent opportunities."""
        # Simplified check - would need more sophisticated analysis
        return False
    
    def _is_scoring_move(self, move, state: AzulState, agent_id: int) -> bool:
        """Check if move creates scoring opportunities."""
        # Simplified check - would need more sophisticated analysis
        return False
    
    def _is_floor_line_move(self, move, state: AzulState, agent_id: int) -> bool:
        """Check if move involves floor line management."""
        return hasattr(move, 'num_to_floor_line') and move.num_to_floor_line > 0
    
    def _is_wall_completion_move(self, move, state: AzulState, agent_id: int) -> bool:
        """Check if move advances wall completion."""
        # Simplified check - would need more sophisticated analysis
        return False
    
    def save_move_quality_data(self, data: MoveQualityData):
        """Save move quality data to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO move_quality_data (
                    position_fen, move_data, alpha_beta_score, mcts_score, 
                    neural_score, consensus_score, quality_tier, strategic_reasoning,
                    tactical_factors, risk_assessment, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.position_fen,
                json.dumps(data.move_data),
                data.alpha_beta_score,
                data.mcts_score,
                data.neural_score,
                data.consensus_score,
                data.quality_tier,
                data.strategic_reasoning,
                json.dumps(data.tactical_factors),
                data.risk_assessment,
                data.created_at
            ))
    
    def build_database_from_positions(self, positions: List[AzulState], agent_id: int = 0):
        """Build database from a list of positions."""
        print(f"Building move quality database from {len(positions)} positions...")
        
        for i, position in enumerate(positions):
            print(f"Analyzing position {i+1}/{len(positions)}...")
            
            try:
                data = self.analyze_position_consensus(position, agent_id)
                if data:
                    self.save_move_quality_data(data)
                    print(f"  Saved: {data.quality_tier} move (consensus: {data.consensus_score:.2f})")
                else:
                    print(f"  No analysis data generated")
            except Exception as e:
                print(f"  Error analyzing position: {e}")
        
        print("Database building complete!")

def main():
    """Main function to build the move quality database."""
    builder = MoveQualityDatabaseBuilder()
    
    # Generate test positions (you can replace this with your own position generation)
    from core.azul_model import AzulState, AzulGameRule
    
    # Create some test positions
    test_positions = []
    
    # Initial position
    initial_state = AzulState()
    test_positions.append(initial_state)
    
    # Add more test positions here...
    # You can load from your position library or generate systematically
    
    # Build the database
    builder.build_database_from_positions(test_positions)
    
    print("Move quality database built successfully!")

if __name__ == "__main__":
    main()
