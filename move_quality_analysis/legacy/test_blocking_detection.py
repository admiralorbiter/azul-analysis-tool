#!/usr/bin/env python3
"""
Test script for blocking detection with test positions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.azul_patterns import AzulPatternDetector
from core.azul_model import AzulState
from core import azul_utils as utils


def test_blocking_detection():
    """Test blocking detection with various scenarios."""
    detector = AzulPatternDetector()
    # Lower threshold for testing
    detector.blocking_urgency_threshold = 0.3
    
    print("🧪 Testing Tile Blocking Detection (R2.1)")
    print("=" * 50)
    
    # Test 1: Simple blocking opportunity
    print("\n1️⃣ Testing Simple Blue Blocking:")
    state = AzulState(2)
    
    # Set up opponent with blue tiles in pattern line 0
    opponent = state.agents[1]
    opponent.lines_number[0] = 1  # 1 tile in pattern line 0
    opponent.lines_tile[0] = utils.Tile.BLUE
    opponent.grid_state[0][utils.Tile.BLUE] = 0  # Not on wall
    
    # Add blue tiles to factory
    state.factories[0].tiles[utils.Tile.BLUE] = 2
    
    patterns = detector.detect_patterns(state, 0)
    print(f"   Patterns detected: {patterns.total_patterns}")
    print(f"   Confidence score: {patterns.confidence_score:.2f}")
    
    if patterns.blocking_opportunities:
        opp = patterns.blocking_opportunities[0]
        print(f"   Blocking opportunity: {opp.description}")
        print(f"   Urgency level: {opp.urgency_score:.2f}")
    
    # Test 2: High urgency blocking
    print("\n2️⃣ Testing High Urgency Red Blocking:")
    state = AzulState(2)
    
    # Set up opponent with 2 red tiles in pattern line 2 (capacity 3)
    opponent = state.agents[1]
    opponent.lines_number[2] = 2  # 2 tiles in pattern line 2
    opponent.lines_tile[2] = utils.Tile.RED
    opponent.grid_state[2][utils.Tile.RED] = 0  # Not on wall
    
    # Add red tiles to factory
    state.factories[0].tiles[utils.Tile.RED] = 3
    
    patterns = detector.detect_patterns(state, 0)
    print(f"   Patterns detected: {patterns.total_patterns}")
    
    if patterns.blocking_opportunities:
        opp = patterns.blocking_opportunities[0]
        print(f"   Blocking opportunity: {opp.description}")
        print(f"   Urgency level: {opp.urgency_score:.2f}")
        print(f"   Urgency should be HIGH: {opp.urgency_score > 0.8}")
    
    # Test 3: No blocking (color already on wall)
    print("\n3️⃣ Testing No Blocking (Color on Wall):")
    state = AzulState(2)
    
    # Set up opponent with blue tiles in pattern line
    opponent = state.agents[1]
    opponent.lines_number[0] = 1
    opponent.lines_tile[0] = utils.Tile.BLUE
    opponent.grid_state[0][utils.Tile.BLUE] = 1  # Already on wall!
    
    # Add blue tiles to factory
    state.factories[0].tiles[utils.Tile.BLUE] = 2
    
    patterns = detector.detect_patterns(state, 0)
    print(f"   Patterns detected: {patterns.total_patterns}")
    print(f"   Should be 0: {patterns.total_patterns == 0}")
    
    # Test 4: Multiple blocking opportunities
    print("\n4️⃣ Testing Multiple Blocking Opportunities:")
    state = AzulState(2)
    
    # Set up opponent with multiple pattern lines
    opponent = state.agents[1]
    opponent.lines_number[0] = 1  # Blue in line 0
    opponent.lines_tile[0] = utils.Tile.BLUE
    opponent.lines_number[1] = 1  # Yellow in line 1
    opponent.lines_tile[1] = utils.Tile.YELLOW
    opponent.lines_number[2] = 2  # Red in line 2
    opponent.lines_tile[2] = utils.Tile.RED
    
    # No colors on wall
    opponent.grid_state[0][utils.Tile.BLUE] = 0
    opponent.grid_state[1][utils.Tile.YELLOW] = 0
    opponent.grid_state[2][utils.Tile.RED] = 0
    
    # Add tiles to factories
    state.factories[0].tiles[utils.Tile.BLUE] = 1
    state.factories[1].tiles[utils.Tile.YELLOW] = 1
    state.factories[2].tiles[utils.Tile.RED] = 1
    
    patterns = detector.detect_patterns(state, 0)
    print(f"   Patterns detected: {patterns.total_patterns}")
    print(f"   Should be 3: {patterns.total_patterns == 3}")
    
    if patterns.blocking_opportunities:
        print("   Blocking opportunities:")
        for i, opp in enumerate(patterns.blocking_opportunities):
            print(f"     {i+1}. {opp.description}")
            print(f"        Urgency: {opp.urgency_score:.2f}")
    
    print("\n✅ Blocking detection tests completed!")
    return True


if __name__ == "__main__":
    try:
        test_blocking_detection()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 