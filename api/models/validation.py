"""
Validation-related request models for the API.

This module contains Pydantic models for board validation and pattern detection
endpoints including rule validation and tactical pattern analysis.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class BoardValidationRequest(BaseModel):
    """Request model for board state validation."""
    game_state: Dict[str, Any]
    validation_type: str = "complete"  # "complete", "pattern_line", "wall", "floor"
    player_id: Optional[int] = None
    element_id: Optional[str] = None


class PatternDetectionRequest(BaseModel):
    """Request model for pattern detection."""
    fen_string: str
    current_player: int = 0
    include_blocking_opportunities: bool = True
    include_move_suggestions: bool = True
    urgency_threshold: float = 0.7


class ScoringOptimizationRequest(BaseModel):
    """Request model for scoring optimization detection."""
    fen_string: str
    current_player: int = 0
    include_wall_completion: bool = True
    include_pattern_line_optimization: bool = True
    include_floor_line_optimization: bool = True
    include_multiplier_setup: bool = True
    include_move_suggestions: bool = True
    urgency_threshold: float = 0.7


class FloorLinePatternRequest(BaseModel):
    """Request model for floor line pattern detection."""
    fen_string: str
    current_player: int = 0
    include_risk_mitigation: bool = True
    include_timing_optimization: bool = True
    include_trade_offs: bool = True
    include_endgame_management: bool = True
    include_blocking_opportunities: bool = True
    include_efficiency_opportunities: bool = True
    include_move_suggestions: bool = True
    urgency_threshold: float = 0.7


class ValidationError(Exception):
    """Custom validation error for API requests."""
    pass 