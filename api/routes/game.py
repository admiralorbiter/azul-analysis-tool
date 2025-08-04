"""
Game Management API Routes

This module contains all game-related endpoints for the Azul Solver & Analysis Toolkit.
"""

import json
import time
import copy
import random
import hashlib
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from ..auth import require_session
from ..models import (
    GameCreationRequest,
    GameAnalysisRequest,
    GameLogUploadRequest,
    GameAnalysisSearchRequest,
    MoveExecutionRequest,
    SimilarPositionRequest,
    ContinuationRequest,
    PositionDatabaseRequest
)
from ..utils import (
    parse_fen_string,
    state_to_fen,
    update_current_game_state,
    convert_frontend_move_to_engine,
    find_matching_move,
    get_engine_response,
    convert_frontend_state_to_azul_state,
    convert_tile_string_to_type,
    format_move
)

# Create Flask blueprint for game endpoints
game_bp = Blueprint('game', __name__)


@game_bp.route('/execute_move', methods=['POST'])
# @require_session # Removed for local development
def execute_move():
    """Execute a move and return new game state."""
    try:
        print("DEBUG: execute_move endpoint called")
        
        try:
            data = request.get_json(force=True)
            print(f"DEBUG: Raw data received: {data}")
            print(f"DEBUG: FEN string received: {data.get('fen_string', 'NOT_FOUND')}")
        except Exception as e:
            print(f"DEBUG: Error parsing JSON: {e}")
            data = None
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        print("DEBUG: About to create MoveExecutionRequest")
        request_model = MoveExecutionRequest(**data)
        print(f"DEBUG: Request model created: {request_model}")
        
        # Parse current state
        try:
            print("DEBUG: About to parse FEN string")
            state = parse_fen_string(request_model.fen_string)
            print(f"DEBUG: FEN parsed successfully - state is None: {state is None}")
            if state is not None:
                print(f"DEBUG: State has agents: {hasattr(state, 'agents')}")
                print(f"DEBUG: Agent count: {len(state.agents) if hasattr(state, 'agents') else 'No agents'}")
                print(f"DEBUG: FEN parsed successfully - agent count: {len(state.agents)}, factories: {len(state.factories)}")
                
                # Debug: Print factory contents
                print("DEBUG: Factory contents:")
                for i, factory in enumerate(state.factories):
                    print(f"  Factory {i}: {dict(factory.tiles)}")
            else:
                print("DEBUG: ERROR - parse_fen_string returned None!")
                return jsonify({'error': f'Invalid FEN string: {request_model.fen_string}'}), 400
                
        except ValueError as e:
            print(f"DEBUG: FEN parsing error: {e}")
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        except Exception as e:
            print(f"DEBUG: Unexpected error parsing FEN: {e}")
            return jsonify({'error': f'Error parsing game state: {str(e)}'}), 500
        
        # Convert frontend move format to engine move format
        try:
            print("DEBUG: About to convert frontend move")
            move_data = request_model.move
            print(f"DEBUG: Frontend move data: {move_data}")
            print(f"DEBUG: Frontend move data type: {type(move_data)}")
            print(f"DEBUG: Frontend move data keys: {move_data.keys() if isinstance(move_data, dict) else 'Not a dict'}")
            
            engine_move = convert_frontend_move_to_engine(move_data)
            print(f"DEBUG: Converted engine move: {engine_move}")
            print(f"DEBUG: Engine move tile_type: {engine_move.get('tile_type')} (should be 0 for blue)")
        except Exception as e:
            print(f"DEBUG: Error converting move: {e}")
            return jsonify({'error': f'Error converting move: {str(e)}'}), 500
        
        # Generate legal moves
        try:
            print("DEBUG: About to generate legal moves")
            print(f"DEBUG: State factories before move generation:")
            for i, factory in enumerate(state.factories):
                print(f"  Factory {i}: {dict(factory.tiles)}")
            print(f"DEBUG: State center pool before move generation: {dict(state.centre_pool.tiles)}")
            
            from core.azul_move_generator import FastMoveGenerator
            generator = FastMoveGenerator()
            legal_moves = generator.generate_moves_fast(state, request_model.agent_id)
            print(f"DEBUG: Generated {len(legal_moves)} legal moves")
            
            # Debug: Print all legal moves to see their format
            print("DEBUG: All legal moves:")
            for i, move in enumerate(legal_moves):
                print(f"  Move {i}: action_type={move.action_type}, source_id={move.source_id}, tile_type={move.tile_type}, pattern_line_dest={move.pattern_line_dest}, num_to_pattern_line={move.num_to_pattern_line}, num_to_floor_line={move.num_to_floor_line}")
                
        except Exception as e:
            print(f"DEBUG: Error generating moves: {e}")
            import traceback
            print(f"DEBUG: Move generation traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Error generating legal moves: {str(e)}'}), 500
        
        # Find matching move
        try:
            print("DEBUG: About to find matching move")
            matching_move = find_matching_move(engine_move, legal_moves)
            print(f"DEBUG: Matching move found: {matching_move}")
            if matching_move:
                print(f"DEBUG: Matching move tile_type: {matching_move.tile_type}")
                print(f"DEBUG: Matching move source_id: {matching_move.source_id}")
                print(f"DEBUG: Matching move pattern_line_dest: {matching_move.pattern_line_dest}")
            if not matching_move:
                print(f"DEBUG: No matching move found. Engine move: {engine_move}")
                return jsonify({'error': 'Illegal move'}), 400
        except Exception as e:
            print(f"DEBUG: Error finding matching move: {e}")
            return jsonify({'error': f'Error validating move: {str(e)}'}), 500
        
        # Apply move using game rule
        try:
            print("DEBUG: About to apply move")
            from core.azul_utils import Action, TileGrab
            
            # Convert FastMove to action format expected by generateSuccessor
            tg = TileGrab()
            tg.tile_type = matching_move.tile_type
            tg.number = matching_move.num_to_pattern_line + matching_move.num_to_floor_line
            tg.pattern_line_dest = matching_move.pattern_line_dest
            tg.num_to_pattern_line = matching_move.num_to_pattern_line
            tg.num_to_floor_line = matching_move.num_to_floor_line
            
            print(f"DEBUG: TileGrab created - tile_type: {tg.tile_type}, number: {tg.number}, pattern_line_dest: {tg.pattern_line_dest}")
            
            if matching_move.action_type == 1:  # Factory move
                action = (Action.TAKE_FROM_FACTORY, matching_move.source_id, tg)
            else:  # Center move
                action = (Action.TAKE_FROM_CENTRE, -1, tg)
            
            print(f"DEBUG: Action created: {action}")
            
            # Apply the move using game rule
            from core.azul_model import AzulGameRule
            game_rule = AzulGameRule(len(state.agents))
            print(f"DEBUG: About to apply move with action: {action}")
            print(f"DEBUG: Action[0] (action_type): {action[0]}")
            print(f"DEBUG: Action[1] (source_id): {action[1]}")
            print(f"DEBUG: Action[2] (tile_grab): {action[2]}")
            print(f"DEBUG: TileGrab tile_type: {action[2].tile_type}")
            print(f"DEBUG: TileGrab number: {action[2].number}")
            print(f"DEBUG: TileGrab pattern_line_dest: {action[2].pattern_line_dest}")
            print(f"DEBUG: TileGrab num_to_pattern_line: {action[2].num_to_pattern_line}")
            print(f"DEBUG: TileGrab num_to_floor_line: {action[2].num_to_floor_line}")
            
            new_state = game_rule.generateSuccessor(state, action, request_model.agent_id)
            print(f"DEBUG: Move applied successfully")
            
        except Exception as e:
            print(f"DEBUG: Error applying move: {e}")
            import traceback
            print(f"DEBUG: Move application traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Error applying move: {str(e)}'}), 500
        
        # Update global game state
        update_current_game_state(new_state)
        
        # Convert new state to FEN
        try:
            new_fen = state_to_fen(new_state)
            print(f"DEBUG: New FEN generated: {new_fen}")
        except Exception as e:
            print(f"DEBUG: Error generating new FEN: {e}")
            return jsonify({'error': f'Error generating new state: {str(e)}'}), 500
        
        # Convert new state to frontend format
        try:
            from ..utils import convert_azul_state_to_frontend
            frontend_state = convert_azul_state_to_frontend(new_state)
            print(f"DEBUG: Frontend state converted successfully")
        except Exception as e:
            print(f"DEBUG: Error converting to frontend format: {e}")
            return jsonify({'error': f'Error converting state: {str(e)}'}), 500
        
        # Build move_executed string for test compatibility
        move_type_str = ''
        if matching_move.action_type == 1:  # Factory move
            move_type_str = f"take_from_factory_{matching_move.source_id}_{matching_move.tile_type}_{matching_move.pattern_line_dest}_{matching_move.num_to_pattern_line}_{matching_move.num_to_floor_line}"
        else:  # Center move
            move_type_str = f"take_from_center_{matching_move.tile_type}_{matching_move.pattern_line_dest}_{matching_move.num_to_pattern_line}_{matching_move.num_to_floor_line}"

        return jsonify({
            'success': True,
            'new_fen': new_fen,
            'new_game_state': frontend_state,
            'move_executed': move_type_str,
            'game_over': False,
            'scores': [agent.score for agent in new_state.agents]
        })
        
    except ValidationError as e:
        print(f"DEBUG: Validation error: {e}")
        return jsonify({'error': f'Invalid request data: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Unexpected error in execute_move: {e}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@game_bp.route('/create_game', methods=['POST'])
def create_game():
    """Create a new game with specified player count."""
    try:
        try:
            data = request.get_json(force=True)
        except Exception:
            data = {}
        
        request_model = GameCreationRequest(**(data or {}))
        
        print(f"DEBUG: Creating new game with {request_model.player_count} players")
        
        # Validate player count - only 2 players supported
        if request_model.player_count != 2:
            return jsonify({'error': 'Only 2-player games are supported'}), 400
        
        # Create new game state
        from core.azul_model import AzulState
        import random
        import time
        
        # Use seed if provided, otherwise use time-based seed
        if request_model.seed is not None:
            random.seed(request_model.seed)
        else:
            # Use a time-based seed for true randomness
            random.seed(int(time.time() * 1000) % 2**32)
        
        # Create new game state
        new_state = AzulState(request_model.player_count)
        
        # Reset the random seed
        random.seed()
        
        # Update global game state
        update_current_game_state(new_state)
        
        # Generate a unique identifier for this state
        state_id = f"state_{int(time.time() * 1000) % 1000000}"
        
        return jsonify({
            'success': True,
            'fen_string': state_id,
            'player_count': request_model.player_count,
            'message': f'New {request_model.player_count}-player game created'
        })
        
    except Exception as e:
        print(f"ERROR in create_game: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Game creation failed: {str(e)}'}), 500


@game_bp.route('/game_state', methods=['GET'])
def get_game_state():
    """Get the current game state for display."""
    try:
        # If we have a stored editable game state, return it with a generated FEN string
        from ..utils import _current_editable_game_state, _initial_game_state
        
        if _current_editable_game_state is not None:
            # Generate a unique FEN string for this state
            import hashlib
            import json
            
            try:
                # Create a hash of the game state
                state_json = json.dumps(_current_editable_game_state, sort_keys=True)
                state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
                unique_fen = f"state_{state_hash}"
                
                # Add the FEN string to the game state
                game_state_with_fen = _current_editable_game_state.copy()
                game_state_with_fen['fen_string'] = unique_fen
                
                return jsonify({
                    'success': True,
                    'game_state': game_state_with_fen
                })
            except Exception as e:
                print(f"Warning: Failed to generate FEN for editable state: {e}")
                # Fallback to returning without FEN
                return jsonify({
                    'success': True,
                    'game_state': _current_editable_game_state
                })
        
        # Otherwise, parse current state from FEN
        fen_string = request.args.get('fen_string', 'initial')
        state = None
        try:
            state = parse_fen_string(fen_string)
        except ValueError:
            # For invalid FEN, return default initial state with consistent seed
            from core.azul_model import AzulState
            import random
            
            # Use fixed seed for consistent initial state
            random.seed(42)
            state = AzulState(2)
            random.seed()  # Reset to random seed
            
            # Store this as the initial state for future use
            if _initial_game_state is None:
                _initial_game_state = copy.deepcopy(state)
        
        # Ensure we have a valid state
        if state is None:
            # Fallback to default initial state
            from core.azul_model import AzulState
            import random
            
            # Use fixed seed for consistent initial state
            random.seed(42)
            state = AzulState(2)
            random.seed()  # Reset to random seed
        
        # Convert state to frontend format using the converter
        from ..utils import convert_azul_state_to_frontend
        game_state = convert_azul_state_to_frontend(state)
        game_state['fen_string'] = state_to_fen(state)  # Include current FEN string
        
        return jsonify({
            'success': True,
            'game_state': game_state
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get game state: {str(e)}'
        }), 500


@game_bp.route('/game_state', methods=['PUT'])
def put_game_state():
    """Update the current game state from frontend."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        fen_string = data.get('fen_string', 'initial')
        game_state = data.get('game_state')
        
        if not game_state:
            return jsonify({'error': 'No game_state provided'}), 400
        
        # Generate a unique FEN string for this state
        import hashlib
        import json
        import time
        
        try:
            # Create a hash of the game state
            state_json = json.dumps(game_state, sort_keys=True)
            state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
            unique_fen = f"state_{state_hash}"
        except Exception as e:
            # Fallback to timestamp-based identifier
            timestamp = int(time.time() * 1000) % 1000000
            unique_fen = f"state_{timestamp}"
        
        # Store the game state for future retrieval
        from ..utils import _current_editable_game_state
        _current_editable_game_state = game_state
        
        return jsonify({
            'success': True,
            'fen_string': unique_fen,
            'message': 'Game state updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to update game state: {str(e)}'
        }), 500


@game_bp.route('/reset_game', methods=['POST'])
def reset_game():
    """Reset the current game state to initial position."""
    from core.azul_model import AzulState
    from ..utils import _initial_game_state, _current_editable_game_state
    
    # Reset to the consistent initial state
    if _initial_game_state is None:
        random.seed(42)
        _initial_game_state = AzulState(2)
        random.seed()
    
    update_current_game_state(copy.deepcopy(_initial_game_state))
    
    # Clear the editable game state so it falls back to the initial state
    _current_editable_game_state = None
    
    return jsonify({
        'success': True,
        'message': 'Game reset to initial position'
    })


@game_bp.route('/analyze_game', methods=['POST'])
@require_session
def analyze_game():
    """Analyze a complete game for blunders and insights."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'game_data' not in data:
            return jsonify({'success': False, 'error': 'Missing game_data field'}), 400
        
        request_model = GameAnalysisRequest(**data)
        
        game_data = request_model.game_data
        moves = game_data.get('moves', [])
        analysis_results = []
        
        print(f"DEBUG: Analyzing game with {len(moves)} moves")
        
        for i, move_data in enumerate(moves):
            # Get position before move
            position = move_data.get('position_before', 'initial')
            
            # Analyze position
            try:
                analysis = analyze_position_internal(position, move_data['player'], request_model.analysis_depth)
                
                # Calculate blunder severity
                actual_move_score = analysis.get('move_scores', {}).get(str(move_data['move']), 0)
                best_move_score = analysis.get('best_score', 0)
                blunder_severity = best_move_score - actual_move_score
                
                analysis_results.append({
                    'move_index': i,
                    'player': move_data['player'],
                    'move': move_data['move'],
                    'position': position,
                    'analysis': analysis,
                    'blunder_severity': blunder_severity,
                    'is_blunder': blunder_severity >= 3.0
                })
                
                print(f"DEBUG: Move {i+1} - Blunder severity: {blunder_severity:.2f}")
                
            except Exception as e:
                print(f"DEBUG: Error analyzing move {i+1}: {e}")
                analysis_results.append({
                    'move_index': i,
                    'player': move_data['player'],
                    'move': move_data['move'],
                    'position': position,
                    'analysis': None,
                    'blunder_severity': 0,
                    'is_blunder': False,
                    'error': str(e)
                })
        
        # Calculate game summary
        blunders = [r for r in analysis_results if r.get('is_blunder', False)]
        total_blunder_severity = sum(r.get('blunder_severity', 0) for r in analysis_results)
        avg_blunder_severity = total_blunder_severity / len(analysis_results) if analysis_results else 0
        
        summary = {
            'total_moves': len(moves),
            'blunder_count': len(blunders),
            'blunder_percentage': (len(blunders) / len(moves)) * 100 if moves else 0,
            'average_blunder_severity': avg_blunder_severity,
            'worst_blunder': max((r.get('blunder_severity', 0) for r in analysis_results), default=0),
            'players': game_data.get('players', ['Player 1', 'Player 2']),
            'game_result': game_data.get('result', {})
        }
        
        return jsonify({
            'success': True,
            'analysis_results': analysis_results,
            'summary': summary
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to analyze game: {str(e)}'}), 500


@game_bp.route('/upload_game_log', methods=['POST'])
@require_session
def upload_game_log():
    """Upload and parse a game log file."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'game_format' not in data:
            return jsonify({'success': False, 'error': 'Missing game_format field'}), 400
        if 'game_content' not in data:
            return jsonify({'success': False, 'error': 'Missing game_content field'}), 400
        
        request_model = GameLogUploadRequest(**data)
        
        # Parse game log based on format
        try:
            game_data = parse_game_log(request_model.game_content, request_model.game_format)
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Invalid game format: {str(e)}'}), 400
        
        # Store in database for later analysis
        game_id = f"game_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Store game data in database
        if not current_app.database:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        try:
            with current_app.database.get_connection() as conn:
                conn.execute("""
                    INSERT INTO game_analyses (game_id, players, total_moves, game_data, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    game_id,
                    json.dumps(game_data.get('players', [])),
                    len(game_data.get('moves', [])),
                    json.dumps(game_data),
                    time.time()
                ))
                conn.commit()
        except Exception as e:
            print(f"DEBUG: Error storing game data: {e}")
            return jsonify({'success': False, 'error': f'Failed to store game data: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'parsed_data': game_data
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in upload_game_log: {e}")
        return jsonify({'success': False, 'error': f'Failed to upload game log: {str(e)}'}), 500


@game_bp.route('/game_analysis/<game_id>', methods=['GET'])
@require_session
def get_game_analysis(game_id: str):
    """Get analysis results for a specific game."""
    try:
        if not current_app.database:
            return jsonify({'error': 'Database not available'}), 503
        
        with current_app.database.get_connection() as conn:
            result = conn.execute("""
                SELECT game_data, analysis_data, created_at
                FROM game_analyses 
                WHERE game_id = ?
            """, (game_id,)).fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        game_data = json.loads(result[0])
        analysis_data = json.loads(result[1]) if result[1] else None
        created_at = result[2]
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'game_data': game_data,
            'game_analysis': analysis_data,
            'created_at': created_at
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get game analysis: {str(e)}'}), 500


@game_bp.route('/game_analyses', methods=['GET'])
@require_session
def search_game_analyses():
    """Search for game analyses."""
    try:
        # Parse query parameters
        player_names = request.args.getlist('player_names')
        min_blunders = request.args.get('min_blunders', type=int)
        max_blunders = request.args.get('max_blunders', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not current_app.database:
            return jsonify({'error': 'Database not available'}), 503
        
        with current_app.database.get_connection() as conn:
            # Build query
            query = "SELECT game_id, players, total_moves, blunder_count, created_at FROM game_analyses WHERE 1=1"
            params = []
            
            if min_blunders is not None:
                query += " AND blunder_count >= ?"
                params.append(min_blunders)
            
            if max_blunders is not None:
                query += " AND blunder_count <= ?"
                params.append(max_blunders)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            results = conn.execute(query, params).fetchall()
        
        games = []
        for row in results:
            games.append({
                'game_id': row[0],
                'players': json.loads(row[1]),
                'total_moves': row[2],
                'blunder_count': row[3],
                'created_at': row[4]
            })
        
        return jsonify({
            'success': True,
            'game_analyses': games,
            'total': len(games)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to search game analyses: {str(e)}'}), 500


# D6: Opening Explorer endpoints
@game_bp.route('/similar_positions', methods=['POST'])
@require_session
def find_similar_positions():
    """Find positions similar to the given position."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'fen_string' not in data:
            return jsonify({'success': False, 'error': 'Missing fen_string field'}), 400
        
        request_model = SimilarPositionRequest(**data)
        
        if not current_app.database:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        # Get position hash
        position_hash = hash_position(request_model.fen_string)
        
        # Find similar positions
        similar_positions = find_similar_positions_internal(
            position_hash, 
            request_model.similarity_threshold, 
            request_model.limit
        )
        
        return jsonify({
            'success': True,
            'similar_positions': similar_positions
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in find_similar_positions: {e}")
        return jsonify({'success': False, 'error': f'Failed to find similar positions: {str(e)}'}), 500


@game_bp.route('/popular_continuations', methods=['POST'])
@require_session
def get_popular_continuations():
    """Get popular continuations for a position."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'fen_string' not in data:
            return jsonify({'success': False, 'error': 'Missing fen_string field'}), 400
        
        request_model = ContinuationRequest(**data)
        
        continuations = get_popular_continuations_internal(
            request_model.fen_string, 
            request_model.limit
        )
        
        # Check if position exists in database
        if not current_app.database:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        with current_app.database.get_connection() as conn:
            position_exists = conn.execute("""
                SELECT id FROM position_database WHERE fen_string = ?
            """, (request_model.fen_string,)).fetchone()
        
        if not position_exists:
            return jsonify({'success': False, 'error': 'Position not found'}), 404
        
        return jsonify({
            'success': True,
            'continuations': continuations
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in get_popular_continuations: {e}")
        return jsonify({'success': False, 'error': f'Failed to get continuations: {str(e)}'}), 500


@game_bp.route('/add_to_database', methods=['POST'])
@require_session
def add_position_to_database():
    """Add a position to the opening database."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No request data provided'}), 400
        
        # Validate required fields
        if 'fen_string' not in data:
            return jsonify({'success': False, 'error': 'Missing fen_string field'}), 400
        
        request_model = PositionDatabaseRequest(**data)
        
        result = add_position_to_database_internal(
            request_model.fen_string,
            request_model.metadata,
            request_model.frequency
        )
        
        return jsonify({
            'success': True,
            'position_id': result['position_id'],
            'action': result['action']
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': f'Invalid request: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Exception in add_position_to_database: {e}")
        return jsonify({'success': False, 'error': f'Failed to add position: {str(e)}'}), 500


# Internal helper functions
def analyze_position_internal(fen_string: str, agent_id: int, depth: int = 3) -> Dict[str, Any]:
    """Internal function to analyze a position."""
    try:
        # Parse position
        state = parse_fen_string(fen_string)
        
        # Get legal moves
        from core.azul_move_generator import FastMoveGenerator
        generator = FastMoveGenerator()
        legal_moves = generator.generate_moves_fast(state, agent_id)
        
        # Analyze with alpha-beta search
        from core.azul_search import AzulAlphaBetaSearch
        searcher = AzulAlphaBetaSearch()
        
        start_time = time.time()
        result = searcher.search(state, depth, agent_id)
        search_time = time.time() - start_time
        
        # Format move scores
        move_scores = {}
        for move in legal_moves:
            move_key = f"{move.source_id}_{move.tile_type}_{move.pattern_line_dest}_{move.num_to_pattern_line}_{move.num_to_floor_line}"
            move_scores[move_key] = 0  # Placeholder - would need to evaluate each move
        
        return {
            'best_move': format_move(result.best_move) if result.best_move else None,
            'best_score': result.best_score,
            'search_time': search_time,
            'nodes_searched': result.nodes_searched,
            'depth_reached': result.depth_reached,
            'move_scores': move_scores
        }
        
    except Exception as e:
        print(f"DEBUG: Error in analyze_position_internal: {e}")
        return {
            'best_move': None,
            'best_score': 0,
            'search_time': 0,
            'nodes_searched': 0,
            'depth_reached': 0,
            'move_scores': {},
            'error': str(e)
        }


def parse_game_log(content: str, format_type: str) -> Dict[str, Any]:
    """Parse game log content based on format."""
    if format_type == 'json':
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format: {content}")
    elif format_type == 'text':
        return parse_text_game_log(content)
    else:
        raise ValueError(f"Unsupported game format: {format_type}")


def parse_text_game_log(content: str) -> Dict[str, Any]:
    """Parse plain text game log format."""
    lines = content.split('\n')
    game_info = {}
    moves = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse move descriptions
        move_data = parse_move_description(line)
        if move_data:
            moves.append(move_data)
    
    return {
        'players': game_info.get('players', ['Player 1', 'Player 2']),
        'moves': moves,
        'result': game_info.get('result', {})
    }


def parse_move_description(desc: str) -> Optional[Dict[str, Any]]:
    """Parse a move description from text format."""
    # Simple parsing - can be enhanced for specific formats
    if 'move' in desc.lower() or 'action' in desc.lower():
        return {
            'player': 0,  # Default to player 0
            'move': desc,
            'position_before': 'initial'
        }
    return None


def hash_position(fen_string: str) -> str:
    """Generate a hash for position similarity comparison."""
    import hashlib
    return hashlib.md5(fen_string.encode('utf-8')).hexdigest()


def find_similar_positions_internal(position_hash: str, threshold: float, limit: int) -> List[Dict[str, Any]]:
    """Find positions similar to the given position hash."""
    if not current_app.database:
        return []
    
    try:
        with current_app.database.get_connection() as conn:
            # Simple similarity based on hash prefix matching
            # This is a placeholder - real similarity would require more sophisticated algorithms
            prefix = position_hash[:8]
            
            results = conn.execute("""
                SELECT fen_string, metadata, frequency
                FROM position_database 
                WHERE fen_string LIKE ? || '%'
                ORDER BY frequency DESC
                LIMIT ?
            """, (prefix, limit)).fetchall()
            
            similar_positions = []
            for row in results:
                similarity = calculate_position_similarity(position_hash, hash_position(row[0]))
                if similarity >= threshold:
                    similar_positions.append({
                        'fen_string': row[0],
                        'metadata': json.loads(row[1]) if row[1] else {},
                        'frequency': row[2],
                        'similarity': similarity
                    })
            
            return similar_positions
            
    except Exception as e:
        print(f"DEBUG: Error finding similar positions: {e}")
        return []


def get_popular_continuations_internal(fen_string: str, limit: int) -> List[Dict[str, Any]]:
    """Get popular continuations for a position."""
    if not current_app.database:
        return []
    
    try:
        with current_app.database.get_connection() as conn:
            # This is a placeholder - real implementation would track move sequences
            results = conn.execute("""
                SELECT next_fen_string, move_data, frequency
                FROM position_continuations 
                WHERE fen_string = ?
                ORDER BY frequency DESC
                LIMIT ?
            """, (fen_string, limit)).fetchall()
            
            continuations = []
            for row in results:
                continuations.append({
                    'next_position': row[0],
                    'move': json.loads(row[1]) if row[1] else {},
                    'frequency': row[2]
                })
            
            return continuations
            
    except Exception as e:
        print(f"DEBUG: Error getting continuations: {e}")
        return []


def add_position_to_database_internal(fen_string: str, metadata: Optional[Dict[str, Any]], frequency: int) -> Dict[str, Any]:
    """Add a position to the database."""
    if not current_app.database:
        return {'position_id': None, 'action': 'skipped_no_database'}
    
    try:
        with current_app.database.get_connection() as conn:
            # Check if position already exists
            existing = conn.execute("""
                SELECT id, frequency FROM position_database WHERE fen_string = ?
            """, (fen_string,)).fetchone()
            
            if existing:
                # Update frequency
                new_frequency = existing[1] + frequency
                conn.execute("""
                    UPDATE position_database 
                    SET frequency = ?, metadata = ?
                    WHERE id = ?
                """, (new_frequency, json.dumps(metadata) if metadata else None, existing[0]))
                action = 'updated'
                position_id = existing[0]
            else:
                # Insert new position
                result = conn.execute("""
                    INSERT INTO position_database (fen_string, metadata, frequency, created_at)
                    VALUES (?, ?, ?, ?)
                """, (fen_string, json.dumps(metadata) if metadata else None, frequency, time.time()))
                position_id = result.lastrowid
                action = 'created'
            
            conn.commit()
            
            return {
                'position_id': position_id,
                'action': action
            }
            
    except Exception as e:
        print(f"DEBUG: Error adding position to database: {e}")
        return {'position_id': None, 'action': 'error', 'error': str(e)}


def calculate_position_similarity(hash1: str, hash2: str) -> float:
    """Calculate similarity between two position hashes."""
    # Simple similarity based on hash prefix matching
    # This is a placeholder - real similarity would require more sophisticated algorithms
    if hash1 == hash2:
        return 1.0
    
    # Compare first 8 characters
    prefix1 = hash1[:8]
    prefix2 = hash2[:8]
    
    if prefix1 == prefix2:
        return 0.8
    
    # Compare first 4 characters
    prefix1 = hash1[:4]
    prefix2 = hash2[:4]
    
    if prefix1 == prefix2:
        return 0.4
    
    return 0.0 