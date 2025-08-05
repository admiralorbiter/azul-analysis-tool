"""
Mathematical Optimization API Routes

This module provides API endpoints for mathematical optimization of Azul moves
using linear programming and other optimization techniques.
"""

from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from typing import Dict, Any, Optional, List

from ..models.validation import PatternDetectionRequest
from ..utils import parse_fen_string
from ..auth import require_session

# Create blueprint for optimization routes
optimization_bp = Blueprint('optimization', __name__)


@optimization_bp.route('/optimize-moves', methods=['POST'])
@require_session
def optimize_moves():
    """
    Optimize moves using linear programming.
    
    This endpoint uses mathematical optimization to find optimal moves
    for scoring maximization, penalty minimization, and resource allocation.
    """
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = PatternDetectionRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
            if state is None:
                return jsonify({'error': 'Invalid FEN string', 'message': 'Could not parse game state from FEN string'}), 400
        except ValueError as e:
            return jsonify({'error': 'Invalid FEN string', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'FEN parsing error', 'message': str(e)}), 400
        
        # Get optimization objective from request
        objective = data.get('objective', 'maximize_scoring')
        player_id = request_model.current_player
        
        # Import and use the linear optimizer
        from analysis_engine.mathematical_optimization.linear_optimizer import (
            AzulLinearOptimizer, OptimizationObjective
        )
        
        optimizer = AzulLinearOptimizer()
        
        # Map objective string to enum
        objective_enum = OptimizationObjective.MAXIMIZE_SCORING
        if objective == 'minimize_penalty':
            objective_enum = OptimizationObjective.MINIMIZE_PENALTY
        elif objective == 'balance_scoring_penalty':
            objective_enum = OptimizationObjective.BALANCE_SCORING_PENALTY
        elif objective == 'maximize_wall_completion':
            objective_enum = OptimizationObjective.MAXIMIZE_WALL_COMPLETION
        elif objective == 'optimize_resource_allocation':
            objective_enum = OptimizationObjective.OPTIMIZE_RESOURCE_ALLOCATION
        
        # Run optimization
        result = optimizer.optimize_scoring(state, player_id, objective_enum)
        
        # Prepare response
        response = {
            'success': True,
            'optimization_type': 'linear_programming',
            'objective': objective,
            'objective_value': result.objective_value,
            'solver_status': result.solver_status,
            'confidence_score': result.confidence_score,
            'optimization_time': result.optimization_time,
            'optimal_moves': result.optimal_moves,
            'recommendations': result.recommendations,
            'constraint_violations': result.constraint_violations
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Move optimization error: {str(e)}")
        return jsonify({
            'error': 'Optimization service error',
            'message': str(e)
        }), 500


@optimization_bp.route('/optimize-scoring', methods=['POST'])
@require_session
def optimize_scoring():
    """
    Optimize for maximum scoring potential.
    
    This endpoint specifically focuses on maximizing scoring opportunities
    through wall completion, pattern line optimization, and bonus maximization.
    """
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = PatternDetectionRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
            if state is None:
                return jsonify({'error': 'Invalid FEN string', 'message': 'Could not parse game state from FEN string'}), 400
        except ValueError as e:
            return jsonify({'error': 'Invalid FEN string', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'FEN parsing error', 'message': str(e)}), 400
        
        # Import and use the linear optimizer
        from analysis_engine.mathematical_optimization.linear_optimizer import (
            AzulLinearOptimizer, OptimizationObjective
        )
        
        optimizer = AzulLinearOptimizer()
        
        # Run scoring optimization
        result = optimizer.optimize_scoring(
            state, 
            request_model.current_player, 
            OptimizationObjective.MAXIMIZE_SCORING
        )
        
        # Prepare response
        response = {
            'success': True,
            'optimization_type': 'scoring_maximization',
            'objective_value': result.objective_value,
            'solver_status': result.solver_status,
            'confidence_score': result.confidence_score,
            'optimization_time': result.optimization_time,
            'optimal_moves': result.optimal_moves,
            'recommendations': result.recommendations,
            'scoring_opportunities': _analyze_scoring_opportunities(state, request_model.current_player)
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Scoring optimization error: {str(e)}")
        return jsonify({
            'error': 'Scoring optimization service error',
            'message': str(e)
        }), 500


@optimization_bp.route('/optimize-resource-allocation', methods=['POST'])
@require_session
def optimize_resource_allocation():
    """
    Optimize resource allocation across different move types.
    
    This endpoint focuses on efficient resource allocation to maximize
    long-term strategic value while minimizing waste.
    """
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = PatternDetectionRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
            if state is None:
                return jsonify({'error': 'Invalid FEN string', 'message': 'Could not parse game state from FEN string'}), 400
        except ValueError as e:
            return jsonify({'error': 'Invalid FEN string', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'FEN parsing error', 'message': str(e)}), 400
        
        # Import and use the linear optimizer
        from analysis_engine.mathematical_optimization.linear_optimizer import AzulLinearOptimizer
        
        optimizer = AzulLinearOptimizer()
        
        # Run resource allocation optimization
        result = optimizer.optimize_resource_allocation(state, request_model.current_player)
        
        # Prepare response
        response = {
            'success': True,
            'optimization_type': 'resource_allocation',
            'objective_value': result.objective_value,
            'solver_status': result.solver_status,
            'confidence_score': result.confidence_score,
            'optimization_time': result.optimization_time,
            'optimal_moves': result.optimal_moves,
            'recommendations': result.recommendations,
            'resource_analysis': _analyze_resource_allocation(state, request_model.current_player)
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Resource allocation optimization error: {str(e)}")
        return jsonify({
            'error': 'Resource allocation optimization service error',
            'message': str(e)
        }), 500


@optimization_bp.route('/optimize-wall-completion', methods=['POST'])
@require_session
def optimize_wall_completion():
    """
    Optimize for wall completion bonuses.
    
    This endpoint specifically focuses on maximizing wall completion bonuses
    through strategic tile placement and pattern line management.
    """
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = PatternDetectionRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
            if state is None:
                return jsonify({'error': 'Invalid FEN string', 'message': 'Could not parse game state from FEN string'}), 400
        except ValueError as e:
            return jsonify({'error': 'Invalid FEN string', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'FEN parsing error', 'message': str(e)}), 400
        
        # Import and use the linear optimizer
        from analysis_engine.mathematical_optimization.linear_optimizer import AzulLinearOptimizer
        
        optimizer = AzulLinearOptimizer()
        
        # Run wall completion optimization
        result = optimizer.optimize_wall_completion(state, request_model.current_player)
        
        # Prepare response
        response = {
            'success': True,
            'optimization_type': 'wall_completion',
            'objective_value': result.objective_value,
            'solver_status': result.solver_status,
            'confidence_score': result.confidence_score,
            'optimization_time': result.optimization_time,
            'optimal_moves': result.optimal_moves,
            'recommendations': result.recommendations,
            'wall_analysis': _analyze_wall_completion_opportunities(state, request_model.current_player)
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Wall completion optimization error: {str(e)}")
        return jsonify({
            'error': 'Wall completion optimization service error',
            'message': str(e)
        }), 500


def _analyze_scoring_opportunities(state, player_id):
    """Analyze scoring opportunities in the current state."""
    player = state.agents[player_id]
    
    opportunities = {
        'row_completions': [],
        'column_completions': [],
        'set_completions': [],
        'pattern_line_opportunities': []
    }
    
    # Analyze row completion opportunities
    for row in range(5):
        filled_positions = sum(1 for col in range(5) if player.grid_state[row][col] != 0)
        if filled_positions >= 3:  # At least 3 tiles in a row
            opportunities['row_completions'].append({
                'row': row,
                'filled_positions': filled_positions,
                'remaining_positions': 5 - filled_positions
            })
    
    # Analyze column completion opportunities
    for col in range(5):
        filled_positions = sum(1 for row in range(5) if player.grid_state[row][col] != 0)
        if filled_positions >= 3:  # At least 3 tiles in a column
            opportunities['column_completions'].append({
                'column': col,
                'filled_positions': filled_positions,
                'remaining_positions': 5 - filled_positions
            })
    
    # Analyze set completion opportunities
    for tile_type in range(5):  # 5 tile types
        tile_count = sum(1 for row in range(5) for col in range(5) 
                        if player.grid_state[row][col] == tile_type)
        if tile_count >= 3:  # At least 3 tiles of same type
            opportunities['set_completions'].append({
                'tile_type': tile_type,
                'tile_count': tile_count,
                'remaining_tiles': 5 - tile_count
            })
    
    # Analyze pattern line opportunities
    for line_idx in range(5):
        if player.lines_number[line_idx] > 0:
            opportunities['pattern_line_opportunities'].append({
                'line_index': line_idx,
                'current_tiles': player.lines_number[line_idx],
                'tile_type': player.lines_tile[line_idx],
                'capacity': line_idx + 1,
                'remaining_space': line_idx + 1 - player.lines_number[line_idx]
            })
    
    return opportunities


def _analyze_resource_allocation(state, player_id):
    """Analyze resource allocation opportunities."""
    player = state.agents[player_id]
    
    analysis = {
        'available_tiles': {},
        'pattern_line_efficiency': [],
        'wall_placement_efficiency': [],
        'resource_waste_analysis': []
    }
    
    # Analyze available tiles
    for factory_idx, factory in enumerate(state.factories):
        if hasattr(factory, 'tiles'):
            for tile_type, count in factory.tiles.items():
                if count > 0:
                    if tile_type not in analysis['available_tiles']:
                        analysis['available_tiles'][tile_type] = 0
                    analysis['available_tiles'][tile_type] += count
    
    # Analyze center pool tiles
    if hasattr(state.centre_pool, 'tiles'):
        for tile_type, count in state.centre_pool.tiles.items():
            if count > 0:
                if tile_type not in analysis['available_tiles']:
                    analysis['available_tiles'][tile_type] = 0
                analysis['available_tiles'][tile_type] += count
    
    # Analyze pattern line efficiency
    for line_idx in range(5):
        if player.lines_number[line_idx] > 0:
            efficiency = player.lines_number[line_idx] / (line_idx + 1)
            analysis['pattern_line_efficiency'].append({
                'line_index': line_idx,
                'efficiency': efficiency,
                'current_tiles': player.lines_number[line_idx],
                'capacity': line_idx + 1
            })
    
    # Analyze wall placement efficiency
    for row in range(5):
        for col in range(5):
            if player.grid_state[row][col] != 0:
                # Calculate how efficiently this position contributes to completions
                row_completion = sum(1 for c in range(5) if player.grid_state[row][c] != 0)
                col_completion = sum(1 for r in range(5) if player.grid_state[r][col] != 0)
                
                analysis['wall_placement_efficiency'].append({
                    'row': row,
                    'col': col,
                    'tile_type': player.grid_state[row][col],
                    'row_completion_contribution': row_completion,
                    'col_completion_contribution': col_completion
                })
    
    return analysis


def _analyze_wall_completion_opportunities(state, player_id):
    """Analyze wall completion opportunities."""
    player = state.agents[player_id]
    
    analysis = {
        'near_completions': [],
        'high_value_positions': [],
        'completion_sequences': []
    }
    
    # Find near-complete rows
    for row in range(5):
        filled_positions = sum(1 for col in range(5) if player.grid_state[row][col] != 0)
        if filled_positions >= 4:  # 4 out of 5 positions filled
            empty_positions = [(row, col) for col in range(5) if player.grid_state[row][col] == 0]
            analysis['near_completions'].append({
                'type': 'row',
                'index': row,
                'filled_positions': filled_positions,
                'empty_positions': empty_positions,
                'completion_value': player.ROW_BONUS
            })
    
    # Find near-complete columns
    for col in range(5):
        filled_positions = sum(1 for row in range(5) if player.grid_state[row][col] != 0)
        if filled_positions >= 4:  # 4 out of 5 positions filled
            empty_positions = [(row, col) for row in range(5) if player.grid_state[row][col] == 0]
            analysis['near_completions'].append({
                'type': 'column',
                'index': col,
                'filled_positions': filled_positions,
                'empty_positions': empty_positions,
                'completion_value': player.COL_BONUS
            })
    
    # Find high-value positions (positions that contribute to multiple completions)
    for row in range(5):
        for col in range(5):
            if player.grid_state[row][col] == 0:  # Empty position
                row_completion = sum(1 for c in range(5) if player.grid_state[row][c] != 0)
                col_completion = sum(1 for r in range(5) if player.grid_state[r][col] != 0)
                
                if row_completion >= 3 or col_completion >= 3:
                    analysis['high_value_positions'].append({
                        'row': row,
                        'col': col,
                        'row_completion_contribution': row_completion,
                        'col_completion_contribution': col_completion,
                        'total_value': row_completion + col_completion
                    })
    
    return analysis 