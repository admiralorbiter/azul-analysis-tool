# Azul Core Engine
"""
Core game engine for the Azul Solver & Analysis Toolkit.

This package contains:
- Game state representation (azul_model.py)
- Utility functions and constants (azul_utils.py) 
- Display interfaces (azul_displayer.py)
- Template base classes (template.py)
"""

from .azul_model import AzulState, AzulGameRule
from .azul_utils import Tile, Action, TileGrab
from .azul_displayer import GUIDisplayer, TextDisplayer

__version__ = "0.1.0"
__all__ = ["AzulState", "AzulGameRule", "Tile", "Action", "TileGrab", "GUIDisplayer", "TextDisplayer"]