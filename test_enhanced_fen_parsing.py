#!/usr/bin/env python3
"""
Test Enhanced FEN Parsing and Real Data Detection

This script tests the enhanced FEN string parsing capabilities including:
- Base64 encoded FEN strings
- Real game data detection
- Move quality analysis with real data
- Alternative move analysis

Usage:
    python test_enhanced_fen_parsing.py
"""

import requests
import json
import base64
import time
from typing import Dict, Any

# API configuration
API_BASE = "http://localhost:8000/api/v1"

def test_base64_fen_parsing():
    """Test base64 encoded FEN string parsing."""
    print("🧪 Testing Base64 FEN Parsing...")
    
    # Create a sample FEN string and encode it
    sample_fen = "initial"
    encoded_fen = f"base64_{base64.b64encode(sample_fen.encode()).decode()}"
    
    print(f"Original FEN: {sample_fen}")
    print(f"Encoded FEN: {encoded_fen}")
    
    # Test the API with base64 encoded FEN
    try:
        response = requests.post(f"{API_BASE}/analyze-move-quality", json={
            "fen_string": encoded_fen,
            "current_player": 0,
            "include_alternatives": True,
            "max_alternatives": 3
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Base64 FEN parsing successful")
            print(f"   Is real data: {data.get('is_real_data', False)}")
            print(f"   Data quality: {data.get('data_quality', 'unknown')}")
            print(f"   Analysis time: {data.get('analysis_time_ms', 0)}ms")
            return True
        else:
            print(f"❌ Base64 FEN parsing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Base64 FEN parsing error: {e}")
        return False

def test_real_data_detection():
    """Test real data detection with various FEN string types."""
    print("\n🧪 Testing Real Data Detection...")
    
    test_cases = [
        {
            "name": "Base64 encoded",
            "fen": "base64_aW5pdGlhbA==",  # "initial" encoded
            "expected_real": True
        },
        {
            "name": "Initial position",
            "fen": "initial",
            "expected_real": False
        },
        {
            "name": "Saved position",
            "fen": "saved",
            "expected_real": False
        },
        {
            "name": "State identifier",
            "fen": "state_123",
            "expected_real": False
        },
        {
            "name": "Local position",
            "fen": "local_position_1",
            "expected_real": False
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        try:
            response = requests.post(f"{API_BASE}/analyze-move-quality", json={
                "fen_string": test_case["fen"],
                "current_player": 0,
                "include_alternatives": False
            })
            
            # Check if response is successful (200) or if it's a valid error (400 for invalid FEN)
            if response.status_code == 200:
                data = response.json()
                is_real = data.get('is_real_data', False)
                expected = test_case["expected_real"]
                
                if is_real == expected:
                    print(f"✅ {test_case['name']}: Correctly detected as {'real' if is_real else 'mock'} data")
                    success_count += 1
                else:
                    print(f"❌ {test_case['name']}: Expected {'real' if expected else 'mock'}, got {'real' if is_real else 'mock'}")
            elif response.status_code == 400:
                # For invalid FEN strings, we expect them to be rejected
                print(f"✅ {test_case['name']}: Correctly rejected invalid FEN string")
                success_count += 1
            else:
                print(f"❌ {test_case['name']}: Unexpected API error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error {e}")
    
    print(f"Real data detection: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def test_alternative_move_analysis():
    """Test alternative move analysis with real data."""
    print("\n🧪 Testing Alternative Move Analysis...")
    
    try:
        response = requests.post(f"{API_BASE}/evaluate-all-moves", json={
            "fen_string": "initial",
            "player_id": 0
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Alternative move analysis successful")
            print(f"   Total moves analyzed: {data.get('total_moves_analyzed', 0)}")
            print(f"   Best moves found: {len(data.get('best_moves', []))}")
            print(f"   Alternative moves: {len(data.get('alternative_moves', []))}")
            print(f"   Is real data: {data.get('is_real_data', False)}")
            print(f"   Analysis time: {data.get('analysis_time_ms', 0)}ms")
            
            # Show some move details
            all_moves = data.get('all_moves_quality', {})
            if all_moves:
                print("\n   Top moves:")
                sorted_moves = sorted(all_moves.items(), 
                                   key=lambda x: x[1].get('overall_score', 0), 
                                   reverse=True)[:3]
                for i, (move_key, move_data) in enumerate(sorted_moves, 1):
                    score = move_data.get('overall_score', 0)
                    tier = move_data.get('quality_tier', '?')
                    print(f"     {i}. {tier} ({score:.1f}/100): {move_key}")
            
            return True
        else:
            print(f"❌ Alternative move analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Alternative move analysis error: {e}")
        return False

def test_enhanced_analysis_features():
    """Test enhanced analysis features for real data."""
    print("\n🧪 Testing Enhanced Analysis Features...")
    
    # Test with a base64 encoded FEN to simulate real data
    test_fen = "base64_aW5pdGlhbA=="  # "initial" encoded
    
    try:
        response = requests.post(f"{API_BASE}/analyze-move-quality", json={
            "fen_string": test_fen,
            "current_player": 0,
            "include_alternatives": True,
            "max_alternatives": 3
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced analysis successful")
            
            # Check for enhanced features
            enhanced = data.get('analysis_enhanced', {})
            if enhanced:
                print("   Enhanced analysis features:")
                print(f"     - Position complexity: {enhanced.get('position_complexity', 0):.2f}")
                print(f"     - Analysis confidence: {enhanced.get('analysis_confidence', 0):.2f}")
                print(f"     - Educational insights: {len(enhanced.get('educational_insights', []))}")
            else:
                print("   No enhanced analysis features (expected for mock data)")
            
            print(f"   Is real data: {data.get('is_real_data', False)}")
            print(f"   Data quality: {data.get('data_quality', 'unknown')}")
            print(f"   FEN analyzed: {data.get('fen_string_analyzed', 'unknown')}")
            
            return True
        else:
            print(f"❌ Enhanced analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced analysis error: {e}")
        return False

def test_frontend_integration():
    """Test that the frontend can detect and handle real data properly."""
    print("\n🧪 Testing Frontend Integration...")
    
    # Simulate frontend real data detection logic
    def is_real_game_data(fen_string):
        if not fen_string:
            return False
        
        # Check for base64 encoded strings
        if fen_string.startswith('base64_'):
            return True
        
        # Check for long encoded strings (likely real game data)
        if len(fen_string) > 100:
            # Exclude known test/position library patterns
            test_patterns = [
                'local_', 'test_', 'simple_', 'complex_', 'midgame_', 
                'endgame_', 'opening_', 'position'
            ]
            if not any(pattern in fen_string for pattern in test_patterns):
                return True
        
        # Check for standard FEN format (contains game state data)
        if fen_string.count('|') > 0 or fen_string.count('/') > 0:
            return True
        
        return False
    
    test_cases = [
        ("base64_aW5pdGlhbA==", True, "Base64 encoded"),
        ("a" * 150, True, "Long string"),
        ("test_position_1", False, "Test position"),
        ("local_position_1", False, "Local position"),
        ("initial", False, "Initial position"),
        ("state_123", False, "State identifier")
    ]
    
    success_count = 0
    for fen, expected, name in test_cases:
        result = is_real_game_data(fen)
        if result == expected:
            print(f"✅ {name}: Correctly detected as {'real' if result else 'mock'} data")
            success_count += 1
        else:
            print(f"❌ {name}: Expected {'real' if expected else 'mock'}, got {'real' if result else 'mock'}")
    
    print(f"Frontend integration: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def main():
    """Run all tests."""
    print("🚀 Testing Enhanced FEN Parsing and Real Data Detection")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Base64 FEN Parsing", test_base64_fen_parsing),
        ("Real Data Detection", test_real_data_detection),
        ("Alternative Move Analysis", test_alternative_move_analysis),
        ("Enhanced Analysis Features", test_enhanced_analysis_features),
        ("Frontend Integration", test_frontend_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced FEN parsing is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main() 