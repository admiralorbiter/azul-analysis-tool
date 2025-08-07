"""
Comprehensive Analysis API Routes

This module provides REST API endpoints for the comprehensive move quality analysis system.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional, List
import json
import time
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.azul_model import AzulState
from move_quality_analysis.scripts.comprehensive_move_quality_analyzer import (
    ComprehensiveMoveQualityAnalyzer, ComprehensiveAnalysisConfig, ComprehensiveAnalysisResult
)
from move_quality_analysis.scripts.enhanced_move_generator import (
    EnhancedMoveGenerator, GeneratedMove
)
from move_quality_analysis.scripts.analysis_config import ConfigurationManager

# Create blueprint
comprehensive_analysis_bp = Blueprint('comprehensive_analysis', __name__)

# Initialize components
config_manager = ConfigurationManager()
analyzer = None
move_generator = None

def get_analyzer():
    """Get or create the analyzer instance."""
    global analyzer
    if analyzer is None:
        config = config_manager.load_configuration()
        analyzer = ComprehensiveMoveQualityAnalyzer(config)
    return analyzer

def get_move_generator():
    """Get or create the move generator instance."""
    global move_generator
    if move_generator is None:
        config = config_manager.load_configuration()
        move_generator = EnhancedMoveGenerator(
            max_moves_per_position=config.move_generation.max_moves_per_position,
            enable_filtering=config.move_generation.enable_move_filtering
        )
    return move_generator

@comprehensive_analysis_bp.route('/analyze-position', methods=['POST'])
def analyze_position():
    """
    Analyze all moves in a position comprehensively.
    
    Request body:
    {
        "state_fen": "game_state_fen_string",
        "player_id": 0,
        "config_overrides": {
            "processing": {"max_workers": 4},
            "move_generation": {"max_moves_per_position": 100}
        }
    }
    
    Response:
    {
        "success": true,
        "analysis_results": [
            {
                "move_data": {...},
                "quality_score": 85.0,
                "quality_tier": "!!",
                "pattern_score": 80.0,
                "strategic_score": 75.0,
                "risk_score": 30.0,
                "board_state_impact": 50.0,
                "opponent_denial_score": 30.0,
                "timing_score": 60.0,
                "risk_reward_ratio": 2.5,
                "strategic_reasoning": "...",
                "tactical_insights": "...",
                "educational_explanation": "...",
                "analysis_time": 0.5
            }
        ],
        "summary": {
            "total_moves": 50,
            "quality_distribution": {...},
            "analysis_time": 25.0
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extract parameters
        state_fen = data.get('state_fen')
        player_id = data.get('player_id', 0)
        config_overrides = data.get('config_overrides', {})
        
        if not state_fen:
            return jsonify({
                "success": False,
                "error": "state_fen is required"
            }), 400
        
        # Parse game state from FEN
        try:
            state = AzulState.from_fen(state_fen)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Invalid FEN string: {str(e)}"
            }), 400
        
        # Apply configuration overrides
        config = config_manager.load_configuration()
        if config_overrides:
            config = _apply_config_overrides(config, config_overrides)
        
        # Get analyzer and move generator
        analyzer = get_analyzer()
        move_generator = get_move_generator()
        
        # Generate all possible moves
        generated_moves = move_generator.generate_all_moves(state, player_id)
        
        # Analyze each move
        analysis_results = []
        start_time = time.time()
        
        for move in generated_moves:
            try:
                result = analyzer.analyze_single_move(state_fen, move.move_data)
                analysis_results.append(result)
            except Exception as e:
                # Log error but continue with other moves
                print(f"Failed to analyze move: {e}")
                continue
        
        analysis_time = time.time() - start_time
        
        # Generate summary
        summary = _generate_analysis_summary(analysis_results, analysis_time)
        
        # Convert results to JSON-serializable format
        results_data = []
        for result in analysis_results:
            results_data.append({
                "move_data": result.move_data,
                "quality_score": result.quality_score,
                "quality_tier": result.quality_tier.value,
                "pattern_score": result.pattern_score,
                "strategic_score": result.strategic_score,
                "risk_score": result.risk_score,
                "board_state_impact": result.board_state_impact,
                "opponent_denial_score": result.opponent_denial_score,
                "timing_score": result.timing_score,
                "risk_reward_ratio": result.risk_reward_ratio,
                "strategic_reasoning": result.strategic_reasoning,
                "tactical_insights": result.tactical_insights,
                "educational_explanation": result.educational_explanation,
                "analysis_time": result.analysis_time
            })
        
        return jsonify({
            "success": True,
            "analysis_results": results_data,
            "summary": summary,
            "config": _config_to_dict(config)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }), 500

@comprehensive_analysis_bp.route('/generate-moves', methods=['POST'])
def generate_moves():
    """
    Generate all possible moves for a position.
    
    Request body:
    {
        "state_fen": "game_state_fen_string",
        "player_id": 0,
        "enable_filtering": true,
        "max_moves": 200
    }
    
    Response:
    {
        "success": true,
        "moves": [
            {
                "move_type": "factory_to_pattern",
                "factory_id": 0,
                "color": 0,
                "count": 4,
                "target_line": 1,
                "priority": "HIGH",
                "strategic_value": 75.0,
                "likelihood": 0.8,
                "validation_score": 1.0
            }
        ],
        "summary": {
            "total_moves": 50,
            "type_distribution": {...},
            "priority_distribution": {...}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extract parameters
        state_fen = data.get('state_fen')
        player_id = data.get('player_id', 0)
        enable_filtering = data.get('enable_filtering', True)
        max_moves = data.get('max_moves', 200)
        
        if not state_fen:
            return jsonify({
                "success": False,
                "error": "state_fen is required"
            }), 400
        
        # Parse game state from FEN
        try:
            state = AzulState.from_fen(state_fen)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Invalid FEN string: {str(e)}"
            }), 400
        
        # Generate moves
        move_generator = get_move_generator()
        move_generator.max_moves_per_position = max_moves
        move_generator.enable_filtering = enable_filtering
        
        moves = move_generator.generate_all_moves(state, player_id)
        
        # Generate summary
        summary = move_generator.generate_move_summary(moves)
        
        # Convert moves to JSON-serializable format
        moves_data = []
        for move in moves:
            moves_data.append({
                "move_type": move.move_type.value,
                "factory_id": move.factory_id,
                "color": move.color,
                "count": move.count,
                "target_line": move.target_line,
                "priority": move.priority.name,
                "strategic_value": move.strategic_value,
                "likelihood": move.likelihood,
                "validation_score": move.validation_score,
                "move_data": move.move_data
            })
        
        return jsonify({
            "success": True,
            "moves": moves_data,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Move generation failed: {str(e)}"
        }), 500

@comprehensive_analysis_bp.route('/analyze-batch', methods=['POST'])
def analyze_batch():
    """
    Analyze a batch of positions.
    
    Request body:
    {
        "positions": [
            {
                "id": "position_1",
                "fen": "game_state_fen_string",
                "player_id": 0
            }
        ],
        "config_overrides": {...}
    }
    
    Response:
    {
        "success": true,
        "batch_results": [...],
        "batch_summary": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        positions = data.get('positions', [])
        config_overrides = data.get('config_overrides', {})
        
        if not positions:
            return jsonify({
                "success": False,
                "error": "positions array is required"
            }), 400
        
        # Apply configuration overrides
        config = config_manager.load_configuration()
        if config_overrides:
            config = _apply_config_overrides(config, config_overrides)
        
        # Get analyzer
        analyzer = get_analyzer()
        
        # Analyze positions in batch
        batch_results = []
        total_start_time = time.time()
        
        for position_data in positions:
            try:
                position_id = position_data.get('id', 'unknown')
                state_fen = position_data.get('fen')
                player_id = position_data.get('player_id', 0)
                
                if not state_fen:
                    continue
                
                # Parse state
                state = AzulState.from_fen(state_fen)
                
                # Generate moves
                move_generator = get_move_generator()
                moves = move_generator.generate_all_moves(state, player_id)
                
                # Analyze moves
                position_results = []
                for move in moves:
                    try:
                        result = analyzer.analyze_single_move(state_fen, move.move_data)
                        position_results.append(result)
                    except Exception as e:
                        print(f"Failed to analyze move in position {position_id}: {e}")
                        continue
                
                batch_results.append({
                    "position_id": position_id,
                    "state_fen": state_fen,
                    "player_id": player_id,
                    "results": position_results,
                    "summary": _generate_analysis_summary(position_results, 0)
                })
                
            except Exception as e:
                print(f"Failed to process position {position_data.get('id', 'unknown')}: {e}")
                continue
        
        total_time = time.time() - total_start_time
        
        # Generate batch summary
        batch_summary = {
            "total_positions": len(positions),
            "processed_positions": len(batch_results),
            "total_analysis_time": total_time,
            "average_time_per_position": total_time / max(1, len(batch_results))
        }
        
        return jsonify({
            "success": True,
            "batch_results": batch_results,
            "batch_summary": batch_summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Batch analysis failed: {str(e)}"
        }), 500

@comprehensive_analysis_bp.route('/config', methods=['GET'])
def get_configuration():
    """
    Get current configuration.
    
    Response:
    {
        "success": true,
        "config": {...}
    }
    """
    try:
        config = config_manager.load_configuration()
        return jsonify({
            "success": True,
            "config": _config_to_dict(config)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load configuration: {str(e)}"
        }), 500

@comprehensive_analysis_bp.route('/config', methods=['POST'])
def update_configuration():
    """
    Update configuration.
    
    Request body:
    {
        "config_overrides": {
            "processing": {"max_workers": 4},
            "move_generation": {"max_moves_per_position": 100}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        config_overrides = data.get('config_overrides', {})
        
        # Load current config and apply overrides
        config = config_manager.load_configuration()
        config = _apply_config_overrides(config, config_overrides)
        
        # Reset analyzer to use new config
        global analyzer
        analyzer = ComprehensiveMoveQualityAnalyzer(config)
        
        return jsonify({
            "success": True,
            "config": _config_to_dict(config)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update configuration: {str(e)}"
        }), 500

def _apply_config_overrides(config: ComprehensiveAnalysisConfig, overrides: Dict[str, Any]) -> ComprehensiveAnalysisConfig:
    """Apply configuration overrides."""
    # Apply processing overrides
    if 'processing' in overrides:
        for key, value in overrides['processing'].items():
            if hasattr(config.processing, key):
                setattr(config.processing, key, value)
    
    # Apply analysis components overrides
    if 'analysis_components' in overrides:
        for key, value in overrides['analysis_components'].items():
            if hasattr(config.analysis_components, key):
                setattr(config.analysis_components, key, value)
    
    # Apply move generation overrides
    if 'move_generation' in overrides:
        for key, value in overrides['move_generation'].items():
            if hasattr(config.move_generation, key):
                setattr(config.move_generation, key, value)
    
    # Apply database overrides
    if 'database' in overrides:
        for key, value in overrides['database'].items():
            if hasattr(config.database, key):
                setattr(config.database, key, value)
    
    # Apply reporting overrides
    if 'reporting' in overrides:
        for key, value in overrides['reporting'].items():
            if hasattr(config.reporting, key):
                setattr(config.reporting, key, value)
    
    return config

def _generate_analysis_summary(results: List[ComprehensiveAnalysisResult], analysis_time: float) -> Dict[str, Any]:
    """Generate a summary of analysis results."""
    if not results:
        return {"error": "No results to summarize"}
    
    # Calculate statistics
    quality_scores = [r.quality_score for r in results]
    pattern_scores = [r.pattern_score for r in results]
    strategic_scores = [r.strategic_score for r in results]
    risk_scores = [r.risk_score for r in results]
    
    # Quality tier distribution
    tier_counts = {}
    for tier in ['!!', '!', '=', '?!', '?']:
        tier_counts[tier] = len([r for r in results if r.quality_tier.value == tier])
    
    summary = {
        "total_moves": len(results),
        "analysis_time": analysis_time,
        "quality_score_stats": {
            "mean": sum(quality_scores) / len(quality_scores),
            "median": sorted(quality_scores)[len(quality_scores)//2],
            "min": min(quality_scores),
            "max": max(quality_scores)
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
        "quality_tier_distribution": tier_counts
    }
    
    return summary

def _config_to_dict(config: ComprehensiveAnalysisConfig) -> Dict[str, Any]:
    """Convert configuration to dictionary."""
    config_dict = {
        "analysis_mode": config.analysis_mode.value,
        "processing_strategy": config.processing_strategy.value,
        "processing": {
            "max_workers": config.processing.max_workers,
            "batch_size": config.processing.batch_size,
            "max_analysis_time": config.processing.max_analysis_time,
            "memory_limit_gb": config.processing.memory_limit_gb,
            "enable_caching": config.processing.enable_caching,
            "cache_size_mb": config.processing.cache_size_mb,
            "retry_failed_analyses": config.processing.retry_failed_analyses,
            "max_retries": config.processing.max_retries,
            "retry_delay": config.processing.retry_delay
        },
        "analysis_components": {
            "enable_pattern_analysis": config.analysis_components.enable_pattern_analysis,
            "enable_strategic_analysis": config.analysis_components.enable_strategic_analysis,
            "enable_risk_analysis": config.analysis_components.enable_risk_analysis,
            "enable_board_state_analysis": config.analysis_components.enable_board_state_analysis,
            "enable_opponent_denial": config.analysis_components.enable_opponent_denial,
            "enable_timing_analysis": config.analysis_components.enable_timing_analysis,
            "enable_neural_evaluation": config.analysis_components.enable_neural_evaluation,
            "enable_ml_integration": config.analysis_components.enable_ml_integration
        },
        "move_generation": {
            "max_moves_per_position": config.move_generation.max_moves_per_position,
            "enable_move_filtering": config.move_generation.enable_move_filtering,
            "enable_move_prioritization": config.move_generation.enable_move_prioritization,
            "enable_move_clustering": config.move_generation.enable_move_clustering,
            "min_strategic_value": config.move_generation.min_strategic_value,
            "min_likelihood": config.move_generation.min_likelihood,
            "min_validation_score": config.move_generation.min_validation_score
        },
        "database": {
            "results_db_path": config.database.results_db_path,
            "cache_db_path": config.database.cache_db_path,
            "enable_indexing": config.database.enable_indexing,
            "enable_compression": config.database.enable_compression,
            "backup_enabled": config.database.backup_enabled,
            "backup_interval_hours": config.database.backup_interval_hours
        },
        "reporting": {
            "save_intermediate_results": config.reporting.save_intermediate_results,
            "generate_detailed_reports": config.reporting.generate_detailed_reports,
            "enable_progress_tracking": config.reporting.enable_progress_tracking,
            "enable_logging": config.reporting.enable_logging,
            "log_level": config.reporting.log_level,
            "output_format": config.reporting.output_format,
            "enable_visualization": config.reporting.enable_visualization,
            "report_directory": config.reporting.report_directory
        },
        "enable_debug_mode": config.enable_debug_mode,
        "enable_profiling": config.enable_profiling,
        "enable_metrics_collection": config.enable_metrics_collection
    }
    
    return config_dict 