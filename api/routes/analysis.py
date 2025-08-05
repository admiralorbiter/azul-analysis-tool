"""
Analysis API Routes

This module contains all analysis-related endpoints for the Azul Solver & Analysis Toolkit.
"""

import json
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from ..auth import require_session
from ..models import AnalysisRequest, HintRequest, AnalysisCacheRequest, AnalysisSearchRequest
from ..utils import parse_fen_string, format_move

# Create Flask blueprint for analysis endpoints
analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analyses/<path:fen_string>', methods=['GET'])
@require_session
def get_analysis(fen_string: str):
    """
    Get cached analysis results for a position.
    
    GET /api/v1/analyses/{fen_string}?agent_id=0&search_type=mcts
    
    Returns:
        Cached analysis results with metadata
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Analysis cache is disabled'
            }), 503
        
        # Get query parameters
        agent_id = request.args.get('agent_id', 0, type=int)
        search_type = request.args.get('search_type', 'mcts')
        
        # Get cached analysis
        cached_analysis = current_app.database.get_cached_analysis(
            fen_string, agent_id, search_type
        )
        
        if cached_analysis is None:
            return jsonify({
                'error': 'Analysis not found',
                'message': f'No {search_type} analysis found for position {fen_string}'
            }), 404
        
        return jsonify({
            'analysis_id': cached_analysis.position_id,
            'fen_string': fen_string,
            'agent_id': cached_analysis.agent_id,
            'search_type': cached_analysis.search_type,
            'best_move': cached_analysis.best_move,
            'best_score': cached_analysis.score,
            'search_time': cached_analysis.search_time,
            'nodes_searched': cached_analysis.nodes_searched,
            'rollout_count': cached_analysis.rollout_count,
            'created_at': cached_analysis.created_at.isoformat(),
            'principal_variation': cached_analysis.principal_variation,
            'cache_hit': True
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting analysis for {fen_string}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve analysis data'
        }), 500


@analysis_bp.route('/analyses/<path:fen_string>', methods=['POST'])
@require_session
def store_analysis(fen_string: str):
    """
    Store analysis results in cache.
    
    POST /api/v1/analyses/{fen_string}
    {
        "agent_id": 0,
        "search_type": "mcts",
        "best_move": "move_string",
        "best_score": 0.5,
        "search_time": 0.2,
        "nodes_searched": 1000,
        "rollout_count": 50,
        "depth_reached": 3,
        "principal_variation": ["move1", "move2"],
        "metadata": {"source": "api", "parameters": {...}}
    }
    
    Returns:
        Analysis ID and cache status
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Analysis cache is disabled'
            }), 503
        
        # Parse request data
        try:
            data = request.get_json(force=True)
        except Exception:
            data = None
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate request
        try:
            analysis_req = AnalysisCacheRequest(fen_string=fen_string, **data)
        except ValidationError as e:
            return jsonify({
                'error': 'Validation error',
                'message': str(e)
            }), 400
        
        # Cache position first
        position_id = current_app.database.cache_position(
            fen_string, 2  # Default to 2 players, could be made configurable
        )
        
        # Prepare analysis result
        analysis_result = {
            'best_move': analysis_req.best_move,
            'best_score': analysis_req.best_score,
            'search_time': analysis_req.search_time,
            'nodes_searched': analysis_req.nodes_searched,
            'rollout_count': analysis_req.rollout_count,
            'principal_variation': analysis_req.principal_variation or []
        }
        
        # Store analysis
        analysis_id = current_app.database.cache_analysis(
            position_id,
            analysis_req.agent_id,
            analysis_req.search_type,
            analysis_result
        )
        
        # Store metadata if provided
        if analysis_req.metadata:
            current_app.logger.info(f"Metadata for analysis {analysis_id}: {analysis_req.metadata}")
        
        return jsonify({
            'analysis_id': analysis_id,
            'position_id': position_id,
            'fen_string': fen_string,
            'agent_id': analysis_req.agent_id,
            'search_type': analysis_req.search_type,
            'cached': True,
            'message': 'Analysis cached successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error caching analysis for {fen_string}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to cache analysis'
        }), 500


@analysis_bp.route('/analyses/<path:fen_string>', methods=['DELETE'])
@require_session
def delete_analysis(fen_string: str):
    """
    Delete analysis results from cache.
    
    DELETE /api/v1/analyses/{fen_string}?agent_id=0&search_type=mcts
    
    Returns:
        Deletion status
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Analysis cache is disabled'
            }), 503
        
        # Get query parameters
        agent_id = request.args.get('agent_id', 0, type=int)
        search_type = request.args.get('search_type', 'mcts')
        
        # Get position ID
        position_id = current_app.database.get_position_id(fen_string)
        if position_id is None:
            return jsonify({
                'error': 'Position not found',
                'message': f'Position {fen_string} not in cache'
            }), 404
        
        # Delete specific analysis
        with current_app.database.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM analysis_results 
                WHERE position_id = ? AND agent_id = ? AND search_type = ?
            """, (position_id, agent_id, search_type))
            
            deleted_count = cursor.rowcount
            conn.commit()
        
        if deleted_count == 0:
            return jsonify({
                'error': 'Analysis not found',
                'message': f'No {search_type} analysis found for position {fen_string}'
            }), 404
        
        return jsonify({
            'deleted': True,
            'fen_string': fen_string,
            'agent_id': agent_id,
            'search_type': search_type,
            'deleted_count': deleted_count,
            'message': f'Analysis deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting analysis for {fen_string}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to delete analysis'
        }), 500


@analysis_bp.route('/analyses/stats', methods=['GET'])
@require_session
def get_analysis_stats():
    """
    Get analysis cache statistics.
    
    GET /api/v1/analyses/stats
    
    Returns:
        Analysis cache statistics and performance metrics
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Analysis cache is disabled'
            }), 503
        
        # Get cache statistics
        stats = current_app.database.get_cache_stats()
        
        # Get query performance stats
        query_stats = current_app.database.get_query_performance_stats()
        
        # Get index usage stats
        index_stats = current_app.database.get_index_usage_stats()
        
        return jsonify({
            'analyses_cached': stats['analyses_cached'],
            'by_search_type': stats['by_search_type'],
            'performance': stats['performance'],
            'query_performance': query_stats,
            'index_usage': index_stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting analysis stats: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve analysis statistics'
        }), 500


@analysis_bp.route('/analyses/search', methods=['GET'])
@require_session
def search_analyses():
    """
    Search analyses by criteria.
    
    GET /api/v1/analyses/search?search_type=mcts&min_score=0.5&limit=50
    
    Returns:
        Matching analyses with metadata
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Analysis cache is disabled'
            }), 503
        
        # Get query parameters
        search_type = request.args.get('search_type')
        agent_id = request.args.get('agent_id', type=int)
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit > 200:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'Limit cannot exceed 200'
            }), 400
        
        # Build query conditions
        conditions = []
        params = []
        
        if search_type:
            conditions.append("ar.search_type = ?")
            params.append(search_type)
        
        if agent_id is not None:
            conditions.append("ar.agent_id = ?")
            params.append(agent_id)
        
        if min_score is not None:
            conditions.append("ar.score >= ?")
            params.append(min_score)
        
        if max_score is not None:
            conditions.append("ar.score <= ?")
            params.append(max_score)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Search analyses
        with current_app.database.get_connection() as conn:
            query = f"""
                SELECT ar.*, p.fen_string 
                FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                WHERE {where_clause}
                ORDER BY ar.created_at DESC
                LIMIT ? OFFSET ?
            """
            
            cursor = conn.execute(query, params + [limit, offset])
            
            analyses = []
            for row in cursor.fetchall():
                # Get principal variation
                pv_cursor = conn.execute("""
                    SELECT move_text FROM move_sequences 
                    WHERE analysis_id = ? ORDER BY move_order
                """, (row['id'],))
                
                principal_variation = [move_row['move_text'] for move_row in pv_cursor.fetchall()]
                
                analyses.append({
                    'analysis_id': row['id'],
                    'position_id': row['position_id'],
                    'fen_string': row['fen_string'],
                    'agent_id': row['agent_id'],
                    'search_type': row['search_type'],
                    'best_move': row['best_move'],
                    'best_score': row['score'],
                    'search_time': row['search_time'],
                    'nodes_searched': row['nodes_searched'],
                    'rollout_count': row['rollout_count'],
                    'created_at': row['created_at'],
                    'principal_variation': principal_variation
                })
            
            # Get total count for this query
            count_query = f"""
                SELECT COUNT(*) as total 
                FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                WHERE {where_clause}
            """
            
            count_cursor = conn.execute(count_query, params)
            total_count = count_cursor.fetchone()['total']
        
        return jsonify({
            'search': True,
            'analyses': analyses,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'returned_count': len(analyses),
            'filters': {
                'search_type': search_type,
                'agent_id': agent_id,
                'min_score': min_score,
                'max_score': max_score
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in analysis search: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to search analyses'
        }), 500


@analysis_bp.route('/analyses/recent', methods=['GET'])
@require_session
def get_recent_analyses():
    """
    Get recent analysis results.
    
    GET /api/v1/analyses/recent?limit=20&search_type=mcts
    
    Returns:
        Recent analyses with metadata
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Analysis cache is disabled'
            }), 503
        
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        search_type = request.args.get('search_type')
        
        # Validate parameters
        if limit > 100:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'Limit cannot exceed 100'
            }), 400
        
        # Get recent analyses
        recent_analyses = current_app.database.get_recent_analyses(limit)
        
        # Filter by search type if specified
        if search_type:
            recent_analyses = [a for a in recent_analyses if a.search_type == search_type]
        
        # Format response
        analyses = []
        for analysis in recent_analyses:
            analyses.append({
                'analysis_id': analysis.position_id,  # Using position_id as analysis_id for now
                'fen_string': 'unknown',  # Would need to get from positions table
                'agent_id': analysis.agent_id,
                'search_type': analysis.search_type,
                'best_move': analysis.best_move,
                'best_score': analysis.score,
                'search_time': analysis.search_time,
                'nodes_searched': analysis.nodes_searched,
                'rollout_count': analysis.rollout_count,
                'created_at': analysis.created_at.isoformat(),
                'principal_variation': analysis.principal_variation
            })
        
        return jsonify({
            'recent_analyses': True,
            'analyses': analyses,
            'limit': limit,
            'search_type_filter': search_type,
            'returned_count': len(analyses)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent analyses: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve recent analyses'
        }), 500


@analysis_bp.route('/analyze', methods=['POST'])
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
        # Check rate limiting
        session_id = request.headers.get('X-Session-ID')
        if current_app.rate_limiter and not current_app.rate_limiter.check_rate_limit(session_id, "heavy"):
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
        
        # If parsing failed, fall back to initial state for resilience
        if state is None:
            state = parse_fen_string("initial")
            if state is None:
                return jsonify({'error': 'Failed to create initial game state'}), 500
        
        # Import search components
        from analysis_engine.mathematical_optimization.azul_search import AzulAlphaBetaSearch
        
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
        if hasattr(current_app, 'database') and current_app.database:
            try:
                position_id = current_app.database.cache_position(analysis_req.fen_string, len(state.agents))
                current_app.database.cache_analysis(position_id, analysis_req.agent_id, 'alpha_beta', {
                    'best_move': str(result.best_move) if result.best_move else None,
                    'best_score': result.best_score,
                    'search_time': result.search_time,
                    'nodes_searched': result.nodes_searched,
                    'depth_reached': result.depth_reached,
                    'principal_variation': [str(move) for move in result.principal_variation]
                })
            except Exception as e:
                current_app.logger.warning(f"Failed to cache analysis: {e}")
        
        return jsonify(response)
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid position', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500


@analysis_bp.route('/hint', methods=['POST'])
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
        # Skip rate limiting for local development
        # session_id = request.headers.get('X-Session-ID')
        # if current_app.rate_limiter and not current_app.rate_limiter.check_rate_limit(session_id, "light"):
        #     return jsonify({
        #         'error': 'Rate limit exceeded',
        #         'message': 'Too many hint requests'
        #     }), 429
        
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        hint_req = HintRequest(**data)
        
        # Parse game state
        state = parse_fen_string(hint_req.fen_string)
        
        # Import MCTS components
        from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS
        
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
        
        # Cache result if database is available
        if hasattr(current_app, 'database') and current_app.database:
            try:
                position_id = current_app.database.cache_position(
                    hint_req.fen_string, 
                    len(state.agents)
                )
                current_app.database.cache_analysis(
                    position_id,
                    hint_req.agent_id,
                    'mcts',
                    {
                        'best_move': str(result.best_move) if result.best_move else None,
                        'best_score': result.best_score,
                        'search_time': search_time,
                        'nodes_searched': result.nodes_searched,
                        'rollout_count': result.rollout_count,
                        'principal_variation': [str(move) for move in result.principal_variation]
                    }
                )
                
                # Update performance stats
                current_app.database.update_performance_stats(
                    'mcts', search_time, result.nodes_searched, result.rollout_count, False
                )
            except Exception as e:
                # Log but don't fail the request
                current_app.logger.warning(f"Failed to cache hint: {e}")
        
        return jsonify(response)
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid position', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Hint generation failed', 'message': str(e)}), 500 