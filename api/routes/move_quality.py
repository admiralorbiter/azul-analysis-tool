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


@move_quality_bp.route('/assess-move-quality', methods=['POST'])
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


@move_quality_bp.route('/evaluate-all-moves', methods=['POST'])
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


@move_quality_bp.route('/move-quality-info', methods=['GET'])
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


@move_quality_bp.route('/education/move-explanation', methods=['POST'])
def get_move_educational_explanation():
    """
    Get educational explanation for a move quality assessment.
    
    Request body:
    {
        "quality_tier": "!",
        "move_description": "Take blue tile from factory 2 to pattern line 3",
        "position_context": "Mid-game position with multiple options"
    }
    
    Response:
    {
        "success": true,
        "educational_content": {
            "title": "Excellent Move - Strong Strategic Play",
            "explanation": "This move is strategically sound...",
            "strategic_reasoning": "Excellent moves typically maximize...",
            "learning_tips": ["Focus on moves that improve your position", ...],
            "best_practices": "Excellent moves are the foundation of strong play...",
            "related_concepts": ["positional play", "strategic planning"],
            "difficulty_level": "intermediate"
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
        
        quality_tier = data.get('quality_tier')
        move_description = data.get('move_description', '')
        position_context = data.get('position_context', '')
        
        if not quality_tier:
            return jsonify({
                "success": False,
                "error": "quality_tier is required"
            }), 400
        
        # Educational content for each quality tier
        educational_content = {
            '!!': {
                "title": "Brilliant Move - Strategic Masterpiece",
                "explanation": "This move demonstrates exceptional strategic thinking. It likely creates multiple threats, blocks opponent opportunities, and sets up future advantages.",
                "strategic_reasoning": "Brilliant moves often combine tactical precision with long-term strategic vision. They may sacrifice immediate gains for superior position.",
                "learning_tips": [
                    "Look for moves that create multiple threats",
                    "Consider long-term strategic implications",
                    "Evaluate opponent's best responses",
                    "Balance immediate gains with future opportunities"
                ],
                "best_practices": "When you find a brilliant move, take time to understand why it works. These moves often reveal deep strategic patterns.",
                "related_concepts": ["tactical combinations", "strategic planning", "positional sacrifice"],
                "difficulty_level": "advanced"
            },
            '!': {
                "title": "Excellent Move - Strong Strategic Play",
                "explanation": "This move is strategically sound and likely the best available option. It improves your position while limiting opponent opportunities.",
                "strategic_reasoning": "Excellent moves typically maximize your advantages while minimizing risks. They follow sound strategic principles.",
                "learning_tips": [
                    "Focus on moves that improve your position",
                    "Consider the principle of least resistance",
                    "Evaluate risk-reward ratios carefully",
                    "Look for moves that limit opponent options"
                ],
                "best_practices": "Excellent moves are the foundation of strong play. Practice identifying these moves consistently.",
                "related_concepts": ["positional play", "risk management", "strategic planning"],
                "difficulty_level": "intermediate"
            },
            '=': {
                "title": "Good Move - Solid Strategic Choice",
                "explanation": "This move is fundamentally sound and maintains a good position. While not exceptional, it avoids mistakes and keeps options open.",
                "strategic_reasoning": "Good moves maintain equilibrium and avoid weakening your position. They provide a solid foundation for future play.",
                "learning_tips": [
                    "Prioritize moves that don't weaken your position",
                    "Maintain flexibility for future opportunities",
                    "Avoid moves that create unnecessary weaknesses",
                    "Consider the principle of least commitment"
                ],
                "best_practices": "Good moves are the backbone of consistent play. Master these before attempting more complex strategies.",
                "related_concepts": ["solid play", "positional maintenance", "flexibility"],
                "difficulty_level": "beginner"
            },
            '?!': {
                "title": "Dubious Move - Questionable Strategic Choice",
                "explanation": "This move has significant drawbacks or risks. While it might work in some situations, it's generally not recommended.",
                "strategic_reasoning": "Dubious moves often involve unnecessary risks or fail to address key strategic concerns. They may create weaknesses.",
                "learning_tips": [
                    "Look for safer alternatives",
                    "Consider the risks before making the move",
                    "Evaluate if the potential gains justify the risks",
                    "Ask yourself if this move creates weaknesses"
                ],
                "best_practices": "When you see a dubious move, look for better alternatives. Sometimes the best move is to avoid making a move.",
                "related_concepts": ["risk assessment", "safety first", "alternative analysis"],
                "difficulty_level": "intermediate"
            },
            '?': {
                "title": "Poor Move - Strategic Mistake",
                "explanation": "This move is strategically unsound and likely worsens your position. It may create weaknesses or miss better opportunities.",
                "strategic_reasoning": "Poor moves often violate basic strategic principles. They may create weaknesses, miss opportunities, or play into opponent plans.",
                "learning_tips": [
                    "Look for moves that improve your position",
                    "Consider the strategic implications carefully",
                    "Avoid moves that create weaknesses",
                    "Think about what your opponent wants you to do"
                ],
                "best_practices": "Learn from poor moves by understanding why they don't work. This helps avoid similar mistakes in the future.",
                "related_concepts": ["mistake analysis", "strategic principles", "positional awareness"],
                "difficulty_level": "beginner"
            }
        }
        
        # Get educational content for the quality tier
        content = educational_content.get(quality_tier, educational_content['='])
        
        # Add contextual information if provided
        if move_description:
            content["move_context"] = move_description
        if position_context:
            content["position_context"] = position_context
        
        return jsonify({
            "success": True,
            "educational_content": content
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Educational explanation failed: {str(e)}"
        }), 500


@move_quality_bp.route('/education/strategic-concepts', methods=['GET'])
def get_strategic_concepts():
    """
    Get list of strategic concepts for educational purposes.
    
    Response:
    {
        "success": true,
        "concepts": [
            {
                "name": "Positional Play",
                "description": "Focusing on improving your position...",
                "difficulty": "intermediate",
                "examples": ["controlling key squares", "piece coordination"]
            }
        ]
    }
    """
    strategic_concepts = [
        {
            "name": "Positional Play",
            "description": "Focusing on improving your position rather than immediate tactical gains. This involves controlling key areas and coordinating your pieces effectively.",
            "difficulty": "intermediate",
            "examples": ["controlling key squares", "piece coordination", "pawn structure"],
            "learning_tips": [
                "Look for moves that improve your position",
                "Consider long-term strategic goals",
                "Evaluate piece coordination"
            ]
        },
        {
            "name": "Tactical Awareness",
            "description": "Recognizing and creating tactical opportunities. This involves calculating specific sequences and identifying immediate threats.",
            "difficulty": "beginner",
            "examples": ["forks", "pins", "discovered attacks"],
            "learning_tips": [
                "Look for multiple threats",
                "Calculate specific sequences",
                "Identify opponent weaknesses"
            ]
        },
        {
            "name": "Risk Management",
            "description": "Balancing potential gains against potential losses. This involves evaluating the safety of your position and avoiding unnecessary risks.",
            "difficulty": "intermediate",
            "examples": ["safe play", "risk assessment", "defensive moves"],
            "learning_tips": [
                "Evaluate risk-reward ratios",
                "Consider opponent counterplay",
                "Prioritize safety when ahead"
            ]
        },
        {
            "name": "Strategic Planning",
            "description": "Developing long-term plans and coordinating your moves toward specific goals. This involves understanding the position's strategic themes.",
            "difficulty": "advanced",
            "examples": ["long-term planning", "strategic themes", "positional understanding"],
            "learning_tips": [
                "Identify the position's key features",
                "Develop long-term plans",
                "Coordinate your pieces"
            ]
        }
    ]
    
    return jsonify({
        "success": True,
        "concepts": strategic_concepts
    }) 