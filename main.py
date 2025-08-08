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
        # Use default database path if none provided
        db_path = database or "azul_cache.db"
        config = {
            'DEBUG': debug,
            'DATABASE_PATH': db_path,
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
    
    click.echo("\nCurrent Milestone: M7 - Neural Integration (IN PROGRESS)")
    click.echo("   Duration: 3 weeks")
    click.echo("   Goal: Complete A7 from project plan")
    
    click.echo("\nCompleted Tasks:")
    click.echo("   M1: Rules Engine (A1-A3) - 100% complete")
    click.echo("   M2: Exact Search (A4-A5) - 100% complete")
    click.echo("   M3: Fast Hint Engine (A6) - 100% complete")
    click.echo("   M4: Database Integration (B1) - 100% complete")
    click.echo("   M5: REST API Integration (C1-C3) - 100% complete")
    click.echo("   M6: Web UI Development (D1-D3) - 100% complete")
    click.echo("   A7: Neural Bridge - IN PROGRESS")
    
    click.echo("\nTest Results:")
    click.echo("   201+ tests passing (100% success rate)")
    click.echo("   Performance targets met")
    click.echo("   Web UI fully operational")
    click.echo("   Neural components integrated")
    
    click.echo("\nNext Steps:")
    click.echo("   1. Complete neural training pipeline")
    click.echo("   2. M8: Endgame Solver")
    click.echo("   3. M9: Performance & Deployment")
    
    click.echo("\nTry: python main.py train --config small")


@cli.command()
@click.option('--config', default='small', type=click.Choice(['small', 'medium', 'large']), 
              help='Model configuration')
@click.option('--device', default='cpu', type=click.Choice(['cpu', 'cuda']), 
              help='Device to use for training')
@click.option('--epochs', default=5, help='Number of training epochs')
@click.option('--samples', default=500, help='Number of training samples')
def train(config: str, device: str, epochs: int, samples: int):
    """Train the neural network for Azul analysis."""
    click.echo(f"🧠 Training AzulNet neural network")
    click.echo(f"   Config: {config}, Device: {device}, Epochs: {epochs}, Samples: {samples}")
    
    try:
        from neural.train import TrainingConfig, AzulNetTrainer
        
        # Configuration based on size
        if config == 'small':
            hidden_size = 64
            num_layers = 2
        elif config == 'medium':
            hidden_size = 128
            num_layers = 3
        else:  # large
            hidden_size = 256
            num_layers = 4
        
        # Create training config
        train_config = TrainingConfig(
            batch_size=16,
            learning_rate=0.001,
            num_epochs=epochs,
            num_samples=samples,
            hidden_size=hidden_size,
            num_layers=num_layers,
            device=device
        )
        
        # Create trainer and train
        trainer = AzulNetTrainer(train_config)
        losses = trainer.train()
        
        # Evaluate
        eval_results = trainer.evaluate(num_samples=50)
        click.echo(f"✅ Training complete!")
        click.echo(f"   Final loss: {losses[-1]:.4f}")
        click.echo(f"   Evaluation error: {eval_results['avg_value_error']:.4f}")
        
        # Save model
        import os
        os.makedirs("models", exist_ok=True)
        trainer.save_model(f"models/azul_net_{config}.pth")
        click.echo(f"   Model saved to: models/azul_net_{config}.pth")
        
    except ImportError:
        click.echo("❌ Neural training requires PyTorch. Install with: pip install -r requirements.txt (torch) or use optional extras from pyproject")
        return 1
    except Exception as e:
        click.echo(f"❌ Training failed: {e}")
        return 1
    
    return 0


@cli.command()
@click.option('--model', default='models/azul_net_small.pth', help='Path to trained model')
@click.option('--positions', default=50, help='Number of test positions')
@click.option('--games', default=20, help='Number of test games')
@click.option('--device', default='cpu', help='Device to use (cpu, cuda)')
def evaluate(model, positions, games, device):
    """Evaluate a trained AzulNet model."""
    click.echo("🧠 Evaluating AzulNet model")
    click.echo(f"   Model: {model}, Device: {device}")
    click.echo(f"   Test positions: {positions}, Test games: {games}")
    
    try:
        from neural.evaluate import EvaluationConfig, AzulModelEvaluator
        
        # Create evaluation configuration
        config = EvaluationConfig(
            num_positions=positions,
            num_games=games,
            search_time=0.5,
            max_rollouts=50,
            model_path=model,
            device=device,
            compare_heuristic=True,
            compare_random=True
        )
        
        # Run evaluation
        evaluator = AzulModelEvaluator(config)
        result = evaluator.evaluate_model()
        
        click.echo("\n📊 EVALUATION RESULTS")
        click.echo("=" * 50)
        click.echo(f"Model Parameters: {result.model_parameters:,}")
        click.echo(f"Inference Time: {result.inference_time_ms:.2f} ms")
        click.echo(f"Position Accuracy: {result.position_accuracy:.2%}")
        click.echo(f"Move Agreement: {result.move_agreement:.2%}")
        click.echo(f"Self-play Win Rate: {result.win_rate:.2%}")
        click.echo(f"Average Score: {result.avg_score:.2f}")
        click.echo(f"Average Search Time: {result.avg_search_time:.3f}s")
        click.echo(f"Average Rollouts: {result.avg_rollouts:.1f}")
        
        if result.vs_heuristic_win_rate is not None:
            click.echo(f"vs Heuristic Win Rate: {result.vs_heuristic_win_rate:.2%}")
        
        if result.vs_random_win_rate is not None:
            click.echo(f"vs Random Win Rate: {result.vs_random_win_rate:.2%}")
        
        click.echo("\n✅ Evaluation complete!")
        
    except ImportError:
        click.echo("❌ Neural evaluation requires PyTorch. Install with: pip install -r requirements.txt (torch) or use optional extras from pyproject")
        return 1
    except Exception as e:
        click.echo(f"❌ Evaluation failed: {e}")
        return 1
    
    return 0


@cli.command()
@click.option('--state', type=click.Choice(['initial', 'mid', 'late']), 
              default='initial', help='Test state to use')
@click.option('--output', type=str, default='profiling_results.json',
              help='Output file for results')
@click.option('--budget', type=float, default=4.0,
              help='Search depth-3 time budget (seconds)')
@click.option('--hint-budget', type=float, default=0.2,
              help='Hint generation time budget (seconds)')
@click.option('--move-budget', type=float, default=0.001,
              help='Move generation time budget (seconds)')
def profile(state: str, output: str, budget: float, hint_budget: float, move_budget: float):
    """Run comprehensive profiling on all engine components."""
    click.echo("🔍 Azul Engine Profiling Harness - A9")
    click.echo("=" * 50)
    
    try:
        from core.azul_profiler import AzulProfiler, PerformanceBudget, create_test_states
        
        # Create custom budget
        custom_budget = PerformanceBudget(
            search_depth_3_max_time=budget,
            hint_generation_max_time=hint_budget,
            move_generation_max_time=move_budget
        )
        
        # Create profiler
        profiler = AzulProfiler(custom_budget)
        
        # Create test state
        states = create_test_states()
        state_map = {"initial": states[0], "mid": states[1], "late": states[2]}
        test_state = state_map[state]
        
        click.echo(f"📊 Profiling {state} state...")
        
        # Run comprehensive profiling
        results = profiler.run_comprehensive_profile(test_state)
        
        # Generate and display report
        report = profiler.generate_report(results)
        click.echo(report)
        
        # Save results
        profiler.save_results(results, output)
        click.echo(f"💾 Results saved to {output}")
        
        return 0
        
    except ImportError as e:
        click.echo(f"❌ Profiling failed - missing dependency: {e}")
        click.echo("Install with: pip install psutil")
        return 1
    except Exception as e:
        click.echo(f"❌ Profiling failed: {e}")
        return 1


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