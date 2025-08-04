"""
API Routes Package

This package contains all modularized route blueprints for the Azul Solver & Analysis Toolkit.
"""

from .positions import positions_bp
from .analysis import analysis_bp
from .game import game_bp
from .neural import neural_bp, evaluate_neural_model
from .core import core_bp
from .move_analysis import move_analysis_bp
from .performance import performance_bp
from .strategic import strategic_bp
from .validation import validation_bp

# Import utility functions that tests need
from ..utils import get_system_resources, get_process_resources

# Register all blueprints here
__all__ = [
    'positions_bp', 
    'analysis_bp', 
    'game_bp', 
    'neural_bp',
    'core_bp',
    'move_analysis_bp',
    'performance_bp',
    'strategic_bp',
    'validation_bp',
    'evaluate_neural_model',
    'get_system_resources',
    'get_process_resources'
] 