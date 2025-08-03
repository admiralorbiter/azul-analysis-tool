"""
Position-related request models for the API.

This module contains Pydantic models for position cache endpoints including
position storage, bulk operations, and position database operations.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class PositionCacheRequest(BaseModel):
    """Request model for position cache endpoints."""
    model_config = ConfigDict(extra="forbid")
    
    fen_string: str
    player_count: int = 2
    compressed_state: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BulkPositionRequest(BaseModel):
    """Request model for bulk position operations."""
    positions: list[PositionCacheRequest]
    overwrite: bool = False


class PositionDatabaseRequest(BaseModel):
    """Request model for position database operations."""
    fen_string: str
    metadata: Optional[Dict[str, Any]] = None
    frequency: int = 1


class SimilarPositionRequest(BaseModel):
    """Request model for finding similar positions."""
    fen_string: str
    similarity_threshold: float = 0.8
    limit: int = 10


class ContinuationRequest(BaseModel):
    """Request model for getting popular continuations."""
    fen_string: str
    limit: int = 5 