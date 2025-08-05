import pytest
import numpy as np
from unittest.mock import Mock, patch
import time

from analysis_engine.mathematical_optimization.dynamic_optimizer import (
    AzulDynamicOptimizer, EndgamePhase, MultiTurnPlan, EndgameState
)
from core.azul_model import AzulState
from core import azul_utils as utils


class TestAzulDynamicOptimizer:
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = AzulDynamicOptimizer(max_depth=3, cache_size=1000)
        self.test_state = AzulState(2)
        
        # Set up a basic test state
        self.test_state.round = 5
        self.test_state.current_player = 0
        
        # Add some tiles to factories
        self.test_state.factories = [
            [1, 1, 2, 3],  # Factory 0
            [2, 3, 4, 5],  # Factory 1
            [1, 2, 3, 4],  # Factory 2
            [],             # Factory 3
            []              # Factory 4
        ]
        
        # Set up player states
        self.test_state.players[0].score = 25
        self.test_state.players[1].score = 20
        
        # Add some tiles to pattern lines
        self.test_state.players[0].pattern_lines[0] = [1, 2]  # 2 tiles in row 0
        self.test_state.players[0].pattern_lines[1] = [3]     # 1 tile in row 1
        
        # Add some tiles to floor line
        self.test_state.players[0].floor_line = [1, 2]
        
        # Add some tiles to wall
        self.test_state.players[0].wall[0][0] = 1  # Blue tile in top-left
        self.test_state.players[0].wall[1][1] = 2  # Yellow tile in second row, second column
    
    def test_optimizer_initialization(self):
        """Test dynamic optimizer initialization."""
        optimizer = AzulDynamicOptimizer(max_depth=5, cache_size=5000)
        
        assert optimizer.max_depth == 5
        assert optimizer.cache_size == 5000
        assert len(optimizer.state_cache) == 0
        assert optimizer.linear_optimizer is not None
        assert len(optimizer.endgame_weights) == 5
        assert len(optimizer.planning_params) == 3
    
    def test_endgame_phase_enum(self):
        """Test EndgamePhase enum values."""
        assert EndgamePhase.EARLY_GAME.value == "early_game"
        assert EndgamePhase.MID_GAME.value == "mid_game"
        assert EndgamePhase.LATE_GAME.value == "late_game"
        assert EndgamePhase.ENDGAME.value == "endgame"
    
    def test_determine_game_phase(self):
        """Test game phase determination."""
        # Test early game
        self.test_state.round = 2
        phase = self.optimizer._determine_game_phase(self.test_state)
        assert phase == EndgamePhase.EARLY_GAME
        
        # Test mid game
        self.test_state.round = 6
        phase = self.optimizer._determine_game_phase(self.test_state)
        assert phase == EndgamePhase.MID_GAME
        
        # Test late game
        self.test_state.round = 9
        phase = self.optimizer._determine_game_phase(self.test_state)
        assert phase == EndgamePhase.LATE_GAME
        
        # Test endgame
        self.test_state.round = 12
        phase = self.optimizer._determine_game_phase(self.test_state)
        assert phase == EndgamePhase.ENDGAME
    
    def test_calculate_wall_completion_score(self):
        """Test wall completion score calculation."""
        score = self.optimizer._calculate_wall_completion_score(self.test_state, 0)
        
        # Should have 2 tiles placed, so completion percentage = 2/25 = 0.08
        # No completed rows, columns, or sets
        expected_score = 0.08 * 50.0  # Only completion percentage contribution
        assert score == expected_score
        
        # Test with more completed tiles
        self.test_state.players[0].wall[0][1] = 2
        self.test_state.players[0].wall[0][2] = 3
        self.test_state.players[0].wall[0][3] = 4
        self.test_state.players[0].wall[0][4] = 5  # Complete first row
        
        score = self.optimizer._calculate_wall_completion_score(self.test_state, 0)
        assert score > expected_score  # Should be higher with completed row
    
    def test_calculate_floor_line_penalty(self):
        """Test floor line penalty calculation."""
        penalty = self.optimizer._calculate_floor_line_penalty(self.test_state, 0)
        
        # Floor line has [1, 2], so penalty = 1 + 2 = 3
        assert penalty == 3
        
        # Test with more floor line tiles
        self.test_state.players[0].floor_line = [1, 2, 3, 4]
        penalty = self.optimizer._calculate_floor_line_penalty(self.test_state, 0)
        assert penalty == 10  # 1 + 2 + 3 + 4
    
    def test_calculate_pattern_line_efficiency(self):
        """Test pattern line efficiency calculation."""
        efficiency = self.optimizer._calculate_pattern_line_efficiency(self.test_state, 0)
        
        # Row 0: 2 tiles, max capacity 1, efficiency = 2/1 = 2.0 (capped at 1.0)
        # Row 1: 1 tile, max capacity 2, efficiency = 1/2 = 0.5
        # Total efficiency = (1.0 + 0.5) / 5 = 0.3
        expected_efficiency = (1.0 + 0.5) / 5.0
        assert abs(efficiency - expected_efficiency) < 0.01
    
    def test_calculate_factory_control(self):
        """Test factory control calculation."""
        control = self.optimizer._calculate_factory_control(self.test_state, 0)
        
        # Available tiles: [1,1,2,3,2,3,4,5,1,2,3,4]
        # Unique tiles: 5 colors, total tiles: 12
        # Diversity score: 5/5 = 1.0
        # Quantity score: 12/20 = 0.6
        # Expected: (1.0 + 0.6) / 2 = 0.8
        expected_control = (1.0 + 0.6) / 2.0
        assert abs(control - expected_control) < 0.01
    
    def test_calculate_opponent_blocking_potential(self):
        """Test opponent blocking potential calculation."""
        blocking = self.optimizer._calculate_opponent_blocking_potential(self.test_state, 0)
        
        # Player 1 has no pattern lines, so blocking should be 0
        assert blocking == 0.0
        
        # Add some pattern lines to opponent
        self.test_state.players[1].pattern_lines[0] = [1, 2]
        self.test_state.players[1].pattern_lines[2] = [3]
        
        blocking = self.optimizer._calculate_opponent_blocking_potential(self.test_state, 0)
        # 2 tiles in row 0 + 1 tile in row 2 = 3 tiles * 0.1 = 0.3
        assert abs(blocking - 0.3) < 0.01
    
    def test_calculate_endgame_confidence(self):
        """Test endgame confidence calculation."""
        confidence = self.optimizer._calculate_endgame_confidence(self.test_state, 0)
        
        # Mid game (round 5) has base confidence 0.5
        # Wall completion bonus should be small
        assert 0.5 <= confidence <= 0.7
    
    def test_evaluate_endgame(self):
        """Test endgame evaluation."""
        evaluation = self.optimizer.evaluate_endgame(self.test_state, 0)
        
        assert 'endgame_score' in evaluation
        assert 'game_phase' in evaluation
        assert 'wall_completion' in evaluation
        assert 'floor_line_penalty' in evaluation
        assert 'pattern_line_efficiency' in evaluation
        assert 'factory_control' in evaluation
        assert 'opponent_blocking_potential' in evaluation
        assert 'evaluation_time' in evaluation
        assert 'confidence' in evaluation
        
        assert evaluation['game_phase'] == 'mid_game'
        assert evaluation['evaluation_time'] > 0
        assert 0 <= evaluation['confidence'] <= 1
    
    def test_generate_possible_moves(self):
        """Test possible move generation."""
        moves = self.optimizer._generate_possible_moves(self.test_state, 0)
        
        # Should generate moves for each factory with tiles
        assert len(moves) > 0
        
        # Check move structure
        for move in moves:
            assert 'type' in move
            assert 'factory_idx' in move
            assert 'color' in move
            assert 'player_id' in move
            
            if move['type'] == 'factory_to_pattern':
                assert 'pattern_line_idx' in move
    
    def test_apply_move(self):
        """Test move application."""
        # Test factory to pattern line move
        move = {
            'type': 'factory_to_pattern',
            'factory_idx': 0,
            'color': 1,
            'pattern_line_idx': 0,
            'player_id': 0
        }
        
        new_state = self.optimizer._apply_move(self.test_state, move, 0)
        assert new_state is not None
        
        # Check that tiles were moved correctly
        # Factory 0 had [1,1,2,3], should now have [2,3]
        assert new_state.factories[0] == [2, 3]
        
        # Pattern line 0 should have additional tiles
        assert len(new_state.players[0].pattern_lines[0]) > 2
    
    def test_evaluate_move_sequence(self):
        """Test move sequence evaluation."""
        sequence = [
            {
                'type': 'factory_to_pattern',
                'factory_idx': 0,
                'color': 1,
                'pattern_line_idx': 0,
                'player_id': 0
            }
        ]
        
        score, confidence, risk = self.optimizer._evaluate_move_sequence(
            sequence, self.test_state, 0
        )
        
        assert isinstance(score, float)
        assert isinstance(confidence, float)
        assert isinstance(risk, float)
        assert 0 <= confidence <= 1
        assert 0 <= risk <= 1
    
    def test_plan_optimal_sequence(self):
        """Test multi-turn planning."""
        plan = self.optimizer.plan_optimal_sequence(self.test_state, 0, turns_ahead=2)
        
        assert isinstance(plan, MultiTurnPlan)
        assert isinstance(plan.total_expected_score, float)
        assert isinstance(plan.move_sequence, list)
        assert isinstance(plan.confidence_score, float)
        assert isinstance(plan.risk_assessment, dict)
        assert isinstance(plan.alternative_plans, list)
        assert isinstance(plan.endgame_evaluation, dict)
        
        assert 0 <= plan.confidence_score <= 1
        assert 'overall_risk' in plan.risk_assessment
    
    def test_calculate_sequence_risk(self):
        """Test sequence risk calculation."""
        sequence = [
            {'type': 'factory_to_pattern', 'factory_idx': 0, 'color': 1, 'pattern_line_idx': 0, 'player_id': 0},
            {'type': 'factory_to_floor', 'factory_idx': 1, 'color': 2, 'player_id': 0}
        ]
        
        risk = self.optimizer._calculate_sequence_risk(sequence, self.test_state, 0)
        
        # Risk should be > 0 due to sequence length and floor move
        assert risk > 0
        assert risk <= 1
    
    def test_calculate_plan_confidence(self):
        """Test plan confidence calculation."""
        plans = [
            {'confidence': 0.8, 'score': 50, 'risk': 0.2},
            {'confidence': 0.6, 'score': 40, 'risk': 0.3},
            {'confidence': 0.4, 'score': 30, 'risk': 0.4}
        ]
        
        confidence = self.optimizer._calculate_plan_confidence(plans)
        
        # Should be weighted average of confidences
        assert 0 < confidence < 1
    
    def test_calculate_plan_risk(self):
        """Test plan risk calculation."""
        plans = [
            {'confidence': 0.8, 'score': 50, 'risk': 0.2},
            {'confidence': 0.6, 'score': 40, 'risk': 0.3},
            {'confidence': 0.4, 'score': 30, 'risk': 0.4}
        ]
        
        risk = self.optimizer._calculate_plan_risk(plans)
        
        # Should be average of risks
        expected_risk = (0.2 + 0.3 + 0.4) / 3
        assert abs(risk - expected_risk) < 0.01
    
    def test_calculate_execution_risk(self):
        """Test execution risk calculation."""
        plan = {
            'sequence': [
                {'type': 'factory_to_pattern', 'factory_idx': 0, 'color': 1, 'pattern_line_idx': 0, 'player_id': 0},
                {'type': 'factory_to_pattern', 'factory_idx': 1, 'color': 2, 'pattern_line_idx': 1, 'player_id': 0}
            ]
        }
        
        risk = self.optimizer._calculate_execution_risk(plan)
        
        # Should be based on sequence length
        assert risk > 0
        assert risk <= 1
    
    def test_calculate_opponent_interference_risk(self):
        """Test opponent interference risk calculation."""
        risk = self.optimizer._calculate_opponent_interference_risk(self.test_state, 0)
        
        # Should be 0 with no opponent pattern lines
        assert risk == 0.0
        
        # Add opponent pattern lines
        self.test_state.players[1].pattern_lines[0] = [1, 2]
        risk = self.optimizer._calculate_opponent_interference_risk(self.test_state, 0)
        
        # Should be > 0 with opponent pattern lines
        assert risk > 0
        assert risk <= 1
    
    def test_calculate_resource_scarcity_risk(self):
        """Test resource scarcity risk calculation."""
        risk = self.optimizer._calculate_resource_scarcity_risk(self.test_state, 0)
        
        # Should be low with many tiles available
        assert 0 <= risk <= 1
        
        # Test with no tiles
        self.test_state.factories = [[] for _ in range(5)]
        risk = self.optimizer._calculate_resource_scarcity_risk(self.test_state, 0)
        
        # Should be high with no tiles
        assert risk == 1.0
    
    def test_error_handling(self):
        """Test error handling in dynamic optimizer."""
        # Test with invalid state
        with pytest.raises(Exception):
            self.optimizer.evaluate_endgame(None, 0)
        
        # Test with invalid player ID
        with pytest.raises(Exception):
            self.optimizer.evaluate_endgame(self.test_state, 999)
    
    def test_performance_characteristics(self):
        """Test performance characteristics."""
        start_time = time.time()
        evaluation = self.optimizer.evaluate_endgame(self.test_state, 0)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 1.0
        
        # Evaluation time should be recorded
        assert evaluation['evaluation_time'] > 0
        assert evaluation['evaluation_time'] < 1.0


class TestEndgameState:
    def test_endgame_state_creation(self):
        """Test EndgameState dataclass creation."""
        state = EndgameState(
            state_hash="test_hash",
            player_id=0,
            depth=3,
            score=25.5,
            moves_remaining=5,
            wall_completion=60.0,
            floor_line_penalty=3,
            pattern_line_efficiency=0.7,
            factory_control=0.8,
            opponent_blocking_potential=0.2
        )
        
        assert state.state_hash == "test_hash"
        assert state.player_id == 0
        assert state.depth == 3
        assert state.score == 25.5
        assert state.moves_remaining == 5
        assert state.wall_completion == 60.0
        assert state.floor_line_penalty == 3
        assert state.pattern_line_efficiency == 0.7
        assert state.factory_control == 0.8
        assert state.opponent_blocking_potential == 0.2


class TestMultiTurnPlan:
    def test_multi_turn_plan_creation(self):
        """Test MultiTurnPlan dataclass creation."""
        plan = MultiTurnPlan(
            total_expected_score=45.0,
            move_sequence=[{'type': 'factory_to_pattern', 'factory_idx': 0, 'color': 1, 'pattern_line_idx': 0, 'player_id': 0}],
            confidence_score=0.8,
            risk_assessment={'overall_risk': 0.3, 'execution_risk': 0.2},
            alternative_plans=[{'sequence': [], 'score': 40.0, 'confidence': 0.7, 'risk': 0.4}],
            endgame_evaluation={'endgame_score': 45.0, 'confidence': 0.8}
        )
        
        assert plan.total_expected_score == 45.0
        assert len(plan.move_sequence) == 1
        assert plan.confidence_score == 0.8
        assert 'overall_risk' in plan.risk_assessment
        assert len(plan.alternative_plans) == 1
        assert 'endgame_score' in plan.endgame_evaluation 