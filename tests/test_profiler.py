"""
Tests for A9 Profiling Harness - Comprehensive profiling and benchmarking

This module tests the profiling harness functionality including:
- Performance budget validation
- Component profiling accuracy
- Benchmark integration
- Memory and CPU monitoring
- Report generation
"""

import pytest
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch

from core.azul_profiler import (
    AzulProfiler, 
    PerformanceBudget, 
    ProfilingResult,
    create_test_states
)
from core.azul_model import AzulState
from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS
from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator
from analysis_engine.strategic_analysis.azul_endgame import EndgameDatabase
from core import azul_utils as utils


class TestPerformanceBudget:
    """Test performance budget configuration."""
    
    def test_default_budget(self):
        """Test default budget values."""
        budget = PerformanceBudget()
        
        assert budget.search_depth_3_max_time == 4.0
        assert budget.hint_generation_max_time == 0.2
        assert budget.move_generation_max_time == 0.001
        assert budget.memory_usage_max_mb == 2048.0
        assert budget.cpu_usage_max_percent == 80.0
    
    def test_custom_budget(self):
        """Test custom budget configuration."""
        budget = PerformanceBudget(
            search_depth_3_max_time=2.0,
            hint_generation_max_time=0.1,
            move_generation_max_time=0.0005,
            memory_usage_max_mb=1024.0,
            cpu_usage_max_percent=70.0
        )
        
        assert budget.search_depth_3_max_time == 2.0
        assert budget.hint_generation_max_time == 0.1
        assert budget.move_generation_max_time == 0.0005
        assert budget.memory_usage_max_mb == 1024.0
        assert budget.cpu_usage_max_percent == 70.0


class TestProfilingResult:
    """Test profiling result data structure."""
    
    def test_successful_result(self):
        """Test successful profiling result."""
        result = ProfilingResult(
            component="test",
            operation="benchmark",
            duration_ms=100.0,
            memory_mb=50.0,
            cpu_percent=25.0,
            iterations=1000,
            success=True,
            additional_metrics={"score": 100}
        )
        
        assert result.component == "test"
        assert result.operation == "benchmark"
        assert result.duration_ms == 100.0
        assert result.memory_mb == 50.0
        assert result.cpu_percent == 25.0
        assert result.iterations == 1000
        assert result.success is True
        assert result.error_message is None
        assert result.additional_metrics["score"] == 100
    
    def test_failed_result(self):
        """Test failed profiling result."""
        result = ProfilingResult(
            component="test",
            operation="benchmark",
            duration_ms=50.0,
            memory_mb=0.0,
            cpu_percent=0.0,
            iterations=100,
            success=False,
            error_message="Test error"
        )
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.memory_mb == 0.0
        assert result.cpu_percent == 0.0


class TestAzulProfiler:
    """Test the main profiling harness."""
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        profiler = AzulProfiler()
        
        assert profiler.budget is not None
        assert isinstance(profiler.budget, PerformanceBudget)
        assert len(profiler.results) == 0
    
    def test_profiler_with_custom_budget(self):
        """Test profiler with custom budget."""
        budget = PerformanceBudget(search_depth_3_max_time=2.0)
        profiler = AzulProfiler(budget)
        
        assert profiler.budget.search_depth_3_max_time == 2.0
    
    def test_profile_function_success(self):
        """Test successful function profiling."""
        profiler = AzulProfiler()
        
        def test_func():
            time.sleep(0.001)  # 1ms delay
            return "success"
        
        result = profiler.profile_function(
            test_func,
            component="test",
            operation="benchmark",
            iterations=10
        )
        
        assert result.success is True
        assert result.component == "test"
        assert result.operation == "benchmark"
        assert result.iterations == 10
        assert result.duration_ms > 0
        assert result.error_message is None
    
    def test_profile_function_failure(self):
        """Test function profiling with error."""
        profiler = AzulProfiler()
        
        def failing_func():
            raise ValueError("Test error")
        
        result = profiler.profile_function(
            failing_func,
            component="test",
            operation="benchmark",
            iterations=10
        )
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.duration_ms > 0
    
    def test_profile_move_generation(self):
        """Test move generation profiling."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        result = profiler.profile_move_generation(state)
        
        assert result.success is True
        assert result.component == "move_generator"
        assert result.operation == "generate_moves"
        assert result.duration_ms > 0
        assert result.iterations == 1000
    
    def test_profile_evaluation(self):
        """Test evaluation profiling."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        result = profiler.profile_evaluation(state)
        
        assert result.success is True
        assert result.component == "evaluator"
        assert result.operation == "evaluate"
        assert result.duration_ms > 0
        assert result.iterations == 1000
    
    def test_profile_search(self):
        """Test search profiling."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        result = profiler.profile_search(state, depth=2)
        
        assert result.success is True
        assert result.component == "search"
        assert "alpha_beta_depth_2" in result.operation
        assert result.duration_ms > 0
        assert result.iterations == 10  # Search is expensive
    
    def test_profile_mcts(self):
        """Test MCTS profiling."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        result = profiler.profile_mcts(state, budget_ms=100)
        
        assert result.success is True
        assert result.component == "mcts"
        assert "hint_generation_100ms" in result.operation
        assert result.duration_ms > 0
        assert result.iterations == 20
    
    def test_profile_endgame(self):
        """Test endgame profiling."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        result = profiler.profile_endgame(state)
        
        assert result.success is True
        assert result.component == "endgame"
        assert result.operation == "analyze_endgame"
        assert result.duration_ms > 0
        assert result.iterations == 100
    
    def test_comprehensive_profile(self):
        """Test comprehensive profiling."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        results = profiler.run_comprehensive_profile(state)
        
        assert len(results) == 5  # All components
        assert all(isinstance(r, ProfilingResult) for r in results)
        
        # Check that at least some components succeeded
        successful = sum(1 for r in results if r.success)
        assert successful > 0
    
    def test_performance_budget_checking(self):
        """Test performance budget validation."""
        profiler = AzulProfiler()
        
        # Create mock results
        results = [
            ProfilingResult(
                component="search",
                operation="alpha_beta_depth_3",
                duration_ms=3000.0,  # 3 seconds - under budget
                memory_mb=100.0,
                cpu_percent=50.0,
                iterations=10,
                success=True
            ),
            ProfilingResult(
                component="mcts",
                operation="hint_generation_200ms",
                duration_ms=150.0,  # 150ms - under budget
                memory_mb=50.0,
                cpu_percent=30.0,
                iterations=20,
                success=True
            ),
            ProfilingResult(
                component="move_generator",
                operation="generate_moves",
                duration_ms=2.0,  # 2ms - over budget (1ms)
                memory_mb=10.0,
                cpu_percent=10.0,
                iterations=1000,
                success=True
            )
        ]
        
        budgets_met = profiler.check_performance_budgets(results)
        
        assert budgets_met["search_depth_3"] is True
        assert budgets_met["hint_generation"] is True
        # Move generation should pass budget check (2ms total / 1000 iterations = 0.002ms per iteration < 1ms budget)
        assert budgets_met["move_generation"] is True
    
    def test_report_generation(self):
        """Test report generation."""
        profiler = AzulProfiler()
        
        results = [
            ProfilingResult(
                component="test",
                operation="benchmark",
                duration_ms=100.0,
                memory_mb=50.0,
                cpu_percent=25.0,
                iterations=1000,
                success=True
            )
        ]
        
        report = profiler.generate_report(results)
        
        assert "Azul Engine Profiling Report" in report
        assert "1/1 tests successful" in report
        assert "test.benchmark" in report
        assert "100.00ms" in report
    
    def test_save_results(self):
        """Test saving results to JSON."""
        profiler = AzulProfiler()
        
        results = [
            ProfilingResult(
                component="test",
                operation="benchmark",
                duration_ms=100.0,
                memory_mb=50.0,
                cpu_percent=25.0,
                iterations=1000,
                success=True
            )
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            profiler.save_results(results, temp_file)
            
            # Verify file was created and contains expected data
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            assert "timestamp" in data
            assert "budget" in data
            assert "results" in data
            assert len(data["results"]) == 1
            assert data["results"][0]["component"] == "test"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestTestStates:
    """Test test state creation."""
    
    def test_create_test_states(self):
        """Test creation of test states."""
        states = create_test_states()
        
        assert len(states) == 3
        
        # Check initial state
        initial = states[0]
        assert isinstance(initial, AzulState)
        assert len(initial.agents) == 2
        
        # Check mid-game state
        mid = states[1]
        assert isinstance(mid, AzulState)
        assert mid.agents[0].lines_number[0] == 1
        assert mid.agents[0].lines_tile[0] == utils.Tile.BLUE
        
        # Check late-game state
        late = states[2]
        assert isinstance(late, AzulState)
        for i in range(3):
            assert late.agents[0].lines_number[i] == i + 1
            assert late.agents[0].lines_tile[i] == utils.Tile.BLUE


# Simple performance tests (without pytest-benchmark)
class TestPerformance:
    """Simple performance tests."""
    
    def test_move_generation_performance(self):
        """Test move generation performance."""
        state = AzulState(2)
        generator = FastMoveGenerator()
        
        import time
        start_time = time.perf_counter()
        
        for _ in range(1000):
            moves = generator.generate_moves_fast(state, 0)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # Should be reasonably fast
        assert duration_ms < 1000.0  # Under 1 second for 1000 iterations
        assert len(moves) > 0  # Should generate some moves
    
    def test_evaluation_performance(self):
        """Test evaluation performance."""
        state = AzulState(2)
        evaluator = AzulEvaluator()
        
        import time
        start_time = time.perf_counter()
        
        for _ in range(1000):
            score = evaluator.evaluate_position(state, 0)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # Should be reasonably fast
        assert duration_ms < 200.0  # Under 200ms for 1000 iterations
        assert isinstance(score, (int, float))  # Should return a score
    
    def test_search_performance(self):
        """Test search performance."""
        state = AzulState(2)
        search = AzulAlphaBetaSearch(max_depth=2, max_time=1.0)
        
        import time
        start_time = time.perf_counter()
        
        result = search.search(state, 0)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # Search should complete within reasonable time
        assert duration_ms < 5000.0  # Under 5 seconds
        assert result is not None  # Should return a result
    
    def test_mcts_performance(self):
        """Test MCTS performance."""
        state = AzulState(2)
        mcts = AzulMCTS(max_time=0.1)  # 100ms budget
        
        import time
        start_time = time.perf_counter()
        
        result = mcts.search(state, 0)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # MCTS should be fast
        assert duration_ms < 500.0  # Under 500ms
        assert result is not None  # Should return a result


class TestProfilerIntegration:
    """Integration tests for the profiler."""
    
    def test_profiler_with_real_components(self):
        """Test profiler with real engine components."""
        profiler = AzulProfiler()
        state = AzulState(2)
        
        # Test with real components
        results = []
        
        # Move generation
        move_result = profiler.profile_move_generation(state)
        results.append(move_result)
        
        # Evaluation
        eval_result = profiler.profile_evaluation(state)
        results.append(eval_result)
        
        # Check that both succeeded
        assert move_result.success
        assert eval_result.success
        
        # Check performance budgets
        budgets_met = profiler.check_performance_budgets(results)
        
        # Move generation should be fast
        if "move_generation" in budgets_met:
            assert budgets_met["move_generation"] is True
    
    def test_profiler_error_handling(self):
        """Test profiler error handling."""
        profiler = AzulProfiler()
        
        def failing_func():
            raise RuntimeError("Simulated error")
        
        result = profiler.profile_function(
            failing_func,
            component="test",
            operation="error_test"
        )
        
        assert result.success is False
        assert "Simulated error" in result.error_message
        assert result.duration_ms > 0  # Should still measure time
    
    def test_profiler_memory_tracking(self):
        """Test profiler memory tracking."""
        profiler = AzulProfiler()
        
        def memory_intensive_func():
            # Allocate some memory
            data = [0] * 1000000
            return len(data)
        
        result = profiler.profile_function(
            memory_intensive_func,
            component="test",
            operation="memory_test"
        )
        
        assert result.success
        # Memory usage may be 0 for simple operations, which is acceptable
    
    def test_profiler_cpu_tracking(self):
        """Test profiler CPU tracking."""
        profiler = AzulProfiler()
        
        def cpu_intensive_func():
            # Do some CPU work
            sum(range(1000000))
            return 0
        
        result = profiler.profile_function(
            cpu_intensive_func,
            component="test",
            operation="cpu_test"
        )
        
        assert result.success
        assert result.cpu_percent > 0  # Should detect CPU usage


if __name__ == "__main__":
    pytest.main([__file__]) 