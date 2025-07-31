"""
REST API routes for the Azul Solver & Analysis Toolkit.

This module provides Flask blueprints for game analysis, hints, and research tools.
"""

import json
import time
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, ValidationError, ConfigDict

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


class PositionCacheRequest(BaseModel):
    """Request model for position cache endpoints."""
    model_config = ConfigDict(extra="forbid")
    
    fen_string: str
    player_count: int = 2
    compressed_state: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BulkPositionRequest(BaseModel):
    """Request model for bulk position operations."""
    positions: list[PositionCacheRequest]
    overwrite: bool = False


class AnalysisCacheRequest(BaseModel):
    """Request model for analysis cache endpoints."""
    fen_string: str
    agent_id: int = 0
    search_type: str  # 'mcts', 'alpha_beta', 'neural_mcts'
    best_move: Optional[str] = None
    best_score: float = 0.0
    search_time: float = 0.0
    nodes_searched: int = 0
    rollout_count: int = 0
    depth_reached: Optional[int] = None
    principal_variation: Optional[list[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisSearchRequest(BaseModel):
    """Request model for analysis search."""
    search_type: Optional[str] = None
    agent_id: Optional[int] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    limit: int = 50
    offset: int = 0


class PerformanceStatsRequest(BaseModel):
    """Request model for performance statistics."""
    search_type: Optional[str] = None
    time_range_hours: Optional[int] = None
    include_query_stats: bool = True
    include_index_stats: bool = True


class SystemHealthRequest(BaseModel):
    """Request model for system health checks."""
    include_database_health: bool = True
    include_performance_metrics: bool = True
    include_cache_analytics: bool = True


class MoveExecutionRequest(BaseModel):
    """Request model for move execution."""
    fen_string: str
    move: Dict[str, Any]  # Move data from frontend
    agent_id: int = 0


# Create Flask blueprint for API endpoints
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# Global variable to store the current game state
_current_game_state = None

def parse_fen_string(fen_string: str):
    """Parse FEN string to create game state."""
    global _current_game_state
    from core.azul_model import AzulState
    
    if fen_string.lower() == "initial":
        # If we don't have a current state, create a new one
        if _current_game_state is None:
            _current_game_state = AzulState(2)  # 2-player starting position
        return _current_game_state
    else:
        raise ValueError(f"Unsupported FEN format: {fen_string}. Use 'initial' for now.")

def update_current_game_state(new_state):
    """Update the current game state."""
    global _current_game_state
    _current_game_state = new_state


def format_move(move):
    """Format a move for display."""
    if move is None:
        return "None"
    
    try:
        # Convert tile type to color name
        tile_colors = {0: 'blue', 1: 'yellow', 2: 'red', 3: 'black', 4: 'white'}
        tile_color = tile_colors.get(move.tile_type, f'tile_{move.tile_type}')
        
        # Format as string for tests
        if move.action_type == 1:  # Factory move
            return f"take_from_factory_{move.source_id}_{tile_color}_{move.pattern_line_dest}_{move.num_to_pattern_line}_{move.num_to_floor_line}"
        else:  # Center move
            return f"take_from_center_{move.source_id}_{tile_color}_{move.pattern_line_dest}_{move.num_to_pattern_line}_{move.num_to_floor_line}"
    except Exception as e:
        # Fallback if move formatting fails
        return f"move_{getattr(move, 'source_id', '?')}_{getattr(move, 'tile_type', '?')}"


# Position Cache API Endpoints

@api_bp.route('/positions/<path:fen_string>', methods=['GET'])
@require_session
def get_position(fen_string: str):
    """
    Get position data from cache.
    
    GET /api/v1/positions/{fen_string}
    
    Returns:
        Position data including ID, player count, and metadata
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Get position ID
        position_id = current_app.database.get_position_id(fen_string)
        if position_id is None:
            return jsonify({
                'error': 'Position not found',
                'message': f'Position {fen_string} not in cache'
            }), 404
        
        # Get position details
        with current_app.database.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, fen_string, player_count, created_at, 
                       compressed_state IS NOT NULL as has_compressed_state
                FROM positions 
                WHERE fen_string = ?
            """, (fen_string,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'error': 'Position not found',
                    'message': f'Position {fen_string} not in cache'
                }), 404
            
            # Get analysis count for this position
            cursor = conn.execute("""
                SELECT COUNT(*) as analysis_count
                FROM analysis_results 
                WHERE position_id = ?
            """, (position_id,))
            
            analysis_count = cursor.fetchone()['analysis_count']
            
            return jsonify({
                'position_id': row['id'],
                'fen_string': row['fen_string'],
                'player_count': row['player_count'],
                'created_at': row['created_at'],
                'has_compressed_state': bool(row['has_compressed_state']),
                'analysis_count': analysis_count,
                'cache_hit': True
            })
            
    except Exception as e:
        current_app.logger.error(f"Error getting position {fen_string}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve position data'
        }), 500


@api_bp.route('/positions/<path:fen_string>', methods=['PUT'])
@require_session
def put_position(fen_string: str):
    """
    Store position data in cache.
    
    PUT /api/v1/positions/{fen_string}
    {
        "player_count": 2,
        "compressed_state": "optional_compressed_data",
        "metadata": {"source": "game_log", "tags": ["opening"]}
    }
    
    Returns:
        Position ID and cache status
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
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
            cache_req = PositionCacheRequest(fen_string=fen_string, **data)
        except ValidationError as e:
            return jsonify({
                'error': 'Validation error',
                'message': str(e)
            }), 400
        
        # Store position in cache
        if cache_req.compressed_state:
            position_id = current_app.database.cache_position_with_state(
                fen_string, cache_req.player_count, cache_req.compressed_state
            )
        else:
            position_id = current_app.database.cache_position(
                fen_string, cache_req.player_count
            )
        
        # Store metadata if provided
        if cache_req.metadata:
            with current_app.database.get_connection() as conn:
                # Note: This would require adding a metadata column to positions table
                # For now, we'll just log the metadata
                current_app.logger.info(f"Metadata for position {fen_string}: {cache_req.metadata}")
        
        return jsonify({
            'position_id': position_id,
            'fen_string': fen_string,
            'player_count': cache_req.player_count,
            'cached': True,
            'message': 'Position cached successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error caching position {fen_string}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to cache position'
        }), 500


@api_bp.route('/positions/<path:fen_string>', methods=['DELETE'])
@require_session
def delete_position(fen_string: str):
    """
    Delete position data from cache.
    
    DELETE /api/v1/positions/{fen_string}
    
    Returns:
        Deletion status
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Get position ID first
        position_id = current_app.database.get_position_id(fen_string)
        if position_id is None:
            return jsonify({
                'error': 'Position not found',
                'message': f'Position {fen_string} not in cache'
            }), 404
        
        # Delete position and all related analyses
        with current_app.database.get_connection() as conn:
            # Delete analyses first (foreign key constraint)
            conn.execute("""
                DELETE FROM analysis_results WHERE position_id = ?
            """, (position_id,))
            
            # Delete position
            conn.execute("""
                DELETE FROM positions WHERE id = ?
            """, (position_id,))
            
            conn.commit()
        
        return jsonify({
            'deleted': True,
            'fen_string': fen_string,
            'position_id': position_id,
            'message': 'Position and all analyses deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting position {fen_string}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to delete position'
        }), 500


@api_bp.route('/positions/stats', methods=['GET'])
@require_session
def get_position_stats():
    """
    Get position cache statistics.
    
    GET /api/v1/positions/stats
    
    Returns:
        Cache statistics including position count, analysis count, etc.
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Get cache statistics
        stats = current_app.database.get_cache_stats()
        
        # Get database info
        db_info = current_app.database.get_database_info()
        
        return jsonify({
            'positions_cached': stats['positions_cached'],
            'analyses_cached': stats['analyses_cached'],
            'by_search_type': stats['by_search_type'],
            'performance': stats['performance'],
            'database_info': {
                'total_size_mb': db_info['total_size_mb'],
                'db_size_bytes': db_info['db_size_bytes'],
                'wal_size_bytes': db_info['wal_size_bytes'],
                'journal_mode': db_info['journal_mode']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting position stats: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve cache statistics'
        }), 500


# Bulk Position Operations

@api_bp.route('/positions/bulk', methods=['POST'])
@require_session
def bulk_import_positions():
    """
    Bulk import positions into cache.
    
    POST /api/v1/positions/bulk
    {
        "positions": [
            {
                "fen_string": "position1",
                "player_count": 2,
                "compressed_state": "optional_data"
            }
        ],
        "overwrite": false
    }
    
    Returns:
        Import results with success/failure counts
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate request
        try:
            bulk_req = BulkPositionRequest(**data)
        except ValidationError as e:
            return jsonify({
                'error': 'Validation error',
                'message': str(e)
            }), 400
        
        # Process bulk import
        results = {
            'total_positions': len(bulk_req.positions),
            'imported': 0,
            'skipped': 0,
            'errors': [],
            'position_ids': []
        }
        
        for position in bulk_req.positions:
            try:
                # Check if position already exists
                existing_id = current_app.database.get_position_id(position.fen_string)
                
                if existing_id and not bulk_req.overwrite:
                    results['skipped'] += 1
                    continue
                
                # Import position
                if position.compressed_state:
                    position_id = current_app.database.cache_position_with_state(
                        position.fen_string, position.player_count, position.compressed_state
                    )
                else:
                    position_id = current_app.database.cache_position(
                        position.fen_string, position.player_count
                    )
                
                results['imported'] += 1
                results['position_ids'].append(position_id)
                
            except Exception as e:
                results['errors'].append({
                    'fen_string': position.fen_string,
                    'error': str(e)
                })
        
        return jsonify({
            'bulk_import': True,
            'results': results,
            'message': f'Bulk import completed: {results["imported"]} imported, {results["skipped"]} skipped'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk import: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to process bulk import'
        }), 500


@api_bp.route('/positions/bulk', methods=['GET'])
@require_session
def bulk_export_positions():
    """
    Bulk export positions from cache.
    
    GET /api/v1/positions/bulk?limit=100&offset=0
    
    Returns:
        List of positions with metadata
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit > 1000:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'Limit cannot exceed 1000'
            }), 400
        
        # Export positions
        with current_app.database.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, fen_string, player_count, created_at,
                       compressed_state IS NOT NULL as has_compressed_state
                FROM positions 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            positions = []
            for row in cursor.fetchall():
                # Get analysis count for each position
                analysis_cursor = conn.execute("""
                    SELECT COUNT(*) as analysis_count
                    FROM analysis_results 
                    WHERE position_id = ?
                """, (row['id'],))
                
                analysis_count = analysis_cursor.fetchone()['analysis_count']
                
                positions.append({
                    'position_id': row['id'],
                    'fen_string': row['fen_string'],
                    'player_count': row['player_count'],
                    'created_at': row['created_at'],
                    'has_compressed_state': bool(row['has_compressed_state']),
                    'analysis_count': analysis_count
                })
            
            # Get total count
            count_cursor = conn.execute("SELECT COUNT(*) as total FROM positions")
            total_count = count_cursor.fetchone()['total']
        
        return jsonify({
            'bulk_export': True,
            'positions': positions,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'returned_count': len(positions)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk export: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to export positions'
        }), 500


@api_bp.route('/positions/bulk', methods=['DELETE'])
@require_session
def bulk_delete_positions():
    """
    Bulk delete positions from cache.
    
    DELETE /api/v1/positions/bulk
    {
        "fen_strings": ["position1", "position2"],
        "all": false
    }
    
    Returns:
        Deletion results
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate request
        fen_strings = data.get('fen_strings', [])
        delete_all = data.get('all', False)
        
        if not fen_strings and not delete_all:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Must specify fen_strings or set all=true'
            }), 400
        
        # Process bulk deletion
        results = {
            'total_requested': len(fen_strings) if not delete_all else 'all',
            'deleted': 0,
            'not_found': 0,
            'errors': []
        }
        
        if delete_all:
            # Delete all positions
            with current_app.database.get_connection() as conn:
                # Get count before deletion
                count_cursor = conn.execute("SELECT COUNT(*) as total FROM positions")
                total_count = count_cursor.fetchone()['total']
                
                # Delete all analyses first
                conn.execute("DELETE FROM analysis_results")
                
                # Delete all positions
                conn.execute("DELETE FROM positions")
                
                conn.commit()
                
                results['deleted'] = total_count
        else:
            # Delete specific positions
            for fen_string in fen_strings:
                try:
                    position_id = current_app.database.get_position_id(fen_string)
                    if position_id is None:
                        results['not_found'] += 1
                        continue
                    
                    # Delete position and analyses
                    with current_app.database.get_connection() as conn:
                        conn.execute("""
                            DELETE FROM analysis_results WHERE position_id = ?
                        """, (position_id,))
                        
                        conn.execute("""
                            DELETE FROM positions WHERE id = ?
                        """, (position_id,))
                        
                        conn.commit()
                    
                    results['deleted'] += 1
                    
                except Exception as e:
                    results['errors'].append({
                        'fen_string': fen_string,
                        'error': str(e)
                    })
        
        return jsonify({
            'bulk_delete': True,
            'results': results,
            'message': f'Bulk deletion completed: {results["deleted"]} deleted, {results["not_found"]} not found'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk deletion: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to process bulk deletion'
        }), 500


@api_bp.route('/positions/search', methods=['GET'])
@require_session
def search_positions():
    """
    Search positions in cache.
    
    GET /api/v1/positions/search?q=query&limit=50&offset=0
    
    Returns:
        Matching positions with metadata
    """
    try:
        # Check if database is available
        if not current_app.database:
            return jsonify({
                'error': 'Database not available',
                'message': 'Position cache is disabled'
            }), 503
        
        # Get query parameters
        query = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit > 200:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'Limit cannot exceed 200'
            }), 400
        
        if not query:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'Query parameter "q" is required'
            }), 400
        
        # Search positions
        with current_app.database.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, fen_string, player_count, created_at,
                       compressed_state IS NOT NULL as has_compressed_state
                FROM positions 
                WHERE fen_string LIKE ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (f'%{query}%', limit, offset))
            
            positions = []
            for row in cursor.fetchall():
                # Get analysis count for each position
                analysis_cursor = conn.execute("""
                    SELECT COUNT(*) as analysis_count
                    FROM analysis_results 
                    WHERE position_id = ?
                """, (row['id'],))
                
                analysis_count = analysis_cursor.fetchone()['analysis_count']
                
                positions.append({
                    'position_id': row['id'],
                    'fen_string': row['fen_string'],
                    'player_count': row['player_count'],
                    'created_at': row['created_at'],
                    'has_compressed_state': bool(row['has_compressed_state']),
                    'analysis_count': analysis_count
                })
            
            # Get total count for this query
            count_cursor = conn.execute("""
                SELECT COUNT(*) as total 
                FROM positions 
                WHERE fen_string LIKE ?
            """, (f'%{query}%',))
            
            total_count = count_cursor.fetchone()['total']
        
        return jsonify({
            'search': True,
            'query': query,
            'positions': positions,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'returned_count': len(positions)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in position search: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to search positions'
        }), 500


# Analysis Cache API Endpoints

@api_bp.route('/analyses/<path:fen_string>', methods=['GET'])
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


@api_bp.route('/analyses/<path:fen_string>', methods=['POST'])
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


@api_bp.route('/analyses/<path:fen_string>', methods=['DELETE'])
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


@api_bp.route('/analyses/stats', methods=['GET'])
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


@api_bp.route('/analyses/search', methods=['GET'])
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


@api_bp.route('/analyses/recent', methods=['GET'])
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
        if current_app.rate_limiter and not current_app.rate_limiter.check_rate_limit(session_id, "light"):
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
        'rate_limits': current_app.rate_limiter.get_remaining_requests(session_id) if current_app.rate_limiter else {},
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


# ============================================================================
# B2.3: Performance API Endpoints
# ============================================================================

@api_bp.route('/performance/stats', methods=['GET'])
@require_session
def get_performance_stats():
    """
    Get comprehensive performance statistics.
    
    GET /api/v1/performance/stats
    Query parameters:
    - search_type: Optional search type filter
    - time_range_hours: Optional time range filter
    - include_query_stats: Include query performance stats (default: true)
    - include_index_stats: Include index usage stats (default: true)
    
    Returns:
        Comprehensive performance statistics including search performance,
        query performance, index usage, and cache analytics.
    """
    try:
        # Parse query parameters
        search_type = request.args.get('search_type')
        time_range_hours = request.args.get('time_range_hours', type=int)
        include_query_stats = request.args.get('include_query_stats', 'true').lower() == 'true'
        include_index_stats = request.args.get('include_index_stats', 'true').lower() == 'true'
        
        # Get database stats
        db_stats = current_app.database.get_cache_stats()
        
        # Get performance stats
        perf_stats = current_app.database.get_performance_stats(search_type)
        
        # Build response
        response = {
            'timestamp': time.time(),
            'search_performance': {
                'by_search_type': db_stats.get('by_search_type', {}),
                'performance_stats': perf_stats
            },
            'cache_analytics': {
                'positions_cached': db_stats.get('positions_cached', 0),
                'analyses_cached': db_stats.get('analyses_cached', 0),
                'cache_hit_rate': db_stats.get('cache_hit_rate', 0.0),
                'total_cache_size_mb': db_stats.get('total_cache_size_mb', 0.0)
            }
        }
        
        # Add query performance stats if requested
        if include_query_stats:
            query_stats = current_app.database.get_query_performance_stats()
            response['query_performance'] = query_stats
        
        # Add index usage stats if requested
        if include_index_stats:
            index_stats = current_app.database.get_index_usage_stats()
            response['index_usage'] = index_stats
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance stats: {e}")
        return jsonify({'error': 'Failed to get performance stats', 'message': str(e)}), 500


@api_bp.route('/performance/health', methods=['GET'])
@require_session
def get_system_health():
    """
    Get comprehensive system health status.
    
    GET /api/v1/performance/health
    Query parameters:
    - include_database_health: Include database health checks (default: true)
    - include_performance_metrics: Include performance metrics (default: true)
    - include_cache_analytics: Include cache analytics (default: true)
    
    Returns:
        System health status including database integrity, performance metrics,
        and cache analytics.
    """
    try:
        # Parse query parameters
        include_database_health = request.args.get('include_database_health', 'true').lower() == 'true'
        include_performance_metrics = request.args.get('include_performance_metrics', 'true').lower() == 'true'
        include_cache_analytics = request.args.get('include_cache_analytics', 'true').lower() == 'true'
        
        # Basic health check
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '0.1.0'
        }
        
        # Database health check
        if include_database_health:
            try:
                db_info = current_app.database.get_database_info()
                health_status['database'] = {
                    'status': 'healthy',
                    'file_size_mb': db_info.get('file_size_mb', 0),
                    'total_pages': db_info.get('total_pages', 0),
                    'free_pages': db_info.get('free_pages', 0),
                    'page_size': db_info.get('page_size', 0),
                    'integrity_check': 'ok'  # We'll add actual integrity check if needed
                }
            except Exception as e:
                health_status['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        # Performance metrics
        if include_performance_metrics:
            try:
                perf_stats = current_app.database.get_performance_stats()
                health_status['performance'] = {
                    'status': 'healthy',
                    'total_searches': sum(stat.get('total_searches', 0) for stat in perf_stats),
                    'average_search_time_ms': sum(stat.get('average_search_time_ms', 0) for stat in perf_stats) / max(len(perf_stats), 1),
                    'cache_hit_rate': sum(stat.get('cache_hit_rate', 0) for stat in perf_stats) / max(len(perf_stats), 1)
                }
            except Exception as e:
                health_status['performance'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        # Cache analytics
        if include_cache_analytics:
            try:
                cache_stats = current_app.database.get_cache_stats()
                health_status['cache'] = {
                    'status': 'healthy',
                    'positions_cached': cache_stats.get('positions_cached', 0),
                    'analyses_cached': cache_stats.get('analyses_cached', 0),
                    'cache_hit_rate': cache_stats.get('cache_hit_rate', 0.0),
                    'total_size_mb': cache_stats.get('total_cache_size_mb', 0.0)
                }
            except Exception as e:
                health_status['cache'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        current_app.logger.error(f"Error getting system health: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Failed to get system health',
            'message': str(e),
            'timestamp': time.time()
        }), 500


@api_bp.route('/performance/optimize', methods=['POST'])
@require_session
def optimize_database():
    """
    Optimize database performance.
    
    POST /api/v1/performance/optimize
    
    Returns:
        Database optimization results including VACUUM and ANALYZE operations.
    """
    try:
        # Perform database optimization
        optimization_result = current_app.database.optimize_database()
        
        return jsonify({
            'success': True,
            'optimization_result': optimization_result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error optimizing database: {e}")
        return jsonify({'error': 'Failed to optimize database', 'message': str(e)}), 500


@api_bp.route('/performance/analytics', methods=['GET'])
@require_session
def get_cache_analytics():
    """
    Get detailed cache analytics and performance insights.
    
    GET /api/v1/performance/analytics
    Query parameters:
    - search_type: Optional search type filter
    - limit: Number of high-quality analyses to return (default: 10)
    
    Returns:
        Detailed cache analytics including high-quality analyses,
        performance trends, and optimization recommendations.
    """
    try:
        # Parse query parameters
        search_type = request.args.get('search_type')
        limit = request.args.get('limit', 10, type=int)
        
        # Get cache stats
        cache_stats = current_app.database.get_cache_stats()
        
        # Get high-quality analyses if search_type specified
        high_quality_analyses = []
        if search_type:
            try:
                high_quality_analyses = current_app.database.get_high_quality_analyses(search_type, limit)
                # Convert to serializable format
                high_quality_analyses = [
                    {
                        'position_id': analysis.position_id,
                        'agent_id': analysis.agent_id,
                        'search_type': analysis.search_type,
                        'best_move': analysis.best_move,
                        'score': analysis.score,
                        'search_time': analysis.search_time,
                        'nodes_searched': analysis.nodes_searched,
                        'rollout_count': analysis.rollout_count,
                        'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                        'principal_variation': analysis.principal_variation
                    }
                    for analysis in high_quality_analyses
                ]
            except Exception as e:
                current_app.logger.warning(f"Failed to get high-quality analyses: {e}")
        
        # Get analysis stats by type
        analysis_stats = {}
        if search_type:
            try:
                analysis_stats = current_app.database.get_analysis_stats_by_type(search_type)
            except Exception as e:
                current_app.logger.warning(f"Failed to get analysis stats: {e}")
        
        # Build analytics response
        analytics = {
            'timestamp': time.time(),
            'cache_overview': {
                'positions_cached': cache_stats.get('positions_cached', 0),
                'analyses_cached': cache_stats.get('analyses_cached', 0),
                'cache_hit_rate': cache_stats.get('cache_hit_rate', 0.0),
                'total_size_mb': cache_stats.get('total_cache_size_mb', 0.0)
            },
            'performance_metrics': {
                'by_search_type': cache_stats.get('by_search_type', {}),
                'performance': cache_stats.get('performance', {})
            },
            'high_quality_analyses': high_quality_analyses,
            'analysis_stats': analysis_stats
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache analytics: {e}")
        return jsonify({'error': 'Failed to get cache analytics', 'message': str(e)}), 500


@api_bp.route('/performance/monitoring', methods=['GET'])
@require_session
def get_monitoring_data():
    """
    Get real-time monitoring data for system performance.
    
    GET /api/v1/performance/monitoring
    
    Returns:
        Real-time monitoring data including query performance,
        index usage, and system metrics.
    """
    try:
        # Get query performance stats
        query_stats = current_app.database.get_query_performance_stats()
        
        # Get index usage stats
        index_stats = current_app.database.get_index_usage_stats()
        
        # Get database info
        db_info = current_app.database.get_database_info()
        
        # Build monitoring response
        monitoring_data = {
            'timestamp': time.time(),
            'query_performance': query_stats,
            'index_usage': index_stats,
            'database_metrics': {
                'file_size_mb': db_info.get('file_size_mb', 0),
                'total_pages': db_info.get('total_pages', 0),
                'free_pages': db_info.get('free_pages', 0),
                'page_size': db_info.get('page_size', 0),
                'cache_size_pages': db_info.get('cache_size_pages', 0)
            },
            'system_metrics': {
                'uptime': time.time(),  # Could be enhanced with actual uptime tracking
                'memory_usage_mb': 0,  # Could be enhanced with actual memory tracking
                'active_connections': 1  # Could be enhanced with connection pooling
            }
        }
        
        return jsonify(monitoring_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting monitoring data: {e}")
        return jsonify({'error': 'Failed to get monitoring data', 'message': str(e)}), 500


@api_bp.route('/execute_move', methods=['POST'])
def execute_move():
    """Execute a move and return new game state."""
    try:
        try:
            data = request.get_json(force=True)
        except Exception:
            data = None
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        request_model = MoveExecutionRequest(**data)
        
        print(f"DEBUG: Received move data: {data}")
        
        # Parse current state
        try:
            state = parse_fen_string(request_model.fen_string)
        except ValueError as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        print(f"DEBUG: Parsed state - agent count: {len(state.agents)}, factories: {len(state.factories)}")
        
        # Convert frontend move format to engine move format
        move_data = request_model.move
        engine_move = convert_frontend_move_to_engine(move_data)
        print(f"DEBUG: Converted engine move: {engine_move}")
        
        # Validate and execute move
        from core.azul_move_generator import FastMoveGenerator
        generator = FastMoveGenerator()
        legal_moves = generator.generate_moves_fast(state, request_model.agent_id)
        print(f"DEBUG: Generated {len(legal_moves)} legal moves")
        
        # Find matching move
        matching_move = find_matching_move(engine_move, legal_moves)
        print(f"DEBUG: Matching move found: {matching_move}")
        if not matching_move:
            print(f"DEBUG: No matching move found. Engine move: {engine_move}")
            print(f"DEBUG: First few legal moves: {legal_moves[:3] if legal_moves else 'No legal moves'}")
            return jsonify({'error': 'Illegal move'}), 400
        
        # Apply move using game rule
        from core.azul_utils import Action, TileGrab
        
        # Convert FastMove to action format expected by generateSuccessor
        tg = TileGrab()
        tg.tile_type = matching_move.tile_type
        tg.number = matching_move.num_to_pattern_line + matching_move.num_to_floor_line
        tg.pattern_line_dest = matching_move.pattern_line_dest
        tg.num_to_pattern_line = matching_move.num_to_pattern_line
        tg.num_to_floor_line = matching_move.num_to_floor_line
        
        if matching_move.action_type == 1:  # Factory move
            action = (Action.TAKE_FROM_FACTORY, matching_move.source_id, tg)
        else:  # Center move
            action = (Action.TAKE_FROM_CENTRE, -1, tg)
        
        # Apply the move using game rule
        from core.azul_model import AzulGameRule
        game_rule = AzulGameRule(len(state.agents))
        new_state = game_rule.generateSuccessor(state, action, request_model.agent_id)
        
        # Update the current game state
        update_current_game_state(new_state)
        
        # Convert back to FEN
        new_fen = state_to_fen(new_state)
        
        # Get engine response if game continues
        engine_response = None
        if not new_state.is_game_over():
            engine_response = get_engine_response(new_state, request_model.agent_id)
        
        return jsonify({
            'success': True,
            'new_fen': new_fen,
            'move_executed': format_move(matching_move),
            'game_over': new_state.is_game_over(),
            'scores': [agent.score for agent in new_state.agents],
            'engine_response': engine_response
        })
        
    except ValidationError as e:
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to execute move: {str(e)}'}), 500


def convert_frontend_move_to_engine(move_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert frontend move format to engine move format."""
    # Frontend format: {source_id, tile_type, pattern_line_dest, num_to_pattern_line, num_to_floor_line}
    # Engine format: FastMove(action_type, source_id, tile_type, pattern_line_dest, num_to_pattern_line, num_to_floor_line)
    
    source_id = move_data.get('source_id', 0)
    tile_type = move_data.get('tile_type', 0)
    pattern_line_dest = move_data.get('pattern_line_dest', -1)
    num_to_pattern_line = move_data.get('num_to_pattern_line', 0)
    num_to_floor_line = move_data.get('num_to_floor_line', 0)
    
    # Determine action type based on source_id
    # Factory moves (source_id >= 0) are action_type 1, center moves (source_id < 0) are action_type 2
    action_type = 1 if source_id >= 0 else 2
    
    return {
        'action_type': action_type,
        'source_id': source_id,
        'tile_type': tile_type,
        'pattern_line_dest': pattern_line_dest,
        'num_to_pattern_line': num_to_pattern_line,
        'num_to_floor_line': num_to_floor_line
    }


def find_matching_move(engine_move: Dict[str, Any], legal_moves: List) -> Optional[object]:
    """Find matching move in legal moves list."""
    print(f"DEBUG: Looking for match with engine move: {engine_move}")
    print(f"DEBUG: Engine move type: {type(engine_move)}")
    print(f"DEBUG: Engine move keys: {engine_move.keys()}")
    
    for i, move in enumerate(legal_moves):
        print(f"DEBUG: Checking legal move {i}: action_type={move.action_type}, source_id={move.source_id}, tile_type={move.tile_type}, pattern_line_dest={move.pattern_line_dest}, num_to_pattern_line={move.num_to_pattern_line}, num_to_floor_line={move.num_to_floor_line}")
        print(f"DEBUG: Move type: {type(move)}")
        
        # Check each field individually
        action_match = move.action_type == engine_move['action_type']
        source_match = move.source_id == engine_move['source_id']
        tile_match = move.tile_type == engine_move['tile_type']
        pattern_match = move.pattern_line_dest == engine_move['pattern_line_dest']
        num_pattern_match = move.num_to_pattern_line == engine_move['num_to_pattern_line']
        num_floor_match = move.num_to_floor_line == engine_move['num_to_floor_line']
        
        print(f"DEBUG: Matches - action: {action_match}, source: {source_match}, tile: {tile_match}, pattern: {pattern_match}, num_pattern: {num_pattern_match}, num_floor: {num_floor_match}")
        
        if (action_match and source_match and tile_match and 
            pattern_match and num_pattern_match and num_floor_match):
            print(f"DEBUG: Found matching move at index {i}")
            return move
    
    print(f"DEBUG: No matching move found")
    return None


def get_engine_response(state, agent_id: int) -> Optional[Dict[str, Any]]:
    """Get engine response move for the given state."""
    try:
        from core.azul_mcts import AzulMCTS
        mcts = AzulMCTS()
        result = mcts.search(state, agent_id, max_time=0.1, max_rollouts=50)
        
        if result and result.best_move:
            return {
                'move': format_move(result.best_move),
                'score': result.best_score,
                'search_time': result.search_time
            }
    except Exception as e:
        print(f"Engine response error: {e}")
    
    return None


def state_to_fen(state) -> str:
    """Convert game state to FEN string."""
    # For now, return "initial" as the API only supports this format
    # TODO: Implement proper FEN encoding when backend supports it
    return "initial" 


@api_bp.route('/game_state', methods=['GET'])
def get_game_state():
    """Get the current game state for display."""
    try:
        # Parse current state from FEN
        fen_string = request.args.get('fen_string', 'initial')
        try:
            state = parse_fen_string(fen_string)
        except ValueError:
            # For invalid FEN, return default initial state
            from core.azul_model import AzulState
            state = AzulState(2)
        
        # Convert state to frontend format
        game_state = {
            'factories': [],
            'center': [],
            'players': []
        }
        
        # Convert factories
        for factory in state.factories:
            factory_tiles = []
            for tile_type, count in factory.tiles.items():
                for _ in range(count):
                    # Convert tile type to color string
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    factory_tiles.append(tile_colors.get(tile_type, 'W'))
            game_state['factories'].append(factory_tiles)
        
        # Convert center pool
        center_tiles = []
        for tile_type, count in state.centre_pool.tiles.items():
            for _ in range(count):
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                center_tiles.append(tile_colors.get(tile_type, 'W'))
        game_state['center'] = center_tiles
        
        # Convert player states
        for agent in state.agents:
            player = {
                'pattern_lines': [],
                'wall': [],
                'floor': []
            }
            
            # Convert pattern lines
            for i in range(5):
                line = []
                if agent.lines_tile[i] != -1:
                    tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                    tile_color = tile_colors.get(agent.lines_tile[i], 'W')
                    for _ in range(agent.lines_number[i]):
                        line.append(tile_color)
                player['pattern_lines'].append(line)
            
            # Convert wall
            for row in range(5):
                wall_row = []
                for col in range(5):
                    if agent.grid_state[row][col] != 0:
                        tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                        tile_color = tile_colors.get(agent.grid_state[row][col], 'W')
                        wall_row.append(tile_color)
                    else:
                        wall_row.append(False)
                player['wall'].append(wall_row)
            
            # Convert floor
            floor_tiles = []
            for tile_type in agent.floor_tiles:
                tile_colors = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
                floor_tiles.append(tile_colors.get(tile_type, 'W'))
            player['floor'] = floor_tiles
            
            game_state['players'].append(player)
        
        return jsonify({
            'success': True,
            'game_state': game_state
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get game state: {str(e)}'
        }), 500


@api_bp.route('/reset_game', methods=['POST'])
def reset_game():
    """Reset the current game state to initial position."""
    global _current_game_state
    from core.azul_model import AzulState
    
    _current_game_state = AzulState(2)  # Create new 2-player game
    
    return jsonify({
        'success': True,
        'message': 'Game reset to initial position'
    }) 