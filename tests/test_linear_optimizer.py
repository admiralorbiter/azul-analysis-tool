"""
Test suite for the Linear Programming Optimizer.

This module tests the AzulLinearOptimizer functionality including
scoring optimization, resource allocation, and wall completion optimization.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from analysis_engine.mathematical_optimization.linear_optimizer import (
    AzulLinearOptimizer, OptimizationObjective, OptimizationResult
)
from core.azul_model import AzulState
from core import azul_utils as utils


class TestAzulLinearOptimizer:
    """Test cases for the AzulLinearOptimizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = AzulLinearOptimizer()
        
        # Create a simple test state
        self.test_state = AzulState(2)  # 2-player game
        
        # Initialize factories with some tiles
        for factory in self.test_state.factories:
            factory.tiles = {utils.Tile.BLUE: 2, utils.Tile.RED: 1, utils.Tile.YELLOW: 1}
        
        # Initialize center pool
        self.test_state.centre_pool.tiles = {utils.Tile.WHITE: 1, utils.Tile.BLACK: 1}
    
    def test_optimizer_initialization(self):
        """Test that the optimizer initializes correctly."""
        assert self.optimizer.solver_name == 'PULP_CBC_CMD'
        assert self.optimizer.time_limit == 30
        assert self.optimizer.verbose is False
    
    def test_optimization_objective_enum(self):
        """Test that optimization objectives are properly defined."""
        objectives = [
            OptimizationObjective.MAXIMIZE_SCORING,
            OptimizationObjective.MINIMIZE_PENALTY,
            OptimizationObjective.BALANCE_SCORING_PENALTY,
            OptimizationObjective.MAXIMIZE_WALL_COMPLETION,
            OptimizationObjective.OPTIMIZE_RESOURCE_ALLOCATION
        ]
        
        for objective in objectives:
            assert isinstance(objective, OptimizationObjective)
            assert objective.value in [
                'maximize_scoring',
                'minimize_penalty',
                'balance_scoring_penalty',
                'maximize_wall_completion',
                'optimize_resource_allocation'
            ]
    
    @patch('analysis_engine.mathematical_optimization.linear_optimizer.pulp')
    def test_optimize_scoring_basic(self, mock_pulp):
        """Test basic scoring optimization functionality."""
        # Mock PuLP components
        mock_problem = Mock()
        mock_pulp.LpProblem.return_value = mock_problem
        mock_pulp.LpMaximize = 'maximize'
        mock_pulp.LpStatusOptimal = 'Optimal'
        mock_pulp.value.return_value = 15.0
        
        # Mock solver
        mock_solver = Mock()
        mock_pulp.PULP_CBC_CMD.return_value = mock_solver
        
        # Mock variables
        mock_var = Mock()
        mock_var.varValue = 0  # No moves selected
        mock_problem.__getitem__.return_value = mock_var
        
        # Test optimization
        result = self.optimizer.optimize_scoring(self.test_state, 0)
        
        # Verify result structure
        assert isinstance(result, OptimizationResult)
        assert result.objective_value == 15.0
        assert result.solver_status == 'Optimal'
        assert isinstance(result.optimal_moves, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.confidence_score, float)
    
    def test_optimize_scoring_error_handling(self):
        """Test that optimization handles errors gracefully."""
        # Test with invalid state
        with pytest.raises(Exception):
            self.optimizer.optimize_scoring(None, 0)
    
    def test_optimize_resource_allocation(self):
        """Test resource allocation optimization."""
        result = self.optimizer.optimize_resource_allocation(self.test_state, 0)
        
        assert isinstance(result, OptimizationResult)
        assert isinstance(result.optimal_moves, list)
        assert isinstance(result.recommendations, list)
    
    def test_optimize_wall_completion(self):
        """Test wall completion optimization."""
        result = self.optimizer.optimize_wall_completion(self.test_state, 0)
        
        assert isinstance(result, OptimizationResult)
        assert isinstance(result.optimal_moves, list)
        assert isinstance(result.recommendations, list)
    
    def test_get_tile_column(self):
        """Test tile column mapping functionality."""
        # Test blue tile mapping
        assert self.optimizer._get_tile_column(utils.Tile.BLUE, 0) == 0
        assert self.optimizer._get_tile_column(utils.Tile.BLUE, 1) == 1
        assert self.optimizer._get_tile_column(utils.Tile.BLUE, 2) == 2
        
        # Test white tile mapping
        assert self.optimizer._get_tile_column(utils.Tile.WHITE, 0) == 4
        assert self.optimizer._get_tile_column(utils.Tile.WHITE, 1) == 0
        
        # Test red tile mapping
        assert self.optimizer._get_tile_column(utils.Tile.RED, 0) == 2
        assert self.optimizer._get_tile_column(utils.Tile.RED, 1) == 3
    
    def test_calculate_row_completion_bonus(self):
        """Test row completion bonus calculation."""
        player = self.test_state.agents[0]
        
        # Test with no completion
        bonus = self.optimizer._calculate_row_completion_bonus(player, 0, 0, utils.Tile.BLUE)
        assert bonus == 0
        
        # Test with near completion (would need to set up state properly)
        # This is a basic test - in practice, you'd need to set up the grid state
    
    def test_calculate_column_completion_bonus(self):
        """Test column completion bonus calculation."""
        player = self.test_state.agents[0]
        
        # Test with no completion
        bonus = self.optimizer._calculate_column_completion_bonus(player, 0, 0, utils.Tile.BLUE)
        assert bonus == 0
    
    def test_calculate_set_completion_bonus(self):
        """Test set completion bonus calculation."""
        player = self.test_state.agents[0]
        
        # Test with no completion
        bonus = self.optimizer._calculate_set_completion_bonus(player, 0, 0, utils.Tile.BLUE)
        assert bonus == 0
    
    def test_parse_move_variable(self):
        """Test move variable parsing."""
        # Test factory move parsing
        factory_move = self.optimizer._parse_move_variable(
            "factory_0_line_2_tile_1", self.test_state, 0
        )
        assert factory_move is not None
        assert factory_move['move_type'] == 'factory_to_pattern_line'
        assert factory_move['factory_idx'] == 0
        assert factory_move['pattern_line'] == 2
        assert factory_move['tile_type'] == 1
        
        # Test center move parsing
        center_move = self.optimizer._parse_move_variable(
            "center_line_1_tile_2", self.test_state, 0
        )
        assert center_move is not None
        assert center_move['move_type'] == 'center_to_pattern_line'
        assert center_move['pattern_line'] == 1
        assert center_move['tile_type'] == 2
        
        # Test wall move parsing
        wall_move = self.optimizer._parse_move_variable(
            "wall_3_4_tile_0", self.test_state, 0
        )
        assert wall_move is not None
        assert wall_move['move_type'] == 'wall_placement'
        assert wall_move['row'] == 3
        assert wall_move['col'] == 4
        assert wall_move['tile_type'] == 0
        
        # Test invalid move parsing
        invalid_move = self.optimizer._parse_move_variable(
            "invalid_format", self.test_state, 0
        )
        assert invalid_move is None
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Mock problem and moves
        mock_problem = Mock()
        mock_problem.status = 'Optimal'
        
        # Test with no moves
        confidence = self.optimizer._calculate_confidence_score(mock_problem, [])
        assert confidence == 0.0
        
        # Test with some moves
        mock_moves = [{'move_type': 'factory_to_pattern_line'}]
        confidence = self.optimizer._calculate_confidence_score(mock_problem, mock_moves)
        assert 0.0 <= confidence <= 1.0
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Test with no moves
        recommendations = self.optimizer._generate_recommendations([], self.test_state, 0)
        assert len(recommendations) == 1
        assert "defensive play" in recommendations[0]
        
        # Test with factory moves
        factory_moves = [{'move_type': 'factory_to_pattern_line'}]
        recommendations = self.optimizer._generate_recommendations(factory_moves, self.test_state, 0)
        assert len(recommendations) > 0
        assert any("factory moves" in rec.lower() for rec in recommendations)
        
        # Test with multiple moves
        multiple_moves = [
            {'move_type': 'factory_to_pattern_line'},
            {'move_type': 'center_to_pattern_line'},
            {'move_type': 'wall_placement'}
        ]
        recommendations = self.optimizer._generate_recommendations(multiple_moves, self.test_state, 0)
        assert len(recommendations) > 0
        assert any("multiple high-value moves" in rec.lower() for rec in recommendations)


class TestOptimizationResult:
    """Test cases for the OptimizationResult dataclass."""
    
    def test_optimization_result_creation(self):
        """Test OptimizationResult creation and attributes."""
        result = OptimizationResult(
            objective_value=25.0,
            optimal_moves=[{'move_type': 'factory_to_pattern_line'}],
            constraint_violations=[],
            optimization_time=1.5,
            solver_status='Optimal',
            confidence_score=0.8,
            recommendations=['Focus on factory moves']
        )
        
        assert result.objective_value == 25.0
        assert len(result.optimal_moves) == 1
        assert result.optimal_moves[0]['move_type'] == 'factory_to_pattern_line'
        assert len(result.constraint_violations) == 0
        assert result.optimization_time == 1.5
        assert result.solver_status == 'Optimal'
        assert result.confidence_score == 0.8
        assert len(result.recommendations) == 1
        assert result.recommendations[0] == 'Focus on factory moves'


if __name__ == '__main__':
    pytest.main([__file__]) 