"""
Move Quality Assessment API Routes

This module provides REST API endpoints for move quality assessment functionality.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import json

from analysis_engine.move_quality import (
    AzulMoveQualityAssessor,
    MoveQualityTier,
    MoveQualityScore,
    MoveQualityAssessment
)
from core.azul_model import AzulState

# Create blueprint
move_quality_bp = Blueprint('move_quality', __name__)

# Initialize assessor
move_quality_assessor = AzulMoveQualityAssessor()


@move_quality_bp.route('/api/v1/assess-move-quality', methods=['POST'])
def assess_move_quality():
    """
    Assess the quality of a specific move.
    
    Request body:
    {
        "state_fen": "game_state_fen_string",
        "player_id": 0,
        "move_key": "factory_0_tile_blue_pattern_line_1"
    }
    
    Response:
    {
        "success": true,
        "move_quality": {
            "overall_score": 85.0,
            "quality_tier": "!",
            "pattern_scores": {"blocking": 80.0, "scoring": 70.0},
            "strategic_value": 75.0,
            "tactical_value": 65.0,
            "risk_assessment": 50.0,
            "opportunity_value": 40.0,
            "explanation": "This is an excellent move...",
            "pattern_connections": ["Applies blocking principles"],
            "confidence_score": 0.8
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
        move_key = data.get('move_key')
        
        if not state_fen:
            return jsonify({
                "success": False,
                "error": "state_fen is required"
            }), 400
        
        if not move_key:
            return jsonify({
                "success": False,
                "error": "move_key is required"
            }), 400
        
        # Parse game state from FEN
        try:
            state = AzulState.from_fen(state_fen)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Invalid FEN string: {str(e)}"
            }), 400
        
        # Assess move quality
        quality_score = move_quality_assessor.assess_move_quality(state, player_id, move_key)
        
        # Convert to JSON-serializable format
        move_quality_data = {
            "overall_score": quality_score.overall_score,
            "quality_tier": quality_score.quality_tier.value,
            "pattern_scores": quality_score.pattern_scores,
            "strategic_value": quality_score.strategic_value,
            "tactical_value": quality_score.tactical_value,
            "risk_assessment": quality_score.risk_assessment,
            "opportunity_value": quality_score.opportunity_value,
            "explanation": quality_score.explanation,
            "pattern_connections": quality_score.pattern_connections,
            "confidence_score": quality_score.confidence_score
        }
        
        return jsonify({
            "success": True,
            "move_quality": move_quality_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Assessment failed: {str(e)}"
        }), 500


@move_quality_bp.route('/api/v1/evaluate-all-moves', methods=['POST'])
def evaluate_all_moves():
    """
    Evaluate all possible moves in a position.
    
    Request body:
    {
        "state_fen": "game_state_fen_string",
        "player_id": 0
    }
    
    Response:
    {
        "success": true,
        "assessment": {
            "position_fen": "game_state_fen_string",
            "player_id": 0,
            "all_moves_quality": {...},
            "best_moves": ["move_1", "move_2"],
            "alternative_moves": ["move_3"],
            "position_complexity": 0.7,
            "analysis_confidence": 0.8,
            "educational_insights": ["This position is complex"]
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
        
        # Evaluate all moves
        assessment = move_quality_assessor.evaluate_all_moves(state, player_id)
        
        # Convert to JSON-serializable format
        assessment_data = {
            "position_fen": assessment.position_fen,
            "player_id": assessment.player_id,
            "all_moves_quality": {
                move_key: {
                    "overall_score": score.overall_score,
                    "quality_tier": score.quality_tier.value,
                    "pattern_scores": score.pattern_scores,
                    "strategic_value": score.strategic_value,
                    "tactical_value": score.tactical_value,
                    "risk_assessment": score.risk_assessment,
                    "opportunity_value": score.opportunity_value,
                    "explanation": score.explanation,
                    "pattern_connections": score.pattern_connections,
                    "confidence_score": score.confidence_score
                }
                for move_key, score in assessment.all_moves_quality.items()
            },
            "best_moves": assessment.best_moves,
            "alternative_moves": assessment.alternative_moves,
            "position_complexity": assessment.position_complexity,
            "analysis_confidence": assessment.analysis_confidence,
            "educational_insights": assessment.educational_insights
        }
        
        return jsonify({
            "success": True,
            "assessment": assessment_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Evaluation failed: {str(e)}"
        }), 500


@move_quality_bp.route('/api/v1/move-quality-info', methods=['GET'])
def get_move_quality_info():
    """
    Get information about the move quality assessment system.
    
    Response:
    {
        "success": true,
        "system_info": {
            "tier_thresholds": {
                "!!": 90.0,
                "!": 75.0,
                "=": 50.0,
                "?!": 25.0,
                "?": 0.0
            },
            "scoring_weights": {
                "pattern_detection": 0.35,
                "strategic_value": 0.25,
                "tactical_value": 0.20,
                "risk_assessment": 0.15,
                "opportunity_value": 0.05
            },
            "tier_descriptions": {
                "!!": "Brilliant - Multiple high-value objectives",
                "!": "Excellent - Primary strategic objective achieved",
                "=": "Good - Reasonable, safe moves",
                "?!": "Dubious - Some benefit but significant downsides",
                "?": "Poor - Clear mistakes with negative impact"
            }
        }
    }
    """
    try:
        # Get tier thresholds
        tier_thresholds = {
            tier.value: threshold
            for tier, threshold in move_quality_assessor.tier_thresholds.items()
        }
        
        # Get scoring weights
        scoring_weights = move_quality_assessor.scoring_weights
        
        # Tier descriptions
        tier_descriptions = {
            "!!": "Brilliant - Multiple high-value objectives",
            "!": "Excellent - Primary strategic objective achieved",
            "=": "Good - Reasonable, safe moves",
            "?!": "Dubious - Some benefit but significant downsides",
            "?": "Poor - Clear mistakes with negative impact"
        }
        
        return jsonify({
            "success": True,
            "system_info": {
                "tier_thresholds": tier_thresholds,
                "scoring_weights": scoring_weights,
                "tier_descriptions": tier_descriptions
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get system info: {str(e)}"
        }), 500 