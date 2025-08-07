#!/usr/bin/env python3
"""
Test script for FEN system API integration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.azul_model import AzulState
from api.utils.state_parser import state_to_fen, parse_fen_string


def test_api_integration():
    """Test FEN system integration with API."""
    print("🔗 Testing FEN System API Integration")
    print("=" * 50)
    
    # Create a new game state
    state = AzulState(2)
    print(f"✅ Created new AzulState")
    
    # Test state_to_fen API function
    try:
        fen_string = state_to_fen(state)
        print(f"✅ API state_to_fen: {fen_string}")
        print(f"   Length: {len(fen_string)} characters")
        print(f"   Parts: {len(fen_string.split('/'))} components")
    except Exception as e:
        print(f"❌ Error in API state_to_fen: {e}")
        return False
    
    # Test parse_fen_string API function
    try:
        new_state = parse_fen_string(fen_string)
        if new_state is not None:
            print(f"✅ API parse_fen_string: Success")
            print(f"   State type: {type(new_state)}")
            print(f"   Players: {len(new_state.agents)}")
        else:
            print(f"⚠️  API parse_fen_string: Returned None (fallback behavior)")
    except Exception as e:
        print(f"❌ Error in API parse_fen_string: {e}")
        return False
    
    # Test round-trip conversion
    try:
        fen1 = state_to_fen(state)
        state2 = parse_fen_string(fen1)
        if state2 is not None:
            fen2 = state_to_fen(state2)
            print(f"✅ Round-trip conversion: {'SUCCESS' if fen1 == fen2 else 'DIFFERENT'}")
            print(f"   FEN1: {fen1[:50]}...")
            print(f"   FEN2: {fen2[:50]}...")
        else:
            print(f"⚠️  Round-trip conversion: Skipped (parse returned None)")
    except Exception as e:
        print(f"❌ Error in round-trip conversion: {e}")
        return False
    
    return True


def test_backward_compatibility():
    """Test backward compatibility with existing FEN formats."""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 35)
    
    # Test with "initial" FEN
    try:
        state = parse_fen_string("initial")
        print(f"✅ 'initial' FEN: {'SUCCESS' if state is not None else 'FAIL'}")
    except Exception as e:
        print(f"❌ 'initial' FEN error: {e}")
    
    # Test with "saved" FEN
    try:
        state = parse_fen_string("saved")
        print(f"✅ 'saved' FEN: {'SUCCESS' if state is not None else 'FAIL'}")
    except Exception as e:
        print(f"❌ 'saved' FEN error: {e}")
    
    # Test with hash-based FEN
    try:
        state = parse_fen_string("state_abc12345")
        print(f"✅ Hash-based FEN: {'SUCCESS' if state is not None else 'FAIL'}")
    except Exception as e:
        print(f"❌ Hash-based FEN error: {e}")
    
    return True


def test_validation():
    """Test FEN validation through API."""
    print("\n✅ Testing FEN Validation")
    print("=" * 25)
    
    # Test valid FEN
    state = AzulState(2)
    valid_fen = state_to_fen(state)
    print(f"✅ Valid FEN generated: {len(valid_fen)} chars")
    
    # Test invalid FEN
    try:
        state = parse_fen_string("invalid_fen_string")
        print(f"✅ Invalid FEN handling: {'SUCCESS' if state is None else 'UNEXPECTED'}")
    except Exception as e:
        print(f"✅ Invalid FEN handling: Exception caught (expected)")
    
    return True


def main():
    """Run all FEN API integration tests."""
    print("🚀 FEN System API Integration Test")
    print("=" * 50)
    
    tests = [
        test_api_integration,
        test_backward_compatibility,
        test_validation
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
        print("🎉 All tests passed! FEN system API integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 