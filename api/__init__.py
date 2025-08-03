"""
Azul Solver & Analysis Toolkit - API Module

This module provides REST API endpoints for game analysis, hints, and research tools.
"""

from .main_routes import api_bp
from .routes.positions import positions_bp
from .routes.analysis import analysis_bp
from .auth import auth_bp
from .rate_limiter import RateLimiter

__all__ = ['api_bp', 'positions_bp', 'analysis_bp', 'auth_bp', 'RateLimiter']