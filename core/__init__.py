# Azul Core Engine
"""
Core game engine for the Azul Solver & Analysis Toolkit.

This package contains:
- Game state representation (azul_model.py)
- Utility functions and constants (azul_utils.py) 
- Display interfaces (azul_displayer.py)
- Template base classes (template.py)
- Search algorithms (azul_search.py)
- Monte Carlo Tree Search (azul_mcts.py)
"""

from .azul_model import AzulState, AzulGameRule
from .azul_utils import Tile, Action, TileGrab
from .azul_displayer import GUIDisplayer, TextDisplayer

# Import search algorithms from analysis_engine
try:
    from analysis_engine.mathematical_optimization import azul_search
    from analysis_engine.mathematical_optimization import azul_mcts
    from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
    from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS
except ImportError:
    # Fallback for when analysis_engine is not available
    azul_search = None
    azul_mcts = None
    AzulAlphaBetaSearch = None
    AzulMCTS = None

__version__ = "0.1.0"
__all__ = [
    "AzulState", "AzulGameRule", "Tile", "Action", "TileGrab", 
    "GUIDisplayer", "TextDisplayer", "AzulAlphaBetaSearch", "AzulMCTS",
    "azul_search", "azul_mcts"
]