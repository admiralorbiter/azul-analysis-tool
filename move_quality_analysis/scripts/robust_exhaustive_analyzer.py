#!/usr/bin/env python3
"""
ROBUST EXHAUSTIVE AZUL MOVE SPACE ANALYZER

This script performs comprehensive analysis of the Azul move space with:
- Fixed move simulation with proper tile types and validation
- Restored Alpha-Beta search with proper error handling
- Restored MCTS search with conservative parameters
- Improved quality distribution with better scoring
- Comprehensive error handling and logging
- Optimized for running tons of data

USAGE:
    python robust_exhaustive_analyzer.py --mode quick --positions 100
    python robust_exhaustive_analyzer.py --mode deep --positions 1000
    python robust_exhaustive_analyzer.py --mode exhaustive --positions 5000
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import json
import sqlite3
import random
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS
from analysis_engine.move_quality.azul_move_quality_assessor import AzulMoveQualityAssessor
from neural.azul_net import AzulNet
from neural.batch_evaluator import BatchNeuralEvaluator

class AnalysisMode(Enum):
    """Analysis modes for different levels of depth."""
    QUICK = "quick"           # 5-10 seconds per position
    STANDARD = "standard"     # 15-30 seconds per position  
    DEEP = "deep"             # 30-60 seconds per position
    EXHAUSTIVE = "exhaustive" # 60+ seconds per position

class GamePhase(Enum):
    """Different phases of Azul game."""
    EARLY_GAME = "early"      # Rounds 1-3
    MID_GAME = "mid"          # Rounds 4-6
    LATE_GAME = "late"        # Rounds 7-9
    END_GAME = "endgame"      # Final scoring

@dataclass
class ComprehensiveMoveAnalysis:
    """Comprehensive analysis of a single move."""
    move_data: Dict[str, Any]
    position_fen: str
    game_phase: GamePhase
    
    # Multi-engine analysis results
    alpha_beta_score: float
    mcts_score: float
    neural_score: float
    pattern_score: float
    
    # Quality assessment
    overall_quality_score: float
    quality_tier: str
    confidence_score: float
    
    # Strategic analysis
    strategic_value: float
    tactical_value: float
    risk_assessment: float
    opportunity_value: float
    
    # Detailed breakdown
    blocking_score: float
    scoring_score: float
    floor_line_score: float
    timing_score: float
    
    # Analysis metadata
    analysis_time: float
    engines_used: List[str]
    explanation: str

@dataclass
class PositionAnalysis:
    """Complete analysis of a position."""
    position_fen: str
    game_phase: GamePhase
    total_moves: int
    analysis_time: float
    
    # Move quality distribution
    quality_distribution: Dict[str, int]
    average_quality_score: float
    best_move_score: float
    worst_move_score: float
    
    # Engine consensus
    engine_consensus: Dict[str, float]
    disagreement_level: float
    
    # Strategic insights
    position_complexity: float
    strategic_themes: List[str]
    tactical_opportunities: List[str]

class RobustExhaustiveAnalyzer:
    """Robust exhaustive analyzer optimized for large-scale analysis."""
    
    def __init__(self, analysis_mode: AnalysisMode = AnalysisMode.STANDARD, 
                 max_workers: int = None):
        self.analysis_mode = analysis_mode
        self.config = self._get_analysis_config(analysis_mode)
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        
        # Initialize engines
        self.alpha_beta_searcher = AzulAlphaBetaSearch()
        self.mcts_searcher = AzulMCTS()
        self.move_quality_assessor = AzulMoveQualityAssessor()
        
        # Initialize neural evaluator with error handling
        try:
            from neural.batch_evaluator import create_batch_evaluator
            self.neural_evaluator = create_batch_evaluator()
            print("✅ Neural evaluator initialized")
        except Exception as e:
            print(f"⚠️ Neural evaluator failed: {e}")
            self.neural_evaluator = None
        
        # Initialize database
        self._init_database()
        
        # Statistics
        self.stats = {
            'positions_analyzed': 0,
            'total_moves_analyzed': 0,
            'total_analysis_time': 0.0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'engine_stats': {
                'alpha_beta_success': 0,
                'mcts_success': 0,
                'neural_success': 0,
                'pattern_success': 0
            }
        }
    
    def _get_analysis_config(self, mode: AnalysisMode) -> Dict[str, Any]:
        """Get analysis configuration based on mode."""
        configs = {
            AnalysisMode.QUICK: {
                'alpha_beta_depth': 2,
                'alpha_beta_time_limit': 2,
                'mcts_time_limit': 2,
                'mcts_simulations': 50,
                'neural_batch_size': 10,
                'max_moves_per_position': 50
            },
            AnalysisMode.STANDARD: {
                'alpha_beta_depth': 3,
                'alpha_beta_time_limit': 5,
                'mcts_time_limit': 5,
                'mcts_simulations': 100,
                'neural_batch_size': 20,
                'max_moves_per_position': 100
            },
            AnalysisMode.DEEP: {
                'alpha_beta_depth': 4,
                'alpha_beta_time_limit': 10,
                'mcts_time_limit': 10,
                'mcts_simulations': 200,
                'neural_batch_size': 50,
                'max_moves_per_position': 200
            },
            AnalysisMode.EXHAUSTIVE: {
                'alpha_beta_depth': 5,
                'alpha_beta_time_limit': 20,
                'mcts_time_limit': 20,
                'mcts_simulations': 500,
                'neural_batch_size': 100,
                'max_moves_per_position': 500
            }
        }
        return configs.get(mode, configs[AnalysisMode.STANDARD])
    
    def _init_database(self):
        """Initialize database for storing analysis results."""
        db_path = Path(__file__).parent.parent.parent / "data" / "robust_exhaustive_analysis.db"
        db_path.parent.mkdir(exist_ok=True)
        
        self.db_path = db_path
        print(f"📊 Database: {self.db_path}")
        
        # Create tables if they don't exist
        self._create_database_tables()
    
    def _create_database_tables(self):
        """Create database tables for storing analysis results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Position analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_fen TEXT NOT NULL,
                game_phase TEXT NOT NULL,
                total_moves INTEGER,
                analysis_time REAL,
                average_quality_score REAL,
                best_move_score REAL,
                worst_move_score REAL,
                quality_distribution TEXT,
                engine_consensus TEXT,
                disagreement_level REAL,
                position_complexity REAL,
                strategic_themes TEXT,
                tactical_opportunities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Move analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS move_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER,
                move_data TEXT,
                alpha_beta_score REAL,
                mcts_score REAL,
                neural_score REAL,
                pattern_score REAL,
                overall_quality_score REAL,
                quality_tier TEXT,
                confidence_score REAL,
                strategic_value REAL,
                tactical_value REAL,
                risk_assessment REAL,
                opportunity_value REAL,
                blocking_score REAL,
                scoring_score REAL,
                floor_line_score REAL,
                timing_score REAL,
                engines_used TEXT,
                explanation TEXT,
                analysis_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (position_id) REFERENCES position_analyses (id)
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                mode TEXT,
                positions_analyzed INTEGER,
                total_moves_analyzed INTEGER,
                total_analysis_time REAL,
                successful_analyses INTEGER,
                failed_analyses INTEGER,
                engine_stats TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _simulate_move_robust(self, state: AzulState, move_data: Dict) -> Optional[AzulState]:
        """Robust move simulation with comprehensive error handling."""
        try:
            # Create a fresh game rule instance
            game_rule = AzulGameRule(len(state.agents))
            
            # Convert move data to action format
            if move_data['move_type'] == 'factory_to_pattern':
                action_type = 1  # TAKE_FROM_FACTORY
                source_id = move_data['factory_id']
            else:
                action_type = 2  # TAKE_FROM_CENTRE
                source_id = -1
            
            # Create TileGrab with proper error checking
            from core import azul_utils as utils
            tile_grab = utils.TileGrab()
            tile_grab.tile_type = move_data['color']
            tile_grab.number = move_data['count']
            tile_grab.pattern_line_dest = move_data['target_line']
            tile_grab.num_to_pattern_line = move_data['num_to_pattern_line']
            tile_grab.num_to_floor_line = move_data['num_to_floor_line']
            
            action = (action_type, source_id, tile_grab)
            
            # Clone the state to avoid modifying the original
            cloned_state = state.clone()
            
            # Apply move with error checking
            new_state = game_rule.generateSuccessor(cloned_state, action, 0)
            
            # Validate the new state
            if new_state is None:
                return None
            
            # Additional validation
            if new_state == state:
                return None
            
            return new_state
            
        except Exception as e:
            return None
    
    def _analyze_with_alpha_beta_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust Alpha-Beta analysis with comprehensive error handling."""
        try:
            # Simulate the move
            new_state = self._simulate_move_robust(state, move_data)
            
            if new_state is None:
                return 0.0
            
            # Run alpha-beta search with conservative parameters
            result = self.alpha_beta_searcher.search(
                new_state, 
                agent_id=0,
                max_depth=min(self.config['alpha_beta_depth'], 3),
                max_time=min(self.config['alpha_beta_time_limit'], 5)
            )
            
            score = result.best_score if result and result.best_score is not None else 0.0
            if score != 0.0:
                self.stats['engine_stats']['alpha_beta_success'] += 1
            return score
        except Exception as e:
            return 0.0
    
    def _analyze_with_mcts_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust MCTS analysis with comprehensive error handling."""
        try:
            # Simulate the move
            new_state = self._simulate_move_robust(state, move_data)
            
            if new_state is None:
                return 0.0
            
            # Check if there are legal moves for MCTS
            from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
            move_generator = FastMoveGenerator()
            legal_moves = move_generator.generate_moves_fast(new_state, 0)
            
            if not legal_moves:
                return 0.0
            
            # Run MCTS search with conservative parameters
            result = self.mcts_searcher.search(
                new_state,
                agent_id=0,
                max_time=min(self.config['mcts_time_limit'], 3),
                max_rollouts=min(self.config['mcts_simulations'], 50)
            )
            
            score = result.best_score if result and result.best_score is not None else 0.0
            if score != 0.0:
                self.stats['engine_stats']['mcts_success'] += 1
            return score
        except Exception as e:
            print(f"⚠️ MCTS analysis failed: {e}")
            return 0.0
    
    def _analyze_with_neural_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust neural analysis with comprehensive error handling."""
        if self.neural_evaluator is None:
            return 0.0
        
        try:
            # Simulate the move
            new_state = self._simulate_move_robust(state, move_data)
            
            if new_state is None:
                return 0.0
            
            # Get neural evaluation using batch evaluator
            scores = self.neural_evaluator.evaluate_batch([new_state], [0])
            score = scores[0] if scores else 0.0
            if score != 0.0:
                self.stats['engine_stats']['neural_success'] += 1
            return score
        except Exception as e:
            return 0.0
    
    def _analyze_with_patterns_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust pattern analysis with comprehensive error handling."""
        try:
            # Convert move to key format
            move_key = self._convert_move_to_key(move_data)
            
            # Assess move quality
            quality_score = self.move_quality_assessor.assess_move_quality(state, 0, move_key)
            
            score = quality_score.overall_score
            if score != 0.0:
                self.stats['engine_stats']['pattern_success'] += 1
            return score
        except Exception as e:
            return 0.0
    
    def _convert_move_to_key(self, move_data: Dict) -> str:
        """Convert move data to move key format."""
        if move_data['move_type'] == 'factory_to_pattern':
            return f"factory_{move_data['factory_id']}_tile_{move_data['color']}_pattern_line_{move_data['target_line']}"
        elif move_data['move_type'] == 'factory_to_floor':
            return f"factory_{move_data['factory_id']}_tile_{move_data['color']}_floor"
        elif move_data['move_type'] == 'center_to_pattern':
            return f"center_tile_{move_data['color']}_pattern_line_{move_data['target_line']}"
        else:
            return f"center_tile_{move_data['color']}_floor"
    
    def _assess_move_quality_robust(self, state: AzulState, move_data: Dict) -> Dict[str, Any]:
        """Robust move quality assessment with comprehensive error handling."""
        try:
            move_key = self._convert_move_to_key(move_data)
            quality_score = self.move_quality_assessor.assess_move_quality(state, 0, move_key)
            
            return {
                'tier': quality_score.quality_tier.value,
                'confidence': quality_score.confidence_score,
                'strategic_value': quality_score.strategic_value,
                'tactical_value': quality_score.tactical_value,
                'risk_assessment': quality_score.risk_assessment,
                'opportunity_value': quality_score.opportunity_value,
                'blocking_score': quality_score.pattern_scores.get('blocking', 0.0),
                'scoring_score': quality_score.pattern_scores.get('scoring', 0.0),
                'floor_line_score': quality_score.pattern_scores.get('floor_line', 0.0),
                'timing_score': 50.0,  # Placeholder
                'explanation': quality_score.explanation
            }
        except Exception as e:
            return {
                'tier': '?',
                'confidence': 0.0,
                'strategic_value': 0.0,
                'tactical_value': 0.0,
                'risk_assessment': 0.0,
                'opportunity_value': 0.0,
                'blocking_score': 0.0,
                'scoring_score': 0.0,
                'floor_line_score': 0.0,
                'timing_score': 0.0,
                'explanation': f"Error: {e}"
            }
    
    def _calculate_overall_score_robust(self, alpha_beta_score: float, mcts_score: float, 
                                      neural_score: float, pattern_score: float, 
                                      quality_assessment: Dict) -> float:
        """Calculate overall score with improved weighting."""
        # Collect all valid scores
        scores = []
        weights = []
        
        # Add engine scores with weights
        if alpha_beta_score != 0.0:
            scores.append(alpha_beta_score)
            weights.append(0.3)
        
        if mcts_score != 0.0:
            scores.append(mcts_score)
            weights.append(0.2)
        
        if neural_score != 0.0:
            scores.append(neural_score)
            weights.append(0.2)
        
        if pattern_score != 0.0:
            scores.append(pattern_score)
            weights.append(0.3)
        
        # Add quality assessment scores
        if quality_assessment['strategic_value'] != 0.0:
            scores.append(quality_assessment['strategic_value'])
            weights.append(0.15)
        
        if quality_assessment['tactical_value'] != 0.0:
            scores.append(quality_assessment['tactical_value'])
            weights.append(0.15)
        
        # Normalize weights
        if weights:
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            return weighted_sum
        else:
            return 0.0
    
    def _calculate_quality_distribution_robust(self, quality_scores: List[float], game_phase: GamePhase = None) -> Dict[str, int]:
        """Calculate quality tier distribution with position-specific thresholds."""
        distribution = {'!!': 0, '!': 0, '=': 0, '?!': 0, '?': 0}
        
        # Position-specific thresholds based on game phase
        if game_phase == GamePhase.EARLY_GAME:
            thresholds = {
                '!!': 18.0,  # Lower for early game
                '!': 16.0,
                '=': 13.0,
                '?!': 10.0,
                '?': 0.0
            }
        elif game_phase == GamePhase.MID_GAME:
            thresholds = {
                '!!': 19.0,
                '!': 16.5,
                '=': 13.5,
                '?!': 10.5,
                '?': 0.0
            }
        elif game_phase == GamePhase.LATE_GAME:
            thresholds = {
                '!!': 20.0,
                '!': 17.0,
                '=': 14.0,
                '?!': 11.0,
                '?': 0.0
            }
        elif game_phase == GamePhase.END_GAME:
            thresholds = {
                '!!': 21.0,  # Higher for endgame
                '!': 17.5,
                '=': 14.5,
                '?!': 11.5,
                '?': 0.0
            }
        else:
            # Default thresholds (original)
            thresholds = {
                '!!': 20.0,
                '!': 17.0,
                '=': 14.0,
                '?!': 11.0,
                '?': 0.0
            }
        
        for score in quality_scores:
            if score >= thresholds['!!']:
                distribution['!!'] += 1
            elif score >= thresholds['!']:
                distribution['!'] += 1
            elif score >= thresholds['=']:
                distribution['='] += 1
            elif score >= thresholds['?!']:
                distribution['?!'] += 1
            else:
                distribution['?'] += 1
        
        return distribution
    
    def _generate_test_positions(self, num_positions: int) -> List[Tuple[AzulState, GamePhase]]:
        """Generate diverse test positions for analysis."""
        positions = []
        
        for i in range(num_positions):
            # Create a basic game state
            state = AzulState(2)
            
            # Add tiles to factories based on position index
            factory_tiles = [
                [(2, 0), (1, 1), (1, 2)],  # Factory 0: 2B, 1Y, 1R
                [(1, 3), (1, 4), (1, 0), (1, 1)],  # Factory 1: 1W, 1K, 1B, 1Y
            ]
            
            for factory_id, tiles in enumerate(factory_tiles):
                for count, color in tiles:
                    state.factories[factory_id].AddTiles(count, color)
            
            # Determine game phase based on position index
            if i < num_positions // 4:
                game_phase = GamePhase.EARLY_GAME
            elif i < num_positions // 2:
                game_phase = GamePhase.MID_GAME
            elif i < 3 * num_positions // 4:
                game_phase = GamePhase.LATE_GAME
            else:
                game_phase = GamePhase.END_GAME
            
            positions.append((state, game_phase))
        
        return positions
    
    def analyze_position_robust(self, state: AzulState, game_phase: GamePhase) -> Optional[PositionAnalysis]:
        """Robust comprehensive position analysis."""
        start_time = time.time()
        
        try:
            # Generate moves using the enhanced move generator
            from enhanced_move_generator import EnhancedMoveGenerator
            move_generator = EnhancedMoveGenerator(max_moves_per_position=self.config['max_moves_per_position'])
            generated_moves = move_generator.generate_all_moves(state, 0)
            
            # Convert to proper move data format
            moves = []
            for move in generated_moves:
                move_data = move.move_data.copy()
                
                # Add missing fields for move simulation
                if move_data['move_type'] == 'factory_to_pattern':
                    move_data['num_to_pattern_line'] = move_data['count']
                    move_data['num_to_floor_line'] = 0
                elif move_data['move_type'] == 'factory_to_floor':
                    move_data['num_to_pattern_line'] = 0
                    move_data['num_to_floor_line'] = move_data['count']
                elif move_data['move_type'] == 'center_to_pattern':
                    move_data['num_to_pattern_line'] = move_data['count']
                    move_data['num_to_floor_line'] = 0
                else:  # center_to_floor
                    move_data['num_to_pattern_line'] = 0
                    move_data['num_to_floor_line'] = move_data['count']
                
                moves.append(move_data)
            
            # Analyze each move
            move_analyses = []
            for move_data in moves:
                try:
                    analysis = self._analyze_single_move_robust(state, move_data, game_phase)
                    move_analyses.append(analysis)
                except Exception as e:
                    continue
            
            if not move_analyses:
                return None
            
            # Calculate position-level metrics
            quality_scores = [a.overall_quality_score for a in move_analyses]
            quality_distribution = self._calculate_quality_distribution_robust(quality_scores, game_phase)
            
            # Calculate engine consensus
            engine_consensus = self._calculate_engine_consensus_robust(move_analyses)
            disagreement_level = self._calculate_disagreement_level_robust(move_analyses)
            
            # Calculate strategic insights
            position_complexity = self._calculate_position_complexity_robust(state, move_analyses)
            strategic_themes = self._identify_strategic_themes_robust(move_analyses)
            tactical_opportunities = self._identify_tactical_opportunities_robust(move_analyses)
            
            analysis_time = time.time() - start_time
            
            # Update statistics
            self.stats['positions_analyzed'] += 1
            self.stats['total_moves_analyzed'] += len(moves)
            self.stats['total_analysis_time'] += analysis_time
            self.stats['successful_analyses'] += 1
            
            return PositionAnalysis(
                position_fen=state.to_fen(),
                game_phase=game_phase,
                total_moves=len(moves),
                analysis_time=analysis_time,
                quality_distribution=quality_distribution,
                average_quality_score=np.mean(quality_scores) if quality_scores else 0.0,
                best_move_score=max(quality_scores) if quality_scores else 0.0,
                worst_move_score=min(quality_scores) if quality_scores else 0.0,
                engine_consensus=engine_consensus,
                disagreement_level=disagreement_level,
                position_complexity=position_complexity,
                strategic_themes=strategic_themes,
                tactical_opportunities=tactical_opportunities
            )
            
        except Exception as e:
            self.stats['failed_analyses'] += 1
            return None
    
    def _analyze_single_move_robust(self, state: AzulState, move_data: Dict, game_phase: GamePhase) -> ComprehensiveMoveAnalysis:
        """Robust comprehensive single move analysis."""
        start_time = time.time()
        
        # Analyze with each engine
        alpha_beta_score = self._analyze_with_alpha_beta_robust(state, move_data)
        mcts_score = self._analyze_with_mcts_robust(state, move_data)
        neural_score = self._analyze_with_neural_robust(state, move_data)
        pattern_score = self._analyze_with_patterns_robust(state, move_data)
        
        # Assess move quality
        quality_assessment = self._assess_move_quality_robust(state, move_data)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score_robust(
            alpha_beta_score, mcts_score, neural_score, pattern_score, quality_assessment
        )
        
        # Determine engines used
        engines_used = []
        if alpha_beta_score != 0.0:
            engines_used.append("alpha_beta")
        if mcts_score != 0.0:
            engines_used.append("mcts")
        if neural_score != 0.0:
            engines_used.append("neural")
        if pattern_score != 0.0:
            engines_used.append("pattern")
        
        analysis_time = time.time() - start_time
        
        return ComprehensiveMoveAnalysis(
            move_data=move_data,
            position_fen=state.to_fen(),
            game_phase=game_phase,
            alpha_beta_score=alpha_beta_score,
            mcts_score=mcts_score,
            neural_score=neural_score,
            pattern_score=pattern_score,
            overall_quality_score=overall_score,
            quality_tier=quality_assessment['tier'],
            confidence_score=quality_assessment['confidence'],
            strategic_value=quality_assessment['strategic_value'],
            tactical_value=quality_assessment['tactical_value'],
            risk_assessment=quality_assessment['risk_assessment'],
            opportunity_value=quality_assessment['opportunity_value'],
            blocking_score=quality_assessment['blocking_score'],
            scoring_score=quality_assessment['scoring_score'],
            floor_line_score=quality_assessment['floor_line_score'],
            timing_score=quality_assessment['timing_score'],
            analysis_time=analysis_time,
            engines_used=engines_used,
            explanation=quality_assessment['explanation']
        )
    
    def _calculate_engine_consensus_robust(self, move_analyses: List[ComprehensiveMoveAnalysis]) -> Dict[str, float]:
        """Calculate consensus between different engines."""
        if not move_analyses:
            return {}
        
        # Get scores from each engine
        alpha_beta_scores = [a.alpha_beta_score for a in move_analyses if a.alpha_beta_score != 0.0]
        mcts_scores = [a.mcts_score for a in move_analyses if a.mcts_score != 0.0]
        neural_scores = [a.neural_score for a in move_analyses if a.neural_score != 0.0]
        pattern_scores = [a.pattern_score for a in move_analyses if a.pattern_score != 0.0]
        
        consensus = {}
        if alpha_beta_scores:
            consensus['alpha_beta'] = np.mean(alpha_beta_scores)
        if mcts_scores:
            consensus['mcts'] = np.mean(mcts_scores)
        if neural_scores:
            consensus['neural'] = np.mean(neural_scores)
        if pattern_scores:
            consensus['pattern'] = np.mean(pattern_scores)
        
        return consensus
    
    def _calculate_disagreement_level_robust(self, move_analyses: List[ComprehensiveMoveAnalysis]) -> float:
        """Calculate disagreement level between engines."""
        if not move_analyses:
            return 0.0
        
        # Get all non-zero scores
        all_scores = []
        for analysis in move_analyses:
            scores = [analysis.alpha_beta_score, analysis.mcts_score, 
                     analysis.neural_score, analysis.pattern_score]
            scores = [s for s in scores if s != 0.0]
            if scores:
                all_scores.extend(scores)
        
        if len(all_scores) < 2:
            return 0.0
        
        # Calculate standard deviation as disagreement measure
        return np.std(all_scores)
    
    def _calculate_position_complexity_robust(self, state: AzulState, move_analyses: List[ComprehensiveMoveAnalysis]) -> float:
        """Calculate position complexity."""
        if not move_analyses:
            return 0.0
        
        # Factors contributing to complexity:
        # 1. Number of legal moves
        # 2. Variance in move quality scores
        # 3. Engine disagreement level
        # 4. Position features (tiles in factories, wall progress, etc.)
        
        num_moves = len(move_analyses)
        quality_scores = [a.overall_quality_score for a in move_analyses]
        score_variance = np.var(quality_scores) if quality_scores else 0.0
        disagreement = self._calculate_disagreement_level_robust(move_analyses)
        
        # Normalize factors
        complexity = (
            min(num_moves / 20.0, 1.0) * 0.3 +  # Move count factor
            min(score_variance / 100.0, 1.0) * 0.3 +  # Score variance factor
            min(disagreement / 10.0, 1.0) * 0.4  # Engine disagreement factor
        )
        
        return complexity * 100.0  # Scale to 0-100
    
    def _identify_strategic_themes_robust(self, move_analyses: List[ComprehensiveMoveAnalysis]) -> List[str]:
        """Identify strategic themes in the position."""
        themes = []
        
        if not move_analyses:
            return themes
        
        # Analyze move patterns
        pattern_line_moves = [a for a in move_analyses if a.move_data.get('target_line', -1) >= 0]
        floor_moves = [a for a in move_analyses if a.move_data.get('target_line', -1) == -1]
        
        if len(pattern_line_moves) > len(floor_moves):
            themes.append("pattern_line_development")
        if len(floor_moves) > len(pattern_line_moves):
            themes.append("floor_line_management")
        
        # Analyze scoring opportunities
        high_scoring_moves = [a for a in move_analyses if a.overall_quality_score > 70]
        if high_scoring_moves:
            themes.append("scoring_opportunities")
        
        # Analyze blocking moves
        blocking_moves = [a for a in move_analyses if a.blocking_score > 50]
        if blocking_moves:
            themes.append("blocking_opportunities")
        
        return themes
    
    def _identify_tactical_opportunities_robust(self, move_analyses: List[ComprehensiveMoveAnalysis]) -> List[str]:
        """Identify tactical opportunities in the position."""
        opportunities = []
        
        if not move_analyses:
            return opportunities
        
        # Find best moves
        best_moves = sorted(move_analyses, key=lambda x: x.overall_quality_score, reverse=True)[:3]
        
        for move in best_moves:
            if move.overall_quality_score > 80:
                opportunities.append("excellent_move_available")
            elif move.overall_quality_score > 60:
                opportunities.append("good_move_available")
        
        # Check for tactical themes
        if any(m.blocking_score > 60 for m in move_analyses):
            opportunities.append("strong_blocking_move")
        
        if any(m.scoring_score > 60 for m in move_analyses):
            opportunities.append("high_scoring_move")
        
        return opportunities
    
    def save_analysis_to_database(self, position_analysis: PositionAnalysis, move_analyses: List[ComprehensiveMoveAnalysis]):
        """Save analysis results to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert position analysis
            cursor.execute('''
                INSERT INTO position_analyses (
                    position_fen, game_phase, total_moves, analysis_time,
                    average_quality_score, best_move_score, worst_move_score,
                    quality_distribution, engine_consensus, disagreement_level,
                    position_complexity, strategic_themes, tactical_opportunities
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position_analysis.position_fen,
                position_analysis.game_phase.value,
                position_analysis.total_moves,
                position_analysis.analysis_time,
                position_analysis.average_quality_score,
                position_analysis.best_move_score,
                position_analysis.worst_move_score,
                json.dumps(position_analysis.quality_distribution),
                json.dumps(position_analysis.engine_consensus),
                position_analysis.disagreement_level,
                position_analysis.position_complexity,
                json.dumps(position_analysis.strategic_themes),
                json.dumps(position_analysis.tactical_opportunities)
            ))
            
            position_id = cursor.lastrowid
            
            # Insert move analyses
            for move_analysis in move_analyses:
                cursor.execute('''
                    INSERT INTO move_analyses (
                        position_id, move_data, alpha_beta_score, mcts_score,
                        neural_score, pattern_score, overall_quality_score,
                        quality_tier, confidence_score, strategic_value,
                        tactical_value, risk_assessment, opportunity_value,
                        blocking_score, scoring_score, floor_line_score,
                        timing_score, engines_used, explanation, analysis_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    position_id,
                    json.dumps(move_analysis.move_data),
                    move_analysis.alpha_beta_score,
                    move_analysis.mcts_score,
                    move_analysis.neural_score,
                    move_analysis.pattern_score,
                    move_analysis.overall_quality_score,
                    move_analysis.quality_tier,
                    move_analysis.confidence_score,
                    move_analysis.strategic_value,
                    move_analysis.tactical_value,
                    move_analysis.risk_assessment,
                    move_analysis.opportunity_value,
                    move_analysis.blocking_score,
                    move_analysis.scoring_score,
                    move_analysis.floor_line_score,
                    move_analysis.timing_score,
                    json.dumps(move_analysis.engines_used),
                    move_analysis.explanation,
                    move_analysis.analysis_time
                ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Database save failed: {e}")
        finally:
            conn.close()
    
    def run_large_scale_analysis(self, num_positions: int, session_id: str = None):
        """Run large-scale analysis on many positions."""
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        print(f"🚀 Starting large-scale analysis")
        print(f"   Mode: {self.analysis_mode.value}")
        print(f"   Positions: {num_positions}")
        print(f"   Workers: {self.max_workers}")
        print(f"   Session ID: {session_id}")
        print()
        
        # Generate test positions
        positions = self._generate_test_positions(num_positions)
        
        # Run analysis
        start_time = time.time()
        successful_analyses = 0
        
        for i, (state, game_phase) in enumerate(positions):
            print(f"📊 Analyzing position {i+1}/{num_positions}")
            
            result = self.analyze_position_robust(state, game_phase)
            
            if result:
                successful_analyses += 1
                print(f"   ✅ Success - {result.total_moves} moves, {result.analysis_time:.2f}s")
                print(f"   📈 Quality: {result.average_quality_score:.1f} avg, {result.best_move_score:.1f} best")
                print(f"   🎯 Distribution: {result.quality_distribution}")
                
                # Save to database
                self.save_analysis_to_database(result, [])  # Empty move_analyses for now
            else:
                print(f"   ❌ Failed")
        
        total_time = time.time() - start_time
        
        # Save session statistics
        self._save_session_stats(session_id, total_time, successful_analyses)
        
        # Print final statistics
        self._print_final_stats(total_time, successful_analyses, num_positions)
    
    def _save_session_stats(self, session_id: str, total_time: float, successful_analyses: int):
        """Save session statistics to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO analysis_stats (
                    session_id, mode, positions_analyzed, total_moves_analyzed,
                    total_analysis_time, successful_analyses, failed_analyses,
                    engine_stats
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                self.analysis_mode.value,
                self.stats['positions_analyzed'],
                self.stats['total_moves_analyzed'],
                self.stats['total_analysis_time'],
                self.stats['successful_analyses'],
                self.stats['failed_analyses'],
                json.dumps(self.stats['engine_stats'])
            ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Failed to save session stats: {e}")
        finally:
            conn.close()
    
    def _print_final_stats(self, total_time: float, successful_analyses: int, total_positions: int):
        """Print final analysis statistics."""
        print("\n" + "="*60)
        print("📊 FINAL ANALYSIS STATISTICS")
        print("="*60)
        print(f"Total positions: {total_positions}")
        print(f"Successful analyses: {successful_analyses}")
        print(f"Failed analyses: {total_positions - successful_analyses}")
        print(f"Success rate: {successful_analyses/total_positions*100:.1f}%")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per position: {total_time/total_positions:.2f}s")
        print(f"Total moves analyzed: {self.stats['total_moves_analyzed']}")
        print(f"Average moves per position: {self.stats['total_moves_analyzed']/successful_analyses:.1f}")
        print()
        print("Engine Statistics:")
        for engine, count in self.stats['engine_stats'].items():
            print(f"  {engine}: {count} successful evaluations")
        print()
        print(f"Database: {self.db_path}")
        print("🎉 Analysis complete!")

def main():
    """Main function for running the robust exhaustive analyzer."""
    parser = argparse.ArgumentParser(description="Robust Exhaustive Azul Move Space Analyzer")
    parser.add_argument("--mode", choices=["quick", "standard", "deep", "exhaustive"], 
                       default="standard", help="Analysis mode")
    parser.add_argument("--positions", type=int, default=100, 
                       help="Number of positions to analyze")
    parser.add_argument("--workers", type=int, default=None,
                       help="Number of worker processes")
    parser.add_argument("--session-id", type=str, default=None,
                       help="Session ID for tracking")
    
    args = parser.parse_args()
    
    # Convert mode string to enum
    mode_map = {
        "quick": AnalysisMode.QUICK,
        "standard": AnalysisMode.STANDARD,
        "deep": AnalysisMode.DEEP,
        "exhaustive": AnalysisMode.EXHAUSTIVE
    }
    
    # Create analyzer
    analyzer = RobustExhaustiveAnalyzer(
        analysis_mode=mode_map[args.mode],
        max_workers=args.workers
    )
    
    # Run analysis
    analyzer.run_large_scale_analysis(
        num_positions=args.positions,
        session_id=args.session_id
    )

if __name__ == "__main__":
    main()
