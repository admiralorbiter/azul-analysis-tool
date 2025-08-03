"""
Game-related request models for the API.

This module contains Pydantic models for game management endpoints including
game creation, move execution, and game analysis.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class MoveExecutionRequest(BaseModel):
    """Request model for move execution."""
    fen_string: str
    move: Dict[str, Any]  # Move data from frontend
    agent_id: int = 0


class GameCreationRequest(BaseModel):
    """Request model for game creation."""
    player_count: int = 2  # Only 2-player games supported
    seed: Optional[int] = None


class GameAnalysisRequest(BaseModel):
    """Request model for game analysis."""
    game_data: Dict[str, Any]  # Game log data
    include_blunder_analysis: bool = True
    include_position_analysis: bool = True
    analysis_depth: int = 3


class GameLogUploadRequest(BaseModel):
    """Request model for game log upload."""
    game_format: str = 'json'  # 'json', 'text', 'pgn'
    game_content: str
    game_metadata: Optional[Dict[str, Any]] = None


class GameAnalysisSearchRequest(BaseModel):
    """Request model for searching game analyses."""
    player_names: Optional[List[str]] = None
    min_blunder_count: Optional[int] = None
    max_blunder_count: Optional[int] = None
    date_range: Optional[Dict[str, str]] = None
    limit: int = 50
    offset: int = 0 