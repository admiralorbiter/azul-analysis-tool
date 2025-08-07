#!/usr/bin/env python3
"""
Direct test script for Game Theory implementation

This script tests the game theory implementation directly without the API.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis_engine.mathematical_optimization.game_theory import AzulGameTheory
from core.azul_model import AzulState


def test_game_theory_direct():
    """Test game theory implementation directly"""
    
    print("🧪 Testing Game Theory Implementation Directly")
    print("=" * 50)
    
    # Create a simple game state
    game_state = AzulState(2)  # 2-player game
    
    # Initialize game theory
    game_theory = AzulGameTheory()
    
    print("\n1️⃣ Testing Nash Equilibrium Detection...")
    try:
        nash_result = game_theory.detect_nash_equilibrium(game_state, 0)
        print("✅ Nash Equilibrium Detection - SUCCESS")
        print(f"   Equilibrium Type: {nash_result.equilibrium_type}")
        print(f"   Confidence: {nash_result.confidence}")
        print(f"   Strategic Insights: {len(nash_result.strategic_insights)} insights")
    except Exception as e:
        print(f"❌ Nash Equilibrium Detection - ERROR: {str(e)}")
    
    print("\n2️⃣ Testing Opponent Modeling...")
    try:
        opponent_model = game_theory.model_opponent_strategy(game_state, 1)
        print("✅ Opponent Modeling - SUCCESS")
        print(f"   Player ID: {opponent_model.player_id}")
        print(f"   Risk Tolerance: {opponent_model.risk_tolerance}")
        print(f"   Aggression Level: {opponent_model.aggression_level}")
        print(f"   Predictability: {opponent_model.predictability_score}")
    except Exception as e:
        print(f"❌ Opponent Modeling - ERROR: {str(e)}")
    
    print("\n3️⃣ Testing Strategic Analysis...")
    try:
        strategic_analysis = game_theory.analyze_strategic_position(game_state, 0)
        print("✅ Strategic Analysis - SUCCESS")
        print(f"   Strategic Value: {strategic_analysis.strategic_value}")
        print(f"   Game Phase: {strategic_analysis.game_phase}")
        print(f"   Confidence: {strategic_analysis.confidence}")
        print(f"   Recommended Actions: {len(strategic_analysis.recommended_actions)} actions")
    except Exception as e:
        print(f"❌ Strategic Analysis - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Direct Game Theory Testing Complete!")
    print("=" * 50)


if __name__ == "__main__":
    test_game_theory_direct() 