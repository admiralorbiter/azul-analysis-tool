#!/usr/bin/env python3
"""
Build Move Quality Database - Simplified Version

This script analyzes positions using your existing engines to build a comprehensive
database of what constitutes "good" moves in Azul.

Uses your existing:
- AzulAlphaBetaSearch (exact analysis)
- AzulMCTS (probabilistic analysis) 
- Pattern detection systems
- Move quality assessment
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import time
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Import your actual modules
from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS
from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator

# Import pattern detection systems
from analysis_engine.comprehensive_patterns.azul_patterns import AzulPatternDetector
from analysis_engine.comprehensive_patterns.azul_scoring_optimization import AzulScoringOptimizationDetector
from analysis_engine.comprehensive_patterns.azul_floor_line_patterns import AzulFloorLinePatternDetector

# Import move quality assessment
from analysis_engine.move_quality.azul_move_quality_assessor import AzulMoveQualityAssessor

# Import state conversion utilities
from api.utils.state_parser import state_to_fen

@dataclass
class MoveQualityData:
    """Data structure for move quality information."""
    position_fen: str
    move_data: Dict[str, Any]
    alpha_beta_score: Optional[float]
    mcts_score: Optional[float]
    pattern_score: Optional[float]
    quality_tier: str
    strategic_reasoning: str
    tactical_factors: List[str]
    risk_assessment: str
    created_at: float

class MoveQualityDatabaseBuilder:
    """Builds a comprehensive database of move quality data."""
    
    def __init__(self, db_path: str = "data/move_quality.db"):
        self.db_path = db_path
        
        # Initialize engines
        self.alpha_beta = AzulAlphaBetaSearch(max_time=2.0)
        self.mcts = AzulMCTS(max_time=0.2, max_rollouts=100)
        self.evaluator = AzulEvaluator()
        
        # Initialize pattern detectors
        self.pattern_detector = AzulPatternDetector()
        self.scoring_detector = AzulScoringOptimizationDetector()
        self.floor_line_detector = AzulFloorLinePatternDetector()
        
        # Initialize move quality assessor
        self.move_quality_assessor = AzulMoveQualityAssessor()
        
        # Initialize move generator
        self.move_generator = FastMoveGenerator()
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the move quality database schema."""
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS move_quality_data (
                    id INTEGER PRIMARY KEY,
                    position_fen TEXT NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON
                    alpha_beta_score REAL,
                    mcts_score REAL,
                    pattern_score REAL,
                    quality_tier TEXT NOT NULL,
                    strategic_reasoning TEXT,
                    tactical_factors TEXT,  -- JSON array
                    risk_assessment TEXT,
                    created_at REAL NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_move_quality_position ON move_quality_data(position_fen);
                CREATE INDEX IF NOT EXISTS idx_move_quality_tier ON move_quality_data(quality_tier);
                CREATE INDEX IF NOT EXISTS idx_move_quality_created ON move_quality_data(created_at DESC);
            """)
    
    def analyze_position(self, state: AzulState, agent_id: int = 0) -> List[MoveQualityData]:
        """Analyze a position and return quality data for all moves."""
        
        # Get legal moves
        moves = self.move_generator.generate_moves_fast(state, agent_id)
        if not moves:
            return []
        
        results = []
        
        for move in moves[:10]:  # Limit to first 10 moves for testing
            try:
                # Analyze with Alpha-Beta
                ab_result = self._analyze_alpha_beta(state, agent_id)
                
                # Analyze with MCTS
                mcts_result = self._analyze_mcts(state, agent_id)
                
                # Analyze with pattern detection
                pattern_score = self._analyze_patterns(state, move, agent_id)
                
                # Get move quality assessment
                quality_assessment = self._get_move_quality(state, move, agent_id)
                
                # Create quality data
                quality_data = MoveQualityData(
                    position_fen=state_to_fen(state),
                    move_data=self._move_to_dict(move),
                    alpha_beta_score=ab_result.best_score if ab_result else None,
                    mcts_score=mcts_result.best_score if mcts_result else None,
                    pattern_score=pattern_score,
                    quality_tier=quality_assessment.quality_tier.value if quality_assessment else "=",
                    strategic_reasoning=quality_assessment.explanation if quality_assessment else "Standard move",
                    tactical_factors=quality_assessment.pattern_connections if quality_assessment else [],
                    risk_assessment=f"Risk: {quality_assessment.risk_assessment:.1f}" if quality_assessment else "Low risk",
                    created_at=time.time()
                )
                
                results.append(quality_data)
                
            except Exception as e:
                print(f"Error analyzing move {move}: {e}")
                continue
        
        return results
    
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
    
    def _analyze_patterns(self, state: AzulState, move, agent_id: int) -> float:
        """Analyze patterns for the move."""
        try:
            # Get pattern detection results
            patterns = self.pattern_detector.detect_patterns(state, agent_id)
            scoring = self.scoring_detector.detect_scoring_optimization(state, agent_id)
            floor_line = self.floor_line_detector.detect_floor_line_patterns(state, agent_id)
            
            # Calculate pattern score (simplified)
            pattern_score = 0.0
            
            # Check blocking opportunities
            if patterns and hasattr(patterns, 'blocking_opportunities'):
                pattern_score += len(patterns.blocking_opportunities) * 0.5
            
            # Check scoring opportunities
            if scoring and hasattr(scoring, 'wall_completion_opportunities'):
                pattern_score += len(scoring.wall_completion_opportunities) * 0.3
            
            # Check floor line opportunities
            if floor_line and hasattr(floor_line, 'risk_mitigation_opportunities'):
                pattern_score += len(floor_line.risk_mitigation_opportunities) * 0.2
            
            return pattern_score
            
        except Exception as e:
            print(f"Pattern analysis failed: {e}")
            return 0.0
    
    def _get_move_quality(self, state: AzulState, move, agent_id: int):
        """Get move quality assessment."""
        try:
            # Convert move object to move key string
            move_key = self._move_to_key(move)
            return self.move_quality_assessor.assess_move_quality(state, agent_id, move_key)
        except Exception as e:
            print(f"Move quality assessment failed: {e}")
            return None
    
    def _move_to_key(self, move) -> str:
        """Convert move object to key string."""
        try:
            # Create a simple key from move attributes
            if hasattr(move, 'tile_type') and hasattr(move, 'pattern_line_dest'):
                return f"factory_{getattr(move, 'source_id', 0)}_tile_{move.tile_type}_pattern_line_{move.pattern_line_dest}"
            else:
                return str(move)
        except Exception:
            return str(move)
    
    def _move_to_dict(self, move) -> Dict[str, Any]:
        """Convert move object to dictionary."""
        if hasattr(move, '__dict__'):
            return move.__dict__
        else:
            return {'move': str(move)}
    
    def save_move_quality_data(self, data: MoveQualityData):
        """Save move quality data to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO move_quality_data (
                    position_fen, move_data, alpha_beta_score, mcts_score, 
                    pattern_score, quality_tier, strategic_reasoning,
                    tactical_factors, risk_assessment, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.position_fen,
                json.dumps(data.move_data),
                data.alpha_beta_score,
                data.mcts_score,
                data.pattern_score,
                data.quality_tier,
                data.strategic_reasoning,
                json.dumps(data.tactical_factors),
                data.risk_assessment,
                data.created_at
            ))
    
    def build_database_from_positions(self, positions: List[AzulState], agent_id: int = 0):
        """Build database from a list of positions."""
        print(f"Building move quality database from {len(positions)} positions...")
        
        total_moves_analyzed = 0
        
        for i, position in enumerate(positions):
            print(f"Analyzing position {i+1}/{len(positions)}...")
            
            try:
                move_data_list = self.analyze_position(position, agent_id)
                
                for move_data in move_data_list:
                    self.save_move_quality_data(move_data)
                    total_moves_analyzed += 1
                
                print(f"  Analyzed {len(move_data_list)} moves")
                
            except Exception as e:
                print(f"  Error analyzing position: {e}")
        
        print(f"Database building complete! Analyzed {total_moves_analyzed} moves total.")

def main():
    """Main function to build the move quality database."""
    builder = MoveQualityDatabaseBuilder()
    
    # Create test positions
    test_positions = []
    
    # Initial position
    initial_state = AzulState(2)  # 2-player game
    test_positions.append(initial_state)
    
    # Add a few more test positions with some tiles
    for i in range(3):
        state = AzulState(2)
        # Add some tiles to factories (simplified)
        for factory_id in range(min(3, len(state.factories))):
            if factory_id < len(state.factories):
                # Add some tiles to this factory using the correct method
                tile_type = (i + factory_id) % 5  # 0-4 for tile types
                state.factories[factory_id].AddTiles(2, tile_type)
        test_positions.append(state)
    
    # Build the database
    builder.build_database_from_positions(test_positions)
    
    print("Move quality database built successfully!")
    print(f"Database saved to: {builder.db_path}")

if __name__ == "__main__":
    main()
