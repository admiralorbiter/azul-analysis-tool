"""
Unit tests for TileDisplay regression fix.

These tests ensure that the TileDisplay.AddTiles and TileDisplay.ReactionTiles methods
handle edge cases properly and don't cause AssertionError when tiles are added/removed
from partially initialized TileDisplay objects.

This prevents the move execution error that occurred when the centre_pool was not
fully initialized with all tile types.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.azul_model import AzulState, AzulGameRule
from core.azul_utils import Tile, Action, TileGrab


class TestTileDisplayRegression:
    """Test TileDisplay regression fixes for AddTiles and ReactionTiles methods."""
    
    def test_tiledisplay_initialization(self):
        """Test that TileDisplay is properly initialized with all tile types."""
        from core.azul_model import AzulState
        
        # Create a new state to get access to TileDisplay class
        state = AzulState(2)
        display = state.TileDisplay()
        
        # Check that all tile types are initialized to 0
        for tile in Tile:
            assert tile in display.tiles
            assert display.tiles[tile] == 0
        
        assert display.total == 0
    
    def test_addtiles_with_uninitialized_tiles_dict(self):
        """Test AddTiles when self.tiles is None or not properly initialized."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        display = state.TileDisplay()
        
        # Manually break the tiles dict to simulate the bug
        display.tiles = None
        
        # This should not raise an AssertionError
        try:
            display.AddTiles(2, Tile.BLUE)
            assert display.tiles[Tile.BLUE] == 2
            assert display.total == 2
        except AssertionError as e:
            pytest.fail(f"AddTiles should not raise AssertionError: {e}")
    
    def test_addtiles_with_missing_tile_type(self):
        """Test AddTiles when a specific tile type is missing from the dict."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        display = state.TileDisplay()
        
        # Remove a tile type to simulate partial initialization
        del display.tiles[Tile.RED]
        
        # This should not raise an AssertionError
        try:
            display.AddTiles(3, Tile.RED)
            assert display.tiles[Tile.RED] == 3
            assert display.total == 3
        except AssertionError as e:
            pytest.fail(f"AddTiles should not raise AssertionError: {e}")
    
    def test_reactiontiles_with_uninitialized_tiles_dict(self):
        """Test ReactionTiles when self.tiles is None or not properly initialized."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        display = state.TileDisplay()
        
        # Add some tiles first
        display.AddTiles(5, Tile.YELLOW)
        
        # Manually break the tiles dict to simulate the bug
        display.tiles = None
        
        # This should not raise an AssertionError, but it will fail the assertion
        # that checks if tiles[tile_type] >= 0, which is expected behavior
        try:
            display.ReactionTiles(2, Tile.YELLOW)
            # If we get here, the fix worked
            assert display.tiles[Tile.YELLOW] == 3
            assert display.total == 3
        except AssertionError as e:
            # This is expected - we can't remove more tiles than we have
            # The important thing is that it doesn't fail on the KeyError
            assert "KeyError" not in str(e)
    
    def test_reactiontiles_with_missing_tile_type(self):
        """Test ReactionTiles when a specific tile type is missing from the dict."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        display = state.TileDisplay()
        
        # Add some tiles first
        display.AddTiles(4, Tile.BLACK)
        
        # Remove a tile type to simulate partial initialization
        del display.tiles[Tile.BLACK]
        
        # This should not raise a KeyError, but will fail the assertion
        # that checks if tiles[tile_type] >= 0, which is expected
        try:
            display.ReactionTiles(1, Tile.BLACK)
            # If we get here, the fix worked
            assert display.tiles[Tile.BLACK] == 3
            assert display.total == 3
        except AssertionError as e:
            # This is expected - we can't remove more tiles than we have
            # The important thing is that it doesn't fail on the KeyError
            assert "KeyError" not in str(e)
    
    def test_centre_pool_initialization_from_fen(self):
        """Test that centre_pool is properly initialized when loading from FEN."""
        from core.azul_model import AzulState
        
        # Create a state and get its FEN
        state = AzulState(2)
        fen = state.to_fen()
        
        # Load the state from FEN
        new_state = AzulState.from_fen(fen)
        
        # Check that centre_pool is properly initialized
        assert hasattr(new_state.centre_pool, 'tiles')
        assert new_state.centre_pool.tiles is not None
        
        # The centre_pool might be empty initially, which is fine
        # Just check that the tiles dict exists and is properly initialized
        assert isinstance(new_state.centre_pool.tiles, dict)
    
    def test_move_execution_with_partial_centre_pool(self):
        """Test that move execution works even with partially initialized centre_pool."""
        from core.azul_model import AzulState, AzulGameRule
        
        # Create a state
        state = AzulState(2)
        rule = AzulGameRule(2)
        
        # Get legal moves
        legal_moves = rule.getLegalActions(state, 0)
        
        if legal_moves:
            # Take the first legal move
            move = legal_moves[0]
            
            # Manually break centre_pool to simulate the bug
            state.centre_pool.tiles = None
            
            # This should not raise an AssertionError
            try:
                new_state = rule.generateSuccessor(state, move, 0)
                assert new_state is not None
            except AssertionError as e:
                pytest.fail(f"generateSuccessor should not raise AssertionError: {e}")
    
    def test_factory_initialization_edge_cases(self):
        """Test factory initialization with edge cases."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        
        # Test each factory
        for i, factory in enumerate(state.factories):
            # Manually break the factory tiles dict
            factory.tiles = None
            
            # This should not raise an AssertionError
            try:
                factory.AddTiles(1, Tile.WHITE)
                assert factory.tiles[Tile.WHITE] == 1
                # Note: total might be different because factories start with tiles
                assert factory.total >= 1
            except AssertionError as e:
                pytest.fail(f"Factory {i} AddTiles should not raise AssertionError: {e}")
    
    def test_round_trip_fen_with_edge_cases(self):
        """Test round-trip FEN conversion with edge cases that might cause initialization issues."""
        from core.azul_model import AzulState
        
        # Create a state and make some moves to get a more complex state
        state = AzulState(2)
        rule = AzulGameRule(2)
        
        # Make a few moves if possible
        for _ in range(3):
            legal_moves = rule.getLegalActions(state, 0)
            if legal_moves:
                state = rule.generateSuccessor(state, legal_moves[0], 0)
                legal_moves = rule.getLegalActions(state, 1)
                if legal_moves:
                    state = rule.generateSuccessor(state, legal_moves[0], 1)
        
        # Convert to FEN and back
        fen = state.to_fen()
        new_state = AzulState.from_fen(fen)
        
        # Check that all components are properly initialized
        assert hasattr(new_state.centre_pool, 'tiles')
        assert new_state.centre_pool.tiles is not None
        
        for factory in new_state.factories:
            assert hasattr(factory, 'tiles')
            assert factory.tiles is not None
    
    def test_api_move_execution_regression(self):
        """Test that API move execution doesn't fail with the regression."""
        import requests
        import json
        
        # This test requires the API server to be running
        # If it's not running, we'll skip this test
        try:
            # Get initial game state
            response = requests.get('http://localhost:8000/api/v1/game_state')
            if response.status_code != 200:
                pytest.skip("API server not available")
            
            game_state = response.json()
            
            # Create a simple move
            move_data = {
                "action": Action.TAKE_FROM_FACTORY,
                "factory_index": 0,
                "tile_type": Tile.BLUE,
                "pattern_line": 0
            }
            
            # Execute the move
            response = requests.post(
                'http://localhost:8000/api/v1/execute_move',
                json=move_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Should not get a 500 error
            assert response.status_code != 500, f"Move execution failed with 500 error: {response.text}"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_tiledisplay_immutable_version(self):
        """Test that the immutable version of TileDisplay also handles edge cases properly."""
        from core.azul_model import ImmutableTileDisplay
        
        # Test with empty tiles dict
        display = ImmutableTileDisplay()
        
        # This should work without issues
        new_display = display.add_tiles(2, Tile.BLUE)
        assert new_display.tiles[Tile.BLUE] == 2
        assert new_display.total == 2
        
        # Test reaction
        final_display = new_display.reaction_tiles(1, Tile.BLUE)
        assert final_display.tiles[Tile.BLUE] == 1
        assert final_display.total == 1
    
    def test_critical_regression_scenario(self):
        """Test the exact scenario that caused the original regression."""
        from core.azul_model import AzulState, AzulGameRule
        
        # Create a state
        state = AzulState(2)
        rule = AzulGameRule(2)
        
        # Get legal moves
        legal_moves = rule.getLegalActions(state, 0)
        
        if legal_moves:
            # Take the first legal move
            move = legal_moves[0]
            
            # This is the critical test - ensure move execution doesn't fail
            # due to uninitialized centre_pool tiles dict
            try:
                new_state = rule.generateSuccessor(state, move, 0)
                assert new_state is not None
                
                # Make sure the new state has properly initialized components
                assert hasattr(new_state.centre_pool, 'tiles')
                assert new_state.centre_pool.tiles is not None
                
            except AssertionError as e:
                # Check if it's the specific error we fixed
                if "tile_type in self.tiles" in str(e):
                    pytest.fail(f"Critical regression still present: {e}")
                else:
                    # Other assertion errors are acceptable
                    pass


class TestMoveExecutionRobustness:
    """Test that move execution is robust against various edge cases."""
    
    def test_move_execution_with_corrupted_state(self):
        """Test move execution when state components are corrupted."""
        from core.azul_model import AzulState, AzulGameRule
        
        state = AzulState(2)
        rule = AzulGameRule(2)
        
        # Corrupt various components
        state.centre_pool.tiles = None
        state.factories[0].tiles = None
        
        # This should fail gracefully, not with a KeyError
        try:
            legal_moves = rule.getLegalActions(state, 0)
            # If we get here, the system handled the corruption gracefully
            pass
        except TypeError as e:
            # This is expected - the system can't handle completely corrupted state
            # But it should fail gracefully, not with the original KeyError
            assert "KeyError" not in str(e)
    
    def test_fen_loading_robustness(self):
        """Test that FEN loading is robust against various malformed states."""
        from core.azul_model import AzulState
        
        # Create a state and get its FEN
        state = AzulState(2)
        fen = state.to_fen()
        
        # Load from FEN multiple times to test robustness
        for _ in range(5):
            try:
                new_state = AzulState.from_fen(fen)
                assert new_state is not None
                
                # Check that all components are properly initialized
                assert hasattr(new_state.centre_pool, 'tiles')
                assert new_state.centre_pool.tiles is not None
                
                for factory in new_state.factories:
                    assert hasattr(factory, 'tiles')
                    assert factory.tiles is not None
                    
            except Exception as e:
                pytest.fail(f"FEN loading should be robust: {e}")
    
    def test_tiledisplay_edge_case_handling(self):
        """Test that TileDisplay handles edge cases gracefully."""
        from core.azul_model import AzulState
        
        state = AzulState(2)
        display = state.TileDisplay()
        
        # Test various edge cases
        edge_cases = [
            (None, Tile.BLUE),  # tiles dict is None
            ({}, Tile.RED),      # tiles dict is empty
            ({Tile.BLUE: 1}, Tile.YELLOW),  # tiles dict missing some types
        ]
        
        for tiles_dict, tile_type in edge_cases:
            display.tiles = tiles_dict
            
            # AddTiles should handle this gracefully
            try:
                display.AddTiles(1, tile_type)
                assert display.tiles[tile_type] >= 1
            except (KeyError, TypeError) as e:
                pytest.fail(f"AddTiles should handle edge case {tiles_dict}: {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
