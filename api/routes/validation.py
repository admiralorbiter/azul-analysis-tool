from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from typing import Dict, Any, Optional, List

from ..models.validation import (
    BoardValidationRequest, 
    PatternDetectionRequest, 
    ScoringOptimizationRequest, 
    FloorLinePatternRequest
)
from ..utils import parse_fen_string
from ..auth import require_session

# Create blueprint for validation routes
validation_bp = Blueprint('validation', __name__)


@validation_bp.route('/validate-board-state', methods=['POST'])
@require_session
def validate_board_state():
    """
    Validate a complete board state for rule compliance.
    
    This endpoint is used by the board editor (R1.1) to ensure
    that edited positions follow all Azul rules.
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validation_request = BoardValidationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid request format', 'details': str(e)}), 400
        
        # Import the validator
        from core.azul_rule_validator import BoardStateValidator
        from core.azul_model import AzulState
        
        # Create validator
        validator = BoardStateValidator()
        
        # Convert game state dict to AzulState
        game_state_dict = validation_request.game_state
        
        # Convert game state dict to AzulState using the new from_dict method
        try:
            # Create AzulState from the provided game state
            state = AzulState.from_dict(game_state_dict)
        except Exception as e:
            return jsonify({
                'error': 'Invalid game state format',
                'message': str(e)
            }), 400
        
        # Perform validation based on type
        if validation_request.validation_type == "complete":
            result = validator.validate_complete_board_state(state)
        elif validation_request.validation_type == "pattern_line":
            # Extract pattern line specific parameters
            player_id = validation_request.player_id or 0
            # Parse element_id like "pattern_line_0_2" -> line_index=2
            if validation_request.element_id:
                parts = validation_request.element_id.split('_')
                line_index = int(parts[-1]) if len(parts) > 2 else 0
            else:
                line_index = 0
            
            # Get current pattern line state
            agent = state.agents[player_id]
            current_color = agent.lines_tile[line_index]
            tile_count = agent.lines_number[line_index]
            
            result = validator.validate_pattern_line_edit(
                state, player_id, line_index, current_color, tile_count
            )
        else:
            # Default to complete validation
            result = validator.validate_complete_board_state(state)
        
        # Convert result to JSON response
        response = {
            'valid': result.is_valid,
            'errors': result.errors,
            'warnings': result.warnings,
            'affected_elements': getattr(result, 'affected_elements', []),
            'suggestion': getattr(result, 'suggestion', None)
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Board validation error: {str(e)}")
        return jsonify({
            'error': 'Validation service error',
            'message': str(e)
        }), 500


@validation_bp.route('/validate-pattern-line-edit', methods=['POST'])
def validate_pattern_line_edit():
    """
    Validate a pattern line edit in real-time (no auth required for UI responsiveness).
    
    This provides immediate feedback during board editing.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        current_color = data.get('current_color', -1)
        new_color = data.get('new_color', -1)
        current_count = data.get('current_count', 0)
        new_count = data.get('new_count', 0)
        line_index = data.get('line_index', 0)
        
        # Import validation function
        from core.azul_rule_validator import validate_pattern_line_edit_simple
        
        # Validate
        result = validate_pattern_line_edit_simple(
            current_color, new_color, current_count, new_count, line_index + 1
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': 'Validation error',
            'message': str(e)
        }), 500


@validation_bp.route('/validate-tile-count', methods=['POST'])
def validate_tile_count():
    """Validate tile count conservation in the game state."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = BoardValidationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.game_state.get('fen', ''))
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the rule validator
        from core.azul_rule_validator import AzulRuleValidator
        validator = AzulRuleValidator()
        
        # Validate tile conservation
        validation_result = validator.validate_tile_conservation(state)
        
        return jsonify({
            'is_valid': validation_result.is_valid,
            'message': validation_result.message,
            'tile_counts': validator.count_all_tiles(state) if hasattr(validator, 'count_all_tiles') else {}
        })
        
    except Exception as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 500


@validation_bp.route('/detect-patterns', methods=['POST'])
def detect_patterns():
    """Detect tactical patterns in the current position."""
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
        
        # Import and use the pattern detector
        from analysis_engine.comprehensive_patterns.azul_patterns import AzulPatternDetector
        detector = AzulPatternDetector()
        
        # Update urgency threshold if provided
        if request_model.urgency_threshold != 0.7:
            detector.blocking_urgency_threshold = request_model.urgency_threshold
        
        # Detect patterns
        pattern_detection = detector.detect_patterns(state, request_model.current_player)
        
        # Prepare response
        response = {
            'total_patterns': pattern_detection.total_patterns,
            'confidence_score': pattern_detection.confidence_score,
            'patterns_detected': True if pattern_detection.total_patterns > 0 else False
        }
        
        # Add blocking opportunities if requested
        if request_model.include_blocking_opportunities:
            blocking_opportunities = []
            for opp in pattern_detection.blocking_opportunities:
                blocking_opportunities.append({
                    'target_player': opp.target_player,
                    'target_pattern_line': opp.target_pattern_line,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'blocking_tiles_available': opp.blocking_tiles_available,
                    'blocking_factories': opp.blocking_factories,
                    'blocking_center': opp.blocking_center,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "HIGH" if opp.urgency_score > 0.8 else "MEDIUM" if opp.urgency_score > 0.6 else "LOW",
                    'description': opp.description
                })
            response['blocking_opportunities'] = blocking_opportunities
        
        # Add move suggestions if requested
        if request_model.include_move_suggestions and pattern_detection.blocking_opportunities:
            move_suggestions = detector.get_blocking_move_suggestions(
                state, request_model.current_player, pattern_detection.blocking_opportunities
            )
            response['move_suggestions'] = move_suggestions
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Pattern detection error: {str(e)}'}), 500


@validation_bp.route('/detect-scoring-optimization', methods=['POST'])
def detect_scoring_optimization():
    """Detect scoring optimization opportunities in the current position."""
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
            request_model = ScoringOptimizationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the scoring optimization detector
        from analysis_engine.comprehensive_patterns.azul_scoring_optimization import AzulScoringOptimizationDetector
        detector = AzulScoringOptimizationDetector()
        
        # Detect scoring optimization opportunities
        optimization_detection = detector.detect_scoring_optimization(state, request_model.current_player)
        # Prepare response
        response = {
            'total_opportunities': optimization_detection.total_opportunities,
            'total_potential_bonus': optimization_detection.total_potential_bonus,
            'confidence_score': optimization_detection.confidence_score,
            'opportunities_detected': True if optimization_detection.total_opportunities > 0 else False,
            'multiplier_opportunities': []  # Add empty list for multiplier opportunities
        }
        # Add wall completion opportunities if requested
        if request_model.include_wall_completion:
            wall_opportunities = []
            for opp in optimization_detection.wall_completion_opportunities:
                wall_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['wall_completion_opportunities'] = wall_opportunities
        # Add pattern line optimization opportunities if requested
        if request_model.include_pattern_line_optimization:
            pattern_line_opportunities = []
            for opp in optimization_detection.pattern_line_opportunities:
                pattern_line_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['pattern_line_opportunities'] = pattern_line_opportunities
        # Add floor line optimization opportunities if requested
        if request_model.include_floor_line_optimization:
            floor_line_opportunities = []
            for opp in optimization_detection.floor_line_opportunities:
                floor_line_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}"),
                    'bonus_value': opp.bonus_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'tiles_needed': opp.tiles_needed,
                    'tiles_available': opp.tiles_available,
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description
                })
            response['floor_line_opportunities'] = floor_line_opportunities
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Scoring optimization detection error: {str(e)}'}), 500


@validation_bp.route('/detect-floor-line-patterns', methods=['POST'])
def detect_floor_line_patterns():
    """Detect floor line management patterns in the current position."""
    try:
        # Handle malformed JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse the request
        try:
            request_model = FloorLinePatternRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request format: {str(e)}'}), 400
        
        # Parse FEN string to get game state
        try:
            state = parse_fen_string(request_model.fen_string)
        except Exception as e:
            return jsonify({'error': f'Invalid FEN string: {str(e)}'}), 400
        
        # Import and use the floor line pattern detector
        from analysis_engine.comprehensive_patterns.azul_floor_line_patterns import AzulFloorLinePatternDetector
        detector = AzulFloorLinePatternDetector()
        
        # Detect floor line patterns
        pattern_detection = detector.detect_floor_line_patterns(state, request_model.current_player)
        
        # Prepare response
        response = {
            'total_opportunities': pattern_detection.total_opportunities,
            'total_penalty_risk': pattern_detection.total_penalty_risk,
            'confidence_score': pattern_detection.confidence_score,
            'patterns_detected': True if pattern_detection.total_opportunities > 0 else False
        }
        
        # Add risk mitigation opportunities if requested
        if request_model.include_risk_mitigation:
            risk_mitigation_opportunities = []
            for opp in pattern_detection.risk_mitigation_opportunities:
                risk_mitigation_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['risk_mitigation_opportunities'] = risk_mitigation_opportunities
        
        # Add timing optimization opportunities if requested
        if request_model.include_timing_optimization:
            timing_optimization_opportunities = []
            for opp in pattern_detection.timing_optimization_opportunities:
                timing_optimization_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['timing_optimization_opportunities'] = timing_optimization_opportunities
        
        # Add trade-off opportunities if requested
        if request_model.include_trade_offs:
            trade_off_opportunities = []
            for opp in pattern_detection.trade_off_opportunities:
                trade_off_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['trade_off_opportunities'] = trade_off_opportunities
        
        # Add endgame management opportunities if requested
        if request_model.include_endgame_management:
            endgame_management_opportunities = []
            for opp in pattern_detection.endgame_management_opportunities:
                endgame_management_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['endgame_management_opportunities'] = endgame_management_opportunities
        
        # Add blocking opportunities if requested
        if request_model.include_blocking_opportunities:
            blocking_opportunities = []
            for opp in pattern_detection.blocking_opportunities:
                blocking_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['blocking_opportunities'] = blocking_opportunities
        
        # Add efficiency opportunities if requested
        if request_model.include_efficiency_opportunities:
            efficiency_opportunities = []
            for opp in pattern_detection.efficiency_opportunities:
                efficiency_opportunities.append({
                    'opportunity_type': opp.opportunity_type,
                    'target_position': opp.target_position,
                    'target_color': opp.target_color,
                    'target_color_name': detector.color_names.get(opp.target_color, f"color {opp.target_color}") if opp.target_color else None,
                    'current_floor_tiles': opp.current_floor_tiles,
                    'potential_penalty': opp.potential_penalty,
                    'penalty_reduction': opp.penalty_reduction,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "CRITICAL" if opp.urgency_score >= 9.0 else "HIGH" if opp.urgency_score >= 7.0 else "MEDIUM" if opp.urgency_score >= 4.0 else "LOW",
                    'risk_assessment': opp.risk_assessment,
                    'description': opp.description,
                    'strategic_value': opp.strategic_value
                })
            response['efficiency_opportunities'] = efficiency_opportunities
        
        # Add move suggestions if requested
        if request_model.include_move_suggestions:
            all_opportunities = (pattern_detection.risk_mitigation_opportunities + 
                               pattern_detection.timing_optimization_opportunities + 
                               pattern_detection.trade_off_opportunities + 
                               pattern_detection.endgame_management_opportunities + 
                               pattern_detection.blocking_opportunities + 
                               pattern_detection.efficiency_opportunities)
            
            move_suggestions = []
            for opp in all_opportunities:
                if opp.move_suggestions:
                    move_suggestions.extend(opp.move_suggestions)
            
            response['move_suggestions'] = move_suggestions
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Floor line pattern detection error: {str(e)}'}), 500 


@validation_bp.route('/detect-comprehensive-patterns', methods=['POST'])
def detect_comprehensive_patterns():
    """Detect comprehensive patterns using the enhanced pattern detector with taxonomy."""
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
        
        # Import and use the enhanced pattern detector
        from analysis_engine.comprehensive_patterns.enhanced_pattern_detector import EnhancedPatternDetector
        detector = EnhancedPatternDetector()
        
        # Detect comprehensive patterns
        comprehensive_analysis = detector.detect_patterns_comprehensive(state, request_model.current_player)
        
        # Prepare response with taxonomy information
        response = {
            'success': True,
            'comprehensive_analysis': True,
            'total_patterns': comprehensive_analysis.total_patterns,
            'quality_metrics': {
                'coverage_score': comprehensive_analysis.analysis_quality.get('coverage_score', 0.0),
                'confidence_score': comprehensive_analysis.analysis_quality.get('confidence_score', 0.0),
                'complexity_score': comprehensive_analysis.analysis_quality.get('complexity_score', 0.0)
            },
            'patterns_by_category': {}
        }
        
        # Organize patterns by taxonomy category
        response['patterns_by_category'] = {
            'TACTICAL': [],
            'STRATEGIC': [],
            'ENDGAME': [],
            'META': [],
            'EDGE_CASE': []
        }
        
        # Add tactical patterns
        for pattern in comprehensive_analysis.tactical_patterns:
            pattern_data = {
                'pattern_name': pattern.pattern_definition.name,
                'category': 'TACTICAL',
                'urgency_level': pattern.urgency_score,
                'complexity_level': pattern.complexity_score,
                'confidence_score': pattern.confidence_score,
                'description': pattern.pattern_definition.description,
                'detection_criteria': pattern.pattern_definition.detection_criteria,
                'success_metrics': pattern.pattern_definition.success_metrics,
                'interaction_effects': pattern.pattern_definition.interaction_effects,
                'examples': pattern.pattern_definition.example_scenarios,
                'counter_patterns': pattern.pattern_definition.counter_patterns,
                'prerequisites': pattern.pattern_definition.prerequisites,
                'alternatives': pattern.pattern_definition.alternatives
            }
            response['patterns_by_category']['TACTICAL'].append(pattern_data)
        
        # Add strategic patterns
        for pattern in comprehensive_analysis.strategic_patterns:
            pattern_data = {
                'pattern_name': pattern.pattern_definition.name,
                'category': 'STRATEGIC',
                'urgency_level': pattern.urgency_score,
                'complexity_level': pattern.complexity_score,
                'confidence_score': pattern.confidence_score,
                'description': pattern.pattern_definition.description,
                'detection_criteria': pattern.pattern_definition.detection_criteria,
                'success_metrics': pattern.pattern_definition.success_metrics,
                'interaction_effects': pattern.pattern_definition.interaction_effects,
                'examples': pattern.pattern_definition.example_scenarios,
                'counter_patterns': pattern.pattern_definition.counter_patterns,
                'prerequisites': pattern.pattern_definition.prerequisites,
                'alternatives': pattern.pattern_definition.alternatives
            }
            response['patterns_by_category']['STRATEGIC'].append(pattern_data)
        
        # Add endgame patterns
        for pattern in comprehensive_analysis.endgame_patterns:
            pattern_data = {
                'pattern_name': pattern.pattern_definition.name,
                'category': 'ENDGAME',
                'urgency_level': pattern.urgency_score,
                'complexity_level': pattern.complexity_score,
                'confidence_score': pattern.confidence_score,
                'description': pattern.pattern_definition.description,
                'detection_criteria': pattern.pattern_definition.detection_criteria,
                'success_metrics': pattern.pattern_definition.success_metrics,
                'interaction_effects': pattern.pattern_definition.interaction_effects,
                'examples': pattern.pattern_definition.example_scenarios,
                'counter_patterns': pattern.pattern_definition.counter_patterns,
                'prerequisites': pattern.pattern_definition.prerequisites,
                'alternatives': pattern.pattern_definition.alternatives
            }
            response['patterns_by_category']['ENDGAME'].append(pattern_data)
        
        # Add meta patterns
        for pattern in comprehensive_analysis.meta_patterns:
            pattern_data = {
                'pattern_name': pattern.pattern_definition.name,
                'category': 'META',
                'urgency_level': pattern.urgency_score,
                'complexity_level': pattern.complexity_score,
                'confidence_score': pattern.confidence_score,
                'description': pattern.pattern_definition.description,
                'detection_criteria': pattern.pattern_definition.detection_criteria,
                'success_metrics': pattern.pattern_definition.success_metrics,
                'interaction_effects': pattern.pattern_definition.interaction_effects,
                'examples': pattern.pattern_definition.example_scenarios,
                'counter_patterns': pattern.pattern_definition.counter_patterns,
                'prerequisites': pattern.pattern_definition.prerequisites,
                'alternatives': pattern.pattern_definition.alternatives
            }
            response['patterns_by_category']['META'].append(pattern_data)
        
        # Add edge case patterns
        for pattern in comprehensive_analysis.edge_case_patterns:
            pattern_data = {
                'pattern_name': pattern.pattern_definition.name,
                'category': 'EDGE_CASE',
                'urgency_level': pattern.urgency_score,
                'complexity_level': pattern.complexity_score,
                'confidence_score': pattern.confidence_score,
                'description': pattern.pattern_definition.description,
                'detection_criteria': pattern.pattern_definition.detection_criteria,
                'success_metrics': pattern.pattern_definition.success_metrics,
                'interaction_effects': pattern.pattern_definition.interaction_effects,
                'examples': pattern.pattern_definition.example_scenarios,
                'counter_patterns': pattern.pattern_definition.counter_patterns,
                'prerequisites': pattern.pattern_definition.prerequisites,
                'alternatives': pattern.pattern_definition.alternatives
            }
            response['patterns_by_category']['EDGE_CASE'].append(pattern_data)
        
        # Add pattern interactions if available
        if comprehensive_analysis.pattern_interactions:
            response['pattern_interactions'] = []
            for key, interaction in comprehensive_analysis.pattern_interactions.items():
                interaction_data = {
                    'pattern_a': key.split('_')[0] if '_' in key else key,
                    'pattern_b': key.split('_')[1] if '_' in key else 'unknown',
                    'interaction_type': interaction.get('type', 'unknown'),
                    'strength': interaction.get('strength', 0.0),
                    'description': interaction.get('description', 'Pattern interaction detected')
                }
                response['pattern_interactions'].append(interaction_data)
        
        # Add backward compatibility with existing pattern detection
        response['backward_compatible'] = {
            'total_patterns': comprehensive_analysis.total_patterns,
            'confidence_score': comprehensive_analysis.confidence_score,
            'patterns_detected': comprehensive_analysis.total_patterns > 0
        }
        
        # Add blocking opportunities if requested
        if request_model.include_blocking_opportunities and comprehensive_analysis.blocking_opportunities:
            blocking_opportunities = []
            for opp in comprehensive_analysis.blocking_opportunities:
                blocking_opportunities.append({
                    'target_player': opp.target_player,
                    'target_pattern_line': opp.target_pattern_line,
                    'target_color': opp.target_color,
                    'blocking_tiles_available': opp.blocking_tiles_available,
                    'blocking_factories': opp.blocking_factories,
                    'blocking_center': opp.blocking_center,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': "HIGH" if opp.urgency_score > 0.8 else "MEDIUM" if opp.urgency_score > 0.6 else "LOW",
                    'description': opp.description
                })
            response['backward_compatible']['blocking_opportunities'] = blocking_opportunities
        
        # Add move suggestions if requested
        if request_model.include_move_suggestions and comprehensive_analysis.blocking_opportunities:
            move_suggestions = detector.get_blocking_move_suggestions(
                state, request_model.current_player, comprehensive_analysis.blocking_opportunities
            )
            response['backward_compatible']['move_suggestions'] = move_suggestions
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Comprehensive pattern detection error: {str(e)}'}), 500 