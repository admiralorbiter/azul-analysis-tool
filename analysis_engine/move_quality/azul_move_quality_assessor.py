"""
Azul Move Quality Assessment Engine

This module provides a comprehensive move quality assessment system that evaluates,
ranks, and explains all possible moves in any Azul position.

Features:
- 5-tier move quality classification (!!, !, =, ?!, ?)
- Numerical quality scoring (0-100 points)
- Integration with existing pattern detection systems
- Alternative move analysis with explanations
- Educational move explanations with pattern connections
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple, Any
from dataclasses import dataclass
from enum import Enum
from core import azul_utils as utils
from core.azul_model import AzulState

# Import existing pattern detectors for integration
from ..comprehensive_patterns.azul_patterns import AzulPatternDetector, PatternDetection
from ..comprehensive_patterns.azul_scoring_optimization import AzulScoringOptimizationDetector, ScoringOptimizationDetection
from ..comprehensive_patterns.azul_floor_line_patterns import AzulFloorLinePatternDetector, FloorLinePatternDetection

# Import move parser
from .move_parser import AzulMoveParser, ParsedMove, MoveType

# Import move generator
from analysis_engine.mathematical_optimization.azul_move_generator import AzulMoveGenerator

# Import strategic analyzer
from .strategic_analyzer import AzulStrategicAnalyzer, StrategicAnalysis


class MoveQualityTier(Enum):
    """5-tier move quality classification system."""
    BRILLIANT = "!!"    # 90-100 points - Multiple high-value objectives
    EXCELLENT = "!"     # 75-89 points - Primary strategic objective achieved
    GOOD = "="          # 50-74 points - Reasonable, safe moves
    DUBIOUS = "?!"      # 25-49 points - Some benefit but significant downsides
    POOR = "?"          # 0-24 points - Clear mistakes with negative impact


@dataclass
class MoveQualityScore:
    """Detailed move quality assessment with scoring breakdown."""
    overall_score: float  # 0-100 points
    quality_tier: MoveQualityTier
    pattern_scores: Dict[str, float]  # Scores from different pattern detectors
    strategic_value: float
    tactical_value: float
    risk_assessment: float
    opportunity_value: float
    explanation: str
    pattern_connections: List[str]
    alternative_moves: List[Dict]
    confidence_score: float


@dataclass
class MoveQualityAssessment:
    """Complete move quality assessment for a position."""
    position_fen: str
    player_id: int
    all_moves_quality: Dict[str, MoveQualityScore]  # move_key -> quality_score
    best_moves: List[str]  # Top 3-5 moves
    alternative_moves: List[str]  # Alternative moves with explanations
    position_complexity: float
    analysis_confidence: float
    educational_insights: List[str]


class AzulMoveQualityAssessor:
    """
    Comprehensive move quality assessment engine.
    
    This system evaluates all possible moves in an Azul position using:
    - Existing pattern detection systems (blocking, scoring, floor line)
    - Strategic and tactical evaluation
    - Risk assessment and opportunity analysis
    - 5-tier quality classification with detailed explanations
    """
    
    def __init__(self):
        # Initialize existing pattern detectors
        self.pattern_detector = AzulPatternDetector()
        self.scoring_detector = AzulScoringOptimizationDetector()
        self.floor_line_detector = AzulFloorLinePatternDetector()
        
        # Initialize move parser and generator
        self.move_parser = AzulMoveParser()
        self.move_generator = AzulMoveGenerator()
        
        # Initialize strategic analyzer
        self.strategic_analyzer = AzulStrategicAnalyzer()
        
        # Quality scoring parameters
        self.tier_thresholds = {
            MoveQualityTier.BRILLIANT: 90.0,
            MoveQualityTier.EXCELLENT: 75.0,
            MoveQualityTier.GOOD: 50.0,
            MoveQualityTier.DUBIOUS: 25.0,
            MoveQualityTier.POOR: 0.0
        }
        
        # Scoring weights for different components
        self.scoring_weights = {
            'pattern_detection': 0.35,    # Blocking, scoring, floor line patterns
            'strategic_value': 0.25,      # Long-term strategic considerations
            'tactical_value': 0.20,       # Immediate tactical benefits
            'risk_assessment': 0.15,      # Risk evaluation and mitigation
            'opportunity_value': 0.05     # Opportunity creation and exploitation
        }
        
        # Pattern detection confidence thresholds
        self.min_pattern_confidence = 0.6
        self.min_urgency_threshold = 0.5
        
        # Educational complexity levels
        self.complexity_levels = {
            'beginner': 0.3,      # Focus on avoiding mistakes
            'intermediate': 0.6,   # Understanding good moves and patterns
            'advanced': 0.8,       # Recognizing brilliant moves
            'expert': 1.0          # Deep strategic understanding
        }
    
    def assess_move_quality(self, state: AzulState, player_id: int, move_key: str) -> MoveQualityScore:
        """
        Assess the quality of a specific move.
        
        Args:
            state: Current game state
            player_id: Player making the move
            move_key: String representation of the move
            
        Returns:
            MoveQualityScore with detailed assessment
        """
        # Parse the move
        move_data = self._parse_move_key(move_key)
        
        # Get pattern detection scores
        pattern_scores = self._evaluate_pattern_detection(state, player_id, move_data)
        
        # Calculate strategic and tactical values
        strategic_value = self._calculate_strategic_value(state, player_id, move_data)
        tactical_value = self._calculate_tactical_value(state, player_id, move_data)
        
        # Assess risks and opportunities
        risk_assessment = self._assess_risk(state, player_id, move_data)
        opportunity_value = self._calculate_opportunity_value(state, player_id, move_data)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            pattern_scores, strategic_value, tactical_value, 
            risk_assessment, opportunity_value
        )
        
        # Determine quality tier
        quality_tier = self._determine_quality_tier(overall_score)
        
        # Generate explanation and pattern connections
        explanation = self._generate_move_explanation(
            move_data, pattern_scores, strategic_value, tactical_value,
            risk_assessment, opportunity_value, quality_tier
        )
        
        pattern_connections = self._identify_pattern_connections(
            pattern_scores, strategic_value, tactical_value
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            pattern_scores, strategic_value, tactical_value
        )
        
        return MoveQualityScore(
            overall_score=overall_score,
            quality_tier=quality_tier,
            pattern_scores=pattern_scores,
            strategic_value=strategic_value,
            tactical_value=tactical_value,
            risk_assessment=risk_assessment,
            opportunity_value=opportunity_value,
            explanation=explanation,
            pattern_connections=pattern_connections,
            alternative_moves=[],  # Will be populated later
            confidence_score=confidence_score
        )
    
    def evaluate_all_moves(self, state: AzulState, player_id: int) -> MoveQualityAssessment:
        """
        Evaluate all possible moves in the current position.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            MoveQualityAssessment with all moves evaluated
        """
        # Generate all possible moves
        all_moves = self._generate_all_possible_moves(state, player_id)
        
        # Assess quality for each move
        all_moves_quality = {}
        for move_key in all_moves:
            quality_score = self.assess_move_quality(state, player_id, move_key)
            all_moves_quality[move_key] = quality_score
        
        # Find best moves and alternatives
        best_moves = self._identify_best_moves(all_moves_quality)
        alternative_moves = self._identify_alternative_moves(all_moves_quality)
        
        # Calculate position complexity
        position_complexity = self._calculate_position_complexity(state, player_id)
        
        # Generate educational insights
        educational_insights = self._generate_educational_insights(all_moves_quality)
        
        # Calculate overall analysis confidence
        analysis_confidence = self._calculate_analysis_confidence(all_moves_quality)
        
        return MoveQualityAssessment(
            position_fen=state.to_fen(),
            player_id=player_id,
            all_moves_quality=all_moves_quality,
            best_moves=best_moves,
            alternative_moves=alternative_moves,
            position_complexity=position_complexity,
            analysis_confidence=analysis_confidence,
            educational_insights=educational_insights
        )
    
    def _parse_move_key(self, move_key: str) -> ParsedMove:
        """Parse move key string into structured move data."""
        return self.move_parser.parse_move(move_key)
    
    def _evaluate_pattern_detection(self, state: AzulState, player_id: int, move_data: ParsedMove) -> Dict[str, float]:
        """Evaluate move using existing pattern detection systems."""
        pattern_scores = {}
        
        try:
            # Blocking pattern detection
            blocking_analysis = self.pattern_detector.detect_patterns(state, player_id)
            pattern_scores['blocking'] = self._score_blocking_patterns(blocking_analysis, move_data)
        except Exception as e:
            pattern_scores['blocking'] = 0.0
        
        try:
            # Scoring optimization detection
            scoring_analysis = self.scoring_detector.detect_scoring_optimization(state, player_id)
            pattern_scores['scoring'] = self._score_scoring_patterns(scoring_analysis, move_data)
        except Exception as e:
            pattern_scores['scoring'] = 0.0
        
        try:
            # Floor line pattern detection
            floor_line_analysis = self.floor_line_detector.detect_floor_line_patterns(state, player_id)
            pattern_scores['floor_line'] = self._score_floor_line_patterns(floor_line_analysis, move_data)
        except Exception as e:
            pattern_scores['floor_line'] = 0.0
        
        return pattern_scores
    
    def _score_blocking_patterns(self, blocking_analysis: PatternDetection, move_data: ParsedMove) -> float:
        """Score move based on blocking pattern detection."""
        if not blocking_analysis.patterns_detected:
            return 0.0
        
        # Calculate score based on blocking opportunities
        total_score = 0.0
        for opportunity in blocking_analysis.blocking_opportunities:
            if opportunity.urgency_score >= self.min_urgency_threshold:
                total_score += opportunity.urgency_score * 10  # Scale to 0-100
        
        return min(total_score, 100.0)
    
    def _score_scoring_patterns(self, scoring_analysis: ScoringOptimizationDetection, move_data: ParsedMove) -> float:
        """Score move based on scoring optimization detection."""
        if scoring_analysis.total_opportunities == 0:
            return 0.0
        
        # Calculate score based on scoring opportunities
        total_score = 0.0
        for opportunity in scoring_analysis.wall_completion_opportunities:
            total_score += opportunity.bonus_value
        
        for opportunity in scoring_analysis.pattern_line_opportunities:
            total_score += opportunity.bonus_value
        
        # Normalize to 0-100 scale
        return min(total_score / 10.0, 100.0)
    
    def _score_floor_line_patterns(self, floor_line_analysis: FloorLinePatternDetection, move_data: ParsedMove) -> float:
        """Score move based on floor line pattern detection."""
        if floor_line_analysis.total_opportunities == 0:
            return 0.0
        
        # Calculate score based on floor line opportunities
        total_score = 0.0
        for opportunity in floor_line_analysis.risk_mitigation_opportunities:
            total_score += opportunity.urgency_score * 10
        
        for opportunity in floor_line_analysis.timing_optimization_opportunities:
            total_score += opportunity.urgency_score * 8
        
        return min(total_score, 100.0)
    
    def _calculate_strategic_value(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Calculate strategic value of the move."""
        try:
            # Use strategic analyzer to get comprehensive strategic assessment
            strategic_analysis = self.strategic_analyzer.analyze_strategic_value(state, player_id, move_data)
            return strategic_analysis.overall_strategic_value
        except Exception as e:
            print(f"Warning: Strategic analysis failed: {e}")
            return 50.0  # Fallback value
    
    def _calculate_tactical_value(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Calculate tactical value of the move."""
        try:
            tactical_score = 0.0
            tactical_factors = 0
            
            # 1. Immediate Scoring Opportunities
            if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
                # Check if this completes a pattern line
                pattern_line = move_data.pattern_line_id
                if pattern_line is not None:
                    player_board = state.agents[player_id]
                    current_tiles = player_board.lines_number[pattern_line]
                    tile_color = move_data.tile_color
                    
                    # Calculate completion value
                    if current_tiles + 1 == pattern_line + 1:
                        # This completes the pattern line
                        tactical_score += 25.0
                        tactical_factors += 1
                    
                    # Check if this sets up wall placement
                    wall_row = pattern_line
                    wall_col = self._get_wall_column_for_color(tile_color)
                    if not player_board.grid_state[wall_row][wall_col]:
                        tactical_score += 15.0
                        tactical_factors += 1
            
            # 2. Floor Line Management
            if move_data.move_type == MoveType.FACTORY_TO_FLOOR:
                # Evaluate floor line penalty avoidance
                floor_penalty = len(state.agents[player_id].floor_tiles)
                if floor_penalty < 3:  # Low penalty
                    tactical_score += 20.0
                    tactical_factors += 1
                elif floor_penalty < 6:  # Medium penalty
                    tactical_score += 10.0
                    tactical_factors += 1
                else:  # High penalty
                    tactical_score -= 10.0
                    tactical_factors += 1
            
            # 3. Wall Placement Value
            if move_data.move_type == MoveType.FACTORY_TO_WALL:
                wall_row = move_data.target_position[0] if move_data.target_position else None
                wall_col = move_data.target_position[1] if move_data.target_position else None
                if wall_row is not None and wall_col is not None:
                    # Check for row/column completion
                    player_board = state.agents[player_id]
                    
                    # Row completion check
                    row_completion = sum(1 for col in range(5) if player_board.grid_state[wall_row][col])
                    if row_completion == 4:  # Will complete row
                        tactical_score += 30.0
                        tactical_factors += 1
                    
                    # Column completion check
                    col_completion = sum(1 for row in range(5) if player_board.grid_state[row][wall_col])
                    if col_completion == 4:  # Will complete column
                        tactical_score += 30.0
                        tactical_factors += 1
            
            # 4. Tile Efficiency
            if move_data.tile_color:
                # Check if this tile is efficiently used
                tile_efficiency = self._calculate_tile_efficiency(state, player_id, move_data)
                tactical_score += tile_efficiency
                tactical_factors += 1
            
            # 5. Immediate Pattern Benefits
            pattern_benefits = self._calculate_immediate_pattern_benefits(state, player_id, move_data)
            tactical_score += pattern_benefits
            if pattern_benefits > 0:
                tactical_factors += 1
            
            # Normalize score
            if tactical_factors > 0:
                tactical_score = tactical_score / tactical_factors
            
            return max(0.0, min(100.0, tactical_score))
            
        except Exception as e:
            print(f"Warning: Tactical analysis failed: {e}")
            return 50.0  # Fallback value
    
    def _get_wall_column_for_color(self, tile_color) -> int:
        """Get wall column for a given tile color."""
        color_to_column = {
            'blue': 0, 'yellow': 1, 'red': 2, 'black': 3, 'white': 4
        }
        return color_to_column.get(tile_color, 0)
    
    def _calculate_tile_efficiency(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Calculate how efficiently the tile is being used."""
        efficiency_score = 0.0
        
        if move_data.tile_color and move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # Check if this tile fits well in the pattern line
                if current_tiles < pattern_line + 1:
                    efficiency_score += 15.0
                
                # Check if this avoids overflow
                if current_tiles + 1 <= pattern_line + 1:
                    efficiency_score += 10.0
        
        return efficiency_score
    
    def _calculate_immediate_pattern_benefits(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Calculate immediate benefits from pattern recognition."""
        benefits_score = 0.0
        
        # Check for immediate scoring patterns
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                # Check if this creates a scoring opportunity
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # If this completes a pattern line, it's a strong tactical move
                if current_tiles + 1 == pattern_line + 1:
                    benefits_score += 20.0
        
        return benefits_score
    
    def _assess_risk(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess risk associated with the move."""
        try:
            risk_score = 50.0  # Start at neutral
            risk_factors = 0
            
            # 1. Floor Line Risk Assessment
            floor_line_risk = self._assess_floor_line_risk(state, player_id, move_data)
            risk_score += floor_line_risk
            risk_factors += 1
            
            # 2. Pattern Line Overflow Risk
            overflow_risk = self._assess_overflow_risk(state, player_id, move_data)
            risk_score += overflow_risk
            risk_factors += 1
            
            # 3. Opponent Opportunity Risk
            opponent_risk = self._assess_opponent_opportunity_risk(state, player_id, move_data)
            risk_score += opponent_risk
            risk_factors += 1
            
            # 4. Timing Risk
            timing_risk = self._assess_timing_risk(state, player_id, move_data)
            risk_score += timing_risk
            risk_factors += 1
            
            # 5. Strategic Risk
            strategic_risk = self._assess_strategic_risk(state, player_id, move_data)
            risk_score += strategic_risk
            risk_factors += 1
            
            # Normalize risk score (lower is better for risk)
            if risk_factors > 0:
                risk_score = risk_score / risk_factors
            
            # Convert to risk assessment (higher score = lower risk)
            risk_assessment = 100.0 - risk_score
            return max(0.0, min(100.0, risk_assessment))
            
        except Exception as e:
            print(f"Warning: Risk assessment failed: {e}")
            return 50.0  # Fallback value
    
    def _assess_floor_line_risk(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess floor line penalty risk."""
        risk_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_FLOOR:
            # Taking tiles to floor is inherently risky
            risk_score += 20.0
            
            # Check current floor line state
            current_floor = len(state.agents[player_id].floor_tiles)
            if current_floor >= 6:  # High penalty
                risk_score += 30.0
            elif current_floor >= 3:  # Medium penalty
                risk_score += 15.0
        
        return risk_score
    
    def _assess_overflow_risk(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess pattern line overflow risk."""
        risk_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # Check if this would cause overflow
                if current_tiles >= pattern_line + 1:
                    risk_score += 25.0
                
                # Check if this creates overflow potential
                if current_tiles + 1 > pattern_line + 1:
                    risk_score += 15.0
        
        return risk_score
    
    def _assess_opponent_opportunity_risk(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess risk of creating opportunities for opponents."""
        risk_score = 0.0
        
        # Check if this move gives opponents good options
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            factory_id = move_data.factory_id
            tile_color = move_data.tile_color
            
            if factory_id is not None and tile_color is not None:
                # Check if this leaves good tiles for opponents
                factory = state.factories[factory_id]
                remaining_tiles = [tile for tile in factory.tiles if tile != tile_color]
                
                # If remaining tiles are valuable, this creates opponent opportunity
                if len(remaining_tiles) > 0:
                    risk_score += 10.0
        
        return risk_score
    
    def _assess_timing_risk(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess timing and tempo risks."""
        risk_score = 0.0
        
        # Check if this is a pass move at a bad time
        if move_data.move_type == MoveType.PASS:
            # Passing early can be risky
            if len(state.factories) > 2:  # Still many factories left
                risk_score += 15.0
        
        # Check if this move is too early or too late
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # If pattern line is empty and it's late game, this might be too late
                if current_tiles == 0 and len(state.factories) <= 2:
                    risk_score += 10.0
        
        return risk_score
    
    def _assess_strategic_risk(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess strategic positioning risks."""
        risk_score = 0.0
        
        # Check if this move commits to a risky strategy
        if move_data.move_type == MoveType.FACTORY_TO_WALL:
            wall_row = move_data.target_position[0] if move_data.target_position else None
            wall_col = move_data.target_position[1] if move_data.target_position else None
            
            if wall_row is not None and wall_col is not None:
                player_board = state.agents[player_id]
                
                # Check if this creates isolated tiles
                isolated_risk = self._check_isolated_tile_risk(player_board, wall_row, wall_col)
                risk_score += isolated_risk
        
        return risk_score
    
    def _check_isolated_tile_risk(self, player_board, wall_row: int, wall_col: int) -> float:
        """Check risk of creating isolated tiles on the wall."""
        risk_score = 0.0
        
        # Check if this tile would be isolated (no adjacent tiles)
        adjacent_tiles = 0
        
        # Check all 4 adjacent positions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = wall_row + dr, wall_col + dc
            if (0 <= new_row < 5 and 0 <= new_col < 5 and 
                player_board.grid_state[new_row][new_col]):
                adjacent_tiles += 1
        
        # If no adjacent tiles, this is risky
        if adjacent_tiles == 0:
            risk_score += 15.0
        
        return risk_score
    
    def _calculate_opportunity_value(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Calculate opportunity value of the move."""
        try:
            opportunity_score = 0.0
            opportunity_factors = 0
            
            # 1. Scoring Opportunities
            scoring_opportunities = self._assess_scoring_opportunities(state, player_id, move_data)
            opportunity_score += scoring_opportunities
            if scoring_opportunities > 0:
                opportunity_factors += 1
            
            # 2. Pattern Completion Opportunities
            pattern_opportunities = self._assess_pattern_opportunities(state, player_id, move_data)
            opportunity_score += pattern_opportunities
            if pattern_opportunities > 0:
                opportunity_factors += 1
            
            # 3. Blocking Opportunities
            blocking_opportunities = self._assess_blocking_opportunities(state, player_id, move_data)
            opportunity_score += blocking_opportunities
            if blocking_opportunities > 0:
                opportunity_factors += 1
            
            # 4. Future Opportunity Creation
            future_opportunities = self._assess_future_opportunities(state, player_id, move_data)
            opportunity_score += future_opportunities
            if future_opportunities > 0:
                opportunity_factors += 1
            
            # 5. Multiplier Opportunities
            multiplier_opportunities = self._assess_multiplier_opportunities(state, player_id, move_data)
            opportunity_score += multiplier_opportunities
            if multiplier_opportunities > 0:
                opportunity_factors += 1
            
            # Normalize score
            if opportunity_factors > 0:
                opportunity_score = opportunity_score / opportunity_factors
            
            return max(0.0, min(100.0, opportunity_score))
            
        except Exception as e:
            print(f"Warning: Opportunity analysis failed: {e}")
            return 50.0  # Fallback value
    
    def _assess_scoring_opportunities(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess immediate scoring opportunities created by this move."""
        opportunity_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # Check if this creates a scoring opportunity
                if current_tiles + 1 == pattern_line + 1:
                    # This completes the pattern line - scoring opportunity
                    opportunity_score += 25.0
                
                # Check if this sets up wall placement
                tile_color = move_data.tile_color
                if tile_color is not None:
                    wall_row = pattern_line
                    wall_col = self._get_wall_column_for_color(tile_color)
                    if not player_board.grid_state[wall_row][wall_col]:
                        opportunity_score += 15.0
        
        return opportunity_score
    
    def _assess_pattern_opportunities(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess pattern completion opportunities."""
        opportunity_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # Check if this progresses toward pattern completion
                if current_tiles < pattern_line + 1:
                    progress_ratio = (current_tiles + 1) / (pattern_line + 1)
                    opportunity_score += progress_ratio * 20.0
        
        return opportunity_score
    
    def _assess_blocking_opportunities(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess opportunities to block opponents."""
        opportunity_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            factory_id = move_data.factory_id
            tile_color = move_data.tile_color
            
            if factory_id is not None and tile_color is not None:
                # Check if this denies valuable tiles to opponents
                factory = state.factories[factory_id]
                tile_count = sum(1 for tile in factory.tiles if tile == tile_color)
                
                # If taking a lot of tiles, this blocks opponents
                if tile_count > 1:
                    opportunity_score += tile_count * 5.0
        
        return opportunity_score
    
    def _assess_future_opportunities(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess opportunities created for future turns."""
        opportunity_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            pattern_line = move_data.pattern_line_id
            if pattern_line is not None:
                player_board = state.agents[player_id]
                current_tiles = player_board.lines_number[pattern_line]
                
                # Check if this sets up future wall placements
                tile_color = move_data.tile_color
                if tile_color is not None:
                    wall_row = pattern_line
                    wall_col = self._get_wall_column_for_color(tile_color)
                    
                    # Check if this tile can be placed on wall in future
                    if not player_board.grid_state[wall_row][wall_col]:
                        # Check if this creates a good wall structure
                        wall_structure_value = self._assess_wall_structure_opportunity(
                            player_board, wall_row, wall_col
                        )
                        opportunity_score += wall_structure_value
        
        return opportunity_score
    
    def _assess_wall_structure_opportunity(self, player_board, wall_row: int, wall_col: int) -> float:
        """Assess the opportunity value of wall structure creation."""
        opportunity_score = 0.0
        
        # Check if this creates good wall structure
        adjacent_tiles = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = wall_row + dr, wall_col + dc
            if (0 <= new_row < 5 and 0 <= new_col < 5 and 
                player_board.grid_state[new_row][new_col]):
                adjacent_tiles += 1
        
        # Good wall structure has adjacent tiles
        if adjacent_tiles > 0:
            opportunity_score += adjacent_tiles * 5.0
        
        return opportunity_score
    
    def _assess_multiplier_opportunities(self, state: AzulState, player_id: int, move_data: ParsedMove) -> float:
        """Assess multiplier and bonus opportunities."""
        opportunity_score = 0.0
        
        if move_data.move_type == MoveType.FACTORY_TO_WALL:
            wall_row = move_data.target_position[0] if move_data.target_position else None
            wall_col = move_data.target_position[1] if move_data.target_position else None
            
            if wall_row is not None and wall_col is not None:
                player_board = state.agents[player_id]
                
                # Check for row completion opportunity
                row_completion = sum(1 for col in range(5) if player_board.grid_state[wall_row][col])
                if row_completion == 4:  # Will complete row
                    opportunity_score += 20.0
                
                # Check for column completion opportunity
                col_completion = sum(1 for row in range(5) if player_board.grid_state[row][wall_col])
                if col_completion == 4:  # Will complete column
                    opportunity_score += 20.0
        
        return opportunity_score
    
    def _calculate_overall_score(self, pattern_scores: Dict[str, float], 
                                strategic_value: float, tactical_value: float,
                                risk_assessment: float, opportunity_value: float) -> float:
        """Calculate overall move quality score."""
        # Weighted combination of all components
        pattern_score = sum(pattern_scores.values()) / len(pattern_scores) if pattern_scores else 0.0
        
        overall_score = (
            pattern_score * self.scoring_weights['pattern_detection'] +
            strategic_value * self.scoring_weights['strategic_value'] +
            tactical_value * self.scoring_weights['tactical_value'] +
            risk_assessment * self.scoring_weights['risk_assessment'] +
            opportunity_value * self.scoring_weights['opportunity_value']
        )
        
        return max(0.0, min(100.0, overall_score))
    
    def _determine_quality_tier(self, overall_score: float) -> MoveQualityTier:
        """Determine quality tier based on overall score."""
        if overall_score >= self.tier_thresholds[MoveQualityTier.BRILLIANT]:
            return MoveQualityTier.BRILLIANT
        elif overall_score >= self.tier_thresholds[MoveQualityTier.EXCELLENT]:
            return MoveQualityTier.EXCELLENT
        elif overall_score >= self.tier_thresholds[MoveQualityTier.GOOD]:
            return MoveQualityTier.GOOD
        elif overall_score >= self.tier_thresholds[MoveQualityTier.DUBIOUS]:
            return MoveQualityTier.DUBIOUS
        else:
            return MoveQualityTier.POOR
    
    def _generate_move_explanation(self, move_data: ParsedMove, pattern_scores: Dict[str, float],
                                  strategic_value: float, tactical_value: float,
                                  risk_assessment: float, opportunity_value: float,
                                  quality_tier: MoveQualityTier) -> str:
        """Generate detailed explanation for the move."""
        try:
            explanation_parts = []
            
            # 1. Quality tier explanation
            tier_explanation = self._explain_quality_tier(quality_tier)
            explanation_parts.append(tier_explanation)
            
            # 2. Strategic insights
            if strategic_value > 70:
                explanation_parts.append("This move has strong strategic value.")
            elif strategic_value > 50:
                explanation_parts.append("This move provides decent strategic positioning.")
            elif strategic_value < 30:
                explanation_parts.append("This move has limited strategic value.")
            
            # 3. Tactical insights
            if tactical_value > 70:
                explanation_parts.append("This move creates immediate tactical benefits.")
            elif tactical_value > 50:
                explanation_parts.append("This move has reasonable tactical value.")
            elif tactical_value < 30:
                explanation_parts.append("This move lacks immediate tactical benefits.")
            
            # 4. Risk assessment
            if risk_assessment > 70:
                explanation_parts.append("This move is relatively safe with low risk.")
            elif risk_assessment < 30:
                explanation_parts.append("This move carries significant risk.")
            else:
                explanation_parts.append("This move has moderate risk.")
            
            # 5. Opportunity insights
            if opportunity_value > 70:
                explanation_parts.append("This move creates excellent opportunities.")
            elif opportunity_value > 50:
                explanation_parts.append("This move creates some opportunities.")
            elif opportunity_value < 30:
                explanation_parts.append("This move creates limited opportunities.")
            
            # 6. Pattern-specific insights
            pattern_insights = self._generate_pattern_insights(move_data, pattern_scores)
            if pattern_insights:
                explanation_parts.append(pattern_insights)
            
            # 7. Move-specific insights
            move_insights = self._generate_move_specific_insights(move_data)
            if move_insights:
                explanation_parts.append(move_insights)
            
            # Combine all parts
            explanation = " ".join(explanation_parts)
            
            # Add overall assessment
            overall_score = sum(pattern_scores.values()) / len(pattern_scores) if pattern_scores else 0.0
            explanation += f" Overall score: {overall_score:.1f}/100."
            
            return explanation
            
        except Exception as e:
            print(f"Warning: Move explanation generation failed: {e}")
            return f"This is a {quality_tier.value} move with an overall score of {sum(pattern_scores.values()) / len(pattern_scores) if pattern_scores else 0:.1f}/100."
    
    def _explain_quality_tier(self, quality_tier: MoveQualityTier) -> str:
        """Explain what the quality tier means."""
        tier_explanations = {
            MoveQualityTier.BRILLIANT: "This is a brilliant move that achieves multiple high-value objectives simultaneously.",
            MoveQualityTier.EXCELLENT: "This is an excellent move that achieves primary strategic objectives with clear benefits.",
            MoveQualityTier.GOOD: "This is a solid move that doesn't harm your position and achieves basic objectives.",
            MoveQualityTier.DUBIOUS: "This move has some benefit but carries significant downsides or risks.",
            MoveQualityTier.POOR: "This move has clear negative impact and should generally be avoided."
        }
        return tier_explanations.get(quality_tier, "This move has moderate quality.")
    
    def _generate_pattern_insights(self, move_data: ParsedMove, pattern_scores: Dict[str, float]) -> str:
        """Generate insights based on pattern detection scores."""
        insights = []
        
        if pattern_scores.get('blocking', 0) > 60:
            insights.append("This move effectively blocks opponents.")
        elif pattern_scores.get('blocking', 0) < 30:
            insights.append("This move doesn't provide much blocking value.")
        
        if pattern_scores.get('scoring', 0) > 60:
            insights.append("This move creates good scoring opportunities.")
        elif pattern_scores.get('scoring', 0) < 30:
            insights.append("This move has limited scoring potential.")
        
        if pattern_scores.get('floor_line', 0) > 60:
            insights.append("This move manages floor line penalties well.")
        elif pattern_scores.get('floor_line', 0) < 30:
            insights.append("This move may create floor line issues.")
        
        return " ".join(insights) if insights else ""
    
    def _generate_move_specific_insights(self, move_data: ParsedMove) -> str:
        """Generate insights specific to the move type."""
        if move_data.move_type == MoveType.FACTORY_TO_PATTERN_LINE:
            return "This move efficiently uses pattern lines to set up wall placement."
        elif move_data.move_type == MoveType.FACTORY_TO_FLOOR:
            return "This move takes tiles to floor, which should be done carefully."
        elif move_data.move_type == MoveType.FACTORY_TO_WALL:
            return "This move directly places tiles on the wall for immediate scoring."
        elif move_data.move_type == MoveType.PASS:
            return "This pass move should be used strategically when no good options are available."
        else:
            return ""
    
    def _identify_pattern_connections(self, pattern_scores: Dict[str, float],
                                    strategic_value: float, tactical_value: float) -> List[str]:
        """Identify pattern connections for educational purposes."""
        connections = []
        
        if pattern_scores.get('blocking', 0) > 0:
            connections.append("This move applies blocking pattern principles")
        
        if pattern_scores.get('scoring', 0) > 0:
            connections.append("This move creates scoring opportunities")
        
        if pattern_scores.get('floor_line', 0) > 0:
            connections.append("This move optimizes floor line management")
        
        return connections
    
    def _calculate_confidence_score(self, pattern_scores: Dict[str, float],
                                  strategic_value: float, tactical_value: float) -> float:
        """Calculate confidence in the assessment."""
        try:
            confidence_factors = []
            
            # 1. Pattern detection confidence
            if pattern_scores:
                pattern_confidence = sum(pattern_scores.values()) / len(pattern_scores) / 100.0
                confidence_factors.append(pattern_confidence)
            
            # 2. Strategic analysis confidence
            strategic_confidence = min(strategic_value / 100.0, 1.0)
            confidence_factors.append(strategic_confidence)
            
            # 3. Tactical analysis confidence
            tactical_confidence = min(tactical_value / 100.0, 1.0)
            confidence_factors.append(tactical_confidence)
            
            # 4. Data quality confidence
            data_quality = self._assess_data_quality()
            confidence_factors.append(data_quality)
            
            # 5. Analysis consistency
            consistency = self._assess_analysis_consistency(pattern_scores, strategic_value, tactical_value)
            confidence_factors.append(consistency)
            
            # Calculate overall confidence
            if confidence_factors:
                overall_confidence = sum(confidence_factors) / len(confidence_factors)
                return max(0.0, min(1.0, overall_confidence))
            else:
                return 0.5  # Default confidence
            
        except Exception as e:
            print(f"Warning: Confidence calculation failed: {e}")
            return 0.5  # Fallback confidence
    
    def _assess_data_quality(self) -> float:
        """Assess the quality of input data for analysis."""
        # This could be enhanced to check data completeness, validity, etc.
        return 0.8  # Assume good data quality for now
    
    def _assess_analysis_consistency(self, pattern_scores: Dict[str, float],
                                   strategic_value: float, tactical_value: float) -> float:
        """Assess consistency between different analysis components."""
        try:
            consistency_score = 0.0
            factors = 0
            
            # Check if pattern scores are consistent
            if pattern_scores:
                pattern_values = list(pattern_scores.values())
                if len(pattern_values) > 1:
                    # Calculate variance in pattern scores
                    mean_pattern = sum(pattern_values) / len(pattern_values)
                    variance = sum((v - mean_pattern) ** 2 for v in pattern_values) / len(pattern_values)
                    
                    # Lower variance = higher consistency
                    consistency_score += max(0.0, 1.0 - variance / 1000.0)
                    factors += 1
            
            # Check if strategic and tactical values are reasonable
            if strategic_value >= 0 and tactical_value >= 0:
                # Values should be in reasonable range
                if 0 <= strategic_value <= 100 and 0 <= tactical_value <= 100:
                    consistency_score += 1.0
                    factors += 1
            
            # Check for extreme inconsistencies
            if strategic_value > 90 and tactical_value < 10:
                consistency_score -= 0.2  # Penalty for extreme inconsistency
            elif tactical_value > 90 and strategic_value < 10:
                consistency_score -= 0.2  # Penalty for extreme inconsistency
            
            if factors > 0:
                return max(0.0, min(1.0, consistency_score / factors))
            else:
                return 0.7  # Default consistency
            
        except Exception as e:
            print(f"Warning: Consistency assessment failed: {e}")
            return 0.7  # Fallback consistency
    
    def _generate_all_possible_moves(self, state: AzulState, player_id: int) -> List[str]:
        """Generate all possible moves for the current position."""
        try:
            # Use the move generator to get all legal moves
            moves = self.move_generator.generate_moves(state, player_id)
            
            # Convert moves to string format
            move_keys = []
            for move in moves:
                # Convert move to string format that our parser can handle
                move_key = self._convert_move_to_key(move)
                if move_key:
                    move_keys.append(move_key)
            
            return move_keys
        except Exception as e:
            print(f"Warning: Move generation failed: {e}")
            return ["pass"]  # Fallback to pass move
    
    def _identify_best_moves(self, all_moves_quality: Dict[str, MoveQualityScore]) -> List[str]:
        """Identify the best moves from the assessment."""
        # Sort moves by overall score
        sorted_moves = sorted(
            all_moves_quality.items(),
            key=lambda x: x[1].overall_score,
            reverse=True
        )
        
        # Return top 3-5 moves
        return [move_key for move_key, _ in sorted_moves[:5]]
    
    def _identify_alternative_moves(self, all_moves_quality: Dict[str, MoveQualityScore]) -> List[str]:
        """Identify alternative moves with explanations."""
        # TODO: Implement alternative move identification
        # This will find moves that are good alternatives to the best moves
        return []
    
    def _calculate_position_complexity(self, state: AzulState, player_id: int) -> float:
        """Calculate position complexity for educational purposes."""
        # TODO: Implement position complexity calculation
        # This will evaluate how complex the position is
        return 0.6  # Placeholder
    
    def _generate_educational_insights(self, all_moves_quality: Dict[str, MoveQualityScore]) -> List[str]:
        """Generate educational insights from the analysis."""
        insights = []
        
        # Count moves by quality tier
        tier_counts = {}
        for quality_score in all_moves_quality.values():
            tier = quality_score.quality_tier
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        # Generate insights based on distribution
        if tier_counts.get(MoveQualityTier.BRILLIANT, 0) > 0:
            insights.append("This position contains brilliant moves - look for multiple high-value objectives")
        
        if tier_counts.get(MoveQualityTier.POOR, 0) > len(all_moves_quality) * 0.5:
            insights.append("This position is challenging - many moves have significant downsides")
        
        return insights
    
    def _calculate_analysis_confidence(self, all_moves_quality: Dict[str, MoveQualityScore]) -> float:
        """Calculate overall confidence in the analysis."""
        if not all_moves_quality:
            return 0.0
        
        # Average confidence scores
        avg_confidence = sum(score.confidence_score for score in all_moves_quality.values()) / len(all_moves_quality)
        
        return avg_confidence
    
    def _convert_move_to_key(self, move) -> str:
        """Convert a move object to a string key format."""
        try:
            # This is a placeholder implementation
            # In a real implementation, you would convert the move object
            # to a string format that matches our parser's expected format
            
            # For now, return a simple format that our parser can handle
            if hasattr(move, 'action') and move.action == 'pass':
                return "pass"
            else:
                # Convert other move types to string format
                # This would need to be implemented based on the actual move object structure
                return f"factory_{getattr(move, 'factory_id', 0)}_tile_{getattr(move, 'color', 'blue')}_pattern_line_{getattr(move, 'pattern_line_id', 0)}"
        except Exception as e:
            print(f"Warning: Move conversion failed: {e}")
            return "pass"  # Fallback 