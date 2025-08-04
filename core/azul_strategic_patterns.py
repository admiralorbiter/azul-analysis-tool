"""
Azul Strategic Pattern Analysis - Phase 2.4 Implementation

This module provides strategic pattern recognition for Azul positions:
- Factory control analysis (domination, disruption, timing, color control)
- Endgame counting scenarios (conservation, optimization, blocking, timing)
- Risk/reward calculations (floor line risk, blocking risk, timing risk, scoring risk)
- Strategic decision analysis and move suggestions

Integrates with existing pattern detection system for comprehensive analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState


@dataclass
class StrategicPattern:
    """Base class for strategic patterns."""
    pattern_type: str
    strategic_value: float
    urgency_score: float
    confidence: float
    description: str


@dataclass
class StrategicPatternDetection:
    """Container for strategic pattern detection results."""
    factory_control_opportunities: List['FactoryControlOpportunity']
    endgame_scenarios: List['EndgameScenario']
    risk_reward_scenarios: List['RiskRewardScenario']
    total_patterns: int
    total_strategic_value: float
    confidence_score: float


class StrategicPatternDetector:
    """
    Main strategic pattern detection engine.
    
    Features:
    - Factory control analysis
    - Endgame counting scenarios
    - Risk/reward calculations
    - Strategic decision analysis
    """
    
    def __init__(self):
        # Import specialized detectors
        from .azul_factory_control import FactoryControlDetector
        from .azul_endgame_counting import EndgameCountingDetector
        from .azul_risk_reward import RiskRewardAnalyzer
        
        self.factory_control_detector = FactoryControlDetector()
        self.endgame_counting_detector = EndgameCountingDetector()
        self.risk_reward_analyzer = RiskRewardAnalyzer()
        
        # Strategic analysis thresholds
        self.high_strategic_value = 8.0
        self.medium_strategic_value = 5.0
        self.low_strategic_value = 2.0
        
        # Confidence thresholds
        self.high_confidence = 0.8
        self.medium_confidence = 0.6
        self.low_confidence = 0.4
    
    def detect_strategic_patterns(self, state: AzulState, player_id: int) -> StrategicPatternDetection:
        """
        Detect all strategic patterns in the current position.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            StrategicPatternDetection with all found patterns
        """
        # Factory control analysis
        factory_control_opportunities = self.factory_control_detector.detect_opportunities(state, player_id)
        
        # Endgame counting analysis
        endgame_scenarios = self.endgame_counting_detector.analyze_scenarios(state, player_id)
        
        # Risk/reward analysis
        risk_reward_scenarios = self.risk_reward_analyzer.analyze_scenarios(state, player_id)
        
        # Calculate totals
        total_patterns = (len(factory_control_opportunities) + 
                         len(endgame_scenarios) + 
                         len(risk_reward_scenarios))
        
        total_strategic_value = self._calculate_total_strategic_value(
            factory_control_opportunities, endgame_scenarios, risk_reward_scenarios
        )
        
        confidence_score = self._calculate_overall_confidence(
            factory_control_opportunities, endgame_scenarios, risk_reward_scenarios
        )
        
        return StrategicPatternDetection(
            factory_control_opportunities=factory_control_opportunities,
            endgame_scenarios=endgame_scenarios,
            risk_reward_scenarios=risk_reward_scenarios,
            total_patterns=total_patterns,
            total_strategic_value=total_strategic_value,
            confidence_score=confidence_score
        )
    
    def get_strategic_move_suggestions(self, state: AzulState, player_id: int) -> List[str]:
        """
        Get strategic move suggestions based on detected patterns.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            List of strategic move suggestions as strings
        """
        patterns = self.detect_strategic_patterns(state, player_id)
        suggestions = []
        suggestion_data = []  # For sorting
        
        # Factory control suggestions
        for opportunity in patterns.factory_control_opportunities:
            for suggestion in opportunity.move_suggestions:
                suggestions.append(suggestion)
                suggestion_data.append({
                    'suggestion': suggestion,
                    'strategic_value': opportunity.strategic_value,
                    'urgency_score': opportunity.urgency_score
                })
        
        # Endgame suggestions
        for scenario in patterns.endgame_scenarios:
            for suggestion in scenario.optimal_sequence:
                suggestions.append(suggestion)
                suggestion_data.append({
                    'suggestion': suggestion,
                    'strategic_value': scenario.scoring_potential,
                    'urgency_score': scenario.urgency_score if hasattr(scenario, 'urgency_score') else 0.0
                })
        
        # Risk/reward suggestions
        for scenario in patterns.risk_reward_scenarios:
            for suggestion in scenario.move_suggestions:
                suggestions.append(suggestion)
                suggestion_data.append({
                    'suggestion': suggestion,
                    'strategic_value': scenario.expected_value,
                    'urgency_score': scenario.urgency_score if hasattr(scenario, 'urgency_score') else 0.0
                })
        
        # Sort by strategic value and urgency using the data list
        suggestion_data.sort(key=lambda x: x.get('strategic_value', 0) + x.get('urgency_score', 0), reverse=True)
        
        # Return the sorted suggestions as strings
        return [item['suggestion'] for item in suggestion_data[:10]]
    
    def analyze_strategic_position(self, state: AzulState, player_id: int) -> Dict:
        """
        Comprehensive strategic position analysis.
        
        Args:
            state: Current game state
            player_id: Player to analyze for
            
        Returns:
            Dictionary with comprehensive strategic analysis
        """
        patterns = self.detect_strategic_patterns(state, player_id)
        
        # Analyze strategic themes
        strategic_themes = self._identify_strategic_themes(patterns)
        
        # Calculate position strength
        position_strength = self._calculate_position_strength(patterns)
        
        # Identify critical decisions
        critical_decisions = self._identify_critical_decisions(patterns)
        
        return {
            'patterns': patterns,
            'strategic_themes': strategic_themes,
            'position_strength': position_strength,
            'critical_decisions': critical_decisions,
            'move_suggestions': self.get_strategic_move_suggestions(state, player_id)
        }
    
    def _calculate_total_strategic_value(self, factory_control: List, 
                                       endgame_scenarios: List, 
                                       risk_reward_scenarios: List) -> float:
        """Calculate total strategic value across all pattern types."""
        total_value = 0.0
        
        for opportunity in factory_control:
            total_value += opportunity.strategic_value
        
        for scenario in endgame_scenarios:
            total_value += scenario.scoring_potential
        
        for scenario in risk_reward_scenarios:
            total_value += scenario.expected_value
        
        return total_value
    
    def _calculate_overall_confidence(self, factory_control: List, 
                                    endgame_scenarios: List, 
                                    risk_reward_scenarios: List) -> float:
        """Calculate overall confidence score for strategic analysis."""
        all_patterns = factory_control + endgame_scenarios + risk_reward_scenarios
        
        if not all_patterns:
            return 0.0
        
        total_confidence = sum(pattern.confidence for pattern in all_patterns)
        return total_confidence / len(all_patterns)
    
    def _identify_strategic_themes(self, patterns: StrategicPatternDetection) -> List[str]:
        """Identify dominant strategic themes in the position."""
        themes = []
        
        # Factory control themes
        if patterns.factory_control_opportunities:
            control_types = [opp.control_type for opp in patterns.factory_control_opportunities]
            if 'domination' in control_types:
                themes.append("Factory Domination")
            if 'disruption' in control_types:
                themes.append("Opponent Disruption")
            if 'timing' in control_types:
                themes.append("Timing Control")
            if 'color_control' in control_types:
                themes.append("Color Control")
        
        # Endgame themes
        if patterns.endgame_scenarios:
            scenario_types = [scenario.scenario_type for scenario in patterns.endgame_scenarios]
            if 'conservation' in scenario_types:
                themes.append("Tile Conservation")
            if 'optimization' in scenario_types:
                themes.append("Endgame Optimization")
            if 'blocking' in scenario_types:
                themes.append("Endgame Blocking")
        
        # Risk/reward themes
        if patterns.risk_reward_scenarios:
            risk_types = [scenario.scenario_type for scenario in patterns.risk_reward_scenarios]
            if 'floor_risk' in risk_types:
                themes.append("Floor Line Risk Management")
            if 'blocking_risk' in risk_types:
                themes.append("Blocking Risk Assessment")
            if 'timing_risk' in risk_types:
                themes.append("Timing Risk Analysis")
            if 'scoring_risk' in risk_types:
                themes.append("Scoring Risk Evaluation")
        
        return themes
    
    def _calculate_position_strength(self, patterns: StrategicPatternDetection) -> Dict:
        """Calculate overall position strength metrics."""
        strength_metrics = {
            'factory_control_strength': 0.0,
            'endgame_strength': 0.0,
            'risk_management_strength': 0.0,
            'overall_strength': 0.0
        }
        
        # Factory control strength
        if patterns.factory_control_opportunities:
            avg_control_value = sum(opp.strategic_value for opp in patterns.factory_control_opportunities) / len(patterns.factory_control_opportunities)
            strength_metrics['factory_control_strength'] = min(avg_control_value / 10.0, 1.0)
        
        # Endgame strength
        if patterns.endgame_scenarios:
            avg_endgame_value = sum(scenario.scoring_potential for scenario in patterns.endgame_scenarios) / len(patterns.endgame_scenarios)
            strength_metrics['endgame_strength'] = min(avg_endgame_value / 15.0, 1.0)
        
        # Risk management strength
        if patterns.risk_reward_scenarios:
            avg_risk_value = sum(scenario.expected_value for scenario in patterns.risk_reward_scenarios) / len(patterns.risk_reward_scenarios)
            strength_metrics['risk_management_strength'] = min(avg_risk_value / 10.0, 1.0)
        
        # Overall strength (weighted average)
        weights = [0.4, 0.3, 0.3]  # Factory control, endgame, risk management
        values = [strength_metrics['factory_control_strength'], 
                 strength_metrics['endgame_strength'], 
                 strength_metrics['risk_management_strength']]
        
        strength_metrics['overall_strength'] = sum(w * v for w, v in zip(weights, values))
        
        return strength_metrics
    
    def _identify_critical_decisions(self, patterns: StrategicPatternDetection) -> List[Dict]:
        """Identify critical strategic decisions that need immediate attention."""
        critical_decisions = []
        
        # High urgency factory control opportunities
        for opp in patterns.factory_control_opportunities:
            if opp.urgency_level in ['CRITICAL', 'HIGH']:
                critical_decisions.append({
                    'type': 'factory_control',
                    'urgency': opp.urgency_level,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value,
                    'move_suggestions': opp.move_suggestions
                })
        
        # High urgency endgame scenarios
        for scenario in patterns.endgame_scenarios:
            if scenario.urgency_score >= 7.0:
                critical_decisions.append({
                    'type': 'endgame_scenario',
                    'urgency': 'HIGH' if scenario.urgency_score >= 8.0 else 'MEDIUM',
                    'description': scenario.description,
                    'scoring_potential': scenario.scoring_potential,
                    'optimal_sequence': scenario.optimal_sequence
                })
        
        # High risk scenarios
        for scenario in patterns.risk_reward_scenarios:
            if scenario.risk_level == 'high':
                critical_decisions.append({
                    'type': 'risk_management',
                    'urgency': 'HIGH',
                    'description': scenario.description,
                    'risk_level': scenario.risk_level,
                    'expected_value': scenario.expected_value
                })
        
        # Sort by urgency and strategic value
        critical_decisions.sort(key=lambda x: (
            {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1}.get(x['urgency'], 0),
            x.get('strategic_value', 0) + x.get('scoring_potential', 0) + x.get('expected_value', 0)
        ), reverse=True)
        
        return critical_decisions[:5]  # Return top 5 critical decisions


# Import the specialized dataclasses for type hints
from .azul_factory_control import FactoryControlOpportunity
from .azul_endgame_counting import EndgameScenario
from .azul_risk_reward import RiskRewardScenario 