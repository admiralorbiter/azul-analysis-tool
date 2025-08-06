#!/usr/bin/env python3
"""
Test script for Move Quality Assessment - Slice 2: Analysis Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis_engine.move_quality.azul_move_quality_assessor import AzulMoveQualityAssessor
from core.azul_model import AzulState
from analysis_engine.move_quality.move_parser import AzulMoveParser, ParsedMove, MoveType

def test_move_quality_slice2():
    """Test the Slice 2 implementation of move quality assessment."""
    print("🎯 Testing Move Quality Assessment - Slice 2: Analysis Integration")
    print("=" * 70)
    
    # Initialize components
    assessor = AzulMoveQualityAssessor()
    parser = AzulMoveParser()
    
    # Test 1: Move Parsing
    print("\n📋 Test 1: Move Parsing System")
    print("-" * 40)
    
    test_moves = [
        "factory_0_tile_blue_pattern_line_1",
        "factory_2_tile_red_floor", 
        "factory_1_tile_yellow_wall_2_3",
        "pass"
    ]
    
    for move_key in test_moves:
        try:
            parsed_move = parser.parse_move(move_key)
            print(f"✅ Parsed '{move_key}' -> {parsed_move.move_type.value}")
            print(f"   Valid: {parsed_move.is_valid}, Errors: {parsed_move.validation_errors}")
        except Exception as e:
            print(f"❌ Failed to parse '{move_key}': {e}")
    
    # Test 2: Tactical Value Calculation
    print("\n📋 Test 2: Tactical Value Calculation")
    print("-" * 40)
    
    # Create a simple test state
    state = AzulState(2)  # 2-player game
    
    # Test tactical value for different move types
    test_tactical_moves = [
        ("factory_0_tile_blue_pattern_line_1", "Pattern line completion"),
        ("factory_2_tile_red_floor", "Floor line management"),
        ("pass", "Pass move")
    ]
    
    for move_key, description in test_tactical_moves:
        try:
            parsed_move = parser.parse_move(move_key)
            if parsed_move.is_valid:
                tactical_value = assessor._calculate_tactical_value(state, 0, parsed_move)
                print(f"✅ {description}: {tactical_value:.1f}/100")
            else:
                print(f"❌ {description}: Invalid move - {parsed_move.validation_errors}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    # Test 3: Risk Assessment
    print("\n📋 Test 3: Risk Assessment")
    print("-" * 40)
    
    for move_key, description in test_tactical_moves:
        try:
            parsed_move = parser.parse_move(move_key)
            if parsed_move.is_valid:
                risk_assessment = assessor._assess_risk(state, 0, parsed_move)
                print(f"✅ {description}: Risk score {risk_assessment:.1f}/100")
            else:
                print(f"❌ {description}: Invalid move - {parsed_move.validation_errors}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    # Test 4: Opportunity Value Calculation
    print("\n📋 Test 4: Opportunity Value Calculation")
    print("-" * 40)
    
    for move_key, description in test_tactical_moves:
        try:
            parsed_move = parser.parse_move(move_key)
            if parsed_move.is_valid:
                opportunity_value = assessor._calculate_opportunity_value(state, 0, parsed_move)
                print(f"✅ {description}: Opportunity score {opportunity_value:.1f}/100")
            else:
                print(f"❌ {description}: Invalid move - {parsed_move.validation_errors}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    # Test 5: Complete Move Quality Assessment
    print("\n📋 Test 5: Complete Move Quality Assessment")
    print("-" * 40)
    
    test_move = "factory_0_tile_blue_pattern_line_1"
    try:
        quality_score = assessor.assess_move_quality(state, 0, test_move)
        print(f"✅ Move: {test_move}")
        print(f"   Overall Score: {quality_score.overall_score:.1f}/100")
        print(f"   Quality Tier: {quality_score.quality_tier.value}")
        print(f"   Strategic Value: {quality_score.strategic_value:.1f}")
        print(f"   Tactical Value: {quality_score.tactical_value:.1f}")
        print(f"   Risk Assessment: {quality_score.risk_assessment:.1f}")
        print(f"   Opportunity Value: {quality_score.opportunity_value:.1f}")
        print(f"   Confidence: {quality_score.confidence_score:.2f}")
        print(f"   Explanation: {quality_score.explanation}")
    except Exception as e:
        print(f"❌ Complete assessment failed: {e}")
    
    # Test 6: Enhanced Explanations
    print("\n📋 Test 6: Enhanced Explanations")
    print("-" * 40)
    
    try:
        parsed_move = parser.parse_move(test_move)
        if parsed_move.is_valid:
            explanation = assessor._generate_move_explanation(
                parsed_move, 
                {"blocking": 75.0, "scoring": 65.0, "floor_line": 80.0},
                70.0, 65.0, 75.0, 60.0,
                assessor._determine_quality_tier(70.0)
            )
            print(f"✅ Enhanced explanation: {explanation}")
        else:
            print(f"❌ Invalid move for explanation test")
    except Exception as e:
        print(f"❌ Explanation generation failed: {e}")
    
    # Test 7: Confidence Calculation
    print("\n📋 Test 7: Confidence Calculation")
    print("-" * 40)
    
    try:
        confidence = assessor._calculate_confidence_score(
            {"blocking": 75.0, "scoring": 65.0, "floor_line": 80.0},
            70.0, 65.0
        )
        print(f"✅ Confidence score: {confidence:.2f}")
    except Exception as e:
        print(f"❌ Confidence calculation failed: {e}")
    
    print("\n🎉 Slice 2 Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_move_quality_slice2() 