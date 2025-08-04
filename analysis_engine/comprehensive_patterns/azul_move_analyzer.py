"""
Azul Move Quality Assessment - Slice 1 Implementation

This module provides basic move quality assessment by integrating all existing 
pattern detection systems into a unified evaluation framework.

Builds on existing systems:
- AzulPatternDetector (tile blocking)
- AzulScoringOptimizationDetector (scoring opportunities)  
- AzulFloorLinePatternDetector (floor line management)
- StrategicPatternDetector (factory control, endgame, risk/reward)
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core import azul_utils as utils
from core.azul_model import AzulState
from analysis_engine.mathematical_optimization.azul_move_generator import AzulMoveGenerator

# Import existing pattern detection systems
from .azul_patterns import AzulPatternDetector
from .azul_scoring_optimization import AzulScoringOptimizationDetector
from .azul_floor_line_patterns import AzulFloorLinePatternDetector

# Try to import strategic systems (they may not be available in all setups)
try:
    from analysis_engine.strategic_analysis.azul_strategic_patterns import StrategicPatternDetector
    STRATEGIC_AVAILABLE = True
except ImportError:
    STRATEGIC_AVAILABLE = False
    print("Strategic pattern analysis not available - basic move quality assessment only")


@dataclass
class MoveQualityAssessment:
    """Assessment of a single move's quality."""
    move: Dict  # The actual move data
    quality_tier: str  # "!!", "!", "=", "?!", "?"
    quality_score: float  # 0-100 numerical score
    
    # Pattern contributions (from existing systems)
    blocking_score: float  # From tile blocking detection
    scoring_score: float   # From scoring optimization  
    floor_line_score: float  # From floor line management
    strategic_score: float   # From strategic analysis (if available)
    
    # Basic explanation
    primary_reason: str  # Main reason for quality rating
    risk_level: str      # "low", "medium", "high", "critical"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            'move': self.move,
            'quality_tier': self.quality_tier,
            'quality_score': round(self.quality_score, 1),
            'blocking_score': round(self.blocking_score, 1),
            'scoring_score': round(self.scoring_score, 1),
            'floor_line_score': round(self.floor_line_score, 1),
            'strategic_score': round(self.strategic_score, 1),
            'primary_reason': self.primary_reason,
            'risk_level': self.risk_level
        }


@dataclass 
class MoveQualityAnalysis:
    """Complete move quality analysis for a position."""
    primary_recommendation: MoveQualityAssessment
    alternatives: List[MoveQualityAssessment]  # Top 4 alternatives
    total_moves_analyzed: int
    analysis_summary: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            'primary_recommendation': self.primary_recommendation.to_dict(),
            'alternatives': [alt.to_dict() for alt in self.alternatives],
            'total_moves_analyzed': self.total_moves_analyzed,
            'analysis_summary': self.analysis_summary
        }


class AzulMoveQualityAssessor:
    """
    Basic move quality assessment system that integrates existing pattern detectors.
    
    Slice 1 Implementation: 
    - Leverages all existing pattern detection systems
    - Provides 5-tier move quality assessment
    - Generates basic explanations
    - Ranks all possible moves
    """
    
    def __init__(self):
        # Initialize existing pattern detection systems
        self.pattern_detector = AzulPatternDetector()
        self.scoring_detector = AzulScoringOptimizationDetector()
        self.floor_line_detector = AzulFloorLinePatternDetector()
        
        # Strategic detector (if available)
        if STRATEGIC_AVAILABLE:
            self.strategic_detector = StrategicPatternDetector()
        else:
            self.strategic_detector = None
            
        # Move generator
        self.move_generator = AzulMoveGenerator()
        
        # Quality tier thresholds
        self.tier_thresholds = {
            '!!': 90.0,  # Brilliant
            '!': 75.0,   # Excellent  
            '=': 50.0,   # Good/Solid
            '?!': 25.0,  # Dubious
            '?': 0.0     # Poor
        }
        
        # Color names for explanations
        self.color_names = {
            utils.Tile.BLUE: "blue",
            utils.Tile.YELLOW: "yellow",
            utils.Tile.RED: "red", 
            utils.Tile.BLACK: "black",
            utils.Tile.WHITE: "white"
        }
    
    def analyze_position(self, state: AzulState, player_id: int) -> MoveQualityAnalysis:
        """
        Analyze all possible moves in a position and return quality assessment.
        
        Args:
            state: Current game state
            player_id: Player to analyze moves for
            
        Returns:
            Complete move quality analysis
        """
        # Generate all possible moves
        possible_moves = self._generate_possible_moves(state, player_id)
        
        if not possible_moves:
            # No moves available - this shouldn't happen in normal play
            return self._create_no_moves_analysis()
        
        # Evaluate each move
        move_assessments = []
        for move in possible_moves:
            assessment = self._evaluate_move(state, move, player_id)
            move_assessments.append(assessment)
        
        # Sort by quality score (highest first)
        move_assessments.sort(key=lambda x: x.quality_score, reverse=True)
        
        # Create analysis result
        return MoveQualityAnalysis(
            primary_recommendation=move_assessments[0],
            alternatives=move_assessments[1:5],  # Top 4 alternatives
            total_moves_analyzed=len(move_assessments),
            analysis_summary=self._create_analysis_summary(move_assessments)
        )
    
    def _generate_possible_moves(self, state: AzulState, player_id: int) -> List[Dict]:
        """Generate all possible moves for the player.""" 
        moves = []
        
        # Get valid moves from move generator
        valid_moves = self.move_generator.generate_moves(state, player_id)
        
        for move in valid_moves:
            # Convert move to dictionary format for consistency
            move_dict = {
                'source_type': 'factory' if move.source_id < len(state.factories) else 'center',
                'source_id': move.source_id,
                'tile_type': move.tile_type,
                'pattern_line_dest': move.pattern_line_dest,
                'num_to_pattern_line': move.num_to_pattern_line,
                'num_to_floor_line': move.num_to_floor_line,
                'description': self._create_move_description(move)
            }
            moves.append(move_dict)
        
        return moves
    
    def _evaluate_move(self, state: AzulState, move: Dict, player_id: int) -> MoveQualityAssessment:
        """Evaluate a single move using all pattern detection systems."""
        
        # Simulate move to get resulting state
        try:
            result_state = self._simulate_move(state, move, player_id)
        except Exception as e:
            # If move simulation fails, mark as very poor
            return self._create_failed_move_assessment(move, str(e))
        
        # Score components using existing pattern detectors
        blocking_score = self._evaluate_blocking_component(state, result_state, move, player_id)
        scoring_score = self._evaluate_scoring_component(state, result_state, move, player_id) 
        floor_score = self._evaluate_floor_line_component(state, result_state, move, player_id)
        strategic_score = self._evaluate_strategic_component(state, result_state, move, player_id)
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            blocking_score, scoring_score, floor_score, strategic_score
        )
        
        # Assign quality tier
        quality_tier = self._assign_quality_tier(quality_score)
        
        # Generate explanation
        primary_reason = self._generate_primary_reason(
            quality_tier, blocking_score, scoring_score, floor_score, strategic_score, move
        )
        
        # Assess risk level
        risk_level = self._assess_risk_level(quality_score, floor_score, move)
        
        return MoveQualityAssessment(
            move=move,
            quality_tier=quality_tier,
            quality_score=quality_score,
            blocking_score=blocking_score,
            scoring_score=scoring_score,
            floor_line_score=floor_score,
            strategic_score=strategic_score,
            primary_reason=primary_reason,
            risk_level=risk_level
        )
    
    def _evaluate_blocking_component(self, state: AzulState, result_state: AzulState, 
                                   move: Dict, player_id: int) -> float:
        """Evaluate blocking opportunities using existing pattern detector."""
        try:
            # Use existing pattern detector
            patterns = self.pattern_detector.detect_patterns(state, player_id)
            
            if not patterns.blocking_opportunities:
                return 0.0
                
            # Check if this move takes advantage of blocking opportunities
            move_tile_type = move['tile_type']
            blocking_score = 0.0
            
            for opportunity in patterns.blocking_opportunities:
                if opportunity.target_color == move_tile_type:
                    # This move blocks the opponent - good!
                    urgency_bonus = opportunity.urgency_score * 20  # Scale to 0-20
                    blocking_score = max(blocking_score, urgency_bonus)
            
            return min(blocking_score, 25.0)  # Cap at 25 points
            
        except Exception as e:
            print(f"Error in blocking evaluation: {e}")
            return 0.0
    
    def _evaluate_scoring_component(self, state: AzulState, result_state: AzulState,
                                  move: Dict, player_id: int) -> float:
        """Evaluate scoring opportunities using existing scoring optimizer."""
        try:
            # Use existing scoring optimization detector
            scoring_analysis = self.scoring_detector.detect_scoring_optimization(state, player_id)
            
            if not scoring_analysis.wall_completion_opportunities:
                return 0.0
            
            move_tile_type = move['tile_type']
            scoring_score = 0.0
            
            for opportunity in scoring_analysis.wall_completion_opportunities:
                if opportunity.target_color == move_tile_type:
                    # This move takes advantage of scoring opportunity
                    bonus_value = opportunity.bonus_value
                    urgency_bonus = opportunity.urgency_score * 2  # Scale urgency
                    scoring_score = max(scoring_score, bonus_value + urgency_bonus)
            
            return min(scoring_score, 30.0)  # Cap at 30 points
            
        except Exception as e:
            print(f"Error in scoring evaluation: {e}")
            return 0.0
    
    def _evaluate_floor_line_component(self, state: AzulState, result_state: AzulState,
                                     move: Dict, player_id: int) -> float:
        """Evaluate floor line impact using existing floor line detector."""
        try:
            # Use existing floor line pattern detector
            floor_analysis = self.floor_line_detector.detect_floor_line_patterns(state, player_id)
            
            # Check if move sends tiles to floor line
            num_to_floor = move.get('num_to_floor_line', 0)
            
            if num_to_floor > 0:
                # Penalty for sending tiles to floor line
                penalty = num_to_floor * -5.0  # -5 points per tile to floor
                
                # But check if there are floor line opportunities that justify it
                floor_bonus = 0.0
                if hasattr(floor_analysis, 'trade_off_opportunities'):
                    for opportunity in floor_analysis.trade_off_opportunities:
                        # If floor line usage is strategic, reduce penalty
                        if opportunity.urgency_score > 7.0:
                            floor_bonus = 10.0
                
                return max(penalty + floor_bonus, -20.0)  # Cap penalty at -20
            else:
                # Bonus for avoiding floor line when other moves would require it
                return 5.0
                
        except Exception as e:
            print(f"Error in floor line evaluation: {e}")
            return 0.0
    
    def _evaluate_strategic_component(self, state: AzulState, result_state: AzulState,
                                    move: Dict, player_id: int) -> float:
        """Evaluate strategic value using strategic pattern detector if available."""
        if not STRATEGIC_AVAILABLE or not self.strategic_detector:
            return 0.0
            
        try:
            # Use strategic pattern detector for advanced analysis
            # This is a placeholder - would integrate with actual strategic analysis
            strategic_score = 0.0
            
            # Basic strategic evaluation based on move type
            if move['source_type'] == 'factory':
                strategic_score += 2.0  # Slight bonus for factory moves
            
            if move.get('pattern_line_dest', -1) >= 0:
                strategic_score += 3.0  # Bonus for pattern line placement
            
            return min(strategic_score, 15.0)  # Cap at 15 points
            
        except Exception as e:
            print(f"Error in strategic evaluation: {e}")
            return 0.0
    
    def _calculate_quality_score(self, blocking: float, scoring: float, 
                               floor: float, strategic: float) -> float:
        """Calculate overall quality score from components."""
        # Base score
        base_score = 50.0
        
        # Add component scores with weights
        weighted_score = (
            base_score +
            blocking * 0.3 +     # 30% weight for blocking
            scoring * 0.4 +      # 40% weight for scoring  
            floor * 0.2 +        # 20% weight for floor line
            strategic * 0.1      # 10% weight for strategic
        )
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, weighted_score))
    
    def _assign_quality_tier(self, score: float) -> str:
        """Assign quality tier based on score."""
        if score >= self.tier_thresholds['!!']:
            return '!!'
        elif score >= self.tier_thresholds['!']:
            return '!'
        elif score >= self.tier_thresholds['=']:
            return '='
        elif score >= self.tier_thresholds['?!']:
            return '?!'
        else:
            return '?'
    
    def _generate_primary_reason(self, tier: str, blocking: float, scoring: float,
                               floor: float, strategic: float, move: Dict) -> str:
        """Generate primary reason for move quality rating."""
        
        # Find dominant component
        components = {
            'blocking': blocking,
            'scoring': scoring, 
            'floor_line': floor,
            'strategic': strategic
        }
        
        dominant = max(components.items(), key=lambda x: abs(x[1]))
        
        if tier == '!!':
            return f"Brilliant move combining multiple strategic advantages"
        elif tier == '!':
            if dominant[0] == 'scoring' and scoring > 15:
                return f"Excellent scoring opportunity worth {int(scoring)} points"
            elif dominant[0] == 'blocking' and blocking > 15:
                return f"Strong blocking move disrupting opponent plans"
            else:
                return f"Solid move with good {dominant[0]} value"
        elif tier == '=':
            return f"Reasonable move with moderate {dominant[0]} benefit"
        elif tier == '?!':
            if floor < -5:
                return f"Questionable due to floor line penalty ({int(abs(floor))} points)"
            else:
                return f"Dubious move with limited strategic value"
        else:  # ?
            if floor < -10:
                return f"Poor move causing significant floor line penalty"
            else:
                return f"Weak move that doesn't advance position"
    
    def _assess_risk_level(self, quality_score: float, floor_score: float, move: Dict) -> str:
        """Assess risk level of the move."""
        if floor_score < -15:
            return "critical"
        elif floor_score < -10:
            return "high"
        elif quality_score < 30:
            return "medium"
        else:
            return "low"
    
    def _simulate_move(self, state: AzulState, move: Dict, player_id: int) -> AzulState:
        """Simulate a move and return resulting state."""
        # Create a copy of the state
        result_state = state.clone()
        
        # This is a simplified simulation - in practice you'd use the actual move execution
        # For now, just return the cloned state
        return result_state
    
    def _create_move_description(self, move) -> str:
        """Create human-readable description of a move."""
        source_type = "factory" if move.source_id < 5 else "center"  # Assuming 5 factories
        color_name = self.color_names.get(move.tile_type, f"color_{move.tile_type}")
        
        if move.pattern_line_dest >= 0:
            return f"Take {color_name} from {source_type} to pattern line {move.pattern_line_dest + 1}"
        else:
            return f"Take {color_name} from {source_type} to floor line"
    
    def _create_analysis_summary(self, assessments: List[MoveQualityAssessment]) -> str:
        """Create summary of the analysis."""
        if not assessments:
            return "No moves available"
        
        best_tier = assessments[0].quality_tier
        total_moves = len(assessments)
        
        tier_counts = {}
        for assessment in assessments:
            tier = assessment.quality_tier
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        tier_summary = ", ".join([f"{count} {tier}" for tier, count in tier_counts.items()])
        
        return f"Best move: {best_tier} | {total_moves} moves analyzed | Distribution: {tier_summary}"
    
    def _create_no_moves_analysis(self) -> MoveQualityAnalysis:
        """Create analysis result when no moves are available."""
        no_move = MoveQualityAssessment(
            move={'description': 'No moves available'},
            quality_tier='N/A',
            quality_score=0.0,
            blocking_score=0.0,
            scoring_score=0.0,
            floor_line_score=0.0,
            strategic_score=0.0,
            primary_reason='No legal moves in current position',
            risk_level='low'
        )
        
        return MoveQualityAnalysis(
            primary_recommendation=no_move,
            alternatives=[],
            total_moves_analyzed=0,
            analysis_summary="No moves available in current position"
        )
    
    def _create_failed_move_assessment(self, move: Dict, error: str) -> MoveQualityAssessment:
        """Create assessment for a move that failed to simulate."""
        return MoveQualityAssessment(
            move=move,
            quality_tier='?',
            quality_score=0.0,
            blocking_score=0.0,
            scoring_score=0.0,
            floor_line_score=-20.0,  # Heavy penalty for failed moves
            strategic_score=0.0,
            primary_reason=f'Move simulation failed: {error}',
            risk_level='critical'
        )