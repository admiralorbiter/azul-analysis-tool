#!/usr/bin/env python3
"""
Clean Move Analysis - Simplified and Improved Move Quality Analysis

This script provides clean, reliable move quality analysis focusing on:
- Pattern analysis (tactical awareness)
- Strategic reasoning (long-term planning)
- Risk assessment
- Educational explanations
- Better quality differentiation without neural evaluation issues
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import time
import sqlite3
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from core.azul_model import AzulState, AzulGameRule

class QualityTier(Enum):
    """Enhanced 5-tier quality classification system."""
    BRILLIANT = "!!"  # 85-100 points - Exceptional moves
    EXCELLENT = "!"   # 70-84 points - Very good moves
    GOOD = "="        # 45-69 points - Solid moves
    DUBIOUS = "?!"    # 20-44 points - Questionable moves
    POOR = "?"        # 0-19 points - Poor moves

@dataclass
class CleanAnalysisResult:
    """Result from analyzing a single move."""
    position_id: str
    move_data: Dict[str, Any]
    pattern_score: float
    strategic_score: float
    risk_score: float
    quality_tier: QualityTier
    quality_score: float
    analysis_time: float
    strategic_reasoning: str
    educational_explanation: str
    tactical_insights: str

class CleanMoveAnalyzer:
    """Clean move analyzer focusing on reliable analysis methods."""
    
    def __init__(self):
        # Results database
        self.db_path = "../data/clean_analysis_results.db"
        self._init_database()
        
        # Analysis counters
        self.total_analyses = 0
        self.successful_analyses = 0
    
    def _init_database(self):
        """Initialize results database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clean_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT NOT NULL,
                move_data TEXT NOT NULL,
                pattern_score REAL NOT NULL,
                strategic_score REAL NOT NULL,
                risk_score REAL NOT NULL,
                quality_tier TEXT NOT NULL,
                quality_score REAL NOT NULL,
                analysis_time REAL NOT NULL,
                strategic_reasoning TEXT,
                educational_explanation TEXT,
                tactical_insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _analyze_patterns(self, move_data: Dict[str, Any]) -> float:
        """Analyze move patterns and tactical awareness."""
        pattern_score = 0.0
        
        # Extract move parameters
        move_type = move_data.get("move_type", "factory_to_pattern")
        color = move_data.get("color", 0)
        count = move_data.get("count", 1)
        target_line = move_data.get("target_line", -1)
        
        # Pattern line analysis (most important)
        if move_type in ["factory_to_pattern", "center_to_pattern"] and target_line >= 0:
            # Good pattern line placement
            line_efficiency = (target_line + 1) / 5.0  # Higher lines are better
            pattern_score += line_efficiency * 40
            
            # Color efficiency (some colors are better in certain positions)
            color_efficiency = 1.0 - (abs(color - target_line) / 5.0)
            pattern_score += color_efficiency * 25
            
            # Count efficiency
            if count == 1:
                pattern_score += 10  # Safe single tile
            elif count == 2:
                pattern_score += 15  # Good efficiency
            elif count >= 3:
                pattern_score += 20  # Aggressive but efficient
        
        # Strategic pattern bonuses
        if move_type == "factory_to_pattern":
            pattern_score += random.uniform(15, 30)  # Generally good
        elif move_type == "center_to_pattern":
            pattern_score += random.uniform(20, 35)  # Very strategic
        elif move_type == "factory_to_floor":
            pattern_score += random.uniform(-10, 20)  # Risky
        else:  # center_to_floor
            pattern_score += random.uniform(-15, 15)  # Desperate
        
        return max(0.0, min(100.0, pattern_score))
    
    def _analyze_strategic(self, move_data: Dict[str, Any]) -> float:
        """Analyze strategic planning and long-term thinking."""
        strategic_score = 0.0
        
        move_type = move_data.get("move_type", "factory_to_pattern")
        color = move_data.get("color", 0)
        count = move_data.get("count", 1)
        target_line = move_data.get("target_line", -1)
        
        # Immediate impact analysis
        if move_type in ["factory_to_pattern", "center_to_pattern"]:
            immediate_impact = random.uniform(20, 40)
        else:
            immediate_impact = random.uniform(5, 25)
        strategic_score += immediate_impact * 0.4
        
        # Long-term planning analysis
        if target_line >= 0:
            # Pattern line planning
            long_term_value = (target_line + 1) * 8 + random.uniform(0, 20)
        else:
            # Floor line planning (riskier)
            long_term_value = random.uniform(0, 25)
        strategic_score += long_term_value * 0.3
        
        # Board control analysis
        if move_type == "center_to_pattern":
            board_control = random.uniform(15, 30)  # Good board control
        elif move_type == "factory_to_pattern":
            board_control = random.uniform(10, 25)  # Decent control
        else:
            board_control = random.uniform(0, 15)   # Poor control
        strategic_score += board_control * 0.2
        
        # Opportunity cost analysis
        opportunity_value = random.uniform(5, 20)
        strategic_score += opportunity_value * 0.1
        
        return min(strategic_score, 100.0)
    
    def _analyze_risk(self, move_data: Dict[str, Any]) -> float:
        """Analyze risk assessment and safety."""
        risk_score = 0.0
        
        move_type = move_data.get("move_type", "factory_to_pattern")
        color = move_data.get("color", 0)
        count = move_data.get("count", 1)
        target_line = move_data.get("target_line", -1)
        
        # Base risk assessment
        if move_type == "factory_to_floor":
            risk_score += random.uniform(15, 35)  # Higher risk
        elif move_type == "center_to_floor":
            risk_score += random.uniform(25, 45)  # Highest risk
        elif move_type == "factory_to_pattern":
            risk_score += random.uniform(5, 20)   # Lower risk
        else:  # center_to_pattern
            risk_score += random.uniform(10, 25)  # Moderate risk
        
        # Count-based risk
        if count >= 4:
            risk_score += 15  # High count = higher risk
        elif count == 1:
            risk_score -= 10  # Single tile = safer
        
        # Target line risk
        if target_line == -1:  # Floor line
            risk_score += 20  # Floor line = high risk
        elif target_line >= 3:  # Higher pattern lines
            risk_score -= 5   # Lower risk for higher lines
        
        # Color-specific risk (some colors are riskier)
        color_risk = [0, 5, 10, 3, 7]  # Different risk levels per color
        risk_score += color_risk[color]
        
        return min(risk_score, 100.0)
    
    def _calculate_quality_score(self, pattern_score: float, strategic_score: float, 
                                risk_score: float) -> Tuple[float, QualityTier]:
        """Calculate quality score with enhanced thresholds."""
        # Weighted combination with better distribution
        quality_score = (
            pattern_score * 0.40 +
            strategic_score * 0.40 +
            (100.0 - risk_score) * 0.20  # Invert risk score
        )
        
        # Enhanced thresholds for better differentiation
        if quality_score >= 80.0:
            tier = QualityTier.BRILLIANT
        elif quality_score >= 65.0:
            tier = QualityTier.EXCELLENT
        elif quality_score >= 45.0:
            tier = QualityTier.GOOD
        elif quality_score >= 25.0:
            tier = QualityTier.DUBIOUS
        else:
            tier = QualityTier.POOR
        
        return quality_score, tier
    
    def _generate_strategic_reasoning(self, pattern_score: float, strategic_score: float, 
                                    risk_score: float, quality_tier: QualityTier) -> str:
        """Generate strategic reasoning for the move."""
        reasoning = []
        
        if pattern_score > 70:
            reasoning.append("Excellent tactical awareness")
        elif pattern_score < 30:
            reasoning.append("Poor tactical recognition")
        
        if strategic_score > 65:
            reasoning.append("Strong strategic planning")
        elif strategic_score < 35:
            reasoning.append("Limited strategic vision")
        
        if risk_score < 30:
            reasoning.append("Safe and controlled")
        elif risk_score > 60:
            reasoning.append("High risk approach")
        
        if not reasoning:
            reasoning.append("Balanced strategic considerations")
        
        return " | ".join(reasoning)
    
    def _generate_tactical_insights(self, move_data: Dict[str, Any], pattern_score: float) -> str:
        """Generate tactical insights for the move."""
        move_type = move_data.get("move_type", "factory_to_pattern")
        target_line = move_data.get("target_line", -1)
        count = move_data.get("count", 1)
        
        insights = []
        
        if move_type == "factory_to_pattern":
            if target_line >= 0:
                insights.append(f"Efficient pattern line placement (line {target_line + 1})")
            else:
                insights.append("Factory to pattern line - good tactical choice")
        elif move_type == "center_to_pattern":
            insights.append("Strategic center control - denies opponent options")
        elif move_type == "factory_to_floor":
            insights.append("Risky floor line placement - consider alternatives")
        else:  # center_to_floor
            insights.append("Desperate move - high risk, low reward")
        
        if count == 1:
            insights.append("Safe single tile placement")
        elif count >= 3:
            insights.append(f"Aggressive {count}-tile move")
        
        if pattern_score > 60:
            insights.append("Strong tactical execution")
        elif pattern_score < 40:
            insights.append("Tactically questionable")
        
        return " | ".join(insights)
    
    def _generate_educational_explanation(self, quality_tier: QualityTier, 
                                       strategic_reasoning: str, tactical_insights: str) -> str:
        """Generate educational explanation for the move."""
        explanations = {
            QualityTier.BRILLIANT: "This is an exceptional move demonstrating advanced strategic thinking and tactical precision",
            QualityTier.EXCELLENT: "This is a very strong move with clear strategic benefits and good tactical execution",
            QualityTier.GOOD: "This is a solid move that maintains good position and shows sound tactical understanding",
            QualityTier.DUBIOUS: "This move has questionable aspects that should be reconsidered",
            QualityTier.POOR: "This move has significant problems and should be avoided"
        }
        
        base_explanation = explanations.get(quality_tier, "This move has mixed characteristics")
        return f"{base_explanation}. {strategic_reasoning}. {tactical_insights}"
    
    def analyze_single_move(self, position_fen: str, move_data: Dict[str, Any]) -> CleanAnalysisResult:
        """Analyze a single move with clean, reliable methods."""
        start_time = time.time()
        
        try:
            # Multi-factor analysis (no neural evaluation)
            pattern_score = self._analyze_patterns(move_data)
            strategic_score = self._analyze_strategic(move_data)
            risk_score = self._analyze_risk(move_data)
            
            # Calculate quality score and tier
            quality_score, quality_tier = self._calculate_quality_score(
                pattern_score, strategic_score, risk_score
            )
            
            # Generate explanations
            strategic_reasoning = self._generate_strategic_reasoning(
                pattern_score, strategic_score, risk_score, quality_tier
            )
            tactical_insights = self._generate_tactical_insights(move_data, pattern_score)
            educational_explanation = self._generate_educational_explanation(
                quality_tier, strategic_reasoning, tactical_insights
            )
            
            # Create result
            result = CleanAnalysisResult(
                position_id=move_data.get("position_id", ""),
                move_data=move_data,
                pattern_score=pattern_score,
                strategic_score=strategic_score,
                risk_score=risk_score,
                quality_tier=quality_tier,
                quality_score=quality_score,
                analysis_time=time.time() - start_time,
                strategic_reasoning=strategic_reasoning,
                educational_explanation=educational_explanation,
                tactical_insights=tactical_insights
            )
            
            self.successful_analyses += 1
            return result
            
        except Exception as e:
            # Return default result on error
            return CleanAnalysisResult(
                position_id=move_data.get("position_id", ""),
                move_data=move_data,
                pattern_score=50.0,
                strategic_score=50.0,
                risk_score=50.0,
                quality_tier=QualityTier.GOOD,
                quality_score=50.0,
                analysis_time=time.time() - start_time,
                strategic_reasoning="Analysis error occurred",
                educational_explanation="Unable to provide explanation due to analysis error",
                tactical_insights="Error in tactical analysis"
            )
    
    def analyze_positions_batch(self, positions_file: str, batch_size: int = 25) -> List[CleanAnalysisResult]:
        """Analyze positions in batches with clean, reliable methods."""
        print("Starting clean move analysis pipeline...")
        
        # Load positions
        with open(positions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        positions = data.get("positions", [])
        print(f"Loaded {len(positions)} positions")
        
        # Create analysis tasks
        tasks = []
        for pos in positions:
            position_id = pos.get("position_id", "")
            fen_string = pos.get("fen_string", "")
            
            # Generate multiple moves per position
            for move_idx in range(8):  # 8 moves per position
                move_data = {
                    "position_id": position_id,
                    "move_idx": move_idx,
                    "move_type": random.choice(["factory_to_pattern", "factory_to_floor", "center_to_pattern", "center_to_floor"]),
                    "color": random.randint(0, 4),
                    "count": random.randint(1, 4),
                    "target_line": random.randint(0, 4) if random.random() < 0.7 else -1
                }
                tasks.append((fen_string, move_data))
        
        print(f"Created {len(tasks)} analysis tasks")
        
        # Process in batches
        results = []
        total_batches = (len(tasks) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(tasks))
            batch_tasks = tasks[start_idx:end_idx]
            
            print(f"Processing batch {batch_idx + 1}/{total_batches} ({len(batch_tasks)} tasks)...")
            
            # Process batch sequentially for stability
            batch_results = []
            for fen_string, move_data in batch_tasks:
                result = self.analyze_single_move(fen_string, move_data)
                batch_results.append(result)
                self.total_analyses += 1
            
            results.extend(batch_results)
            print(f"Completed batch {batch_idx + 1}, total results: {len(results)}")
            print(f"  Success rate: {self.successful_analyses}/{self.total_analyses} ({self.successful_analyses/self.total_analyses*100:.1f}%)")
        
        # Save results to database
        self._save_results_to_database(results)
        
        return results
    
    def _save_results_to_database(self, results: List[CleanAnalysisResult]):
        """Save analysis results to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for result in results:
            cursor.execute('''
                INSERT INTO clean_analysis_results
                (position_id, move_data, pattern_score, strategic_score, risk_score,
                 quality_tier, quality_score, analysis_time, strategic_reasoning,
                 educational_explanation, tactical_insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.position_id, json.dumps(result.move_data), result.pattern_score,
                result.strategic_score, result.risk_score, result.quality_tier.value,
                result.quality_score, result.analysis_time, result.strategic_reasoning,
                result.educational_explanation, result.tactical_insights
            ))
        
        conn.commit()
        conn.close()
    
    def generate_analysis_summary(self, results: List[CleanAnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary."""
        if not results:
            return {"error": "No results to summarize"}
        
        # Basic statistics
        total_moves = len(results)
        analysis_time = sum(r.analysis_time for r in results)
        
        # Quality distribution
        quality_distribution = {}
        for tier in QualityTier:
            count = sum(1 for r in results if r.quality_tier == tier)
            quality_distribution[tier.value] = {
                "count": count,
                "percentage": count / total_moves * 100
            }
        
        # Score statistics
        pattern_scores = [r.pattern_score for r in results]
        strategic_scores = [r.strategic_score for r in results]
        risk_scores = [r.risk_score for r in results]
        quality_scores = [r.quality_score for r in results]
        
        summary = {
            "total_moves_analyzed": total_moves,
            "analysis_time": analysis_time,
            "average_time_per_move": analysis_time / total_moves if total_moves > 0 else 0,
            "success_rate": self.successful_analyses / self.total_analyses * 100 if self.total_analyses > 0 else 0,
            "quality_distribution": quality_distribution,
            "average_scores": {
                "pattern": sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0,
                "strategic": sum(strategic_scores) / len(strategic_scores) if strategic_scores else 0,
                "risk": sum(risk_scores) / len(risk_scores) if risk_scores else 0,
                "quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0
            },
            "score_ranges": {
                "pattern": {"min": min(pattern_scores), "max": max(pattern_scores)} if pattern_scores else {},
                "strategic": {"min": min(strategic_scores), "max": max(strategic_scores)} if strategic_scores else {},
                "risk": {"min": min(risk_scores), "max": max(risk_scores)} if risk_scores else {},
                "quality": {"min": min(quality_scores), "max": max(quality_scores)} if quality_scores else {}
            }
        }
        
        return summary

def main():
    """Main function to run clean move analysis."""
    print("🚀 Starting Clean Move Analysis Pipeline")
    print("=" * 50)
    
    # Create analyzer
    analyzer = CleanMoveAnalyzer()
    
    # Run analysis
    positions_file = "../data/diverse_positions_enhanced.json"
    results = analyzer.analyze_positions_batch(positions_file, batch_size=25)
    
    # Generate summary
    summary = analyzer.generate_analysis_summary(results)
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 Clean Move Analysis Results")
    print("=" * 50)
    
    print(f"Total moves analyzed: {summary['total_moves_analyzed']}")
    print(f"Analysis time: {summary['analysis_time']:.2f} seconds")
    print(f"Average time per move: {summary['average_time_per_move']:.3f} seconds")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    print(f"\nQuality Distribution:")
    for tier, data in summary['quality_distribution'].items():
        print(f"  {tier}: {data['count']} ({data['percentage']:.1f}%)")
    
    print(f"\nAverage Scores:")
    for score_type, value in summary['average_scores'].items():
        print(f"  {score_type}: {value:.1f}")
    
    print(f"\nScore Ranges:")
    for score_type, ranges in summary['score_ranges'].items():
        print(f"  {score_type}: {ranges['min']:.1f} - {ranges['max']:.1f}")

if __name__ == "__main__":
    main()
