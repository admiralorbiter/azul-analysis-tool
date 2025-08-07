#!/usr/bin/env python3
"""
Pipeline Orchestrator - Complete Data Generation & Analysis Pipeline

This script orchestrates the entire pipeline from position generation through
analysis to final dataset creation, with comprehensive progress tracking and
error handling.
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
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
import traceback

# Import pipeline components
from enhanced_position_generator import EnhancedPositionGenerator
from parallel_analysis_pipeline import ParallelMoveAnalyzer

class PipelineStage(Enum):
    """Pipeline stages for tracking progress."""
    POSITION_GENERATION = "position_generation"
    POSITION_VALIDATION = "position_validation"
    MOVE_ANALYSIS = "move_analysis"
    QUALITY_CLASSIFICATION = "quality_classification"
    DATA_VALIDATION = "data_validation"
    FINAL_EXPORT = "final_export"

class PipelineStatus(Enum):
    """Pipeline status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PipelineStageResult:
    """Result from a pipeline stage."""
    stage: PipelineStage
    status: PipelineStatus
    start_time: float
    end_time: float
    duration: float
    metrics: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class PipelineConfig:
    """Configuration for the pipeline."""
    target_positions: int = 1000
    target_moves: int = 20000
    max_workers: int = 4
    batch_size: int = 50
    cache_enabled: bool = True
    parallel_processing: bool = True
    quality_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.quality_thresholds is None:
            self.quality_thresholds = {
                "brilliant": 90.0,
                "excellent": 75.0,
                "good": 50.0,
                "dubious": 25.0,
                "poor": 0.0
            }

class PipelineOrchestrator:
    """Orchestrates the complete move quality analysis pipeline."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.stage_results: List[PipelineStageResult] = []
        
        # Setup logging
        self._setup_logging()
        
        # Initialize pipeline components
        self.position_generator = EnhancedPositionGenerator(target_count=config.target_positions)
        self.move_analyzer = ParallelMoveAnalyzer(max_workers=config.max_workers)
        
        # Pipeline database
        self.db_path = "../data/pipeline_tracking.db"
        self._init_pipeline_database()
    
    def _setup_logging(self):
        """Setup logging for the pipeline."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../data/pipeline.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('PipelineOrchestrator')
    
    def _json_default_serializer(self, obj):
        """Custom JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    def _init_pipeline_database(self):
        """Initialize pipeline tracking database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pipeline_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                duration REAL,
                metrics TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pipeline_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _save_stage_result(self, result: PipelineStageResult):
        """Save stage result to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pipeline_stages 
            (stage, status, start_time, end_time, duration, metrics, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.stage.value,
            result.status.value,
            result.start_time,
            result.end_time,
            result.duration,
            json.dumps(result.metrics),
            result.error_message
        ))
        
        conn.commit()
        conn.close()
    
    def _save_config(self):
        """Save pipeline configuration to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        config_dict = asdict(self.config)
        for key, value in config_dict.items():
            cursor.execute('''
                INSERT OR REPLACE INTO pipeline_config (config_key, config_value)
                VALUES (?, ?)
            ''', (key, json.dumps(value, default=self._json_default_serializer)))
        
        conn.commit()
        conn.close()
    
    def run_stage(self, stage: PipelineStage, stage_func) -> PipelineStageResult:
        """Run a single pipeline stage with error handling."""
        self.logger.info(f"Starting stage: {stage.value}")
        
        start_time = time.time()
        result = PipelineStageResult(
            stage=stage,
            status=PipelineStatus.IN_PROGRESS,
            start_time=start_time,
            end_time=0.0,
            duration=0.0,
            metrics={}
        )
        
        try:
            # Run the stage function
            stage_metrics = stage_func()
            
            end_time = time.time()
            result.status = PipelineStatus.COMPLETED
            result.end_time = end_time
            result.duration = end_time - start_time
            result.metrics = stage_metrics
            
            self.logger.info(f"Completed stage: {stage.value} in {result.duration:.2f}s")
            
        except Exception as e:
            end_time = time.time()
            result.status = PipelineStatus.FAILED
            result.end_time = end_time
            result.duration = end_time - start_time
            result.error_message = str(e)
            
            self.logger.error(f"Failed stage: {stage.value} - {e}")
            self.logger.error(traceback.format_exc())
        
        # Save result
        self._save_stage_result(result)
        self.stage_results.append(result)
        
        return result
    
    def stage_position_generation(self) -> Dict[str, Any]:
        """Stage 1: Generate diverse positions."""
        self.logger.info("Generating diverse positions...")
        
        positions = self.position_generator.generate_all_positions()
        
        # Export positions
        self.position_generator.export_positions_to_json(
            positions, "../data/diverse_positions_enhanced.json"
        )
        
        # Calculate metrics
        metrics = {
            "total_positions": len(positions),
            "positions_by_phase": {},
            "positions_by_scenario": {},
            "complexity_distribution": {"simple": 0, "medium": 0, "complex": 0, "expert": 0}
        }
        
        for pos in positions:
            # Count by phase
            phase = pos.game_phase.value
            metrics["positions_by_phase"][phase] = metrics["positions_by_phase"].get(phase, 0) + 1
            
            # Count by scenario
            scenario = pos.strategic_scenario.value
            metrics["positions_by_scenario"][scenario] = metrics["positions_by_scenario"].get(scenario, 0) + 1
            
            # Count by complexity
            if pos.complexity_score < 0.3:
                metrics["complexity_distribution"]["simple"] += 1
            elif pos.complexity_score < 0.6:
                metrics["complexity_distribution"]["medium"] += 1
            elif pos.complexity_score < 0.8:
                metrics["complexity_distribution"]["complex"] += 1
            else:
                metrics["complexity_distribution"]["expert"] += 1
        
        self.logger.info(f"Generated {len(positions)} positions")
        return metrics
    
    def stage_position_validation(self) -> Dict[str, Any]:
        """Stage 2: Validate generated positions."""
        self.logger.info("Validating generated positions...")
        
        # Load positions
        with open("../data/diverse_positions_enhanced.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        positions = data.get("positions", [])
        
        # Validation metrics
        metrics = {
            "total_positions": len(positions),
            "valid_positions": 0,
            "invalid_positions": 0,
            "validation_errors": []
        }
        
        for pos in positions:
            try:
                # Basic validation checks
                if pos.get("position_id") and pos.get("fen_string"):
                    metrics["valid_positions"] += 1
                else:
                    metrics["invalid_positions"] += 1
                    metrics["validation_errors"].append(f"Missing required fields for position {pos.get('position_id', 'unknown')}")
            except Exception as e:
                metrics["invalid_positions"] += 1
                metrics["validation_errors"].append(f"Validation error: {e}")
        
        self.logger.info(f"Validated {metrics['valid_positions']} positions, {metrics['invalid_positions']} invalid")
        return metrics
    
    def stage_move_analysis(self) -> Dict[str, Any]:
        """Stage 3: Analyze moves for all positions."""
        self.logger.info("Analyzing moves for all positions...")
        
        # Check if positions file exists
        positions_file = "../data/diverse_positions_enhanced.json"
        if not os.path.exists(positions_file):
            raise FileNotFoundError(f"Positions file {positions_file} not found. Run position generation first.")
        
        # Run parallel analysis
        results = self.move_analyzer.analyze_positions_batch(
            positions_file, batch_size=self.config.batch_size
        )
        
        # Generate summary
        summary = self.move_analyzer.generate_analysis_summary(results)
        
        self.logger.info(f"Analyzed {summary['total_moves_analyzed']} moves")
        return summary
    
    def stage_quality_classification(self) -> Dict[str, Any]:
        """Stage 4: Classify move quality and generate insights."""
        self.logger.info("Classifying move quality and generating insights...")
        
        # Load analysis results from database
        conn = sqlite3.connect(self.move_analyzer.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT quality_tier, quality_score, neural_score, pattern_score
            FROM analysis_results
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Calculate quality metrics
        metrics = {
            "total_moves": len(results),
            "quality_distribution": {},
            "score_statistics": {
                "neural": {"min": 0, "max": 0, "avg": 0},
                "pattern": {"min": 0, "max": 0, "avg": 0},
                "quality": {"min": 0, "max": 0, "avg": 0}
            }
        }
        
        if results:
            # Quality distribution
            for tier in ["!!", "!", "=", "?!", "?"]:
                count = sum(1 for r in results if r[0] == tier)  # r[0] is quality_tier
                metrics["quality_distribution"][tier] = {
                    "count": count,
                    "percentage": count / len(results) * 100
                }
            
            # Score statistics
            neural_scores = [r[2] for r in results]  # r[2] is neural_score
            pattern_scores = [r[3] for r in results]  # r[3] is pattern_score
            quality_scores = [r[1] for r in results]  # r[1] is quality_score
            
            metrics["score_statistics"]["neural"] = {
                "min": min(neural_scores),
                "max": max(neural_scores),
                "avg": sum(neural_scores) / len(neural_scores)
            }
            metrics["score_statistics"]["pattern"] = {
                "min": min(pattern_scores),
                "max": max(pattern_scores),
                "avg": sum(pattern_scores) / len(pattern_scores)
            }
            metrics["score_statistics"]["quality"] = {
                "min": min(quality_scores),
                "max": max(quality_scores),
                "avg": sum(quality_scores) / len(quality_scores)
            }
        
        self.logger.info(f"Classified quality for {metrics['total_moves']} moves")
        return metrics
    
    def stage_data_validation(self) -> Dict[str, Any]:
        """Stage 5: Validate the complete dataset."""
        self.logger.info("Validating complete dataset...")
        
        metrics = {
            "validation_checks": {},
            "data_quality_score": 0.0,
            "recommendations": []
        }
        
        # Check database integrity
        conn = sqlite3.connect(self.move_analyzer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        total_results = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT position_id) FROM analysis_results")
        unique_positions = cursor.fetchone()[0]
        
        conn.close()
        
        metrics["validation_checks"]["total_results"] = total_results
        metrics["validation_checks"]["unique_positions"] = unique_positions
        metrics["validation_checks"]["results_per_position"] = total_results / unique_positions if unique_positions > 0 else 0
        
        # Quality checks
        if total_results >= self.config.target_moves * 0.8:  # 80% of target
            metrics["validation_checks"]["coverage"] = "GOOD"
            metrics["data_quality_score"] += 0.3
        else:
            metrics["validation_checks"]["coverage"] = "INSUFFICIENT"
            metrics["recommendations"].append("Increase move coverage")
        
        if unique_positions >= self.config.target_positions * 0.8:  # 80% of target
            metrics["validation_checks"]["position_diversity"] = "GOOD"
            metrics["data_quality_score"] += 0.3
        else:
            metrics["validation_checks"]["position_diversity"] = "INSUFFICIENT"
            metrics["recommendations"].append("Increase position diversity")
        
        # Check for balanced quality distribution
        conn = sqlite3.connect(self.move_analyzer.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT quality_tier, COUNT(*) 
            FROM analysis_results 
            GROUP BY quality_tier
        ''')
        
        quality_distribution = dict(cursor.fetchall())
        conn.close()
        
        # Check if any tier has more than 40% of moves
        max_percentage = max(quality_distribution.values()) / total_results * 100 if total_results > 0 else 0
        if max_percentage <= 40:
            metrics["validation_checks"]["quality_balance"] = "GOOD"
            metrics["data_quality_score"] += 0.4
        else:
            metrics["validation_checks"]["quality_balance"] = "UNBALANCED"
            metrics["recommendations"].append("Adjust quality thresholds for better balance")
        
        self.logger.info(f"Dataset validation complete. Quality score: {metrics['data_quality_score']:.1f}")
        return metrics
    
    def stage_final_export(self) -> Dict[str, Any]:
        """Stage 6: Export final dataset and generate reports."""
        self.logger.info("Exporting final dataset and generating reports...")
        
        metrics = {
            "exported_files": [],
            "report_files": [],
            "dataset_size": 0
        }
        
        # Export analysis results
        conn = sqlite3.connect(self.move_analyzer.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT position_id, move_data, neural_score, pattern_score, 
                   quality_tier, quality_score, strategic_reasoning, educational_explanation
            FROM analysis_results
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Create final dataset
        dataset = {
            "metadata": {
                "total_moves": len(results),
                "generation_time": time.time(),
                "pipeline_version": "1.0",
                "config": asdict(self.config)
            },
            "moves": []
        }
        
        for result in results:
            move_data = {
                "position_id": result[0],
                "move_data": json.loads(result[1]),
                "neural_score": result[2],
                "pattern_score": result[3],
                "quality_tier": result[4],
                "quality_score": result[5],
                "strategic_reasoning": result[6],
                "educational_explanation": result[7]
            }
            dataset["moves"].append(move_data)
        
        # Export dataset
        dataset_file = "../data/final_move_quality_dataset.json"
        with open(dataset_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, default=self._json_default_serializer)
        
        metrics["exported_files"].append(dataset_file)
        metrics["dataset_size"] = len(results)
        
        # Generate summary report
        report_file = "../data/pipeline_summary_report.json"
        report = {
            "pipeline_summary": {
                "total_stages": len(self.stage_results),
                "successful_stages": sum(1 for r in self.stage_results if r.status == PipelineStatus.COMPLETED),
                "failed_stages": sum(1 for r in self.stage_results if r.status == PipelineStatus.FAILED),
                "total_duration": sum(r.duration for r in self.stage_results)
            },
            "stage_results": [asdict(r) for r in self.stage_results],
            "final_metrics": {
                "total_positions": len(dataset["moves"]),
                "total_moves": len(dataset["moves"]),
                "quality_distribution": {},
                "average_scores": {
                    "neural": sum(m["neural_score"] for m in dataset["moves"]) / len(dataset["moves"]) if dataset["moves"] else 0,
                    "pattern": sum(m["pattern_score"] for m in dataset["moves"]) / len(dataset["moves"]) if dataset["moves"] else 0,
                    "quality": sum(m["quality_score"] for m in dataset["moves"]) / len(dataset["moves"]) if dataset["moves"] else 0
                }
            }
        }
        
        # Calculate quality distribution
        for tier in ["!!", "!", "=", "?!", "?"]:
            count = sum(1 for m in dataset["moves"] if m["quality_tier"] == tier)
            report["final_metrics"]["quality_distribution"][tier] = {
                "count": count,
                "percentage": count / len(dataset["moves"]) * 100 if dataset["moves"] else 0
            }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=self._json_default_serializer)
        
        metrics["report_files"].append(report_file)
        
        self.logger.info(f"Exported final dataset with {len(dataset['moves'])} moves")
        return metrics
    
    def run_pipeline(self) -> List[PipelineStageResult]:
        """Run the complete pipeline."""
        self.logger.info("Starting complete move quality analysis pipeline...")
        
        # Save configuration
        self._save_config()
        
        # Define pipeline stages
        stages = [
            (PipelineStage.POSITION_GENERATION, self.stage_position_generation),
            (PipelineStage.POSITION_VALIDATION, self.stage_position_validation),
            (PipelineStage.MOVE_ANALYSIS, self.stage_move_analysis),
            (PipelineStage.QUALITY_CLASSIFICATION, self.stage_quality_classification),
            (PipelineStage.DATA_VALIDATION, self.stage_data_validation),
            (PipelineStage.FINAL_EXPORT, self.stage_final_export)
        ]
        
        # Run each stage
        for stage, stage_func in stages:
            result = self.run_stage(stage, stage_func)
            
            # Check if stage failed
            if result.status == PipelineStatus.FAILED:
                self.logger.error(f"Pipeline failed at stage: {stage.value}")
                break
        
        # Generate final summary
        self._generate_pipeline_summary()
        
        return self.stage_results
    
    def _generate_pipeline_summary(self):
        """Generate final pipeline summary."""
        successful_stages = sum(1 for r in self.stage_results if r.status == PipelineStatus.COMPLETED)
        failed_stages = sum(1 for r in self.stage_results if r.status == PipelineStatus.FAILED)
        total_duration = sum(r.duration for r in self.stage_results)
        
        self.logger.info(f"\n=== Pipeline Summary ===")
        self.logger.info(f"Successful stages: {successful_stages}")
        self.logger.info(f"Failed stages: {failed_stages}")
        self.logger.info(f"Total duration: {total_duration:.2f} seconds")
        
        if failed_stages == 0:
            self.logger.info("✅ Pipeline completed successfully!")
        else:
            self.logger.error("❌ Pipeline completed with errors!")

def main():
    """Main function to run the complete pipeline."""
    # Create pipeline configuration
    config = PipelineConfig(
        target_positions=1000,
        target_moves=20000,
        max_workers=4,
        batch_size=50,
        cache_enabled=True,
        parallel_processing=True
    )
    
    # Create and run pipeline
    orchestrator = PipelineOrchestrator(config)
    results = orchestrator.run_pipeline()
    
    # Print final summary
    print(f"\n=== Pipeline Complete ===")
    print(f"Total stages: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r.status == PipelineStatus.COMPLETED)}")
    print(f"Failed: {sum(1 for r in results if r.status == PipelineStatus.FAILED)}")
    print(f"Total time: {sum(r.duration for r in results):.2f} seconds")

if __name__ == "__main__":
    main()
