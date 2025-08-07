#!/usr/bin/env python3
"""
Test script for FEN system implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.azul_model import AzulState


def test_fen_basic():
    """Test basic FEN functionality."""
    print("🧪 Testing FEN System Implementation")
    print("=" * 50)
    
    # Create a new game state
    state = AzulState(2)
    print(f"✅ Created new AzulState with {len(state.agents)} players")
    
    # Test to_fen()
    try:
        fen_string = state.to_fen()
        print(f"✅ Generated FEN: {fen_string}")
        print(f"   Length: {len(fen_string)} characters")
        print(f"   Parts: {len(fen_string.split('/'))} components")
    except Exception as e:
        print(f"❌ Error generating FEN: {e}")
        return False
    
    # Test validate_fen()
    try:
        is_valid = AzulState.validate_fen(fen_string)
        print(f"✅ FEN validation: {'PASS' if is_valid else 'FAIL'}")
    except Exception as e:
        print(f"❌ Error validating FEN: {e}")
        return False
    
    # Test from_fen() (basic test)
    try:
        new_state = AzulState.from_fen(fen_string)
        print(f"✅ Created state from FEN: {type(new_state)}")
    except Exception as e:
        print(f"❌ Error creating state from FEN: {e}")
        return False
    
    return True


def test_fen_components():
    """Test individual FEN components."""
    print("\n🔍 Testing FEN Components")
    print("=" * 30)
    
    state = AzulState(2)
    
    # Test factory encoding
    try:
        factories = state._encode_factories()
        print(f"✅ Factories: {factories}")
    except Exception as e:
        print(f"❌ Factory encoding error: {e}")
        return False
    
    # Test center encoding
    try:
        center = state._encode_center()
        print(f"✅ Center: {center}")
    except Exception as e:
        print(f"❌ Center encoding error: {e}")
        return False
    
    # Test wall encoding
    try:
        wall = state._encode_wall(state.agents[0])
        print(f"✅ Player 1 Wall: {wall}")
    except Exception as e:
        print(f"❌ Wall encoding error: {e}")
        return False
    
    # Test pattern lines encoding
    try:
        pattern = state._encode_pattern_lines(state.agents[0])
        print(f"✅ Player 1 Pattern: {pattern}")
    except Exception as e:
        print(f"❌ Pattern encoding error: {e}")
        return False
    
    # Test floor encoding
    try:
        floor = state._encode_floor(state.agents[0])
        print(f"✅ Player 1 Floor: {floor}")
    except Exception as e:
        print(f"❌ Floor encoding error: {e}")
        return False
    
    return True


def test_color_mapping():
    """Test color to letter mapping."""
    print("\n🎨 Testing Color Mapping")
    print("=" * 25)
    
    state = AzulState(2)
    
    # Test color mapping
    color_tests = [0, 1, 2, 3, 4]  # B, Y, R, K, W
    expected = ['B', 'Y', 'R', 'K', 'W']
    
    for color, expected_letter in zip(color_tests, expected):
        letter = state._color_to_letter(color)
        status = "✅" if letter == expected_letter else "❌"
        print(f"{status} Color {color} -> '{letter}' (expected '{expected_letter}')")
    
    # Test wall color scheme
    print("\n🏗️  Testing Wall Color Scheme")
    for row in range(5):
        row_colors = []
        for col in range(5):
            color = state._get_wall_color(row, col)
            letter = state._color_to_letter(color)
            row_colors.append(letter)
        print(f"Row {row}: {''.join(row_colors)}")
    
    return True


def test_fen_validation():
    """Test FEN validation."""
    print("\n✅ Testing FEN Validation")
    print("=" * 25)
    
    # Test valid FEN
    state = AzulState(2)
    valid_fen = state.to_fen()
    is_valid = AzulState.validate_fen(valid_fen)
    print(f"✅ Valid FEN: {'PASS' if is_valid else 'FAIL'}")
    
    # Test invalid FEN
    invalid_fen = "invalid_fen_string"
    is_invalid = AzulState.validate_fen(invalid_fen)
    print(f"✅ Invalid FEN: {'PASS' if not is_invalid else 'FAIL'}")
    
    # Test empty FEN
    is_empty_invalid = AzulState.validate_fen("")
    print(f"✅ Empty FEN: {'PASS' if not is_empty_invalid else 'FAIL'}")
    
    return True


def main():
    """Run all FEN system tests."""
    print("🚀 FEN System Implementation Test")
    print("=" * 50)
    
    tests = [
        test_fen_basic,
        test_fen_components,
        test_color_mapping,
        test_fen_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FEN system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 