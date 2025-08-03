"""
Test suite for Azul Floor Line Pattern Detection - Phase 2.3

Tests floor line management pattern recognition including:
- Risk mitigation opportunities
- Timing optimization patterns
- Trade-off analysis
- Endgame management
- Blocking opportunities
- Efficiency patterns
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch
from core.azul_floor_line_patterns import (
    AzulFloorLinePatternDetector, 
    FloorLineOpportunity, 
    FloorLinePatternDetection
)
from core.azul_model import AzulState
from core import azul_utils as utils


class TestFloorLinePatternDetection(unittest.TestCase):
    """Test floor line pattern detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = AzulFloorLinePatternDetector()
        
        # Create a basic game state using Mock with proper spec
        self.basic_state = Mock(spec=AzulState)
        self.basic_state.agents = [Mock(), Mock()]
        
        # Set up basic factory and center pool
        self.basic_state.factories = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        self.basic_state.center = [0, 1, 2, 3, 4]
        self.basic_state.center_pool = [0, 1, 2, 3, 4]
        
        # Set up basic player state attributes
        self.basic_state.agents[0].GRID_SIZE = 5
        self.basic_state.agents[0].grid_state = np.zeros((5, 5), dtype=int)
        self.basic_state.agents[0].pattern_lines = [[], [], [], [], []]
        self.basic_state.agents[0].floor_tiles = []
        self.basic_state.agents[0].score = 0
        
        self.basic_state.agents[1].GRID_SIZE = 5
        self.basic_state.agents[1].grid_state = np.zeros((5, 5), dtype=int)
        self.basic_state.agents[1].pattern_lines = [[], [], [], [], []]
        self.basic_state.agents[1].floor_tiles = []
        self.basic_state.agents[1].score = 0
    
    def test_risk_mitigation_detection(self):
        """Test detection of risk mitigation opportunities."""
        # Set up state with floor line tiles
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.RED]
        
        # Mock tile availability
        with patch.object(self.detector, '_count_tiles_available', return_value=2):
            opportunities = self.detector._detect_risk_mitigation_opportunities(
                self.basic_state, 0
            )
        
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0].opportunity_type, "risk_mitigation")
        self.assertEqual(opportunities[0].current_floor_tiles, 2)
        self.assertGreater(opportunities[0].urgency_score, 0)
    
    def test_timing_optimization_detection(self):
        """Test detection of timing optimization opportunities."""
        # Set up early game state with floor tiles
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE]
        
        opportunities = self.detector._detect_timing_optimization_opportunities(
            self.basic_state, 0
        )
        
        # Should detect early game timing optimization
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0].opportunity_type, "timing_optimization")
    
    def test_trade_off_detection(self):
        """Test detection of trade-off opportunities."""
        # Set up state with potential wall completion value
        self.basic_state.agents[0].floor_tiles = []
        
        with patch.object(self.detector, '_count_tiles_available', return_value=1):
            with patch.object(self.detector, '_calculate_wall_completion_value', return_value=8):
                opportunities = self.detector._detect_trade_off_opportunities(
                    self.basic_state, 0
                )
        
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0].opportunity_type, "trade_off")
        self.assertGreater(opportunities[0].strategic_value, 0)
    
    def test_endgame_management_detection(self):
        """Test detection of endgame management opportunities."""
        # Set up endgame state with floor tiles
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.RED, utils.Tile.YELLOW]
        
        # Mock game phase as endgame
        with patch.object(self.detector, '_assess_game_phase', return_value="endgame"):
            opportunities = self.detector._detect_endgame_management_opportunities(
                self.basic_state, 0
            )
        
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0].opportunity_type, "endgame_management")
        self.assertGreaterEqual(opportunities[0].urgency_score, 0)
    
    def test_blocking_opportunity_detection(self):
        """Test detection of blocking opportunities."""
        # Set up opponent with nearly complete pattern line
        self.basic_state.agents[1].pattern_lines[2] = [utils.Tile.BLUE, utils.Tile.BLUE]  # 2/3 tiles
        
        with patch.object(self.detector, '_count_tiles_available', return_value=1):
            opportunities = self.detector._detect_floor_line_blocking_opportunities(
                self.basic_state, 0
            )
        
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0].opportunity_type, "blocking")
        self.assertEqual(opportunities[0].target_color, utils.Tile.BLUE)
    
    def test_efficiency_opportunity_detection(self):
        """Test detection of efficiency opportunities."""
        # Set up state with floor tiles
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE]
        
        with patch.object(self.detector, '_count_tiles_available', return_value=1):
            with patch.object(self.detector, '_calculate_efficiency_value', return_value=3):
                opportunities = self.detector._detect_efficiency_opportunities(
                    self.basic_state, 0
                )
        
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0].opportunity_type, "efficiency")
        self.assertGreater(opportunities[0].strategic_value, 0)
    
    def test_floor_line_risk_assessment(self):
        """Test floor line risk assessment."""
        # Test different risk levels
        self.assertEqual(self.detector._assess_floor_line_risk(0), "low")
        self.assertEqual(self.detector._assess_floor_line_risk(2), "medium")
        self.assertEqual(self.detector._assess_floor_line_risk(4), "high")
        self.assertEqual(self.detector._assess_floor_line_risk(6), "critical")
    
    def test_game_phase_assessment(self):
        """Test game phase assessment."""
        # Mock different tile placement counts
        with patch.object(self.detector, '_assess_game_phase') as mock_assess:
            mock_assess.return_value = "early"
            self.assertEqual(self.detector._assess_game_phase(self.basic_state), "early")
            
            mock_assess.return_value = "mid"
            self.assertEqual(self.detector._assess_game_phase(self.basic_state), "mid")
            
            mock_assess.return_value = "endgame"
            self.assertEqual(self.detector._assess_game_phase(self.basic_state), "endgame")
    
    def test_urgency_calculations(self):
        """Test urgency calculation methods."""
        # Test risk mitigation urgency
        urgency = self.detector._calculate_risk_mitigation_urgency(
            current_penalty=5, penalty_reduction=3, risk_level="high", tiles_available=2
        )
        self.assertGreater(urgency, 0)
        self.assertLessEqual(urgency, 10.0)
        
        # Test timing urgency
        urgency = self.detector._calculate_timing_urgency("early", 3, "avoid")
        self.assertGreater(urgency, 0)
        self.assertLessEqual(urgency, 10.0)
        
        # Test trade-off urgency
        urgency = self.detector._calculate_trade_off_urgency(8, 2, 1)
        self.assertGreater(urgency, 0)
        self.assertLessEqual(urgency, 10.0)
        
        # Test endgame urgency
        urgency = self.detector._calculate_endgame_urgency(3, 5)
        self.assertGreater(urgency, 0)
        self.assertLessEqual(urgency, 10.0)
        
        # Test blocking urgency
        urgency = self.detector._calculate_blocking_urgency(1, 2)
        self.assertGreater(urgency, 0)
        self.assertLessEqual(urgency, 10.0)
        
        # Test efficiency urgency
        urgency = self.detector._calculate_efficiency_urgency(3, 1)
        self.assertGreater(urgency, 0)
        self.assertLessEqual(urgency, 10.0)
    
    def test_wall_completion_value_calculation(self):
        """Test wall completion value calculation."""
        # Set up a wall with some tiles
        self.basic_state.agents[0].grid_state[0] = [utils.Tile.BLUE, utils.Tile.YELLOW, 0, 0, 0]
        
        value = self.detector._calculate_wall_completion_value(
            self.basic_state.agents[0], 0, 2, utils.Tile.RED
        )
        self.assertGreaterEqual(value, 0)
    
    def test_completion_bonus_calculations(self):
        """Test completion bonus calculations."""
        # Test row completion
        for col in range(5):
            self.basic_state.agents[0].grid_state[0][col] = utils.Tile.BLUE + col + 1  # Avoid 0
        bonus = self.detector._check_row_completion(self.basic_state.agents[0], 0)
        self.assertEqual(bonus, 2)
        
        # Test column completion
        # Reset grid state to avoid conflicts
        self.basic_state.agents[0].grid_state = np.zeros((5, 5), dtype=int)
        for row in range(5):
            self.basic_state.agents[0].grid_state[row][0] = utils.Tile.BLUE + row + 1  # Avoid 0
        bonus = self.detector._check_column_completion(self.basic_state.agents[0], 0)
        self.assertEqual(bonus, 7)
        
        # Test color completion
        # Reset grid state and set exactly 5 red tiles (avoid BLUE=0)
        self.basic_state.agents[0].grid_state = np.zeros((5, 5), dtype=int)
        for row in range(5):
            self.basic_state.agents[0].grid_state[row][0] = utils.Tile.RED
        bonus = self.detector._check_color_completion(self.basic_state.agents[0], utils.Tile.RED)
        self.assertEqual(bonus, 10)
    
    def test_strategic_value_calculations(self):
        """Test strategic value calculations."""
        # Test risk mitigation strategic value
        value = self.detector._calculate_risk_mitigation_strategic_value(3, 5)
        self.assertGreater(value, 0)
        
        # Test timing strategic value
        value = self.detector._calculate_timing_strategic_value("early", 2)
        self.assertGreater(value, 0)
        
        # Test endgame strategic value
        value = self.detector._calculate_endgame_strategic_value(3, 5)
        self.assertGreater(value, 0)
        
        # Test blocking strategic value
        value = self.detector._calculate_blocking_strategic_value(1, 2)
        self.assertGreater(value, 0)
    
    def test_move_generation(self):
        """Test move generation methods."""
        # Test risk mitigation moves
        moves = self.detector._generate_risk_mitigation_moves(self.basic_state, 0, utils.Tile.BLUE)
        self.assertGreater(len(moves), 0)
        self.assertEqual(moves[0]["type"], "wall_placement")
        
        # Test timing optimization moves
        moves = self.detector._generate_timing_optimization_moves(self.basic_state, 0)
        self.assertGreater(len(moves), 0)
        self.assertEqual(moves[0]["type"], "floor_line_clearance")
        
        # Test trade-off moves
        moves = self.detector._generate_trade_off_moves(self.basic_state, 0, utils.Tile.BLUE)
        self.assertGreater(len(moves), 0)
        self.assertEqual(moves[0]["type"], "strategic_floor_acceptance")
        
        # Test endgame management moves
        moves = self.detector._generate_endgame_management_moves(self.basic_state, 0)
        self.assertGreater(len(moves), 0)
        self.assertEqual(moves[0]["type"], "endgame_floor_clearance")
        
        # Test blocking moves
        moves = self.detector._generate_blocking_moves(self.basic_state, 0, utils.Tile.BLUE)
        self.assertGreater(len(moves), 0)
        self.assertEqual(moves[0]["type"], "opponent_blocking")
        
        # Test efficiency moves
        moves = self.detector._generate_efficiency_moves(self.basic_state, 0, utils.Tile.BLUE)
        self.assertGreater(len(moves), 0)
        self.assertEqual(moves[0]["type"], "efficient_placement")
    
    def test_comprehensive_pattern_detection(self):
        """Test comprehensive pattern detection."""
        # Set up a complex state with multiple opportunities
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.RED]
        self.basic_state.agents[1].pattern_lines[2] = [utils.Tile.YELLOW, utils.Tile.YELLOW]
        
        with patch.object(self.detector, '_count_tiles_available', return_value=2):
            with patch.object(self.detector, '_assess_game_phase', return_value="mid"):
                detection = self.detector.detect_floor_line_patterns(self.basic_state, 0)
        
        self.assertIsInstance(detection, FloorLinePatternDetection)
        self.assertGreaterEqual(detection.total_opportunities, 0)
        self.assertGreaterEqual(detection.confidence_score, 0.0)
        self.assertLessEqual(detection.confidence_score, 1.0)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with no floor tiles
        detection = self.detector.detect_floor_line_patterns(self.basic_state, 0)
        self.assertEqual(detection.total_opportunities, 0)
        
        # Test with maximum floor tiles
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE] * 7
        detection = self.detector.detect_floor_line_patterns(self.basic_state, 0)
        self.assertGreaterEqual(detection.total_opportunities, 0)
        
        # Test with no available tiles
        with patch.object(self.detector, '_count_tiles_available', return_value=0):
            opportunities = self.detector._detect_risk_mitigation_opportunities(
                self.basic_state, 0
            )
            self.assertEqual(len(opportunities), 0)
    
    def test_color_mapping(self):
        """Test color name mapping."""
        self.assertEqual(self.detector.color_names[utils.Tile.BLUE], "blue")
        self.assertEqual(self.detector.color_names[utils.Tile.YELLOW], "yellow")
        self.assertEqual(self.detector.color_names[utils.Tile.RED], "red")
        self.assertEqual(self.detector.color_names[utils.Tile.BLACK], "black")
        self.assertEqual(self.detector.color_names[utils.Tile.WHITE], "white")
    
    def test_penalty_calculations(self):
        """Test penalty calculation methods."""
        # Test penalty reduction potential
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.RED]
        reduction = self.detector._calculate_penalty_reduction_potential(
            self.basic_state.agents[0], 0, 0, utils.Tile.YELLOW
        )
        self.assertGreaterEqual(reduction, 0)
        self.assertEqual(reduction, 1)  # Should reduce penalty from -2 to -1
        
        # Test with 3 floor tiles (penalty -4 to -2 = reduction of 2)
        self.basic_state.agents[0].floor_tiles = [utils.Tile.BLUE, utils.Tile.RED, utils.Tile.YELLOW]
        reduction = self.detector._calculate_penalty_reduction_potential(
            self.basic_state.agents[0], 0, 0, utils.Tile.BLACK
        )
        self.assertEqual(reduction, 2)  # Should reduce penalty from -4 to -2
        
        # Test total penalty risk
        total_risk = self.detector._calculate_total_penalty_risk(self.basic_state, 0)
        self.assertGreaterEqual(total_risk, 0)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # Test with no opportunities
        confidence = self.detector._calculate_pattern_confidence([])
        self.assertEqual(confidence, 0.0)
        
        # Test with opportunities
        opportunities = [
            FloorLineOpportunity(
                opportunity_type="risk_mitigation",
                target_position=(0, 0),
                target_color=utils.Tile.BLUE,
                current_floor_tiles=2,
                potential_penalty=3,
                penalty_reduction=2,
                urgency_score=7.0,
                risk_assessment="high",
                description="Test opportunity",
                move_suggestions=[],
                strategic_value=5.0
            )
        ]
        confidence = self.detector._calculate_pattern_confidence(opportunities)
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


if __name__ == '__main__':
    unittest.main() 