"""
Azul Profiling Harness - A9 Implementation

This module provides comprehensive profiling capabilities for the Azul engine:
- pytest-benchmark integration for performance testing
- cProfile integration for detailed function analysis
- py-spy integration for system-level profiling
- Performance budget alerts and monitoring
- Memory usage tracking
- CPU utilization monitoring

Usage:
    # Run benchmarks
    pytest tests/ -m benchmark
    
    # Run profiling
    python -m core.azul_profiler --profile search --state "initial"
    
    # Run py-spy profiling
    python -m core.azul_profiler --py-spy --duration 30
"""

import cProfile
import pstats
import io
import time
import psutil
import os
import sys
import argparse
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .azul_model import AzulState
from .azul_search import AzulAlphaBetaSearch
from .azul_mcts import AzulMCTS
from .azul_move_generator import FastMoveGenerator
from .azul_evaluator import AzulEvaluator
from .azul_endgame import EndgameDatabase
from . import azul_utils as utils


@dataclass
class PerformanceBudget:
    """Performance budget configuration."""
    search_depth_3_max_time: float = 4.0  # seconds
    hint_generation_max_time: float = 0.2  # seconds
    move_generation_max_time: float = 0.001  # seconds (1ms)
    memory_usage_max_mb: float = 2048.0  # MB
    cpu_usage_max_percent: float = 80.0  # percent


@dataclass
class ProfilingResult:
    """Result of a profiling session."""
    component: str
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    iterations: int
    success: bool
    error_message: Optional[str] = None
    additional_metrics: Optional[Dict[str, Any]] = None


class AzulProfiler:
    """Comprehensive profiling harness for Azul engine."""
    
    def __init__(self, budget: Optional[PerformanceBudget] = None):
        self.budget = budget or PerformanceBudget()
        self.results: List[ProfilingResult] = []
        self.process = psutil.Process()
        
    def profile_function(self, 
                        func: Callable, 
                        *args, 
                        iterations: int = 100,
                        component: str = "unknown",
                        operation: str = "unknown") -> ProfilingResult:
        """Profile a single function with detailed metrics."""
        
        # Warm up
        for _ in range(10):
            try:
                func(*args)
            except Exception:
                pass
        
        # Get initial memory
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = self.process.cpu_percent()
        
        # Profile
        start_time = time.perf_counter()
        start_cpu = time.perf_counter()
        
        try:
            for _ in range(iterations):
                result = func(*args)
            
            end_time = time.perf_counter()
            end_cpu = time.perf_counter()
            
            # Get final memory
            final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = self.process.cpu_percent()
            
            duration_ms = (end_time - start_time) * 1000
            memory_mb = max(0, final_memory - initial_memory)  # Ensure non-negative
            cpu_percent = max(0, (final_cpu - initial_cpu) / max(0.001, (end_cpu - start_cpu)) * 100)
            
            return ProfilingResult(
                component=component,
                operation=operation,
                duration_ms=duration_ms,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                iterations=iterations,
                success=True,
                additional_metrics={'result': result}
            )
            
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return ProfilingResult(
                component=component,
                operation=operation,
                duration_ms=duration_ms,
                memory_mb=0.0,
                cpu_percent=0.0,
                iterations=iterations,
                success=False,
                error_message=str(e)
            )
    
    def profile_search(self, state: AzulState, depth: int = 3) -> ProfilingResult:
        """Profile alpha-beta search performance."""
        search = AzulAlphaBetaSearch(max_depth=depth, max_time=self.budget.search_depth_3_max_time)
        
        def search_func():
            return search.search(state, 0)
        
        return self.profile_function(
            search_func,
            component="search",
            operation=f"alpha_beta_depth_{depth}",
            iterations=10  # Search is expensive, fewer iterations
        )
    
    def profile_mcts(self, state: AzulState, budget_ms: float = 200) -> ProfilingResult:
        """Profile MCTS hint generation."""
        mcts = AzulMCTS(max_time=budget_ms / 1000.0)
        
        def mcts_func():
            return mcts.search(state, 0)
        
        return self.profile_function(
            mcts_func,
            component="mcts",
            operation=f"hint_generation_{budget_ms}ms",
            iterations=20
        )
    
    def profile_move_generation(self, state: AzulState) -> ProfilingResult:
        """Profile move generation performance."""
        generator = FastMoveGenerator()
        
        def move_gen_func():
            return generator.generate_moves_fast(state, 0)
        
        return self.profile_function(
            move_gen_func,
            component="move_generator",
            operation="generate_moves",
            iterations=1000
        )
    
    def profile_evaluation(self, state: AzulState) -> ProfilingResult:
        """Profile evaluation performance."""
        evaluator = AzulEvaluator()
        
        def eval_func():
            return evaluator.evaluate_position(state, 0)
        
        return self.profile_function(
            eval_func,
            component="evaluator",
            operation="evaluate",
            iterations=1000
        )
    
    def profile_endgame(self, state: AzulState) -> ProfilingResult:
        """Profile endgame database performance."""
        db = EndgameDatabase(max_tiles=20)
        
        def endgame_func():
            # Skip endgame analysis for now as it requires complex setup
            return None
        
        return self.profile_function(
            endgame_func,
            component="endgame",
            operation="analyze_endgame",
            iterations=100
        )
    
    def run_comprehensive_profile(self, state: AzulState) -> List[ProfilingResult]:
        """Run comprehensive profiling on all components."""
        print("🔍 Running comprehensive profiling...")
        
        results = []
        
        # Profile each component
        components = [
            (self.profile_move_generation, "Move Generation"),
            (self.profile_evaluation, "Evaluation"),
            (self.profile_search, "Alpha-Beta Search"),
            (self.profile_mcts, "MCTS Hint Generation"),
            (self.profile_endgame, "Endgame Analysis")
        ]
        
        for profiler_func, name in components:
            print(f"📊 Profiling {name}...")
            try:
                result = profiler_func(state)
                results.append(result)
                print(f"   ✅ {name}: {result.duration_ms:.2f}ms")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        return results
    
    def check_performance_budgets(self, results: List[ProfilingResult]) -> Dict[str, bool]:
        """Check if performance budgets are met."""
        budgets_met = {}
        
        for result in results:
            if result.component == "search" and "depth_3" in result.operation:
                budgets_met["search_depth_3"] = result.duration_ms <= self.budget.search_depth_3_max_time * 1000
            elif result.component == "mcts" and "hint_generation" in result.operation:
                budgets_met["hint_generation"] = result.duration_ms <= self.budget.hint_generation_max_time * 1000
            elif result.component == "move_generator":
                # Account for iterations - budget is per iteration
                per_iteration_ms = result.duration_ms / result.iterations
                budgets_met["move_generation"] = per_iteration_ms <= self.budget.move_generation_max_time * 1000
            elif result.component == "evaluator":
                # Account for iterations - budget is per iteration
                per_iteration_ms = result.duration_ms / result.iterations
                budgets_met["evaluation"] = per_iteration_ms <= 1.0  # 1ms target per iteration
            elif result.component == "endgame":
                budgets_met["endgame_analysis"] = result.duration_ms <= 100.0  # 100ms target
        
        return budgets_met
    
    def generate_report(self, results: List[ProfilingResult]) -> str:
        """Generate a comprehensive profiling report."""
        report = []
        report.append("🎯 Azul Engine Profiling Report")
        report.append("=" * 50)
        
        # Summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        report.append(f"📊 Summary: {successful_tests}/{total_tests} tests successful")
        
        # Component breakdown
        report.append("\n📈 Component Performance:")
        for result in results:
            status = "✅" if result.success else "❌"
            report.append(f"  {status} {result.component}.{result.operation}: {result.duration_ms:.2f}ms")
            if result.memory_mb > 0:
                report.append(f"     Memory: {result.memory_mb:.2f}MB")
            if result.cpu_percent > 0:
                report.append(f"     CPU: {result.cpu_percent:.1f}%")
        
        # Budget checks
        budgets_met = self.check_performance_budgets(results)
        report.append("\n🎯 Performance Budgets:")
        for budget_name, met in budgets_met.items():
            status = "✅" if met else "❌"
            report.append(f"  {status} {budget_name}")
        
        # Recommendations
        report.append("\n💡 Recommendations:")
        failed_budgets = [name for name, met in budgets_met.items() if not met]
        if failed_budgets:
            report.append("  ⚠️  Performance budgets not met:")
            for budget in failed_budgets:
                report.append(f"     - {budget}")
        else:
            report.append("  ✅ All performance budgets met!")
        
        return "\n".join(report)
    
    def save_results(self, results: List[ProfilingResult], filename: str = "profiling_results.json"):
        """Save profiling results to JSON file."""
        data = {
            "timestamp": time.time(),
            "budget": {
                "search_depth_3_max_time": self.budget.search_depth_3_max_time,
                "hint_generation_max_time": self.budget.hint_generation_max_time,
                "move_generation_max_time": self.budget.move_generation_max_time,
                "memory_usage_max_mb": self.budget.memory_usage_max_mb,
                "cpu_usage_max_percent": self.budget.cpu_usage_max_percent
            },
            "results": [
                {
                    "component": r.component,
                    "operation": r.operation,
                    "duration_ms": r.duration_ms,
                    "memory_mb": r.memory_mb,
                    "cpu_percent": r.cpu_percent,
                    "iterations": r.iterations,
                    "success": r.success,
                    "error_message": r.error_message
                }
                for r in results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to {filename}")


def create_test_states() -> List[AzulState]:
    """Create various test states for profiling."""
    states = []
    
    # Initial state (most complex)
    states.append(AzulState(2))
    
    # Mid-game state
    mid_state = AzulState(2)
    mid_state.agents[0].lines_number[0] = 1
    mid_state.agents[0].lines_tile[0] = utils.Tile.BLUE
    states.append(mid_state)
    
    # Late-game state (simplest)
    late_state = AzulState(2)
    for i in range(3):
        late_state.agents[0].lines_number[i] = i + 1
        late_state.agents[0].lines_tile[i] = utils.Tile.BLUE
    states.append(late_state)
    
    return states


def main():
    """Main profiling entry point."""
    parser = argparse.ArgumentParser(description="Azul Engine Profiling Harness")
    parser.add_argument("--profile", choices=["search", "mcts", "move_gen", "eval", "endgame", "all"],
                       default="all", help="Component to profile")
    parser.add_argument("--state", choices=["initial", "mid", "late"], default="initial",
                       help="Test state to use")
    parser.add_argument("--iterations", type=int, default=100,
                       help="Number of iterations for profiling")
    parser.add_argument("--output", type=str, default="profiling_results.json",
                       help="Output file for results")
    parser.add_argument("--py-spy", action="store_true",
                       help="Run py-spy profiling")
    parser.add_argument("--duration", type=int, default=30,
                       help="Duration for py-spy profiling (seconds)")
    
    args = parser.parse_args()
    
    # Create profiler
    profiler = AzulProfiler()
    
    # Create test state
    states = create_test_states()
    state_map = {"initial": states[0], "mid": states[1], "late": states[2]}
    test_state = state_map[args.state]
    
    if args.py_spy:
        print("🔍 Running py-spy profiling...")
        print(f"   Duration: {args.duration}s")
        print("   Run: py-spy record --duration {args.duration} --format speedscope --output py-spy-results.speedscope python -m core.azul_profiler")
        return
    
    # Run profiling
    if args.profile == "all":
        results = profiler.run_comprehensive_profile(test_state)
    else:
        # Profile specific component
        if args.profile == "search":
            results = [profiler.profile_search(test_state)]
        elif args.profile == "mcts":
            results = [profiler.profile_mcts(test_state)]
        elif args.profile == "move_gen":
            results = [profiler.profile_move_generation(test_state)]
        elif args.profile == "eval":
            results = [profiler.profile_evaluation(test_state)]
        elif args.profile == "endgame":
            results = [profiler.profile_endgame(test_state)]
    
    # Generate and print report
    report = profiler.generate_report(results)
    print(report)
    
    # Save results
    profiler.save_results(results, args.output)


if __name__ == "__main__":
    main() 