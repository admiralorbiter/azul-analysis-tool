#!/usr/bin/env python3
"""
Test runner for position library and move execution tests.

This script runs the specific tests that were created to prevent the position
library and move execution issues that were fixed in the debugging session.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_position_library_tests():
    """Run the position library and move execution tests."""
    print("=" * 80)
    print("RUNNING POSITION LIBRARY AND MOVE EXECUTION TESTS")
    print("=" * 80)
    
    # List of test files to run
    test_files = [
        "tests/test_position_library_move_execution.py",
        "tests/test_api_position_library.py"
    ]
    
    # Additional test classes to run from existing files
    test_classes = [
        "tests.test_api.TestInteractiveGameAPI",
        "tests.test_core.TestAzulState",
        "tests.test_move_generator.TestMoveGenerator"
    ]
    
    all_passed = True
    
    # Run the new test files
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nRunning {test_file}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_file, "-v"
                ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - PASSED")
                else:
                    print(f"❌ {test_file} - FAILED")
                    print(result.stdout)
                    print(result.stderr)
                    all_passed = False
            except Exception as e:
                print(f"❌ {test_file} - ERROR: {e}")
                all_passed = False
        else:
            print(f"⚠️  {test_file} - NOT FOUND")
    
    # Run specific test classes from existing files
    for test_class in test_classes:
        print(f"\nRunning {test_class}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_class, "-v"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                print(f"✅ {test_class} - PASSED")
            else:
                print(f"❌ {test_class} - FAILED")
                print(result.stdout)
                print(result.stderr)
                all_passed = False
        except Exception as e:
            print(f"❌ {test_class} - ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL POSITION LIBRARY TESTS PASSED!")
    else:
        print("💥 SOME TESTS FAILED - CHECK THE OUTPUT ABOVE")
    print("=" * 80)
    
    return all_passed


def run_specific_issue_tests():
    """Run tests that specifically check for the issues we fixed."""
    print("\n" + "=" * 80)
    print("RUNNING SPECIFIC ISSUE TESTS")
    print("=" * 80)
    
    # Test the specific issues that were fixed
    specific_tests = [
        "tests/test_position_library_move_execution.py::TestGenerateSuccessorEdgeCases::test_generate_successor_with_empty_factory",
        "tests/test_position_library_move_execution.py::TestGenerateSuccessorEdgeCases::test_generate_successor_with_single_tile_type_factory",
        "tests/test_position_library_move_execution.py::TestGenerateSuccessorEdgeCases::test_generate_successor_with_missing_tile_types",
        "tests/test_position_library_move_execution.py::TestErrorHandling::test_key_error_handling",
        "tests/test_api_position_library.py::TestPositionLibraryAPI::test_execute_move_tile_type_mismatch",
        "tests/test_api_position_library.py::TestPositionLibraryAPI::test_execute_move_with_invalid_factory_data"
    ]
    
    all_passed = True
    
    for test_name in specific_tests:
        print(f"\nRunning {test_name}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_name, "-v"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
                print(result.stdout)
                print(result.stderr)
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL SPECIFIC ISSUE TESTS PASSED!")
    else:
        print("💥 SOME SPECIFIC ISSUE TESTS FAILED - CHECK THE OUTPUT ABOVE")
    print("=" * 80)
    
    return all_passed


def run_validation_tests():
    """Run validation tests to ensure our fixes are working."""
    print("\n" + "=" * 80)
    print("RUNNING VALIDATION TESTS")
    print("=" * 80)
    
    # Import and run validation tests
    try:
        from tests.test_position_library_move_execution import (
            TestFactoryTileCountValidation,
            TestTileTypeConsistency,
            TestComprehensiveMoveValidation
        )
        
        validation_classes = [
            TestFactoryTileCountValidation,
            TestTileTypeConsistency,
            TestComprehensiveMoveValidation
        ]
        
        all_passed = True
        
        for test_class in validation_classes:
            print(f"\nRunning {test_class.__name__}...")
            try:
                # Create test instance and run all methods
                test_instance = test_class()
                
                # Get all test methods
                test_methods = [method for method in dir(test_class) 
                              if method.startswith('test_')]
                
                for method_name in test_methods:
                    print(f"  Running {method_name}...")
                    try:
                        method = getattr(test_instance, method_name)
                        method()
                        print(f"    ✅ {method_name} - PASSED")
                    except Exception as e:
                        print(f"    ❌ {method_name} - FAILED: {e}")
                        all_passed = False
                        
            except Exception as e:
                print(f"❌ {test_class.__name__} - ERROR: {e}")
                all_passed = False
        
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 ALL VALIDATION TESTS PASSED!")
        else:
            print("💥 SOME VALIDATION TESTS FAILED - CHECK THE OUTPUT ABOVE")
        print("=" * 80)
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ Could not import validation tests: {e}")
        return False


def main():
    """Main function to run all position library tests."""
    print("Position Library and Move Execution Test Runner")
    print("This runner tests the fixes for the position library issues.")
    
    # Run all test categories
    test_results = []
    
    test_results.append(run_position_library_tests())
    test_results.append(run_specific_issue_tests())
    test_results.append(run_validation_tests())
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if all(test_results):
        print("🎉 ALL TESTS PASSED! The position library fixes are working correctly.")
        print("\nThe following issues have been tested and should be prevented:")
        print("- Factory tile count validation")
        print("- Tile type consistency between frontend and backend")
        print("- KeyError in generateSuccessor with missing tile types")
        print("- Move validation and execution")
        print("- State synchronization issues")
        print("- Error handling for invalid moves")
    else:
        print("💥 SOME TESTS FAILED! There may still be issues with the position library.")
        print("\nPlease check the test output above and fix any failing tests.")
    
    print("=" * 80)
    
    return all(test_results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 