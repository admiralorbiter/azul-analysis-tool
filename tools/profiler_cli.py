"""
Profiler CLI - A9 Implementation

This module provides CLI commands for the profiling harness:
- Run comprehensive profiling
- Generate performance reports
- Export results to various formats
- Monitor performance budgets
"""

import click
import json
import time
from pathlib import Path
from typing import Optional

from core.azul_profiler import AzulProfiler, create_test_states
from core.azul_model import AzulState


@click.group()
def profiler():
    """Azul Engine Profiling Harness - A9 Implementation."""
    pass


@profiler.command()
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
    from core.azul_profiler import PerformanceBudget
    
    click.echo("🔍 Azul Engine Profiling Harness")
    click.echo("=" * 50)
    
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


@profiler.command()
@click.option('--component', type=click.Choice(['search', 'mcts', 'move_gen', 'eval', 'endgame']),
              required=True, help='Component to profile')
@click.option('--state', type=click.Choice(['initial', 'mid', 'late']), 
              default='initial', help='Test state to use')
@click.option('--iterations', type=int, default=100,
              help='Number of iterations')
@click.option('--output', type=str, default='component_profile.json',
              help='Output file for results')
def profile_component(component: str, state: str, iterations: int, output: str):
    """Profile a specific engine component."""
    click.echo(f"🔍 Profiling {component} component...")
    
    # Create profiler
    profiler = AzulProfiler()
    
    # Create test state
    states = create_test_states()
    state_map = {"initial": states[0], "mid": states[1], "late": states[2]}
    test_state = state_map[state]
    
    # Profile specific component
    if component == "search":
        result = profiler.profile_search(test_state, depth=2)
    elif component == "mcts":
        result = profiler.profile_mcts(test_state, budget_ms=100)
    elif component == "move_gen":
        result = profiler.profile_move_generation(test_state)
    elif component == "eval":
        result = profiler.profile_evaluation(test_state)
    elif component == "endgame":
        result = profiler.profile_endgame(test_state)
    
    # Display result
    click.echo(f"📊 {component} Results:")
    click.echo(f"  Duration: {result.duration_ms:.2f}ms")
    click.echo(f"  Memory: {result.memory_mb:.2f}MB")
    click.echo(f"  CPU: {result.cpu_percent:.1f}%")
    click.echo(f"  Success: {result.success}")
    
    if result.error_message:
        click.echo(f"  Error: {result.error_message}")
    
    # Save result
    profiler.save_results([result], output)
    click.echo(f"💾 Results saved to {output}")


@profiler.command()
@click.option('--input', type=str, required=True,
              help='Input JSON file with profiling results')
@click.option('--format', type=click.Choice(['json', 'csv', 'markdown']),
              default='json', help='Output format')
@click.option('--output', type=str, default='report',
              help='Output file (without extension)')
def generate_report(input: str, format: str, output: str):
    """Generate a performance report from profiling results."""
    click.echo(f"📊 Generating {format} report from {input}...")
    
    # Load results
    with open(input, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    
    if format == 'json':
        # Already in JSON format
        output_file = f"{output}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    elif format == 'csv':
        import csv
        output_file = f"{output}.csv"
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Component', 'Operation', 'Duration (ms)', 'Memory (MB)', 
                           'CPU (%)', 'Iterations', 'Success', 'Error'])
            for result in results:
                writer.writerow([
                    result['component'],
                    result['operation'],
                    result['duration_ms'],
                    result['memory_mb'],
                    result['cpu_percent'],
                    result['iterations'],
                    result['success'],
                    result.get('error_message', '')
                ])
    
    elif format == 'markdown':
        output_file = f"{output}.md"
        with open(output_file, 'w') as f:
            f.write("# Azul Engine Performance Report\n\n")
            f.write(f"Generated from: {input}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            total = len(results)
            successful = sum(1 for r in results if r['success'])
            f.write(f"- Total tests: {total}\n")
            f.write(f"- Successful: {successful}\n")
            f.write(f"- Failed: {total - successful}\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Component | Operation | Duration (ms) | Memory (MB) | CPU (%) | Success |\n")
            f.write("|-----------|-----------|---------------|-------------|---------|---------|\n")
            
            for result in results:
                status = "✅" if result['success'] else "❌"
                f.write(f"| {result['component']} | {result['operation']} | "
                       f"{result['duration_ms']:.2f} | {result['memory_mb']:.2f} | "
                       f"{result['cpu_percent']:.1f} | {status} |\n")
    
    click.echo(f"💾 Report saved to {output_file}")


@profiler.command()
@click.option('--input', type=str, required=True,
              help='Input JSON file with profiling results')
@click.option('--threshold', type=float, default=1.0,
              help='Performance threshold multiplier (1.0 = exact budget)')
def check_budgets(input: str, threshold: float):
    """Check if performance budgets are met."""
    click.echo(f"🎯 Checking performance budgets (threshold: {threshold}x)...")
    
    # Load results
    with open(input, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    budget = data.get('budget', {})
    
    # Create profiler to check budgets
    profiler = AzulProfiler()
    
    # Convert results to ProfilingResult objects
    from core.azul_profiler import ProfilingResult
    profiling_results = []
    
    for result in results:
        profiling_results.append(ProfilingResult(
            component=result['component'],
            operation=result['operation'],
            duration_ms=result['duration_ms'],
            memory_mb=result['memory_mb'],
            cpu_percent=result['cpu_percent'],
            iterations=result['iterations'],
            success=result['success'],
            error_message=result.get('error_message')
        ))
    
    # Check budgets
    budgets_met = profiler.check_performance_budgets(profiling_results)
    
    click.echo("\n📊 Budget Analysis:")
    for budget_name, met in budgets_met.items():
        status = "✅" if met else "❌"
        click.echo(f"  {status} {budget_name}")
    
    # Summary
    total_budgets = len(budgets_met)
    met_budgets = sum(1 for met in budgets_met.values() if met)
    
    click.echo(f"\n📈 Summary: {met_budgets}/{total_budgets} budgets met")
    
    if met_budgets == total_budgets:
        click.echo("🎉 All performance budgets met!")
    else:
        click.echo("⚠️  Some performance budgets not met. Consider optimization.")


@profiler.command()
@click.option('--duration', type=int, default=30,
              help='Duration for py-spy profiling (seconds)')
@click.option('--output', type=str, default='py-spy-results.speedscope',
              help='Output file for py-spy results')
def py_spy(duration: int, output: str):
    """Run py-spy profiling and provide instructions."""
    click.echo("🔍 Py-Spy Profiling Instructions")
    click.echo("=" * 50)
    click.echo(f"Duration: {duration} seconds")
    click.echo(f"Output: {output}")
    click.echo()
    click.echo("Run the following command:")
    click.echo(f"py-spy record --duration {duration} --format speedscope --output {output} python -m core.azul_profiler --profile all")
    click.echo()
    click.echo("Then view the results at: https://www.speedscope.app/")


@profiler.command()
@click.option('--state', type=str, default='initial',
              help='State to analyze (FEN format or preset)')
@click.option('--depth', type=int, default=3,
              help='Search depth for analysis')
@click.option('--time-limit', type=float, default=4.0,
              help='Time limit for analysis (seconds)')
def analyze_position(state: str, depth: int, time_limit: float):
    """Analyze a specific position with performance metrics."""
    click.echo(f"🔍 Analyzing position with depth {depth}...")
    
    # Create test state (simplified - in real implementation would parse FEN)
    test_state = AzulState(2)
    
    # Create profiler
    profiler = AzulProfiler()
    
    # Profile search
    result = profiler.profile_search(test_state, depth=depth)
    
    click.echo(f"📊 Search Analysis Results:")
    click.echo(f"  Duration: {result.duration_ms:.2f}ms")
    click.echo(f"  Memory: {result.memory_mb:.2f}MB")
    click.echo(f"  CPU: {result.cpu_percent:.1f}%")
    click.echo(f"  Success: {result.success}")
    
    if result.success:
        search_result = result.additional_metrics.get('result')
        if search_result:
            click.echo(f"  Best Move: {search_result.best_move}")
            click.echo(f"  Score: {search_result.score}")
            click.echo(f"  PV Length: {len(search_result.pv)}")
    
    # Check if within budget
    budget_met = result.duration_ms <= time_limit * 1000
    status = "✅" if budget_met else "❌"
    click.echo(f"  Budget ({time_limit}s): {status}")


if __name__ == "__main__":
    profiler() 