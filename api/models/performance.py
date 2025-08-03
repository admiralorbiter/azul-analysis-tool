"""
Performance-related request models for the API.

This module contains Pydantic models for performance monitoring and system health
endpoints including statistics and health checks.
"""

from typing import Optional
from pydantic import BaseModel


class PerformanceStatsRequest(BaseModel):
    """Request model for performance statistics."""
    search_type: Optional[str] = None
    time_range_hours: Optional[int] = None
    include_query_stats: bool = True
    include_index_stats: bool = True


class SystemHealthRequest(BaseModel):
    """Request model for system health checks."""
    include_database_health: bool = True
    include_performance_metrics: bool = True
    include_cache_analytics: bool = True 