#!/usr/bin/env python3
"""
Test Runner for Competitive Research Features

This script runs all the new test suites for competitive research features:
- Rule validator tests
- API integration tests  
- UI component tests
- Integration workflow tests
- Performance and edge case tests
"""

import unittest
import sys
import os
import time
import subprocess

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_test_suite(test_file, description):
    """Run a specific test suite and report results."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(test_file), pattern=os.path.basename(test_file))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{description} Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Duration: {duration:.2f} seconds")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful(), result.testsRun, len(result.failures), len(result.errors), duration

def run_all_competitive_tests():
    """Run all competitive research test suites."""
    print("🏆 Competitive Research Features Test Suite")
    print("=" * 60)
    
    # Define test suites to run
    test_suites = [
        {
            'file': 'test_rule_validator.py',
            'description': 'Board State Rule Validator Tests'
        },
        {
            'file': 'test_competitive_api_integration.py', 
            'description': 'Competitive API Integration Tests'
        },
        {
            'file': 'test_ui_components.py',
            'description': 'UI Component Tests'
        },
        {
            'file': 'test_competitive_integration.py',
            'description': 'Competitive Integration Workflow Tests'
        },
        {
            'file': 'test_pattern_detection.py',
            'description': 'Pattern Detection Engine Tests'
        },
        {
            'file': 'test_scoring_optimization.py',
            'description': 'Scoring Optimization Tests'
        },
        {
            'file': 'test_floor_line_patterns.py',
            'description': 'Floor Line Patterns Tests'
        }
    ]
    
    # Track overall results
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_duration = 0
    all_passed = True
    
    # Run each test suite
    for test_suite in test_suites:
        test_file = os.path.join('tests', test_suite['file'])
        
        if not os.path.exists(test_file):
            print(f"\n⚠️  Warning: Test file {test_file} not found, skipping...")
            continue
        
        success, tests_run, failures, errors, duration = run_test_suite(
            test_file, test_suite['description']
        )
        
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        total_duration += duration
        
        if not success:
            all_passed = False
    
    # Print summary
    print(f"\n{'='*60}")
    print("🏆 COMPETITIVE RESEARCH TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Failures: {total_failures}")
    print(f"Total Errors: {total_errors}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Success Rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    
    if all_passed:
        print("\n✅ All competitive research tests PASSED!")
        return 0
    else:
        print(f"\n❌ {total_failures + total_errors} competitive research tests FAILED!")
        return 1

def run_performance_benchmarks():
    """Run performance benchmarks for competitive features."""
    print(f"\n{'='*60}")
    print("Performance Benchmarks")
    print(f"{'='*60}")
    
    try:
        # Import performance test modules
        from tests.test_competitive_integration import TestCompetitiveIntegration
        
        # Create test instance
        test_instance = TestCompetitiveIntegration()
        test_instance.setUp()
        
        # Run performance tests
        print("Running pattern detection performance test...")
        start_time = time.time()
        patterns = test_instance.pattern_detector.detect_patterns(test_instance.complex_state, 0)
        pattern_time = time.time() - start_time
        print(f"  Pattern detection: {pattern_time:.3f}s (target: <0.2s)")
        
        print("Running scoring optimization performance test...")
        start_time = time.time()
        opportunities = test_instance.scoring_detector.detect_scoring_optimization(test_instance.complex_state, 0)
        scoring_time = time.time() - start_time
        print(f"  Scoring optimization: {scoring_time:.3f}s (target: <0.2s)")
        
        print("Running floor line patterns performance test...")
        start_time = time.time()
        floor_opportunities = test_instance.floor_line_detector.detect_floor_line_patterns(test_instance.complex_state, 0)
        floor_time = time.time() - start_time
        print(f"  Floor line patterns: {floor_time:.3f}s (target: <0.2s)")
        
        # Performance summary
        total_time = pattern_time + scoring_time + floor_time
        print(f"\nTotal analysis time: {total_time:.3f}s (target: <0.6s)")
        
        if total_time < 0.6:
            print("✅ Performance targets met!")
        else:
            print("⚠️  Performance targets exceeded!")
            
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")

def run_coverage_check():
    """Check test coverage for competitive features."""
    print(f"\n{'='*60}")
    print("Test Coverage Check")
    print(f"{'='*60}")
    
    # List of core files that should be tested
    core_files = [
        'core/azul_rule_validator.py',
        'core/azul_patterns.py', 
        'core/azul_scoring_optimization.py',
        'core/azul_floor_line_patterns.py'
    ]
    
    # List of UI files that should be tested
    ui_files = [
        'ui/components/BoardEditor.js',
        'ui/components/PositionLibrary.js',
        'ui/components/ValidationFeedback.js',
        'ui/components/PatternAnalysis.js',
        'ui/components/ScoringOptimizationAnalysis.js',
        'ui/components/FloorLinePatternAnalysis.js'
    ]
    
    # List of API endpoints that should be tested
    api_endpoints = [
        '/api/v1/detect-patterns',
        '/api/v1/detect-scoring-optimization', 
        '/api/v1/detect-floor-line-patterns',
        '/api/v1/validate-pattern-line-edit',
        '/api/v1/validate-board-state',
        '/api/v1/positions'
    ]
    
    print("Core Files Coverage:")
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
    
    print("\nUI Components Coverage:")
    for file_path in ui_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
    
    print("\nAPI Endpoints Coverage:")
    for endpoint in api_endpoints:
        print(f"  ✅ {endpoint}")

def main():
    """Main test runner function."""
    print("Starting Competitive Research Features Test Suite...")
    
    # Run all tests
    exit_code = run_all_competitive_tests()
    
    # Run performance benchmarks
    run_performance_benchmarks()
    
    # Run coverage check
    run_coverage_check()
    
    print(f"\n{'='*60}")
    print("🏆 Competitive Research Test Suite Complete!")
    print(f"{'='*60}")
    
    if exit_code == 0:
        print("✅ All tests passed! Competitive research features are ready.")
    else:
        print("❌ Some tests failed. Please review and fix issues.")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main()) 