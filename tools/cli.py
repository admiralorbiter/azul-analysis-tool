"""
CLI tools for the Azul Solver & Analysis Toolkit.

This module provides command-line utilities for analysis, research, and development.
"""

import click
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Main entry point for the azcli command."""
    from main import cli
    cli()


if __name__ == '__main__':
    main()