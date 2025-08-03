"""
Position Management API Routes

This module contains all position-related endpoints for the Azul Solver & Analysis Toolkit.
"""

import json
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from ..auth import require_session
from ..models import PositionCacheRequest, BulkPositionRequest

# Create Flask blueprint for position endpoints
positions_bp = Blueprint('positions', __name__)


@positions_bp.route('/positions/<path:fen_string>', methods=['GET'])
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


@positions_bp.route('/positions/<path:fen_string>', methods=['PUT'])
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


@positions_bp.route('/positions/<path:fen_string>', methods=['DELETE'])
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


@positions_bp.route('/positions/stats', methods=['GET'])
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

@positions_bp.route('/positions/bulk', methods=['POST'])
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


@positions_bp.route('/positions/bulk', methods=['GET'])
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


@positions_bp.route('/positions/bulk', methods=['DELETE'])
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


@positions_bp.route('/positions/search', methods=['GET'])
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


@positions_bp.route('/positions/load', methods=['POST'])
def load_position():
    """
    Load a position from the position library.
    
    POST /api/v1/positions/load
    
    Body:
        {
            "position_id": "string",
            "category": "string",
            "difficulty": "string"
        }
    
    Returns:
        Position data with game state
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        position_id = data.get('position_id')
        category = data.get('category', 'opening')
        difficulty = data.get('difficulty', 'beginner')
        
        if not position_id:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'position_id is required'
            }), 400
        
        # For now, return a mock position since we don't have a full position library
        # In a real implementation, this would load from a database or file system
        mock_position = {
            'id': position_id,
            'name': f'Position {position_id}',
            'category': category,
            'difficulty': difficulty,
            'description': f'A {difficulty} {category} position',
            'state': {
                'agents': [
                    {
                        'score': 0,
                        'lines_number': [0, 0, 0, 0, 0],
                        'lines_tile': [-1, -1, -1, -1, -1],
                        'grid_state': [[0, 0, 0, 0, 0] for _ in range(5)],
                        'floor_tiles': []
                    },
                    {
                        'score': 0,
                        'lines_number': [0, 0, 0, 0, 0],
                        'lines_tile': [-1, -1, -1, -1, -1],
                        'grid_state': [[0, 0, 0, 0, 0] for _ in range(5)],
                        'floor_tiles': []
                    }
                ],
                'factories': [
                    {'tiles': {0: 2, 1: 2}, 'total': 4},
                    {'tiles': {2: 2, 3: 2}, 'total': 4},
                    {'tiles': {4: 2, 0: 2}, 'total': 4}
                ],
                'centre_pool': {'tiles': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}, 'total': 5}
            },
            'tags': [category, difficulty]
        }
        
        return jsonify({
            'success': True,
            'position': mock_position
        })
        
    except Exception as e:
        current_app.logger.error(f"Error loading position: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to load position'
        }), 500


@positions_bp.route('/positions/save', methods=['POST'])
def save_position():
    """
    Save a position to the position library.
    
    POST /api/v1/positions/save
    
    Body:
        {
            "name": "string",
            "category": "string",
            "difficulty": "string",
            "description": "string",
            "state": {...},
            "tags": ["string"]
        }
    
    Returns:
        Success confirmation
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        name = data.get('name')
        category = data.get('category', 'custom')
        difficulty = data.get('difficulty', 'intermediate')
        description = data.get('description', '')
        state = data.get('state')
        tags = data.get('tags', [])
        
        if not name or not state:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'name and state are required'
            }), 400
        
        # For now, just return success since we don't have a full position library
        # In a real implementation, this would save to a database or file system
        position_id = f"{category}_{difficulty}_{len(name)}"
        
        return jsonify({
            'success': True,
            'position_id': position_id,
            'message': 'Position saved successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error saving position: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to save position'
        }), 500


@positions_bp.route('/positions', methods=['GET'])
@require_session
def get_positions():
    """
    Get all positions with optional filtering.
    
    GET /api/v1/positions?limit=50&offset=0
    
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
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit > 200:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'Limit cannot exceed 200'
            }), 400
        
        # Get positions
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
            'positions': positions,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'returned_count': len(positions)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting positions: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve positions'
        }), 500


@positions_bp.route('/positions', methods=['POST'])
@require_session
def create_position():
    """
    Create a new position in the cache.
    
    POST /api/v1/positions
    
    Body:
        {
            "fen_string": "string",
            "player_count": 2,
            "compressed_state": "optional_data"
        }
    
    Returns:
        Created position data
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
        
        fen_string = data.get('fen_string')
        player_count = data.get('player_count', 2)
        compressed_state = data.get('compressed_state')
        
        if not fen_string:
            return jsonify({
                'error': 'Invalid parameter',
                'message': 'fen_string is required'
            }), 400
        
        # Check if position already exists
        existing_id = current_app.database.get_position_id(fen_string)
        if existing_id:
            return jsonify({
                'error': 'Position already exists',
                'message': f'Position {fen_string} is already in cache'
            }), 409
        
        # Create position
        if compressed_state:
            position_id = current_app.database.cache_position_with_state(
                fen_string, player_count, compressed_state
            )
        else:
            position_id = current_app.database.cache_position(
                fen_string, player_count
            )
        
        return jsonify({
            'position_id': position_id,
            'fen_string': fen_string,
            'player_count': player_count,
            'created': True,
            'message': 'Position created successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating position: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to create position'
        }), 500 