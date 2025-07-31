#!/usr/bin/env python3
"""
CLI Test Examples - Run various test scenarios
"""

import subprocess
import sys
import time


def run_test(name, command, expected_timeout=10):
    """Run a test and report results."""
    print(f"\n{'='*50}")
    print(f"🧪 Test: {name}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*50}")
    
    try:
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True, timeout=expected_timeout)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            print(f"⏱️  Time: {elapsed:.2f}s")
            
            # Extract key information
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['Best move:', 'Nodes searched:', 'Search completed']):
                    print(f"📊 {line.strip()}")
        else:
            print("❌ FAILED")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")


def main():
    """Run various CLI test examples."""
    print("🚀 Azul CLI Test Examples")
    print("=" * 50)
    
    # Test 1: Basic status
    run_test("Project Status", [sys.executable, "main.py", "status"])
    
    # Test 2: Help
    run_test("Help Command", [sys.executable, "main.py", "exact", "--help"])
    
    # Test 3: Quick search
    run_test("Depth 1 Search", [
        sys.executable, "main.py", "exact", "initial", 
        "--depth", "1", "--timeout", "1.0"
    ])
    
    # Test 4: Medium search
    run_test("Depth 2 Search", [
        sys.executable, "main.py", "exact", "initial", 
        "--depth", "2", "--timeout", "2.0"
    ])
    
    # Test 5: Full search
    run_test("Depth 3 Search", [
        sys.executable, "main.py", "exact", "initial", 
        "--depth", "3", "--timeout", "5.0"
    ])
    
    # Test 6: Different agent
    run_test("Agent 1 Search", [
        sys.executable, "main.py", "exact", "initial", 
        "--depth", "2", "--agent", "1", "--timeout", "2.0"
    ])
    
    # Test 7: Error handling - invalid FEN
    run_test("Invalid FEN", [
        sys.executable, "main.py", "exact", "invalid", 
        "--depth", "1"
    ])
    
    # Test 8: Error handling - depth 0
    run_test("Depth 0", [
        sys.executable, "main.py", "exact", "initial", 
        "--depth", "0", "--timeout", "1.0"
    ])
    
    # Test 9: Short timeout
    run_test("Short Timeout", [
        sys.executable, "main.py", "exact", "initial", 
        "--depth", "3", "--timeout", "0.1"
    ])
    
    print(f"\n{'='*50}")
    print("🎉 All tests completed!")
    print("Check the output above for results.")


if __name__ == "__main__":
    main() 