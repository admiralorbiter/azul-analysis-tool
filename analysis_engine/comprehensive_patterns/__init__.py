"""
Comprehensive Patterns Analysis

This module contains pattern detection and analysis components for Azul.
"""

from .azul_patterns import AzulPatternDetector
from .azul_scoring_optimization import AzulScoringOptimizationDetector
from .azul_floor_line_patterns import AzulFloorLinePatternDetector
from .azul_move_analyzer import AzulMoveQualityAssessor
from .comprehensive_pattern_taxonomy import (
    ComprehensivePatternTaxonomy,
    ComprehensivePatternTaxonomyBuilder,
    ComprehensivePatternTaxonomyManager,
    PatternCategory,
    PatternUrgency,
    PatternComplexity,
    PatternDefinition,
    PatternInstance,
    create_comprehensive_pattern_taxonomy,
    COMPREHENSIVE_PATTERN_TAXONOMY,
    TAXONOMY_MANAGER
)

__all__ = [
    'AzulPatternDetector',
    'AzulScoringOptimizationDetector', 
    'AzulFloorLinePatternDetector',
    'AzulMoveQualityAssessor',
    'ComprehensivePatternTaxonomy',
    'ComprehensivePatternTaxonomyBuilder',
    'ComprehensivePatternTaxonomyManager',
    'PatternCategory',
    'PatternUrgency',
    'PatternComplexity',
    'PatternDefinition',
    'PatternInstance',
    'create_comprehensive_pattern_taxonomy',
    'COMPREHENSIVE_PATTERN_TAXONOMY',
    'TAXONOMY_MANAGER'
] 