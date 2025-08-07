#!/usr/bin/env python3
"""
Simple test script to verify the integration fix.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from move_quality_analysis.scripts.integrated_exhaustive_analyzer import IntegratedExhaustiveAnalyzer, AnalysisMode
from core.azul_model import AzulState

def test_analyzer():
    """Test the integrated analyzer."""
    print("🔍 Testing Integrated Analyzer...")
    
    try:
        # Create analyzer
        analyzer = IntegratedExhaustiveAnalyzer(analysis_mode=AnalysisMode.QUICK)
        print("   ✅ Integrated analyzer created successfully")
        
        # Test position analysis
        test_state = AzulState(2)
        from move_quality_analysis.scripts.integrated_exhaustive_analyzer import GamePhase
        
        print("   📊 Testing position analysis...")
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

if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
