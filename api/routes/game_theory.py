"""
Game Theory API Routes

Provides REST API endpoints for game theory analysis including Nash equilibrium detection,
opponent modeling, and strategic analysis.
"""

from flask import Blueprint, request, jsonify
from api.utils.state_converter import StateConverter
from analysis_engine.mathematical_optimization.game_theory import AzulGameTheory

game_theory_bp = Blueprint('game_theory', __name__)


@game_theory_bp.route('/game-theory/detect-nash-equilibrium', methods=['POST'])
def detect_nash_equilibrium():
    """Detect Nash equilibrium in the current game state."""
    try:
        data = request.get_json()
        if not data or 'game_state' not in data:
            return jsonify({
                "success": False,
                "error": "Missing game_state in request"
            }), 400
        
        # Convert frontend state to AzulState
        converter = StateConverter()
        azul_state = converter.json_to_game_state(data['game_state'])
        
        if azul_state is None:
            return jsonify({
                "success": False,
                "error": "Failed to convert game state"
            }), 400
        
        # Perform Nash equilibrium analysis
        game_theory = AzulGameTheory()
        result = game_theory.detect_nash_equilibrium(azul_state)
        
        return jsonify({
            "success": True,
            "equilibrium_type": result.equilibrium_type.value,
            "confidence": result.confidence,
            "strategic_insights": result.strategic_insights,
            "player_strategies": result.player_strategies
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Nash equilibrium detection failed: {str(e)}"
        }), 500


@game_theory_bp.route('/game-theory/model-opponent', methods=['POST'])
def model_opponent():
    """Model opponent behavior and strategy preferences."""
    try:
        data = request.get_json()
        if not data or 'game_state' not in data:
            return jsonify({
                "success": False,
                "error": "Missing game_state in request"
            }), 400
        
        opponent_id = data.get('opponent_id', 1)
        
        # Convert frontend state to AzulState
        converter = StateConverter()
        azul_state = converter.json_to_game_state(data['game_state'])
        
        if azul_state is None:
            return jsonify({
                "success": False,
                "error": "Failed to convert game state"
            }), 400
        
        # Perform opponent modeling
        game_theory = AzulGameTheory()
        result = game_theory.model_opponent(azul_state, opponent_id)
        
        return jsonify({
            "success": True,
            "opponent_model": {
                "player_id": result.player_id,
                "risk_tolerance": result.risk_tolerance,
                "aggression_level": result.aggression_level,
                "strategy_preferences": result.strategy_preferences,
                "confidence": result.confidence
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Opponent modeling failed: {str(e)}"
        }), 500


@game_theory_bp.route('/game-theory/analyze-strategy', methods=['POST'])
def analyze_strategy():
    """Analyze strategic position and provide recommendations."""
    try:
        data = request.get_json()
        if not data or 'game_state' not in data:
            return jsonify({
                "success": False,
                "error": "Missing game_state in request"
            }), 400
        
        player_id = data.get('player_id', 0)
        
        # Convert frontend state to AzulState
        converter = StateConverter()
        azul_state = converter.json_to_game_state(data['game_state'])
        
        if azul_state is None:
            return jsonify({
                "success": False,
                "error": "Failed to convert game state"
            }), 400
        
        # Perform strategic analysis
        game_theory = AzulGameTheory()
        result = game_theory.analyze_strategy(azul_state, player_id)
        
        return jsonify({
            "success": True,
            "strategic_analysis": {
                "strategic_value": result.strategic_value,
                "game_phase": result.game_phase.value,
                "confidence": result.confidence,
                "recommendations": result.recommendations,
                "risk_assessment": result.risk_assessment
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Strategic analysis failed: {str(e)}"
        }), 500


@game_theory_bp.route('/game-theory/predict-opponent-moves', methods=['POST'])
def predict_opponent_moves():
    """Predict opponent's likely move sequence."""
    try:
        data = request.get_json()
        if not data or 'game_state' not in data:
            return jsonify({
                "success": False,
                "error": "Missing game_state in request"
            }), 400
        
        opponent_id = data.get('opponent_id', 1)
        depth = data.get('depth', 3)
        
        # Convert frontend state to AzulState
        converter = StateConverter()
        azul_state = converter.json_to_game_state(data['game_state'])
        
        if azul_state is None:
            return jsonify({
                "success": False,
                "error": "Failed to convert game state"
            }), 400
        
        # Predict opponent moves
        game_theory = AzulGameTheory()
        result = game_theory.predict_opponent_moves(azul_state, opponent_id, depth)
        
        return jsonify({
            "success": True,
            "predicted_moves": result.predicted_moves,
            "confidence": result.confidence,
            "prediction_depth": depth
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Move prediction failed: {str(e)}"
        }), 500


@game_theory_bp.route('/game-theory/calculate-strategic-value', methods=['POST'])
def calculate_strategic_value():
    """Calculate strategic value of the current position."""
    try:
        data = request.get_json()
        if not data or 'game_state' not in data:
            return jsonify({
                "success": False,
                "error": "Missing game_state in request"
            }), 400
        
        player_id = data.get('player_id', 0)
        
        # Convert frontend state to AzulState
        converter = StateConverter()
        azul_state = converter.json_to_game_state(data['game_state'])
        
        if azul_state is None:
            return jsonify({
                "success": False,
                "error": "Failed to convert game state"
            }), 400
        
        # Calculate strategic value
        game_theory = AzulGameTheory()
        result = game_theory.calculate_strategic_value(azul_state, player_id)
        
        return jsonify({
            "success": True,
            "strategic_value": result.strategic_value,
            "confidence": result.confidence,
            "breakdown": result.breakdown
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Strategic value calculation failed: {str(e)}"
        }), 500 