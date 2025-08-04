"""
REST API routes for the Azul Solver & Analysis Toolkit.

This module provides Flask blueprints for game analysis, hints, and research tools.
"""

from flask import Blueprint

from core.azul_database import AzulDatabase

# All models and utilities are now imported in their respective route modules

# Import route blueprints from the new modular structure
from .routes import positions_bp, game_bp, analysis_bp
from .routes.neural import neural_bp, init_neural_routes
from .routes.validation import validation_bp
from .routes.performance import performance_bp
from .routes.core import core_bp
from .routes.move_analysis import move_analysis_bp

# Initialize database connection
db = AzulDatabase()

# Initialize neural routes with database
init_neural_routes(db)


# Create Flask blueprint for API endpoints
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Register all route blueprints
api_bp.register_blueprint(positions_bp)
api_bp.register_blueprint(game_bp)
api_bp.register_blueprint(analysis_bp)
api_bp.register_blueprint(neural_bp)
api_bp.register_blueprint(validation_bp)
api_bp.register_blueprint(performance_bp)
api_bp.register_blueprint(core_bp)
api_bp.register_blueprint(move_analysis_bp)


# Global state variables moved to api/utils/state_parser.py






# All endpoints have been modularized into separate route files




# Core endpoints moved to api/routes/core.py


# ============================================================================
# Performance Monitoring Endpoints
# ============================================================================
# Moved to api/routes/performance.py


# Game endpoints moved to api/routes/game.py





# Helper functions moved to api/routes/game.py





# state_to_fen function moved to api/utils/state_parser.py 


# All endpoints and functions have been modularized



# All remaining code has been modularized





# Import middleware functions
from .middleware import add_cors_headers, handle_bad_request, handle_internal_error, handle_options

# Register middleware
api_bp.after_request(add_cors_headers)
api_bp.errorhandler(400)(handle_bad_request)
api_bp.errorhandler(500)(handle_internal_error)

# Handle OPTIONS requests for CORS preflight
@api_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options_route(path):
    return handle_options(path)


