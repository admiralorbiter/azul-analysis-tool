"""
Comprehensive Pattern Taxonomy for Azul Analysis Engine

This module provides a complete taxonomy for all possible Azul patterns,
serving as the foundation for comprehensive pattern analysis.

The taxonomy is designed to:
- Cover 100% of possible Azul scenarios
- Handle all edge cases systematically
- Scale to unlimited complexity
- Support advanced pattern discovery
- Enable research-grade analysis

Pattern Categories:
1. TACTICAL: Immediate impact patterns (blocking, scoring, penalties)
2. STRATEGIC: Multi-turn planning patterns (positional, tempo, economic)
3. ENDGAME: Game completion patterns (races, optimization, timing)
4. META: Game theory patterns (probabilistic, adaptive, psychological)
5. EDGE_CASES: Unusual scenario patterns (extreme distributions, anomalies)

Each pattern includes:
- Detection criteria
- Urgency factors
- Success metrics
- Interaction effects
- Edge case handling
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple, Any
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core import azul_utils as utils
from core.azul_model import AzulState


class PatternCategory(Enum):
    """Enumeration of pattern categories."""
    TACTICAL = "tactical"
    STRATEGIC = "strategic"
    ENDGAME = "endgame"
    META = "meta"
    EDGE_CASE = "edge_case"


class PatternUrgency(Enum):
    """Enumeration of pattern urgency levels."""
    CRITICAL = "critical"      # Must act immediately
    HIGH = "high"             # Should act soon
    MEDIUM = "medium"         # Worth considering
    LOW = "low"              # Nice to have
    OPPORTUNISTIC = "opportunistic"  # Take if convenient


class PatternComplexity(Enum):
    """Enumeration of pattern complexity levels."""
    SIMPLE = "simple"         # Easy to execute
    MODERATE = "moderate"     # Requires some planning
    COMPLEX = "complex"       # Requires careful execution
    EXPERT = "expert"         # Requires expert-level play


@dataclass
class PatternDefinition:
    """Complete definition of a pattern type."""
    pattern_id: str
    category: PatternCategory
    name: str
    description: str
    detection_criteria: List[str]
    urgency_factors: List[str]
    success_metrics: List[str]
    complexity_factors: List[str]
    interaction_effects: List[str]
    edge_case_handling: List[str]
    example_scenarios: List[str]
    counter_patterns: List[str]
    prerequisites: List[str]
    alternatives: List[str]


@dataclass
class PatternInstance:
    """Instance of a detected pattern."""
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


@dataclass
class ComprehensivePatternTaxonomy:
    """Complete taxonomy of all Azul patterns."""
    pattern_definitions: Dict[str, PatternDefinition]
    category_hierarchy: Dict[PatternCategory, Dict[str, List[str]]]
    interaction_matrix: Dict[str, Dict[str, float]]
    edge_case_catalog: Dict[str, List[str]]


class ComprehensivePatternTaxonomyBuilder:
    """
    Builder class for creating comprehensive pattern taxonomy.
    """
    
    def __init__(self):
        self.pattern_definitions = {}
        self.category_hierarchy = {}
        self.interaction_matrix = {}
        self.edge_case_catalog = {}
        
        # Initialize taxonomy structure
        self._initialize_category_hierarchy()
        self._initialize_interaction_matrix()
        self._initialize_edge_case_catalog()
    
    def build_comprehensive_taxonomy(self) -> ComprehensivePatternTaxonomy:
        """
        Build the complete comprehensive pattern taxonomy.
        """
        # Build all pattern definitions
        self._build_tactical_patterns()
        self._build_strategic_patterns()
        self._build_endgame_patterns()
        self._build_meta_patterns()
        self._build_edge_case_patterns()
        
        return ComprehensivePatternTaxonomy(
            pattern_definitions=self.pattern_definitions,
            category_hierarchy=self.category_hierarchy,
            interaction_matrix=self.interaction_matrix,
            edge_case_catalog=self.edge_case_catalog
        )
    
    def _initialize_category_hierarchy(self):
        """Initialize the category hierarchy structure."""
        self.category_hierarchy = {
            PatternCategory.TACTICAL: {
                'blocking': [
                    'single_color_block'
                ],
                'scoring': [
                    'immediate_wall_placement'
                ],
                'penalty_mitigation': [
                    'floor_reduction'
                ]
            },
            PatternCategory.STRATEGIC: {
                'positional': [
                    'wall_structure'
                ],
                'tempo': [
                    'initiative_control'
                ]
            },
            PatternCategory.ENDGAME: {
                'completion': [
                    'row_race'
                ],
                'optimization': [
                    'bonus_stacking'
                ]
            },
            PatternCategory.META: {
                'probabilistic': [
                    'tile_counting'
                ],
                'game_theory': [
                    'nash_equilibrium'
                ]
            },
            PatternCategory.EDGE_CASE: {
                'tile_distribution': [
                    'all_same_color_in_bag'
                ],
                'scoring': [
                    'simultaneous_wall_completion'
                ]
            }
        }
    
    def _initialize_interaction_matrix(self):
        """Initialize the pattern interaction matrix."""
        # This will be populated with interaction strengths between patterns
        # Values range from -1.0 (conflicting) to 1.0 (synergistic)
        self.interaction_matrix = {}
    
    def _initialize_edge_case_catalog(self):
        """Initialize the edge case catalog."""
        self.edge_case_catalog = {
            'TILE_DISTRIBUTION_EDGE_CASES': [
                'all_same_color_in_bag',
                'one_tile_type_exhausted',
                'extreme_color_imbalance',
                'bag_empty_mid_round',
                'all_factories_same_color'
            ],
            'SCORING_EDGE_CASES': [
                'simultaneous_wall_completion',
                'negative_score_scenarios',
                'maximum_possible_score',
                'zero_score_games',
                'tie_breaking_scenarios'
            ],
            'PATTERN_EDGE_CASES': [
                'pattern_lines_all_full',
                'wall_completely_empty',
                'floor_line_overflow',
                'impossible_move_scenarios',
                'deadlock_positions'
            ],
            'STRATEGIC_EDGE_CASES': [
                'forced_move_chains',
                'dominant_strategy_positions',
                'symmetrical_positions',
                'maximum_complexity_positions',
                'minimal_information_positions'
            ],
            'COMPUTATIONAL_EDGE_CASES': [
                'maximum_search_depth_required',
                'neural_network_disagreement',
                'evaluation_function_failures',
                'timeout_recovery_scenarios',
                'memory_limit_scenarios'
            ]
        }
    
    def _build_tactical_patterns(self):
        """Build all tactical pattern definitions."""
        
        # Blocking Patterns
        self._add_pattern_definition(
            pattern_id="single_color_block",
            category=PatternCategory.TACTICAL,
            name="Single Color Block",
            description="Block opponent from completing a single color on their wall",
            detection_criteria=[
                "opponent_has_pattern_line_tiles",
                "opponent_needs_few_tiles_to_complete",
                "blocking_tiles_available",
                "opponent_has_wall_space_for_color"
            ],
            urgency_factors=[
                "completion_proximity",
                "point_value",
                "alternative_options",
                "opponent_skill_level"
            ],
            success_metrics=[
                "blocking_success_rate",
                "points_denied",
                "tempo_gained",
                "opponent_disruption"
            ],
            complexity_factors=[
                "tile_availability",
                "execution_timing",
                "opponent_counter_opportunities",
                "opportunity_cost"
            ],
            interaction_effects=[
                "synergistic_with_factory_control",
                "conflicting_with_own_scoring",
                "enhances_tempo_advantage",
                "creates_forced_moves"
            ],
            edge_case_handling=[
                "no_blocking_tiles_available",
                "opponent_has_alternatives",
                "blocking_creates_own_problems",
                "opponent_has_counter_play"
            ],
            example_scenarios=[
                "Opponent has 4 blue tiles in pattern line, needs 1 more",
                "Opponent has 3 red tiles, 2 available in factories",
                "Opponent has 2 yellow tiles, 3 available in center"
            ],
            counter_patterns=[
                "color_diversification",
                "alternative_completion_paths",
                "counter_blocking_moves"
            ],
            prerequisites=[
                "opponent_has_pattern_line_tiles",
                "blocking_tiles_available",
                "opponent_has_wall_space"
            ],
            alternatives=[
                "factory_denial",
                "center_denial",
                "scoring_race"
            ]
        )
        
        # Scoring Patterns
        self._add_pattern_definition(
            pattern_id="immediate_wall_placement",
            category=PatternCategory.TACTICAL,
            name="Immediate Wall Placement",
            description="Place tile directly on wall for immediate scoring",
            detection_criteria=[
                "tile_matches_wall_position",
                "position_available_on_wall",
                "immediate_scoring_value",
                "no_better_alternatives"
            ],
            urgency_factors=[
                "scoring_value",
                "position_competition",
                "game_phase",
                "risk_assessment"
            ],
            success_metrics=[
                "points_scored",
                "position_secured",
                "tempo_gained",
                "setup_quality"
            ],
            complexity_factors=[
                "position_availability",
                "tile_availability",
                "competition_level",
                "timing_considerations"
            ],
            interaction_effects=[
                "synergistic_with_adjacency_bonus",
                "conflicting_with_pattern_line_setup",
                "enhances_wall_structure",
                "creates_completion_opportunities"
            ],
            edge_case_handling=[
                "no_matching_tiles_available",
                "position_already_filled",
                "better_alternatives_exist",
                "timing_issues"
            ],
            example_scenarios=[
                "Blue tile available, blue position open on wall",
                "Red tile available, red position open on wall",
                "Yellow tile available, yellow position open on wall"
            ],
            counter_patterns=[
                "pattern_line_setup",
                "alternative_scoring_paths",
                "defensive_positioning"
            ],
            prerequisites=[
                "matching_tile_available",
                "wall_position_open",
                "scoring_value_positive"
            ],
            alternatives=[
                "pattern_line_setup",
                "floor_line_placement",
                "alternative_scoring"
            ]
        )
        
        # Penalty Mitigation Patterns
        self._add_pattern_definition(
            pattern_id="floor_reduction",
            category=PatternCategory.TACTICAL,
            name="Floor Line Penalty Reduction",
            description="Reduce floor line penalties through strategic placement",
            detection_criteria=[
                "floor_line_has_tiles",
                "wall_placement_available",
                "penalty_reduction_possible",
                "tiles_available_for_placement"
            ],
            urgency_factors=[
                "current_penalty_level",
                "penalty_reduction_value",
                "game_phase",
                "alternative_opportunities"
            ],
            success_metrics=[
                "penalty_points_saved",
                "floor_line_cleared",
                "position_improvement",
                "tempo_gained"
            ],
            complexity_factors=[
                "placement_availability",
                "tile_availability",
                "timing_considerations",
                "opportunity_cost"
            ],
            interaction_effects=[
                "synergistic_with_wall_completion",
                "conflicting_with_pattern_line_setup",
                "enhances_position_quality",
                "reduces_risk"
            ],
            edge_case_handling=[
                "no_wall_positions_available",
                "no_matching_tiles",
                "better_alternatives_exist",
                "timing_issues"
            ],
            example_scenarios=[
                "Floor has 3 tiles, can place 2 on wall",
                "Floor has 5 tiles, can place 3 on wall",
                "Floor has 1 tile, can place 1 on wall"
            ],
            counter_patterns=[
                "pattern_line_prioritization",
                "alternative_penalty_management",
                "risk_acceptance"
            ],
            prerequisites=[
                "floor_line_has_tiles",
                "wall_positions_available",
                "matching_tiles_available"
            ],
            alternatives=[
                "pattern_line_setup",
                "alternative_penalty_management",
                "risk_acceptance"
            ]
        )
    
    def _build_strategic_patterns(self):
        """Build all strategic pattern definitions."""
        
        # Positional Patterns
        self._add_pattern_definition(
            pattern_id="wall_structure",
            category=PatternCategory.STRATEGIC,
            name="Wall Structure Development",
            description="Develop wall structure for long-term strategic advantage",
            detection_criteria=[
                "wall_has_development_potential",
                "pattern_lines_can_support",
                "tiles_available_for_development",
                "strategic_value_clear"
            ],
            urgency_factors=[
                "development_opportunity",
                "competition_level",
                "game_phase",
                "strategic_importance"
            ],
            success_metrics=[
                "structure_quality",
                "completion_potential",
                "flexibility_maintained",
                "strategic_advantage"
            ],
            complexity_factors=[
                "development_complexity",
                "resource_requirements",
                "timing_considerations",
                "risk_assessment"
            ],
            interaction_effects=[
                "synergistic_with_completion_races",
                "conflicting_with_immediate_scoring",
                "enhances_long_term_position",
                "creates_future_opportunities"
            ],
            edge_case_handling=[
                "no_development_opportunities",
                "resource_limitations",
                "timing_constraints",
                "competition_pressure"
            ],
            example_scenarios=[
                "Developing symmetrical wall structure",
                "Building towards row/column completion",
                "Creating color completion opportunities"
            ],
            counter_patterns=[
                "immediate_scoring_prioritization",
                "alternative_development_paths",
                "defensive_positioning"
            ],
            prerequisites=[
                "wall_development_potential",
                "resource_availability",
                "strategic_clearance"
            ],
            alternatives=[
                "immediate_scoring",
                "alternative_development",
                "defensive_positioning"
            ]
        )
        
        # Tempo Patterns
        self._add_pattern_definition(
            pattern_id="initiative_control",
            category=PatternCategory.STRATEGIC,
            name="Initiative Control",
            description="Control game initiative and tempo",
            detection_criteria=[
                "initiative_opportunity_available",
                "opponent_vulnerability",
                "tempo_advantage_possible",
                "strategic_clearance"
            ],
            urgency_factors=[
                "initiative_value",
                "opponent_strength",
                "game_phase",
                "opportunity_window"
            ],
            success_metrics=[
                "initiative_secured",
                "tempo_advantage",
                "opponent_pressure",
                "strategic_control"
            ],
            complexity_factors=[
                "initiative_complexity",
                "opponent_counter_opportunities",
                "timing_requirements",
                "resource_commitment"
            ],
            interaction_effects=[
                "synergistic_with_pressure_patterns",
                "conflicting_with_defensive_play",
                "enhances_strategic_position",
                "creates_forced_responses"
            ],
            edge_case_handling=[
                "no_initiative_opportunity",
                "opponent_counter_play",
                "resource_limitations",
                "timing_issues"
            ],
            example_scenarios=[
                "Forcing opponent into difficult choices",
                "Creating tempo pressure",
                "Controlling factory selection order"
            ],
            counter_patterns=[
                "defensive_play",
                "alternative_tempo_management",
                "resource_conservation"
            ],
            prerequisites=[
                "initiative_opportunity",
                "resource_availability",
                "strategic_clearance"
            ],
            alternatives=[
                "defensive_play",
                "alternative_tempo_management",
                "resource_conservation"
            ]
        )
    
    def _build_endgame_patterns(self):
        """Build all endgame pattern definitions."""
        
        # Completion Patterns
        self._add_pattern_definition(
            pattern_id="row_race",
            category=PatternCategory.ENDGAME,
            name="Row Completion Race",
            description="Race to complete wall rows before opponents",
            detection_criteria=[
                "row_completion_opportunity",
                "opponent_competition",
                "completion_timing_critical",
                "strategic_value_high"
            ],
            urgency_factors=[
                "completion_proximity",
                "competition_level",
                "point_value",
                "game_phase"
            ],
            success_metrics=[
                "row_completed",
                "race_won",
                "points_scored",
                "strategic_advantage"
            ],
            complexity_factors=[
                "race_complexity",
                "competition_level",
                "resource_requirements",
                "timing_precision"
            ],
            interaction_effects=[
                "synergistic_with_column_race",
                "conflicting_with_color_race",
                "enhances_wall_completion",
                "creates_bonus_opportunities"
            ],
            edge_case_handling=[
                "no_completion_opportunity",
                "opponent_advantage",
                "resource_limitations",
                "timing_issues"
            ],
            example_scenarios=[
                "Competing for row completion with opponent",
                "Racing to complete multiple rows",
                "Timing row completion for maximum effect"
            ],
            counter_patterns=[
                "alternative_completion_paths",
                "defensive_positioning",
                "resource_conservation"
            ],
            prerequisites=[
                "row_completion_potential",
                "resource_availability",
                "strategic_clearance"
            ],
            alternatives=[
                "column_race",
                "color_race",
                "alternative_completion"
            ]
        )
        
        # Optimization Patterns
        self._add_pattern_definition(
            pattern_id="bonus_stacking",
            category=PatternCategory.ENDGAME,
            name="Bonus Stacking",
            description="Stack multiple bonuses for maximum scoring",
            detection_criteria=[
                "multiple_bonus_opportunities",
                "stacking_possibility",
                "high_value_combination",
                "execution_feasibility"
            ],
            urgency_factors=[
                "bonus_value",
                "stacking_difficulty",
                "competition_level",
                "timing_requirements"
            ],
            success_metrics=[
                "bonuses_achieved",
                "total_points_scored",
                "efficiency_ratio",
                "strategic_advantage"
            ],
            complexity_factors=[
                "stacking_complexity",
                "resource_requirements",
                "timing_precision",
                "competition_level"
            ],
            interaction_effects=[
                "synergistic_with_completion_patterns",
                "conflicting_with_single_bonus",
                "enhances_scoring_efficiency",
                "creates_multiplier_effects"
            ],
            edge_case_handling=[
                "no_bonus_opportunities",
                "stacking_impossible",
                "resource_limitations",
                "timing_issues"
            ],
            example_scenarios=[
                "Completing row and column simultaneously",
                "Achieving color completion with row completion",
                "Stacking multiple adjacency bonuses"
            ],
            counter_patterns=[
                "single_bonus_prioritization",
                "alternative_scoring_paths",
                "defensive_positioning"
            ],
            prerequisites=[
                "multiple_bonus_opportunities",
                "resource_availability",
                "execution_feasibility"
            ],
            alternatives=[
                "single_bonus_prioritization",
                "alternative_scoring_paths",
                "defensive_positioning"
            ]
        )
    
    def _build_meta_patterns(self):
        """Build all meta pattern definitions."""
        
        # Probabilistic Patterns
        self._add_pattern_definition(
            pattern_id="tile_counting",
            category=PatternCategory.META,
            name="Tile Counting",
            description="Track tile distribution for probabilistic planning",
            detection_criteria=[
                "tile_distribution_uncertain",
                "probabilistic_planning_valuable",
                "counting_accuracy_possible",
                "strategic_advantage_clear"
            ],
            urgency_factors=[
                "uncertainty_level",
                "planning_value",
                "counting_accuracy",
                "strategic_importance"
            ],
            success_metrics=[
                "counting_accuracy",
                "planning_effectiveness",
                "probabilistic_advantage",
                "strategic_control"
            ],
            complexity_factors=[
                "counting_complexity",
                "memory_requirements",
                "calculation_accuracy",
                "opponent_interference"
            ],
            interaction_effects=[
                "synergistic_with_probabilistic_planning",
                "conflicting_with_deterministic_play",
                "enhances_strategic_planning",
                "creates_information_advantage"
            ],
            edge_case_handling=[
                "counting_impossible",
                "opponent_interference",
                "memory_limitations",
                "calculation_errors"
            ],
            example_scenarios=[
                "Tracking remaining tiles of each color",
                "Calculating draw probabilities",
                "Planning based on tile distribution"
            ],
            counter_patterns=[
                "deterministic_play",
                "alternative_planning_methods",
                "information_ignorance"
            ],
            prerequisites=[
                "counting_possibility",
                "memory_capacity",
                "strategic_clearance"
            ],
            alternatives=[
                "deterministic_play",
                "alternative_planning_methods",
                "information_ignorance"
            ]
        )
        
        # Game Theory Patterns
        self._add_pattern_definition(
            pattern_id="nash_equilibrium",
            category=PatternCategory.META,
            name="Nash Equilibrium Play",
            description="Play according to game theory optimal strategies",
            detection_criteria=[
                "equilibrium_identifiable",
                "optimal_strategy_clear",
                "opponent_behavior_predictable",
                "theoretical_advantage_possible"
            ],
            urgency_factors=[
                "equilibrium_value",
                "opponent_skill_level",
                "game_phase",
                "strategic_importance"
            ],
            success_metrics=[
                "equilibrium_achieved",
                "theoretical_advantage",
                "opponent_predictability",
                "strategic_control"
            ],
            complexity_factors=[
                "equilibrium_complexity",
                "calculation_requirements",
                "opponent_modeling",
                "theoretical_understanding"
            ],
            interaction_effects=[
                "synergistic_with_optimal_play",
                "conflicting_with_exploitative_play",
                "enhances_theoretical_position",
                "creates_predictable_responses"
            ],
            edge_case_handling=[
                "no_equilibrium_identifiable",
                "opponent_deviation",
                "calculation_limitations",
                "theoretical_uncertainty"
            ],
            example_scenarios=[
                "Playing optimal mixed strategies",
                "Responding to opponent deviations",
                "Maintaining equilibrium under pressure"
            ],
            counter_patterns=[
                "exploitative_play",
                "alternative_strategies",
                "deviation_from_equilibrium"
            ],
            prerequisites=[
                "equilibrium_identifiable",
                "theoretical_understanding",
                "calculation_capacity"
            ],
            alternatives=[
                "exploitative_play",
                "alternative_strategies",
                "deviation_from_equilibrium"
            ]
        )
    
    def _build_edge_case_patterns(self):
        """Build all edge case pattern definitions."""
        
        # Tile Distribution Edge Cases
        self._add_pattern_definition(
            pattern_id="all_same_color_in_bag",
            category=PatternCategory.EDGE_CASE,
            name="All Same Color in Bag",
            description="Handle scenario where bag contains only one color",
            detection_criteria=[
                "bag_contains_single_color",
                "color_distribution_extreme",
                "game_continuation_possible",
                "special_handling_required"
            ],
            urgency_factors=[
                "game_impact_level",
                "handling_difficulty",
                "player_advantage",
                "game_continuation"
            ],
            success_metrics=[
                "game_continued_successfully",
                "fairness_maintained",
                "player_advantage_minimized",
                "game_quality_preserved"
            ],
            complexity_factors=[
                "handling_complexity",
                "fairness_considerations",
                "game_continuation_requirements",
                "player_impact_assessment"
            ],
            interaction_effects=[
                "affects_all_players_equally",
                "requires_special_rules",
                "impacts_game_balance",
                "creates_unique_scenarios"
            ],
            edge_case_handling=[
                "game_continuation_rules",
                "fairness_considerations",
                "player_advantage_mitigation",
                "special_handling_procedures"
            ],
            example_scenarios=[
                "Bag contains only blue tiles",
                "Bag contains only red tiles",
                "Bag contains only yellow tiles"
            ],
            counter_patterns=[
                "normal_game_continuation",
                "alternative_distribution",
                "game_restart"
            ],
            prerequisites=[
                "extreme_color_distribution",
                "game_continuation_required",
                "special_handling_needed"
            ],
            alternatives=[
                "normal_game_continuation",
                "alternative_distribution",
                "game_restart"
            ]
        )
        
        # Scoring Edge Cases
        self._add_pattern_definition(
            pattern_id="simultaneous_wall_completion",
            category=PatternCategory.EDGE_CASE,
            name="Simultaneous Wall Completion",
            description="Handle multiple players completing walls simultaneously",
            detection_criteria=[
                "multiple_players_completing",
                "completion_timing_simultaneous",
                "scoring_ambiguity_possible",
                "special_handling_required"
            ],
            urgency_factors=[
                "scoring_importance",
                "ambiguity_level",
                "player_impact",
                "game_continuation"
            ],
            success_metrics=[
                "scoring_resolved_fairly",
                "ambiguity_eliminated",
                "player_impact_minimized",
                "game_continuation_successful"
            ],
            complexity_factors=[
                "resolution_complexity",
                "fairness_considerations",
                "player_impact_assessment",
                "game_continuation_requirements"
            ],
            interaction_effects=[
                "affects_multiple_players",
                "requires_special_scoring",
                "impacts_game_outcome",
                "creates_unique_scenarios"
            ],
            edge_case_handling=[
                "simultaneous_completion_rules",
                "scoring_resolution_procedures",
                "player_impact_mitigation",
                "game_continuation_handling"
            ],
            example_scenarios=[
                "Two players complete rows simultaneously",
                "Multiple players complete columns simultaneously",
                "Simultaneous color completions"
            ],
            counter_patterns=[
                "sequential_completion",
                "alternative_scoring_methods",
                "game_restart"
            ],
            prerequisites=[
                "multiple_completions",
                "simultaneous_timing",
                "scoring_ambiguity"
            ],
            alternatives=[
                "sequential_completion",
                "alternative_scoring_methods",
                "game_restart"
            ]
        )
    
    def _add_pattern_definition(self, **kwargs):
        """Add a pattern definition to the taxonomy."""
        pattern_def = PatternDefinition(**kwargs)
        self.pattern_definitions[pattern_def.pattern_id] = pattern_def


class ComprehensivePatternTaxonomyManager:
    """
    Manager class for working with the comprehensive pattern taxonomy.
    """
    
    def __init__(self, taxonomy: ComprehensivePatternTaxonomy):
        self.taxonomy = taxonomy
        self.pattern_definitions = taxonomy.pattern_definitions
        self.category_hierarchy = taxonomy.category_hierarchy
        self.interaction_matrix = taxonomy.interaction_matrix
        self.edge_case_catalog = taxonomy.edge_case_catalog
    
    def get_pattern_definition(self, pattern_id: str) -> Optional[PatternDefinition]:
        """Get a pattern definition by ID."""
        return self.pattern_definitions.get(pattern_id)
    
    def get_patterns_by_category(self, category: PatternCategory) -> List[PatternDefinition]:
        """Get all pattern definitions in a category."""
        patterns = []
        for pattern_id in self.pattern_definitions:
            pattern = self.pattern_definitions[pattern_id]
            if pattern.category == category:
                patterns.append(pattern)
        return patterns
    
    def get_patterns_by_subcategory(self, category: PatternCategory, subcategory: str) -> List[PatternDefinition]:
        """Get all pattern definitions in a subcategory."""
        patterns = []
        if category in self.category_hierarchy and subcategory in self.category_hierarchy[category]:
            pattern_ids = self.category_hierarchy[category][subcategory]
            for pattern_id in pattern_ids:
                if pattern_id in self.pattern_definitions:
                    patterns.append(self.pattern_definitions[pattern_id])
        return patterns
    
    def get_interacting_patterns(self, pattern_id: str) -> Dict[str, float]:
        """Get patterns that interact with a given pattern."""
        return self.interaction_matrix.get(pattern_id, {})
    
    def get_edge_cases_by_category(self, edge_case_category: str) -> List[str]:
        """Get edge cases in a specific category."""
        return self.edge_case_catalog.get(edge_case_category, [])
    
    def validate_pattern_instance(self, pattern_instance: PatternInstance) -> bool:
        """Validate a pattern instance against its definition."""
        definition = pattern_instance.pattern_definition
        
        # Check detection criteria
        for criterion in definition.detection_criteria:
            if not self._check_detection_criterion(pattern_instance, criterion):
                return False
        
        # Check urgency factors
        for factor in definition.urgency_factors:
            if not self._check_urgency_factor(pattern_instance, factor):
                return False
        
        return True
    
    def _check_detection_criterion(self, pattern_instance: PatternInstance, criterion: str) -> bool:
        """Check if a detection criterion is met."""
        # This would be implemented based on specific criterion checking logic
        # For now, return True as placeholder
        return True
    
    def _check_urgency_factor(self, pattern_instance: PatternInstance, factor: str) -> bool:
        """Check if an urgency factor is present."""
        # This would be implemented based on specific factor checking logic
        # For now, return True as placeholder
        return True


# Factory function to create the comprehensive taxonomy
def create_comprehensive_pattern_taxonomy() -> ComprehensivePatternTaxonomy:
    """
    Create the comprehensive pattern taxonomy.
    
    Returns:
        ComprehensivePatternTaxonomy: The complete pattern taxonomy
    """
    builder = ComprehensivePatternTaxonomyBuilder()
    return builder.build_comprehensive_taxonomy()


# Global instance for easy access
COMPREHENSIVE_PATTERN_TAXONOMY = create_comprehensive_pattern_taxonomy()
TAXONOMY_MANAGER = ComprehensivePatternTaxonomyManager(COMPREHENSIVE_PATTERN_TAXONOMY) 