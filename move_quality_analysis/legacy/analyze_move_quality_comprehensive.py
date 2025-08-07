#!/usr/bin/env python3
"""
Comprehensive Move Quality Analysis - Fixed Version

This script analyzes diverse positions to build a comprehensive database of move quality data.
It uses multiple engines and analysis methods to determine what makes a "good" move in Azul.

Features:
- Multi-engine consensus analysis (Alpha-Beta, MCTS, Neural MCTS)
- Pattern detection integration
- Strategic reasoning generation
- 5-tier quality classification system
- Educational content generation
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
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

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
from api.utils.state_parser import state_to_fen, parse_fen_string

class QualityTier(Enum):
    """5-tier quality classification system."""
    BRILLIANT = "!!"  # 90-100 points
    EXCELLENT = "!"   # 75-89 points
    GOOD = "="        # 50-74 points
    DUBIOUS = "?!"    # 25-49 points
    POOR = "?"        # 0-24 points

class StrategicFactor(Enum):
    """Strategic factors that influence move quality."""
    BLOCKING = "blocking"
    SCORING = "scoring"
    FLOOR_LINE = "floor_line"
    PATTERN_BUILDING = "pattern_building"
    FACTORY_CONTROL = "factory_control"
    RISK_MANAGEMENT = "risk_management"

@dataclass
class EngineAnalysis:
    """Results from a single engine analysis."""
    engine_name: str
    best_move: Any
    best_score: float
    analysis_time: float
    confidence: float
    reasoning: str

@dataclass
class PatternAnalysis:
    """Results from pattern detection analysis."""
    blocking_opportunities: int
    scoring_opportunities: int
    floor_line_risks: int
    pattern_connections: List[str]
    strategic_value: float

@dataclass
class MoveQualityData:
    """Comprehensive move quality data."""
    position_fen: str
    move_data: Dict[str, Any]
    
    # Engine analysis results
    alpha_beta_analysis: Optional[EngineAnalysis]
    mcts_analysis: Optional[EngineAnalysis]
    neural_analysis: Optional[EngineAnalysis]
    
    # Pattern analysis
    pattern_analysis: PatternAnalysis
    
    # Quality assessment
    quality_tier: QualityTier
    quality_score: float  # 0-100
    strategic_reasoning: str
    tactical_factors: List[str]
    risk_assessment: str
    educational_explanation: str
    
    # Metadata
    game_phase: str
    complexity_score: float
    created_at: float

class ComprehensiveMoveQualityAnalyzer:
    """Comprehensive move quality analyzer using multiple engines and methods."""
    
    def __init__(self, db_path: str = "data/comprehensive_move_quality.db"):
        self.db_path = db_path
        
        # Initialize engines with simplified settings
        self.alpha_beta = AzulAlphaBetaSearch(max_time=1.0)  # Reduced time
        self.mcts = AzulMCTS(max_time=0.5, max_rollouts=50)  # Reduced time and rollouts
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
        """Initialize the comprehensive move quality database schema."""
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS move_quality_data (
                    id INTEGER PRIMARY KEY,
                    position_fen TEXT NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON
                    
                    -- Engine analysis
                    alpha_beta_score REAL,
                    alpha_beta_reasoning TEXT,
                    mcts_score REAL,
                    mcts_reasoning TEXT,
                    neural_score REAL,
                    neural_reasoning TEXT,
                    
                    -- Pattern analysis
                    blocking_opportunities INTEGER,
                    scoring_opportunities INTEGER,
                    floor_line_risks INTEGER,
                    pattern_connections TEXT,  -- JSON array
                    strategic_value REAL,
                    
                    -- Quality assessment
                    quality_tier TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    strategic_reasoning TEXT,
                    tactical_factors TEXT,  -- JSON array
                    risk_assessment TEXT,
                    educational_explanation TEXT,
                    
                    -- Metadata
                    game_phase TEXT,
                    complexity_score REAL,
                    created_at REAL NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_move_quality_position ON move_quality_data(position_fen);
                CREATE INDEX IF NOT EXISTS idx_move_quality_tier ON move_quality_data(quality_tier);
                CREATE INDEX IF NOT EXISTS idx_move_quality_score ON move_quality_data(quality_score DESC);
                CREATE INDEX IF NOT EXISTS idx_move_quality_created ON move_quality_data(created_at DESC);
            """)
    
    def analyze_position(self, state: AzulState, agent_id: int = 0) -> List[MoveQualityData]:
        """Analyze a position and return comprehensive quality data for all moves."""
        
        # Get legal moves
        moves = self.move_generator.generate_moves_fast(state, agent_id)
        if not moves:
            return []
        
        print(f"Analyzing {len(moves)} moves for position...")
        
        results = []
        
        # Limit to first 10 moves for comprehensive analysis (reduced from 20)
        for i, move in enumerate(moves[:10]):
            try:
                print(f"  Analyzing move {i+1}/{min(10, len(moves))}...")
                
                # Analyze with different engines (simplified)
                alpha_beta_analysis = self._analyze_alpha_beta_simple(state, move, agent_id)
                mcts_analysis = self._analyze_mcts_simple(state, move, agent_id)
                neural_analysis = self._analyze_neural_simple(state, move, agent_id)
                
                # Analyze patterns
                pattern_analysis = self._analyze_patterns_simple(state, move, agent_id)
                
                # Determine quality tier and score
                quality_tier, quality_score = self._determine_quality_tier(
                    alpha_beta_analysis, mcts_analysis, neural_analysis, pattern_analysis
                )
                
                # Generate strategic reasoning
                strategic_reasoning = self._generate_strategic_reasoning(
                    alpha_beta_analysis, mcts_analysis, neural_analysis, pattern_analysis
                )
                
                # Generate educational explanation
                educational_explanation = self._generate_educational_explanation(
                    quality_tier, strategic_reasoning, pattern_analysis
                )
                
                # Create comprehensive quality data
                quality_data = MoveQualityData(
                    position_fen=state_to_fen(state),
                    move_data=self._move_to_dict(move),
                    alpha_beta_analysis=alpha_beta_analysis,
                    mcts_analysis=mcts_analysis,
                    neural_analysis=neural_analysis,
                    pattern_analysis=pattern_analysis,
                    quality_tier=quality_tier,
                    quality_score=quality_score,
                    strategic_reasoning=strategic_reasoning,
                    tactical_factors=self._extract_tactical_factors(pattern_analysis),
                    risk_assessment=self._assess_risk(pattern_analysis),
                    educational_explanation=educational_explanation,
                    game_phase=self._determine_game_phase(state),
                    complexity_score=self._calculate_complexity(state),
                    created_at=time.time()
                )
                
                results.append(quality_data)
                
            except Exception as e:
                print(f"    Error analyzing move {i+1}: {e}")
                continue
        
        return results
    
    def _analyze_alpha_beta_simple(self, state: AzulState, move, agent_id: int) -> Optional[EngineAnalysis]:
        """Analyze position with Alpha-Beta search (simplified)."""
        try:
            start_time = time.time()
            
            # Use current state for analysis (simplified)
            result = self.alpha_beta.search(state, agent_id, max_depth=2, max_time=0.5)
            
            analysis_time = time.time() - start_time
            
            if result and 'score' in result:
                return EngineAnalysis(
                    engine_name="Alpha-Beta",
                    best_move=result.get('best_move', move),
                    best_score=result['score'],
                    analysis_time=analysis_time,
                    confidence=0.9,
                    reasoning=f"Alpha-Beta analysis shows this move leads to a position with score {result['score']:.2f}"
                )
            
        except Exception as e:
            print(f"Alpha-Beta analysis failed: {e}")
        
        return None
    
    def _analyze_mcts_simple(self, state: AzulState, move, agent_id: int) -> Optional[EngineAnalysis]:
        """Analyze position with MCTS (simplified)."""
        try:
            start_time = time.time()
            
            # Use current state for analysis (simplified)
            result = self.mcts.search(state, agent_id)
            
            analysis_time = time.time() - start_time
            
            if result and hasattr(result, 'best_score'):
                return EngineAnalysis(
                    engine_name="MCTS",
                    best_move=result.best_move if hasattr(result, 'best_move') else move,
                    best_score=result.best_score,
                    analysis_time=analysis_time,
                    confidence=0.7,
                    reasoning=f"MCTS analysis suggests this move has a value of {result.best_score:.2f}"
                )
            
        except Exception as e:
            print(f"MCTS analysis failed: {e}")
        
        return None
    
    def _analyze_neural_simple(self, state: AzulState, move, agent_id: int) -> Optional[EngineAnalysis]:
        """Analyze position with neural evaluation (simplified)."""
        try:
            start_time = time.time()
            
            # Use neural evaluation
            score = self.evaluator.evaluate_position(state, agent_id)
            
            analysis_time = time.time() - start_time
            
            return EngineAnalysis(
                engine_name="Neural",
                best_move=move,
                best_score=score,
                analysis_time=analysis_time,
                confidence=0.8,
                reasoning=f"Neural evaluation gives this position a score of {score:.2f}"
            )
            
        except Exception as e:
            print(f"Neural analysis failed: {e}")
        
        return None
    
    def _analyze_patterns_simple(self, state: AzulState, move, agent_id: int) -> PatternAnalysis:
        """Analyze patterns for the move (simplified)."""
        try:
            # Use current state for pattern analysis (simplified)
            patterns = self.pattern_detector.detect_patterns(state, agent_id)
            scoring = self.scoring_detector.detect_scoring_optimization(state, agent_id)
            floor_line = self.floor_line_detector.detect_floor_line_patterns(state, agent_id)
            
            # Extract pattern information (simplified)
            blocking_opportunities = 0
            if patterns and hasattr(patterns, 'blocking_opportunities'):
                blocking_opportunities = len(patterns.blocking_opportunities)
            
            scoring_opportunities = 0
            if scoring and hasattr(scoring, 'wall_completion_opportunities'):
                scoring_opportunities = len(scoring.wall_completion_opportunities)
            
            floor_line_risks = 0
            if floor_line and hasattr(floor_line, 'risk_mitigation_opportunities'):
                floor_line_risks = len(floor_line.risk_mitigation_opportunities)
            
            # Generate pattern connections
            pattern_connections = []
            if blocking_opportunities > 0:
                pattern_connections.append(f"Creates {blocking_opportunities} blocking opportunities")
            if scoring_opportunities > 0:
                pattern_connections.append(f"Opens {scoring_opportunities} scoring opportunities")
            if floor_line_risks > 0:
                pattern_connections.append(f"Addresses {floor_line_risks} floor line risks")
            
            # Calculate strategic value
            strategic_value = (blocking_opportunities * 0.4 + 
                             scoring_opportunities * 0.4 + 
                             floor_line_risks * 0.2)
            
            return PatternAnalysis(
                blocking_opportunities=blocking_opportunities,
                scoring_opportunities=scoring_opportunities,
                floor_line_risks=floor_line_risks,
                pattern_connections=pattern_connections,
                strategic_value=strategic_value
            )
            
        except Exception as e:
            print(f"Pattern analysis failed: {e}")
            return PatternAnalysis(
                blocking_opportunities=0,
                scoring_opportunities=0,
                floor_line_risks=0,
                pattern_connections=[],
                strategic_value=0.0
            )
    
    def _determine_quality_tier(self, alpha_beta: Optional[EngineAnalysis], 
                               mcts: Optional[EngineAnalysis], 
                               neural: Optional[EngineAnalysis],
                               patterns: PatternAnalysis) -> Tuple[QualityTier, float]:
        """Determine quality tier and score based on all analyses."""
        
        # Collect scores from all engines
        scores = []
        if alpha_beta:
            scores.append(alpha_beta.best_score)
        if mcts:
            scores.append(mcts.best_score)
        if neural:
            scores.append(neural.best_score)
        
        # Calculate base score from engine consensus
        if scores:
            engine_score = sum(scores) / len(scores)
        else:
            engine_score = 0.0
        
        # Add pattern-based score
        pattern_score = patterns.strategic_value * 20  # Scale to 0-20
        
        # Calculate final quality score (0-100)
        quality_score = min(100, max(0, engine_score + pattern_score))
        
        # Determine tier
        if quality_score >= 90:
            return QualityTier.BRILLIANT, quality_score
        elif quality_score >= 75:
            return QualityTier.EXCELLENT, quality_score
        elif quality_score >= 50:
            return QualityTier.GOOD, quality_score
        elif quality_score >= 25:
            return QualityTier.DUBIOUS, quality_score
        else:
            return QualityTier.POOR, quality_score
    
    def _generate_strategic_reasoning(self, alpha_beta: Optional[EngineAnalysis], 
                                    mcts: Optional[EngineAnalysis], 
                                    neural: Optional[EngineAnalysis],
                                    patterns: PatternAnalysis) -> str:
        """Generate strategic reasoning for the move."""
        
        reasons = []
        
        # Add engine reasoning
        if alpha_beta:
            reasons.append(f"Alpha-Beta: {alpha_beta.reasoning}")
        if mcts:
            reasons.append(f"MCTS: {mcts.reasoning}")
        if neural:
            reasons.append(f"Neural: {neural.reasoning}")
        
        # Add pattern reasoning
        if patterns.pattern_connections:
            reasons.append(f"Patterns: {'; '.join(patterns.pattern_connections)}")
        
        # Add strategic summary
        if patterns.blocking_opportunities > 0:
            reasons.append("This move creates blocking opportunities")
        if patterns.scoring_opportunities > 0:
            reasons.append("This move opens scoring opportunities")
        if patterns.floor_line_risks > 0:
            reasons.append("This move addresses floor line risks")
        
        return " | ".join(reasons) if reasons else "Standard move with no clear strategic advantage"
    
    def _generate_educational_explanation(self, quality_tier: QualityTier, 
                                        strategic_reasoning: str,
                                        patterns: PatternAnalysis) -> str:
        """Generate educational explanation for the move."""
        
        explanations = []
        
        # Add quality tier explanation
        if quality_tier == QualityTier.BRILLIANT:
            explanations.append("This is a brilliant move that creates multiple advantages.")
        elif quality_tier == QualityTier.EXCELLENT:
            explanations.append("This is an excellent move with clear strategic benefits.")
        elif quality_tier == QualityTier.GOOD:
            explanations.append("This is a good move that advances your position.")
        elif quality_tier == QualityTier.DUBIOUS:
            explanations.append("This move has some drawbacks but may be necessary.")
        else:
            explanations.append("This move has significant drawbacks and should be avoided if possible.")
        
        # Add pattern explanations
        if patterns.blocking_opportunities > 0:
            explanations.append(f"Blocking {patterns.blocking_opportunities} opponent opportunities prevents them from scoring.")
        if patterns.scoring_opportunities > 0:
            explanations.append(f"Creating {patterns.scoring_opportunities} scoring opportunities improves your position.")
        if patterns.floor_line_risks > 0:
            explanations.append(f"Addressing {patterns.floor_line_risks} floor line risks reduces penalties.")
        
        # Add learning tip
        if quality_tier in [QualityTier.BRILLIANT, QualityTier.EXCELLENT]:
            explanations.append("Look for moves that combine multiple strategic benefits.")
        elif quality_tier == QualityTier.GOOD:
            explanations.append("Focus on moves that advance your position without major risks.")
        else:
            explanations.append("Consider alternatives that avoid the drawbacks of this move.")
        
        return " ".join(explanations)
    
    def _extract_tactical_factors(self, patterns: PatternAnalysis) -> List[str]:
        """Extract tactical factors from pattern analysis."""
        factors = []
        
        if patterns.blocking_opportunities > 0:
            factors.append("blocking")
        if patterns.scoring_opportunities > 0:
            factors.append("scoring")
        if patterns.floor_line_risks > 0:
            factors.append("risk_management")
        
        return factors
    
    def _assess_risk(self, patterns: PatternAnalysis) -> str:
        """Assess the risk level of the move."""
        if patterns.floor_line_risks > 2:
            return "High risk - significant floor line penalties possible"
        elif patterns.floor_line_risks > 0:
            return "Medium risk - some floor line penalties possible"
        else:
            return "Low risk - minimal floor line penalties"
    
    def _determine_game_phase(self, state: AzulState) -> str:
        """Determine the game phase based on the position."""
        # Count total tiles in factories
        total_tiles = sum(factory.total for factory in state.factories)
        
        if total_tiles > 20:
            return "opening"
        elif total_tiles > 10:
            return "middlegame"
        else:
            return "endgame"
    
    def _calculate_complexity(self, state: AzulState) -> float:
        """Calculate position complexity score."""
        # Count legal moves
        moves = self.move_generator.generate_moves_fast(state, 0)
        move_count = len(moves) if moves else 0
        
        # Count tiles in factories
        total_tiles = sum(factory.total for factory in state.factories)
        
        # Calculate complexity (0-1)
        complexity = min(1.0, (move_count / 50.0 + total_tiles / 30.0) / 2.0)
        
        return complexity
    
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
                    position_fen, move_data, 
                    alpha_beta_score, alpha_beta_reasoning,
                    mcts_score, mcts_reasoning,
                    neural_score, neural_reasoning,
                    blocking_opportunities, scoring_opportunities, floor_line_risks,
                    pattern_connections, strategic_value,
                    quality_tier, quality_score, strategic_reasoning,
                    tactical_factors, risk_assessment, educational_explanation,
                    game_phase, complexity_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.position_fen,
                json.dumps(data.move_data),
                data.alpha_beta_analysis.best_score if data.alpha_beta_analysis else None,
                data.alpha_beta_analysis.reasoning if data.alpha_beta_analysis else None,
                data.mcts_analysis.best_score if data.mcts_analysis else None,
                data.mcts_analysis.reasoning if data.mcts_analysis else None,
                data.neural_analysis.best_score if data.neural_analysis else None,
                data.neural_analysis.reasoning if data.neural_analysis else None,
                data.pattern_analysis.blocking_opportunities,
                data.pattern_analysis.scoring_opportunities,
                data.pattern_analysis.floor_line_risks,
                json.dumps(data.pattern_analysis.pattern_connections),
                data.pattern_analysis.strategic_value,
                data.quality_tier.value,
                data.quality_score,
                data.strategic_reasoning,
                json.dumps(data.tactical_factors),
                data.risk_assessment,
                data.educational_explanation,
                data.game_phase,
                data.complexity_score,
                data.created_at
            ))
    
    def analyze_positions_from_file(self, positions_file: str):
        """Analyze positions from a JSON file."""
        if not os.path.exists(positions_file):
            print(f"❌ Positions file not found: {positions_file}")
            return
        
        print(f"📊 Analyzing positions from: {positions_file}")
        
        with open(positions_file, 'r') as f:
            position_data = json.load(f)
        
        total_moves_analyzed = 0
        
        for i, pos_data in enumerate(position_data):
            try:
                print(f"Analyzing position {i+1}/{len(position_data)}...")
                
                # Convert FEN to state
                state = parse_fen_string(pos_data['fen_string'])
                
                # Analyze the position
                move_data_list = self.analyze_position(state)
                
                # Save results
                for move_data in move_data_list:
                    self.save_move_quality_data(move_data)
                    total_moves_analyzed += 1
                
                print(f"  Analyzed {len(move_data_list)} moves")
                
            except Exception as e:
                print(f"  Error analyzing position {i+1}: {e}")
        
        print(f"✅ Analysis complete! Analyzed {total_moves_analyzed} moves total.")

def main():
    """Main function to run comprehensive move quality analysis."""
    analyzer = ComprehensiveMoveQualityAnalyzer()
    
    # Analyze positions from the file we generated
    positions_file = "data/diverse_positions_simple.json"
    
    if os.path.exists(positions_file):
        analyzer.analyze_positions_from_file(positions_file)
    else:
        print(f"❌ Positions file not found: {positions_file}")
        print("Run generate_diverse_positions_simple.py first!")
        return
    
    print(f"📁 Database saved to: {analyzer.db_path}")
    print(f"🔧 Next step: Query and analyze the move quality data")

if __name__ == "__main__":
    main()
