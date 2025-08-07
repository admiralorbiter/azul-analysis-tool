#!/usr/bin/env python3
"""
Test script for Move Quality Assessment API

This script tests the move quality assessment API endpoints to verify functionality.
"""

import requests
import json
import sys
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:5000"

def test_move_quality_info():
    """Test the move quality info endpoint."""
    print("Testing /api/v1/move-quality-info...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/move-quality-info")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                system_info = data.get("system_info", {})
                print("✅ Move quality info endpoint working")
                print(f"   Tier thresholds: {system_info.get('tier_thresholds', {})}")
                print(f"   Scoring weights: {system_info.get('scoring_weights', {})}")
                return True
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error testing move quality info: {e}")
        return False


def test_assess_move_quality():
    """Test the assess move quality endpoint."""
    print("\nTesting /api/v1/assess-move-quality...")
    
    # Test data - using a simple game state
    test_data = {
        "state_fen": "start",  # Simple starting position
        "player_id": 0,
        "move_key": "factory_0_tile_blue_pattern_line_1"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/assess-move-quality",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                move_quality = data.get("move_quality", {})
                print("✅ Move quality assessment endpoint working")
                print(f"   Overall score: {move_quality.get('overall_score', 'N/A')}")
                print(f"   Quality tier: {move_quality.get('quality_tier', 'N/A')}")
                print(f"   Explanation: {move_quality.get('explanation', 'N/A')}")
                return True
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error testing move quality assessment: {e}")
        return False


def test_evaluate_all_moves():
    """Test the evaluate all moves endpoint."""
    print("\nTesting /api/v1/evaluate-all-moves...")
    
    # Test data - using a simple game state
    test_data = {
        "state_fen": "start",  # Simple starting position
        "player_id": 0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/evaluate-all-moves",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                assessment = data.get("assessment", {})
                print("✅ Evaluate all moves endpoint working")
                print(f"   Best moves: {assessment.get('best_moves', [])}")
                print(f"   Position complexity: {assessment.get('position_complexity', 'N/A')}")
                print(f"   Analysis confidence: {assessment.get('analysis_confidence', 'N/A')}")
                print(f"   Educational insights: {assessment.get('educational_insights', [])}")
                return True
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error testing evaluate all moves: {e}")
        return False


def main():
    """Run all move quality API tests."""
    print("🧪 Testing Move Quality Assessment API")
    print("=" * 50)
    
    # Test results
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_move_quality_info():
        tests_passed += 1
    
    if test_assess_move_quality():
        tests_passed += 1
    
    if test_evaluate_all_moves():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All move quality API tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 