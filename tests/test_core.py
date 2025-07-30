"""
Basic unit tests for the Azul core engine.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.azul_model import AzulState, AzulGameRule
from core.azul_utils import Tile, Action, TileGrab, AgentTrace


class TestTileEnum:
    """Test the Tile enumeration."""
    
    def test_tile_values(self):
        """Test that tile enum has correct values."""
        assert Tile.BLUE == 0
        assert Tile.YELLOW == 1
        assert Tile.RED == 2
        assert Tile.BLACK == 3
        assert Tile.WHITE == 4
    
    def test_tile_count(self):
        """Test that there are exactly 5 tile types."""
        assert len(Tile) == 5


class TestActionEnum:
    """Test the Action enumeration."""
    
    def test_action_values(self):
        """Test that action enum has correct values."""
        assert Action.TAKE_FROM_FACTORY == 1
        assert Action.TAKE_FROM_CENTRE == 2
    
    def test_action_count(self):
        """Test that there are exactly 2 action types."""
        assert len(Action) == 2


class TestTileGrab:
    """Test the TileGrab class."""
    
    def test_initialization(self):
        """Test TileGrab initialization."""
        tg = TileGrab()
        assert tg.tile_type == -1
        assert tg.number == 0
        assert tg.pattern_line_dest == -1
        assert tg.num_to_pattern_line == 0
        assert tg.num_to_floor_line == 0


class TestAgentTrace:
    """Test the AgentTrace class."""
    
    def test_initialization(self):
        """Test AgentTrace initialization."""
        trace = AgentTrace(0)
        assert trace.id == 0
        assert trace.actions == []
        assert trace.round_scores == []
        assert trace.bonuses == 0
    
    def test_start_round(self):
        """Test starting a new round."""
        trace = AgentTrace(1)
        trace.StartRound()
        assert len(trace.actions) == 1
        assert len(trace.round_scores) == 1
        assert trace.actions[0] == []
        assert trace.round_scores[0] == 0


class TestAzulState:
    """Test the AzulState class."""
    
    def test_initialization_2_players(self):
        """Test AzulState initialization with 2 players."""
        state = AzulState(2)
        assert len(state.agents) == 2
        assert len(state.factories) == 5  # 2 players = 5 factories
        assert state.centre_pool is not None
        assert not state.first_agent_taken
        assert state.next_first_agent == -1
    
    def test_initialization_3_players(self):
        """Test AzulState initialization with 3 players."""
        state = AzulState(3)
        assert len(state.agents) == 3
        assert len(state.factories) == 7  # 3 players = 7 factories
    
    def test_initialization_4_players(self):
        """Test AzulState initialization with 4 players."""
        state = AzulState(4)
        assert len(state.agents) == 4
        assert len(state.factories) == 9  # 4 players = 9 factories
    
    def test_tile_bag_initialization(self):
        """Test that the tile bag is properly initialized."""
        state = AzulState(2)
        # The bag starts with 100 tiles but some are used for factory initialization
        # 5 factories × 4 tiles per factory = 20 tiles used
        # So we should have 100 - 20 = 80 tiles remaining
        assert len(state.bag) == 80
        
        # Total tiles across bag, factories, and used bag should be 100
        total_tiles = len(state.bag) + len(state.bag_used)
        for factory in state.factories:
            total_tiles += factory.total
        assert total_tiles == 100
    
    def test_tiles_remaining(self):
        """Test the TilesRemaining method."""
        state = AzulState(2)
        
        # Initially, factories should have tiles
        # (This might be False if factories start empty)
        # Let's initialize a factory to test
        state.InitialiseFactory(state.factories[0])
        if state.factories[0].total > 0:
            assert state.TilesRemaining()


class TestAzulGameRule:
    """Test the AzulGameRule class."""
    
    def test_initialization(self):
        """Test AzulGameRule initialization."""
        rule = AzulGameRule(2)
        assert rule.num_of_agent == 2
        assert rule.private_information is None
        assert rule.current_agent_index == 0
    
    def test_initial_game_state(self):
        """Test initial game state creation."""
        rule = AzulGameRule(2)
        state = rule.initialGameState()
        assert isinstance(state, AzulState)
        assert len(state.agents) == 2
        assert rule.current_agent_index == 2  # Should be set to num_of_agent
    
    def test_game_ends_initially_false(self):
        """Test that game doesn't end at the start."""
        rule = AzulGameRule(2)
        rule.current_game_state = rule.initialGameState()
        assert not rule.gameEnds()


class TestZobristHashing:
    """Test the Zobrist hashing functionality."""
    
    def test_zobrist_initialization(self):
        """Test that Zobrist tables are properly initialized."""
        from core.azul_model import AzulState
        
        # Initialize tables
        AzulState._initialize_zobrist_tables()
        
        # Check that tables exist and have correct shapes
        assert AzulState._ZOBRIST_TABLES is not None
        assert 'grid' in AzulState._ZOBRIST_TABLES
        assert 'floor' in AzulState._ZOBRIST_TABLES
        assert 'pattern' in AzulState._ZOBRIST_TABLES
        assert 'factory' in AzulState._ZOBRIST_TABLES
        assert 'center' in AzulState._ZOBRIST_TABLES
        assert 'first_player' in AzulState._ZOBRIST_TABLES
        assert 'bag' in AzulState._ZOBRIST_TABLES
        
        # Check shapes
        assert AzulState._ZOBRIST_TABLES['grid'].shape == (4, 5, 5, 5)
        assert AzulState._ZOBRIST_TABLES['floor'].shape == (4, 7, 5)
        assert AzulState._ZOBRIST_TABLES['pattern'].shape == (4, 5, 5)
        assert AzulState._ZOBRIST_TABLES['factory'].shape == (9, 5)
        assert AzulState._ZOBRIST_TABLES['center'].shape == (5,)
        assert AzulState._ZOBRIST_TABLES['first_player'].shape == (4,)
        assert AzulState._ZOBRIST_TABLES['bag'].shape == (5,)
    
    def test_zobrist_hash_consistency(self):
        """Test that identical states produce identical hashes."""
        from core.azul_model import AzulState
        
        # Create two identical states
        state1 = AzulState(2)
        state2 = AzulState(2)
        
        # Set same random seed for both
        import random
        random.seed(42)
        state1 = AzulState(2)
        random.seed(42)
        state2 = AzulState(2)
        
        # Get hashes
        hash1 = state1.get_zobrist_hash()
        hash2 = state2.get_zobrist_hash()
        
        # Should be identical
        assert hash1 == hash2
    
    def test_zobrist_hash_uniqueness(self):
        """Test that different states produce different hashes."""
        from core.azul_model import AzulState
        
        # Create two states
        state1 = AzulState(2)
        state2 = AzulState(2)
        
        # Get initial hashes
        hash1 = state1.get_zobrist_hash()
        hash2 = state2.get_zobrist_hash()
        
        # Should be different (due to random initialization)
        assert hash1 != hash2
    
    def test_zobrist_hash_update(self):
        """Test that hash updates correctly when state changes."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        original_hash = state.get_zobrist_hash()
        
        # Make a change to the state
        state.agents[0].score = 10
        
        # Hash should be different
        new_hash = state.get_zobrist_hash()
        assert new_hash != original_hash


class TestCloneAndUndo:
    """Test the clone and undo functionality."""
    
    def test_clone_creates_independent_copy(self):
        """Test that clone creates a truly independent copy."""
        from core.azul_model import AzulState
        
        original = AzulState(2)
        original.agents[0].score = 100
        
        # Clone the state
        cloned = original.clone()
        
        # Modify the original
        original.agents[0].score = 200
        
        # Cloned state should be unchanged
        assert cloned.agents[0].score == 100
        assert original.agents[0].score == 200
    
    def test_clone_preserves_all_state(self):
        """Test that clone preserves all important state information."""
        from core.azul_model import AzulState
        
        original = AzulState(2)
        
        # Modify various parts of the state
        original.agents[0].score = 50
        original.agents[1].score = 75
        original.first_agent = 1
        original.first_agent_taken = True
        
        # Clone
        cloned = original.clone()
        
        # Check that all state is preserved
        assert cloned.agents[0].score == 50
        assert cloned.agents[1].score == 75
        assert cloned.first_agent == 1
        assert cloned.first_agent_taken == True
        
        # Check that arrays are properly copied
        assert cloned.agents[0].lines_number is not original.agents[0].lines_number
        assert cloned.agents[0].grid_state is not original.agents[0].grid_state
        assert cloned.bag is not original.bag
    
    def test_get_move_info_captures_state(self):
        """Test that get_move_info captures the current state correctly."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        state.agents[0].score = 100
        state.agents[1].score = 200
        
        move_info = state.get_move_info()
        
        # Check that move info contains the right data
        assert move_info['agents'][0]['score'] == 100
        assert move_info['agents'][1]['score'] == 200
        assert 'bag' in move_info
        assert 'factories' in move_info
        assert 'centre_pool' in move_info
    
    def test_undo_move_restores_state(self):
        """Test that undo_move correctly restores the previous state."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        
        # Capture initial state
        initial_score = state.agents[0].score
        move_info = state.get_move_info()
        
        # Make changes
        state.agents[0].score = 999
        state.agents[1].score = 888
        
        # Undo the changes
        state.undo_move(move_info)
        
        # Check that state is restored
        assert state.agents[0].score == initial_score
        assert state.agents[1].score == initial_score
    
    def test_clone_and_undo_integration(self):
        """Test that clone and undo work together correctly."""
        from core.azul_model import AzulState
        
        original = AzulState(2)
        original.agents[0].score = 100
        
        # Clone and modify original
        cloned = original.clone()
        original.agents[0].score = 200
        
        # Capture state of cloned
        move_info = cloned.get_move_info()
        
        # Modify cloned
        cloned.agents[0].score = 300
        
        # Undo in cloned
        cloned.undo_move(move_info)
        
        # Check that cloned is back to original state
        assert cloned.agents[0].score == 100
        assert original.agents[0].score == 200  # Original unchanged


class TestStateImmutability:
    """Test that state objects maintain immutability guarantees."""
    
    def test_agent_state_arrays_are_copied(self):
        """Test that agent state arrays are properly copied to prevent mutations."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        original = state.clone()
        
        # Modify arrays in original
        state.agents[0].lines_number[0] = 999
        state.agents[0].grid_state[0][0] = 1
        
        # Check that cloned state is unchanged
        assert original.agents[0].lines_number[0] != 999
        assert original.agents[0].grid_state[0][0] != 1
    
    def test_bag_arrays_are_copied(self):
        """Test that bag arrays are properly copied."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        original = state.clone()
        
        # Modify bag in original
        if len(state.bag) > 0:
            state.bag[0] = None
        
        # Check that cloned state is unchanged
        if len(original.bag) > 0:
            assert original.bag[0] is not None


class TestImmutabilityFeatures:
    """Test the new immutability features and guarantees."""
    
    def test_immutable_tile_display(self):
        """Test that ImmutableTileDisplay works correctly."""
        from core.azul_model import ImmutableTileDisplay
        from core import azul_utils as utils
        
        # Create initial display
        display = ImmutableTileDisplay()
        assert display.total == 0
        assert all(display.tiles[tile] == 0 for tile in utils.Tile)
        
        # Add tiles
        new_display = display.add_tiles(3, utils.Tile.BLUE)
        assert new_display.total == 3
        assert new_display.tiles[utils.Tile.BLUE] == 3
        assert display.total == 0  # Original unchanged
        
        # Remove tiles
        final_display = new_display.reaction_tiles(2, utils.Tile.BLUE)
        assert final_display.total == 1
        assert final_display.tiles[utils.Tile.BLUE] == 1
        assert new_display.total == 3  # Previous unchanged
    
    def test_immutable_agent_state(self):
        """Test that ImmutableAgentState works correctly."""
        from core.azul_model import ImmutableAgentState
        
        # Create initial state
        agent = ImmutableAgentState(id=0)
        assert agent.id == 0
        assert agent.score == 0
        assert len(agent.lines_number) == 5
        assert len(agent.lines_tile) == 5
        assert agent.grid_state.shape == (5, 5)
        
        # Update score
        new_agent = agent.with_score(100)
        assert new_agent.score == 100
        assert agent.score == 0  # Original unchanged
        
        # Update lines
        new_lines_number = [1, 2, 3, 4, 5]
        new_lines_tile = [0, 1, 2, 3, 4]
        new_agent2 = agent.with_lines(new_lines_number, new_lines_tile)
        assert new_agent2.lines_number == new_lines_number
        assert new_agent2.lines_tile == new_lines_tile
        assert agent.lines_number == [0] * 5  # Original unchanged
    
    def test_immutable_azul_state(self):
        """Test that ImmutableAzulState works correctly."""
        from core.azul_model import AzulState, ImmutableAzulState
        
        # Create mutable state
        state = AzulState(2)
        state.agents[0].score = 50
        
        # Convert to immutable
        immutable_state = state.to_immutable()
        assert isinstance(immutable_state, ImmutableAzulState)
        assert immutable_state.agents[0].score == 50
        assert len(immutable_state.agents) == 2
        assert len(immutable_state.factories) == 5  # 2-player game
        
        # Convert back to mutable
        new_state = immutable_state.to_mutable()
        assert isinstance(new_state, AzulState)
        assert new_state.agents[0].score == 50
    
    def test_immutability_validation(self):
        """Test that immutability validation works correctly."""
        from core.azul_model import AzulState
        
        # This should work without errors
        state = AzulState(2)
        
        # Test that validation catches issues (if we had any)
        # The validation is currently just type checking, so it should pass
        assert hasattr(state, '_validate_immutability')
    
    def test_debug_immutability_warnings(self):
        """Test that debug immutability warnings work."""
        from core.azul_model import AzulState
        import os
        import warnings
        
        # Set debug flag
        os.environ['AZUL_DEBUG_IMMUTABILITY'] = 'true'
        
        state = AzulState(2)
        
        # Test warning function
        with warnings.catch_warnings(record=True) as w:
            state._check_mutation_attempt("test_operation")
            assert len(w) == 1
            assert "Mutation attempt detected" in str(w[0].message)
        
        # Clean up
        os.environ['AZUL_DEBUG_IMMUTABILITY'] = 'false'
    
    def test_immutable_conversion_preserves_state(self):
        """Test that immutable conversion preserves all state correctly."""
        from core.azul_model import AzulState
        
        # Create state with some modifications
        state = AzulState(2)
        state.agents[0].score = 100
        state.agents[1].score = 200
        state.first_agent = 1
        state.first_agent_taken = True
        
        # Convert to immutable and back
        immutable_state = state.to_immutable()
        new_state = immutable_state.to_mutable()
        
        # Check that all state is preserved
        assert new_state.agents[0].score == 100
        assert new_state.agents[1].score == 200
        assert new_state.first_agent == 1
        assert new_state.first_agent_taken == True
        
        # Check that arrays are properly copied
        assert new_state.agents[0].lines_number is not state.agents[0].lines_number
        assert new_state.agents[0].grid_state is not state.agents[0].grid_state
        assert new_state.bag is not state.bag
    
    def test_immutable_methods_return_new_objects(self):
        """Test that immutable methods return new objects, not modified ones."""
        from core.azul_model import ImmutableTileDisplay, ImmutableAgentState
        from core import azul_utils as utils
        
        # Test TileDisplay
        display1 = ImmutableTileDisplay()
        display2 = display1.add_tiles(5, utils.Tile.RED)
        
        assert display1 is not display2
        assert display1.total == 0
        assert display2.total == 5
        
        # Test AgentState
        agent1 = ImmutableAgentState(id=0)
        agent2 = agent1.with_score(150)
        
        assert agent1 is not agent2
        assert agent1.score == 0
        assert agent2.score == 150
    
    def test_immutable_state_hash_consistency(self):
        """Test that immutable states produce consistent hashes."""
        from core.azul_model import AzulState
        
        # Create two identical states
        state1 = AzulState(2)
        state2 = AzulState(2)
        
        # Set same random seed for both
        import random
        random.seed(42)
        state1 = AzulState(2)
        random.seed(42)
        state2 = AzulState(2)
        
        # Convert both to immutable
        immutable1 = state1.to_immutable()
        immutable2 = state2.to_immutable()
        
        # Convert back and check hashes
        new_state1 = immutable1.to_mutable()
        new_state2 = immutable2.to_mutable()
        
        hash1 = new_state1.get_zobrist_hash()
        hash2 = new_state2.get_zobrist_hash()
        
        assert hash1 == hash2


if __name__ == '__main__':
    pytest.main([__file__])