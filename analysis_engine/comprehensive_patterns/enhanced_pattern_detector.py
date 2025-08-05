"""
Enhanced Pattern Detector - Taxonomy Integration

This module integrates the comprehensive pattern taxonomy with existing pattern detectors
to provide a unified, taxonomy-aware pattern detection system.

Features:
- Taxonomy-based pattern classification
- Enhanced pattern detection with taxonomy validation
- Pattern interaction analysis
- Edge case handling
- Comprehensive pattern reporting
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple, Any
from dataclasses import dataclass
from core import azul_utils as utils
from core.azul_model import AzulState

# Import existing pattern detectors
from .azul_patterns import AzulPatternDetector, BlockingOpportunity, PatternDetection
from .azul_scoring_optimization import AzulScoringOptimizationDetector, ScoringOpportunity, ScoringOptimizationDetection
from .azul_floor_line_patterns import AzulFloorLinePatternDetector, FloorLineOpportunity, FloorLinePatternDetection

# Import taxonomy components
from .comprehensive_pattern_taxonomy import (
    ComprehensivePatternTaxonomy,
    TAXONOMY_MANAGER,
    COMPREHENSIVE_PATTERN_TAXONOMY,
    PatternCategory,
    PatternUrgency,
    PatternComplexity,
    PatternDefinition,
    PatternInstance
)


@dataclass
class TaxonomyPatternInstance:
    """Enhanced pattern instance with taxonomy information."""
    pattern_definition: PatternDefinition
    state: AzulState
    player_id: int
    urgency_score: float
    confidence_score: float
    complexity_score: float
    success_probability: float
    move_suggestions: List[Dict]
    alternative_executions: List[Dict]
    interaction_effects: Dict
    edge_case_flags: List[str]
    raw_detection_data: Any  # Original detection data from existing detectors


@dataclass
class ComprehensivePatternAnalysis:
    """Complete pattern analysis with taxonomy integration."""
    # Taxonomy-organized patterns
    tactical_patterns: List[TaxonomyPatternInstance]
    strategic_patterns: List[TaxonomyPatternInstance]
    endgame_patterns: List[TaxonomyPatternInstance]
    meta_patterns: List[TaxonomyPatternInstance]
    edge_case_patterns: List[TaxonomyPatternInstance]
    
    # Original detector results (for backward compatibility)
    blocking_opportunities: List[BlockingOpportunity]
    scoring_opportunities: List[ScoringOpportunity]
    floor_line_opportunities: List[FloorLineOpportunity]
    
    # Analysis metadata
    total_patterns: int
    confidence_score: float
    taxonomy_coverage: float
    edge_case_coverage: float
    pattern_interactions: Dict
    analysis_quality: Dict


class EnhancedPatternDetector:
    """
    Enhanced pattern detector with comprehensive taxonomy integration.
    
    This detector combines the existing pattern detection capabilities
    with the comprehensive taxonomy to provide:
    - Taxonomy-aware pattern classification
    - Enhanced pattern validation
    - Pattern interaction analysis
    - Edge case handling
    - Comprehensive reporting
    """
    
    def __init__(self):
        # Initialize existing detectors
        self.basic_pattern_detector = AzulPatternDetector()
        self.scoring_optimization_detector = AzulScoringOptimizationDetector()
        self.floor_line_pattern_detector = AzulFloorLinePatternDetector()
        
        # Initialize taxonomy components
        self.taxonomy = COMPREHENSIVE_PATTERN_TAXONOMY
        self.taxonomy_manager = TAXONOMY_MANAGER
        
        # Analysis thresholds
        self.min_confidence_threshold = 0.6
        self.min_urgency_threshold = 0.5
        self.edge_case_threshold = 0.8
    
    def detect_patterns_comprehensive(self, state: AzulState, player_id: int) -> ComprehensivePatternAnalysis:
        """
        Perform comprehensive pattern detection with taxonomy integration.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            ComprehensivePatternAnalysis with all detected patterns organized by taxonomy
        """
        
        # Run existing pattern detectors
        try:
            basic_patterns = self.basic_pattern_detector.detect_patterns(state, player_id)
        except Exception as e:
            print(f"Warning: Basic pattern detection failed: {e}")
            basic_patterns = PatternDetection(blocking_opportunities=[], patterns_detected=False, total_patterns=0, confidence_score=0.0)
        
        try:
            scoring_patterns = self.scoring_optimization_detector.detect_scoring_optimization(state, player_id)
        except Exception as e:
            print(f"Warning: Scoring optimization detection failed: {e}")
            scoring_patterns = ScoringOptimizationDetection(wall_completion_opportunities=[], pattern_line_opportunities=[], floor_line_opportunities=[], multiplier_opportunities=[], total_opportunities=0, total_potential_bonus=0, confidence_score=0.0)
        
        try:
            floor_line_patterns = self.floor_line_pattern_detector.detect_floor_line_patterns(state, player_id)
        except Exception as e:
            print(f"Warning: Floor line pattern detection failed: {e}")
            floor_line_patterns = FloorLinePatternDetection(risk_mitigation_opportunities=[], timing_optimization_opportunities=[], trade_off_opportunities=[], endgame_management_opportunities=[], blocking_opportunities=[], efficiency_opportunities=[], total_opportunities=0, total_penalty_risk=0, confidence_score=0.0)
        
        # Convert to taxonomy-aware patterns
        taxonomy_patterns = self._convert_to_taxonomy_patterns(
            state, player_id, basic_patterns, scoring_patterns, floor_line_patterns
        )
        
        # Organize patterns by taxonomy category
        organized_patterns = self._organize_patterns_by_taxonomy(taxonomy_patterns)
        
        # Analyze pattern interactions
        pattern_interactions = self._analyze_pattern_interactions(organized_patterns)
        
        # Calculate analysis quality metrics
        analysis_quality = self._calculate_analysis_quality(organized_patterns, pattern_interactions)
        
        return ComprehensivePatternAnalysis(
            tactical_patterns=organized_patterns.get('tactical', []),
            strategic_patterns=organized_patterns.get('strategic', []),
            endgame_patterns=organized_patterns.get('endgame', []),
            meta_patterns=organized_patterns.get('meta', []),
            edge_case_patterns=organized_patterns.get('edge_case', []),
            blocking_opportunities=basic_patterns.blocking_opportunities,
            scoring_opportunities=scoring_patterns.wall_completion_opportunities,
            floor_line_opportunities=floor_line_patterns.risk_mitigation_opportunities,
            total_patterns=len(taxonomy_patterns),
            confidence_score=self._calculate_overall_confidence(organized_patterns),
            taxonomy_coverage=self._calculate_taxonomy_coverage(organized_patterns),
            edge_case_coverage=self._calculate_edge_case_coverage(organized_patterns),
            pattern_interactions=pattern_interactions,
            analysis_quality=analysis_quality
        )
    
    def _convert_to_taxonomy_patterns(self, state: AzulState, player_id: int,
                                    basic_patterns: PatternDetection,
                                    scoring_patterns: ScoringOptimizationDetection,
                                    floor_line_patterns: FloorLinePatternDetection) -> List[TaxonomyPatternInstance]:
        """Convert existing pattern detection results to taxonomy-aware patterns."""
        
        taxonomy_patterns = []
        
        # Convert blocking opportunities to single_color_block patterns
        for blocking_opp in basic_patterns.blocking_opportunities:
            try:
                pattern_def = self.taxonomy_manager.get_pattern_definition("single_color_block")
                if pattern_def:
                    taxonomy_pattern = self._create_taxonomy_pattern_instance(
                        pattern_def, state, player_id, blocking_opp
                    )
                    taxonomy_patterns.append(taxonomy_pattern)
            except Exception as e:
                print(f"Warning: Could not create taxonomy pattern for blocking opportunity: {e}")
                continue
        
        # Convert scoring opportunities to immediate_wall_placement patterns
        for scoring_opp in scoring_patterns.wall_completion_opportunities:
            try:
                pattern_def = self.taxonomy_manager.get_pattern_definition("immediate_wall_placement")
                if pattern_def:
                    taxonomy_pattern = self._create_taxonomy_pattern_instance(
                        pattern_def, state, player_id, scoring_opp
                    )
                    taxonomy_patterns.append(taxonomy_pattern)
            except Exception as e:
                print(f"Warning: Could not create taxonomy pattern for scoring opportunity: {e}")
                continue
        
        # Convert floor line opportunities to floor_reduction patterns
        for floor_opp in floor_line_patterns.risk_mitigation_opportunities:
            try:
                pattern_def = self.taxonomy_manager.get_pattern_definition("floor_reduction")
                if pattern_def:
                    taxonomy_pattern = self._create_taxonomy_pattern_instance(
                        pattern_def, state, player_id, floor_opp
                    )
                    taxonomy_patterns.append(taxonomy_pattern)
            except Exception as e:
                print(f"Warning: Could not create taxonomy pattern for floor line opportunity: {e}")
                continue
        
        # Detect additional patterns based on taxonomy
        try:
            additional_patterns = self._detect_additional_taxonomy_patterns(state, player_id)
            taxonomy_patterns.extend(additional_patterns)
        except Exception as e:
            print(f"Warning: Could not detect additional taxonomy patterns: {e}")
            # Continue with existing patterns
        
        return taxonomy_patterns
    
    def _create_taxonomy_pattern_instance(self, pattern_def: PatternDefinition, 
                                        state: AzulState, player_id: int, 
                                        raw_data: Any) -> TaxonomyPatternInstance:
        """Create a taxonomy pattern instance from raw detection data."""
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(pattern_def, raw_data)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(pattern_def, raw_data)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(pattern_def, raw_data)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(pattern_def, raw_data)
        
        # Generate move suggestions
        move_suggestions = self._generate_move_suggestions(pattern_def, raw_data)
        
        # Find alternative executions
        alternative_executions = self._find_alternative_executions(pattern_def, raw_data)
        
        # Analyze interaction effects
        interaction_effects = self._analyze_interaction_effects(pattern_def, raw_data)
        
        # Check for edge cases
        edge_case_flags = self._check_edge_cases(pattern_def, raw_data)
        
        return TaxonomyPatternInstance(
            pattern_definition=pattern_def,
            state=state,
            player_id=player_id,
            urgency_score=urgency_score,
            confidence_score=confidence_score,
            complexity_score=complexity_score,
            success_probability=success_probability,
            move_suggestions=move_suggestions,
            alternative_executions=alternative_executions,
            interaction_effects=interaction_effects,
            edge_case_flags=edge_case_flags,
            raw_detection_data=raw_data
        )
    
    def _detect_additional_taxonomy_patterns(self, state: AzulState, player_id: int) -> List[TaxonomyPatternInstance]:
        """Detect additional patterns based on taxonomy definitions."""
        
        additional_patterns = []
        
        # Detect wall structure patterns (strategic)
        wall_structure_pattern = self._detect_wall_structure_pattern(state, player_id)
        if wall_structure_pattern:
            additional_patterns.append(wall_structure_pattern)
        
        # Detect initiative control patterns (strategic)
        initiative_pattern = self._detect_initiative_control_pattern(state, player_id)
        if initiative_pattern:
            additional_patterns.append(initiative_pattern)
        
        # Detect row race patterns (endgame)
        row_race_pattern = self._detect_row_race_pattern(state, player_id)
        if row_race_pattern:
            additional_patterns.append(row_race_pattern)
        
        # Detect bonus stacking patterns (endgame)
        bonus_stacking_pattern = self._detect_bonus_stacking_pattern(state, player_id)
        if bonus_stacking_pattern:
            additional_patterns.append(bonus_stacking_pattern)
        
        # Detect tile counting patterns (meta)
        tile_counting_pattern = self._detect_tile_counting_pattern(state, player_id)
        if tile_counting_pattern:
            additional_patterns.append(tile_counting_pattern)
        
        # Detect edge cases
        edge_case_patterns = self._detect_edge_case_patterns(state, player_id)
        additional_patterns.extend(edge_case_patterns)
        
        return additional_patterns
    
    def _detect_wall_structure_pattern(self, state: AzulState, player_id: int) -> Optional[TaxonomyPatternInstance]:
        """Detect wall structure development patterns."""
        
        pattern_def = self.taxonomy_manager.get_pattern_definition("wall_structure")
        if not pattern_def:
            return None
        
        # Analyze wall structure
        player_state = state.agents[player_id]
        wall = player_state.grid_state
        
        # Check for wall development opportunities
        development_score = self._calculate_wall_development_score(wall)
        
        if development_score > 0.3:  # Threshold for wall structure pattern
            return self._create_taxonomy_pattern_instance(
                pattern_def, state, player_id, {'development_score': development_score}
            )
        
        return None
    
    def _detect_initiative_control_pattern(self, state: AzulState, player_id: int) -> Optional[TaxonomyPatternInstance]:
        """Detect initiative control patterns."""
        
        pattern_def = self.taxonomy_manager.get_pattern_definition("initiative_control")
        if not pattern_def:
            return None
        
        # Analyze initiative opportunities
        initiative_score = self._calculate_initiative_score(state, player_id)
        
        if initiative_score > 0.4:  # Threshold for initiative control
            return self._create_taxonomy_pattern_instance(
                pattern_def, state, player_id, {'initiative_score': initiative_score}
            )
        
        return None
    
    def _detect_row_race_pattern(self, state: AzulState, player_id: int) -> Optional[TaxonomyPatternInstance]:
        """Detect row completion race patterns."""
        
        pattern_def = self.taxonomy_manager.get_pattern_definition("row_race")
        if not pattern_def:
            return None
        
        # Analyze row completion races
        race_score = self._calculate_row_race_score(state, player_id)
        
        if race_score > 0.5:  # Threshold for row race
            return self._create_taxonomy_pattern_instance(
                pattern_def, state, player_id, {'race_score': race_score}
            )
        
        return None
    
    def _detect_bonus_stacking_pattern(self, state: AzulState, player_id: int) -> Optional[TaxonomyPatternInstance]:
        """Detect bonus stacking patterns."""
        
        pattern_def = self.taxonomy_manager.get_pattern_definition("bonus_stacking")
        if not pattern_def:
            return None
        
        # Analyze bonus stacking opportunities
        stacking_score = self._calculate_bonus_stacking_score(state, player_id)
        
        if stacking_score > 0.6:  # Threshold for bonus stacking
            return self._create_taxonomy_pattern_instance(
                pattern_def, state, player_id, {'stacking_score': stacking_score}
            )
        
        return None
    
    def _detect_tile_counting_pattern(self, state: AzulState, player_id: int) -> Optional[TaxonomyPatternInstance]:
        """Detect tile counting patterns."""
        
        pattern_def = self.taxonomy_manager.get_pattern_definition("tile_counting")
        if not pattern_def:
            return None
        
        # Analyze tile counting opportunities
        counting_score = self._calculate_tile_counting_score(state)
        
        if counting_score > 0.4:  # Threshold for tile counting
            return self._create_taxonomy_pattern_instance(
                pattern_def, state, player_id, {'counting_score': counting_score}
            )
        
        return None
    
    def _detect_edge_case_patterns(self, state: AzulState, player_id: int) -> List[TaxonomyPatternInstance]:
        """Detect edge case patterns."""
        
        edge_case_patterns = []
        
        # Check for all same color in bag
        if self._is_all_same_color_in_bag(state):
            pattern_def = self.taxonomy_manager.get_pattern_definition("all_same_color_in_bag")
            if pattern_def:
                edge_case_patterns.append(self._create_taxonomy_pattern_instance(
                    pattern_def, state, player_id, {'edge_case_type': 'all_same_color'}
                ))
        
        # Check for simultaneous wall completion
        if self._is_simultaneous_wall_completion(state):
            pattern_def = self.taxonomy_manager.get_pattern_definition("simultaneous_wall_completion")
            if pattern_def:
                edge_case_patterns.append(self._create_taxonomy_pattern_instance(
                    pattern_def, state, player_id, {'edge_case_type': 'simultaneous_completion'}
                ))
        
        return edge_case_patterns
    
    def _organize_patterns_by_taxonomy(self, patterns: List[TaxonomyPatternInstance]) -> Dict[str, List[TaxonomyPatternInstance]]:
        """Organize patterns by taxonomy category."""
        
        organized = {
            'tactical': [],
            'strategic': [],
            'endgame': [],
            'meta': [],
            'edge_case': []
        }
        
        for pattern in patterns:
            category = pattern.pattern_definition.category.value
            if category in organized:
                organized[category].append(pattern)
        
        return organized
    
    def _analyze_pattern_interactions(self, organized_patterns: Dict[str, List[TaxonomyPatternInstance]]) -> Dict:
        """Analyze interactions between patterns."""
        
        interactions = {}
        
        # Analyze tactical-strategic interactions
        tactical_patterns = organized_patterns.get('tactical', [])
        strategic_patterns = organized_patterns.get('strategic', [])
        
        for tactical in tactical_patterns:
            for strategic in strategic_patterns:
                interaction_strength = self._calculate_pattern_interaction(tactical, strategic)
                if interaction_strength > 0.3:  # Significant interaction
                    key = f"{tactical.pattern_definition.pattern_id}_{strategic.pattern_definition.pattern_id}"
                    interactions[key] = {
                        'type': 'tactical_strategic',
                        'strength': interaction_strength,
                        'description': f"Tactical pattern {tactical.pattern_definition.name} interacts with strategic pattern {strategic.pattern_definition.name}"
                    }
        
        return interactions
    
    def _calculate_analysis_quality(self, organized_patterns: Dict[str, List[TaxonomyPatternInstance]], 
                                  pattern_interactions: Dict) -> Dict:
        """Calculate overall analysis quality metrics."""
        
        total_patterns = sum(len(patterns) for patterns in organized_patterns.values())
        total_interactions = len(pattern_interactions)
        
        # Calculate coverage metrics
        taxonomy_coverage = self._calculate_taxonomy_coverage(organized_patterns)
        edge_case_coverage = self._calculate_edge_case_coverage(organized_patterns)
        
        # Calculate quality score
        quality_score = (taxonomy_coverage + edge_case_coverage) / 2
        
        return {
            'total_patterns': total_patterns,
            'total_interactions': total_interactions,
            'coverage_score': taxonomy_coverage,
            'confidence_score': quality_score,
            'complexity_score': edge_case_coverage,
            'taxonomy_coverage': taxonomy_coverage,
            'edge_case_coverage': edge_case_coverage,
            'quality_score': quality_score,
            'confidence_level': 'high' if quality_score > 0.8 else 'medium' if quality_score > 0.6 else 'low'
        }
    
    # Helper methods for pattern detection
    def _calculate_urgency_score(self, pattern_def: PatternDefinition, raw_data: Any) -> float:
        """Calculate urgency score for a pattern."""
        # Implementation would analyze raw_data and pattern definition
        # For now, return a default score
        return 0.7
    
    def _calculate_confidence_score(self, pattern_def: PatternDefinition, raw_data: Any) -> float:
        """Calculate confidence score for a pattern."""
        # Implementation would analyze pattern definition criteria
        return 0.8
    
    def _calculate_complexity_score(self, pattern_def: PatternDefinition, raw_data: Any) -> float:
        """Calculate complexity score for a pattern."""
        # Implementation would analyze complexity factors
        return 0.6
    
    def _calculate_success_probability(self, pattern_def: PatternDefinition, raw_data: Any) -> float:
        """Calculate success probability for a pattern."""
        # Implementation would analyze success metrics
        return 0.75
    
    def _generate_move_suggestions(self, pattern_def: PatternDefinition, raw_data: Any) -> List[Dict]:
        """Generate move suggestions for a pattern."""
        # Implementation would generate specific moves
        return [{'type': 'suggestion', 'description': 'Move suggestion based on pattern'}]
    
    def _find_alternative_executions(self, pattern_def: PatternDefinition, raw_data: Any) -> List[Dict]:
        """Find alternative execution paths for a pattern."""
        # Implementation would find alternatives
        return [{'type': 'alternative', 'description': 'Alternative execution path'}]
    
    def _analyze_interaction_effects(self, pattern_def: PatternDefinition, raw_data: Any) -> Dict:
        """Analyze interaction effects for a pattern."""
        # Implementation would analyze interactions
        return {'synergistic': [], 'conflicting': [], 'neutral': []}
    
    def _check_edge_cases(self, pattern_def: PatternDefinition, raw_data: Any) -> List[str]:
        """Check for edge cases in pattern execution."""
        # Implementation would check edge cases
        return []
    
    def _calculate_wall_development_score(self, wall) -> float:
        """Calculate wall development score."""
        # Implementation would analyze wall structure
        return 0.5
    
    def _calculate_initiative_score(self, state: AzulState, player_id: int) -> float:
        """Calculate initiative control score."""
        # Implementation would analyze initiative opportunities
        return 0.4
    
    def _calculate_row_race_score(self, state: AzulState, player_id: int) -> float:
        """Calculate row race score."""
        # Implementation would analyze row completion races
        return 0.3
    
    def _calculate_bonus_stacking_score(self, state: AzulState, player_id: int) -> float:
        """Calculate bonus stacking score."""
        # Implementation would analyze bonus stacking opportunities
        return 0.2
    
    def _calculate_tile_counting_score(self, state: AzulState) -> float:
        """Calculate tile counting score."""
        # Implementation would analyze tile counting opportunities
        return 0.6
    
    def _is_all_same_color_in_bag(self, state: AzulState) -> bool:
        """Check if bag contains only one color."""
        # Implementation would check bag contents
        return False
    
    def _is_simultaneous_wall_completion(self, state: AzulState) -> bool:
        """Check for simultaneous wall completion."""
        # Implementation would check for simultaneous completions
        return False
    
    def _calculate_pattern_interaction(self, pattern1: TaxonomyPatternInstance, 
                                    pattern2: TaxonomyPatternInstance) -> float:
        """Calculate interaction strength between two patterns."""
        # Implementation would calculate interaction strength
        return 0.5
    
    def _calculate_taxonomy_coverage(self, organized_patterns: Dict[str, List[TaxonomyPatternInstance]]) -> float:
        """Calculate taxonomy coverage percentage."""
        total_categories = 5
        covered_categories = sum(1 for patterns in organized_patterns.values() if len(patterns) > 0)
        return covered_categories / total_categories
    
    def _calculate_edge_case_coverage(self, organized_patterns: Dict[str, List[TaxonomyPatternInstance]]) -> float:
        """Calculate edge case coverage percentage."""
        edge_case_patterns = organized_patterns.get('edge_case', [])
        return min(len(edge_case_patterns) / 10.0, 1.0)  # Normalize to 0-1
    
    def _calculate_overall_confidence(self, organized_patterns: Dict[str, List[TaxonomyPatternInstance]]) -> float:
        """Calculate overall confidence score."""
        all_patterns = []
        for patterns in organized_patterns.values():
            all_patterns.extend(patterns)
        
        if not all_patterns:
            return 0.0
        
        total_confidence = sum(pattern.confidence_score for pattern in all_patterns)
        return total_confidence / len(all_patterns)
    
    def get_patterns_by_category(self, category: PatternCategory) -> List[TaxonomyPatternInstance]:
        """Get all patterns of a specific category."""
        # This would be implemented to return patterns by category
        return []
    
    def get_patterns_by_urgency(self, min_urgency: float) -> List[TaxonomyPatternInstance]:
        """Get all patterns with urgency above threshold."""
        # This would be implemented to return patterns by urgency
        return []
    
    def get_pattern_recommendations(self, state: AzulState, player_id: int) -> List[Dict]:
        """Get pattern-based move recommendations."""
        analysis = self.detect_patterns_comprehensive(state, player_id)
        
        recommendations = []
        
        # Add recommendations from each category
        for category_patterns in [analysis.tactical_patterns, analysis.strategic_patterns, 
                                analysis.endgame_patterns, analysis.meta_patterns]:
            for pattern in category_patterns:
                if pattern.urgency_score > self.min_urgency_threshold:
                    recommendations.append({
                        'pattern_name': pattern.pattern_definition.name,
                        'category': pattern.pattern_definition.category.value,
                        'urgency': pattern.urgency_score,
                        'confidence': pattern.confidence_score,
                        'moves': pattern.move_suggestions,
                        'alternatives': pattern.alternative_executions
                    })
        
        return sorted(recommendations, key=lambda x: x['urgency'], reverse=True)
    
    def get_blocking_move_suggestions(self, state: AzulState, player_id: int, blocking_opportunities: List) -> List[Dict]:
        """Get move suggestions for blocking opportunities."""
        suggestions = []
        
        for opp in blocking_opportunities:
            if hasattr(opp, 'target_player') and hasattr(opp, 'target_pattern_line'):
                suggestion = {
                    'type': 'blocking',
                    'target_player': getattr(opp, 'target_player', 0),
                    'target_pattern_line': getattr(opp, 'target_pattern_line', 0),
                    'target_color': getattr(opp, 'target_color', 'blue'),
                    'urgency_score': getattr(opp, 'urgency_score', 0.5),
                    'description': getattr(opp, 'description', 'Block opponent pattern line'),
                    'move_type': 'factory_selection',
                    'priority': 'high' if getattr(opp, 'urgency_score', 0.5) > 0.8 else 'medium'
                }
                suggestions.append(suggestion)
        
        return suggestions 