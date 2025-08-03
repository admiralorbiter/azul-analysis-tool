"""
Analysis-related request models for the API.

This module contains Pydantic models for analysis endpoints including
position analysis, hints, and analysis caching.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoints."""
    fen_string: str
    agent_id: int = 0
    depth: Optional[int] = None
    time_budget: Optional[float] = None
    rollouts: Optional[int] = None


class HintRequest(BaseModel):
    """Request model for hint endpoints."""
    fen_string: str
    agent_id: int = 0
    budget: float = 0.2
    rollouts: int = 100


class AnalysisCacheRequest(BaseModel):
    """Request model for analysis cache endpoints."""
    fen_string: str
    agent_id: int = 0
    search_type: str  # 'mcts', 'alpha_beta', 'neural_mcts'
    best_move: Optional[str] = None
    best_score: float = 0.0
    search_time: float = 0.0
    nodes_searched: int = 0
    rollout_count: int = 0
    depth_reached: Optional[int] = None
    principal_variation: Optional[list[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisSearchRequest(BaseModel):
    """Request model for analysis search."""
    search_type: Optional[str] = None
    agent_id: Optional[int] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    limit: int = 50
    offset: int = 0 