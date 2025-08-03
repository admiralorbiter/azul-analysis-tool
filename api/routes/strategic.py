"""
Strategic Analysis API Routes

This module contains all strategic pattern analysis endpoints for the Azul Solver & Analysis Toolkit.
"""

import json
import time
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from ..auth import require_session
from ..utils import parse_fen_string, format_move
from core.azul_strategic_patterns import StrategicPatternDetector
from core.azul_strategic_utils import StrategicAnalysisCache, timeout, StrategicAnalysisReporter

# Create Flask blueprint for strategic analysis endpoints
strategic_bp = Blueprint('strategic', __name__)

# Initialize strategic pattern detector
strategic_detector = StrategicPatternDetector()
strategic_cache = StrategicAnalysisCache()


@strategic_bp.route('/detect-factory-control', methods=['POST'])
def detect_factory_control():
    """
    Detect factory control opportunities in a position.
    
    POST /api/v1/detect-factory-control
    {
        "fen_string": "fen_string",
        "player_id": 0,
        "timeout": 5
    }
    
    Returns:
        Factory control opportunities with strategic analysis
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        fen_string = data.get('fen_string')
        player_id = data.get('player_id', data.get('current_player', 0))  # Handle both parameter names
        timeout_seconds = data.get('timeout', 5)
        
        if not fen_string:
            return jsonify({
                'error': 'Invalid request',
                'message': 'fen_string is required'
            }), 400
        
        # Parse FEN string to get game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({
                'error': 'Invalid FEN string',
                'message': 'Could not parse game state from FEN string'
            }), 400
        
        # Check cache first
        cache_key = f"factory_control_{fen_string}_{player_id}"
        cached_result = strategic_cache.get_cached_result(cache_key, "factory_control")
        if cached_result:
            return jsonify({
                'cache_hit': True,
                'analysis_time': cached_result.get('analysis_time', 0),
                'opportunities': cached_result.get('opportunities', []),
                'summary': cached_result.get('summary', {})
            })
        
        # Perform analysis with timeout
        start_time = time.time()
        try:
            with timeout(timeout_seconds):
                opportunities = strategic_detector.factory_control_detector.detect_opportunities(
                    state, player_id
                )
        except TimeoutError:
            return jsonify({
                'error': 'Analysis timeout',
                'message': f'Factory control analysis timed out after {timeout_seconds} seconds'
            }), 408
        
        analysis_time = time.time() - start_time
        
        # Format opportunities for JSON response
        formatted_opportunities = []
        for opp in opportunities:
            formatted_opportunities.append({
                'control_type': opp.control_type,
                'factory_id': opp.factory_id,
                'strategic_value': opp.strategic_value,
                'urgency_score': opp.urgency_score,
                'urgency_level': opp.urgency_level,
                'risk_assessment': opp.risk_assessment,
                'move_suggestions': opp.move_suggestions,
                'confidence': opp.confidence,
                'description': opp.description
            })
        
        # Generate summary
        summary = {
            'total_opportunities': len(opportunities),
            'high_urgency_count': len([o for o in opportunities if o.urgency_level in ['CRITICAL', 'HIGH']]),
            'average_strategic_value': sum(o.strategic_value for o in opportunities) / len(opportunities) if opportunities else 0,
            'analysis_time': analysis_time
        }
        
        # Cache results
        result_data = {
            'opportunities': formatted_opportunities,
            'summary': summary,
            'analysis_time': analysis_time
        }
        strategic_cache.cache_result(cache_key, "factory_control", result_data)
        
        return jsonify({
            'cache_hit': False,
            'opportunities': formatted_opportunities,
            'summary': summary,
            'analysis_time': analysis_time
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in factory control analysis: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to analyze factory control opportunities'
        }), 500


@strategic_bp.route('/analyze-endgame-scenarios', methods=['POST'])
def analyze_endgame_scenarios():
    """
    Analyze endgame counting scenarios in a position.
    
    POST /api/v1/analyze-endgame-scenarios
    {
        "fen_string": "fen_string",
        "player_id": 0,
        "timeout": 10
    }
    
    Returns:
        Endgame scenarios with tile counting and optimization
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        fen_string = data.get('fen_string')
        player_id = data.get('player_id', data.get('current_player', 0))  # Handle both parameter names
        timeout_seconds = data.get('timeout', 10)
        
        if not fen_string:
            return jsonify({
                'error': 'Invalid request',
                'message': 'fen_string is required'
            }), 400
        
        # Parse FEN string to get game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({
                'error': 'Invalid FEN string',
                'message': 'Could not parse game state from FEN string'
            }), 400
        
        # Check cache first
        cache_key = f"endgame_scenarios_{fen_string}_{player_id}"
        cached_result = strategic_cache.get_cached_result(cache_key, "endgame_scenarios")
        if cached_result:
            return jsonify({
                'cache_hit': True,
                'analysis_time': cached_result.get('analysis_time', 0),
                'scenarios': cached_result.get('scenarios', []),
                'summary': cached_result.get('summary', {})
            })
        
        # Perform analysis with timeout
        start_time = time.time()
        try:
            with timeout(timeout_seconds):
                scenarios = strategic_detector.endgame_counting_detector.analyze_scenarios(
                    state, player_id
                )
        except TimeoutError:
            return jsonify({
                'error': 'Analysis timeout',
                'message': f'Endgame analysis timed out after {timeout_seconds} seconds'
            }), 408
        
        analysis_time = time.time() - start_time
        
        # Format scenarios for JSON response
        formatted_scenarios = []
        for scenario in scenarios:
            formatted_scenarios.append({
                'scenario_type': scenario.scenario_type,
                'scoring_potential': scenario.scoring_potential,
                'optimal_sequence': scenario.optimal_sequence,
                'risk_level': scenario.risk_level,
                'confidence': scenario.confidence,
                'description': scenario.description,
                'remaining_tiles': scenario.remaining_tiles,
                'urgency_score': scenario.urgency_score
            })
        
        # Generate summary
        summary = {
            'total_scenarios': len(scenarios),
            'high_potential_count': len([s for s in scenarios if s.scoring_potential > 0.7]),
            'average_conservation_score': sum(s.tile_conservation_score for s in scenarios) / len(scenarios) if scenarios else 0,
            'analysis_time': analysis_time
        }
        
        # Cache results
        result_data = {
            'scenarios': formatted_scenarios,
            'summary': summary,
            'analysis_time': analysis_time
        }
        strategic_cache.set(cache_key, result_data)
        
        return jsonify({
            'cache_hit': False,
            'scenarios': formatted_scenarios,
            'summary': summary,
            'analysis_time': analysis_time
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in endgame scenario analysis: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to analyze endgame scenarios'
        }), 500


@strategic_bp.route('/analyze-risk-reward', methods=['POST'])
def analyze_risk_reward():
    """
    Analyze risk/reward scenarios in a position.
    
    POST /api/v1/analyze-risk-reward
    {
        "fen_string": "fen_string",
        "player_id": 0,
        "timeout": 8
    }
    
    Returns:
        Risk/reward scenarios with strategic decision analysis
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        fen_string = data.get('fen_string')
        player_id = data.get('player_id', data.get('current_player', 0))  # Handle both parameter names
        timeout_seconds = data.get('timeout', 8)
        
        if not fen_string:
            return jsonify({
                'error': 'Invalid request',
                'message': 'fen_string is required'
            }), 400
        
        # Parse FEN string to get game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({
                'error': 'Invalid FEN string',
                'message': 'Could not parse game state from FEN string'
            }), 400
        
        # Check cache first
        cache_key = f"risk_reward_{fen_string}_{player_id}"
        cached_result = strategic_cache.get_cached_result(cache_key, "risk_reward")
        if cached_result:
            return jsonify({
                'cache_hit': True,
                'analysis_time': cached_result.get('analysis_time', 0),
                'scenarios': cached_result.get('scenarios', []),
                'summary': cached_result.get('summary', {})
            })
        
        # Perform analysis with timeout
        start_time = time.time()
        try:
            with timeout(timeout_seconds):
                scenarios = strategic_detector.risk_reward_analyzer.analyze_scenarios(
                    state, player_id
                )
        except TimeoutError:
            return jsonify({
                'error': 'Analysis timeout',
                'message': f'Risk/reward analysis timed out after {timeout_seconds} seconds'
            }), 408
        
        analysis_time = time.time() - start_time
        
        # Format scenarios for JSON response
        formatted_scenarios = []
        for scenario in scenarios:
            formatted_scenarios.append({
                'scenario_type': scenario.scenario_type,
                'risk_score': scenario.risk_score,
                'reward_score': scenario.reward_score,
                'risk_reward_ratio': scenario.risk_reward_ratio,
                'game_phase': scenario.game_phase,
                'risk_factors': scenario.risk_factors,
                'reward_factors': scenario.reward_factors,
                'recommendation': scenario.recommendation,
                'confidence': scenario.confidence,
                'description': scenario.description
            })
        
        # Generate summary
        summary = {
            'total_scenarios': len(scenarios),
            'high_risk_count': len([s for s in scenarios if s.risk_score > 0.7]),
            'high_reward_count': len([s for s in scenarios if s.reward_score > 0.7]),
            'average_risk_reward_ratio': sum(s.risk_reward_ratio for s in scenarios) / len(scenarios) if scenarios else 0,
            'analysis_time': analysis_time
        }
        
        # Cache results
        result_data = {
            'scenarios': formatted_scenarios,
            'summary': summary,
            'analysis_time': analysis_time
        }
        strategic_cache.cache_result(cache_key, "risk_reward", result_data)
        
        return jsonify({
            'cache_hit': False,
            'scenarios': formatted_scenarios,
            'summary': summary,
            'analysis_time': analysis_time
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in risk/reward analysis: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to analyze risk/reward scenarios'
        }), 500


@strategic_bp.route('/analyze-strategic-patterns', methods=['POST'])
def analyze_strategic_patterns():
    """
    Comprehensive strategic pattern analysis.
    
    POST /api/v1/analyze-strategic-patterns
    {
        "fen_string": "fen_string",
        "player_id": 0,
        "timeout": 15,
        "include_factory_control": true,
        "include_endgame_scenarios": true,
        "include_risk_reward": true
    }
    
    Returns:
        Comprehensive strategic analysis with all pattern types
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        fen_string = data.get('fen_string')
        player_id = data.get('player_id', data.get('current_player', 0))  # Handle both parameter names
        timeout_seconds = data.get('timeout', 15)
        include_factory_control = data.get('include_factory_control', True)
        include_endgame_scenarios = data.get('include_endgame_scenarios', True)
        include_risk_reward = data.get('include_risk_reward', True)
        
        if not fen_string:
            return jsonify({
                'error': 'Invalid request',
                'message': 'fen_string is required'
            }), 400
        
        # Parse FEN string to get game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({
                'error': 'Invalid FEN string',
                'message': 'Could not parse game state from FEN string'
            }), 400
        
        # Check cache first
        cache_key = f"strategic_patterns_{fen_string}_{player_id}_{include_factory_control}_{include_endgame_scenarios}_{include_risk_reward}"
        cached_result = strategic_cache.get_cached_result(cache_key, "strategic_patterns")
        if cached_result:
            return jsonify({
                'cache_hit': True,
                'analysis_time': cached_result.get('analysis_time', 0),
                'strategic_analysis': cached_result.get('strategic_analysis', {}),
                'summary': cached_result.get('summary', {})
            })
        
        # Perform comprehensive analysis with timeout
        start_time = time.time()
        try:
            with timeout(timeout_seconds):
                strategic_analysis = strategic_detector.detect_strategic_patterns(
                    state, player_id
                )
        except TimeoutError:
            return jsonify({
                'error': 'Analysis timeout',
                'message': f'Strategic pattern analysis timed out after {timeout_seconds} seconds'
            }), 408
        
        analysis_time = time.time() - start_time
        
        # Format analysis for JSON response
        formatted_analysis = {
            'factory_control_opportunities': [
                {
                    'control_type': opp.control_type,
                    'factory_id': opp.factory_id,
                    'strategic_value': opp.strategic_value,
                    'urgency_score': opp.urgency_score,
                    'urgency_level': opp.urgency_level,
                    'risk_assessment': opp.risk_assessment,
                    'move_suggestions': opp.move_suggestions,
                    'confidence': opp.confidence,
                    'description': opp.description
                }
                for opp in strategic_analysis.factory_control_opportunities
            ],
            'endgame_scenarios': [
                {
                    'scenario_type': scenario.scenario_type,
                    'scoring_potential': scenario.scoring_potential,
                    'optimal_sequence': scenario.optimal_sequence,
                    'risk_level': scenario.risk_level,
                    'confidence': scenario.confidence,
                    'description': scenario.description,
                    'remaining_tiles': scenario.remaining_tiles,
                    'urgency_score': scenario.urgency_score
                }
                for scenario in strategic_analysis.endgame_scenarios
            ],
            'risk_reward_scenarios': [
                {
                    'scenario_type': scenario.scenario_type,
                    'risk_score': scenario.risk_score,
                    'reward_score': scenario.reward_score,
                    'risk_reward_ratio': scenario.risk_reward_ratio,
                    'game_phase': scenario.game_phase,
                    'risk_factors': scenario.risk_factors,
                    'reward_factors': scenario.reward_factors,
                    'recommendation': scenario.recommendation,
                    'confidence': scenario.confidence,
                    'description': scenario.description
                }
                for scenario in strategic_analysis.risk_reward_scenarios
            ],
            'strategic_move_suggestions': [],  # TODO: Implement move suggestions
            'position_assessment': f"Found {strategic_analysis.total_patterns} strategic patterns with {strategic_analysis.total_strategic_value:.1f} total strategic value",
            'confidence': strategic_analysis.confidence_score
        }
        
        # Generate comprehensive summary
        summary = {
            'total_factory_opportunities': len(strategic_analysis.factory_control_opportunities),
            'total_endgame_scenarios': len(strategic_analysis.endgame_scenarios),
            'total_risk_reward_scenarios': len(strategic_analysis.risk_reward_scenarios),
            'high_urgency_opportunities': len([o for o in strategic_analysis.factory_control_opportunities if o.urgency_level in ['CRITICAL', 'HIGH']]),
            'high_potential_scenarios': len([s for s in strategic_analysis.endgame_scenarios if s.scoring_potential > 0.7]),
            'high_risk_scenarios': len([s for s in strategic_analysis.risk_reward_scenarios if s.risk_score > 0.7]),
            'analysis_time': analysis_time,
            'position_assessment': f"Found {strategic_analysis.total_patterns} strategic patterns with {strategic_analysis.total_strategic_value:.1f} total strategic value",
            'overall_confidence': strategic_analysis.confidence_score
        }
        
        # Cache results
        result_data = {
            'strategic_analysis': formatted_analysis,
            'summary': summary,
            'analysis_time': analysis_time
        }
        strategic_cache.cache_result(cache_key, "strategic_patterns", result_data)
        
        return jsonify({
            'cache_hit': False,
            'strategic_analysis': formatted_analysis,
            'summary': summary,
            'analysis_time': analysis_time
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in comprehensive strategic analysis: {e}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Internal server error',
            'message': f'Failed to analyze strategic patterns: {str(e)}'
        }), 500


@strategic_bp.route('/strategic-analysis/report', methods=['POST'])
def generate_strategic_report():
    """
    Generate a human-readable strategic analysis report.
    
    POST /api/v1/strategic-analysis/report
    {
        "fen_string": "fen_string",
        "player_id": 0,
        "format": "text"  # "text" or "html"
    }
    
    Returns:
        Human-readable strategic analysis report
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        fen_string = data.get('fen_string')
        player_id = data.get('player_id', data.get('current_player', 0))  # Handle both parameter names
        report_format = data.get('format', 'text')
        
        if not fen_string:
            return jsonify({
                'error': 'Invalid request',
                'message': 'fen_string is required'
            }), 400
        
        # Parse FEN string to get game state
        state = parse_fen_string(fen_string)
        if not state:
            return jsonify({
                'error': 'Invalid FEN string',
                'message': 'Could not parse game state from FEN string'
            }), 400
        
        # Perform strategic analysis
        strategic_analysis = strategic_detector.detect_strategic_patterns(state, player_id)
        
        # Generate report
        reporter = StrategicAnalysisReporter()
        if report_format == 'html':
            report = reporter.generate_html_report(strategic_analysis, state, player_id)
        else:
            report = reporter.generate_text_report(strategic_analysis, state, player_id)
        
        return jsonify({
            'report': report,
            'format': report_format,
            'fen_string': fen_string,
            'player_id': player_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating strategic report: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to generate strategic analysis report'
        }), 500


@strategic_bp.route('/strategic-analysis/cache/clear', methods=['POST'])
def clear_strategic_cache():
    """
    Clear the strategic analysis cache.
    
    POST /api/v1/strategic-analysis/cache/clear
    
    Returns:
        Cache clearing status
    """
    try:
        # Clear all cache entries
        strategic_cache.cache.clear()
        cleared_count = len(strategic_cache.cache)
        return jsonify({
            'message': 'Strategic analysis cache cleared successfully',
            'cleared_entries': cleared_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clearing strategic cache: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to clear strategic analysis cache'
        }), 500


@strategic_bp.route('/strategic-analysis/cache/stats', methods=['GET'])
def get_strategic_cache_stats():
    """
    Get strategic analysis cache statistics.
    
    GET /api/v1/strategic-analysis/cache/stats
    
    Returns:
        Cache statistics
    """
    try:
        stats = strategic_cache.get_cache_stats()
        return jsonify({
            'cache_stats': stats,
            'cache_size': len(strategic_cache.cache),
            'cache_hit_rate': 0,  # Not implemented in current cache
            'total_requests': 0,   # Not implemented in current cache
            'cache_hits': 0,       # Not implemented in current cache
            'cache_misses': 0      # Not implemented in current cache
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting strategic cache stats: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to get strategic analysis cache statistics'
        }), 500 