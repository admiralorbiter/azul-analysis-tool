#!/usr/bin/env python3
"""
Pattern-Based Move Quality Analysis

This script analyzes move quality based on pattern detection and strategic factors.
Uses your existing pattern detection systems to identify high-quality moves.
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from core.azul_model import AzulState
from core.azul_patterns import AzulPatternDetector
from core.azul_scoring_optimization import AzulScoringOptimization
from core.azul_floor_line_patterns import AzulFloorLinePatterns

@dataclass
class PatternQualityAnalysis:
    """Results from pattern-based quality analysis."""
    position_fen: str
    move_data: Dict[str, Any]
    blocking_score: float
    scoring_score: float
    floor_line_score: float
    strategic_score: float
    overall_quality: float
    quality_tier: str
    pattern_factors: List[str]
    strategic_reasoning: str

class PatternBasedQualityAnalyzer:
    """Analyzes move quality based on pattern detection."""
    
    def __init__(self):
        self.pattern_detector = AzulPatternDetector()
        self.scoring_optimizer = AzulScoringOptimization()
        self.floor_line_analyzer = AzulFloorLinePatterns()
    
    def analyze_move_quality(self, state: AzulState, move: Any, agent_id: int = 0) -> PatternQualityAnalysis:
        """Analyze move quality based on patterns and strategic factors."""
        
        # Analyze blocking opportunities
        blocking_score = self._analyze_blocking_quality(state, move, agent_id)
        
        # Analyze scoring opportunities
        scoring_score = self._analyze_scoring_quality(state, move, agent_id)
        
        # Analyze floor line management
        floor_line_score = self._analyze_floor_line_quality(state, move, agent_id)
        
        # Analyze strategic factors
        strategic_score = self._analyze_strategic_quality(state, move, agent_id)
        
        # Calculate overall quality
        overall_quality = self._calculate_overall_quality(
            blocking_score, scoring_score, floor_line_score, strategic_score
        )
        
        # Determine quality tier
        quality_tier = self._determine_quality_tier(overall_quality)
        
        # Identify pattern factors
        pattern_factors = self._identify_pattern_factors(
            state, move, agent_id, blocking_score, scoring_score, floor_line_score
        )
        
        # Generate strategic reasoning
        strategic_reasoning = self._generate_strategic_reasoning(
            blocking_score, scoring_score, floor_line_score, strategic_score
        )
        
        return PatternQualityAnalysis(
            position_fen=state.to_fen_string(),
            move_data=move.__dict__ if move else {},
            blocking_score=blocking_score,
            scoring_score=scoring_score,
            floor_line_score=floor_line_score,
            strategic_score=strategic_score,
            overall_quality=overall_quality,
            quality_tier=quality_tier,
            pattern_factors=pattern_factors,
            strategic_reasoning=strategic_reasoning
        )
    
    def _analyze_blocking_quality(self, state: AzulState, move: Any, agent_id: int) -> float:
        """Analyze blocking quality of the move."""
        try:
            # Get pattern detection results
            patterns = self.pattern_detector.detect_patterns(state, agent_id)
            
            if not patterns or 'opportunities' not in patterns:
                return 0.0
            
            # Check if move blocks opponent opportunities
            blocking_opportunities = [
                opp for opp in patterns['opportunities'] 
                if opp.get('opportunity_type') == 'blocking_move'
            ]
            
            if not blocking_opportunities:
                return 0.0
            
            # Calculate blocking score based on urgency and strategic value
            total_blocking_score = 0.0
            for opp in blocking_opportunities:
                urgency = opp.get('urgency_score', 0.0)
                strategic_value = opp.get('strategic_value', 0.0)
                total_blocking_score += urgency * strategic_value
            
            return min(total_blocking_score / len(blocking_opportunities), 10.0)
            
        except Exception as e:
            print(f"Blocking analysis failed: {e}")
            return 0.0
    
    def _analyze_scoring_quality(self, state: AzulState, move: Any, agent_id: int) -> float:
        """Analyze scoring quality of the move."""
        try:
            # Get scoring optimization results
            scoring_results = self.scoring_optimizer.detect_scoring_optimization(state, agent_id)
            
            if not scoring_results or 'opportunities' not in scoring_results:
                return 0.0
            
            # Check if move creates scoring opportunities
            scoring_opportunities = [
                opp for opp in scoring_results['opportunities']
                if opp.get('opportunity_type') in ['wall_completion', 'pattern_line_optimization']
            ]
            
            if not scoring_opportunities:
                return 0.0
            
            # Calculate scoring score based on urgency and strategic value
            total_scoring_score = 0.0
            for opp in scoring_opportunities:
                urgency = opp.get('urgency_score', 0.0)
                strategic_value = opp.get('strategic_value', 0.0)
                total_scoring_score += urgency * strategic_value
            
            return min(total_scoring_score / len(scoring_opportunities), 10.0)
            
        except Exception as e:
            print(f"Scoring analysis failed: {e}")
            return 0.0
    
    def _analyze_floor_line_quality(self, state: AzulState, move: Any, agent_id: int) -> float:
        """Analyze floor line management quality of the move."""
        try:
            # Get floor line pattern results
            floor_results = self.floor_line_analyzer.detect_floor_line_patterns(state, agent_id)
            
            if not floor_results or 'opportunities' not in floor_results:
                return 0.0
            
            # Check if move manages floor line well
            floor_opportunities = [
                opp for opp in floor_results['opportunities']
                if opp.get('opportunity_type') in ['risk_mitigation', 'efficiency_optimization']
            ]
            
            if not floor_opportunities:
                return 0.0
            
            # Calculate floor line score (negative for penalties, positive for good management)
            total_floor_score = 0.0
            for opp in floor_opportunities:
                urgency = opp.get('urgency_score', 0.0)
                strategic_value = opp.get('strategic_value', 0.0)
                total_floor_score += urgency * strategic_value
            
            return min(total_floor_score / len(floor_opportunities), 10.0)
            
        except Exception as e:
            print(f"Floor line analysis failed: {e}")
            return 0.0
    
    def _analyze_strategic_quality(self, state: AzulState, move: Any, agent_id: int) -> float:
        """Analyze strategic quality of the move."""
        # This would include factors like:
        # - Game phase awareness
        # - Position control
        # - Long-term planning
        # - Risk management
        
        # Simplified implementation
        strategic_score = 0.0
        
        # Check game phase
        game_phase = self._determine_game_phase(state)
        if game_phase == 'opening':
            strategic_score += 2.0  # Opening moves are generally good
        elif game_phase == 'endgame':
            strategic_score += 3.0  # Endgame moves are critical
        
        # Check if move avoids floor line penalties
        if hasattr(move, 'num_to_floor_line') and move.num_to_floor_line == 0:
            strategic_score += 2.0
        
        # Check if move advances wall completion
        if hasattr(move, 'pattern_line_dest') and move.pattern_line_dest >= 0:
            strategic_score += 1.0
        
        return min(strategic_score, 10.0)
    
    def _determine_game_phase(self, state: AzulState) -> str:
        """Determine the current game phase."""
        # Count completed pattern lines
        total_completed = 0
        for agent in state.agents:
            for pattern_line in agent.pattern_lines:
                if len(pattern_line) == pattern_line.capacity:
                    total_completed += 1
        
        if total_completed < 3:
            return 'opening'
        elif total_completed < 8:
            return 'middlegame'
        else:
            return 'endgame'
    
    def _calculate_overall_quality(self, blocking: float, scoring: float, 
                                 floor_line: float, strategic: float) -> float:
        """Calculate overall quality score."""
        # Weighted combination of all factors
        weights = {
            'blocking': 0.25,
            'scoring': 0.30,
            'floor_line': 0.20,
            'strategic': 0.25
        }
        
        overall = (
            blocking * weights['blocking'] +
            scoring * weights['scoring'] +
            floor_line * weights['floor_line'] +
            strategic * weights['strategic']
        )
        
        return min(max(overall, -10.0), 10.0)  # Clamp to -10 to 10
    
    def _determine_quality_tier(self, overall_quality: float) -> str:
        """Determine quality tier based on overall score."""
        if overall_quality >= 7.0:
            return "!!"  # Brilliant
        elif overall_quality >= 4.0:
            return "!"   # Excellent
        elif overall_quality >= 1.0:
            return "="   # Good
        elif overall_quality >= -2.0:
            return "?!"  # Dubious
        else:
            return "?"   # Poor
    
    def _identify_pattern_factors(self, state: AzulState, move: Any, agent_id: int,
                                blocking_score: float, scoring_score: float, 
                                floor_line_score: float) -> List[str]:
        """Identify pattern factors that contribute to move quality."""
        factors = []
        
        if blocking_score > 3.0:
            factors.append("Strong blocking opportunity")
        elif blocking_score > 1.0:
            factors.append("Moderate blocking opportunity")
        
        if scoring_score > 3.0:
            factors.append("High scoring potential")
        elif scoring_score > 1.0:
            factors.append("Moderate scoring potential")
        
        if floor_line_score > 2.0:
            factors.append("Good floor line management")
        elif floor_line_score < -2.0:
            factors.append("Floor line penalty risk")
        
        if not factors:
            factors.append("Standard tactical move")
        
        return factors
    
    def _generate_strategic_reasoning(self, blocking_score: float, scoring_score: float,
                                    floor_line_score: float, strategic_score: float) -> str:
        """Generate strategic reasoning for the move."""
        reasoning_parts = []
        
        if blocking_score > 2.0:
            reasoning_parts.append("Blocks opponent opportunities")
        
        if scoring_score > 2.0:
            reasoning_parts.append("Creates scoring opportunities")
        
        if floor_line_score > 1.0:
            reasoning_parts.append("Manages floor line well")
        elif floor_line_score < -1.0:
            reasoning_parts.append("Risky floor line management")
        
        if strategic_score > 3.0:
            reasoning_parts.append("Strong strategic play")
        
        if not reasoning_parts:
            reasoning_parts.append("Standard tactical move")
        
        return "; ".join(reasoning_parts)

def main():
    """Example usage of pattern-based quality analysis."""
    analyzer = PatternBasedQualityAnalyzer()
    
    # Create a test position and move
    from core.azul_model import AzulState
    from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
    
    state = AzulState()
    generator = FastMoveGenerator()
    moves = generator.generate_moves_fast(state, 0)
    
    if moves:
        move = moves[0]  # Analyze first move
        analysis = analyzer.analyze_move_quality(state, move, 0)
        
        print("Pattern-Based Quality Analysis Results:")
        print(f"Overall Quality: {analysis.overall_quality:.2f}")
        print(f"Quality Tier: {analysis.quality_tier}")
        print(f"Blocking Score: {analysis.blocking_score:.2f}")
        print(f"Scoring Score: {analysis.scoring_score:.2f}")
        print(f"Floor Line Score: {analysis.floor_line_score:.2f}")
        print(f"Strategic Score: {analysis.strategic_score:.2f}")
        print(f"Pattern Factors: {analysis.pattern_factors}")
        print(f"Strategic Reasoning: {analysis.strategic_reasoning}")

if __name__ == "__main__":
    main()
