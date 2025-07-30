#!/usr/bin/env python3
"""
Azul Solver & Analysis Toolkit - Main Entry Point

This is the main entry point for the Azul Solver & Analysis Toolkit.
It provides CLI commands for exact analysis, hint generation, and web server.
"""

import click
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.azul_model import AzulState, AzulGameRule
from core.azul_utils import Tile, Action


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Azul Solver & Analysis Toolkit
    
    A Python-based engine, web UI, and research tools for the Azul board game.
    Provides exact search, fast hints, and analysis capabilities.
    """
    pass


@cli.command()
@click.argument('fen_string')
@click.option('--depth', '-d', default=3, help='Search depth for exact analysis')
@click.option('--timeout', '-t', default=4.0, help='Timeout in seconds')
def exact(fen_string, depth, timeout):
    """Perform exact analysis of a game position.
    
    FEN_STRING: The game position in FEN-like notation
    """
    click.echo(f"🔍 Analyzing position: {fen_string}")
    click.echo(f"   Depth: {depth}, Timeout: {timeout}s")
    
    # TODO: Implement exact search
    click.echo("⚠️  Exact search not yet implemented - this is planned for Milestone M2")
    click.echo("   Expected completion: 2 weeks after M1 (Rules Engine)")


@cli.command()
@click.argument('fen_string')
@click.option('--budget', '-b', default=0.2, help='Time budget in seconds')
@click.option('--rollouts', '-r', default=100, help='Number of MCTS rollouts')
def hint(fen_string, budget, rollouts):
    """Generate fast hints for a game position.
    
    FEN_STRING: The game position in FEN-like notation
    """
    click.echo(f"💡 Generating hint for: {fen_string}")
    click.echo(f"   Budget: {budget}s, Rollouts: {rollouts}")
    
    # TODO: Implement fast hint generation
    click.echo("⚠️  Fast hint generation not yet implemented - this is planned for Milestone M3")
    click.echo("   Expected completion: 4 weeks after M1 (Rules Engine)")


@cli.command()
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind to')
@click.option('--port', '-p', default=8000, help='Port to listen on')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def serve(host, port, debug):
    """Start the web server for the analysis UI."""
    click.echo(f"🚀 Starting Azul Solver web server...")
    click.echo(f"   Host: {host}, Port: {port}, Debug: {debug}")
    
    # TODO: Implement web server
    click.echo("⚠️  Web server not yet implemented - this is planned for Milestone M4")
    click.echo("   Expected completion: 7 weeks after M1 (Rules Engine)")


@cli.command()
def test():
    """Run basic engine tests to verify functionality."""
    click.echo("🧪 Running basic engine tests...")
    
    try:
        # Test basic imports and classes
        click.echo("✓ Testing imports...")
        
        # Test game state creation
        click.echo("✓ Testing game state creation...")
        game_state = AzulState(2)  # 2-player game
        
        # Test game rule creation
        click.echo("✓ Testing game rule creation...")
        game_rule = AzulGameRule(2)
        
        # Test tile enums
        click.echo("✓ Testing tile enums...")
        assert len(Tile) == 5
        assert Tile.BLUE == 0
        assert Tile.YELLOW == 1
        
        # Test action enums
        click.echo("✓ Testing action enums...")
        assert Action.TAKE_FROM_FACTORY == 1
        assert Action.TAKE_FROM_CENTRE == 2
        
        click.echo("✅ All basic tests passed!")
        click.echo("\n📋 Current Status:")
        click.echo("   ✅ Core imports working")
        click.echo("   ✅ Game state creation")
        click.echo("   ✅ Basic enums and constants")
        click.echo("   🚧 Full rule validation (in progress)")
        click.echo("   📋 Move generation (planned)")
        click.echo("   📋 Search algorithms (planned)")
        
    except Exception as e:
        click.echo(f"❌ Test failed: {e}")
        click.echo("\n🔧 Next steps:")
        click.echo("   1. Fix import issues")
        click.echo("   2. Verify game state initialization")
        click.echo("   3. Add comprehensive unit tests")
        sys.exit(1)


@cli.command()
def status():
    """Show current project status and next steps."""
    click.echo("📊 Azul Solver & Analysis Toolkit - Project Status")
    click.echo("=" * 50)
    
    click.echo("\n🎯 Current Milestone: M1 - Rules Engine")
    click.echo("   ⏳ Duration: 2 weeks")
    click.echo("   🎯 Goal: Complete A1-A3 from project plan")
    
    click.echo("\n✅ Completed Tasks:")
    click.echo("   ✅ Repository setup and cleanup")
    click.echo("   ✅ Fixed import conflicts")
    click.echo("   ✅ Created project structure")
    click.echo("   ✅ Python packaging setup")
    
    click.echo("\n🚧 In Progress:")
    click.echo("   🚧 A1: State model with immutable dataclass + NumPy arrays")
    click.echo("   🚧 A2: Rule validator with 100 golden tests")
    click.echo("   🚧 A3: Move generator for compound moves")
    
    click.echo("\n📋 Next Steps:")
    click.echo("   1. Fix remaining import issues in core modules")
    click.echo("   2. Create comprehensive unit tests")
    click.echo("   3. Implement proper state immutability")
    click.echo("   4. Add move generation and validation")
    
    click.echo("\n🎲 Try: python main.py test")


if __name__ == '__main__':
    cli()