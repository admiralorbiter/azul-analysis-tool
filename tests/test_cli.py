#!/usr/bin/env python3
"""
Test script for CLI functionality.
"""

import subprocess
import sys
import time


def test_cli_commands():
    """Test the CLI commands."""
    print("🧪 Testing CLI functionality...")
    
    # Test status command
    print("\n1. Testing status command...")
    try:
        result = subprocess.run([sys.executable, "main.py", "status"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Status command works")
        else:
            print(f"❌ Status command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Status command timed out")
        return False
    
    # Test exact command with shallow search
    print("\n2. Testing exact command (depth 1)...")
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, "main.py", "exact", "initial", "--depth", "1", "--timeout", "1.0"], 
                              capture_output=True, text=True, timeout=5)
        search_time = time.time() - start_time
        
        if result.returncode == 0:
            print("✅ Exact command works (depth 1)")
            print(f"   Search time: {search_time:.2f}s")
            if "Best move:" in result.stdout:
                print("✅ Best move found")
            else:
                print("⚠️  No best move in output")
        else:
            print(f"❌ Exact command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Exact command timed out")
        return False
    
    # Test exact command with medium search
    print("\n3. Testing exact command (depth 2)...")
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, "main.py", "exact", "initial", "--depth", "2", "--timeout", "3.0"], 
                              capture_output=True, text=True, timeout=10)
        search_time = time.time() - start_time
        
        if result.returncode == 0:
            print("✅ Exact command works (depth 2)")
            print(f"   Search time: {search_time:.2f}s")
            if "Nodes searched:" in result.stdout:
                print("✅ Search statistics displayed")
            else:
                print("⚠️  No search statistics in output")
        else:
            print(f"❌ Exact command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Exact command timed out")
        return False
    
    # Test help command
    print("\n4. Testing help command...")
    try:
        result = subprocess.run([sys.executable, "main.py", "exact", "--help"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "Usage:" in result.stdout:
            print("✅ Help command works")
        else:
            print(f"❌ Help command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Help command timed out")
        return False
    
    print("\n🎉 All CLI tests passed!")
    return True


def test_error_handling():
    """Test error handling in CLI."""
    print("\n🧪 Testing error handling...")
    
    # Test invalid FEN
    print("\n1. Testing invalid FEN...")
    try:
        result = subprocess.run([sys.executable, "main.py", "exact", "invalid"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("✅ Invalid FEN properly rejected")
        else:
            print("⚠️  Invalid FEN not rejected")
    except subprocess.TimeoutExpired:
        print("❌ Invalid FEN test timed out")
        return False
    
    # Test invalid depth
    print("\n2. Testing invalid depth...")
    try:
        result = subprocess.run([sys.executable, "main.py", "exact", "initial", "--depth", "0"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ CLI handles depth 0 gracefully")
        else:
            print("⚠️  CLI rejected depth 0")
    except subprocess.TimeoutExpired:
        print("❌ Invalid depth test timed out")
        return False
    
    print("\n🎉 Error handling tests completed!")
    return True


if __name__ == "__main__":
    print("🚀 Azul CLI Test Suite")
    print("=" * 40)
    
    success = True
    success &= test_cli_commands()
    success &= test_error_handling()
    
    if success:
        print("\n✅ All tests passed! CLI is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 