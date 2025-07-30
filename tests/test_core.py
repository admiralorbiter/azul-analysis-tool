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


if __name__ == '__main__':
    pytest.main([__file__])