"""
Tests for Move Quality Assessment System

This module tests the core move quality assessment functionality.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from core.azul_model import AzulState
from analysis_engine.move_quality import (
    AzulMoveQualityAssessor,
    MoveQualityTier,
    MoveQualityScore,
    MoveQualityAssessment
)


class TestMoveQualityTier:
    """Test the 5-tier move quality classification system."""
    
    def test_tier_enum_values(self):
        """Test that tier enum values are correct."""
        assert MoveQualityTier.BRILLIANT.value == "!!"
        assert MoveQualityTier.EXCELLENT.value == "!"
        assert MoveQualityTier.GOOD.value == "="
        assert MoveQualityTier.DUBIOUS.value == "?!"
        assert MoveQualityTier.POOR.value == "?"
    
    def test_tier_ordering(self):
        """Test that tiers are properly ordered by quality."""
        tiers = list(MoveQualityTier)
        # Should be ordered from best to worst
        assert tiers[0] == MoveQualityTier.BRILLIANT
        assert tiers[-1] == MoveQualityTier.POOR


class TestAzulMoveQualityAssessor:
    """Test the main move quality assessment engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.assessor = AzulMoveQualityAssessor()
        self.mock_state = Mock(spec=AzulState)
        self.mock_state.to_fen.return_value = "test_fen_string"
    
    def test_initialization(self):
        """Test that the assessor initializes correctly."""
        assert self.assessor is not None
        assert hasattr(self.assessor, 'pattern_detector')
        assert hasattr(self.assessor, 'scoring_detector')
        assert hasattr(self.assessor, 'floor_line_detector')
        assert hasattr(self.assessor, 'tier_thresholds')
        assert hasattr(self.assessor, 'scoring_weights')
    
    def test_tier_thresholds(self):
        """Test that tier thresholds are properly set."""
        thresholds = self.assessor.tier_thresholds
        assert thresholds[MoveQualityTier.BRILLIANT] == 90.0
        assert thresholds[MoveQualityTier.EXCELLENT] == 75.0
        assert thresholds[MoveQualityTier.GOOD] == 50.0
        assert thresholds[MoveQualityTier.DUBIOUS] == 25.0
        assert thresholds[MoveQualityTier.POOR] == 0.0
    
    def test_scoring_weights(self):
        """Test that scoring weights sum to approximately 1.0."""
        weights = self.assessor.scoring_weights
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01  # Allow small floating point differences
    
    def test_determine_quality_tier(self):
        """Test quality tier determination based on scores."""
        # Test brilliant moves
        assert self.assessor._determine_quality_tier(95.0) == MoveQualityTier.BRILLIANT
        assert self.assessor._determine_quality_tier(90.0) == MoveQualityTier.BRILLIANT
        
        # Test excellent moves
        assert self.assessor._determine_quality_tier(85.0) == MoveQualityTier.EXCELLENT
        assert self.assessor._determine_quality_tier(75.0) == MoveQualityTier.EXCELLENT
        
        # Test good moves
        assert self.assessor._determine_quality_tier(70.0) == MoveQualityTier.GOOD
        assert self.assessor._determine_quality_tier(50.0) == MoveQualityTier.GOOD
        
        # Test dubious moves
        assert self.assessor._determine_quality_tier(40.0) == MoveQualityTier.DUBIOUS
        assert self.assessor._determine_quality_tier(25.0) == MoveQualityTier.DUBIOUS
        
        # Test poor moves
        assert self.assessor._determine_quality_tier(20.0) == MoveQualityTier.POOR
        assert self.assessor._determine_quality_tier(0.0) == MoveQualityTier.POOR
    
    def test_calculate_overall_score(self):
        """Test overall score calculation with weighted components."""
        pattern_scores = {'blocking': 80.0, 'scoring': 70.0, 'floor_line': 60.0}
        strategic_value = 75.0
        tactical_value = 65.0
        risk_assessment = 50.0
        opportunity_value = 40.0
        
        score = self.assessor._calculate_overall_score(
            pattern_scores, strategic_value, tactical_value, 
            risk_assessment, opportunity_value
        )
        
        # Score should be between 0 and 100
        assert 0.0 <= score <= 100.0
        assert isinstance(score, float)
    
    def test_identify_best_moves(self):
        """Test identification of best moves from quality assessment."""
        # Create mock quality scores
        all_moves_quality = {
            'move_1': Mock(spec=MoveQualityScore, overall_score=85.0),
            'move_2': Mock(spec=MoveQualityScore, overall_score=92.0),
            'move_3': Mock(spec=MoveQualityScore, overall_score=78.0),
            'move_4': Mock(spec=MoveQualityScore, overall_score=65.0),
            'move_5': Mock(spec=MoveQualityScore, overall_score=45.0),
        }
        
        best_moves = self.assessor._identify_best_moves(all_moves_quality)
        
        # Should return top 5 moves in order
        assert len(best_moves) <= 5
        assert 'move_2' in best_moves  # Highest score
        assert 'move_1' in best_moves  # Second highest
        assert 'move_3' in best_moves  # Third highest
    
    def test_identify_pattern_connections(self):
        """Test pattern connection identification."""
        pattern_scores = {
            'blocking': 80.0,
            'scoring': 0.0,
            'floor_line': 60.0
        }
        strategic_value = 75.0
        tactical_value = 65.0
        
        connections = self.assessor._identify_pattern_connections(
            pattern_scores, strategic_value, tactical_value
        )
        
        # Should identify blocking and floor line connections
        assert "blocking pattern principles" in connections
        assert "floor line management" in connections
        assert "scoring opportunities" not in connections  # scoring score is 0
    
    def test_generate_educational_insights(self):
        """Test educational insight generation."""
        # Create mock quality scores with different tiers
        all_moves_quality = {
            'move_1': Mock(spec=MoveQualityScore, quality_tier=MoveQualityTier.BRILLIANT),
            'move_2': Mock(spec=MoveQualityScore, quality_tier=MoveQualityTier.GOOD),
            'move_3': Mock(spec=MoveQualityScore, quality_tier=MoveQualityTier.POOR),
            'move_4': Mock(spec=MoveQualityScore, quality_tier=MoveQualityTier.POOR),
            'move_5': Mock(spec=MoveQualityScore, quality_tier=MoveQualityTier.POOR),
        }
        
        insights = self.assessor._generate_educational_insights(all_moves_quality)
        
        # Should generate insights based on move distribution
        assert isinstance(insights, list)
        assert len(insights) > 0
    
    @patch('analysis_engine.move_quality.azul_move_quality_assessor.AzulPatternDetector')
    @patch('analysis_engine.move_quality.azul_move_quality_assessor.AzulScoringOptimizationDetector')
    @patch('analysis_engine.move_quality.azul_move_quality_assessor.AzulFloorLinePatternDetector')
    def test_evaluate_pattern_detection(self, mock_floor_line, mock_scoring, mock_pattern):
        """Test pattern detection evaluation."""
        # Mock pattern detection results
        mock_pattern.return_value.detect_patterns.return_value = Mock(
            patterns_detected=True,
            blocking_opportunities=[Mock(urgency_score=0.8)]
        )
        mock_scoring.return_value.detect_scoring_optimization.return_value = Mock(
            total_opportunities=2,
            wall_completion_opportunities=[Mock(bonus_value=5.0)],
            pattern_line_opportunities=[Mock(bonus_value=3.0)]
        )
        mock_floor_line.return_value.detect_floor_line_patterns.return_value = Mock(
            total_opportunities=1,
            risk_mitigation_opportunities=[Mock(urgency_score=0.7)],
            timing_optimization_opportunities=[Mock(urgency_score=0.6)]
        )
        
        move_data = {"move_type": "test", "data": "test_move"}
        pattern_scores = self.assessor._evaluate_pattern_detection(
            self.mock_state, 0, move_data
        )
        
        # Should return scores for all pattern types
        assert 'blocking' in pattern_scores
        assert 'scoring' in pattern_scores
        assert 'floor_line' in pattern_scores
        assert all(isinstance(score, float) for score in pattern_scores.values())
        assert all(0.0 <= score <= 100.0 for score in pattern_scores.values())


class TestMoveQualityScore:
    """Test the MoveQualityScore dataclass."""
    
    def test_move_quality_score_creation(self):
        """Test creating a MoveQualityScore instance."""
        score = MoveQualityScore(
            overall_score=85.0,
            quality_tier=MoveQualityTier.EXCELLENT,
            pattern_scores={'blocking': 80.0, 'scoring': 70.0},
            strategic_value=75.0,
            tactical_value=65.0,
            risk_assessment=50.0,
            opportunity_value=40.0,
            explanation="This is an excellent move",
            pattern_connections=["Applies blocking principles"],
            alternative_moves=[],
            confidence_score=0.8
        )
        
        assert score.overall_score == 85.0
        assert score.quality_tier == MoveQualityTier.EXCELLENT
        assert len(score.pattern_scores) == 2
        assert score.explanation == "This is an excellent move"
        assert score.confidence_score == 0.8


class TestMoveQualityAssessment:
    """Test the MoveQualityAssessment dataclass."""
    
    def test_move_quality_assessment_creation(self):
        """Test creating a MoveQualityAssessment instance."""
        assessment = MoveQualityAssessment(
            position_fen="test_fen",
            player_id=0,
            all_moves_quality={},
            best_moves=["move_1", "move_2"],
            alternative_moves=["move_3"],
            position_complexity=0.7,
            analysis_confidence=0.8,
            educational_insights=["This position is complex"]
        )
        
        assert assessment.position_fen == "test_fen"
        assert assessment.player_id == 0
        assert len(assessment.best_moves) == 2
        assert assessment.position_complexity == 0.7
        assert assessment.analysis_confidence == 0.8
        assert len(assessment.educational_insights) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 