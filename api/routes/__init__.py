"""
API Routes Package

This package contains all modularized route blueprints for the Azul Solver & Analysis Toolkit.
"""

from .positions import positions_bp
from .analysis import analysis_bp
from .game import game_bp

# Register all blueprints here
__all__ = ['positions_bp', 'analysis_bp', 'game_bp'] 