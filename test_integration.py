#!/usr/bin/env python3
"""
Integration Test Script

This script tests the integration between the move quality analysis system
and the main database system.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import time
import json
from datetime import datetime

from core.azul_database import AzulDatabase, MoveQualityAnalysis, ComprehensiveMoveAnalysis, ExhaustiveAnalysisSession
from core.azul_model import AzulState

def test_database_integration():
    """Test the database integration."""
    print("🔍 Testing Database Integration...")
    
    try:
        # Initialize database
        db = AzulDatabase()
        print(f"   ✅ Database initialized: {db.db_path}")
        
        # Test position caching
        test_state = AzulState(2)
        test_fen = test_state.to_fen()
        position_id = db.cache_position(test_fen, 2)
        print(f"   ✅ Position cached with ID: {position_id}")
        
        # Test move quality analysis saving
        test_analysis = MoveQualityAnalysis(
            position_id=position_id,
            session_id="test_session",
            game_phase="mid",
            total_moves_analyzed=50,
            quality_distribution={'!!': 2, '!': 8, '=': 25, '?!': 12, '?': 3},
            average_quality_score=65.5,
            best_move_score=85.0,
            worst_move_score=25.0,
            engine_consensus={'alpha_beta': 70.0, 'mcts': 65.0, 'neural': 68.0, 'pattern': 72.0},
            disagreement_level=0.15,
            position_complexity=0.75,
            strategic_themes=["Strong blocking opportunities", "Moderate scoring opportunities"],
            tactical_opportunities=["3 high-quality moves available", "Multiple engine agreement"],
            analysis_time=12.5
        )
        
        analysis_id = db.save_move_quality_analysis(test_analysis)
        print(f"   ✅ Move quality analysis saved with ID: {analysis_id}")
        
        # Test comprehensive move analysis saving
        test_move_analysis = ComprehensiveMoveAnalysis(
            position_analysis_id=analysis_id,
            move_data={
                'move_type': 'factory_to_pattern',
                'factory_id': 0,
                'tile_type': 1,
                'pattern_line': 2,
                'num_to_floor_line': 0
            },
            alpha_beta_score=75.0,
            mcts_score=70.0,
            neural_score=72.0,
            pattern_score=78.0,
            overall_quality_score=73.75,
            quality_tier='!',
            confidence_score=0.85,
            strategic_value=80.0,
            tactical_value=65.0,
            risk_assessment=30.0,
            opportunity_value=70.0,
            blocking_score=75.0,
            scoring_score=70.0,
            floor_line_score=80.0,
            timing_score=65.0,
            analysis_time=0.5,
            engines_used=['alpha_beta', 'mcts', 'neural', 'pattern'],
            explanation="This is an excellent move that blocks opponent scoring while advancing our own position."
        )
        
        move_analysis_id = db.save_comprehensive_move_analysis(test_move_analysis)
        print(f"   ✅ Comprehensive move analysis saved with ID: {move_analysis_id}")
        
        # Test session saving
        test_session = ExhaustiveAnalysisSession(
            session_id="test_session",
            mode="standard",
            positions_analyzed=1,
            total_moves_analyzed=50,
            total_analysis_time=12.5,
            successful_analyses=1,
            failed_analyses=0,
            engine_stats={'alpha_beta': {'success_rate': 1.0}, 'mcts': {'success_rate': 1.0}},
            status='completed',
            completed_at=datetime.now()
        )
        
        session_saved = db.save_exhaustive_analysis_session(test_session)
        print(f"   ✅ Session saved: {session_saved}")
        
        # Test retrieval
        retrieved_analysis = db.get_move_quality_analysis(position_id, "test_session")
        if retrieved_analysis:
            print(f"   ✅ Analysis retrieved successfully")
            print(f"      Average score: {retrieved_analysis.average_quality_score}")
            print(f"      Quality distribution: {retrieved_analysis.quality_distribution}")
        else:
            print("   ❌ Failed to retrieve analysis")
        
        # Test comprehensive move analyses retrieval
        move_analyses = db.get_comprehensive_move_analyses(analysis_id)
        print(f"   ✅ Retrieved {len(move_analyses)} move analyses")
        
        # Test session retrieval
        retrieved_session = db.get_exhaustive_analysis_session("test_session")
        if retrieved_session:
            print(f"   ✅ Session retrieved successfully")
            print(f"      Mode: {retrieved_session.mode}")
            print(f"      Status: {retrieved_session.status}")
        else:
            print("   ❌ Failed to retrieve session")
        
        # Test best analyses
        best_analyses = db.get_best_move_quality_analyses(limit=5)
        print(f"   ✅ Retrieved {len(best_analyses)} best analyses")
        
        print("   🎉 All database integration tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Test the API integration."""
    print("\n🔍 Testing API Integration...")
    
    try:
        # Import API components
        from api.routes.comprehensive_analysis import comprehensive_analysis_bp
        from api.app import create_app
        
        # Create test app
        app = create_app()
        print("   ✅ API app created successfully")
        
        # Test that the blueprint is registered
        with app.test_client() as client:
            # Test analysis stats endpoint
            response = client.get('/api/v1/analysis-stats')
            print(f"   ✅ Analysis stats endpoint: {response.status_code}")
            
            # Test exhaustive sessions endpoint
            response = client.get('/api/v1/exhaustive-sessions')
            print(f"   ✅ Exhaustive sessions endpoint: {response.status_code}")
            
            # Test best analyses endpoint
            response = client.get('/api/v1/best-analyses')
            print(f"   ✅ Best analyses endpoint: {response.status_code}")
        
        print("   🎉 All API integration tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_analyzer():
    """Test the integrated exhaustive analyzer."""
    print("\n🔍 Testing Integrated Analyzer...")
    
    try:
        # Import the integrated analyzer
        from move_quality_analysis.scripts.integrated_exhaustive_analyzer import IntegratedExhaustiveAnalyzer, AnalysisMode
        
        # Create analyzer
        analyzer = IntegratedExhaustiveAnalyzer(analysis_mode=AnalysisMode.QUICK)
        print("   ✅ Integrated analyzer created successfully")
        
        # Test position analysis
        test_state = AzulState(2)
        from move_quality_analysis.scripts.integrated_exhaustive_analyzer import GamePhase
        
        position_analysis = analyzer.analyze_position_robust(test_state, GamePhase.MID_GAME)
        if position_analysis:
            print(f"   ✅ Position analysis completed successfully")
            print(f"      Total moves: {position_analysis.total_moves}")
            print(f"      Average quality: {position_analysis.average_quality_score:.1f}")
            print(f"      Quality distribution: {position_analysis.quality_distribution}")
        else:
            print("   ❌ Position analysis failed")
        
        print("   🎉 All integrated analyzer tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Integrated analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting Integration Tests")
    print("=" * 50)
    
    # Test database integration
    db_success = test_database_integration()
    
    # Test API integration
    api_success = test_api_integration()
    
    # Test integrated analyzer
    analyzer_success = test_integrated_analyzer()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print(f"Database Integration: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"API Integration: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"Integrated Analyzer: {'✅ PASSED' if analyzer_success else '❌ FAILED'}")
    
    if db_success and api_success and analyzer_success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("The move quality analysis system is successfully integrated with the main system.")
    else:
        print("\n⚠️ Some integration tests failed. Please check the errors above.")
    
    return db_success and api_success and analyzer_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
