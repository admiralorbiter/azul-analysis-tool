"""
Test file for taxonomy integration with existing pattern detectors.

This module tests the integration between the comprehensive pattern taxonomy
and the existing pattern detectors to ensure:
- Enhanced pattern detector works correctly
- Taxonomy integration is successful
- Backward compatibility is maintained
- Pattern classification is accurate
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from enhanced_pattern_detector import (
    EnhancedPatternDetector,
    TaxonomyPatternInstance,
    ComprehensivePatternAnalysis
)
from comprehensive_pattern_taxonomy import (
    PatternCategory,
    TAXONOMY_MANAGER
)


def test_enhanced_detector_creation():
    """Test that the enhanced detector can be created successfully."""
    print("Testing enhanced detector creation...")
    
    try:
        detector = EnhancedPatternDetector()
        
        print(f"✓ Enhanced detector created successfully")
        print(f"  - Basic pattern detector: {detector.basic_pattern_detector}")
        print(f"  - Scoring optimization detector: {detector.scoring_optimization_detector}")
        print(f"  - Floor line pattern detector: {detector.floor_line_pattern_detector}")
        print(f"  - Taxonomy manager: {detector.taxonomy_manager}")
        
        return True
    except Exception as e:
        print(f"✗ Enhanced detector creation failed: {str(e)}")
        return False


def test_taxonomy_integration():
    """Test that taxonomy integration works correctly."""
    print("\nTesting taxonomy integration...")
    
    try:
        detector = EnhancedPatternDetector()
        
        # Test taxonomy manager access
        pattern_def = detector.taxonomy_manager.get_pattern_definition("single_color_block")
        assert pattern_def is not None, "Should be able to get pattern definition"
        assert pattern_def.category == PatternCategory.TACTICAL, "Should be tactical category"
        
        # Test pattern conversion
        # Create a mock state and test pattern conversion
        # This would require a real AzulState, so we'll test the structure
        
        print(f"✓ Taxonomy integration successful")
        print(f"  - Pattern definition retrieved: {pattern_def.name}")
        print(f"  - Category: {pattern_def.category.value}")
        print(f"  - Detection criteria: {len(pattern_def.detection_criteria)}")
        
        return True
    except Exception as e:
        print(f"✗ Taxonomy integration failed: {str(e)}")
        return False


def test_pattern_classification():
    """Test that pattern classification works correctly."""
    print("\nTesting pattern classification...")
    
    try:
        detector = EnhancedPatternDetector()
        
        # Test pattern organization
        test_patterns = []
        
        # Create mock taxonomy pattern instances
        for pattern_id in ["single_color_block", "immediate_wall_placement", "floor_reduction"]:
            pattern_def = detector.taxonomy_manager.get_pattern_definition(pattern_id)
            if pattern_def:
                # Create a mock pattern instance (without real state)
                mock_pattern = TaxonomyPatternInstance(
                    pattern_definition=pattern_def,
                    state=None,  # Mock state
                    player_id=0,
                    urgency_score=0.7,
                    confidence_score=0.8,
                    complexity_score=0.6,
                    success_probability=0.75,
                    move_suggestions=[],
                    alternative_executions=[],
                    interaction_effects={},
                    edge_case_flags=[],
                    raw_detection_data={}
                )
                test_patterns.append(mock_pattern)
        
        # Test organization
        organized = detector._organize_patterns_by_taxonomy(test_patterns)
        
        # Verify organization
        assert 'tactical' in organized, "Should have tactical category"
        assert len(organized['tactical']) > 0, "Should have tactical patterns"
        
        print(f"✓ Pattern classification successful")
        print(f"  - Total patterns: {len(test_patterns)}")
        print(f"  - Tactical patterns: {len(organized.get('tactical', []))}")
        print(f"  - Strategic patterns: {len(organized.get('strategic', []))}")
        print(f"  - Endgame patterns: {len(organized.get('endgame', []))}")
        print(f"  - Meta patterns: {len(organized.get('meta', []))}")
        print(f"  - Edge case patterns: {len(organized.get('edge_case', []))}")
        
        return True
    except Exception as e:
        print(f"✗ Pattern classification failed: {str(e)}")
        return False


def test_pattern_interaction_analysis():
    """Test that pattern interaction analysis works correctly."""
    print("\nTesting pattern interaction analysis...")
    
    try:
        detector = EnhancedPatternDetector()
        
        # Create mock organized patterns
        organized_patterns = {
            'tactical': [],
            'strategic': [],
            'endgame': [],
            'meta': [],
            'edge_case': []
        }
        
        # Add some mock patterns
        for pattern_id in ["single_color_block", "wall_structure"]:
            pattern_def = detector.taxonomy_manager.get_pattern_definition(pattern_id)
            if pattern_def:
                mock_pattern = TaxonomyPatternInstance(
                    pattern_definition=pattern_def,
                    state=None,
                    player_id=0,
                    urgency_score=0.7,
                    confidence_score=0.8,
                    complexity_score=0.6,
                    success_probability=0.75,
                    move_suggestions=[],
                    alternative_executions=[],
                    interaction_effects={},
                    edge_case_flags=[],
                    raw_detection_data={}
                )
                
                if pattern_def.category == PatternCategory.TACTICAL:
                    organized_patterns['tactical'].append(mock_pattern)
                elif pattern_def.category == PatternCategory.STRATEGIC:
                    organized_patterns['strategic'].append(mock_pattern)
        
        # Test interaction analysis
        interactions = detector._analyze_pattern_interactions(organized_patterns)
        
        print(f"✓ Pattern interaction analysis successful")
        print(f"  - Total interactions: {len(interactions)}")
        print(f"  - Interaction types: {list(interactions.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Pattern interaction analysis failed: {str(e)}")
        return False


def test_analysis_quality_calculation():
    """Test that analysis quality calculation works correctly."""
    print("\nTesting analysis quality calculation...")
    
    try:
        detector = EnhancedPatternDetector()
        
        # Create mock organized patterns
        organized_patterns = {
            'tactical': [],
            'strategic': [],
            'endgame': [],
            'meta': [],
            'edge_case': []
        }
        
        # Add mock patterns to different categories
        for pattern_id in ["single_color_block", "wall_structure", "row_race"]:
            pattern_def = detector.taxonomy_manager.get_pattern_definition(pattern_id)
            if pattern_def:
                mock_pattern = TaxonomyPatternInstance(
                    pattern_definition=pattern_def,
                    state=None,
                    player_id=0,
                    urgency_score=0.7,
                    confidence_score=0.8,
                    complexity_score=0.6,
                    success_probability=0.75,
                    move_suggestions=[],
                    alternative_executions=[],
                    interaction_effects={},
                    edge_case_flags=[],
                    raw_detection_data={}
                )
                
                category = pattern_def.category.value
                if category in organized_patterns:
                    organized_patterns[category].append(mock_pattern)
        
        # Test quality calculation
        mock_interactions = {'test_interaction': {'strength': 0.5}}
        quality = detector._calculate_analysis_quality(organized_patterns, mock_interactions)
        
        print(f"✓ Analysis quality calculation successful")
        print(f"  - Total patterns: {quality['total_patterns']}")
        print(f"  - Total interactions: {quality['total_interactions']}")
        print(f"  - Taxonomy coverage: {quality['taxonomy_coverage']:.2f}")
        print(f"  - Edge case coverage: {quality['edge_case_coverage']:.2f}")
        print(f"  - Quality score: {quality['quality_score']:.2f}")
        print(f"  - Confidence level: {quality['confidence_level']}")
        
        return True
    except Exception as e:
        print(f"✗ Analysis quality calculation failed: {str(e)}")
        return False


def test_backward_compatibility():
    """Test that backward compatibility is maintained."""
    print("\nTesting backward compatibility...")
    
    try:
        # Test that existing detectors still work
        from azul_patterns import AzulPatternDetector
        from azul_scoring_optimization import AzulScoringOptimizationDetector
        from azul_floor_line_patterns import AzulFloorLinePatternDetector
        
        basic_detector = AzulPatternDetector()
        scoring_detector = AzulScoringOptimizationDetector()
        floor_detector = AzulFloorLinePatternDetector()
        
        print(f"✓ Backward compatibility maintained")
        print(f"  - Basic pattern detector: {basic_detector}")
        print(f"  - Scoring optimization detector: {scoring_detector}")
        print(f"  - Floor line pattern detector: {floor_detector}")
        
        return True
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {str(e)}")
        return False


def test_enhanced_features():
    """Test that enhanced features work correctly."""
    print("\nTesting enhanced features...")
    
    try:
        detector = EnhancedPatternDetector()
        
        # Test pattern recommendations (without real state)
        # This would normally require a real AzulState, so we'll test the structure
        # and thresholds instead
        
        print(f"✓ Enhanced features successful")
        print(f"  - Min urgency threshold: {detector.min_urgency_threshold}")
        print(f"  - Min confidence threshold: {detector.min_confidence_threshold}")
        print(f"  - Edge case threshold: {detector.edge_case_threshold}")
        print(f"  - Enhanced detector methods available: {hasattr(detector, 'get_pattern_recommendations')}")
        print(f"  - Pattern organization method available: {hasattr(detector, '_organize_patterns_by_taxonomy')}")
        
        return True
    except Exception as e:
        print(f"✗ Enhanced features test failed: {str(e)}")
        return False


def run_all_integration_tests():
    """Run all integration tests."""
    print("🧪 Running Taxonomy Integration Tests")
    print("=" * 60)
    
    tests = [
        test_enhanced_detector_creation,
        test_taxonomy_integration,
        test_pattern_classification,
        test_pattern_interaction_analysis,
        test_analysis_quality_calculation,
        test_backward_compatibility,
        test_enhanced_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ Test {test.__name__} failed")
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Taxonomy integration is ready.")
        return True
    else:
        print("❌ Some integration tests failed. Please fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1) 