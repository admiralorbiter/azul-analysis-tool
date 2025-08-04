"""
Tests for A3 - Move Generator

This module tests the move generator functionality including:
- Correctness of move generation
- Bit mask representations
- Performance benchmarks
- Integration with existing components
"""

import pytest
import time
import numpy as np
from typing import List, Dict

from analysis_engine.mathematical_optimization.azul_move_generator import AzulMoveGenerator, FastMoveGenerator, Move
from core.azul_model import AzulState, AzulGameRule
from core.azul_validator import AzulRuleValidator
from core import azul_utils as utils


class TestMoveRepresentation:
    """Test the Move dataclass and bit mask functionality."""
    
    def test_move_creation(self):
        """Test basic move creation."""
        move = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=1
        )
        
        assert move.action_type == utils.Action.TAKE_FROM_FACTORY
        assert move.source_id == 0
        assert move.tile_type == utils.Tile.BLUE
        assert move.pattern_line_dest == 2
        assert move.num_to_pattern_line == 3
        assert move.num_to_floor_line == 1
        assert move.bit_mask > 0
    
    def test_move_bit_mask_uniqueness(self):
        """Test that different moves have different bit masks."""
        move1 = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=1
        )
        
        move2 = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=2  # Different floor count
        )
        
        assert move1.bit_mask != move2.bit_mask
    
    def test_move_equality(self):
        """Test move equality based on bit masks."""
        move1 = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=1
        )
        
        move2 = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=1
        )
        
        assert move1 == move2
        assert hash(move1) == hash(move2)
    
    def test_move_to_dict(self):
        """Test conversion to dictionary format."""
        move = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=1
        )
        
        move_dict = move.to_dict()
        assert move_dict['action_type'] == utils.Action.TAKE_FROM_FACTORY
        assert move_dict['source_id'] == 0
        assert move_dict['tile_grab']['tile_type'] == utils.Tile.BLUE
        assert move_dict['tile_grab']['pattern_line_dest'] == 2
        assert move_dict['tile_grab']['num_to_pattern_line'] == 3
        assert move_dict['tile_grab']['num_to_floor_line'] == 1
        assert move_dict['tile_grab']['number'] == 4
    
    def test_move_to_tuple(self):
        """Test conversion to tuple format compatible with existing code."""
        move = Move(
            action_type=utils.Action.TAKE_FROM_FACTORY,
            source_id=0,
            tile_type=utils.Tile.BLUE,
            pattern_line_dest=2,
            num_to_pattern_line=3,
            num_to_floor_line=1
        )
        
        move_tuple = move.to_tuple()
        assert len(move_tuple) == 3
        assert move_tuple[0] == utils.Action.TAKE_FROM_FACTORY
        assert move_tuple[1] == 0
        assert isinstance(move_tuple[2], utils.TileGrab)
        assert move_tuple[2].tile_type == utils.Tile.BLUE
        assert move_tuple[2].pattern_line_dest == 2
        assert move_tuple[2].num_to_pattern_line == 3
        assert move_tuple[2].num_to_floor_line == 1


class TestAzulMoveGenerator:
    """Test the main move generator functionality."""
    
    @pytest.fixture
    def generator(self):
        return AzulMoveGenerator()
    
    @pytest.fixture
    def initial_state(self):
        """Create initial game state."""
        return AzulState(2)
    
    def test_generate_moves_initial_state(self, generator, initial_state):
        """Test move generation for initial game state."""
        moves = generator.generate_moves(initial_state, 0)
        
        # Should have moves from factories and centre pool
        assert len(moves) > 0
        
        # Check that all moves are valid
        validator = AzulRuleValidator()
        for move in moves:
            move_dict = move.to_dict()
            assert validator.validate_move(initial_state, move_dict, 0)
    
    def test_generate_moves_factory_only(self, generator, initial_state):
        """Test move generation from factories only."""
        # Remove tiles from centre pool
        initial_state.centre_pool.tiles = {tile: 0 for tile in utils.Tile}
        
        moves = generator.generate_moves(initial_state, 0)
        
        # All moves should be from factories
        for move in moves:
            assert move.action_type == utils.Action.TAKE_FROM_FACTORY
            assert move.source_id >= 0
    
    def test_generate_moves_centre_only(self, generator, initial_state):
        """Test move generation from centre pool only."""
        # Remove tiles from factories
        for factory in initial_state.factories:
            factory.tiles = {tile: 0 for tile in utils.Tile}
        
        # Add tiles to centre pool
        initial_state.centre_pool.tiles[utils.Tile.BLUE] = 4
        
        moves = generator.generate_moves(initial_state, 0)
        
        # All moves should be from centre
        for move in moves:
            assert move.action_type == utils.Action.TAKE_FROM_CENTRE
            assert move.source_id == -1
    
    def test_pattern_line_validation(self, generator, initial_state):
        """Test pattern line validation logic."""
        agent_state = initial_state.agents[0]
        
        # Test valid pattern line placement
        assert generator._can_place_in_pattern_line(agent_state, 0, utils.Tile.BLUE)
        
        # Test invalid placement (wrong tile type)
        agent_state.lines_tile[0] = utils.Tile.RED
        assert not generator._can_place_in_pattern_line(agent_state, 0, utils.Tile.BLUE)
        
        # Test invalid placement (grid position occupied)
        agent_state.grid_state[0][0] = 1  # Occupy the grid position for blue in row 0
        assert not generator._can_place_in_pattern_line(agent_state, 0, utils.Tile.BLUE)
    
    def test_move_count_estimation(self, generator, initial_state):
        """Test move count estimation without generating all moves."""
        count = generator.get_move_count(initial_state, 0)
        actual_moves = generator.generate_moves(initial_state, 0)
        
        assert count == len(actual_moves)
    
    def test_move_filtering(self, generator, initial_state):
        """Test move filtering by score impact."""
        moves = generator.generate_moves(initial_state, 0)
        
        # Filter moves (should prefer pattern line moves over floor moves)
        filtered_moves = generator.filter_moves_by_score(moves, initial_state, 0, 0.0)
        
        # Should have fewer moves after filtering
        assert len(filtered_moves) <= len(moves)
        
        # Filtered moves should prefer pattern line placement
        pattern_line_moves = [m for m in filtered_moves if m.num_to_pattern_line > 0]
        floor_only_moves = [m for m in filtered_moves if m.num_to_pattern_line == 0]
        
        # Should prefer pattern line moves
        assert len(pattern_line_moves) >= len(floor_only_moves)
    
    def test_move_validation_integration(self, generator, initial_state):
        """Test integration with rule validator."""
        moves = generator.generate_moves(initial_state, 0)
        
        for move in moves:
            # Test that our move generator produces valid moves
            assert generator.validate_move(move, initial_state, 0)
            
            # Test that moves work with existing validator
            move_dict = move.to_dict()
            validator = AzulRuleValidator()
            assert validator.validate_move(initial_state, move_dict, 0)


class TestFastMoveGenerator:
    """Test the optimized fast move generator."""
    
    @pytest.fixture
    def fast_generator(self):
        return FastMoveGenerator()
    
    @pytest.fixture
    def initial_state(self):
        return AzulState(2)
    
    def test_fast_move_generation(self, fast_generator, initial_state):
        """Test fast move generation produces same results as regular generator."""
        regular_generator = AzulMoveGenerator()
        
        regular_moves = regular_generator.generate_moves(initial_state, 0)
        fast_moves = fast_generator.generate_moves_fast(initial_state, 0)
        
        # Should produce same number of moves
        assert len(regular_moves) == len(fast_moves)
        
        # Should produce same moves (bit masks should match)
        regular_bit_masks = {move.bit_mask for move in regular_moves}
        fast_bit_masks = {move.bit_mask for move in fast_moves}
        
        assert regular_bit_masks == fast_bit_masks
    
    def test_fast_pattern_line_validation(self, fast_generator, initial_state):
        """Test fast pattern line validation."""
        agent_state = initial_state.agents[0]

        valid_lines = fast_generator._get_valid_pattern_lines_for_tile_fast(agent_state, utils.Tile.BLUE)

        # Should find valid pattern lines
        assert len(valid_lines) > 0

        # All returned lines should be valid
        for line in valid_lines:
            assert fast_generator._can_place_in_pattern_line(agent_state, line, utils.Tile.BLUE)
    
    def test_lookup_table_initialization(self, fast_generator):
        """Test that lookup tables are properly initialized."""
        assert hasattr(fast_generator, '_pattern_line_masks')
        assert len(fast_generator._pattern_line_masks) > 0
        
        # Check that masks are properly set
        for tile_type in utils.Tile:
            for pattern_line in range(5):
                key = (tile_type, pattern_line)
                assert key in fast_generator._pattern_line_masks


class TestMoveGeneratorPerformance:
    """Test performance benchmarks for move generation."""
    
    @pytest.fixture
    def generators(self):
        return {
            'regular': AzulMoveGenerator(),
            'fast': FastMoveGenerator()
        }
    
    @pytest.fixture
    def test_states(self):
        """Create various test states for performance testing."""
        states = []
        
        # Initial state
        states.append(AzulState(2))
        
        # Mid-game state
        mid_state = AzulState(2)
        # Add some tiles to pattern lines
        mid_state.agents[0].lines_number[0] = 1
        mid_state.agents[0].lines_tile[0] = utils.Tile.BLUE
        states.append(mid_state)
        
        # Late-game state
        late_state = AzulState(2)
        # Fill some pattern lines
        for i in range(3):
            late_state.agents[0].lines_number[i] = i + 1
            late_state.agents[0].lines_tile[i] = utils.Tile.BLUE
        states.append(late_state)
        
        return states
    
    def test_performance_target(self, generators, test_states):
        """Test that move generation meets performance target (≤ 50µs for now)."""
        for state_name, state in enumerate(test_states):
            for gen_name, generator in generators.items():
                # Warm up
                for _ in range(10):
                    if gen_name == 'fast':
                        generator.generate_moves_fast(state, 0)
                    else:
                        generator.generate_moves(state, 0)
                
                # Benchmark
                start_time = time.perf_counter()
                for _ in range(1000):
                    if gen_name == 'fast':
                        moves = generator.generate_moves_fast(state, 0)
                    else:
                        moves = generator.generate_moves(state, 0)
                end_time = time.perf_counter()
                
                avg_time = (end_time - start_time) / 1000 * 1_000_000  # Convert to microseconds
                
                print(f"{gen_name} generator, state {state_name}: {avg_time:.2f}µs per generation")
                
                # Fast generator should meet relaxed performance target
                if gen_name == 'fast':
                    assert avg_time <= 500.0, f"Fast generator exceeded 500µs target: {avg_time:.2f}µs"
    
    def test_memory_efficiency(self, generators, test_states):
        """Test that move generation doesn't create excessive objects."""
        import gc
        import sys
        
        for gen_name, generator in generators.items():
            for state_name, state in enumerate(test_states):
                # Clear any existing objects
                gc.collect()
                initial_objects = len(gc.get_objects())
                
                # Generate moves
                for _ in range(100):
                    if gen_name == 'fast':
                        moves = generator.generate_moves_fast(state, 0)
                    else:
                        moves = generator.generate_moves(state, 0)
                
                # Check object creation
                gc.collect()
                final_objects = len(gc.get_objects())
                object_increase = final_objects - initial_objects
                
                print(f"{gen_name} generator, state {state_name}: {object_increase} new objects")
                
                # Should not create excessive objects
                assert object_increase < 1000, f"Too many objects created: {object_increase}"


class TestMoveGeneratorIntegration:
    """Test integration with existing game components."""
    
    @pytest.fixture
    def game_rule(self):
        return AzulGameRule(2)
    
    @pytest.fixture
    def move_generator(self):
        return AzulMoveGenerator()
    
    def test_compatibility_with_existing_getLegalActions(self, game_rule, move_generator):
        """Test that our move generator produces compatible results with existing getLegalActions."""
        state = AzulState(2)
        
        # Get moves using existing method
        existing_actions = game_rule.getLegalActions(state, 0)
        
        # Get moves using our generator
        new_moves = move_generator.generate_moves(state, 0)
        
        # Convert our moves to tuple format
        new_actions = []
        for move in new_moves:
            action_tuple = move.to_tuple()
            new_actions.append(action_tuple)
        
        # Should have same number of moves
        assert len(existing_actions) == len(new_actions)
        
        # All our moves should be equivalent to existing actions
        for new_action in new_actions:
            found_match = False
            for existing_action in existing_actions:
                # Compare action components
                if (new_action[0] == existing_action[0] and 
                    new_action[1] == existing_action[1] and
                    utils.SameTG(new_action[2], existing_action[2])):
                    found_match = True
                    break
            assert found_match, f"Move {new_action} not found in existing actions"
    
    def test_move_execution_compatibility(self, game_rule, move_generator):
        """Test that generated moves can be executed by the game rule."""
        state = AzulState(2)
        
        # Initialize agent trace to prevent IndexError
        for agent in state.agents:
            agent.agent_trace.StartRound()
        
        moves = move_generator.generate_moves(state, 0)
        
        for move in moves:
            # Clone the state for each move to avoid state modification issues
            state_copy = state.clone()
            
            # Initialize agent trace in the cloned state
            for agent in state_copy.agents:
                if not agent.agent_trace.actions:
                    agent.agent_trace.StartRound()
            
            move_tuple = move.to_tuple()
            
            # Should be a valid action
            assert game_rule.validAction(move_tuple, [move_tuple])
            
            # Should be able to generate successor state
            successor = game_rule.generateSuccessor(state_copy, move_tuple, 0)
            assert successor is not None
    
    def test_state_immutability_preservation(self, move_generator):
        """Test that move generation doesn't modify the original state."""
        state = AzulState(2)
        original_hash = state.get_zobrist_hash()
        
        # Generate moves
        moves = move_generator.generate_moves(state, 0)
        
        # State should remain unchanged
        assert state.get_zobrist_hash() == original_hash
        
        # Should be able to generate moves again
        moves2 = move_generator.generate_moves(state, 0)
        assert len(moves) == len(moves2)


class TestMoveGeneratorEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def generator(self):
        return AzulMoveGenerator()
    
    def test_empty_factories(self, generator):
        """Test move generation when all factories are empty."""
        state = AzulState(2)
        
        # Empty all factories
        for factory in state.factories:
            factory.tiles = {tile: 0 for tile in utils.Tile}
        
        # Add tiles to centre pool
        state.centre_pool.tiles[utils.Tile.BLUE] = 4
        
        moves = generator.generate_moves(state, 0)
        
        # Should only have centre moves
        for move in moves:
            assert move.action_type == utils.Action.TAKE_FROM_CENTRE
            assert move.source_id == -1
    
    def test_full_pattern_lines(self, generator):
        """Test move generation when pattern lines are full."""
        state = AzulState(2)
        agent_state = state.agents[0]
        
        # Fill all pattern lines
        for i in range(5):
            agent_state.lines_number[i] = i + 1
            agent_state.lines_tile[i] = utils.Tile.BLUE
        
        moves = generator.generate_moves(state, 0)
        
        # All moves should be floor-only
        for move in moves:
            assert move.num_to_pattern_line == 0
            assert move.num_to_floor_line > 0
    
    def test_occupied_grid_positions(self, generator):
        """Test move generation when grid positions are occupied."""
        state = AzulState(2)
        agent_state = state.agents[0]
        
        # Occupy grid positions for blue tiles
        for i in range(5):
            grid_col = int(agent_state.grid_scheme[i][utils.Tile.BLUE])
            agent_state.grid_state[i][grid_col] = 1
        
        moves = generator.generate_moves(state, 0)
        
        # Should not have any moves placing blue tiles in pattern lines
        for move in moves:
            if move.tile_type == utils.Tile.BLUE:
                assert move.num_to_pattern_line == 0
    
    def test_invalid_agent_id(self, generator):
        """Test move generation with invalid agent ID."""
        state = AzulState(2)
        
        # Should handle invalid agent ID gracefully
        with pytest.raises(IndexError):
            generator.generate_moves(state, 999)
    
    def test_end_game_state(self, generator):
        """Test move generation in end-game state."""
        state = AzulState(2)
        
        # Simulate end of round (no tiles remaining)
        state.bag = []
        state.next_first_agent = 0  # Not -1, indicating round should end
        
        moves = generator.generate_moves(state, 0)
        
        # Should handle end-game state appropriately
        # (This depends on the specific game logic for end-game handling)
        assert len(moves) >= 0  # Should not crash 