#!/usr/bin/env python3
"""
Test script for the Linear Programming Optimizer.

This script tests the basic functionality of the AzulLinearOptimizer
to ensure it can be imported and used correctly.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_linear_optimizer_import():
    """Test that the linear optimizer can be imported."""
    try:
        from analysis_engine.mathematical_optimization.linear_optimizer import (
            AzulLinearOptimizer, OptimizationObjective, OptimizationResult
        )
        print("✅ Linear optimizer imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import linear optimizer: {e}")
        return False

def test_optimizer_creation():
    """Test that the optimizer can be created."""
    try:
        from analysis_engine.mathematical_optimization.linear_optimizer import AzulLinearOptimizer
        
        optimizer = AzulLinearOptimizer()
        print("✅ Optimizer created successfully")
        print(f"   - Solver: {optimizer.solver_name}")
        print(f"   - Time limit: {optimizer.time_limit}s")
        print(f"   - Verbose: {optimizer.verbose}")
        return True
    except Exception as e:
        print(f"❌ Failed to create optimizer: {e}")
        return False

def test_optimization_objectives():
    """Test that optimization objectives are properly defined."""
    try:
        from analysis_engine.mathematical_optimization.linear_optimizer import OptimizationObjective
        
        objectives = [
            OptimizationObjective.MAXIMIZE_SCORING,
            OptimizationObjective.MINIMIZE_PENALTY,
            OptimizationObjective.BALANCE_SCORING_PENALTY,
            OptimizationObjective.MAXIMIZE_WALL_COMPLETION,
            OptimizationObjective.OPTIMIZE_RESOURCE_ALLOCATION
        ]
        
        print("✅ Optimization objectives defined:")
        for obj in objectives:
            print(f"   - {obj.name}: {obj.value}")
        return True
    except Exception as e:
        print(f"❌ Failed to test optimization objectives: {e}")
        return False

def test_optimization_result():
    """Test that OptimizationResult can be created."""
    try:
        from analysis_engine.mathematical_optimization.linear_optimizer import OptimizationResult
        
        result = OptimizationResult(
            objective_value=25.0,
            optimal_moves=[{'move_type': 'factory_to_pattern_line'}],
            constraint_violations=[],
            optimization_time=1.5,
            solver_status='Optimal',
            confidence_score=0.8,
            recommendations=['Focus on factory moves']
        )
        
        print("✅ OptimizationResult created successfully")
        print(f"   - Objective value: {result.objective_value}")
        print(f"   - Optimal moves: {len(result.optimal_moves)}")
        print(f"   - Confidence: {result.confidence_score}")
        return True
    except Exception as e:
        print(f"❌ Failed to create OptimizationResult: {e}")
        return False

def test_pulp_import():
    """Test that PuLP can be imported."""
    try:
        import pulp
        print("✅ PuLP imported successfully")
        print(f"   - Version: {pulp.__version__}")
        return True
    except Exception as e:
        print(f"❌ Failed to import PuLP: {e}")
        return False

def test_api_endpoint_import():
    """Test that the API endpoint can be imported."""
    try:
        from api.routes.optimization import optimization_bp
        print("✅ Optimization API blueprint imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import optimization API: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Linear Programming Optimizer Implementation")
    print("=" * 60)
    
    tests = [
        ("PuLP Import", test_pulp_import),
        ("Linear Optimizer Import", test_linear_optimizer_import),
        ("Optimizer Creation", test_optimizer_creation),
        ("Optimization Objectives", test_optimization_objectives),
        ("Optimization Result", test_optimization_result),
        ("API Endpoint Import", test_api_endpoint_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Linear optimizer implementation is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 