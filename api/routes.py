"""
REST API routes for the Azul Solver & Analysis Toolkit.

This module provides Flask blueprints for game analysis, hints, and research tools.
"""

import json
import time
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, ValidationError

from .auth import require_session
from .rate_limiter import RateLimiter


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoints."""
    fen_string: str
    agent_id: int = 0
    depth: Optional[int] = None
    time_budget: Optional[float] = None
    rollouts: Optional[int] = None


class HintRequest(BaseModel):
    """Request model for hint endpoints."""
    fen_string: str
    agent_id: int = 0
    budget: float = 0.2
    rollouts: int = 100


# Create Flask blueprint for API endpoints
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def parse_fen_string(fen_string: str):
    """Parse FEN string to create game state."""
    from core.azul_model import AzulState
    
    if fen_string.lower() == "initial":
        return AzulState(2)  # 2-player starting position
    else:
        raise ValueError(f"Unsupported FEN format: {fen_string}. Use 'initial' for now.")


def format_move(move):
    """Format a move for display."""
    if move is None:
        return "None"
    
    try:
        # Convert FastMove to readable format
        action_type = "factory" if move.source_id >= 0 else "centre"
        
        # Map tile types correctly (check azul_utils for proper mapping)
        tile_names = {0: "blue", 1: "yellow", 2: "red", 3: "black", 4: "white"}
        tile_type = tile_names.get(move.tile_type, f"unknown_tile_{move.tile_type}")
        
        if move.pattern_line_dest >= 0:
            return f"take {move.num_to_pattern_line} {tile_type} from {action_type} {move.source_id} to pattern line {move.pattern_line_dest + 1}"
        else:
            return f"take {move.num_to_floor_line} {tile_type} from {action_type} {move.source_id} to floor"
    except Exception as e:
        # Fallback if move formatting fails
        return f"move(source={getattr(move, 'source_id', '?')}, tile={getattr(move, 'tile_type', '?')})"


@api_bp.route('/analyze', methods=['POST'])
@require_session
def analyze_position():
    """
    Analyze a game position with exact search.
    
    POST /api/v1/analyze
    {
        "fen_string": "game state in FEN format",
        "agent_id": 0,
        "depth": 3,
        "time_budget": 4.0
    }
    """
    try:
        # Check rate limit for heavy analysis
        session_id = request.headers.get('X-Session-ID')
        if not current_app.rate_limiter.check_rate_limit(session_id, "heavy"):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many heavy analysis requests'
            }), 429
        
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        analysis_req = AnalysisRequest(**data)
        
        # Parse game state
        state = parse_fen_string(analysis_req.fen_string)
        
        # Import search components
        from core.azul_search import AzulAlphaBetaSearch
        
        # Create search engine
        search_engine = AzulAlphaBetaSearch(
            max_depth=analysis_req.depth or 3,
            max_time=analysis_req.time_budget or 4.0
        )
        
        # Perform search
        result = search_engine.search(
            state, 
            analysis_req.agent_id, 
            max_depth=analysis_req.depth or 3,
            max_time=analysis_req.time_budget or 4.0
        )
        search_time = getattr(result, 'search_time', 0.0)
        
        # Format response
        response = {
            'success': True,
            'analysis': {
                'best_move': format_move(result.best_move) if result.best_move else None,
                'best_score': result.best_score,
                'principal_variation': [format_move(move) for move in result.principal_variation],
                'search_time': search_time,
                'nodes_searched': result.nodes_searched,
                'depth_reached': result.depth_reached
            },
            'position': {
                'fen_string': analysis_req.fen_string,
                'agent_id': analysis_req.agent_id
            }
        }
        
        # Cache result if database is available
        if hasattr(current_app, 'database'):
            try:
                position_id = current_app.database.cache_position(
                    analysis_req.fen_string, 
                    len(state.agents)
                )
                current_app.database.cache_analysis(
                    position_id,
                    analysis_req.agent_id,
                    'alpha_beta',
                    {
                        'best_move': str(result.best_move) if result.best_move else None,
                        'best_score': result.best_score,
                        'search_time': search_time,
                        'nodes_searched': result.nodes_searched,
                        'depth_reached': result.depth_reached,
                        'principal_variation': [str(move) for move in result.principal_variation]
                    }
                )
            except Exception as e:
                # Log but don't fail the request
                current_app.logger.warning(f"Failed to cache analysis: {e}")
        
        return jsonify(response)
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid position', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500


@api_bp.route('/hint', methods=['POST'])
@require_session
def get_hint():
    """
    Get a fast hint for a game position.
    
    POST /api/v1/hint
    {
        "fen_string": "game state in FEN format",
        "agent_id": 0,
        "budget": 0.2,
        "rollouts": 100
    }
    """
    try:
        # Check rate limit for light analysis
        session_id = request.headers.get('X-Session-ID')
        if not current_app.rate_limiter.check_rate_limit(session_id, "light"):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many hint requests'
            }), 429
        
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        hint_req = HintRequest(**data)
        
        # Parse game state
        state = parse_fen_string(hint_req.fen_string)
        
        # Import MCTS components
        from core.azul_mcts import AzulMCTS
        
        # Create MCTS engine
        mcts_engine = AzulMCTS(
            max_time=hint_req.budget,
            max_rollouts=hint_req.rollouts,
            database=getattr(current_app, 'database', None)
        )
        
        # Perform search
        result = mcts_engine.search(state, hint_req.agent_id)
        search_time = getattr(result, 'search_time', 0.0)
        
        # Format response
        response = {
            'success': True,
            'hint': {
                'best_move': format_move(result.best_move) if result.best_move else None,
                'expected_value': result.best_score,
                'confidence': min(1.0, result.nodes_searched / 100.0),  # Simple confidence based on nodes
                'search_time': search_time,
                'rollouts_performed': result.rollout_count,
                'top_moves': [
                    {
                        'move': format_move(result.best_move),
                        'score': result.best_score,
                        'visits': result.nodes_searched
                    }
                ] if result.best_move else []
            },
            'position': {
                'fen_string': hint_req.fen_string,
                'agent_id': hint_req.agent_id
            }
        }
        
        return jsonify(response)
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid position', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Hint generation failed', 'message': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
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


@api_bp.route('/stats', methods=['GET'])
@require_session
def get_api_stats():
    """Get API usage statistics."""
    session_id = request.headers.get('X-Session-ID')
    
    return jsonify({
        'rate_limits': current_app.rate_limiter.get_remaining_requests(session_id),
        'session_stats': current_app.session_manager.get_session_stats() if hasattr(current_app, 'session_manager') else {}
    }) 


@api_bp.route('/analyze_neural', methods=['POST'])
@require_session
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
        
        # Create neural MCTS
        from core.azul_mcts import AzulMCTS, RolloutPolicy
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
        if hasattr(current_app, 'database'):
            position_id = current_app.database.cache_position(fen_string, len(state.agents))
            current_app.database.cache_analysis(position_id, agent_id, 'neural_mcts', analysis)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 