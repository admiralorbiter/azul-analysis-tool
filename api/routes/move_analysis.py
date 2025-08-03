"""
Move Quality Analysis API Routes - Slice 1 Implementation

Provides REST API endpoints for move quality assessment that integrates
all existing pattern detection systems.
"""

from flask import Blueprint, request, jsonify
import traceback
import time

# Import core analysis engine
from core.azul_move_analyzer import AzulMoveQualityAssessor

# Import existing utilities for FEN string parsing
from api.routes.core import parse_fen_string
from core.azul_model import AzulState

# Create blueprint
move_analysis_bp = Blueprint('move_analysis', __name__)

# Global assessor instance (for performance)
_move_assessor = None

def get_move_assessor():
    """Get singleton move assessor instance."""
    global _move_assessor
    if _move_assessor is None:
        _move_assessor = AzulMoveQualityAssessor()
    return _move_assessor


@move_analysis_bp.route('/analyze-move-quality', methods=['POST'])
def analyze_move_quality():
    """
    Analyze move quality for a given position.
    
    Expected JSON payload:
    {
        "fen_string": "position_identifier",
        "current_player": 0,
        "include_alternatives": true,
        "max_alternatives": 4
    }
    
    Returns:
    {
        "success": true,
        "primary_recommendation": {...},
        "alternatives": [...],
        "total_moves_analyzed": 10,
        "analysis_summary": "...",
        "analysis_time_ms": 150
    }
    """
    start_time = time.time()
    
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract parameters
        fen_string = data.get('fen_string')
        current_player = data.get('current_player', 0)
        include_alternatives = data.get('include_alternatives', True)
        max_alternatives = data.get('max_alternatives', 4)
        
        # Validate required parameters
        if not fen_string:
            return jsonify({
                'success': False,
                'error': 'fen_string is required'
            }), 400
        
        if not isinstance(current_player, int) or current_player < 0:
            return jsonify({
                'success': False,
                'error': 'current_player must be a non-negative integer'
            }), 400
        
        # Parse game state from FEN string
        try:
            game_state = parse_fen_string(fen_string)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid FEN string: {str(e)}'
            }), 400
        
        # Validate player ID
        if current_player >= len(game_state.agents):
            return jsonify({
                'success': False,
                'error': f'Invalid player ID: {current_player}. Game has {len(game_state.agents)} players.'
            }), 400
        
        # Perform move quality analysis
        assessor = get_move_assessor()
        analysis = assessor.analyze_position(game_state, current_player)
        
        # Prepare response
        response_data = {
            'success': True,
            'primary_recommendation': analysis.primary_recommendation.to_dict(),
            'total_moves_analyzed': analysis.total_moves_analyzed,
            'analysis_summary': analysis.analysis_summary,
            'analysis_time_ms': round((time.time() - start_time) * 1000, 1)
        }
        
        # Include alternatives if requested
        if include_alternatives and analysis.alternatives:
            alternatives_to_include = analysis.alternatives[:max_alternatives]
            response_data['alternatives'] = [alt.to_dict() for alt in alternatives_to_include]
        else:
            response_data['alternatives'] = []
        
        return jsonify(response_data)
        
    except Exception as e:
        # Log error details
        error_details = traceback.format_exc()
        print(f"Move quality analysis error: {error_details}")
        
        return jsonify({
            'success': False,
            'error': 'Internal server error during move analysis',
            'details': str(e)
        }), 500


@move_analysis_bp.route('/move-quality-info', methods=['GET'])
def move_quality_info():
    """
    Get information about the move quality analysis system.
    
    Returns system capabilities and configuration.
    """
    try:
        assessor = get_move_assessor()
        
        return jsonify({
            'success': True,
            'system_info': {
                'name': 'Azul Move Quality Assessment System',
                'version': '1.0.0-slice1',
                'capabilities': [
                    'Tile blocking analysis',
                    'Scoring optimization analysis', 
                    'Floor line management analysis',
                    'Strategic pattern analysis (if available)',
                    '5-tier quality classification (!!,!,=,?!,?)',
                    'Alternative move ranking',
                    'Risk assessment',
                    'Move explanations'
                ],
                'quality_tiers': {
                    '!!': 'Brilliant (90-100)',
                    '!': 'Excellent (75-89)',
                    '=': 'Good/Solid (50-74)', 
                    '?!': 'Dubious (25-49)',
                    '?': 'Poor (0-24)'
                },
                'pattern_detectors': {
                    'blocking': True,
                    'scoring_optimization': True,
                    'floor_line_management': True,
                    'strategic_analysis': assessor.strategic_detector is not None
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get system info',
            'details': str(e)
        }), 500


@move_analysis_bp.route('/test-move-quality', methods=['GET'])
def test_move_quality():
    """
    Test endpoint to verify move quality analysis is working.
    
    Uses a simple test position to validate the system.
    """
    try:
        # Create a simple test position
        test_state = AzulState(2)  # 2-player game
        
        # Perform analysis
        assessor = get_move_assessor()
        analysis = assessor.analyze_position(test_state, player_id=0)
        
        return jsonify({
            'success': True,
            'message': 'Move quality analysis system is working',
            'test_results': {
                'moves_analyzed': analysis.total_moves_analyzed,
                'best_move_tier': analysis.primary_recommendation.quality_tier,
                'best_move_score': analysis.primary_recommendation.quality_score,
                'analysis_summary': analysis.analysis_summary
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Test failed',
            'details': str(e)
        }), 500