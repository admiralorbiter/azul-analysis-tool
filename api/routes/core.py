"""
Core API Routes

This module contains the core API endpoints that are fundamental to the application.
"""

import json
import time
from typing import Dict, Any
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from ..auth import require_session
from ..utils import parse_fen_string, format_move

# Create Flask blueprint for core endpoints
core_bp = Blueprint('core', __name__)


@core_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Check rate limit if session is provided
    session_id = request.headers.get('X-Session-ID')
    if session_id and current_app.rate_limiter:
        if not current_app.rate_limiter.check_rate_limit(session_id, "general"):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests'
            }), 429
    
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'timestamp': time.time()
    })


@core_bp.route('/stats', methods=['GET'])
@require_session
def get_api_stats():
    """Get API usage statistics."""
    session_id = request.headers.get('X-Session-ID')
    
    return jsonify({
        'rate_limits': current_app.rate_limiter.get_remaining_requests(session_id) if current_app.rate_limiter else {},
        'session_stats': current_app.session_manager.get_session_stats() if hasattr(current_app, 'session_manager') else {}
    })


@core_bp.route('/analyze_neural', methods=['POST'])
def analyze_neural():
    """Analyze position using neural MCTS."""
    try:
        data = request.get_json()
        
        # Parse request
        fen_string = data.get('fen', 'initial')
        agent_id = data.get('agent_id', 0)
        time_budget = data.get('time_budget', 2.0)
        max_rollouts = data.get('max_rollouts', 100)
        
        # Parse FEN and create state
        state = parse_fen_string(fen_string)
        if state is None:
            return jsonify({'error': 'Invalid FEN string'}), 400
        
        # Check if neural components are available
        try:
            from core.azul_mcts import AzulMCTS, RolloutPolicy
            from neural.azul_net import create_azul_net, AzulNeuralRolloutPolicy
            
            # Create neural MCTS
            mcts = AzulMCTS(
                rollout_policy=RolloutPolicy.NEURAL,
                max_time=time_budget,
                max_rollouts=max_rollouts,
                database=getattr(current_app, 'database', None)
            )
            
            # Perform search
            result = mcts.search(state, agent_id=agent_id, fen_string=fen_string)
            
            # Format response
            analysis = {
                'best_move': format_move(result.best_move),
                'best_score': result.best_score,
                'principal_variation': [format_move(move) for move in result.principal_variation],
                'search_time': result.search_time,
                'nodes_searched': result.nodes_searched,
                'rollout_count': result.rollout_count,
                'average_rollout_depth': result.average_rollout_depth,
                'method': 'neural_mcts'
            }
            
            # Cache result if database available
            if hasattr(current_app, 'database') and current_app.database:
                try:
                    position_id = current_app.database.cache_position(fen_string, len(state.agents))
                    current_app.database.cache_analysis(position_id, agent_id, 'neural_mcts', analysis)
                except Exception as e:
                    current_app.logger.warning(f"Failed to cache neural analysis: {e}")
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except ImportError as e:
            return jsonify({
                'error': 'Neural analysis not available',
                'message': 'PyTorch and neural components are not installed. Install with: pip install torch',
                'details': str(e)
            }), 503
            
        except Exception as e:
            return jsonify({
                'error': 'Neural analysis failed',
                'message': 'Neural model not trained or available',
                'details': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 