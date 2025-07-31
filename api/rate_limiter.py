"""
Rate limiting functionality for the Azul API.

This module provides session-based rate limiting to prevent abuse
and ensure fair resource allocation across users.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int
    window_seconds: int
    heavy_analysis_limit: int = 10  # Heavy analyses per minute
    light_analysis_limit: int = 100  # Light analyses per minute


class RateLimiter:
    """
    Thread-safe rate limiter for API endpoints.
    
    Provides session-based rate limiting with configurable limits
    for different types of analysis requests.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize the rate limiter with configuration."""
        self.config = config or RateLimitConfig(
            max_requests=100,
            window_seconds=60,
            heavy_analysis_limit=10,
            light_analysis_limit=100
        )
        
        # Thread-safe storage for request tracking
        self._lock = threading.Lock()
        self._requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
        self._heavy_analyses: Dict[str, Deque[float]] = defaultdict(lambda: deque())
        self._light_analyses: Dict[str, Deque[float]] = defaultdict(lambda: deque())
    
    def _cleanup_old_requests(self, session_id: str, window_seconds: int):
        """Remove requests older than the window."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Clean up general requests
        while (self._requests[session_id] and 
               self._requests[session_id][0] < cutoff_time):
            self._requests[session_id].popleft()
        
        # Clean up heavy analyses
        while (self._heavy_analyses[session_id] and 
               self._heavy_analyses[session_id][0] < cutoff_time):
            self._heavy_analyses[session_id].popleft()
        
        # Clean up light analyses
        while (self._light_analyses[session_id] and 
               self._light_analyses[session_id][0] < cutoff_time):
            self._light_analyses[session_id].popleft()
    
    def check_rate_limit(self, session_id: str, request_type: str = "general") -> bool:
        """
        Check if a request is allowed under rate limiting.
        
        Args:
            session_id: Unique session identifier
            request_type: Type of request ("general", "heavy", "light")
            
        Returns:
            True if request is allowed, False if rate limited
        """
        with self._lock:
            current_time = time.time()
            
            # Clean up old requests
            self._cleanup_old_requests(session_id, self.config.window_seconds)
            
            # Check general rate limit
            if len(self._requests[session_id]) >= self.config.max_requests:
                return False
            
            # Check specific limits for analysis types
            if request_type == "heavy":
                if len(self._heavy_analyses[session_id]) >= self.config.heavy_analysis_limit:
                    return False
            elif request_type == "light":
                if len(self._light_analyses[session_id]) >= self.config.light_analysis_limit:
                    return False
            
            # Record the request
            self._requests[session_id].append(current_time)
            
            if request_type == "heavy":
                self._heavy_analyses[session_id].append(current_time)
            elif request_type == "light":
                self._light_analyses[session_id].append(current_time)
            
            return True
    
    def get_remaining_requests(self, session_id: str, request_type: str = "general") -> Dict[str, int]:
        """
        Get remaining request counts for a session.
        
        Args:
            session_id: Unique session identifier
            request_type: Type of request to check
            
        Returns:
            Dictionary with remaining request counts
        """
        with self._lock:
            self._cleanup_old_requests(session_id, self.config.window_seconds)
            
            return {
                "general_remaining": max(0, self.config.max_requests - len(self._requests[session_id])),
                "heavy_remaining": max(0, self.config.heavy_analysis_limit - len(self._heavy_analyses[session_id])),
                "light_remaining": max(0, self.config.light_analysis_limit - len(self._light_analyses[session_id])),
                "window_seconds": self.config.window_seconds
            }
    
    def get_session_stats(self, session_id: str) -> Dict[str, any]:
        """
        Get detailed statistics for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with session statistics
        """
        with self._lock:
            self._cleanup_old_requests(session_id, self.config.window_seconds)
            
            return {
                "session_id": session_id,
                "total_requests": len(self._requests[session_id]),
                "heavy_analyses": len(self._heavy_analyses[session_id]),
                "light_analyses": len(self._light_analyses[session_id]),
                "limits": {
                    "max_requests": self.config.max_requests,
                    "heavy_limit": self.config.heavy_analysis_limit,
                    "light_limit": self.config.light_analysis_limit,
                    "window_seconds": self.config.window_seconds
                }
            } 