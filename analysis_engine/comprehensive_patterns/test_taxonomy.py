"""
Test file for comprehensive pattern taxonomy validation.

This module tests the comprehensive pattern taxonomy to ensure:
- Taxonomy can be created without errors
- All pattern definitions are valid
- Category hierarchy is complete
- Edge case catalog is comprehensive
- Manager functions work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from comprehensive_pattern_taxonomy import (
    ComprehensivePatternTaxonomy,
    ComprehensivePatternTaxonomyBuilder,
    ComprehensivePatternTaxonomyManager,
    PatternCategory,
    PatternUrgency,
    PatternComplexity,
    create_comprehensive_pattern_taxonomy,
    COMPREHENSIVE_PATTERN_TAXONOMY,
    TAXONOMY_MANAGER
)


def test_taxonomy_creation():
    """Test that the taxonomy can be created successfully."""
    print("Testing taxonomy creation...")
    
    try:
        # Test builder creation
        builder = ComprehensivePatternTaxonomyBuilder()
        taxonomy = builder.build_comprehensive_taxonomy()
        
        print(f"✓ Taxonomy created successfully")
        print(f"  - Pattern definitions: {len(taxonomy.pattern_definitions)}")
        print(f"  - Categories: {len(taxonomy.category_hierarchy)}")
        print(f"  - Edge case categories: {len(taxonomy.edge_case_catalog)}")
        
        return True
    except Exception as e:
        print(f"✗ Taxonomy creation failed: {str(e)}")
        return False


def test_pattern_definitions():
    """Test that all pattern definitions are valid."""
    print("\nTesting pattern definitions...")
    
    try:
        taxonomy = create_comprehensive_pattern_taxonomy()
        
        # Test each pattern definition
        for pattern_id, pattern_def in taxonomy.pattern_definitions.items():
            # Check required fields
            assert pattern_def.pattern_id == pattern_id
            assert pattern_def.category in PatternCategory
            assert pattern_def.name
            assert pattern_def.description
            assert len(pattern_def.detection_criteria) > 0
            assert len(pattern_def.urgency_factors) > 0
            assert len(pattern_def.success_metrics) > 0
            assert len(pattern_def.complexity_factors) > 0
            assert len(pattern_def.interaction_effects) > 0
            assert len(pattern_def.edge_case_handling) > 0
            assert len(pattern_def.example_scenarios) > 0
            assert len(pattern_def.counter_patterns) > 0
            assert len(pattern_def.prerequisites) > 0
            assert len(pattern_def.alternatives) > 0
        
        print(f"✓ All {len(taxonomy.pattern_definitions)} pattern definitions are valid")
        return True
    except Exception as e:
        print(f"✗ Pattern definition validation failed: {str(e)}")
        return False


def test_category_hierarchy():
    """Test that the category hierarchy is complete."""
    print("\nTesting category hierarchy...")
    
    try:
        taxonomy = create_comprehensive_pattern_taxonomy()
        
        # Check all categories are present
        expected_categories = [
            PatternCategory.TACTICAL,
            PatternCategory.STRATEGIC,
            PatternCategory.ENDGAME,
            PatternCategory.META,
            PatternCategory.EDGE_CASE
        ]
        
        for category in expected_categories:
            assert category in taxonomy.category_hierarchy
            assert len(taxonomy.category_hierarchy[category]) > 0
            
            # Check each subcategory has pattern IDs
            for subcategory, pattern_ids in taxonomy.category_hierarchy[category].items():
                assert len(pattern_ids) > 0
                for pattern_id in pattern_ids:
                    assert pattern_id in taxonomy.pattern_definitions
        
        print(f"✓ Category hierarchy is complete")
        print(f"  - TACTICAL subcategories: {len(taxonomy.category_hierarchy[PatternCategory.TACTICAL])}")
        print(f"  - STRATEGIC subcategories: {len(taxonomy.category_hierarchy[PatternCategory.STRATEGIC])}")
        print(f"  - ENDGAME subcategories: {len(taxonomy.category_hierarchy[PatternCategory.ENDGAME])}")
        print(f"  - META subcategories: {len(taxonomy.category_hierarchy[PatternCategory.META])}")
        print(f"  - EDGE_CASE subcategories: {len(taxonomy.category_hierarchy[PatternCategory.EDGE_CASE])}")
        
        return True
    except Exception as e:
        print(f"✗ Category hierarchy validation failed: {str(e)}")
        return False


def test_edge_case_catalog():
    """Test that the edge case catalog is comprehensive."""
    print("\nTesting edge case catalog...")
    
    try:
        taxonomy = create_comprehensive_pattern_taxonomy()
        
        # Check all edge case categories are present
        expected_edge_case_categories = [
            'TILE_DISTRIBUTION_EDGE_CASES',
            'SCORING_EDGE_CASES',
            'PATTERN_EDGE_CASES',
            'STRATEGIC_EDGE_CASES',
            'COMPUTATIONAL_EDGE_CASES'
        ]
        
        for category in expected_edge_case_categories:
            assert category in taxonomy.edge_case_catalog
            assert len(taxonomy.edge_case_catalog[category]) > 0
        
        print(f"✓ Edge case catalog is comprehensive")
        print(f"  - Total edge case categories: {len(taxonomy.edge_case_catalog)}")
        for category, edge_cases in taxonomy.edge_case_catalog.items():
            print(f"    {category}: {len(edge_cases)} edge cases")
        
        return True
    except Exception as e:
        print(f"✗ Edge case catalog validation failed: {str(e)}")
        return False


def test_taxonomy_manager():
    """Test that the taxonomy manager functions work correctly."""
    print("\nTesting taxonomy manager...")
    
    try:
        manager = TAXONOMY_MANAGER
        
        # Test getting pattern definition
        pattern_def = manager.get_pattern_definition("single_color_block")
        assert pattern_def is not None
        assert pattern_def.pattern_id == "single_color_block"
        assert pattern_def.category == PatternCategory.TACTICAL
        
        # Test getting patterns by category
        tactical_patterns = manager.get_patterns_by_category(PatternCategory.TACTICAL)
        assert len(tactical_patterns) > 0
        
        # Test getting patterns by subcategory
        blocking_patterns = manager.get_patterns_by_subcategory(PatternCategory.TACTICAL, "blocking")
        assert len(blocking_patterns) > 0
        
        # Test getting edge cases
        tile_distribution_edge_cases = manager.get_edge_cases_by_category("TILE_DISTRIBUTION_EDGE_CASES")
        assert len(tile_distribution_edge_cases) > 0
        
        print(f"✓ Taxonomy manager functions work correctly")
        print(f"  - Tactical patterns: {len(tactical_patterns)}")
        print(f"  - Blocking patterns: {len(blocking_patterns)}")
        print(f"  - Tile distribution edge cases: {len(tile_distribution_edge_cases)}")
        
        return True
    except Exception as e:
        print(f"✗ Taxonomy manager validation failed: {str(e)}")
        return False


def test_specific_patterns():
    """Test specific pattern definitions for completeness."""
    print("\nTesting specific pattern definitions...")
    
    try:
        taxonomy = create_comprehensive_pattern_taxonomy()
        
        # Test a few specific patterns
        test_patterns = [
            "single_color_block",
            "immediate_wall_placement", 
            "floor_reduction",
            "wall_structure",
            "initiative_control",
            "row_race",
            "bonus_stacking",
            "tile_counting",
            "nash_equilibrium",
            "all_same_color_in_bag",
            "simultaneous_wall_completion"
        ]
        
        for pattern_id in test_patterns:
            pattern_def = taxonomy.pattern_definitions.get(pattern_id)
            assert pattern_def is not None, f"Pattern {pattern_id} not found"
            assert pattern_def.pattern_id == pattern_id
            assert pattern_def.name
            assert pattern_def.description
            assert len(pattern_def.detection_criteria) > 0
            assert len(pattern_def.example_scenarios) > 0
        
        print(f"✓ All {len(test_patterns)} test patterns are complete")
        return True
    except Exception as e:
        print(f"✗ Specific pattern validation failed: {str(e)}")
        return False


def run_all_tests():
    """Run all taxonomy tests."""
    print("🧪 Running Comprehensive Pattern Taxonomy Tests")
    print("=" * 60)
    
    tests = [
        test_taxonomy_creation,
        test_pattern_definitions,
        test_category_hierarchy,
        test_edge_case_catalog,
        test_taxonomy_manager,
        test_specific_patterns
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
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Taxonomy is ready for use.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 