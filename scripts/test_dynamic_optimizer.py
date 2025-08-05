#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dynamic_optimizer_import():
    """Test that the dynamic optimizer can be imported."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import (
            AzulDynamicOptimizer, EndgamePhase, MultiTurnPlan
        )
        print("✅ Dynamic optimizer imports successful")
        return True
    except ImportError as e:
        print(f"❌ Dynamic optimizer import failed: {e}")
        return False

def test_optimizer_creation():
    """Test dynamic optimizer creation."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import AzulDynamicOptimizer
        
        optimizer = AzulDynamicOptimizer(max_depth=3, cache_size=1000)
        print("✅ Dynamic optimizer creation successful")
        return True
    except Exception as e:
        print(f"❌ Dynamic optimizer creation failed: {e}")
        return False

def test_endgame_phases():
    """Test endgame phase enum."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import EndgamePhase
        
        phases = [EndgamePhase.EARLY_GAME, EndgamePhase.MID_GAME, 
                 EndgamePhase.LATE_GAME, EndgamePhase.ENDGAME]
        
        for phase in phases:
            print(f"✅ Phase: {phase.value}")
        
        return True
    except Exception as e:
        print(f"❌ Endgame phases test failed: {e}")
        return False

def test_multi_turn_plan():
    """Test MultiTurnPlan dataclass."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import MultiTurnPlan
        
        plan = MultiTurnPlan(
            total_expected_score=45.0,
            move_sequence=[],
            confidence_score=0.8,
            risk_assessment={'overall_risk': 0.3},
            alternative_plans=[],
            endgame_evaluation={'endgame_score': 45.0}
        )
        
        print("✅ MultiTurnPlan creation successful")
        return True
    except Exception as e:
        print(f"❌ MultiTurnPlan test failed: {e}")
        return False

def test_basic_endgame_evaluation():
    """Test basic endgame evaluation."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import AzulDynamicOptimizer
        from core.azul_model import AzulState
        
        # Create a simple test state
        state = AzulState(2)
        state.round = 5
        state.current_player = 0
        
        # Add some tiles to factories
        state.factories = [
            [1, 1, 2, 3],  # Factory 0
            [2, 3, 4, 5],  # Factory 1
            [], [], []      # Empty factories
        ]
        
        # Add some tiles to player's wall
        state.agents[0].grid_state[0][0] = 1  # Blue tile
        state.agents[0].grid_state[1][1] = 1  # Yellow tile
        
        # Add some tiles to pattern lines
        state.agents[0].lines_number[0] = 2
        state.agents[0].lines_tile[0] = 1  # Blue tiles
        state.agents[0].lines_number[1] = 1
        state.agents[0].lines_tile[1] = 3  # Red tiles
        
        # Add some tiles to floor line
        state.agents[0].floor_tiles = [1, 2]
        
        # Initialize optimizer
        optimizer = AzulDynamicOptimizer(max_depth=3)
        
        # Evaluate endgame
        evaluation = optimizer.evaluate_endgame(state, 0)
        
        print(f"✅ Endgame evaluation successful:")
        print(f"   - Game phase: {evaluation['game_phase']}")
        print(f"   - Endgame score: {evaluation['endgame_score']:.2f}")
        print(f"   - Wall completion: {evaluation['wall_completion']:.2f}")
        print(f"   - Floor line penalty: {evaluation['floor_line_penalty']}")
        print(f"   - Pattern line efficiency: {evaluation['pattern_line_efficiency']:.2f}")
        print(f"   - Factory control: {evaluation['factory_control']:.2f}")
        print(f"   - Confidence: {evaluation['confidence']:.2f}")
        print(f"   - Evaluation time: {evaluation['evaluation_time']:.4f}s")
        
        return True
    except Exception as e:
        print(f"❌ Basic endgame evaluation failed: {e}")
        return False

def test_multi_turn_planning():
    """Test multi-turn planning."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import AzulDynamicOptimizer
        from core.azul_model import AzulState
        
        # Create a simple test state
        state = AzulState(2)
        state.round = 5
        state.current_player = 0
        
        # Add some tiles to factories
        state.factories = [
            [1, 1, 2, 3],  # Factory 0
            [2, 3, 4, 5],  # Factory 1
            [1, 2, 3, 4],  # Factory 2
            [], []          # Empty factories
        ]
        
        # Initialize optimizer
        optimizer = AzulDynamicOptimizer(max_depth=3)
        
        # Plan multi-turn sequence
        plan = optimizer.plan_optimal_sequence(state, 0, turns_ahead=2)
        
        print(f"✅ Multi-turn planning successful:")
        print(f"   - Total expected score: {plan.total_expected_score:.2f}")
        print(f"   - Move sequence length: {len(plan.move_sequence)}")
        print(f"   - Confidence score: {plan.confidence_score:.2f}")
        print(f"   - Alternative plans: {len(plan.alternative_plans)}")
        print(f"   - Risk assessment keys: {list(plan.risk_assessment.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Multi-turn planning failed: {e}")
        return False

def test_api_endpoint_import():
    """Test that the API endpoints can be imported."""
    try:
        from api.routes.dynamic_optimization import dynamic_optimization_bp
        
        print("✅ Dynamic optimization API endpoints import successful")
        return True
    except ImportError as e:
        print(f"❌ Dynamic optimization API import failed: {e}")
        return False

def test_app_registration():
    """Test that the dynamic optimization blueprint is registered in the app."""
    try:
        from api.app import create_app
        
        app = create_app()
        
        # Check if the blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        if 'dynamic_optimization' in blueprint_names:
            print("✅ Dynamic optimization blueprint registered in app")
            return True
        else:
            print("❌ Dynamic optimization blueprint not found in app")
            print(f"Available blueprints: {blueprint_names}")
            return False
    except Exception as e:
        print(f"❌ App registration test failed: {e}")
        return False

def test_integration_with_linear_optimizer():
    """Test integration with linear optimizer."""
    try:
        from analysis_engine.mathematical_optimization.dynamic_optimizer import AzulDynamicOptimizer
        from analysis_engine.mathematical_optimization.linear_optimizer import AzulLinearOptimizer
        
        # Create both optimizers
        dynamic_optimizer = AzulDynamicOptimizer()
        linear_optimizer = AzulLinearOptimizer()
        
        print("✅ Integration with linear optimizer successful")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests for the dynamic programming optimizer."""
    print("🧪 Testing Dynamic Programming Optimizer Implementation")
    print("=" * 60)
    
    tests = [
        ("Dynamic Optimizer Import", test_dynamic_optimizer_import),
        ("Optimizer Creation", test_optimizer_creation),
        ("Endgame Phases", test_endgame_phases),
        ("MultiTurnPlan", test_multi_turn_plan),
        ("Basic Endgame Evaluation", test_basic_endgame_evaluation),
        ("Multi-turn Planning", test_multi_turn_planning),
        ("API Endpoint Import", test_api_endpoint_import),
        ("App Registration", test_app_registration),
        ("Linear Optimizer Integration", test_integration_with_linear_optimizer)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All dynamic programming optimizer tests passed!")
        print("\n🚀 Ready for Day 3: Game Theory Integration")
        print("Next steps:")
        print("1. Create analysis_engine/mathematical_optimization/game_theory.py")
        print("2. Implement Nash equilibrium detection")
        print("3. Add opponent modeling")
        print("4. Create API endpoints for game theory")
        print("5. Integrate with existing optimizers")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 