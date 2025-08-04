"""
Demonstration script for the Comprehensive Pattern Taxonomy.

This script shows how to use the taxonomy for:
- Pattern discovery and classification
- Category-based pattern analysis
- Edge case handling
- Pattern interaction analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from comprehensive_pattern_taxonomy import (
    COMPREHENSIVE_PATTERN_TAXONOMY,
    TAXONOMY_MANAGER,
    PatternCategory,
    PatternUrgency,
    PatternComplexity
)


def demo_taxonomy_overview():
    """Demonstrate the taxonomy overview."""
    print("🏆 Comprehensive Pattern Taxonomy Overview")
    print("=" * 60)
    
    taxonomy = COMPREHENSIVE_PATTERN_TAXONOMY
    
    print(f"📊 Total Pattern Definitions: {len(taxonomy.pattern_definitions)}")
    print(f"📂 Categories: {len(taxonomy.category_hierarchy)}")
    print(f"⚠️  Edge Case Categories: {len(taxonomy.edge_case_catalog)}")
    
    print("\n📋 Pattern Categories:")
    for category in PatternCategory:
        patterns = TAXONOMY_MANAGER.get_patterns_by_category(category)
        print(f"  {category.value.upper()}: {len(patterns)} patterns")
    
    print("\n🔍 Edge Case Categories:")
    for category, edge_cases in taxonomy.edge_case_catalog.items():
        print(f"  {category}: {len(edge_cases)} edge cases")


def demo_pattern_details():
    """Demonstrate detailed pattern information."""
    print("\n\n🔍 Pattern Details")
    print("=" * 60)
    
    # Show details for a few key patterns
    key_patterns = [
        "single_color_block",
        "immediate_wall_placement", 
        "floor_reduction",
        "wall_structure",
        "initiative_control"
    ]
    
    for pattern_id in key_patterns:
        pattern_def = TAXONOMY_MANAGER.get_pattern_definition(pattern_id)
        if pattern_def:
            print(f"\n📌 {pattern_def.name} ({pattern_id})")
            print(f"   Category: {pattern_def.category.value}")
            print(f"   Description: {pattern_def.description}")
            print(f"   Detection Criteria: {len(pattern_def.detection_criteria)} criteria")
            print(f"   Urgency Factors: {len(pattern_def.urgency_factors)} factors")
            print(f"   Success Metrics: {len(pattern_def.success_metrics)} metrics")
            print(f"   Example Scenarios: {len(pattern_def.example_scenarios)} scenarios")


def demo_category_analysis():
    """Demonstrate category-based analysis."""
    print("\n\n📂 Category Analysis")
    print("=" * 60)
    
    # Analyze each category
    for category in PatternCategory:
        patterns = TAXONOMY_MANAGER.get_patterns_by_category(category)
        print(f"\n🎯 {category.value.upper()} Patterns ({len(patterns)} total):")
        
        for pattern in patterns:
            print(f"  • {pattern.name}: {pattern.description[:60]}...")


def demo_edge_case_handling():
    """Demonstrate edge case handling."""
    print("\n\n⚠️  Edge Case Handling")
    print("=" * 60)
    
    taxonomy = COMPREHENSIVE_PATTERN_TAXONOMY
    
    for category, edge_cases in taxonomy.edge_case_catalog.items():
        print(f"\n🔧 {category}:")
        for edge_case in edge_cases:
            print(f"  • {edge_case}")


def demo_pattern_interactions():
    """Demonstrate pattern interaction analysis."""
    print("\n\n🔄 Pattern Interactions")
    print("=" * 60)
    
    # Show interaction effects for key patterns
    key_patterns = ["single_color_block", "immediate_wall_placement", "floor_reduction"]
    
    for pattern_id in key_patterns:
        pattern_def = TAXONOMY_MANAGER.get_pattern_definition(pattern_id)
        if pattern_def:
            print(f"\n🔗 {pattern_def.name} Interactions:")
            for interaction in pattern_def.interaction_effects:
                print(f"  • {interaction}")


def demo_taxonomy_manager():
    """Demonstrate taxonomy manager functionality."""
    print("\n\n🛠️  Taxonomy Manager Functions")
    print("=" * 60)
    
    manager = TAXONOMY_MANAGER
    
    # Get tactical patterns
    tactical_patterns = manager.get_patterns_by_category(PatternCategory.TACTICAL)
    print(f"📊 Tactical Patterns: {len(tactical_patterns)}")
    for pattern in tactical_patterns:
        print(f"  • {pattern.name}")
    
    # Get blocking patterns specifically
    blocking_patterns = manager.get_patterns_by_subcategory(PatternCategory.TACTICAL, "blocking")
    print(f"\n🛡️  Blocking Patterns: {len(blocking_patterns)}")
    for pattern in blocking_patterns:
        print(f"  • {pattern.name}")
    
    # Get edge cases
    tile_edge_cases = manager.get_edge_cases_by_category("TILE_DISTRIBUTION_EDGE_CASES")
    print(f"\n🎲 Tile Distribution Edge Cases: {len(tile_edge_cases)}")
    for edge_case in tile_edge_cases:
        print(f"  • {edge_case}")


def demo_validation():
    """Demonstrate pattern validation."""
    print("\n\n✅ Pattern Validation")
    print("=" * 60)
    
    # Test validation for a pattern
    pattern_def = TAXONOMY_MANAGER.get_pattern_definition("single_color_block")
    if pattern_def:
        print(f"🔍 Validating {pattern_def.name}:")
        print(f"  ✓ Pattern ID: {pattern_def.pattern_id}")
        print(f"  ✓ Category: {pattern_def.category.value}")
        print(f"  ✓ Detection Criteria: {len(pattern_def.detection_criteria)}")
        print(f"  ✓ Urgency Factors: {len(pattern_def.urgency_factors)}")
        print(f"  ✓ Success Metrics: {len(pattern_def.success_metrics)}")
        print(f"  ✓ Complexity Factors: {len(pattern_def.complexity_factors)}")
        print(f"  ✓ Interaction Effects: {len(pattern_def.interaction_effects)}")
        print(f"  ✓ Edge Case Handling: {len(pattern_def.edge_case_handling)}")
        print(f"  ✓ Example Scenarios: {len(pattern_def.example_scenarios)}")
        print(f"  ✓ Counter Patterns: {len(pattern_def.counter_patterns)}")
        print(f"  ✓ Prerequisites: {len(pattern_def.prerequisites)}")
        print(f"  ✓ Alternatives: {len(pattern_def.alternatives)}")


def demo_scalability():
    """Demonstrate taxonomy scalability."""
    print("\n\n🚀 Taxonomy Scalability")
    print("=" * 60)
    
    taxonomy = COMPREHENSIVE_PATTERN_TAXONOMY
    
    print("📈 Current Scale:")
    print(f"  • Pattern Definitions: {len(taxonomy.pattern_definitions)}")
    print(f"  • Categories: {len(taxonomy.category_hierarchy)}")
    print(f"  • Edge Case Categories: {len(taxonomy.edge_case_catalog)}")
    
    print("\n🔧 Extensibility Features:")
    print("  • Easy to add new pattern definitions")
    print("  • Category hierarchy supports unlimited subcategories")
    print("  • Edge case catalog can handle any scenario")
    print("  • Interaction matrix supports complex relationships")
    print("  • Manager provides clean API for all operations")


def run_demo():
    """Run the complete taxonomy demonstration."""
    print("🎯 Comprehensive Pattern Taxonomy Demonstration")
    print("=" * 80)
    
    demos = [
        demo_taxonomy_overview,
        demo_pattern_details,
        demo_category_analysis,
        demo_edge_case_handling,
        demo_pattern_interactions,
        demo_taxonomy_manager,
        demo_validation,
        demo_scalability
    ]
    
    for demo in demos:
        try:
            demo()
            print("\n" + "-" * 40)
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
    
    print("\n🎉 Taxonomy demonstration complete!")
    print("✅ The comprehensive pattern taxonomy is ready for integration with the analysis engine.")


if __name__ == "__main__":
    run_demo() 