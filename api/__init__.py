"""
Azul Solver & Analysis Toolkit - API Module

This module provides REST API endpoints for game analysis, hints, and research tools.
"""

from .routes import api_bp
from .auth import auth_bp
from .rate_limiter import RateLimiter

__all__ = ['api_bp', 'auth_bp', 'RateLimiter']