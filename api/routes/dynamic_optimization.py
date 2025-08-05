from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from typing import Dict, Any, Optional, List
import time

from ..models.validation import PatternDetectionRequest
from ..utils import parse_fen_string
from ..auth import require_session
from analysis_engine.mathematical_optimization.dynamic_optimizer import (
    AzulDynamicOptimizer, EndgamePhase, MultiTurnPlan
)

dynamic_optimization_bp = Blueprint('dynamic_optimization', __name__)


@dynamic_optimization_bp.route('/evaluate-endgame', methods=['POST'])
@require_session
def evaluate_endgame():
    """
    Evaluate the current game state for endgame optimization.
    
    Expected JSON payload:
    {
        "fen_string": "game state in FEN format",
        "current_player": 0,
        "evaluation_depth": 3
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Parse request data
        fen_string = data.get('fen_string')
        current_player = data.get('current_player', 0)
        evaluation_depth = data.get('evaluation_depth', 3)
        
        if not fen_string:
            return jsonify({'error': 'fen_string is required'}), 400
        
        # Parse game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({'error': 'Invalid FEN string'}), 400
        
        # Initialize dynamic optimizer
        optimizer = AzulDynamicOptimizer(max_depth=evaluation_depth)
        
        # Evaluate endgame
        start_time = time.time()
        endgame_evaluation = optimizer.evaluate_endgame(state, current_player)
        evaluation_time = time.time() - start_time
        
        # Prepare response
        response = {
            'success': True,
            'endgame_evaluation': endgame_evaluation,
            'evaluation_time': evaluation_time,
            'game_phase': endgame_evaluation['game_phase'],
            'recommendations': _generate_endgame_recommendations(endgame_evaluation),
            'risk_assessment': _assess_endgame_risks(endgame_evaluation)
        }
        
        return jsonify(response), 200
        
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in evaluate_endgame: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@dynamic_optimization_bp.route('/plan-multi-turn', methods=['POST'])
@require_session
def plan_multi_turn():
    """
    Plan optimal move sequence for multiple turns ahead.
    
    Expected JSON payload:
    {
        "fen_string": "game state in FEN format",
        "current_player": 0,
        "turns_ahead": 3,
        "planning_depth": 5
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Parse request data
        fen_string = data.get('fen_string')
        current_player = data.get('current_player', 0)
        turns_ahead = data.get('turns_ahead', 3)
        planning_depth = data.get('planning_depth', 5)
        
        if not fen_string:
            return jsonify({'error': 'fen_string is required'}), 400
        
        # Parse game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({'error': 'Invalid FEN string'}), 400
        
        # Initialize dynamic optimizer
        optimizer = AzulDynamicOptimizer(max_depth=planning_depth)
        
        # Plan multi-turn sequence
        start_time = time.time()
        multi_turn_plan = optimizer.plan_optimal_sequence(state, current_player, turns_ahead)
        planning_time = time.time() - start_time
        
        # Prepare response
        response = {
            'success': True,
            'multi_turn_plan': {
                'total_expected_score': multi_turn_plan.total_expected_score,
                'move_sequence': multi_turn_plan.move_sequence,
                'confidence_score': multi_turn_plan.confidence_score,
                'risk_assessment': multi_turn_plan.risk_assessment,
                'alternative_plans': multi_turn_plan.alternative_plans,
                'endgame_evaluation': multi_turn_plan.endgame_evaluation
            },
            'planning_time': planning_time,
            'recommendations': _generate_planning_recommendations(multi_turn_plan),
            'execution_guidance': _generate_execution_guidance(multi_turn_plan)
        }
        
        return jsonify(response), 200
        
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in plan_multi_turn: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@dynamic_optimization_bp.route('/analyze-game-phase', methods=['POST'])
@require_session
def analyze_game_phase():
    """
    Analyze the current game phase and provide strategic insights.
    
    Expected JSON payload:
    {
        "fen_string": "game state in FEN format",
        "current_player": 0
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Parse request data
        fen_string = data.get('fen_string')
        current_player = data.get('current_player', 0)
        
        if not fen_string:
            return jsonify({'error': 'fen_string is required'}), 400
        
        # Parse game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({'error': 'Invalid FEN string'}), 400
        
        # Initialize dynamic optimizer
        optimizer = AzulDynamicOptimizer()
        
        # Analyze game phase
        endgame_evaluation = optimizer.evaluate_endgame(state, current_player)
        game_phase = EndgamePhase(endgame_evaluation['game_phase'])
        
        # Generate phase-specific analysis
        phase_analysis = _analyze_game_phase(state, current_player, game_phase)
        
        # Prepare response
        response = {
            'success': True,
            'game_phase': game_phase.value,
            'phase_analysis': phase_analysis,
            'strategic_insights': _generate_strategic_insights(game_phase, endgame_evaluation),
            'phase_recommendations': _generate_phase_recommendations(game_phase, endgame_evaluation)
        }
        
        return jsonify(response), 200
        
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in analyze_game_phase: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@dynamic_optimization_bp.route('/optimize-endgame-strategy', methods=['POST'])
@require_session
def optimize_endgame_strategy():
    """
    Optimize strategy specifically for endgame scenarios.
    
    Expected JSON payload:
    {
        "fen_string": "game state in FEN format",
        "current_player": 0,
        "strategy_focus": "wall_completion|penalty_minimization|scoring_maximization"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Parse request data
        fen_string = data.get('fen_string')
        current_player = data.get('current_player', 0)
        strategy_focus = data.get('strategy_focus', 'scoring_maximization')
        
        if not fen_string:
            return jsonify({'error': 'fen_string is required'}), 400
        
        # Parse game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({'error': 'Invalid FEN string'}), 400
        
        # Initialize dynamic optimizer
        optimizer = AzulDynamicOptimizer()
        
        # Evaluate endgame
        endgame_evaluation = optimizer.evaluate_endgame(state, current_player)
        
        # Generate strategy-specific optimization
        strategy_optimization = _optimize_endgame_strategy(state, current_player, strategy_focus, endgame_evaluation)
        
        # Prepare response
        response = {
            'success': True,
            'strategy_focus': strategy_focus,
            'endgame_evaluation': endgame_evaluation,
            'strategy_optimization': strategy_optimization,
            'recommendations': _generate_strategy_recommendations(strategy_focus, strategy_optimization)
        }
        
        return jsonify(response), 200
        
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in optimize_endgame_strategy: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


def _generate_endgame_recommendations(evaluation: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on endgame evaluation."""
    recommendations = []
    
    # Wall completion recommendations
    wall_completion = evaluation.get('wall_completion', 0)
    if wall_completion < 50:
        recommendations.append("Focus on completing wall tiles to improve scoring potential")
    elif wall_completion > 80:
        recommendations.append("Excellent wall completion - focus on maximizing scoring from completed areas")
    
    # Floor line penalty recommendations
    floor_penalty = evaluation.get('floor_line_penalty', 0)
    if floor_penalty > 5:
        recommendations.append("High floor line penalty - prioritize moving tiles to pattern lines")
    
    # Pattern line efficiency recommendations
    pattern_efficiency = evaluation.get('pattern_line_efficiency', 0)
    if pattern_efficiency < 0.5:
        recommendations.append("Low pattern line efficiency - optimize tile placement in pattern lines")
    
    # Factory control recommendations
    factory_control = evaluation.get('factory_control', 0)
    if factory_control < 0.3:
        recommendations.append("Limited factory control - consider strategic tile selection")
    
    return recommendations


def _assess_endgame_risks(evaluation: Dict[str, Any]) -> Dict[str, float]:
    """Assess risks based on endgame evaluation."""
    risks = {}
    
    # Wall completion risk
    wall_completion = evaluation.get('wall_completion', 0)
    risks['wall_completion_risk'] = max(0, 1.0 - (wall_completion / 100.0))
    
    # Floor line penalty risk
    floor_penalty = evaluation.get('floor_line_penalty', 0)
    risks['floor_line_risk'] = min(1.0, floor_penalty / 10.0)
    
    # Pattern line efficiency risk
    pattern_efficiency = evaluation.get('pattern_line_efficiency', 0)
    risks['pattern_line_risk'] = 1.0 - pattern_efficiency
    
    # Factory control risk
    factory_control = evaluation.get('factory_control', 0)
    risks['factory_control_risk'] = 1.0 - factory_control
    
    return risks


def _generate_planning_recommendations(plan: MultiTurnPlan) -> List[str]:
    """Generate recommendations based on multi-turn plan."""
    recommendations = []
    
    # Confidence-based recommendations
    confidence = plan.confidence_score
    if confidence < 0.5:
        recommendations.append("Low confidence in plan - consider alternative strategies")
    elif confidence > 0.8:
        recommendations.append("High confidence plan - execute with focus")
    
    # Risk-based recommendations
    overall_risk = plan.risk_assessment.get('overall_risk', 0)
    if overall_risk > 0.7:
        recommendations.append("High risk plan - monitor execution carefully")
    
    # Score-based recommendations
    expected_score = plan.total_expected_score
    if expected_score > 50:
        recommendations.append("High scoring potential - prioritize execution")
    
    return recommendations


def _generate_execution_guidance(plan: MultiTurnPlan) -> Dict[str, Any]:
    """Generate execution guidance for the multi-turn plan."""
    guidance = {
        'execution_priority': 'high' if plan.confidence_score > 0.7 else 'medium',
        'risk_monitoring': plan.risk_assessment.get('overall_risk', 0) > 0.5,
        'alternative_ready': len(plan.alternative_plans) > 0,
        'key_moves': plan.move_sequence[:2] if plan.move_sequence else [],
        'success_metrics': {
            'target_score': plan.total_expected_score,
            'confidence_threshold': 0.6,
            'risk_tolerance': 0.3
        }
    }
    
    return guidance


def _analyze_game_phase(state, player_id: int, game_phase: EndgamePhase) -> Dict[str, Any]:
    """Analyze the current game phase."""
    # Calculate current round from agent trace actions
    if hasattr(state, 'agents') and state.agents:
        # Get the first agent's trace to determine round
        agent = state.agents[0]
        if hasattr(agent, 'agent_trace') and agent.agent_trace:
            current_round = len(agent.agent_trace.actions)
        else:
            current_round = 0
    else:
        current_round = 0
    
    analysis = {
        'phase': game_phase.value,
        'round_number': current_round,
        'turns_remaining': max(0, 20 - current_round * 4),  # Approximate
        'phase_characteristics': _get_phase_characteristics(game_phase),
        'strategic_focus': _get_phase_strategic_focus(game_phase)
    }
    
    return analysis


def _get_phase_characteristics(game_phase: EndgamePhase) -> Dict[str, Any]:
    """Get characteristics of the current game phase."""
    characteristics = {
        EndgamePhase.EARLY_GAME: {
            'tile_abundance': 'high',
            'planning_horizon': 'long',
            'risk_tolerance': 'medium',
            'scoring_opportunities': 'developing'
        },
        EndgamePhase.MID_GAME: {
            'tile_abundance': 'medium',
            'planning_horizon': 'medium',
            'risk_tolerance': 'medium',
            'scoring_opportunities': 'expanding'
        },
        EndgamePhase.LATE_GAME: {
            'tile_abundance': 'low',
            'planning_horizon': 'short',
            'risk_tolerance': 'low',
            'scoring_opportunities': 'maximizing'
        },
        EndgamePhase.ENDGAME: {
            'tile_abundance': 'very_low',
            'planning_horizon': 'immediate',
            'risk_tolerance': 'very_low',
            'scoring_opportunities': 'final'
        }
    }
    
    return characteristics.get(game_phase, {})


def _get_phase_strategic_focus(game_phase: EndgamePhase) -> List[str]:
    """Get strategic focus areas for the current game phase."""
    focus_areas = {
        EndgamePhase.EARLY_GAME: [
            "Establish wall foundation",
            "Build pattern line efficiency",
            "Avoid floor line penalties",
            "Develop scoring opportunities"
        ],
        EndgamePhase.MID_GAME: [
            "Complete wall sections",
            "Maximize pattern line scoring",
            "Minimize floor line penalties",
            "Optimize tile selection"
        ],
        EndgamePhase.LATE_GAME: [
            "Complete wall rows/columns",
            "Maximize immediate scoring",
            "Minimize penalties",
            "Secure victory conditions"
        ],
        EndgamePhase.ENDGAME: [
            "Final scoring optimization",
            "Penalty minimization",
            "Victory condition achievement",
            "Defensive play if needed"
        ]
    }
    
    return focus_areas.get(game_phase, [])


def _generate_strategic_insights(game_phase: EndgamePhase, evaluation: Dict[str, Any]) -> List[str]:
    """Generate strategic insights for the current game phase."""
    insights = []
    
    if game_phase == EndgamePhase.EARLY_GAME:
        insights.append("Early game: Focus on building strong foundation")
        insights.append("Establish efficient pattern line usage")
    elif game_phase == EndgamePhase.MID_GAME:
        insights.append("Mid game: Optimize scoring opportunities")
        insights.append("Balance wall completion with immediate scoring")
    elif game_phase == EndgamePhase.LATE_GAME:
        insights.append("Late game: Maximize final scoring potential")
        insights.append("Complete key wall sections for bonuses")
    elif game_phase == EndgamePhase.ENDGAME:
        insights.append("Endgame: Final optimization for victory")
        insights.append("Minimize penalties and maximize bonuses")
    
    return insights


def _generate_phase_recommendations(game_phase: EndgamePhase, evaluation: Dict[str, Any]) -> List[str]:
    """Generate phase-specific recommendations."""
    recommendations = []
    
    wall_completion = evaluation.get('wall_completion', 0)
    floor_penalty = evaluation.get('floor_line_penalty', 0)
    
    if game_phase == EndgamePhase.EARLY_GAME:
        if wall_completion < 20:
            recommendations.append("Focus on establishing wall foundation")
        if floor_penalty > 3:
            recommendations.append("Avoid floor line penalties in early game")
    elif game_phase == EndgamePhase.MID_GAME:
        if wall_completion < 50:
            recommendations.append("Accelerate wall completion")
        recommendations.append("Optimize pattern line efficiency")
    elif game_phase == EndgamePhase.LATE_GAME:
        if wall_completion < 80:
            recommendations.append("Complete key wall sections")
        recommendations.append("Maximize immediate scoring opportunities")
    elif game_phase == EndgamePhase.ENDGAME:
        recommendations.append("Final scoring optimization")
        recommendations.append("Minimize all penalties")
    
    return recommendations


def _optimize_endgame_strategy(state, player_id: int, strategy_focus: str, 
                             evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize strategy based on specific focus area."""
    optimization = {
        'strategy_focus': strategy_focus,
        'optimization_actions': [],
        'expected_improvement': 0.0,
        'implementation_priority': 'medium'
    }
    
    if strategy_focus == 'wall_completion':
        wall_completion = evaluation.get('wall_completion', 0)
        if wall_completion < 70:
            optimization['optimization_actions'].append("Prioritize tiles that complete wall sections")
            optimization['optimization_actions'].append("Focus on completing rows and columns")
            optimization['expected_improvement'] = min(30, 100 - wall_completion)
    
    elif strategy_focus == 'penalty_minimization':
        floor_penalty = evaluation.get('floor_line_penalty', 0)
        if floor_penalty > 5:
            optimization['optimization_actions'].append("Move tiles from floor to pattern lines")
            optimization['optimization_actions'].append("Avoid taking tiles that would go to floor")
            optimization['expected_improvement'] = min(10, floor_penalty)
    
    elif strategy_focus == 'scoring_maximization':
        pattern_efficiency = evaluation.get('pattern_line_efficiency', 0)
        if pattern_efficiency < 0.7:
            optimization['optimization_actions'].append("Optimize pattern line usage")
            optimization['optimization_actions'].append("Maximize scoring from completed pattern lines")
            optimization['expected_improvement'] = (0.7 - pattern_efficiency) * 50
    
    return optimization


def _generate_strategy_recommendations(strategy_focus: str, optimization: Dict[str, Any]) -> List[str]:
    """Generate recommendations for the specific strategy focus."""
    recommendations = []
    
    actions = optimization.get('optimization_actions', [])
    for action in actions:
        recommendations.append(f"Strategy: {action}")
    
    expected_improvement = optimization.get('expected_improvement', 0)
    if expected_improvement > 0:
        recommendations.append(f"Expected improvement: {expected_improvement:.1f} points")
    
    return recommendations 