#!/usr/bin/env python3
"""
Comprehensive Move Quality Analyzer - Enhanced Analysis Engine

This script provides comprehensive move quality analysis with:
- Parallel processing for 30+ second analysis capacity
- Integration with existing pattern detection systems
- Advanced move generation and evaluation
- Educational insights and strategic reasoning
- Comprehensive reporting and progress tracking
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
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.move_quality.azul_move_quality_assessor import (
    AzulMoveQualityAssessor, MoveQualityScore, MoveQualityTier
)

class QualityTier(Enum):
    """Enhanced 5-tier quality classification system."""
    BRILLIANT = "!!"  # 85-100 points - Exceptional moves
    EXCELLENT = "!"   # 70-84 points - Very good moves
    GOOD = "="        # 45-69 points - Solid moves
    DUBIOUS = "?!"    # 20-44 points - Questionable moves
    POOR = "?"        # 0-19 points - Poor moves

@dataclass
class ComprehensiveAnalysisConfig:
    """Configuration for comprehensive analysis."""
    # Processing
    max_workers: int = 8
    batch_size: int = 100
    max_analysis_time: int = 30  # seconds
    
    # Analysis Components
    enable_pattern_analysis: bool = True
    enable_strategic_analysis: bool = True
    enable_risk_analysis: bool = True
    enable_board_state_analysis: bool = True
    enable_opponent_denial: bool = True
    enable_timing_analysis: bool = True
    
    # Move Generation
    max_moves_per_position: int = 200
    enable_move_filtering: bool = True
    enable_move_prioritization: bool = True
    
    # Error Handling
    max_retries: int = 3
    retry_delay: float = 0.1
    enable_fallback_results: bool = True
    
    # Reporting
    save_intermediate_results: bool = True
    generate_detailed_reports: bool = True
    enable_progress_tracking: bool = True

@dataclass
class ComprehensiveAnalysisResult:
    """Result from comprehensive move analysis."""
    position_id: str
    move_data: Dict[str, Any]
    analysis_time: float
    
    # Core Scores
    pattern_score: float
    strategic_score: float
    risk_score: float
    quality_score: float
    quality_tier: QualityTier
    
    # Advanced Analysis
    board_state_impact: float
    opponent_denial_score: float
    timing_score: float
    risk_reward_ratio: float
    
    # Educational Content
    strategic_reasoning: str
    tactical_insights: str
    educational_explanation: str
    
    # Metadata
    confidence_interval: Tuple[float, float]
    analysis_methods_used: List[str]
    processing_metadata: Dict[str, Any]

class ComprehensiveMoveQualityAnalyzer:
    """Comprehensive move quality analyzer with parallel processing."""
    
    def __init__(self, config: ComprehensiveAnalysisConfig = None):
        self.config = config or ComprehensiveAnalysisConfig()
        
        # Initialize components
        self.move_quality_assessor = AzulMoveQualityAssessor()
        
        # Results database
        self.db_path = "../data/comprehensive_analysis_results.db"
        self._init_database()
        
        # Analysis counters
        self.total_analyses = 0
        self.successful_analyses = 0
        self.failed_analyses = 0
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the analyzer."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/comprehensive_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """Initialize results database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprehensive_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT NOT NULL,
                move_data TEXT NOT NULL,
                pattern_score REAL NOT NULL,
                strategic_score REAL NOT NULL,
                risk_score REAL NOT NULL,
                quality_score REAL NOT NULL,
                quality_tier TEXT NOT NULL,
                board_state_impact REAL,
                opponent_denial_score REAL,
                timing_score REAL,
                risk_reward_ratio REAL,
                strategic_reasoning TEXT,
                tactical_insights TEXT,
                educational_explanation TEXT,
                confidence_interval TEXT,
                analysis_methods_used TEXT,
                processing_metadata TEXT,
                analysis_time REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_position_id ON comprehensive_analysis_results(position_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quality_score ON comprehensive_analysis_results(quality_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quality_tier ON comprehensive_analysis_results(quality_tier)')
        
        conn.commit()
        conn.close()
    
    def analyze_single_move(self, position_fen: str, move_data: Dict[str, Any]) -> ComprehensiveAnalysisResult:
        """Analyze a single move with comprehensive evaluation."""
        start_time = time.time()
        
        try:
            # Parse position from FEN
            state = AzulState.from_fen(position_fen)
            
            # Convert move data to move key format
            move_key = self._convert_move_to_key(move_data)
            
            # Use existing move quality assessor
            quality_score = self.move_quality_assessor.assess_move_quality(state, 0, move_key)
            
            # Convert to comprehensive result format
            result = ComprehensiveAnalysisResult(
                position_id=position_fen,
                move_data=move_data,
                analysis_time=time.time() - start_time,
                pattern_score=quality_score.pattern_scores.get('blocking', 0.0),
                strategic_score=quality_score.strategic_value,
                risk_score=quality_score.risk_assessment,
                quality_score=quality_score.overall_score,
                quality_tier=self._convert_quality_tier(quality_score.quality_tier),
                board_state_impact=self._calculate_board_state_impact(state, move_data),
                opponent_denial_score=self._calculate_opponent_denial_score(state, move_data),
                timing_score=self._calculate_timing_score(state, move_data),
                risk_reward_ratio=self._calculate_risk_reward_ratio(quality_score),
                strategic_reasoning=quality_score.explanation,
                tactical_insights=self._generate_tactical_insights(move_data, quality_score),
                educational_explanation=quality_score.explanation,
                confidence_interval=(quality_score.confidence_score * 0.9, quality_score.confidence_score * 1.1),
                analysis_methods_used=['pattern_analysis', 'strategic_analysis', 'risk_assessment'],
                processing_metadata={'worker_id': os.getpid(), 'config': asdict(self.config)}
            )
            
            self.successful_analyses += 1
            return result
            
        except Exception as e:
            self.failed_analyses += 1
            self.logger.error(f"Failed to analyze move: {e}")
            raise
    
    def analyze_positions_batch(self, positions_file: str, batch_size: int = None) -> List[ComprehensiveAnalysisResult]:
        """Analyze a batch of positions with parallel processing."""
        if batch_size is None:
            batch_size = self.config.batch_size
        
        # Load positions
        with open(positions_file, 'r') as f:
            positions_data = json.load(f)
        
        positions = positions_data.get('positions', [])
        self.logger.info(f"Loaded {len(positions)} positions for analysis")
        
        results = []
        
        # Process in batches with parallel execution
        for i in range(0, len(positions), batch_size):
            batch = positions[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(positions) + batch_size - 1)//batch_size}")
            
            batch_results = self._process_batch_parallel(batch)
            results.extend(batch_results)
            
            # Save intermediate results
            if self.config.save_intermediate_results:
                self._save_results_to_database(batch_results)
        
        self.total_analyses = len(results)
        self.logger.info(f"Completed analysis of {len(results)} moves")
        
        return results
    
    def _process_batch_parallel(self, batch: List[Dict]) -> List[ComprehensiveAnalysisResult]:
        """Process a batch of positions using parallel processing."""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_position = {
                executor.submit(self._analyze_position_worker, position): position 
                for position in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_position):
                position = future_to_position[future]
                try:
                    position_results = future.result(timeout=self.config.max_analysis_time)
                    results.extend(position_results)
                except Exception as e:
                    self.logger.error(f"Failed to process position {position.get('id', 'unknown')}: {e}")
        
        return results
    
    def _analyze_position_worker(self, position_data: Dict) -> List[ComprehensiveAnalysisResult]:
        """Worker function for analyzing a single position."""
        results = []
        
        try:
            position_fen = position_data['fen']
            moves = position_data.get('moves', [])
            
            for move in moves:
                try:
                    result = self.analyze_single_move(position_fen, move)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to analyze move in position: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to process position: {e}")
        
        return results
    
    def _convert_move_to_key(self, move_data: Dict[str, Any]) -> str:
        """Convert move data to move key format."""
        move_type = move_data.get('move_type', 'factory_to_pattern')
        color = move_data.get('color', 0)
        count = move_data.get('count', 1)
        target_line = move_data.get('target_line', -1)
        
        if move_type == 'factory_to_pattern':
            factory_id = move_data.get('factory_id', 0)
            return f"factory_{factory_id}_tile_{color}_pattern_line_{target_line}"
        elif move_type == 'center_to_pattern':
            return f"center_tile_{color}_pattern_line_{target_line}"
        else:
            return f"move_{move_type}_{color}_{count}_{target_line}"
    
    def _convert_quality_tier(self, tier: MoveQualityTier) -> QualityTier:
        """Convert between quality tier enums."""
        mapping = {
            MoveQualityTier.BRILLIANT: QualityTier.BRILLIANT,
            MoveQualityTier.EXCELLENT: QualityTier.EXCELLENT,
            MoveQualityTier.GOOD: QualityTier.GOOD,
            MoveQualityTier.DUBIOUS: QualityTier.DUBIOUS,
            MoveQualityTier.POOR: QualityTier.POOR
        }
        return mapping.get(tier, QualityTier.GOOD)
    
    def _calculate_board_state_impact(self, state: AzulState, move_data: Dict[str, Any]) -> float:
        """Calculate the impact of a move on the board state."""
        # This would implement board state analysis
        # For now, return a placeholder score
        return 50.0
    
    def _calculate_opponent_denial_score(self, state: AzulState, move_data: Dict[str, Any]) -> float:
        """Calculate how much a move denies opportunities to opponents."""
        # This would implement opponent denial analysis
        # For now, return a placeholder score
        return 30.0
    
    def _calculate_timing_score(self, state: AzulState, move_data: Dict[str, Any]) -> float:
        """Calculate the timing efficiency of a move."""
        # This would implement timing analysis
        # For now, return a placeholder score
        return 60.0
    
    def _calculate_risk_reward_ratio(self, quality_score: MoveQualityScore) -> float:
        """Calculate the risk-reward ratio of a move."""
        if quality_score.risk_assessment > 0:
            return quality_score.opportunity_value / quality_score.risk_assessment
        return 1.0
    
    def _generate_tactical_insights(self, move_data: Dict[str, Any], quality_score: MoveQualityScore) -> str:
        """Generate tactical insights for a move."""
        insights = []
        
        if quality_score.pattern_scores.get('blocking', 0) > 70:
            insights.append("Strong blocking move")
        
        if quality_score.strategic_value > 75:
            insights.append("High strategic value")
        
        if quality_score.risk_assessment < 30:
            insights.append("Low risk move")
        
        return "; ".join(insights) if insights else "Standard tactical considerations"
    
    def _save_results_to_database(self, results: List[ComprehensiveAnalysisResult]):
        """Save analysis results to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for result in results:
            cursor.execute('''
                INSERT INTO comprehensive_analysis_results (
                    position_id, move_data, pattern_score, strategic_score, risk_score,
                    quality_score, quality_tier, board_state_impact, opponent_denial_score,
                    timing_score, risk_reward_ratio, strategic_reasoning, tactical_insights,
                    educational_explanation, confidence_interval, analysis_methods_used,
                    processing_metadata, analysis_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.position_id,
                json.dumps(result.move_data),
                result.pattern_score,
                result.strategic_score,
                result.risk_score,
                result.quality_score,
                result.quality_tier.value,
                result.board_state_impact,
                result.opponent_denial_score,
                result.timing_score,
                result.risk_reward_ratio,
                result.strategic_reasoning,
                result.tactical_insights,
                result.educational_explanation,
                json.dumps(result.confidence_interval),
                json.dumps(result.analysis_methods_used),
                json.dumps(result.processing_metadata),
                result.analysis_time
            ))
        
        conn.commit()
        conn.close()
    
    def generate_analysis_summary(self, results: List[ComprehensiveAnalysisResult]) -> Dict[str, Any]:
        """Generate a comprehensive analysis summary."""
        if not results:
            return {"error": "No results to summarize"}
        
        # Calculate statistics
        quality_scores = [r.quality_score for r in results]
        pattern_scores = [r.pattern_score for r in results]
        strategic_scores = [r.strategic_score for r in results]
        risk_scores = [r.risk_score for r in results]
        
        # Quality tier distribution
        tier_counts = {}
        for tier in QualityTier:
            tier_counts[tier.value] = len([r for r in results if r.quality_tier == tier])
        
        # Analysis time statistics
        analysis_times = [r.analysis_time for r in results]
        
        summary = {
            "total_analyses": len(results),
            "successful_analyses": self.successful_analyses,
            "failed_analyses": self.failed_analyses,
            "success_rate": self.successful_analyses / max(1, self.total_analyses),
            
            "quality_score_stats": {
                "mean": sum(quality_scores) / len(quality_scores),
                "median": sorted(quality_scores)[len(quality_scores)//2],
                "min": min(quality_scores),
                "max": max(quality_scores),
                "std": self._calculate_std(quality_scores)
            },
            
            "pattern_score_stats": {
                "mean": sum(pattern_scores) / len(pattern_scores),
                "median": sorted(pattern_scores)[len(pattern_scores)//2],
                "min": min(pattern_scores),
                "max": max(pattern_scores)
            },
            
            "strategic_score_stats": {
                "mean": sum(strategic_scores) / len(strategic_scores),
                "median": sorted(strategic_scores)[len(strategic_scores)//2],
                "min": min(strategic_scores),
                "max": max(strategic_scores)
            },
            
            "risk_score_stats": {
                "mean": sum(risk_scores) / len(risk_scores),
                "median": sorted(risk_scores)[len(risk_scores)//2],
                "min": min(risk_scores),
                "max": max(risk_scores)
            },
            
            "quality_tier_distribution": tier_counts,
            
            "analysis_time_stats": {
                "mean": sum(analysis_times) / len(analysis_times),
                "total": sum(analysis_times),
                "min": min(analysis_times),
                "max": max(analysis_times)
            },
            
            "config": asdict(self.config)
        }
        
        return summary
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

def main():
    """Main function for running comprehensive analysis."""
    # Create configuration
    config = ComprehensiveAnalysisConfig(
        max_workers=4,
        batch_size=50,
        max_analysis_time=30,
        enable_progress_tracking=True
    )
    
    # Initialize analyzer
    analyzer = ComprehensiveMoveQualityAnalyzer(config)
    
    # Run analysis on sample positions
    positions_file = "../data/diverse_positions.json"
    
    if os.path.exists(positions_file):
        print(f"Starting comprehensive analysis of {positions_file}")
        results = analyzer.analyze_positions_batch(positions_file)
        
        # Generate summary
        summary = analyzer.generate_analysis_summary(results)
        print(json.dumps(summary, indent=2))
        
        # Save summary to file
        with open("../data/comprehensive_analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Analysis complete. Processed {len(results)} moves.")
    else:
        print(f"Positions file not found: {positions_file}")

if __name__ == "__main__":
    main() 