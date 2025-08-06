#!/usr/bin/env python3
"""
Test Educational Integration Features

This script tests the educational enhancements to the move quality system.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_educational_move_explanation():
    """Test the educational move explanation endpoint."""
    print("🧪 Testing Educational Move Explanation...")
    
    # Test data
    test_data = {
        "quality_tier": "!",
        "move_description": "Take blue tile from factory 2 to pattern line 3",
        "position_context": "Mid-game position with multiple options"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/education/move-explanation",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                content = data.get("educational_content", {})
                print("✅ Educational move explanation working!")
                print(f"   Title: {content.get('title', 'N/A')}")
                print(f"   Difficulty: {content.get('difficulty_level', 'N/A')}")
                print(f"   Learning Tips: {len(content.get('learning_tips', []))} tips")
                return True
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_strategic_concepts():
    """Test the strategic concepts endpoint."""
    print("\n🧪 Testing Strategic Concepts...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/education/strategic-concepts")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                concepts = data.get("concepts", [])
                print(f"✅ Strategic concepts working! Found {len(concepts)} concepts")
                for concept in concepts:
                    print(f"   - {concept.get('name', 'N/A')} ({concept.get('difficulty', 'N/A')})")
                return True
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_move_quality_with_educational():
    """Test move quality analysis with educational content."""
    print("\n🧪 Testing Move Quality with Educational Content...")
    
    # Test FEN string (simplified for testing)
    test_fen = "local_test_position_simple"
    
    test_data = {
        "fen_string": test_fen,
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
                print("✅ Move quality analysis working!")
                print(f"   Total moves analyzed: {len(assessment.get('all_moves_quality', {}))}")
                print(f"   Best moves: {len(assessment.get('best_moves', []))}")
                print(f"   Alternative moves: {len(assessment.get('alternative_moves', []))}")
                
                # Check for educational insights
                insights = assessment.get('educational_insights', [])
                if insights:
                    print(f"   Educational insights: {len(insights)} found")
                    for insight in insights[:2]:  # Show first 2 insights
                        print(f"     - {insight}")
                else:
                    print("   No educational insights found (expected for test data)")
                
                return True
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_all_quality_tiers():
    """Test educational content for all quality tiers."""
    print("\n🧪 Testing All Quality Tiers...")
    
    quality_tiers = ['!!', '!', '=', '?!', '?']
    success_count = 0
    
    for tier in quality_tiers:
        test_data = {
            "quality_tier": tier,
            "move_description": f"Test move for {tier} tier",
            "position_context": "Test position"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/education/move-explanation",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    content = data.get("educational_content", {})
                    print(f"✅ {tier} tier: {content.get('title', 'N/A')}")
                    success_count += 1
                else:
                    print(f"❌ {tier} tier: API error")
            else:
                print(f"❌ {tier} tier: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {tier} tier: Request failed - {str(e)}")
    
    print(f"\n📊 Quality tier tests: {success_count}/{len(quality_tiers)} passed")
    return success_count == len(quality_tiers)

def main():
    """Run all educational integration tests."""
    print("🎓 Educational Integration Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/v1/move-quality-info")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    print("✅ Server is running")
    
    # Run tests
    tests = [
        test_educational_move_explanation,
        test_strategic_concepts,
        test_move_quality_with_educational,
        test_all_quality_tiers
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All educational integration tests passed!")
        print("\n✅ Educational features are working correctly:")
        print("   - Move quality explanations with educational content")
        print("   - Strategic concepts and learning tips")
        print("   - Quality tier educational content")
        print("   - API endpoints for educational features")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🚀 Ready for next phase: Pattern recognition educational content")

if __name__ == "__main__":
    main() 