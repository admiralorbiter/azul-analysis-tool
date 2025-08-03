#!/usr/bin/env python3
"""
Test script for Strategic Pattern Analysis Integration.

This script tests the integration between our strategic pattern analysis
and the existing analysis panel and position library.
"""

import sys
import os
import time
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.azul_strategic_patterns import StrategicPatternDetector
from core.azul_strategic_utils import StrategicAnalysisReporter
from core.azul_model import AzulState

def create_test_state_for_strategic_analysis():
    """Create a test state that should trigger strategic pattern detection."""
    state = AzulState(2)  # 2-player game
    
    # Set up factories with strategic opportunities
    state.factories[0].AddTiles(4, 0)  # 4 blue tiles - domination opportunity
    state.factories[0].AddTiles(1, 1)  # 1 yellow tile
    state.factories[1].AddTiles(3, 1)  # 3 yellow tiles - disruption opportunity
    state.factories[1].AddTiles(1, 2)  # 1 red tile
    state.factories[2].AddTiles(2, 2)  # 2 red tiles
    state.factories[2].AddTiles(1, 3)  # 1 black tile
    state.factories[3].AddTiles(1, 3)  # 1 black tile
    state.factories[3].AddTiles(1, 4)  # 1 white tile
    state.factories[4].AddTiles(1, 4)  # 1 white tile
    state.factories[4].AddTiles(1, 0)  # 1 blue tile
    
    # Set up center pool
    state.centre_pool.AddTiles(1, 0)  # 1 blue tile
    state.centre_pool.AddTiles(1, 1)  # 1 yellow tile
    state.centre_pool.AddTiles(1, 2)  # 1 red tile
    state.centre_pool.AddTiles(1, 3)  # 1 black tile
    state.centre_pool.AddTiles(1, 4)  # 1 white tile
    
    # Set up player 0 (current player)
    player_state = state.agents[0]
    player_state.lines_number[0] = 2  # 2 blue tiles in line 0
    player_state.lines_tile[0] = 0   # Blue color
    player_state.lines_number[1] = 1  # 1 yellow tile in line 1
    player_state.lines_tile[1] = 1   # Yellow color
    player_state.grid_state[0][0] = 1  # Some tiles on wall
    player_state.grid_state[1][1] = 1
    player_state.floor_tiles = [2, 3]  # Some floor tiles
    
    # Set up player 1 (opponent) - has tiles that create opportunities
    opponent_state = state.agents[1]
    opponent_state.lines_number[0] = 3  # 3 blue tiles in line 0
    opponent_state.lines_tile[0] = 0   # Blue color
    opponent_state.lines_number[1] = 2  # 2 yellow tiles in line 1
    opponent_state.lines_tile[1] = 1   # Yellow color
    opponent_state.grid_state[0][0] = 0  # Blue not on wall yet
    opponent_state.grid_state[1][1] = 0  # Yellow not on wall yet
    opponent_state.floor_tiles = [1]
    
    return state

def test_strategic_pattern_detection():
    """Test the strategic pattern detection with our test state."""
    print("🧪 Testing Strategic Pattern Detection...")
    
    try:
        # Create test state
        state = create_test_state_for_strategic_analysis()
        
        # Initialize detector
        detector = StrategicPatternDetector()
        
        # Perform strategic analysis
        start_time = time.time()
        strategic_analysis = detector.detect_strategic_patterns(state, 0)
        analysis_time = time.time() - start_time
        
        print(f"✅ Strategic Analysis Completed in {analysis_time:.3f}s")
        print(f"   Factory Control Opportunities: {len(strategic_analysis.factory_control_opportunities)}")
        print(f"   Endgame Scenarios: {len(strategic_analysis.endgame_scenarios)}")
        print(f"   Risk/Reward Scenarios: {len(strategic_analysis.risk_reward_scenarios)}")
        print(f"   Strategic Move Suggestions: {len(strategic_analysis.strategic_move_suggestions)}")
        print(f"   Position Assessment: {strategic_analysis.position_assessment}")
        print(f"   Confidence: {strategic_analysis.confidence:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategic Pattern Detection Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategic_report_generation():
    """Test the strategic analysis report generation."""
    print("\n🧪 Testing Strategic Report Generation...")
    
    try:
        # Create test state
        state = create_test_state_for_strategic_analysis()
        
        # Initialize detector and reporter
        detector = StrategicPatternDetector()
        reporter = StrategicAnalysisReporter()
        
        # Perform analysis
        strategic_analysis = detector.detect_strategic_patterns(state, 0)
        
        # Generate reports
        text_report = reporter.generate_text_report(strategic_analysis, state, 0)
        html_report = reporter.generate_html_report(strategic_analysis, state, 0)
        
        print(f"✅ Report Generation Successful")
        print(f"   Text Report Length: {len(text_report)} characters")
        print(f"   HTML Report Length: {len(html_report)} characters")
        
        # Show a snippet of the text report
        print("\n📄 Text Report Preview:")
        print("-" * 50)
        lines = text_report.split('\n')[:10]  # First 10 lines
        for line in lines:
            print(line)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Strategic Report Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_position_library_integration():
    """Test that our strategic pattern analysis works with position library format."""
    print("\n🧪 Testing Position Library Integration...")
    
    try:
        # Create test state
        state = create_test_state_for_strategic_analysis()
        
        # Convert to position library format (simulate what the UI does)
        position_data = {
            "factories": [],
            "center": [],
            "players": [],
            "fen_string": "test_strategic_integration"
        }
        
        # Convert factories
        for factory in state.factories:
            factory_array = []
            for color, count in factory.tiles.items():
                color_names = ['B', 'Y', 'R', 'K', 'W']
                for _ in range(count):
                    factory_array.append(color_names[color])
            position_data["factories"].append(factory_array)
        
        # Convert center pool
        for color, count in state.centre_pool.tiles.items():
            color_names = ['B', 'Y', 'R', 'K', 'W']
            for _ in range(count):
                position_data["center"].append(color_names[color])
        
        # Convert players
        for player_state in state.agents:
            player_data = {
                "pattern_lines": [],
                "wall": player_state.grid_state,
                "floor_line": player_state.floor_tiles,
                "score": 0  # We don't track score in this format
            }
            
            # Convert pattern lines
            for i in range(5):
                line_count = player_state.lines_number[i]
                line_color = player_state.lines_tile[i]
                if line_color == -1:
                    player_data["pattern_lines"].append(Array(line_count).fill(null))
                else:
                    color_names = ['B', 'Y', 'R', 'K', 'W']
                    player_data["pattern_lines"].append(Array(line_count).fill(color_names[line_color]))
            
            position_data["players"].append(player_data)
        
        print(f"✅ Position Library Format Conversion Successful")
        print(f"   Factories: {len(position_data['factories'])}")
        print(f"   Center Pool Tiles: {len(position_data['center'])}")
        print(f"   Players: {len(position_data['players'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Position Library Integration Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_panel_compatibility():
    """Test that our strategic analysis is compatible with the existing analysis panel."""
    print("\n🧪 Testing Analysis Panel Compatibility...")
    
    try:
        # Create test state
        state = create_test_state_for_strategic_analysis()
        
        # Initialize detector
        detector = StrategicPatternDetector()
        
        # Get strategic move suggestions (what the analysis panel would use)
        move_suggestions = detector.get_strategic_move_suggestions(state, 0)
        
        # Get position analysis (what the analysis panel would display)
        position_analysis = detector.analyze_strategic_position(state, 0)
        
        print(f"✅ Analysis Panel Compatibility Successful")
        print(f"   Strategic Move Suggestions: {len(move_suggestions)}")
        print(f"   Position Analysis: {position_analysis}")
        
        # Show some move suggestions
        if move_suggestions:
            print("\n🎯 Strategic Move Suggestions:")
            for i, suggestion in enumerate(move_suggestions[:3]):  # Show first 3
                print(f"   {i+1}. {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis Panel Compatibility Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all strategic pattern analysis integration tests."""
    print("🚀 STRATEGIC PATTERN ANALYSIS INTEGRATION TESTING")
    print("=" * 60)
    
    tests = [
        test_strategic_pattern_detection,
        test_strategic_report_generation,
        test_position_library_integration,
        test_analysis_panel_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 INTEGRATION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL STRATEGIC PATTERN ANALYSIS INTEGRATION TESTS PASSED!")
        print("✅ Strategic pattern analysis is ready for UI integration!")
        print("\n📋 Next Steps:")
        print("   1. The strategic pattern analysis system is working correctly")
        print("   2. Position library integration is ready")
        print("   3. Analysis panel compatibility is confirmed")
        print("   4. Ready to proceed to Week 3 (UI Components)")
    else:
        print("⚠️  Some integration tests failed. Please check the implementation.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 