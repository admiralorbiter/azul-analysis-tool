#!/usr/bin/env python3
"""
Test script for Move Quality Assessment Slice 1

This script tests the end-to-end functionality of the move quality assessment system:
1. Backend move analysis engine
2. API endpoint
3. Basic integration

Run with: python test_move_quality_slice.py
"""

import sys
import os
import json
import time

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_analysis():
    """Test the backend move quality analysis engine directly."""
    print("🔍 Testing Backend Move Quality Analysis Engine...")
    
    try:
        from core.azul_move_analyzer import AzulMoveQualityAssessor
        from core.azul_model import AzulState
        
        # Create test state
        test_state = AzulState(2)  # 2-player game
        
        # Create assessor
        assessor = AzulMoveQualityAssessor()
        
        # Analyze position
        start_time = time.time()
        analysis = assessor.analyze_position(test_state, player_id=0)
        analysis_time = time.time() - start_time
        
        # Validate results
        assert analysis.primary_recommendation is not None, "No primary recommendation"
        assert analysis.primary_recommendation.quality_tier in ['!!', '!', '=', '?!', '?'], f"Invalid quality tier: {analysis.primary_recommendation.quality_tier}"
        assert 0 <= analysis.primary_recommendation.quality_score <= 100, f"Invalid quality score: {analysis.primary_recommendation.quality_score}"
        assert analysis.total_moves_analyzed > 0, "No moves analyzed"
        
        print(f"   ✅ Backend analysis working!")
        print(f"   📊 Analyzed {analysis.total_moves_analyzed} moves in {analysis_time:.3f}s")
        print(f"   🎯 Best move: {analysis.primary_recommendation.quality_tier} ({analysis.primary_recommendation.quality_score:.1f}/100)")
        print(f"   📝 Reason: {analysis.primary_recommendation.primary_reason}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Backend test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Test the API endpoint integration."""
    print("\n🌐 Testing API Integration...")
    
    try:
        import requests
        
        # Test the info endpoint first
        print("   Testing system info endpoint...")
        response = requests.get('http://localhost:8000/api/v1/move-quality-info')
        
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ System info endpoint working!")
            print(f"   📋 System: {info['system_info']['name']}")
            print(f"   🔧 Capabilities: {len(info['system_info']['capabilities'])} features")
        else:
            print(f"   ⚠️ System info endpoint returned {response.status_code}")
        
        # Test the analysis endpoint
        print("   Testing move quality analysis endpoint...")
        test_payload = {
            "fen_string": "initial",  # Use basic initial position
            "current_player": 0,
            "include_alternatives": True,
            "max_alternatives": 3
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/analyze-move-quality',
            json=test_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print(f"   ✅ API analysis endpoint working!")
                print(f"   📊 Analyzed {data['total_moves_analyzed']} moves in {data.get('analysis_time_ms', 0)}ms")
                
                primary = data['primary_recommendation']
                print(f"   🎯 Best move: {primary['quality_tier']} ({primary['quality_score']}/100)")
                print(f"   📝 Reason: {primary['primary_reason']}")
                
                if data['alternatives']:
                    print(f"   🔄 {len(data['alternatives'])} alternatives provided")
                
                return True
            else:
                print(f"   ❌ API returned success=false: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ API endpoint returned {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   📝 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️ Could not connect to API server. Make sure it's running on http://localhost:8000")
        print("   💡 Start server with: python main.py serve")
        return False
    except Exception as e:
        print(f"   ❌ API test failed: {str(e)}")
        return False

def test_component_dependencies():
    """Test that component dependencies are available."""
    print("\n🔧 Testing Component Dependencies...")
    
    try:
        # Test that existing pattern detectors are available
        from core.azul_patterns import AzulPatternDetector
        from core.azul_scoring_optimization import AzulScoringOptimizationDetector
        from core.azul_floor_line_patterns import AzulFloorLinePatternDetector
        
        print("   ✅ Pattern detection systems available")
        
        # Test move generator
        from core.azul_move_generator import AzulMoveGenerator
        print("   ✅ Move generator available")
        
        # Test that all components initialize
        pattern_detector = AzulPatternDetector()
        scoring_detector = AzulScoringOptimizationDetector() 
        floor_detector = AzulFloorLinePatternDetector()
        move_generator = AzulMoveGenerator()
        
        print("   ✅ All components initialize successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Dependency test failed: {str(e)}")
        return False

def main():
    """Run all tests for the move quality assessment slice."""
    print("🎯 Move Quality Assessment - Slice 1 Testing")
    print("=" * 50)
    
    # Run tests
    backend_ok = test_backend_analysis()
    deps_ok = test_component_dependencies()
    api_ok = test_api_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Backend Engine: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"   API Integration: {'✅ PASS' if api_ok else '⚠️ SKIP/FAIL'}")
    
    if backend_ok and deps_ok:
        print("\n🎉 Slice 1 Core Functionality: WORKING!")
        print("💡 Next steps:")
        print("   1. Start the server: python main.py serve")
        print("   2. Open http://localhost:8000/ui/index.html")
        print("   3. Test the UI component in the Game Controls sidebar")
        print("   4. Load a position and check Move Quality Assessment section")
    else:
        print("\n⚠️ Some core functionality not working. Check errors above.")
    
    if not api_ok and (backend_ok and deps_ok):
        print("\n💡 API not tested - make sure server is running:")
        print("   python main.py serve")
        print("   Then run this test again")

if __name__ == "__main__":
    main()