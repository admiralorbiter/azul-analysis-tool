#!/usr/bin/env python3
"""
Test script for Position Library FEN Integration

This script tests that:
1. Position library positions generate standard FEN strings
2. Generated FEN strings can be parsed correctly
3. Round-trip conversion works properly
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.azul_model import AzulState

def test_fen_generation():
    """Test that position library generates valid FEN strings."""
    print("🧪 Testing Position Library FEN Generation")
    print("=" * 50)
    
    # Test data representing position library game states
    test_positions = [
        {
            "name": "Balanced Start",
            "game_state": {
                "factories": [
                    ['B', 'Y', 'R', 'K'],
                    ['W', 'B', 'Y', 'R'],
                    ['K', 'W', 'B', 'Y'],
                    ['R', 'K', 'W', 'B'],
                    ['Y', 'R', 'K', 'W']
                ],
                "center": ['B', 'Y', 'R', 'K', 'W'],
                "players": [
                    {
                        "pattern_lines": [[], [], [], [], []],
                        "wall": [[None]*5 for _ in range(5)],
                        "floor": [],
                        "score": 0
                    },
                    {
                        "pattern_lines": [[], [], [], [], []],
                        "wall": [[None]*5 for _ in range(5)],
                        "floor": [],
                        "score": 0
                    }
                ]
            }
        },
        {
            "name": "Midgame Position",
            "game_state": {
                "factories": [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                "center": ['B', 'Y', 'R'],
                "players": [
                    {
                        "pattern_lines": [['B'], ['Y'], ['R'], [], []],
                        "wall": [
                            ['B', None, None, None, None],
                            [None, 'Y', None, None, None],
                            [None, None, 'R', None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None]
                        ],
                        "floor": ['B', 'Y'],
                        "score": 15
                    },
                    {
                        "pattern_lines": [['B'], ['Y'], ['R'], [], []],
                        "wall": [
                            ['B', None, None, None, None],
                            [None, 'Y', None, None, None],
                            [None, None, 'R', None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None]
                        ],
                        "floor": ['B', 'Y'],
                        "score": 20
                    }
                ]
            }
        },
        {
            "name": "Endgame Position",
            "game_state": {
                "factories": [
                    ['R'],
                    ['R'],
                    ['R'],
                    ['R'],
                    ['R']
                ],
                "center": ['R', 'R', 'R', 'W'],
                "players": [
                    {
                        "pattern_lines": [[], [], ['R', 'R', 'R'], [], ['W']],
                        "wall": [
                            ['B', 'Y', 'R', 'K', 'W'],
                            ['W', 'B', 'Y', 'R', 'K'],
                            ['K', 'W', 'B', 'Y', 'R'],
                            ['R', 'K', 'W', 'B', 'Y'],
                            ['Y', 'R', 'K', 'W', 'B']
                        ],
                        "floor": ['R', 'W'],
                        "score": 45
                    },
                    {
                        "pattern_lines": [[], [], ['R', 'R', 'R'], [], ['W']],
                        "wall": [
                            ['B', 'Y', 'R', 'K', 'W'],
                            ['W', 'B', 'Y', 'R', 'K'],
                            ['K', 'W', 'B', 'Y', 'R'],
                            ['R', 'K', 'W', 'B', 'Y'],
                            ['Y', 'R', 'K', 'W', 'B']
                        ],
                        "floor": ['R', 'W'],
                        "score": 53
                    }
                ]
            }
        }
    ]
    
    passed_tests = 0
    total_tests = 0
    
    for position in test_positions:
        print(f"\n📋 Testing: {position['name']}")
        total_tests += 1
        
        try:
            # Create AzulState from game state
            state = create_azul_state_from_position(position['game_state'])
            
            # Generate FEN string
            fen_string = state.to_fen()
            print(f"✅ Generated FEN: {fen_string[:50]}...")
            
            # Validate FEN string
            if AzulState.validate_fen(fen_string):
                print("✅ FEN validation passed")
            else:
                print("❌ FEN validation failed")
                continue
            
            # Test round-trip conversion
            parsed_state = AzulState.from_fen(fen_string)
            regenerated_fen = parsed_state.to_fen()
            
            if fen_string == regenerated_fen:
                print("✅ Round-trip conversion successful")
                passed_tests += 1
            else:
                print("❌ Round-trip conversion failed")
                print(f"   Original: {fen_string}")
                print(f"   Regenerated: {regenerated_fen}")
            
        except Exception as e:
            print(f"❌ Error testing position: {e}")
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests

def create_azul_state_from_position(position_data):
    """Create an AzulState from position library game state data."""
    # Create new state
    state = AzulState(2)
    
    # Apply factories
    for i, factory_tiles in enumerate(position_data['factories']):
        if i < len(state.factories):
            state.factories[i].tiles.clear()
            for tile in factory_tiles:
                color = letter_to_color(tile)
                if color is not None:
                    state.factories[i].tiles[color] = state.factories[i].tiles.get(color, 0) + 1
    
    # Apply center pool
    state.centre_pool.tiles.clear()
    for tile in position_data['center']:
        color = letter_to_color(tile)
        if color is not None:
            state.centre_pool.tiles[color] = state.centre_pool.tiles.get(color, 0) + 1
    
    # Apply player data
    for player_idx, player_data in enumerate(position_data['players']):
        if player_idx < len(state.agents):
            agent = state.agents[player_idx]
            
            # Apply pattern lines
            for line_idx, line_tiles in enumerate(player_data['pattern_lines']):
                if line_idx < 5:
                    agent.lines_number[line_idx] = len(line_tiles)
                    if line_tiles:
                        agent.lines_tile[line_idx] = letter_to_color(line_tiles[0])
                    else:
                        agent.lines_tile[line_idx] = -1
            
            # Apply wall
            agent.grid_state.fill(0)
            for row_idx, row in enumerate(player_data['wall']):
                for col_idx, tile in enumerate(row):
                    if tile is not None:
                        expected_color = get_wall_color(row_idx, col_idx)
                        actual_color = letter_to_color(tile)
                        if expected_color == actual_color:
                            agent.grid_state[row_idx][col_idx] = 1
            
            # Apply floor
            agent.floor_tiles = []
            for tile in player_data['floor']:
                color = letter_to_color(tile)
                if color is not None:
                    agent.floor_tiles.append(color)
            
            # Apply score
            agent.score = player_data['score']
    
    return state

def letter_to_color(letter):
    """Convert letter to color number."""
    color_map = {'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4}
    return color_map.get(letter, None)

def get_wall_color(row, col):
    """Get the color that should be at wall position."""
    # This is the Azul wall color scheme
    color_scheme = [
        [0, 1, 2, 3, 4],  # Row 0: B,Y,R,K,W
        [4, 0, 1, 2, 3],  # Row 1: W,B,Y,R,K
        [3, 4, 0, 1, 2],  # Row 2: K,W,B,Y,R
        [2, 3, 4, 0, 1],  # Row 3: R,K,W,B,Y
        [1, 2, 3, 4, 0]   # Row 4: Y,R,K,W,B
    ]
    return color_scheme[row][col]

def test_fen_format_consistency():
    """Test that FEN format is consistent across different positions."""
    print("\n🧪 Testing FEN Format Consistency")
    print("=" * 50)
    
    # Test that FEN strings follow the expected format
    test_cases = [
        {
            "name": "Empty Game State",
            "fen_parts": 7,  # factories/center/player1/player2/scores/round/current_player
            "expected_structure": "factories/center/player1_wall/player1_pattern/player1_floor/player2_wall/player2_pattern/player2_floor/scores/round/current_player"
        }
    ]
    
    passed_tests = 0
    total_tests = 0
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        total_tests += 1
        
        try:
            # Create a basic state
            state = AzulState(2)
            fen_string = state.to_fen()
            
            # Check that FEN has the right number of parts
            parts = fen_string.split('/')
            if len(parts) >= test_case['fen_parts']:
                print(f"✅ FEN has correct number of parts: {len(parts)}")
                passed_tests += 1
            else:
                print(f"❌ FEN has wrong number of parts: {len(parts)}, expected >= {test_case['fen_parts']}")
            
            print(f"   FEN structure: {test_case['expected_structure']}")
            print(f"   Actual FEN: {fen_string}")
            
        except Exception as e:
            print(f"❌ Error testing FEN format: {e}")
    
    print(f"\n📊 Format Test Results: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests

def main():
    """Run all FEN integration tests."""
    print("🚀 Position Library FEN Integration Tests")
    print("=" * 60)
    
    # Run tests
    fen_generation_success = test_fen_generation()
    fen_format_success = test_fen_format_consistency()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ FEN Generation Tests: {'PASSED' if fen_generation_success else 'FAILED'}")
    print(f"✅ FEN Format Tests: {'PASSED' if fen_format_success else 'FAILED'}")
    
    overall_success = fen_generation_success and fen_format_success
    print(f"\n🎯 Overall Result: {'PASSED' if overall_success else 'FAILED'}")
    
    if overall_success:
        print("\n🎉 Phase 4: Position Library Integration - SUCCESS!")
        print("✅ Standard FEN format is working correctly")
        print("✅ Position library generates valid FEN strings")
        print("✅ Round-trip conversion is working")
        print("✅ FEN validation is working")
    else:
        print("\n❌ Phase 4: Position Library Integration - FAILED!")
        print("Please check the test results above for issues.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 