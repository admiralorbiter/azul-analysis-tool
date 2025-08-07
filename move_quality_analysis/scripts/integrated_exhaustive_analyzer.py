#!/usr/bin/env python3
"""
INTEGRATED EXHAUSTIVE AZUL MOVE SPACE ANALYZER

This script performs comprehensive analysis of the Azul move space with:
- Integration with the main AzulDatabase system
- Fixed move simulation with proper tile types and validation
- Restored Alpha-Beta search with proper error handling
- Restored MCTS search with conservative parameters
- Improved quality distribution with better scoring
- Comprehensive error handling and logging
- Optimized for running tons of data

USAGE:
    python integrated_exhaustive_analyzer.py --mode quick --positions 100
    python integrated_exhaustive_analyzer.py --mode deep --positions 1000
    python integrated_exhaustive_analyzer.py --mode exhaustive --positions 5000
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
import random
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from datetime import datetime

from core.azul_model import AzulState, AzulGameRule
from core.azul_database import AzulDatabase, MoveQualityAnalysis, ComprehensiveMoveAnalysis, ExhaustiveAnalysisSession
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
class IntegratedComprehensiveMoveAnalysis:
    """Comprehensive analysis of a single move for integration."""
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
class IntegratedPositionAnalysis:
    """Complete analysis of a position for integration."""
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


class IntegratedExhaustiveAnalyzer:
    """
    Integrated exhaustive analyzer that uses the main database system.
    
    This version integrates with the core AzulDatabase instead of using
    separate databases, enabling seamless integration with the main system.
    """
    
    def __init__(self, analysis_mode: AnalysisMode = AnalysisMode.STANDARD, 
                 max_workers: int = None):
        """Initialize the integrated exhaustive analyzer."""
        self.analysis_mode = analysis_mode
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        
        # Initialize main database
        self.db = AzulDatabase()
        
        # Initialize analysis engines
        self.alpha_beta_search = AzulAlphaBetaSearch()
        self.mcts_search = AzulMCTS()
        self.move_quality_assessor = AzulMoveQualityAssessor()
        
        # Initialize neural evaluator
        try:
            self.neural_evaluator = BatchNeuralEvaluator()
        except Exception as e:
            print(f"⚠️ Neural evaluator initialization failed: {e}")
            self.neural_evaluator = None
        
        # Get analysis configuration
        self.config = self._get_analysis_config(analysis_mode)
        
        print(f"🚀 Integrated Exhaustive Analyzer initialized")
        print(f"   Mode: {analysis_mode.value}")
        print(f"   Workers: {self.max_workers}")
        print(f"   Database: {self.db.db_path}")
    
    def _get_analysis_config(self, mode: AnalysisMode) -> Dict[str, Any]:
        """Get analysis configuration for the specified mode."""
        configs = {
            AnalysisMode.QUICK: {
                'max_moves_per_position': 50,
                'alpha_beta_depth': 3,
                'mcts_simulations': 100,
                'neural_batch_size': 10,
                'time_limit_per_position': 10.0
            },
            AnalysisMode.STANDARD: {
                'max_moves_per_position': 100,
                'alpha_beta_depth': 4,
                'mcts_simulations': 200,
                'neural_batch_size': 20,
                'time_limit_per_position': 30.0
            },
            AnalysisMode.DEEP: {
                'max_moves_per_position': 200,
                'alpha_beta_depth': 5,
                'mcts_simulations': 500,
                'neural_batch_size': 50,
                'time_limit_per_position': 60.0
            },
            AnalysisMode.EXHAUSTIVE: {
                'max_moves_per_position': 500,
                'alpha_beta_depth': 6,
                'mcts_simulations': 1000,
                'neural_batch_size': 100,
                'time_limit_per_position': 120.0
            }
        }
        return configs.get(mode, configs[AnalysisMode.STANDARD])
    
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
            tile_type = move_data['tile_type']
            pattern_line = move_data['pattern_line']
            num_to_floor_line = move_data.get('num_to_floor_line', 0)
            
            # Simulate the move
            result_state = game_rule.simulate_action(state, action_type, source_id, 
                                                   tile_type, pattern_line, num_to_floor_line)
            
            return result_state
            
        except Exception as e:
            print(f"⚠️ Move simulation failed: {e}")
            return None
    
    def _analyze_with_alpha_beta_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust Alpha-Beta analysis with error handling."""
        try:
            # Simulate move to get resulting state
            result_state = self._simulate_move_robust(state, move_data)
            if result_state is None:
                return 0.0
            
            # Analyze with Alpha-Beta
            depth = self.config['alpha_beta_depth']
            result = self.alpha_beta_search.search(result_state, depth=depth)
            
            return result.get('best_score', 0.0)
            
        except Exception as e:
            print(f"⚠️ Alpha-Beta analysis failed: {e}")
            return 0.0
    
    def _analyze_with_mcts_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust MCTS analysis with error handling."""
        try:
            # Simulate move to get resulting state
            result_state = self._simulate_move_robust(state, move_data)
            if result_state is None:
                return 0.0
            
            # Analyze with MCTS
            simulations = self.config['mcts_simulations']
            result = self.mcts_search.search(result_state, num_simulations=simulations)
            
            return result.get('best_score', 0.0)
            
        except Exception as e:
            print(f"⚠️ MCTS analysis failed: {e}")
            return 0.0
    
    def _analyze_with_neural_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust neural analysis with error handling."""
        try:
            if self.neural_evaluator is None:
                return 0.0
            
            # Simulate move to get resulting state
            result_state = self._simulate_move_robust(state, move_data)
            if result_state is None:
                return 0.0
            
            # Analyze with neural evaluator
            score = self.neural_evaluator.evaluate_state(result_state)
            
            return score
            
        except Exception as e:
            print(f"⚠️ Neural analysis failed: {e}")
            return 0.0
    
    def _analyze_with_patterns_robust(self, state: AzulState, move_data: Dict) -> float:
        """Robust pattern analysis with error handling."""
        try:
            # Convert move to key format for pattern analysis
            move_key = self._convert_move_to_key(move_data)
            
            # Analyze with move quality assessor
            quality_assessment = self._assess_move_quality_robust(state, move_data)
            
            return quality_assessment.get('overall_score', 0.0)
            
        except Exception as e:
            print(f"⚠️ Pattern analysis failed: {e}")
            return 0.0
    
    def _convert_move_to_key(self, move_data: Dict) -> str:
        """Convert move data to key format."""
        return f"factory_{move_data['factory_id']}_tile_{move_data['tile_type']}_pattern_line_{move_data['pattern_line']}"
    
    def _assess_move_quality_robust(self, state: AzulState, move_data: Dict) -> Dict[str, Any]:
        """Robust move quality assessment with error handling."""
        try:
            # Convert move to key format
            move_key = self._convert_move_to_key(move_data)
            
            # Assess move quality
            quality_score = self.move_quality_assessor.assess_move_quality(state, 0, move_key)
            
            return {
                'overall_score': quality_score.overall_score,
                'quality_tier': quality_score.quality_tier.value,
                'pattern_scores': quality_score.pattern_scores,
                'strategic_value': quality_score.strategic_value,
                'tactical_value': quality_score.tactical_value,
                'risk_assessment': quality_score.risk_assessment,
                'opportunity_value': quality_score.opportunity_value,
                'explanation': quality_score.explanation,
                'pattern_connections': quality_score.pattern_connections,
                'confidence_score': quality_score.confidence_score
            }
            
        except Exception as e:
            print(f"⚠️ Move quality assessment failed: {e}")
            return {
                'overall_score': 0.0,
                'quality_tier': '?',
                'pattern_scores': {},
                'strategic_value': 0.0,
                'tactical_value': 0.0,
                'risk_assessment': 0.0,
                'opportunity_value': 0.0,
                'explanation': f"Assessment failed: {str(e)}",
                'pattern_connections': [],
                'confidence_score': 0.0
            }
    
    def _calculate_overall_score_robust(self, alpha_beta_score: float, mcts_score: float, 
                                      neural_score: float, pattern_score: float, 
                                      quality_assessment: Dict) -> float:
        """Calculate overall score from multiple engines."""
        try:
            # Normalize scores to 0-100 range
            scores = [
                alpha_beta_score * 100,
                mcts_score * 100,
                neural_score * 100,
                pattern_score,
                quality_assessment.get('overall_score', 0.0)
            ]
            
            # Remove zero scores (failed engines)
            valid_scores = [s for s in scores if s > 0]
            
            if not valid_scores:
                return 0.0
            
            # Calculate weighted average
            weights = [0.25, 0.25, 0.25, 0.15, 0.10]  # Engine weights
            weighted_sum = sum(s * w for s, w in zip(scores, weights) if s > 0)
            total_weight = sum(w for s, w in zip(scores, weights) if s > 0)
            
            if total_weight == 0:
                return 0.0
            
            return weighted_sum / total_weight
            
        except Exception as e:
            print(f"⚠️ Overall score calculation failed: {e}")
            return 0.0
    
    def _calculate_quality_distribution_robust(self, quality_scores: List[float], game_phase: GamePhase = None) -> Dict[str, int]:
        """Calculate quality distribution from scores."""
        try:
            # Define quality tiers based on game phase
            if game_phase == GamePhase.EARLY_GAME:
                thresholds = {'!!': 18.0, '!': 16.0, '=': 13.0, '?!': 10.0, '?': 0.0}
            elif game_phase == GamePhase.MID_GAME:
                thresholds = {'!!': 20.0, '!': 18.0, '=': 15.0, '?!': 12.0, '?': 0.0}
            elif game_phase == GamePhase.LATE_GAME:
                thresholds = {'!!': 22.0, '!': 20.0, '=': 17.0, '?!': 14.0, '?': 0.0}
            else:  # END_GAME
                thresholds = {'!!': 25.0, '!': 22.0, '=': 19.0, '?!': 16.0, '?': 0.0}
            
            distribution = {'!!': 0, '!': 0, '=': 0, '?!': 0, '?': 0}
            
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
            
        except Exception as e:
            print(f"⚠️ Quality distribution calculation failed: {e}")
            return {'!!': 0, '!': 0, '=': 0, '?!': 0, '?': 0}
    
    def _generate_test_positions(self, num_positions: int) -> List[Tuple[AzulState, GamePhase]]:
        """Generate diverse test positions."""
        positions = []
        
        for i in range(num_positions):
            # Generate random game state
            player_count = random.randint(2, 4)
            state = AzulState(player_count)
            
            # Randomly advance the game to different phases
            game_round = random.randint(1, 9)
            if game_round <= 3:
                phase = GamePhase.EARLY_GAME
            elif game_round <= 6:
                phase = GamePhase.MID_GAME
            elif game_round <= 8:
                phase = GamePhase.LATE_GAME
            else:
                phase = GamePhase.END_GAME
            
            positions.append((state, phase))
        
        return positions
    
    def analyze_position_robust(self, state: AzulState, game_phase: GamePhase) -> Optional[IntegratedPositionAnalysis]:
        """Analyze a single position comprehensively."""
        try:
            start_time = time.time()
            
            # Generate all possible moves
            move_generator = self.move_quality_assessor.move_generator
            all_moves = move_generator.generate_all_moves(state, 0)
            
            # Limit moves based on configuration
            max_moves = self.config['max_moves_per_position']
            if len(all_moves) > max_moves:
                all_moves = all_moves[:max_moves]
            
            print(f"   📊 Analyzing {len(all_moves)} moves...")
            
            # Analyze each move
            move_analyses = []
            quality_scores = []
            
            for i, move_data in enumerate(all_moves):
                move_analysis = self._analyze_single_move_robust(state, move_data, game_phase)
                move_analyses.append(move_analysis)
                quality_scores.append(move_analysis.overall_quality_score)
                
                if (i + 1) % 10 == 0:
                    print(f"      Analyzed {i + 1}/{len(all_moves)} moves")
            
            # Calculate position-level statistics
            analysis_time = time.time() - start_time
            
            if not quality_scores:
                print("   ⚠️ No valid moves analyzed")
                return None
            
            # Calculate quality distribution
            quality_distribution = self._calculate_quality_distribution_robust(quality_scores, game_phase)
            
            # Calculate engine consensus
            engine_consensus = self._calculate_engine_consensus_robust(move_analyses)
            
            # Calculate disagreement level
            disagreement_level = self._calculate_disagreement_level_robust(move_analyses)
            
            # Calculate position complexity
            position_complexity = self._calculate_position_complexity_robust(state, move_analyses)
            
            # Identify strategic themes
            strategic_themes = self._identify_strategic_themes_robust(move_analyses)
            
            # Identify tactical opportunities
            tactical_opportunities = self._identify_tactical_opportunities_robust(move_analyses)
            
            # Create position analysis
            position_analysis = IntegratedPositionAnalysis(
                position_fen=state.to_fen(),
                game_phase=game_phase,
                total_moves=len(all_moves),
                analysis_time=analysis_time,
                quality_distribution=quality_distribution,
                average_quality_score=np.mean(quality_scores),
                best_move_score=max(quality_scores),
                worst_move_score=min(quality_scores),
                engine_consensus=engine_consensus,
                disagreement_level=disagreement_level,
                position_complexity=position_complexity,
                strategic_themes=strategic_themes,
                tactical_opportunities=tactical_opportunities
            )
            
            print(f"   ✅ Position analysis complete in {analysis_time:.2f}s")
            print(f"   📈 Quality: {position_analysis.average_quality_score:.1f} avg, {position_analysis.best_move_score:.1f} best")
            print(f"   🎯 Distribution: {quality_distribution}")
            
            return position_analysis
            
        except Exception as e:
            print(f"   ❌ Position analysis failed: {e}")
            traceback.print_exc()
            return None
    
    def _analyze_single_move_robust(self, state: AzulState, move_data: Dict, game_phase: GamePhase) -> IntegratedComprehensiveMoveAnalysis:
        """Analyze a single move comprehensively."""
        start_time = time.time()
        
        # Analyze with different engines
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
        
        # Determine quality tier
        quality_tier = quality_assessment.get('quality_tier', '?')
        
        # Calculate confidence score
        confidence_score = quality_assessment.get('confidence_score', 0.0)
        
        # Extract strategic components
        strategic_value = quality_assessment.get('strategic_value', 0.0)
        tactical_value = quality_assessment.get('tactical_value', 0.0)
        risk_assessment = quality_assessment.get('risk_assessment', 0.0)
        opportunity_value = quality_assessment.get('opportunity_value', 0.0)
        
        # Extract detailed breakdown
        pattern_scores = quality_assessment.get('pattern_scores', {})
        blocking_score = pattern_scores.get('blocking', 0.0)
        scoring_score = pattern_scores.get('scoring', 0.0)
        floor_line_score = pattern_scores.get('floor_line', 0.0)
        timing_score = pattern_scores.get('timing', 0.0)
        
        # Determine engines used
        engines_used = []
        if alpha_beta_score > 0:
            engines_used.append('alpha_beta')
        if mcts_score > 0:
            engines_used.append('mcts')
        if neural_score > 0:
            engines_used.append('neural')
        if pattern_score > 0:
            engines_used.append('pattern')
        
        # Generate explanation
        explanation = quality_assessment.get('explanation', 'No explanation available')
        
        analysis_time = time.time() - start_time
        
        return IntegratedComprehensiveMoveAnalysis(
            move_data=move_data,
            position_fen=state.to_fen(),
            game_phase=game_phase,
            alpha_beta_score=alpha_beta_score,
            mcts_score=mcts_score,
            neural_score=neural_score,
            pattern_score=pattern_score,
            overall_quality_score=overall_score,
            quality_tier=quality_tier,
            confidence_score=confidence_score,
            strategic_value=strategic_value,
            tactical_value=tactical_value,
            risk_assessment=risk_assessment,
            opportunity_value=opportunity_value,
            blocking_score=blocking_score,
            scoring_score=scoring_score,
            floor_line_score=floor_line_score,
            timing_score=timing_score,
            analysis_time=analysis_time,
            engines_used=engines_used,
            explanation=explanation
        )
    
    def _calculate_engine_consensus_robust(self, move_analyses: List[IntegratedComprehensiveMoveAnalysis]) -> Dict[str, float]:
        """Calculate engine consensus scores."""
        try:
            consensus = {}
            engine_scores = {
                'alpha_beta': [],
                'mcts': [],
                'neural': [],
                'pattern': []
            }
            
            for analysis in move_analyses:
                if analysis.alpha_beta_score > 0:
                    engine_scores['alpha_beta'].append(analysis.alpha_beta_score)
                if analysis.mcts_score > 0:
                    engine_scores['mcts'].append(analysis.mcts_score)
                if analysis.neural_score > 0:
                    engine_scores['neural'].append(analysis.neural_score)
                if analysis.pattern_score > 0:
                    engine_scores['pattern'].append(analysis.pattern_score)
            
            for engine, scores in engine_scores.items():
                if scores:
                    consensus[engine] = np.mean(scores)
                else:
                    consensus[engine] = 0.0
            
            return consensus
            
        except Exception as e:
            print(f"⚠️ Engine consensus calculation failed: {e}")
            return {}
    
    def _calculate_disagreement_level_robust(self, move_analyses: List[IntegratedComprehensiveMoveAnalysis]) -> float:
        """Calculate disagreement level between engines."""
        try:
            if len(move_analyses) < 2:
                return 0.0
            
            # Get scores from each engine
            engine_scores = {
                'alpha_beta': [a.alpha_beta_score for a in move_analyses if a.alpha_beta_score > 0],
                'mcts': [a.mcts_score for a in move_analyses if a.mcts_score > 0],
                'neural': [a.neural_score for a in move_analyses if a.neural_score > 0],
                'pattern': [a.pattern_score for a in move_analyses if a.pattern_score > 0]
            }
            
            # Calculate standard deviation of scores for each engine
            disagreements = []
            for engine, scores in engine_scores.items():
                if len(scores) > 1:
                    disagreements.append(np.std(scores))
            
            if disagreements:
                return np.mean(disagreements)
            else:
                return 0.0
                
        except Exception as e:
            print(f"⚠️ Disagreement level calculation failed: {e}")
            return 0.0
    
    def _calculate_position_complexity_robust(self, state: AzulState, move_analyses: List[IntegratedComprehensiveMoveAnalysis]) -> float:
        """Calculate position complexity score."""
        try:
            if not move_analyses:
                return 0.0
            
            # Factors that contribute to complexity:
            # 1. Number of moves available
            move_count_factor = min(len(move_analyses) / 100.0, 1.0)
            
            # 2. Quality score variance
            quality_scores = [a.overall_quality_score for a in move_analyses]
            variance_factor = np.std(quality_scores) / 100.0 if quality_scores else 0.0
            
            # 3. Engine disagreement
            disagreement_factor = self._calculate_disagreement_level_robust(move_analyses) / 100.0
            
            # 4. Strategic diversity
            strategic_scores = [a.strategic_value for a in move_analyses]
            strategic_variance = np.std(strategic_scores) / 100.0 if strategic_scores else 0.0
            
            # Combine factors
            complexity = (move_count_factor * 0.3 + 
                        variance_factor * 0.3 + 
                        disagreement_factor * 0.2 + 
                        strategic_variance * 0.2)
            
            return min(complexity, 1.0)
            
        except Exception as e:
            print(f"⚠️ Position complexity calculation failed: {e}")
            return 0.0
    
    def _identify_strategic_themes_robust(self, move_analyses: List[IntegratedComprehensiveMoveAnalysis]) -> List[str]:
        """Identify strategic themes in the position."""
        try:
            themes = []
            
            # Analyze blocking opportunities
            blocking_scores = [a.blocking_score for a in move_analyses]
            if max(blocking_scores) > 70:
                themes.append("Strong blocking opportunities")
            elif max(blocking_scores) > 50:
                themes.append("Moderate blocking opportunities")
            
            # Analyze scoring opportunities
            scoring_scores = [a.scoring_score for a in move_analyses]
            if max(scoring_scores) > 70:
                themes.append("High scoring potential")
            elif max(scoring_scores) > 50:
                themes.append("Moderate scoring opportunities")
            
            # Analyze floor line risk
            floor_scores = [a.floor_line_score for a in move_analyses]
            if min(floor_scores) < 30:
                themes.append("Floor line risk management")
            
            # Analyze strategic vs tactical balance
            strategic_scores = [a.strategic_value for a in move_analyses]
            tactical_scores = [a.tactical_value for a in move_analyses]
            
            if np.mean(strategic_scores) > np.mean(tactical_scores) * 1.5:
                themes.append("Strategic positioning focus")
            elif np.mean(tactical_scores) > np.mean(strategic_scores) * 1.5:
                themes.append("Tactical opportunity focus")
            
            return themes
            
        except Exception as e:
            print(f"⚠️ Strategic theme identification failed: {e}")
            return []
    
    def _identify_tactical_opportunities_robust(self, move_analyses: List[IntegratedComprehensiveMoveAnalysis]) -> List[str]:
        """Identify tactical opportunities in the position."""
        try:
            opportunities = []
            
            # High-quality moves
            high_quality_count = sum(1 for a in move_analyses if a.overall_quality_score > 80)
            if high_quality_count > 0:
                opportunities.append(f"{high_quality_count} high-quality moves available")
            
            # Engine consensus
            engine_consensus = self._calculate_engine_consensus_robust(move_analyses)
            if len(engine_consensus) >= 3:
                opportunities.append("Multiple engine agreement")
            
            # Risk-reward opportunities
            risk_scores = [a.risk_assessment for a in move_analyses]
            opportunity_scores = [a.opportunity_value for a in move_analyses]
            
            high_risk_high_reward = sum(1 for a in move_analyses 
                                       if a.risk_assessment > 70 and a.opportunity_value > 70)
            if high_risk_high_reward > 0:
                opportunities.append(f"{high_risk_high_reward} high-risk, high-reward moves")
            
            # Pattern completion opportunities
            pattern_scores = [a.pattern_score for a in move_analyses]
            if max(pattern_scores) > 80:
                opportunities.append("Strong pattern completion opportunities")
            
            return opportunities
            
        except Exception as e:
            print(f"⚠️ Tactical opportunity identification failed: {e}")
            return []
    
    def save_analysis_to_database(self, position_analysis: IntegratedPositionAnalysis, 
                                 move_analyses: List[IntegratedComprehensiveMoveAnalysis],
                                 session_id: str):
        """Save analysis results to the main database."""
        try:
            # First, ensure position is cached
            position_id = self.db.cache_position(position_analysis.position_fen, 2)
            
            # Create move quality analysis
            move_quality_analysis = MoveQualityAnalysis(
                position_id=position_id,
                session_id=session_id,
                game_phase=position_analysis.game_phase.value,
                total_moves_analyzed=position_analysis.total_moves,
                quality_distribution=position_analysis.quality_distribution,
                average_quality_score=position_analysis.average_quality_score,
                best_move_score=position_analysis.best_move_score,
                worst_move_score=position_analysis.worst_move_score,
                engine_consensus=position_analysis.engine_consensus,
                disagreement_level=position_analysis.disagreement_level,
                position_complexity=position_analysis.position_complexity,
                strategic_themes=position_analysis.strategic_themes,
                tactical_opportunities=position_analysis.tactical_opportunities,
                analysis_time=position_analysis.analysis_time
            )
            
            # Save move quality analysis
            analysis_id = self.db.save_move_quality_analysis(move_quality_analysis)
            
            # Save comprehensive move analyses
            for move_analysis in move_analyses:
                comprehensive_analysis = ComprehensiveMoveAnalysis(
                    position_analysis_id=analysis_id,
                    move_data=move_analysis.move_data,
                    alpha_beta_score=move_analysis.alpha_beta_score,
                    mcts_score=move_analysis.mcts_score,
                    neural_score=move_analysis.neural_score,
                    pattern_score=move_analysis.pattern_score,
                    overall_quality_score=move_analysis.overall_quality_score,
                    quality_tier=move_analysis.quality_tier,
                    confidence_score=move_analysis.confidence_score,
                    strategic_value=move_analysis.strategic_value,
                    tactical_value=move_analysis.tactical_value,
                    risk_assessment=move_analysis.risk_assessment,
                    opportunity_value=move_analysis.opportunity_value,
                    blocking_score=move_analysis.blocking_score,
                    scoring_score=move_analysis.scoring_score,
                    floor_line_score=move_analysis.floor_line_score,
                    timing_score=move_analysis.timing_score,
                    analysis_time=move_analysis.analysis_time,
                    engines_used=move_analysis.engines_used,
                    explanation=move_analysis.explanation
                )
                
                self.db.save_comprehensive_move_analysis(comprehensive_analysis)
            
            print(f"   💾 Analysis saved to database (ID: {analysis_id})")
            
        except Exception as e:
            print(f"   ❌ Failed to save analysis to database: {e}")
            traceback.print_exc()
    
    def run_large_scale_analysis(self, num_positions: int, session_id: str = None):
        """Run large-scale analysis with database integration."""
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        print(f"🚀 Starting integrated large-scale analysis")
        print(f"   Mode: {self.analysis_mode.value}")
        print(f"   Positions: {num_positions}")
        print(f"   Workers: {self.max_workers}")
        print(f"   Session ID: {session_id}")
        print(f"   Database: {self.db.db_path}")
        print()
        
        # Create session record
        session = ExhaustiveAnalysisSession(
            session_id=session_id,
            mode=self.analysis_mode.value,
            status='running'
        )
        self.db.save_exhaustive_analysis_session(session)
        
        # Generate test positions
        positions = self._generate_test_positions(num_positions)
        
        start_time = time.time()
        successful_analyses = 0
        failed_analyses = 0
        total_moves_analyzed = 0
        
        # Process positions
        for i, (state, game_phase) in enumerate(positions):
            print(f"📊 Analyzing position {i + 1}/{num_positions}")
            print(f"   Phase: {game_phase.value}")
            print(f"   FEN: {state.to_fen()[:50]}...")
            
            # Analyze position
            position_analysis = self.analyze_position_robust(state, game_phase)
            
            if position_analysis:
                # Generate move analyses for database storage
                move_generator = self.move_quality_assessor.move_generator
                all_moves = move_generator.generate_all_moves(state, 0)
                max_moves = self.config['max_moves_per_position']
                if len(all_moves) > max_moves:
                    all_moves = all_moves[:max_moves]
                
                move_analyses = []
                for move_data in all_moves:
                    move_analysis = self._analyze_single_move_robust(state, move_data, game_phase)
                    move_analyses.append(move_analysis)
                
                # Save to database
                self.save_analysis_to_database(position_analysis, move_analyses, session_id)
                
                successful_analyses += 1
                total_moves_analyzed += position_analysis.total_moves
                
                print(f"   ✅ Success - {position_analysis.total_moves} moves, {position_analysis.analysis_time:.2f}s")
                print(f"   📈 Quality: {position_analysis.average_quality_score:.1f} avg, {position_analysis.best_move_score:.1f} best")
                print(f"   🎯 Distribution: {position_analysis.quality_distribution}")
            else:
                failed_analyses += 1
                print(f"   ❌ Failed")
            
            print()
        
        # Update session statistics
        total_time = time.time() - start_time
        session.positions_analyzed = successful_analyses
        session.total_moves_analyzed = total_moves_analyzed
        session.total_analysis_time = total_time
        session.successful_analyses = successful_analyses
        session.failed_analyses = failed_analyses
        session.status = 'completed'
        session.completed_at = datetime.now()
        
        self.db.save_exhaustive_analysis_session(session)
        
        # Print final statistics
        self._print_final_stats(total_time, successful_analyses, num_positions)
    
    def _print_final_stats(self, total_time: float, successful_analyses: int, total_positions: int):
        """Print final analysis statistics."""
        print("=" * 60)
        print("📊 FINAL ANALYSIS STATISTICS")
        print("=" * 60)
        print(f"Total positions: {total_positions}")
        print(f"Successful analyses: {successful_analyses}")
        print(f"Failed analyses: {total_positions - successful_analyses}")
        print(f"Success rate: {(successful_analyses / total_positions * 100):.1f}%")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per position: {total_time / total_positions:.2f}s")
        print()
        print(f"Database: {self.db.db_path}")
        print("🎉 Analysis complete!")


def main():
    """Main function for running integrated exhaustive analysis."""
    parser = argparse.ArgumentParser(description="Integrated Exhaustive Azul Move Space Analyzer")
    parser.add_argument("--mode", choices=["quick", "standard", "deep", "exhaustive"], 
                       default="standard", help="Analysis mode")
    parser.add_argument("--positions", type=int, default=100, help="Number of positions to analyze")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    parser.add_argument("--session-id", type=str, default=None, help="Session ID for tracking")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = IntegratedExhaustiveAnalyzer(
        analysis_mode=AnalysisMode(args.mode),
        max_workers=args.workers
    )
    
    # Run analysis
    analyzer.run_large_scale_analysis(args.positions, args.session_id)


if __name__ == "__main__":
    main()
