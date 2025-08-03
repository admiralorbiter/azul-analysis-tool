#!/usr/bin/env python3
"""
Test script for Strategic Analysis API endpoints.

This script tests all the strategic pattern analysis API endpoints
to ensure they are working correctly.
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:5000/api/v1"

def create_test_fen():
    """Create a test FEN string for strategic analysis."""
    # This is a simplified test FEN - in practice, you'd use a real game state
    return "test_fen_string_for_strategic_analysis"

def test_factory_control_endpoint():
    """Test the factory control detection endpoint."""
    print("🧪 Testing Factory Control Detection Endpoint...")
    
    url = f"{BASE_URL}/detect-factory-control"
    data = {
        "fen_string": create_test_fen(),
        "player_id": 0,
        "timeout": 5
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Factory Control Detection Successful")
            print(f"Cache Hit: {result.get('cache_hit', False)}")
            print(f"Analysis Time: {result.get('analysis_time', 0):.3f}s")
            print(f"Opportunities Found: {len(result.get('opportunities', []))}")
            return True
        else:
            print(f"❌ Factory Control Detection Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing factory control endpoint: {e}")
        return False

def test_endgame_scenarios_endpoint():
    """Test the endgame scenarios analysis endpoint."""
    print("\n🧪 Testing Endgame Scenarios Analysis Endpoint...")
    
    url = f"{BASE_URL}/analyze-endgame-scenarios"
    data = {
        "fen_string": create_test_fen(),
        "player_id": 0,
        "timeout": 10
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endgame Scenarios Analysis Successful")
            print(f"Cache Hit: {result.get('cache_hit', False)}")
            print(f"Analysis Time: {result.get('analysis_time', 0):.3f}s")
            print(f"Scenarios Found: {len(result.get('scenarios', []))}")
            return True
        else:
            print(f"❌ Endgame Scenarios Analysis Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endgame scenarios endpoint: {e}")
        return False

def test_risk_reward_endpoint():
    """Test the risk/reward analysis endpoint."""
    print("\n🧪 Testing Risk/Reward Analysis Endpoint...")
    
    url = f"{BASE_URL}/analyze-risk-reward"
    data = {
        "fen_string": create_test_fen(),
        "player_id": 0,
        "timeout": 8
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Risk/Reward Analysis Successful")
            print(f"Cache Hit: {result.get('cache_hit', False)}")
            print(f"Analysis Time: {result.get('analysis_time', 0):.3f}s")
            print(f"Scenarios Found: {len(result.get('scenarios', []))}")
            return True
        else:
            print(f"❌ Risk/Reward Analysis Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing risk/reward endpoint: {e}")
        return False

def test_comprehensive_strategic_analysis():
    """Test the comprehensive strategic pattern analysis endpoint."""
    print("\n🧪 Testing Comprehensive Strategic Analysis Endpoint...")
    
    url = f"{BASE_URL}/analyze-strategic-patterns"
    data = {
        "fen_string": create_test_fen(),
        "player_id": 0,
        "timeout": 15,
        "include_factory_control": True,
        "include_endgame_scenarios": True,
        "include_risk_reward": True
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Comprehensive Strategic Analysis Successful")
            print(f"Cache Hit: {result.get('cache_hit', False)}")
            print(f"Analysis Time: {result.get('analysis_time', 0):.3f}s")
            
            strategic_analysis = result.get('strategic_analysis', {})
            print(f"Factory Control Opportunities: {len(strategic_analysis.get('factory_control_opportunities', []))}")
            print(f"Endgame Scenarios: {len(strategic_analysis.get('endgame_scenarios', []))}")
            print(f"Risk/Reward Scenarios: {len(strategic_analysis.get('risk_reward_scenarios', []))}")
            return True
        else:
            print(f"❌ Comprehensive Strategic Analysis Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing comprehensive strategic analysis endpoint: {e}")
        return False

def test_strategic_report_endpoint():
    """Test the strategic analysis report generation endpoint."""
    print("\n🧪 Testing Strategic Analysis Report Endpoint...")
    
    url = f"{BASE_URL}/strategic-analysis/report"
    data = {
        "fen_string": create_test_fen(),
        "player_id": 0,
        "format": "text"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Strategic Analysis Report Generation Successful")
            print(f"Report Format: {result.get('format', 'text')}")
            print(f"Report Length: {len(result.get('report', ''))} characters")
            return True
        else:
            print(f"❌ Strategic Analysis Report Generation Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing strategic report endpoint: {e}")
        return False

def test_cache_endpoints():
    """Test the cache management endpoints."""
    print("\n🧪 Testing Cache Management Endpoints...")
    
    # Test cache stats
    try:
        response = requests.get(f"{BASE_URL}/strategic-analysis/cache/stats")
        print(f"Cache Stats Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cache Stats Retrieved Successfully")
            print(f"Cache Size: {result.get('cache_size', 0)}")
            print(f"Cache Hit Rate: {result.get('cache_hit_rate', 0):.2%}")
        else:
            print(f"❌ Cache Stats Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing cache stats endpoint: {e}")
    
    # Test cache clear
    try:
        response = requests.post(f"{BASE_URL}/strategic-analysis/cache/clear")
        print(f"Cache Clear Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cache Clear Successful")
            print(f"Cleared Entries: {result.get('cleared_entries', 0)}")
        else:
            print(f"❌ Cache Clear Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing cache clear endpoint: {e}")

def main():
    """Run all strategic analysis API tests."""
    print("🚀 STRATEGIC ANALYSIS API TESTING")
    print("=" * 50)
    
    # Check if API server is running
    try:
        health_response = requests.get("http://localhost:5000/healthz")
        if health_response.status_code != 200:
            print("❌ API server is not running. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to API server. Please start the server first.")
        return
    
    print("✅ API server is running")
    print()
    
    # Run all tests
    tests = [
        test_factory_control_endpoint,
        test_endgame_scenarios_endpoint,
        test_risk_reward_endpoint,
        test_comprehensive_strategic_analysis,
        test_strategic_report_endpoint,
        test_cache_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL STRATEGIC ANALYSIS API TESTS PASSED!")
        print("✅ Week 2 (API Integration) is ready for testing!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 