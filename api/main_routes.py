"""
REST API routes for the Azul Solver & Analysis Toolkit.

This module provides Flask blueprints for game analysis, hints, and research tools.
"""

import json
import time
import copy
import random
import threading
import uuid
import psutil
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, ValidationError, ConfigDict
from dataclasses import asdict

from .auth import require_session
from .rate_limiter import RateLimiter
from core.azul_database import AzulDatabase

# Import models from the new modular structure
from .models import (
    # Analysis models
    AnalysisRequest,
    HintRequest,
    AnalysisCacheRequest,
    AnalysisSearchRequest,
    
    # Position models
    PositionCacheRequest,
    BulkPositionRequest,
    PositionDatabaseRequest,
    SimilarPositionRequest,
    ContinuationRequest,
    
    # Neural models
    NeuralTrainingRequest,
    NeuralEvaluationRequest,
    NeuralConfigRequest,
    
    # Game models
    GameCreationRequest,
    GameAnalysisRequest,
    GameLogUploadRequest,
    GameAnalysisSearchRequest,
    MoveExecutionRequest,
    
    # Validation models
    BoardValidationRequest,
    PatternDetectionRequest,
    ScoringOptimizationRequest,
    FloorLinePatternRequest,
    
    # Performance models
    PerformanceStatsRequest,
    SystemHealthRequest,
)

# Import utilities from the new modular structure
from .utils import (
    parse_fen_string,
    state_to_fen,
    update_current_game_state,
    convert_frontend_move_to_engine,
    find_matching_move,
    get_engine_response,
    convert_frontend_state_to_azul_state,
    convert_tile_string_to_type,
    format_move
)

# Import route blueprints from the new modular structure
from .routes import positions_bp

# Initialize database connection
db = AzulDatabase()


# Create Flask blueprint for API endpoints
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# Global variable to store the current game state
_current_game_state = None
_initial_game_state = None  # Store the original initial state
_current_editable_game_state = None  # Store the current editable game state from frontend

# Global training sessions storage (now database-backed)
# training_sessions = {}  # Replaced with database storage

# Global evaluation sessions storage
evaluation_sessions = {}

# The TrainingSession class has been removed - we now use database-backed NeuralTrainingSession only

def parse_fen_string(fen_string: str):
    """Parse FEN string to create game state."""
    global _current_game_state, _initial_game_state, _current_editable_game_state
    from core.azul_model import AzulState
    
    print(f"DEBUG: parse_fen_string called with: {fen_string}")
    print(f"DEBUG: _initial_game_state is None: {_initial_game_state is None}")
    print(f"DEBUG: _current_game_state is None: {_current_game_state is None}")
    print(f"DEBUG: _current_editable_game_state is None: {_current_editable_game_state is None}")
    
    try:
        if fen_string.lower() == "initial":
            # Use a consistent initial state with fixed seed for reproducibility
            if _initial_game_state is None:
                print("DEBUG: Creating initial game state")
                # Set a fixed seed to ensure consistent initial state
                random.seed(42)
                _initial_game_state = AzulState(2)  # 2-player starting position
                print(f"DEBUG: Initial game state created: {_initial_game_state is not None}")
                # Reset seed to random
                random.seed()
                # Initialize current state from initial state
                print("DEBUG: About to create current game state from initial")
                _current_game_state = copy.deepcopy(_initial_game_state)
                print(f"DEBUG: Current game state created: {_current_game_state is not None}")
            
            # Always return the current game state (which starts as a copy of initial)
            print(f"DEBUG: Returning current game state: {_current_game_state is not None}")
            if _current_game_state is None:
                print("DEBUG: ERROR - _current_game_state is None!")
                return None
            return _current_game_state
        elif fen_string.startswith("state_"):
            # This is a state identifier - check if we have an editable game state
            if _current_editable_game_state is not None:
                print("DEBUG: Using editable game state for custom state identifier")
                # Convert the frontend state back to an AzulState object
                try:
                    converted_state = convert_frontend_state_to_azul_state(_current_editable_game_state)
                    if converted_state is not None:
                        print("DEBUG: Successfully converted frontend state to AzulState. Setting as _current_game_state.")
                        _current_game_state = converted_state  # IMPORTANT: Update _current_game_state
                        return _current_game_state
                    else:
                        print("DEBUG: Failed to convert frontend state, falling back to current state")
                except Exception as e:
                    print(f"DEBUG: Error converting frontend state: {e}")
                
                # Fall back to current game state if conversion fails
                if _current_game_state is None:
                    # Fall back to initial state if no current state
                    if _initial_game_state is None:
                        random.seed(42)
                        _initial_game_state = AzulState(2)
                        random.seed()
                    _current_game_state = copy.deepcopy(_initial_game_state)
                return _current_game_state
            else:
                # No editable state, use current game state
                if _current_game_state is None:
                    # If we don't have a current state, create from initial state
                    if _initial_game_state is None:
                        print("DEBUG: Creating initial game state for state_ identifier")
                        random.seed(42)
                        _initial_game_state = AzulState(2)
                        random.seed()
                    _current_game_state = copy.deepcopy(_initial_game_state)
                return _current_game_state
        elif fen_string.lower() == "saved":
            # Handle 'saved' as equivalent to 'initial' for now
            # In the future, this could load from a saved state file
            print("DEBUG: Handling 'saved' FEN string as 'initial'")
            if _initial_game_state is None:
                print("DEBUG: Creating initial game state for saved")
                random.seed(42)
                _initial_game_state = AzulState(2)
                random.seed()
                _current_game_state = copy.deepcopy(_initial_game_state)
            return _current_game_state
        elif fen_string == "test_blocking_position":
            # Handle test blocking position - create a state with blocking opportunities
            print("DEBUG: Creating test blocking position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up a blocking scenario: Player 1 has blue tiles in pattern line 0
            # Player 0 (current player) can block by taking blue tiles
            test_state.agents[1].lines_tile[0] = 0  # Blue tiles in pattern line 0
            test_state.agents[1].lines_number[0] = 1  # 1 blue tile
            
            # Add blue tiles to factories for blocking
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add some blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "simple_blue_blocking":
            # Create simple blue blocking test position
            print("DEBUG: Creating simple blue blocking position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up simple blue blocking position
            # Player 2 has blue tiles in pattern line 0, needs 0 more tiles
            test_state.agents[1].lines_number[0] = 1  # 1 blue tile in line 0
            test_state.agents[1].lines_tile[0] = 0   # Blue color
            test_state.agents[1].grid_state[0][0] = 0  # Blue not on wall yet
            
            # Add blue tiles to factories
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            test_state.factories[2].tiles[0] = 1  # 1 blue tile in factory 2
            test_state.factories[3].tiles[0] = 1  # 1 blue tile in factory 3
            test_state.factories[4].tiles[0] = 1  # 1 blue tile in factory 4
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "high_urgency_red_blocking":
            # Create high urgency red blocking test position
            print("DEBUG: Creating high urgency red blocking position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up high urgency red blocking position
            # Player 2 has red tiles in pattern line 2, needs 1 more tile
            test_state.agents[1].lines_number[2] = 2  # 2 red tiles in line 2
            test_state.agents[1].lines_tile[2] = 2   # Red color
            test_state.agents[1].grid_state[2][2] = 0  # Red not on wall yet
            
            # Add red tiles to factories
            test_state.factories[0].tiles[2] = 1  # 1 red tile in factory 0
            test_state.factories[1].tiles[2] = 3  # 3 red tiles in factory 1
            test_state.factories[2].tiles[2] = 1  # 1 red tile in factory 2
            test_state.factories[3].tiles[2] = 1  # 1 red tile in factory 3
            test_state.factories[4].tiles[2] = 1  # 1 red tile in factory 4
            
            # Add red tiles to center pool
            test_state.centre_pool.tiles[2] = 2  # 2 red tiles in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "simple_row_completion":
            # Create simple row completion test position
            print("DEBUG: Creating simple row completion position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up simple row completion position
            # Player 0 has 4 tiles in row 0, needs 1 more to complete
            test_state.agents[0].grid_state[0][0] = 1  # Blue tile at (0,0)
            test_state.agents[0].grid_state[0][1] = 1  # Yellow tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Red tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Black tile at (0,3)
            # Missing white tile at (0,4) - this is the opportunity
            
            # Add white tiles to factories for completion
            test_state.factories[0].tiles[4] = 2  # 2 white tiles in factory 0
            test_state.factories[1].tiles[4] = 1  # 1 white tile in factory 1
            test_state.factories[2].tiles[4] = 1  # 1 white tile in factory 2
            
            # Add white tiles to center pool
            test_state.centre_pool.tiles[4] = 1  # 1 white tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "simple_column_completion":
            # Create simple column completion test position
            print("DEBUG: Creating simple column completion position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up simple column completion position
            # Player 0 has 4 tiles in column 0, needs 1 more to complete
            test_state.agents[0].grid_state[0][0] = 1  # Blue tile at (0,0)
            test_state.agents[0].grid_state[1][0] = 1  # Yellow tile at (1,0)
            test_state.agents[0].grid_state[2][0] = 1  # Red tile at (2,0)
            test_state.agents[0].grid_state[3][0] = 1  # Black tile at (3,0)
            # Missing white tile at (4,0) - this is the opportunity
            
            # Add white tiles to factories for completion
            test_state.factories[0].tiles[4] = 2  # 2 white tiles in factory 0
            test_state.factories[1].tiles[4] = 1  # 1 white tile in factory 1
            test_state.factories[2].tiles[4] = 1  # 1 white tile in factory 2
            
            # Add white tiles to center pool
            test_state.centre_pool.tiles[4] = 1  # 1 white tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "color_set_completion":
            # Create color set completion test position
            print("DEBUG: Creating color set completion position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up color set completion position (blue tiles)
            # Player 0 has 4 blue tiles, needs 1 more to complete set
            test_state.agents[0].grid_state[0][0] = 1  # Blue at (0,0)
            test_state.agents[0].grid_state[1][1] = 1  # Blue at (1,1)
            test_state.agents[0].grid_state[2][2] = 1  # Blue at (2,2)
            test_state.agents[0].grid_state[3][3] = 1  # Blue at (3,3)
            # Missing blue tile at (4,4) - this is the opportunity
            
            # Add blue tiles to factories for completion
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            test_state.factories[2].tiles[0] = 1  # 1 blue tile in factory 2
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "pattern_line_optimization":
            # Create pattern line optimization test position
            print("DEBUG: Creating pattern line optimization position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up pattern line optimization position
            # Player 0 has 2 tiles in pattern line 2 (capacity 3), needs 1 more
            test_state.agents[0].lines_number[2] = 2  # 2 tiles in line 2
            test_state.agents[0].lines_tile[2] = 0   # Blue color
            
            # Add blue tiles to factories for completion
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "floor_line_optimization":
            # Create floor line optimization test position
            print("DEBUG: Creating floor line optimization position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up floor line optimization position
            # Player 0 has 3 tiles in floor line (penalty -4)
            test_state.agents[0].floor_tiles = [0, 1, 2]  # 3 tiles in floor
            
            # Add tiles to factories for wall placement
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "multiplier_setup":
            # Create multiplier setup test position
            print("DEBUG: Creating multiplier setup position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up multiplier setup position
            # Player 0 has 4 tiles in row 0 and 4 tiles in column 0
            # Placing at (0,0) would complete both row and column
            test_state.agents[0].grid_state[0][1] = 1  # Tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Tile at (0,3)
            test_state.agents[0].grid_state[0][4] = 1  # Tile at (0,4)
            test_state.agents[0].grid_state[1][0] = 1  # Tile at (1,0)
            test_state.agents[0].grid_state[2][0] = 1  # Tile at (2,0)
            test_state.agents[0].grid_state[3][0] = 1  # Tile at (3,0)
            test_state.agents[0].grid_state[4][0] = 1  # Tile at (4,0)
            # Missing tile at (0,0) - this would complete both row and column
            
            # Add blue tiles to factories (blue goes at (0,0))
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        # Floor Line Management Test Positions
        elif fen_string == "critical_floor_risk":
            # Create critical floor risk test position
            print("DEBUG: Creating critical floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up critical floor risk position - Player 0 has 6 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2, 3, 4, 5]  # 6 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            test_state.factories[2].tiles[2] = 2  # 2 red tiles in factory 2
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            test_state.centre_pool.tiles[2] = 1  # 1 red tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "high_floor_risk":
            # Create high floor risk test position
            print("DEBUG: Creating high floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up high floor risk position - Player 0 has 4 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2, 3]  # 4 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "medium_floor_risk":
            # Create medium floor risk test position
            print("DEBUG: Creating medium floor risk position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up medium floor risk position - Player 0 has 2 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1]  # 2 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "early_game_floor_timing":
            # Create early game floor timing test position
            print("DEBUG: Creating early game floor timing position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up early game floor timing position - Player 0 has 1 tile on floor line
            test_state.agents[0].floor_tiles = [0]  # 1 tile on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "mid_game_floor_timing":
            # Create mid game floor timing test position
            print("DEBUG: Creating mid game floor timing position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up mid game floor timing position - Player 0 has 3 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2]  # 3 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "endgame_floor_timing":
            # Create endgame floor timing test position
            print("DEBUG: Creating endgame floor timing position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up endgame floor timing position - Player 0 has 5 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2, 3, 4]  # 5 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "wall_completion_trade_off":
            # Create wall completion trade-off test position
            print("DEBUG: Creating wall completion trade-off position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up wall completion trade-off position - Player 0 has 2 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1]  # 2 tiles on floor line
            
            # Player 0 has 4 tiles in row 0, needs 1 more to complete
            test_state.agents[0].grid_state[0][1] = 1  # Tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Tile at (0,3)
            test_state.agents[0].grid_state[0][4] = 1  # Tile at (0,4)
            # Missing tile at (0,0) - this would complete the row
            
            # Add blue tiles to factories (blue goes at (0,0))
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "endgame_penalty_minimization":
            # Create endgame penalty minimization test position
            print("DEBUG: Creating endgame penalty minimization position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up endgame penalty minimization position - Player 0 has 3 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2]  # 3 tiles on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "opponent_blocking_opportunity":
            # Create opponent blocking opportunity test position
            print("DEBUG: Creating opponent blocking opportunity position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up opponent blocking opportunity position - Player 0 has 2 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1]  # 2 tiles on floor line
            
            # Player 1 has blue tiles in pattern line 0, needs 1 more tile
            test_state.agents[1].lines_number[0] = 1  # 1 blue tile in line 0
            test_state.agents[1].lines_tile[0] = 0   # Blue color
            test_state.agents[1].grid_state[0][0] = 0  # Blue not on wall yet
            
            # Add blue tiles to factories for blocking
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "efficient_floor_clearance":
            # Create efficient floor clearance test position
            print("DEBUG: Creating efficient floor clearance position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up efficient floor clearance position - Player 0 has 1 tile on floor line
            test_state.agents[0].floor_tiles = [0]  # 1 tile on floor line
            
            # Add tiles to factories for wall placement opportunities
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[1] = 2  # 2 yellow tiles in factory 1
            
            # Add tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            test_state.centre_pool.tiles[1] = 1  # 1 yellow tile in center
            
            random.seed()  # Reset seed
            return test_state
        elif fen_string == "complex_risk_reward":
            # Create complex risk reward test position
            print("DEBUG: Creating complex risk reward position")
            random.seed(42)  # Use fixed seed for reproducibility
            test_state = AzulState(2)
            
            # Set up complex risk reward position - Player 0 has 4 tiles on floor line
            test_state.agents[0].floor_tiles = [0, 1, 2, 3]  # 4 tiles on floor line
            
            # Player 0 has 4 tiles in row 0, needs 1 more to complete
            test_state.agents[0].grid_state[0][1] = 1  # Tile at (0,1)
            test_state.agents[0].grid_state[0][2] = 1  # Tile at (0,2)
            test_state.agents[0].grid_state[0][3] = 1  # Tile at (0,3)
            test_state.agents[0].grid_state[0][4] = 1  # Tile at (0,4)
            # Missing tile at (0,0) - this would complete the row
            
            # Player 1 has blue tiles in pattern line 0, needs 1 more tile
            test_state.agents[1].lines_number[0] = 1  # 1 blue tile in line 0
            test_state.agents[1].lines_tile[0] = 0   # Blue color
            test_state.agents[1].grid_state[0][0] = 0  # Blue not on wall yet
            
            # Add blue tiles to factories for wall placement and blocking
            test_state.factories[0].tiles[0] = 2  # 2 blue tiles in factory 0
            test_state.factories[1].tiles[0] = 1  # 1 blue tile in factory 1
            
            # Add blue tiles to center pool
            test_state.centre_pool.tiles[0] = 1  # 1 blue tile in center
            
            random.seed()  # Reset seed
            return test_state
        else:
            raise ValueError(f"Unsupported FEN format: {fen_string}. Use 'initial', 'saved', 'test_blocking_position', 'simple_row_completion', 'simple_column_completion', 'color_set_completion', 'pattern_line_optimization', 'floor_line_optimization', 'multiplier_setup', 'critical_floor_risk', 'high_floor_risk', 'medium_floor_risk', 'early_game_floor_timing', 'mid_game_floor_timing', 'endgame_floor_timing', 'wall_completion_trade_off', 'endgame_penalty_minimization', 'opponent_blocking_opportunity', 'efficient_floor_clearance', 'complex_risk_reward', or state identifiers.")
    except Exception as e:
        print(f"DEBUG: Exception in parse_fen_string: {e}")
        import traceback
        traceback.print_exc()
        # Re-raise ValueError for invalid FEN strings to get proper 400 status codes
        if isinstance(e, ValueError):
            raise
        return None




# Analysis Cache API Endpoints


# Analysis Cache API Endpoints




@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Check rate limit if session is provided
    session_id = request.headers.get('X-Session-ID')
    if session_id and current_app.rate_limiter:
        if not current_app.rate_limiter.check_rate_limit(session_id, "general"):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests'
            }), 429
    
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'timestamp': time.time()
    })


@api_bp.route('/stats', methods=['GET'])
@require_session
def get_api_stats():
    """Get API usage statistics."""
    session_id = request.headers.get('X-Session-ID')
    
    return jsonify({
        'rate_limits': current_app.rate_limiter.get_remaining_requests(session_id) if current_app.rate_limiter else {},
        'session_stats': current_app.session_manager.get_session_stats() if hasattr(current_app, 'session_manager') else {}
    }) 


@api_bp.route('/analyze_neural', methods=['POST'])
def analyze_neural():
    """Analyze position using neural MCTS."""
    try:
        data = request.get_json()
        
        # Parse request
        fen_string = data.get('fen', 'initial')
        agent_id = data.get('agent_id', 0)
        time_budget = data.get('time_budget', 2.0)
        max_rollouts = data.get('max_rollouts', 100)
        
        # Parse FEN and create state
        state = parse_fen_string(fen_string)
        if state is None:
            return jsonify({'error': 'Invalid FEN string'}), 400
        
        # Check if neural components are available
        try:
            from core.azul_mcts import AzulMCTS, RolloutPolicy
            from neural.azul_net import create_azul_net, AzulNeuralRolloutPolicy
            
            # Create neural MCTS
            mcts = AzulMCTS(
                rollout_policy=RolloutPolicy.NEURAL,
                max_time=time_budget,
                max_rollouts=max_rollouts,
                database=getattr(current_app, 'database', None)
            )
            
            # Perform search
            result = mcts.search(state, agent_id=agent_id, fen_string=fen_string)
            
            # Format response
            analysis = {
                'best_move': format_move(result.best_move),
                'best_score': result.best_score,
                'principal_variation': [format_move(move) for move in result.principal_variation],
                'search_time': result.search_time,
                'nodes_searched': result.nodes_searched,
                'rollout_count': result.rollout_count,
                'average_rollout_depth': result.average_rollout_depth,
                'method': 'neural_mcts'
            }
            
            # Cache result if database available
            if hasattr(current_app, 'database') and current_app.database:
                try:
                    position_id = current_app.database.cache_position(fen_string, len(state.agents))
                    current_app.database.cache_analysis(position_id, agent_id, 'neural_mcts', analysis)
                except Exception as e:
                    current_app.logger.warning(f"Failed to cache neural analysis: {e}")
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except ImportError as e:
            return jsonify({
                'error': 'Neural analysis not available',
                'message': 'PyTorch and neural components are not installed. Install with: pip install torch',
                'details': str(e)
            }), 503
            
        except Exception as e:
            return jsonify({
                'error': 'Neural analysis failed',
                'message': 'Neural model not trained or available',
                'details': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# B2.3: Performance API Endpoints
# ============================================================================

@api_bp.route('/performance/stats', methods=['GET'])
@require_session
def get_performance_stats():
    """
    Get comprehensive performance statistics.
    
    GET /api/v1/performance/stats
    Query parameters:
    - search_type: Optional search type filter
    - time_range_hours: Optional time range filter
    - include_query_stats: Include query performance stats (default: true)
    - include_index_stats: Include index usage stats (default: true)
    
    Returns:
        Comprehensive performance statistics including search performance,
        query performance, index usage, and cache analytics.
    """
    try:
        # Parse query parameters
        search_type = request.args.get('search_type')
        time_range_hours = request.args.get('time_range_hours', type=int)
        include_query_stats = request.args.get('include_query_stats', 'true').lower() == 'true'
        include_index_stats = request.args.get('include_index_stats', 'true').lower() == 'true'
        
        # Get database stats
        db_stats = current_app.database.get_cache_stats()
        
        # Get performance stats
        perf_stats = current_app.database.get_performance_stats(search_type)
        
        # Build response
        response = {
            'timestamp': time.time(),
            'search_performance': {
                'by_search_type': db_stats.get('by_search_type', {}),
                'performance_stats': perf_stats
            },
            'cache_analytics': {
                'positions_cached': db_stats.get('positions_cached', 0),
                'analyses_cached': db_stats.get('analyses_cached', 0),
                'cache_hit_rate': db_stats.get('cache_hit_rate', 0.0),
                'total_cache_size_mb': db_stats.get('total_cache_size_mb', 0.0)
            }
        }
        
        # Add query performance stats if requested
        if include_query_stats:
            query_stats = current_app.database.get_query_performance_stats()
            response['query_performance'] = query_stats
        
        # Add index usage stats if requested
        if include_index_stats:
            index_stats = current_app.database.get_index_usage_stats()
            response['index_usage'] = index_stats
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance stats: {e}")
        return jsonify({'error': 'Failed to get performance stats', 'message': str(e)}), 500


@api_bp.route('/performance/health', methods=['GET'])
@require_session
def get_system_health():
    """
    Get comprehensive system health status.
    
    GET /api/v1/performance/health
    Query parameters:
    - include_database_health: Include database health checks (default: true)
    - include_performance_metrics: Include performance metrics (default: true)
    - include_cache_analytics: Include cache analytics (default: true)
    
    Returns:
        System health status including database integrity, performance metrics,
        and cache analytics.
    """
    try:
        # Parse query parameters
        include_database_health = request.args.get('include_database_health', 'true').lower() == 'true'
        include_performance_metrics = request.args.get('include_performance_metrics', 'true').lower() == 'true'
        include_cache_analytics = request.args.get('include_cache_analytics', 'true').lower() == 'true'
        
        # Basic health check
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '0.1.0'
        }
        
        # Database health check
        if include_database_health:
            try:
                db_info = current_app.database.get_database_info()
                health_status['database'] = {
                    'status': 'healthy',
                    'file_size_mb': db_info.get('file_size_mb', 0),
                    'total_pages': db_info.get('total_pages', 0),
                    'free_pages': db_info.get('free_pages', 0),
                    'page_size': db_info.get('page_size', 0),
                    'integrity_check': 'ok'  # We'll add actual integrity check if needed
                }
            except Exception as e:
                health_status['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        # Performance metrics
        if include_performance_metrics:
            try:
                perf_stats = current_app.database.get_performance_stats()
                health_status['performance'] = {
                    'status': 'healthy',
                    'total_searches': sum(stat.get('total_searches', 0) for stat in perf_stats),
                    'average_search_time_ms': sum(stat.get('average_search_time_ms', 0) for stat in perf_stats) / max(len(perf_stats), 1),
                    'cache_hit_rate': sum(stat.get('cache_hit_rate', 0) for stat in perf_stats) / max(len(perf_stats), 1)
                }
            except Exception as e:
                health_status['performance'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        # Cache analytics
        if include_cache_analytics:
            try:
                cache_stats = current_app.database.get_cache_stats()
                health_status['cache'] = {
                    'status': 'healthy',
                    'positions_cached': cache_stats.get('positions_cached', 0),
                    'analyses_cached': cache_stats.get('analyses_cached', 0),
                    'cache_hit_rate': cache_stats.get('cache_hit_rate', 0.0),
                    'total_size_mb': cache_stats.get('total_cache_size_mb', 0.0)
                }
            except Exception as e:
                health_status['cache'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        current_app.logger.error(f"Error getting system health: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Failed to get system health',
            'message': str(e),
            'timestamp': time.time()
        }), 500


@api_bp.route('/performance/optimize', methods=['POST'])
@require_session
def optimize_database():
    """
    Optimize database performance.
    
    POST /api/v1/performance/optimize
    
    Returns:
        Database optimization results including VACUUM and ANALYZE operations.
    """
    try:
        # Perform database optimization
        optimization_result = current_app.database.optimize_database()
        
        return jsonify({
            'success': True,
            'optimization_result': optimization_result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error optimizing database: {e}")
        return jsonify({'error': 'Failed to optimize database', 'message': str(e)}), 500


@api_bp.route('/performance/analytics', methods=['GET'])
@require_session
def get_cache_analytics():
    """
    Get detailed cache analytics and performance insights.
    
    GET /api/v1/performance/analytics
    Query parameters:
    - search_type: Optional search type filter
    - limit: Number of high-quality analyses to return (default: 10)
    
    Returns:
        Detailed cache analytics including high-quality analyses,
        performance trends, and optimization recommendations.
    """
    try:
        # Parse query parameters
        search_type = request.args.get('search_type')
        limit = request.args.get('limit', 10, type=int)
        
        # Get cache stats
        cache_stats = current_app.database.get_cache_stats()
        
        # Get high-quality analyses if search_type specified
        high_quality_analyses = []
        if search_type:
            try:
                high_quality_analyses = current_app.database.get_high_quality_analyses(search_type, limit)
                # Convert to serializable format
                high_quality_analyses = [
                    {
                        'position_id': analysis.position_id,
                        'agent_id': analysis.agent_id,
                        'search_type': analysis.search_type,
                        'best_move': analysis.best_move,
                        'score': analysis.score,
                        'search_time': analysis.search_time,
                        'nodes_searched': analysis.nodes_searched,
                        'rollout_count': analysis.rollout_count,
                        'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                        'principal_variation': analysis.principal_variation
                    }
                    for analysis in high_quality_analyses
                ]
            except Exception as e:
                current_app.logger.warning(f"Failed to get high-quality analyses: {e}")
        
        # Get analysis stats by type
        analysis_stats = {}
        if search_type:
            try:
                analysis_stats = current_app.database.get_analysis_stats_by_type(search_type)
            except Exception as e:
                current_app.logger.warning(f"Failed to get analysis stats: {e}")
        
        # Build analytics response
        analytics = {
            'timestamp': time.time(),
            'cache_overview': {
                'positions_cached': cache_stats.get('positions_cached', 0),
                'analyses_cached': cache_stats.get('analyses_cached', 0),
                'cache_hit_rate': cache_stats.get('cache_hit_rate', 0.0),
                'total_size_mb': cache_stats.get('total_cache_size_mb', 0.0)
            },
            'performance_metrics': {
                'by_search_type': cache_stats.get('by_search_type', {}),
                'performance': cache_stats.get('performance', {})
            },
            'high_quality_analyses': high_quality_analyses,
            'analysis_stats': analysis_stats
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache analytics: {e}")
        return jsonify({'error': 'Failed to get cache analytics', 'message': str(e)}), 500


@api_bp.route('/performance/monitoring', methods=['GET'])
@require_session
def get_monitoring_data():
    """
    Get real-time monitoring data for system performance.
    
    GET /api/v1/performance/monitoring
    
    Returns:
        Real-time monitoring data including query performance,
        index usage, and system metrics.
    """
    try:
        # Get query performance stats
        query_stats = current_app.database.get_query_performance_stats()
        
        # Get index usage stats
        index_stats = current_app.database.get_index_usage_stats()
        
        # Get database info
        db_info = current_app.database.get_database_info()
        
        # Build monitoring response
        monitoring_data = {
            'timestamp': time.time(),
            'query_performance': query_stats,
            'index_usage': index_stats,
            'database_metrics': {
                'file_size_mb': db_info.get('file_size_mb', 0),
                'total_pages': db_info.get('total_pages', 0),
                'free_pages': db_info.get('free_pages', 0),
                'page_size': db_info.get('page_size', 0),
                'cache_size_pages': db_info.get('cache_size_pages', 0)
            },
            'system_metrics': {
                'uptime': time.time(),  # Could be enhanced with actual uptime tracking
                'memory_usage_mb': 0,  # Could be enhanced with actual memory tracking
                'active_connections': 1  # Could be enhanced with connection pooling
            }
        }
        
        return jsonify(monitoring_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting monitoring data: {e}")
        return jsonify({'error': 'Failed to get monitoring data', 'message': str(e)}), 500


@api_bp.route('/execute_move', methods=['POST'])
# @require_session # Removed for local development
def execute_move():
    """Execute a move and return new game state."""
    try:
        print("DEBUG: execute_move endpoint called")
        
        try:
            data = request.get_json(force=True)
            print(f"DEBUG: Raw data received: {data}")
            print(f"DEBUG: FEN string received: {data.get('fen_string', 'NOT_FOUND')}")
        except Exception as e:
            print(f"DEBUG: Error parsing JSON: {e}")
            data = None
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        print("DEBUG: About to create MoveExecutionRequest")
        request_model = MoveExecutionRequest(**data)
        print(f"DEBUG: Request model created: {request_model}")
        
        # Parse current state
        try:
            print("DEBUG: About to parse FEN string")
            state = parse_fen_string(request_model.fen_string)
            print(f"DEBUG: FEN parsed successfully - state is None: {state is None}")
            if state is not None:
                print(f"DEBUG: State has agents: {hasattr(state, 'agents')}")
                print(f"DEBUG: Agent count: {len(state.agents) if hasattr(state, 'agents') else 'No agents'}")
                print(f"DEBUG: FEN parsed successfully - agent count: {len(state.agents)}, factories: {len(state.factories)}")
                
                # Debug: Print factory contents
                print("DEBUG: Factory contents:")
                for i, factory in enumerate(state.factories):
                    print(f"  Factory {i}: {dict(factory.tiles)}")
            else:
                print("DEBUG: ERROR - parse_fen_string returned None!")
                
        except ValueError as e:
            print(f"DEBUG: FEN parsing error: {e}")
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        except Exception as e:
            print(f"DEBUG: Unexpected error parsing FEN: {e}")
            return jsonify({'error': f'Error parsing game state: {str(e)}'}), 500
        
        # Convert frontend move format to engine move format
        try:
            print("DEBUG: About to convert frontend move")
            move_data = request_model.move
            print(f"DEBUG: Frontend move data: {move_data}")
            print(f"DEBUG: Frontend move data type: {type(move_data)}")
            print(f"DEBUG: Frontend move data keys: {move_data.keys() if isinstance(move_data, dict) else 'Not a dict'}")
            
            engine_move = convert_frontend_move_to_engine(move_data)
            print(f"DEBUG: Converted engine move: {engine_move}")
            print(f"DEBUG: Engine move tile_type: {engine_move.get('tile_type')} (should be 0 for blue)")
        except Exception as e:
            print(f"DEBUG: Error converting move: {e}")
            return jsonify({'error': f'Error converting move: {str(e)}'}), 500
        
        # Generate legal moves
        try:
            print("DEBUG: About to generate legal moves")
            print(f"DEBUG: State factories before move generation:")
            for i, factory in enumerate(state.factories):
                print(f"  Factory {i}: {dict(factory.tiles)}")
            print(f"DEBUG: State center pool before move generation: {dict(state.centre_pool.tiles)}")
            
            from core.azul_move_generator import FastMoveGenerator
            generator = FastMoveGenerator()
            legal_moves = generator.generate_moves_fast(state, request_model.agent_id)
            print(f"DEBUG: Generated {len(legal_moves)} legal moves")
            
            # Debug: Print all legal moves to see their format
            print("DEBUG: All legal moves:")
            for i, move in enumerate(legal_moves):
                print(f"  Move {i}: action_type={move.action_type}, source_id={move.source_id}, tile_type={move.tile_type}, pattern_line_dest={move.pattern_line_dest}, num_to_pattern_line={move.num_to_pattern_line}, num_to_floor_line={move.num_to_floor_line}")
                
        except Exception as e:
            print(f"DEBUG: Error generating moves: {e}")
            import traceback
            print(f"DEBUG: Move generation traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Error generating legal moves: {str(e)}'}), 500
        
        # Find matching move
        try:
            print("DEBUG: About to find matching move")
            matching_move = find_matching_move(engine_move, legal_moves)
            print(f"DEBUG: Matching move found: {matching_move}")
            if matching_move:
                print(f"DEBUG: Matching move tile_type: {matching_move.tile_type}")
                print(f"DEBUG: Matching move source_id: {matching_move.source_id}")
                print(f"DEBUG: Matching move pattern_line_dest: {matching_move.pattern_line_dest}")
            if not matching_move:
                print(f"DEBUG: No matching move found. Engine move: {engine_move}")
                return jsonify({'error': 'Illegal move'}), 400
        except Exception as e:
            print(f"DEBUG: Error finding matching move: {e}")
            return jsonify({'error': f'Error validating move: {str(e)}'}), 500
        
        # Apply move using game rule
        try:
            print("DEBUG: About to apply move")
            from core.azul_utils import Action, TileGrab
            
            # Convert FastMove to action format expected by generateSuccessor
            tg = TileGrab()
            tg.tile_type = matching_move.tile_type
            tg.number = matching_move.num_to_pattern_line + matching_move.num_to_floor_line
            tg.pattern_line_dest = matching_move.pattern_line_dest
            tg.num_to_pattern_line = matching_move.num_to_pattern_line
            tg.num_to_floor_line = matching_move.num_to_floor_line
            
            print(f"DEBUG: TileGrab created - tile_type: {tg.tile_type}, number: {tg.number}, pattern_line_dest: {tg.pattern_line_dest}")
            
            if matching_move.action_type == 1:  # Factory move
                action = (Action.TAKE_FROM_FACTORY, matching_move.source_id, tg)
            else:  # Center move
                action = (Action.TAKE_FROM_CENTRE, -1, tg)
            
            print(f"DEBUG: Action created: {action}")
            
            # Apply the move using game rule
            from core.azul_model import AzulGameRule
            game_rule = AzulGameRule(len(state.agents))
            print(f"DEBUG: About to apply move with action: {action}")
            print(f"DEBUG: Action[0] (action_type): {action[0]}")
            print(f"DEBUG: Action[1] (source_id): {action[1]}")
            print(f"DEBUG: Action[2] (tile_grab): {action[2]}")
            print(f"DEBUG: TileGrab tile_type: {action[2].tile_type}")
            print(f"DEBUG: TileGrab number: {action[2].number}")
            print(f"DEBUG: TileGrab pattern_line_dest: {action[2].pattern_line_dest}")
            print(f"DEBUG: TileGrab num_to_pattern_line: {action[2].num_to_pattern_line}")
            print(f"DEBUG: TileGrab num_to_floor_line: {action[2].num_to_floor_line}")
            
            # Debug: Check factory state before move
            print(f"DEBUG: Factory {action[1]} state before move: {dict(state.factories[action[1]].tiles)}")
            print(f"DEBUG: Center pool state before move: {dict(state.centre_pool.tiles)}")
            
            try:
                new_state = game_rule.generateSuccessor(state, action, request_model.agent_id)
                print("DEBUG: Move applied successfully")
                
                # Debug: Check factory state after move
                print(f"DEBUG: Factory {action[1]} state after move: {dict(new_state.factories[action[1]].tiles)}")
                print(f"DEBUG: Center pool state after move: {dict(new_state.centre_pool.tiles)}")
                
                # Debug: Check if tiles were actually moved
                print(f"DEBUG: Tiles moved from factory {action[1]}: {action[2].number} tiles of type {action[2].tile_type}")
                print(f"DEBUG: Tiles to pattern line: {action[2].num_to_pattern_line}")
                print(f"DEBUG: Tiles to floor: {action[2].num_to_floor_line}")
                
            except Exception as e:
                print(f"DEBUG: Error in generateSuccessor: {e}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                raise
            
            # Update the current game state
            update_current_game_state(new_state)
            
            # Convert back to FEN
            new_fen = state_to_fen(new_state)
            print(f"DEBUG: New FEN: {new_fen}")
            
        except Exception as e:
            print(f"DEBUG: Error applying move: {e}")
            return jsonify({'error': f'Error applying move: {str(e)}'}), 500
        
        # Convert the new state to frontend format for immediate use
        game_state = {
            'factories': [],
            'center': [],
            'players': [],
            'fen_string': new_fen
        }
        
        # Convert factories
        for factory in new_state.factories:
            factory_tiles = []
            for tile_type, count in factory.tiles.items():
                for _ in range(count):
                    # Convert tile type to color string
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    factory_tiles.append(tile_colors.get(tile_type, 'W'))
            game_state['factories'].append(factory_tiles)
        
        # Convert center pool
        center_tiles = []
        for tile_type, count in new_state.centre_pool.tiles.items():
            for _ in range(count):
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                center_tiles.append(tile_colors.get(tile_type, 'W'))
        game_state['center'] = center_tiles
        
        # Convert player states
        for agent in new_state.agents:
            player = {
                'pattern_lines': [],
                'wall': [],
                'floor': []
            }
            
            # Convert pattern lines
            for i in range(5):
                line = []
                if agent.lines_tile[i] != -1:
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    tile_color = tile_colors.get(agent.lines_tile[i], 'W')
                    for _ in range(agent.lines_number[i]):
                        line.append(tile_color)
                player['pattern_lines'].append(line)
            
            # Convert wall
            for row in range(5):
                wall_row = []
                for col in range(5):
                    if agent.grid_state[row][col] != 0:
                        tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                        tile_color = tile_colors.get(agent.grid_state[row][col], 'W')
                        wall_row.append(tile_color)
                    else:
                        wall_row.append(False)
                player['wall'].append(wall_row)
            
            # Convert floor
            floor_tiles = []
            for tile_type in agent.floor_tiles:
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                floor_tiles.append(tile_colors.get(tile_type, 'W'))
            player['floor'] = floor_tiles
            
            game_state['players'].append(player)
        
        # Return the actual response with complete game state
        return jsonify({
            'success': True,
            'new_fen': new_fen,
            'fen_string': new_fen,  # Include for consistency
            'game_state': game_state,  # Include complete game state
            'move_executed': format_move(matching_move),
            'game_over': new_state.is_game_over(),
            'scores': [agent.score for agent in new_state.agents],
            'engine_response': None  # Temporarily disabled
        })
        
    except ValidationError as e:
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        import traceback
        print(f"ERROR in execute_move: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to execute move: {str(e)}'}), 500





def convert_frontend_state_to_azul_state(frontend_state):
    """Convert frontend game state to AzulState object."""
    try:
        from core.azul_model import AzulState
        
        # Create a new AzulState
        state = AzulState(2)  # 2-player game
        
        # Convert factories
        if 'factories' in frontend_state:
            print(f"DEBUG: Converting factories from frontend state: {frontend_state['factories']}")
            for i, factory in enumerate(frontend_state['factories']):
                if i < len(state.factories):
                    # Clear existing tiles
                    state.factories[i].tiles.clear()
                    
                    # Add tiles from frontend format
                    if isinstance(factory, list):
                        # New format: array of tile strings
                        tile_counts = {}
                        for tile in factory:
                            tile_type = convert_tile_string_to_type(tile)
                            tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
                            print(f"DEBUG: Converting tile '{tile}' to type {tile_type}")
                        state.factories[i].tiles.update(tile_counts)
                        print(f"DEBUG: Factory {i} converted from list format: {factory} -> {tile_counts}")
                        print(f"DEBUG: Factory {i} final state: {dict(state.factories[i].tiles)}")
                    elif isinstance(factory, dict) and 'tiles' in factory:
                        # Old format: object with tiles
                        for tile_type_str, count in factory['tiles'].items():
                            tile_type = int(tile_type_str)
                            state.factories[i].tiles[tile_type] = count
                        print(f"DEBUG: Factory {i} converted from dict format: {factory} -> {dict(state.factories[i].tiles)}")
                    else:
                        print(f"DEBUG: Factory {i} has unknown format: {factory}")
        
        # Convert center pool
        if 'center' in frontend_state:
            state.centre_pool.tiles.clear()
            center_data = frontend_state['center']
            if isinstance(center_data, dict):
                # Dictionary format: {"0": 2, "1": 1} (tile_type: count)
                for tile_type_str, count in center_data.items():
                    tile_type = int(tile_type_str)
                    state.centre_pool.tiles[tile_type] = count
            elif isinstance(center_data, list):
                # List format: ["B", "B", "Y"] (array of tile strings)
                tile_counts = {}
                for tile in center_data:
                    tile_type = convert_tile_string_to_type(tile)
                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
                state.centre_pool.tiles.update(tile_counts)
        
        # Convert players/agents
        if 'players' in frontend_state:
            for i, player in enumerate(frontend_state['players']):
                if i < len(state.agents):
                    agent = state.agents[i]
                    
                    # Convert pattern lines
                    if 'pattern_lines' in player:
                        for j, pattern_line in enumerate(player['pattern_lines']):
                            if j < len(agent.lines_tile):
                                if isinstance(pattern_line, list) and len(pattern_line) > 0:
                                    # Get tile type from first tile in pattern line
                                    tile_type = convert_tile_string_to_type(pattern_line[0])
                                    agent.lines_tile[j] = tile_type
                                    agent.lines_number[j] = len(pattern_line)
                                else:
                                    agent.lines_tile[j] = -1
                                    agent.lines_number[j] = 0
                    
                    # Convert wall
                    if 'wall' in player:
                        wall_data = player['wall']
                        if isinstance(wall_data, list) and len(wall_data) == 5:
                            for row in range(5):
                                if row < len(agent.grid_state) and len(wall_data[row]) == 5:
                                    for col in range(5):
                                        if col < len(agent.grid_state[row]):
                                            # wall_data[row][col] should be False (empty) or tile color string (has tile)
                                            if wall_data[row][col] and wall_data[row][col] is not False:
                                                # Convert tile color string to tile type
                                                tile_type = convert_tile_string_to_type(wall_data[row][col])
                                                agent.grid_state[row][col] = tile_type
                                            else:
                                                agent.grid_state[row][col] = 0  # Empty
                    
                    # Convert floor tiles
                    if 'floor_tiles' in player:
                        agent.floor_tiles = player['floor_tiles']
                    
                    # Convert score
                    if 'score' in player:
                        agent.score = player['score']
        
        print(f"DEBUG: State conversion completed successfully")
        print(f"DEBUG: Final factory contents:")
        for i, factory in enumerate(state.factories):
            print(f"  Factory {i}: {dict(factory.tiles)}")
        print(f"DEBUG: Final center pool: {dict(state.centre_pool.tiles)}")
        
        return state
        
    except Exception as e:
        print(f"DEBUG: Error converting frontend state: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return None





def state_to_fen(state) -> str:
    """Convert game state to FEN string."""
    global _current_game_state
    
    # If this is the current game state, return a unique identifier
    if state is _current_game_state:
        # Generate a unique state identifier based on the state's content
        # This is a simple hash-based approach for now
        import hashlib
        import json
        
        try:
            # Create a hash of the state's key components using JSON instead of pickle
            state_data = {
                'factories': [(i, dict(factory.tiles)) for i, factory in enumerate(state.factories)],
                'center': dict(state.centre_pool.tiles),
                'agents': [
                    {
                        'lines_tile': agent.lines_tile,
                        'lines_number': agent.lines_number,
                        'grid_state': agent.grid_state,
                        'floor_tiles': agent.floor_tiles,
                        'score': agent.score
                    }
                    for agent in state.agents
                ],
                'current_player': getattr(state, 'current_player', state.first_agent)
            }
            
            # Create a hash of the state data using JSON
            state_json = json.dumps(state_data, sort_keys=True)
            state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
            
            return f"state_{state_hash}"
        except Exception as e:
            # Fallback to a simple timestamp-based identifier if serialization fails
            import time
            timestamp = int(time.time() * 1000) % 1000000
            return f"state_{timestamp}"
    
    # For other states, return "initial" for backward compatibility
    return "initial" 


@api_bp.route('/create_game', methods=['POST'])
def create_game():
    """Create a new game with specified player count."""
    try:
        try:
            data = request.get_json(force=True)
        except Exception:
            data = {}
        
        request_model = GameCreationRequest(**(data or {}))
        
        print(f"DEBUG: Creating new game with {request_model.player_count} players")
        
        # Validate player count - only 2 players supported
        if request_model.player_count != 2:
            return jsonify({'error': 'Only 2-player games are supported'}), 400
        
        # Create new game state
        from core.azul_model import AzulState
        import random
        import time
        
        # Use seed if provided, otherwise use time-based seed
        if request_model.seed is not None:
            random.seed(request_model.seed)
        else:
            # Use a time-based seed for true randomness
            random.seed(int(time.time() * 1000) % 2**32)
        
        # Create new game state
        new_state = AzulState(request_model.player_count)
        
        # Reset the random seed
        random.seed()
        
        # Update global game state
        global _current_game_state, _initial_game_state
        _current_game_state = new_state
        _initial_game_state = copy.deepcopy(new_state)
        
        # Generate a unique identifier for this state
        state_id = f"state_{int(time.time() * 1000) % 1000000}"
        
        return jsonify({
            'success': True,
            'fen_string': state_id,
            'player_count': request_model.player_count,
            'message': f'New {request_model.player_count}-player game created'
        })
        
    except Exception as e:
        print(f"ERROR in create_game: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Game creation failed: {str(e)}'}), 500


@api_bp.route('/game_state', methods=['GET'])
def get_game_state():
    """Get the current game state for display."""
    global _current_editable_game_state, _initial_game_state
    
    try:
        # If we have a stored editable game state, return it with a generated FEN string
        if _current_editable_game_state is not None:
            # Generate a unique FEN string for this state
            import hashlib
            import json
            
            try:
                # Create a hash of the game state
                state_json = json.dumps(_current_editable_game_state, sort_keys=True)
                state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
                unique_fen = f"state_{state_hash}"
                
                # Add the FEN string to the game state
                game_state_with_fen = _current_editable_game_state.copy()
                game_state_with_fen['fen_string'] = unique_fen
                
                return jsonify({
                    'success': True,
                    'game_state': game_state_with_fen
                })
            except Exception as e:
                print(f"Warning: Failed to generate FEN for editable state: {e}")
                # Fallback to returning without FEN
                return jsonify({
                    'success': True,
                    'game_state': _current_editable_game_state
                })
        
        # Otherwise, parse current state from FEN
        fen_string = request.args.get('fen_string', 'initial')
        try:
            state = parse_fen_string(fen_string)
        except ValueError:
            # For invalid FEN, return default initial state with consistent seed
            from core.azul_model import AzulState
            import random
            
            # Use fixed seed for consistent initial state
            random.seed(42)
            state = AzulState(2)
            random.seed()  # Reset to random seed
            
            # Store this as the initial state for future use
            if _initial_game_state is None:
                _initial_game_state = copy.deepcopy(state)
        
        # Convert state to frontend format
        game_state = {
            'factories': [],
            'center': [],
            'players': [],
            'fen_string': state_to_fen(state)  # Include current FEN string
        }
        
        # Convert factories
        for factory in state.factories:
            factory_tiles = []
            for tile_type, count in factory.tiles.items():
                for _ in range(count):
                    # Convert tile type to color string
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    factory_tiles.append(tile_colors.get(tile_type, 'W'))
            game_state['factories'].append(factory_tiles)
        
        # Convert center pool
        center_tiles = []
        for tile_type, count in state.centre_pool.tiles.items():
            for _ in range(count):
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                center_tiles.append(tile_colors.get(tile_type, 'W'))
        game_state['center'] = center_tiles
        
        # Convert player states
        for agent in state.agents:
            player = {
                'pattern_lines': [],
                'wall': [],
                'floor': []
            }
            
            # Convert pattern lines
            for i in range(5):
                line = []
                if agent.lines_tile[i] != -1:
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    tile_color = tile_colors.get(agent.lines_tile[i], 'W')
                    for _ in range(agent.lines_number[i]):
                        line.append(tile_color)
                player['pattern_lines'].append(line)
            
            # Convert wall
            for row in range(5):
                wall_row = []
                for col in range(5):
                    if agent.grid_state[row][col] != 0:
                        tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                        tile_color = tile_colors.get(agent.grid_state[row][col], 'W')
                        wall_row.append(tile_color)
                    else:
                        wall_row.append(False)
                player['wall'].append(wall_row)
            
            # Convert floor
            floor_tiles = []
            for tile_type in agent.floor_tiles:
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                floor_tiles.append(tile_colors.get(tile_type, 'W'))
            player['floor'] = floor_tiles
            
            game_state['players'].append(player)
        
        return jsonify({
            'success': True,
            'game_state': game_state
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get game state: {str(e)}'
        }), 500


@api_bp.route('/game_state', methods=['PUT'])
def put_game_state():
    """Update the current game state from frontend."""
    global _current_editable_game_state
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        fen_string = data.get('fen_string', 'initial')
        game_state = data.get('game_state')
        
        if not game_state:
            return jsonify({'error': 'No game_state provided'}), 400
        
        # Generate a unique FEN string for this state
        import hashlib
        import json
        import time
        
        try:
            # Create a hash of the game state
            state_json = json.dumps(game_state, sort_keys=True)
            state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
            unique_fen = f"state_{state_hash}"
        except Exception as e:
            # Fallback to timestamp-based identifier
            timestamp = int(time.time() * 1000) % 1000000
            unique_fen = f"state_{timestamp}"
        
        # Store the game state for future retrieval
        _current_editable_game_state = game_state
        
        return jsonify({
            'success': True,
            'message': 'Game state saved successfully',
            'fen_string': unique_fen
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to save game state: {str(e)}'
        }), 500


@api_bp.route('/reset_game', methods=['POST'])
def reset_game():
    """Reset the current game state to initial position."""
    global _current_game_state, _initial_game_state, _current_editable_game_state
    from core.azul_model import AzulState
    
    # Reset to the consistent initial state
    if _initial_game_state is None:
        random.seed(42)
        _initial_game_state = AzulState(2)
        random.seed()
    
    _current_game_state = copy.deepcopy(_initial_game_state)
    
    # Clear the editable game state so it falls back to the initial state
    _current_editable_game_state = None
    
    return jsonify({
        'success': True,
        'message': 'Game reset to initial position'
    }) 


@api_bp.route('/analyze_game', methods=['POST'])
@require_session
def analyze_game():
    """Analyze a complete game for blunders and insights."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'game_data' not in data:
            return jsonify({'success': False, 'error': 'Missing game_data field'}), 400
        
        request_model = GameAnalysisRequest(**data)
        
        game_data = request_model.game_data
        moves = game_data.get('moves', [])
        analysis_results = []
        
        print(f"DEBUG: Analyzing game with {len(moves)} moves")
        
        for i, move_data in enumerate(moves):
            # Get position before move
            position = move_data.get('position_before', 'initial')
            
            # Analyze position
            try:
                analysis = analyze_position_internal(position, move_data['player'], request_model.analysis_depth)
                
                # Calculate blunder severity
                actual_move_score = analysis.get('move_scores', {}).get(str(move_data['move']), 0)
                best_move_score = analysis.get('best_score', 0)
                blunder_severity = best_move_score - actual_move_score
                
                analysis_results.append({
                    'move_index': i,
                    'player': move_data['player'],
                    'move': move_data['move'],
                    'position': position,
                    'analysis': analysis,
                    'blunder_severity': blunder_severity,
                    'is_blunder': blunder_severity >= 3.0
                })
                
                print(f"DEBUG: Move {i+1} - Blunder severity: {blunder_severity:.2f}")
                
            except Exception as e:
                print(f"DEBUG: Error analyzing move {i+1}: {e}")
                analysis_results.append({
                    'move_index': i,
                    'player': move_data['player'],
                    'move': move_data['move'],
                    'position': position,
                    'analysis': None,
                    'blunder_severity': 0,
                    'is_blunder': False,
                    'error': str(e)
                })
        
        # Calculate game summary
        blunders = [r for r in analysis_results if r.get('is_blunder', False)]
        total_blunder_severity = sum(r.get('blunder_severity', 0) for r in analysis_results)
        avg_blunder_severity = total_blunder_severity / len(analysis_results) if analysis_results else 0
        
        summary = {
            'total_moves': len(moves),
            'blunder_count': len(blunders),
            'blunder_percentage': (len(blunders) / len(moves)) * 100 if moves else 0,
            'average_blunder_severity': avg_blunder_severity,
            'worst_blunder': max((r.get('blunder_severity', 0) for r in analysis_results), default=0),
            'players': game_data.get('players', ['Player 1', 'Player 2']),
            'game_result': game_data.get('result', {})
        }
        
        return jsonify({
            'success': True,
            'analysis_results': analysis_results,
            'summary': summary
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to analyze game: {str(e)}'}), 500


@api_bp.route('/upload_game_log', methods=['POST'])
@require_session
def upload_game_log():
    """Upload and parse a game log file."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'game_format' not in data:
            return jsonify({'success': False, 'error': 'Missing game_format field'}), 400
        if 'game_content' not in data:
            return jsonify({'success': False, 'error': 'Missing game_content field'}), 400
        
        request_model = GameLogUploadRequest(**data)
        
        # Parse game log based on format
        try:
            game_data = parse_game_log(request_model.game_content, request_model.game_format)
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Invalid game format: {str(e)}'}), 400
        
        # Store in database for later analysis
        game_id = f"game_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Store game data in database
        if not current_app.database:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        try:
            with current_app.database.get_connection() as conn:
                conn.execute("""
                    INSERT INTO game_analyses (game_id, players, total_moves, game_data, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    game_id,
                    json.dumps(game_data.get('players', [])),
                    len(game_data.get('moves', [])),
                    json.dumps(game_data),
                    time.time()
                ))
                conn.commit()
        except Exception as e:
            print(f"DEBUG: Error storing game data: {e}")
            return jsonify({'success': False, 'error': f'Failed to store game data: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'parsed_data': game_data
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in upload_game_log: {e}")
        return jsonify({'success': False, 'error': f'Failed to upload game log: {str(e)}'}), 500


@api_bp.route('/game_analysis/<game_id>', methods=['GET'])
@require_session
def get_game_analysis(game_id: str):
    """Get analysis results for a specific game."""
    try:
        if not current_app.database:
            return jsonify({'error': 'Database not available'}), 503
        
        with current_app.database.get_connection() as conn:
            result = conn.execute("""
                SELECT game_data, analysis_data, created_at
                FROM game_analyses 
                WHERE game_id = ?
            """, (game_id,)).fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        game_data = json.loads(result[0])
        analysis_data = json.loads(result[1]) if result[1] else None
        created_at = result[2]
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'game_data': game_data,
            'game_analysis': analysis_data,
            'created_at': created_at
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get game analysis: {str(e)}'}), 500


@api_bp.route('/game_analyses', methods=['GET'])
@require_session
def search_game_analyses():
    """Search for game analyses."""
    try:
        # Parse query parameters
        player_names = request.args.getlist('player_names')
        min_blunders = request.args.get('min_blunders', type=int)
        max_blunders = request.args.get('max_blunders', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not current_app.database:
            return jsonify({'error': 'Database not available'}), 503
        
        with current_app.database.get_connection() as conn:
            # Build query
            query = "SELECT game_id, players, total_moves, blunder_count, created_at FROM game_analyses WHERE 1=1"
            params = []
            
            if min_blunders is not None:
                query += " AND blunder_count >= ?"
                params.append(min_blunders)
            
            if max_blunders is not None:
                query += " AND blunder_count <= ?"
                params.append(max_blunders)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            results = conn.execute(query, params).fetchall()
        
        games = []
        for row in results:
            games.append({
                'game_id': row[0],
                'players': json.loads(row[1]),
                'total_moves': row[2],
                'blunder_count': row[3],
                'created_at': row[4]
            })
        
        return jsonify({
            'success': True,
            'game_analyses': games,
            'total': len(games)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to search game analyses: {str(e)}'}), 500


# D6: Opening Explorer endpoints
@api_bp.route('/similar_positions', methods=['POST'])
@require_session
def find_similar_positions():
    """Find positions similar to the given position."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'fen_string' not in data:
            return jsonify({'success': False, 'error': 'Missing fen_string field'}), 400
        
        request_model = SimilarPositionRequest(**data)
        
        if not current_app.database:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        # Get position hash
        position_hash = hash_position(request_model.fen_string)
        
        # Find similar positions
        similar_positions = find_similar_positions_internal(
            position_hash, 
            request_model.similarity_threshold, 
            request_model.limit
        )
        
        return jsonify({
            'success': True,
            'similar_positions': similar_positions
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in find_similar_positions: {e}")
        return jsonify({'success': False, 'error': f'Failed to find similar positions: {str(e)}'}), 500


@api_bp.route('/popular_continuations', methods=['POST'])
@require_session
def get_popular_continuations():
    """Get popular continuations for a position."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'fen_string' not in data:
            return jsonify({'success': False, 'error': 'Missing fen_string field'}), 400
        
        request_model = ContinuationRequest(**data)
        
        continuations = get_popular_continuations_internal(
            request_model.fen_string, 
            request_model.limit
        )
        
        # Check if position exists in database
        if not current_app.database:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        with current_app.database.get_connection() as conn:
            position_exists = conn.execute("""
                SELECT id FROM position_database WHERE fen_string = ?
            """, (request_model.fen_string,)).fetchone()
        
        if not position_exists:
            return jsonify({'success': False, 'error': 'Position not found'}), 404
        
        return jsonify({
            'success': True,
            'continuations': continuations
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in get_popular_continuations: {e}")
        return jsonify({'success': False, 'error': f'Failed to get continuations: {str(e)}'}), 500


@api_bp.route('/add_to_database', methods=['POST'])
@require_session
def add_position_to_database():
    """Add a position to the opening database."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'fen_string' not in data:
            return jsonify({'success': False, 'error': 'Missing fen_string field'}), 400
        
        request_model = PositionDatabaseRequest(**data)
        
        result = add_position_to_database_internal(
            request_model.fen_string,
            request_model.metadata,
            request_model.frequency
        )
        
        return jsonify({
            'success': True,
            'position_id': result['position_id'],
            'action': result['action']
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in add_position_to_database: {e}")
        return jsonify({'success': False, 'error': f'Failed to add position: {str(e)}'}), 500


def analyze_position_internal(fen_string: str, agent_id: int, depth: int = 3) -> Dict[str, Any]:
    """Internal function to analyze a position."""
    try:
        # Parse position
        state = parse_fen_string(fen_string)
        
        # Get legal moves
        from core.azul_move_generator import FastMoveGenerator
        generator = FastMoveGenerator()
        legal_moves = generator.generate_moves_fast(state, agent_id)
        
        # Analyze with alpha-beta search
        from core.azul_search import AzulAlphaBetaSearch
        searcher = AzulAlphaBetaSearch()
        
        start_time = time.time()
        result = searcher.search(state, depth, agent_id)
        search_time = time.time() - start_time
        
        # Format move scores
        move_scores = {}
        for move in legal_moves:
            move_key = f"{move.source_id}_{move.tile_type}_{move.pattern_line_dest}_{move.num_to_pattern_line}_{move.num_to_floor_line}"
            move_scores[move_key] = 0  # Placeholder - would need to evaluate each move
        
        return {
            'best_move': format_move(result.best_move) if result.best_move else None,
            'best_score': result.best_score,
            'search_time': search_time,
            'nodes_searched': result.nodes_searched,
            'depth_reached': result.depth_reached,
            'move_scores': move_scores
        }
        
    except Exception as e:
        print(f"DEBUG: Error in analyze_position_internal: {e}")
        return {
            'best_move': None,
            'best_score': 0,
            'search_time': 0,
            'nodes_searched': 0,
            'depth_reached': 0,
            'move_scores': {},
            'error': str(e)
        }


def parse_game_log(content: str, format_type: str) -> Dict[str, Any]:
    """Parse game log content based on format."""
    if format_type == 'json':
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format: {content}")
    elif format_type == 'text':
        return parse_text_game_log(content)
    else:
        raise ValueError(f"Unsupported game format: {format_type}")


def parse_text_game_log(content: str) -> Dict[str, Any]:
    """Parse plain text game log format."""
    lines = content.split('\n')
    game_info = {}
    moves = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Parse game info
        if line.startswith('Game:'):
            game_info['players'] = line.replace('Game:', '').strip().split(' vs ')
        elif line.startswith('Date:'):
            game_info['date'] = line.replace('Date:', '').strip()
        elif line.startswith('Result:'):
            game_info['result'] = line.replace('Result:', '').strip()
        elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
            # Parse move
            parts = line.split(':', 1)
            if len(parts) == 2:
                move_num = int(parts[0].replace('.', ''))
                move_desc = parts[1].strip()
                
                # Parse move description (simplified)
                move_data = parse_move_description(move_desc)
                if move_data:
                    moves.append({
                        'player': (move_num - 1) % 2,  # Alternate players
                        'move': move_data,
                        'description': move_desc,
                        'position_before': 'initial',  # Would need to reconstruct
                        'position_after': 'initial'    # Would need to reconstruct
                    })
    
    return {
        'players': game_info.get('players', ['Player 1', 'Player 2']),
        'date': game_info.get('date', ''),
        'result': game_info.get('result', ''),
        'moves': moves
    }


def parse_move_description(desc: str) -> Optional[Dict[str, Any]]:
    """Parse a move description into move data."""
    desc = desc.lower()
    
    # Extract tile color
    tile_colors = {'blue': 0, 'yellow': 1, 'red': 2, 'black': 3, 'white': 4}
    tile_type = None
    for color, tile_id in tile_colors.items():
        if color in desc:
            tile_type = tile_id
            break
    
    if tile_type is None:
        return None
    
    # Extract source (factory or center)
    source_id = -1  # Default to center
    if 'factory' in desc:
        # Extract factory number
        import re
        factory_match = re.search(r'factory (\d+)', desc)
        if factory_match:
            source_id = int(factory_match.group(1))
    
    # Extract destination
    pattern_line_dest = -1
    if 'pattern line' in desc:
        import re
        line_match = re.search(r'pattern line (\d+)', desc)
        if line_match:
            pattern_line_dest = int(line_match.group(1))
    
    return {
        'source_id': source_id,
        'tile_type': tile_type,
        'pattern_line_dest': pattern_line_dest,
        'num_to_pattern_line': 1,
        'num_to_floor_line': 0
    }


# D6: Opening Explorer helper functions
def hash_position(fen_string: str) -> str:
    """Create a hash for a position."""
    # Simple hash based on FEN string
    import hashlib
    return hashlib.md5(fen_string.encode()).hexdigest()[:16]


def find_similar_positions_internal(position_hash: str, threshold: float, limit: int) -> List[Dict[str, Any]]:
    """Find positions similar to the given position hash."""
    try:
        from flask import current_app
        if not current_app.database:
            return []
        
        # Get all positions from database
        with current_app.database.get_connection() as conn:
            results = conn.execute("""
                SELECT fen_string, frequency, metadata, created_at
                FROM position_database
                ORDER BY frequency DESC
                LIMIT ?
            """, (limit * 10,)).fetchall()  # Get more to filter by similarity
        
        similar_positions = []
        for row in results:
            fen_string = row[0]
            frequency = row[1]
            metadata = json.loads(row[2]) if row[2] else {}
            created_at = row[3]
            
            # Calculate similarity
            similarity = calculate_position_similarity(position_hash, hash_position(fen_string))
            
            if similarity >= threshold:
                similar_positions.append({
                    'fen_string': fen_string,
                    'frequency': frequency,
                    'similarity': similarity,
                    'metadata': metadata,
                    'created_at': created_at
                })
        
        # Sort by similarity and limit
        similar_positions.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_positions[:limit]
        
    except Exception as e:
        print(f"DEBUG: Error finding similar positions: {e}")
        return []


def get_popular_continuations_internal(fen_string: str, limit: int) -> List[Dict[str, Any]]:
    """Get popular continuations for a position."""
    try:
        from flask import current_app
        if not current_app.database:
            return []
        
        # Get continuations for this position
        with current_app.database.get_connection() as conn:
            results = conn.execute("""
                SELECT pc.move_data, pc.frequency, pc.win_rate
                FROM position_continuations pc
                JOIN position_database pd ON pc.position_id = pd.id
                WHERE pd.fen_string = ?
                ORDER BY pc.frequency DESC
                LIMIT ?
            """, (fen_string, limit)).fetchall()
        
        continuations = []
        for row in results:
            move_data = json.loads(row[0])
            frequency = row[1]
            win_rate = row[2]
            
            continuations.append({
                'move': move_data,
                'frequency': frequency,
                'win_rate': win_rate,
                'description': str(move_data)
            })
        
        return continuations
        
    except Exception as e:
        print(f"DEBUG: Error getting continuations: {e}")
        return []


def add_position_to_database_internal(fen_string: str, metadata: Optional[Dict[str, Any]], frequency: int) -> Dict[str, Any]:
    """Add a position to the opening database."""
    try:
        from flask import current_app
        if not current_app.database:
            raise Exception("Database not available")
        
        # Check if position already exists
        with current_app.database.get_connection() as conn:
            existing = conn.execute("""
                SELECT id, frequency FROM position_database WHERE fen_string = ?
            """, (fen_string,)).fetchone()
            
            if existing:
                # Update frequency
                new_frequency = existing[1] + frequency
                conn.execute("""
                    UPDATE position_database 
                    SET frequency = ?, metadata = ?
                    WHERE id = ?
                """, (new_frequency, json.dumps(metadata or {}), existing[0]))
                conn.commit()
                return {
                    'position_id': existing[0],
                    'action': 'updated',
                    'new_frequency': new_frequency
                }
            else:
                # Insert new position
                result = conn.execute("""
                    INSERT INTO position_database (fen_string, frequency, metadata, created_at)
                    VALUES (?, ?, ?, ?)
                """, (fen_string, frequency, json.dumps(metadata or {}), time.time()))
                position_id = result.lastrowid
                conn.commit()
                return {
                    'position_id': position_id,
                    'action': 'created'
                }
        
    except Exception as e:
        print(f"DEBUG: Error adding position to database: {e}")
        raise e


def calculate_position_similarity(hash1: str, hash2: str) -> float:
    """Calculate similarity between two position hashes."""
    # Simple similarity based on hash comparison
    # In practice, this would be more sophisticated
    matches = 0
    for i in range(min(len(hash1), len(hash2))):
        if hash1[i] == hash2[i]:
            matches += 1
    return matches / max(len(hash1), len(hash2))


# Neural Training Request Models



# Neural Training API Endpoints
@api_bp.route('/neural/train', methods=['POST'])
def start_neural_training():
    """Start neural network training in background with enhanced monitoring."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate request data
        try:
            training_request = NeuralTrainingRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid training configuration', 'details': e.errors()}), 400
        
        # Check if neural components are available
        try:
            from neural.train import TrainingConfig, AzulNetTrainer
        except ImportError:
            return jsonify({
                'error': 'Neural training not available',
                'message': 'PyTorch and neural components are not installed. Install with: pip install torch'
            }), 503
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create database session only (no in-memory session)
        from core.azul_database import NeuralTrainingSession
        db_session = NeuralTrainingSession(
            session_id=session_id,
            status='starting',
            progress=0,
            start_time=datetime.now(),
            config=training_request.dict(),
            logs=['Training session created'],
            error=None,
            results=None,
            loss_history=[],
            epoch_history=[],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            estimated_total_time=None,
            current_epoch=0,
            total_epochs=training_request.epochs,
            created_at=datetime.now(),
            metadata={
                'device': training_request.device,
                'config_size': training_request.config,
                'epochs': training_request.epochs,
                'samples': training_request.samples,
                'batch_size': training_request.batch_size,
                'learning_rate': training_request.learning_rate
            }
        )
        db.save_neural_training_session(db_session)
        
        # Start training in background thread
        def train_in_background():
            try:
                # Update status to running
                db_session = db.get_neural_training_session(session_id)
                if not db_session:
                    return
                
                db_session.status = 'running'
                db_session.logs.append('Training started')
                db.save_neural_training_session(db_session)
                
                # Configuration based on size
                if training_request.config == 'small':
                    hidden_size = 64
                    num_layers = 2
                elif training_request.config == 'medium':
                    hidden_size = 128
                    num_layers = 3
                else:  # large
                    hidden_size = 256
                    num_layers = 4
                
                # Create training config
                train_config = TrainingConfig(
                    batch_size=training_request.batch_size,
                    learning_rate=training_request.learning_rate,
                    num_epochs=training_request.epochs,
                    num_samples=training_request.samples,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    device=training_request.device
                )
                
                # Create custom trainer with progress callbacks
                class MonitoredTrainer(AzulNetTrainer):
                    def __init__(self, config, session_id, db):
                        super().__init__(config)
                        self.session_id = session_id
                        self.db = db
                        self.epoch_count = 0
                    
                    def _train_epoch(self, states, policy_targets, value_targets):
                        """Override to add progress monitoring."""
                        # Get current session from database
                        db_session = self.db.get_neural_training_session(self.session_id)
                        if not db_session:
                            raise InterruptedError("Session not found")
                        
                        # Check if stop requested
                        if db_session.status == 'stopped':
                            raise InterruptedError("Training stopped by user")
                        
                        # Get resource usage
                        resources = get_process_resources()
                        db_session.cpu_usage.append(resources['cpu_percent'])
                        db_session.memory_usage.append(resources['memory_percent'])
                        
                        # Train epoch
                        loss = super()._train_epoch(states, policy_targets, value_targets)
                        
                        # Update progress
                        self.epoch_count += 1
                        progress = min(80, (self.epoch_count / train_config.num_epochs) * 80)
                        
                        # Update database session with progress
                        db_session.progress = int(progress)
                        db_session.current_epoch = self.epoch_count
                        db_session.loss_history.append(loss)
                        db_session.epoch_history.append(self.epoch_count)
                        db_session.timestamp_history.append(datetime.now().isoformat())
                        
                        # Save progress to database
                        self.db.save_neural_training_session(db_session)
                        
                        return loss
                
                # Train model with monitoring
                trainer = MonitoredTrainer(train_config, session_id, db)
                losses = trainer.train()
                
                # Get final session and update with completion
                db_session = db.get_neural_training_session(session_id)
                if db_session:
                    db_session.logs.append(f'Training completed with {len(losses)} epochs')
                    db_session.progress = 80
                    db.save_neural_training_session(db_session)
                
                # Evaluate
                eval_results = trainer.evaluate(num_samples=50)
                if db_session:
                    db_session.logs.append('Evaluation completed')
                    db_session.progress = 90
                    db.save_neural_training_session(db_session)
                
                # Save model
                import os
                os.makedirs("models", exist_ok=True)
                model_path = f"models/azul_net_{training_request.config}.pth"
                trainer.save_model(model_path)
                
                # Final update with completed status
                if db_session:
                    db_session.logs.append(f'Model saved to {model_path}')
                    db_session.progress = 100
                    db_session.status = 'completed'
                    db_session.end_time = datetime.now()
                    db_session.results = {
                        'final_loss': losses[-1] if losses else 0.0,
                        'evaluation_error': eval_results.get('avg_value_error', 0.0),
                        'model_path': model_path,
                        'config': training_request.config,
                        'epochs': training_request.epochs,
                        'samples': training_request.samples
                    }
                    
                    # Update metadata with final results
                    if not db_session.metadata:
                        db_session.metadata = {}
                    db_session.metadata.update({
                        'final_loss': losses[-1] if losses else 0.0,
                        'evaluation_error': eval_results.get('avg_value_error', 0.0),
                        'model_path': model_path
                    })
                    
                    db.save_neural_training_session(db_session)
                
            except InterruptedError:
                # Update database with stopped status
                db_session = db.get_neural_training_session(session_id)
                if db_session:
                    db_session.status = 'stopped'
                    db_session.logs.append('Training stopped by user')
                    db_session.end_time = datetime.now()
                    db.save_neural_training_session(db_session)
                
            except Exception as e:
                # Update database with failed status
                db_session = db.get_neural_training_session(session_id)
                if db_session:
                    db_session.status = 'failed'
                    db_session.error = str(e)
                    db_session.logs.append(f'Error: {str(e)}')
                    db_session.end_time = datetime.now()
                    db.save_neural_training_session(db_session)
        
        # Start background thread
        thread = threading.Thread(target=train_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Training started in background',
            'session_id': session_id,
            'status': 'starting'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@api_bp.route('/neural/status/<session_id>', methods=['GET'])
def get_training_status(session_id):
    """Get enhanced training status for a session with loss history and resource monitoring."""
    try:
        # Get session from database
        db_session = db.get_neural_training_session(session_id)
        if not db_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Convert database session to API response format
        response_data = {
            'session_id': db_session.session_id,
            'status': db_session.status,
            'progress': db_session.progress,
            'start_time': db_session.start_time.isoformat() if db_session.start_time else None,
            'end_time': db_session.end_time.isoformat() if db_session.end_time else None,
            'config': db_session.config if isinstance(db_session.config, dict) else {},
            'logs': db_session.logs if isinstance(db_session.logs, list) else [],
            'error': db_session.error,
            'results': db_session.results if isinstance(db_session.results, dict) else None,
            'metadata': db_session.metadata if isinstance(db_session.metadata, dict) else {},
            # Enhanced monitoring fields
            'loss_history': db_session.loss_history if db_session.loss_history else [],
            'epoch_history': db_session.epoch_history if db_session.epoch_history else [],
            'timestamp_history': db_session.timestamp_history if db_session.timestamp_history else [],
            'cpu_usage': db_session.cpu_usage if db_session.cpu_usage else [],
            'memory_usage': db_session.memory_usage if db_session.memory_usage else [],
            'gpu_usage': db_session.gpu_usage if db_session.gpu_usage else [],
            'estimated_total_time': db_session.estimated_total_time,
            'current_epoch': db_session.current_epoch,
            'total_epochs': db_session.total_epochs
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get session status',
            'message': str(e)
        }), 500


@api_bp.route('/neural/stop/<session_id>', methods=['POST'])
def stop_training(session_id):
    """Stop training for a session."""
    try:
        # Get session from database
        db_session = db.get_neural_training_session(session_id)
        if not db_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update session status to stopped
        db_session.status = 'stopped'
        db_session.logs.append('Stop requested - training will terminate gracefully')
        
        # Save updated session to database
        db.save_neural_training_session(db_session)
        
        return jsonify({
            'success': True,
            'message': 'Training stop requested',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to stop training',
            'message': str(e)
        }), 500


@api_bp.route('/neural/evaluate', methods=['POST'])
def evaluate_neural_model():
    """Evaluate a trained neural model."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate request data
        try:
            eval_request = NeuralEvaluationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid evaluation configuration', 'details': e.errors()}), 400
        
        # Check if neural components are available
        try:
            from neural.evaluate import EvaluationConfig, AzulModelEvaluator
        except ImportError:
            return jsonify({
                'error': 'Neural evaluation not available',
                'message': 'PyTorch and neural components are not installed. Install with: pip install torch'
            }), 503
        
        # Check if model exists
        import os
        if not os.path.exists(eval_request.model):
            return jsonify({
                'error': 'Model not found',
                'message': f'Model file {eval_request.model} does not exist'
            }), 404
        
        # Create evaluation configuration
        config = EvaluationConfig(
            num_positions=eval_request.positions,
            num_games=eval_request.games,
            search_time=0.5,
            max_rollouts=50,
            model_path=eval_request.model,
            device=eval_request.device,
            compare_heuristic=True,
            compare_random=True
        )
        
        # Generate session ID for this evaluation
        import uuid
        session_id = f"eval_{uuid.uuid4().hex[:8]}"
        
        # Create evaluation session
        # Convert config to dict and remove non-serializable fields
        config_dict = asdict(config)
        if 'progress_callback' in config_dict:
            del config_dict['progress_callback']
        evaluation_sessions[session_id] = {
            'status': 'running',
            'progress': 0,
            'start_time': time.time(),
            'config': config_dict,
            'results': None,
            'error': None
        }
        
        # Run evaluation in background
        def evaluate_in_background():
            try:
                def progress_callback(percent):
                    evaluation_sessions[session_id]['progress'] = percent
                config.progress_callback = progress_callback
                evaluator = AzulModelEvaluator(config)
                results = evaluator.evaluate_model()
                evaluation_sessions[session_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'results': results,
                    'end_time': time.time()
                })
            except Exception as e:
                evaluation_sessions[session_id].update({
                    'status': 'failed',
                    'error': str(e),
                    'end_time': time.time()
                })
        
        # Start background thread
        import threading
        thread = threading.Thread(target=evaluate_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Evaluation started in background',
            'session_id': session_id,
            'status_url': f'/api/v1/neural/evaluate/status/{session_id}'
        })
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@api_bp.route('/neural/evaluate/status/<session_id>', methods=['GET'])
def get_evaluation_status(session_id):
    """Get evaluation status for a specific session."""
    try:
        if session_id not in evaluation_sessions:
            return jsonify({
                'error': 'Session not found',
                'message': f'Evaluation session {session_id} does not exist'
            }), 404
        
        session = evaluation_sessions[session_id]
        
        # Calculate elapsed time
        elapsed_time = time.time() - session['start_time']
        
        response = {
            'session_id': session_id,
            'status': session['status'],
            'progress': session['progress'],
            'elapsed_time': round(elapsed_time, 2),
            'start_time': session['start_time']
        }
        
        if session['status'] == 'completed':
            response['results'] = session['results']
            response['end_time'] = session['end_time']
            response['total_time'] = round(session['end_time'] - session['start_time'], 2)
        elif session['status'] == 'failed':
            response['error'] = session['error']
            response['end_time'] = session['end_time']
            response['total_time'] = round(session['end_time'] - session['start_time'], 2)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get evaluation status',
            'message': str(e)
        }), 500


@api_bp.route('/neural/models', methods=['GET'])
def get_available_models():
    """Get list of available trained models."""
    try:
        import os
        import glob
        
        models_dir = "models"
        if not os.path.exists(models_dir):
            return jsonify({
                'models': [],
                'message': 'No models directory found'
            })
        
        # Find all .pth files
        model_files = glob.glob(os.path.join(models_dir, "*.pth"))
        models = []
        
        for model_path in model_files:
            filename = os.path.basename(model_path)
            size = os.path.getsize(model_path)
            models.append({
                'name': filename,
                'path': model_path,
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2)
            })
        
        return jsonify({
            'models': models,
            'count': len(models)
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get models',
            'message': str(e)
        }), 500


@api_bp.route('/neural/config', methods=['GET'])
def get_neural_config():
    """Get current neural training configuration."""
    try:
        # Return default configuration
        config = {
            'config': 'small',
            'device': 'cpu',
            'epochs': 5,
            'samples': 500,
            'batch_size': 16,
            'learning_rate': 0.001,
            'available_configs': ['small', 'medium', 'large'],
            'available_devices': ['cpu', 'cuda']
        }
        
        return jsonify(config)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get configuration',
            'message': str(e)
        }), 500


@api_bp.route('/neural/config', methods=['POST'])
def save_neural_config():
    """Save neural training configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate request data
        try:
            config_request = NeuralConfigRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid configuration', 'details': e.errors()}), 400
        
        # In a real implementation, this would save to a config file or database
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to save configuration',
            'message': str(e)
        }), 500


@api_bp.route('/neural/status', methods=['GET'])
def get_neural_status():
    """Get neural training status."""
    try:
        # Check if neural components are available
        neural_available = False
        pytorch_version = None
        cuda_available = False
        
        try:
            import torch
            pytorch_version = torch.__version__
            
            # Try to import neural modules
            try:
                from neural.train import TrainingConfig, AzulNetTrainer
                neural_available = True
            except ImportError as e:
                print(f"Warning: Neural modules not available: {e}")
                neural_available = False
            
            # Check CUDA availability (this can sometimes cause issues)
            try:
                cuda_available = torch.cuda.is_available()
            except Exception as e:
                print(f"Warning: CUDA check failed: {e}")
                cuda_available = False
                
        except ImportError as e:
            print(f"Warning: PyTorch not available: {e}")
            neural_available = False
        except Exception as e:
            print(f"Warning: PyTorch initialization failed: {e}")
            neural_available = False
        
        # Check available models
        import os
        import glob
        models_dir = "models"
        model_count = 0
        try:
            if os.path.exists(models_dir):
                model_files = glob.glob(os.path.join(models_dir, "*.pth"))
                model_count = len(model_files)
        except Exception as e:
            print(f"Warning: Model directory check failed: {e}")
            model_count = 0
        
        status = {
            'neural_available': neural_available,
            'model_count': model_count,
            'pytorch_version': pytorch_version,
            'cuda_available': cuda_available
        }
        
        return jsonify(status)
        
    except Exception as e:
        print(f"Error in get_neural_status: {e}")
        return jsonify({
            'error': 'Failed to get status',
            'message': str(e)
        }), 500


def calculate_position_similarity(hash1: str, hash2: str) -> float:
    """Calculate similarity between two position hashes."""
    # Simple similarity based on hash comparison
    # In practice, this would be more sophisticated
    matches = 0
    for i in range(min(len(hash1), len(hash2))):
        if hash1[i] == hash2[i]:
            matches += 1
    return matches / max(len(hash1), len(hash2))


def get_system_resources():
    """Get current system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Try to get GPU usage if available
        gpu_percent = None
        try:
            import torch
            if torch.cuda.is_available():
                gpu_percent = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
        except ImportError:
            pass
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_used_gb': memory.used / (1024**3),
            'memory_total_gb': memory.total / (1024**3),
            'gpu_percent': gpu_percent
        }
    except Exception as e:
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_gb': 0.0,
            'memory_total_gb': 0.0,
            'gpu_percent': None,
            'error': str(e)
        }


def get_process_resources():
    """Get current process resource usage."""
    try:
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_used_mb': memory_info.rss / (1024**2),
            'threads': process.num_threads()
        }
    except Exception as e:
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_mb': 0.0,
            'threads': 0,
            'error': str(e)
        }


@api_bp.route('/neural/sessions', methods=['GET'])
def get_all_training_sessions():
    """Get all training sessions from database."""
    try:
        # Get query parameters for filtering
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get sessions from database
        db_sessions = db.get_all_neural_training_sessions(
            status=status,
            limit=limit,
            offset=offset
        )
        
        # Convert database sessions to API response format
        sessions = []
        for db_session in db_sessions:
            session_data = {
                'session_id': db_session.session_id,
                'status': db_session.status,
                'progress': db_session.progress,
                'start_time': db_session.created_at.isoformat() if db_session.created_at else None,
                'end_time': db_session.updated_at.isoformat() if db_session.updated_at else None,
                'config': json.loads(db_session.config) if db_session.config else {},
                'logs': json.loads(db_session.logs) if db_session.logs else [],
                'error': db_session.error,
                'results': json.loads(db_session.results) if db_session.results else None,
                'metadata': json.loads(db_session.metadata) if db_session.metadata else {}
            }
            sessions.append(session_data)
        
        # Get total count for pagination
        all_sessions = db.get_all_neural_training_sessions()
        total_count = len(all_sessions)
        active_count = len([s for s in all_sessions if s.status in ['starting', 'running']])
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions),
            'total_count': total_count,
            'active_count': active_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get sessions',
            'message': str(e)
        }), 500


@api_bp.route('/neural/sessions/<session_id>', methods=['DELETE'])
def delete_training_session(session_id):
    """Delete a training session from database."""
    try:
        # Check if session exists
        db_session = db.get_neural_training_session(session_id)
        if not db_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Delete session from database
        success = db.delete_neural_training_session(session_id)
        if not success:
            return jsonify({'error': 'Failed to delete session'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Session deleted',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete session',
            'message': str(e)
        }), 500


@api_bp.route('/neural/evaluation-sessions', methods=['GET'])
def get_all_evaluation_sessions():
    """Get all active evaluation sessions."""
    try:
        sessions = []
        for session_id, session in evaluation_sessions.items():
            # Calculate elapsed time
            elapsed_time = None
            if 'start_time' in session:
                start_time = session['start_time']
                if isinstance(start_time, (int, float)):
                    elapsed_time = time.time() - start_time
                else:
                    # Handle string timestamps
                    try:
                        import datetime
                        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        elapsed_time = (datetime.datetime.now() - start_dt).total_seconds()
                    except:
                        elapsed_time = 0
            
            session_data = {
                'session_id': session_id,
                'status': session.get('status', 'unknown'),
                'progress': session.get('progress', 0),
                'start_time': session.get('start_time'),
                'end_time': session.get('end_time'),
                'elapsed_time': elapsed_time,
                'config': session.get('config'),
                'error': session.get('error'),
                'results': session.get('results')
            }
            sessions.append(session_data)
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions),
            'active_count': len([s for s in sessions if s['status'] in ['starting', 'running']])
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get evaluation sessions',
            'message': str(e)
        }), 500


@api_bp.route('/neural/evaluation-sessions/<session_id>', methods=['DELETE'])
def delete_evaluation_session(session_id):
    """Delete an evaluation session."""
    if session_id not in evaluation_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    del evaluation_sessions[session_id]
    
    return jsonify({
        'success': True,
        'message': 'Evaluation session deleted',
        'session_id': session_id
    })


# New API endpoints for Part 2.1.4: Historical Data and Configuration Management

@api_bp.route('/neural/history', methods=['GET'])
def get_training_history():
    """Get historical training data with advanced filtering and sorting."""
    try:
        # Get query parameters
        status = request.args.get('status')
        config_size = request.args.get('config_size')  # small, medium, large
        device = request.args.get('device')  # cpu, cuda
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, progress, status
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        # Get sessions from database with filtering
        db_sessions = db.get_all_neural_training_sessions(
            status=status,
            limit=limit,
            offset=offset
        )
        
        # Apply additional filtering
        filtered_sessions = []
        for session in db_sessions:
            # Parse metadata for additional filtering
            metadata = json.loads(session.metadata) if session.metadata else {}
            
            # Filter by config size
            if config_size and metadata.get('config_size') != config_size:
                continue
                
            # Filter by device
            if device and metadata.get('device') != device:
                continue
                
            # Filter by date range
            if date_from and session.created_at:
                from datetime import datetime
                try:
                    date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    if session.created_at < date_from_dt:
                        continue
                except:
                    pass
                    
            if date_to and session.created_at:
                from datetime import datetime
                try:
                    date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    if session.created_at > date_to_dt:
                        continue
                except:
                    pass
            
            filtered_sessions.append(session)
        
        # Sort sessions
        if sort_by == 'created_at':
            filtered_sessions.sort(key=lambda x: x.created_at or datetime.min, reverse=(sort_order == 'desc'))
        elif sort_by == 'progress':
            filtered_sessions.sort(key=lambda x: x.progress or 0, reverse=(sort_order == 'desc'))
        elif sort_by == 'status':
            filtered_sessions.sort(key=lambda x: x.status or '', reverse=(sort_order == 'desc'))
        
        # Convert to API response format
        sessions = []
        for db_session in filtered_sessions:
            session_data = {
                'session_id': db_session.session_id,
                'status': db_session.status,
                'progress': db_session.progress,
                'start_time': db_session.created_at.isoformat() if db_session.created_at else None,
                'end_time': db_session.updated_at.isoformat() if db_session.updated_at else None,
                'config': json.loads(db_session.config) if db_session.config else {},
                'logs': json.loads(db_session.logs) if db_session.logs else [],
                'error': db_session.error,
                'results': json.loads(db_session.results) if db_session.results else None,
                'metadata': json.loads(db_session.metadata) if db_session.metadata else {}
            }
            sessions.append(session_data)
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions),
            'total_count': len(filtered_sessions),
            'filters': {
                'status': status,
                'config_size': config_size,
                'device': device,
                'date_from': date_from,
                'date_to': date_to
            },
            'sorting': {
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get training history',
            'message': str(e)
        }), 500


@api_bp.route('/neural/configurations', methods=['GET'])
def get_neural_configurations():
    """Get all saved neural training configurations."""
    try:
        # Get query parameters
        is_default = request.args.get('is_default', type=bool)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get configurations from database
        db_configs = db.get_neural_configurations(
            is_default=is_default
        )
        
        # Convert to API response format
        configurations = []
        for db_config in db_configs:
            config_data = {
                'config_id': db_config.config_id,
                'name': db_config.name,
                'description': db_config.description,
                'is_default': db_config.is_default,
                'config': json.loads(db_config.config) if db_config.config else {},
                'metadata': json.loads(db_config.metadata) if db_config.metadata else {},
                'created_at': db_config.created_at.isoformat() if db_config.created_at else None,
                'updated_at': db_config.updated_at.isoformat() if db_config.updated_at else None
            }
            configurations.append(config_data)
        
        return jsonify({
            'configurations': configurations,
            'count': len(configurations),
            'filters': {
                'is_default': is_default
            },
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get configurations',
            'message': str(e)
        }), 500


@api_bp.route('/neural/configurations', methods=['POST'])
def save_neural_configuration():
    """Save a new neural training configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'config']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create configuration object
        from core.azul_database import NeuralConfiguration
        db_config = NeuralConfiguration(
            config_id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description', ''),
            is_default=data.get('is_default', False),
            config=json.dumps(data['config']),
            metadata=json.dumps(data.get('metadata', {}))
        )
        
        # Save to database
        success = db.save_neural_configuration(db_config)
        if not success:
            return jsonify({'error': 'Failed to save configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration saved',
            'config_id': db_config.config_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to save configuration',
            'message': str(e)
        }), 500


@api_bp.route('/neural/configurations/<config_id>', methods=['PUT'])
def update_neural_configuration(config_id):
    """Update an existing neural training configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get existing configuration
        db_config = db.get_neural_configuration(config_id)
        if not db_config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Update fields
        if 'name' in data:
            db_config.name = data['name']
        if 'description' in data:
            db_config.description = data['description']
        if 'is_default' in data:
            db_config.is_default = data['is_default']
        if 'config' in data:
            db_config.config = json.dumps(data['config'])
        if 'metadata' in data:
            db_config.metadata = json.dumps(data['metadata'])
        
        # Save updated configuration
        success = db.save_neural_configuration(db_config)
        if not success:
            return jsonify({'error': 'Failed to update configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated',
            'config_id': config_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update configuration',
            'message': str(e)
        }), 500


@api_bp.route('/neural/configurations/<config_id>', methods=['DELETE'])
def delete_neural_configuration(config_id):
    """Delete a neural training configuration."""
    try:
        # Check if configuration exists
        db_config = db.get_neural_configuration(config_id)
        if not db_config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Delete configuration
        success = db.delete_neural_configuration(config_id)
        if not success:
            return jsonify({'error': 'Failed to delete configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration deleted',
            'config_id': config_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete configuration',
            'message': str(e)
        }), 500


@api_bp.route('/neural/models', methods=['GET'])
def get_neural_models():
    """Get all saved neural models with metadata."""
    try:
        # Get query parameters
        architecture = request.args.get('architecture')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get models from database
        db_models = db.get_neural_models(
            architecture=architecture
        )
        
        # Convert to API response format
        models = []
        for db_model in db_models:
            model_data = {
                'model_id': db_model.model_id,
                'name': db_model.name,
                'architecture': db_model.architecture,
                'file_path': db_model.file_path,
                'training_session_id': db_model.training_session_id,
                'metadata': json.loads(db_model.metadata) if db_model.metadata else {},
                'created_at': db_model.created_at.isoformat() if db_model.created_at else None,
                'updated_at': db_model.updated_at.isoformat() if db_model.updated_at else None
            }
            models.append(model_data)
        
        return jsonify({
            'models': models,
            'count': len(models),
            'filters': {
                'architecture': architecture
            },
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get models',
            'message': str(e)
        }), 500


# ================================
# Board State Validation Endpoints
# ================================




@api_bp.route('/validate-board-state', methods=['POST'])
@require_session
def validate_board_state():
    """
    Validate a complete board state for rule compliance.
    
    This endpoint is used by the board editor (R1.1) to ensure
    that edited positions follow all Azul rules.
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validation_request = BoardValidationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid request format', 'details': str(e)}), 400
        
        # Import the validator
        from core.azul_rule_validator import BoardStateValidator
        from core.azul_model import AzulState
        
        # Create validator
        validator = BoardStateValidator()
        
        # Convert game state dict to AzulState
        game_state_dict = validation_request.game_state
        
        # Convert game state dict to AzulState using the new from_dict method
        try:
            # Create AzulState from the provided game state
            state = AzulState.from_dict(game_state_dict)
        except Exception as e:
            return jsonify({
                'error': 'Invalid game state format',
                'message': str(e)
            }), 400
        
        # Perform validation based on type
        if validation_request.validation_type == "complete":
            result = validator.validate_complete_board_state(state)
        elif validation_request.validation_type == "pattern_line":
            # Extract pattern line specific parameters
            player_id = validation_request.player_id or 0
            # Parse element_id like "pattern_line_0_2" -> line_index=2
            if validation_request.element_id:
                parts = validation_request.element_id.split('_')
                line_index = int(parts[-1]) if len(parts) > 2 else 0
            else:
                line_index = 0
            
            # Get current pattern line state
            agent = state.agents[player_id]
            current_color = agent.lines_tile[line_index]
            tile_count = agent.lines_number[line_index]
            
            result = validator.validate_pattern_line_edit(
                state, player_id, line_index, current_color, tile_count
            )
        else:
            # Default to complete validation
            result = validator.validate_complete_board_state(state)
        
        # Convert result to JSON response
        response = {
            'valid': result.is_valid,
            'errors': result.errors,
            'warnings': result.warnings,
            'affected_elements': getattr(result, 'affected_elements', []),
            'suggestion': getattr(result, 'suggestion', None)
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Board validation error: {str(e)}")
        return jsonify({
            'error': 'Validation service error',
            'message': str(e)
        }), 500


@api_bp.route('/validate-pattern-line-edit', methods=['POST'])
def validate_pattern_line_edit():
    """
    Validate a pattern line edit in real-time (no auth required for UI responsiveness).
    
    This provides immediate feedback during board editing.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        current_color = data.get('current_color', -1)
        new_color = data.get('new_color', -1)
        current_count = data.get('current_count', 0)
        new_count = data.get('new_count', 0)
        line_index = data.get('line_index', 0)
        
        # Import validation function
        from core.azul_rule_validator import validate_pattern_line_edit_simple
        
        # Validate
        result = validate_pattern_line_edit_simple(
            current_color, new_color, current_count, new_count, line_index + 1
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': 'Validation error',
            'message': str(e)
        }), 500


@api_bp.route('/validate-tile-count', methods=['POST'])
def validate_tile_count():
    """Validate tile count conservation in the game state."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = BoardValidationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.game_state.get('fen', ''))
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the rule validator
        from core.azul_rule_validator import AzulRuleValidator
        validator = AzulRuleValidator()
        
        # Validate tile conservation
        validation_result = validator.validate_tile_conservation(state)
        
        return jsonify({
            'is_valid': validation_result.is_valid,
            'message': validation_result.message,
            'tile_counts': validator.count_all_tiles(state) if hasattr(validator, 'count_all_tiles') else {}
        })
        
    except Exception as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 500


@api_bp.route('/detect-patterns', methods=['POST'])
def detect_patterns():
    """Detect tactical patterns in the current position."""
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = PatternDetectionRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the pattern detector
        from core.azul_patterns import AzulPatternDetector
        detector = AzulPatternDetector()
        
        # Update urgency threshold if provided
        if request_model.urgency_threshold != 0.7:
            detector.blocking_urgency_threshold = request_model.urgency_threshold
        
        # Detect patterns
        pattern_detection = detector.detect_patterns(state, request_model.current_player)
        
        # Prepare response
        response = {
            'total_patterns': pattern_detection.total_patterns,
            'confidence_score': pattern_detection.confidence_score,
            'patterns_detected': True if pattern_detection.total_patterns > 0 else False
        }
        
        # Add blocking opportunities if requested
        if request_model.include_blocking_opportunities:
            blocking_opportunities = []
            for opp in pattern_detection.blocking_opportunities:
                blocking_opportunities.append({
                    'target_player': opp.target_player,
                    'target_pattern_line': opp.target_pattern_line,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'blocking_tiles_available': opp.blocking_tiles_available,
                    'blocking_factories': opp.blocking_factories,
                    'blocking_center': opp.blocking_center,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "HIGH" if opp.urgency_score > 0.8 else "MEDIUM" if opp.urgency_score > 0.6 else "LOW",
                    'description': opp.description
                })
            response['blocking_opportunities'] = blocking_opportunities
        
        # Add move suggestions if requested
        if request_model.include_move_suggestions and pattern_detection.blocking_opportunities:
            move_suggestions = detector.get_blocking_move_suggestions(
                state, request_model.current_player, pattern_detection.blocking_opportunities
            )
            response['move_suggestions'] = move_suggestions
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Pattern detection error: {str(e)}'}), 500


@api_bp.route('/detect-scoring-optimization', methods=['POST'])
def detect_scoring_optimization():
    """Detect scoring optimization opportunities in the current position."""
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = ScoringOptimizationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the scoring optimization detector
        from core.azul_scoring_optimization import AzulScoringOptimizationDetector
        detector = AzulScoringOptimizationDetector()
        
        # Detect scoring optimization opportunities
        optimization_detection = detector.detect_scoring_optimization(state, request_model.current_player)
        
        # Prepare response
        response = {
            'total_opportunities': optimization_detection.total_opportunities,
            'total_potential_bonus': optimization_detection.total_potential_bonus,
            'confidence_score': optimization_detection.confidence_score,
            'opportunities_detected': True if optimization_detection.total_opportunities > 0 else False
        }
        
        # Add wall completion opportunities if requested
        if request_model.include_wall_completion:
            wall_opportunities = []
            for opp in optimization_detection.wall_completion_opportunities:
                wall_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['wall_completion_opportunities'] = wall_opportunities
        
        # Add pattern line optimization opportunities if requested
        if request_model.include_pattern_line_optimization:
            pattern_line_opportunities = []
            for opp in optimization_detection.pattern_line_opportunities:
                pattern_line_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['pattern_line_opportunities'] = pattern_line_opportunities
        
        # Add floor line optimization opportunities if requested
        if request_model.include_floor_line_optimization:
            floor_line_opportunities = []
            for opp in optimization_detection.floor_line_opportunities:
                floor_line_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['floor_line_opportunities'] = floor_line_opportunities
        
        # Add multiplier setup opportunities if requested
        if request_model.include_multiplier_setup:
            multiplier_opportunities = []
            for opp in optimization_detection.multiplier_opportunities:
                multiplier_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['multiplier_opportunities'] = multiplier_opportunities
        
        # Add move suggestions if requested
        if request_model.include_move_suggestions:
            all_opportunities = (optimization_detection.wall_completion_opportunities + 
                               optimization_detection.pattern_line_opportunities + 
                               optimization_detection.floor_line_opportunities + 
                               optimization_detection.multiplier_opportunities)
            
            move_suggestions = []
            for opp in all_opportunities:
                if opp.move_suggestions:
                    move_suggestions.extend(opp.move_suggestions)
            
            response['move_suggestions'] = move_suggestions
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Scoring optimization detection error: {str(e)}'}), 500


@api_bp.route('/detect-floor-line-patterns', methods=['POST'])
def detect_floor_line_patterns():
    """Detect floor line management patterns in the current position."""
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = FloorLinePatternRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the floor line pattern detector
        from core.azul_floor_line_patterns import AzulFloorLinePatternDetector
        detector = AzulFloorLinePatternDetector()
        
        # Detect floor line patterns
        pattern_detection = detector.detect_floor_line_patterns(state, request_model.current_player)
        
        # Prepare response
        response = {
            'total_opportunities': pattern_detection.total_opportunities,
            'total_penalty_risk': pattern_detection.total_penalty_risk,
            'confidence_score': pattern_detection.confidence_score,
            'patterns_detected': True if pattern_detection.total_opportunities > 0 else False
        }
        
        # Add risk mitigation opportunities if requested
        if request_model.include_risk_mitigation:
            risk_mitigation_opportunities = []
            for opp in pattern_detection.risk_mitigation_opportunities:
                risk_mitigation_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['risk_mitigation_opportunities'] = risk_mitigation_opportunities
        
        # Add timing optimization opportunities if requested
        if request_model.include_timing_optimization:
            timing_optimization_opportunities = []
            for opp in pattern_detection.timing_optimization_opportunities:
                timing_optimization_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['timing_optimization_opportunities'] = timing_optimization_opportunities
        
        # Add trade-off opportunities if requested
        if request_model.include_trade_offs:
            trade_off_opportunities = []
            for opp in pattern_detection.trade_off_opportunities:
                trade_off_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['trade_off_opportunities'] = trade_off_opportunities
        
        # Add endgame management opportunities if requested
        if request_model.include_endgame_management:
            endgame_management_opportunities = []
            for opp in pattern_detection.endgame_management_opportunities:
                endgame_management_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['endgame_management_opportunities'] = endgame_management_opportunities
        
        # Add blocking opportunities if requested
        if request_model.include_blocking_opportunities:
            blocking_opportunities = []
            for opp in pattern_detection.blocking_opportunities:
                blocking_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['blocking_opportunities'] = blocking_opportunities
        
        # Add efficiency opportunities if requested
        if request_model.include_efficiency_opportunities:
            efficiency_opportunities = []
            for opp in pattern_detection.efficiency_opportunities:
                efficiency_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['efficiency_opportunities'] = efficiency_opportunities
        
        # Add move suggestions if requested
        if request_model.include_move_suggestions:
            all_opportunities = (pattern_detection.risk_mitigation_opportunities + 
                               pattern_detection.timing_optimization_opportunities + 
                               pattern_detection.trade_off_opportunities + 
                               pattern_detection.endgame_management_opportunities + 
                               pattern_detection.blocking_opportunities + 
                               pattern_detection.efficiency_opportunities)
            
            move_suggestions = []
            for opp in all_opportunities:
                if opp.move_suggestions:
                    move_suggestions.extend(opp.move_suggestions)
            
            response['move_suggestions'] = move_suggestions
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Floor line pattern detection error: {str(e)}'}), 500





# Add CORS headers to all responses
@api_bp.after_request
def add_cors_headers(response):
    """Add CORS headers to all API responses."""
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# Global error handler for malformed JSON
@api_bp.errorhandler(400)
def handle_bad_request(error):
    """Handle 400 Bad Request errors."""
    if request.is_json:
        return jsonify({'error': 'Invalid JSON format'}), 400
    return jsonify({'error': 'Bad request'}), 400


# Global error handler for JSON decode errors
@api_bp.errorhandler(500)
def handle_internal_error(error):
    """Handle 500 Internal Server errors."""
    if hasattr(error, 'description') and 'JSON' in error.description:
        return jsonify({'error': 'Invalid JSON format'}), 400
    return jsonify({'error': 'Internal server error'}), 500


# Handle OPTIONS requests for CORS preflight
@api_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Handle CORS preflight requests."""
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


