#!/usr/bin/env python3
"""
Simple test script for Game Theory implementation

This script tests the game theory implementation directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_game_theory_import():
    """Test if we can import the game theory module"""
    try:
        from analysis_engine.mathematical_optimization.game_theory import AzulGameTheory
        from core.azul_model import AzulState
        print("✅ Game theory imports successful")
        return True
    except Exception as e:
        print(f"❌ Game theory import failed: {e}")
        return False

def test_game_theory_creation():
    """Test if we can create game theory objects"""
    try:
        from analysis_engine.mathematical_optimization.game_theory import AzulGameTheory
        from core.azul_model import AzulState
        
        # Create game state
        game_state = AzulState(2)
        print("✅ Game state created successfully")
        
        # Create game theory
        game_theory = AzulGameTheory()
        print("✅ Game theory object created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Game theory creation failed: {e}")
        return False

def test_game_theory_methods():
    """Test if game theory methods work"""
    try:
        from analysis_engine.mathematical_optimization.game_theory import AzulGameTheory
        from core.azul_model import AzulState
        
        # Create objects
        game_state = AzulState(2)
        game_theory = AzulGameTheory()
        
        # Test Nash equilibrium detection
        nash_result = game_theory.detect_nash_equilibrium(game_state, 0)
        print(f"✅ Nash equilibrium detection: {nash_result.equilibrium_type}")
        
        # Test opponent modeling
        opponent_model = game_theory.model_opponent_strategy(game_state, 1)
        print(f"✅ Opponent modeling: Player {opponent_model.player_id}")
        
        # Test strategic analysis
        strategic_analysis = game_theory.analyze_strategic_position(game_state, 0)
        print(f"✅ Strategic analysis: Value {strategic_analysis.strategic_value}")
        
        return True
    except Exception as e:
        print(f"❌ Game theory methods failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Game Theory Implementation")
    print("=" * 50)
    
    # Test 1: Import
    print("\n1️⃣ Testing imports...")
    import_success = test_game_theory_import()
    
    # Test 2: Creation
    print("\n2️⃣ Testing object creation...")
    creation_success = test_game_theory_creation()
    
    # Test 3: Methods
    print("\n3️⃣ Testing methods...")
    methods_success = test_game_theory_methods()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Creation: {'✅ PASS' if creation_success else '❌ FAIL'}")
    print(f"   Methods: {'✅ PASS' if methods_success else '❌ FAIL'}")
    
    if import_success and creation_success and methods_success:
        print("\n🎉 All tests passed! Game theory implementation is working.")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main() 