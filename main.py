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
@click.option('--agent', '-a', default=0, help='Agent ID to analyze for (default: 0)')
@click.option('--database', '-db', help='Path to SQLite database for caching')
def exact(fen_string, depth, timeout, agent, database):
    """Perform exact analysis of a game position.
    
    FEN_STRING: The game position in FEN-like notation
    """
    click.echo(f"Analyzing position: {fen_string}")
    click.echo(f"   Depth: {depth}, Timeout: {timeout}s, Agent: {agent}")
    
    if database:
        click.echo(f"   Database: {database}")
    
    try:
        # Import search components
        from core.azul_search import AzulAlphaBetaSearch
        from core.azul_model import AzulState
        
        # Initialize database if provided
        db = None
        if database:
            from core.azul_database import AzulDatabase
            db = AzulDatabase(database)
            click.echo("   ✅ Database connected for caching")
        
        # Parse FEN string to create game state
        state = parse_fen_string(fen_string)
        
        # Create search engine
        search_engine = AzulAlphaBetaSearch(max_depth=depth, max_time=timeout)
        
        # Perform search
        click.echo("   Searching...")
        result = search_engine.search(state, agent, max_depth=depth, max_time=timeout)
        
        # Display results
        click.echo(f"Search completed in {result.search_time:.2f}s")
        click.echo(f"   Nodes searched: {result.nodes_searched:,}")
        click.echo(f"   Depth reached: {result.depth_reached}")
        click.echo(f"   Best score: {result.best_score:.1f}")
        
        if result.best_move:
            click.echo(f"   Best move: {format_move(result.best_move)}")
            click.echo(f"   Principal variation: {len(result.principal_variation)} moves")
        else:
            click.echo("   No best move found (terminal position)")
            
        # Show search statistics
        stats = search_engine.get_search_stats()
        click.echo(f"   Nodes/sec: {stats['nodes_per_second']:.0f}")
        click.echo(f"   TT hits: {stats['transposition_table']['hits']}")
        
        # Cache result if database is available
        if db:
            try:
                position_id = db.cache_position(fen_string, state.player_count)
                db.cache_analysis(position_id, agent, 'alpha_beta', {
                    'best_move': str(result.best_move) if result.best_move else None,
                    'best_score': result.best_score,
                    'search_time': result.search_time,
                    'nodes_searched': result.nodes_searched,
                    'depth_reached': result.depth_reached,
                    'principal_variation': [str(move) for move in result.principal_variation]
                })
                click.echo("   ✅ Analysis cached in database")
            except Exception as e:
                click.echo(f"   ⚠️  Failed to cache analysis: {e}")
        
    except Exception as e:
        click.echo(f"Error during analysis: {e}")
        sys.exit(1)


@cli.command()
@click.argument('fen_string')
@click.option('--budget', '-b', default=0.2, help='Time budget in seconds')
@click.option('--rollouts', '-r', default=100, help='Number of MCTS rollouts')
@click.option('--agent', '-a', default=0, help='Agent ID to analyze for (default: 0)')
@click.option('--database', '-d', help='Path to SQLite database for caching')
def hint(fen_string, budget, rollouts, agent, database):
    """Generate fast hints for a game position.
    
    FEN_STRING: The game position in FEN-like notation
    """
    click.echo(f"💡 Generating hint for: {fen_string}")
    click.echo(f"   Budget: {budget}s, Rollouts: {rollouts}, Agent: {agent}")
    
    if database:
        click.echo(f"   Database: {database}")
    
    try:
        # Import MCTS components
        from core.azul_mcts import AzulMCTS
        from core.azul_model import AzulState
        
        # Initialize database if provided
        db = None
        if database:
            from core.azul_database import AzulDatabase
            db = AzulDatabase(database)
            click.echo("   ✅ Database connected for caching")
        
        # Parse FEN string to create game state
        state = parse_fen_string(fen_string)
        
        # Create MCTS engine
        mcts_engine = AzulMCTS(
            max_time=budget,
            max_rollouts=rollouts,
            database=db
        )
        
        # Perform search
        click.echo("   Searching...")
        result = mcts_engine.search(state, agent)
        
        # Display results
        click.echo(f"Search completed in {result.search_time:.3f}s")
        click.echo(f"   Rollouts performed: {result.rollouts_performed}")
        click.echo(f"   Expected value: {result.expected_value:.2f}")
        click.echo(f"   Confidence: {result.confidence:.2f}")
        
        if result.best_move:
            click.echo(f"   Best move: {format_move(result.best_move)}")
            click.echo(f"   Top moves:")
            for i, (move, score, visits) in enumerate(result.top_moves[:3]):
                click.echo(f"     {i+1}. {format_move(move)} (score: {score:.2f}, visits: {visits})")
        else:
            click.echo("   No best move found (terminal position)")
            
        # Show cache statistics if database is used
        if db:
            stats = db.get_cache_stats()
            click.echo(f"   Cache hit rate: {stats.get('cache_hit_rate', 0):.1f}%")
        
    except Exception as e:
        click.echo(f"Error during hint generation: {e}")
        sys.exit(1)


@cli.command()
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind to')
@click.option('--port', '-p', default=8000, help='Port to listen on')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--database', '-d', help='Path to SQLite database file')
def serve(host, port, debug, database):
    """Start the REST API server for analysis requests."""
    click.echo(f"🚀 Starting Azul Solver REST API server...")
    click.echo(f"   Host: {host}, Port: {port}, Debug: {debug}")
    
    if database:
        click.echo(f"   Database: {database}")
    
    try:
        from api.app import create_app
        
        # Create Flask app with configuration
        config = {
            'DEBUG': debug,
            'DATABASE_PATH': database,
            'RATE_LIMIT_ENABLED': True
        }
        
        app = create_app(config)
        
                    click.echo("✅ REST API server ready!")
            click.echo("📋 Available endpoints:")
            click.echo("   POST /api/v1/auth/session - Create session")
            click.echo("   POST /api/v1/analyze - Exact analysis")
            click.echo("   POST /api/v1/hint - Fast hints")
            click.echo("   GET  /api/v1/health - Health check")
            click.echo("   GET  /api/v1/stats - Usage statistics")
            click.echo(f"\n🌐 Web UI will be available at: http://{host}:{port}")
            click.echo("   📊 Interactive game analysis with live hints")
            click.echo("   🎮 Drag-and-drop tile placement")
            click.echo("   📈 Real-time analysis results")
        
        # Start the server
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        click.echo(f"❌ Failed to start server: {e}")
        sys.exit(1)


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
    click.echo("Azul Solver & Analysis Toolkit - Project Status")
    click.echo("=" * 50)
    
    click.echo("\nCurrent Milestone: M2 - Exact Search (COMPLETE)")
    click.echo("   Duration: 2 weeks")
    click.echo("   Goal: Complete A4-A5 from project plan")
    
    click.echo("\nCompleted Tasks:")
    click.echo("   M1: Rules Engine (A1-A3) - 100% complete")
    click.echo("   A1: State model with Zobrist hashing")
    click.echo("   A2: Rule validator with comprehensive tests")
    click.echo("   A3: Move generator with bit masks")
    click.echo("   A4: Heuristic evaluation")
    click.echo("   A5: Alpha-beta search with depth-3 < 4s")
    click.echo("   CLI integration for exact analysis")
    
    click.echo("\nTest Results:")
    click.echo("   133 tests passing (100% success rate)")
    click.echo("   Performance targets met")
    click.echo("   Integration with all components")
    
    click.echo("\nNext Steps:")
    click.echo("   1. M3: Fast Hint Engine (MCTS)")
    click.echo("   2. M4: Web UI with React")
    click.echo("   3. M5: Research Tools")
    
    click.echo("\nTry: python main.py exact initial --depth 3")


def parse_fen_string(fen_string):
    """Parse a FEN-like string to create an AzulState.
    
    For now, we'll support a simple format: "initial" for starting position.
    Future: Support full position encoding.
    """
    if fen_string.lower() == "initial":
        return AzulState(2)  # 2-player starting position
    else:
        raise ValueError(f"Unsupported FEN format: {fen_string}. Use 'initial' for now.")


def format_move(move):
    """Format a move for display."""
    if move is None:
        return "None"
    
    # Convert FastMove to readable format
    action_type = "factory" if move.source_id >= 0 else "centre"
    tile_type = ["blue", "yellow", "red", "black", "white"][move.tile_type]
    
    if move.pattern_line_dest >= 0:
        return f"take {move.num_to_pattern_line} {tile_type} from {action_type} {move.source_id} to pattern line {move.pattern_line_dest}"
    else:
        return f"take {move.num_to_floor_line} {tile_type} from {action_type} {move.source_id} to floor"


if __name__ == '__main__':
    cli()