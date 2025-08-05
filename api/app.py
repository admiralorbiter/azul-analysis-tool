"""
Flask application factory for the Azul REST API.

This module creates and configures the Flask application with all
API endpoints, authentication, rate limiting, and database integration.
"""

import os
import tempfile
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from .main_routes import api_bp
from .routes.positions import positions_bp
from .routes.analysis import analysis_bp
from .routes.game import game_bp
from .routes.neural import neural_bp
from .routes.strategic import strategic_bp
from .routes.optimization import optimization_bp
from .routes.dynamic_optimization import dynamic_optimization_bp
from .routes.game_theory import game_theory_bp
from .auth import auth_bp, session_manager
from .rate_limiter import RateLimiter
from core.azul_database import AzulDatabase


def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    else:
        app.config.update({
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'DATABASE_PATH': os.environ.get('DATABASE_PATH', None),
            'RATE_LIMIT_ENABLED': os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            'DEBUG': os.environ.get('DEBUG', 'false').lower() == 'true'
        })
    
    # Enable CORS for web UI integration
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Initialize rate limiter
    if app.config.get('RATE_LIMIT_ENABLED', True):
        app.rate_limiter = RateLimiter()
    else:
        app.rate_limiter = None
    
    # Initialize session manager
    app.session_manager = session_manager
    
    # Initialize database if path is provided
    if app.config.get('DATABASE_PATH'):
        try:
            app.database = AzulDatabase(app.config['DATABASE_PATH'])
        except Exception as e:
            app.logger.warning(f"Failed to initialize database: {e}")
            app.database = None
    else:
        app.database = None
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(positions_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(neural_bp, url_prefix='/api/v1')
    app.register_blueprint(strategic_bp, url_prefix='/api/v1')
    app.register_blueprint(optimization_bp, url_prefix='/api/v1')
    app.register_blueprint(dynamic_optimization_bp, url_prefix='/api/v1')
    app.register_blueprint(game_theory_bp, url_prefix='/api/v1')
    
    # Serve static files from ui directory
    @app.route('/ui/<path:filename>')
    def ui_static(filename):
        ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui')
        response = send_from_directory(ui_dir, filename)
        
        # Set correct MIME types for JavaScript files
        if filename.endswith('.js') or filename.endswith('.jsx'):
            response.headers['Content-Type'] = 'application/javascript'
        elif filename.endswith('.css'):
            response.headers['Content-Type'] = 'text/css'
        
        return response
    
    # Serve UI files at root level for easier access
    @app.route('/<path:filename>')
    def static_files(filename):
        ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui')
        
        # Only serve files that exist in the ui directory
        if os.path.exists(os.path.join(ui_dir, filename)):
            response = send_from_directory(ui_dir, filename)
            
            # Set correct MIME types
            if filename.endswith('.js') or filename.endswith('.jsx'):
                response.headers['Content-Type'] = 'application/javascript'
            elif filename.endswith('.css'):
                response.headers['Content-Type'] = 'text/css'
            elif filename.endswith('.png'):
                response.headers['Content-Type'] = 'image/png'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                response.headers['Content-Type'] = 'image/jpeg'
            
            return response
        else:
            # Only fall back to index.html for known UI routes (not API routes)
            if not filename.startswith('api/'):
                return send_from_directory(ui_dir, 'index.html')
            else:
                # Let Flask handle 404 for API routes
                from werkzeug.exceptions import NotFound
                raise NotFound()
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': 'Azul Solver & Analysis Toolkit API',
            'version': '0.1.0',
            'endpoints': {
                'auth': '/api/v1/auth',
                'analysis': '/api/v1/analyze',
                'hint': '/api/v1/hint',
                'health': '/api/v1/health',
                'stats': '/api/v1/stats',
                'positions': {
                    'get': '/api/v1/positions/{fen_string}',
                    'put': '/api/v1/positions/{fen_string}',
                    'delete': '/api/v1/positions/{fen_string}',
                    'stats': '/api/v1/positions/stats',
                    'search': '/api/v1/positions/search',
                    'bulk': {
                        'import': '/api/v1/positions/bulk (POST)',
                        'export': '/api/v1/positions/bulk (GET)',
                        'delete': '/api/v1/positions/bulk (DELETE)'
                    }
                },
                'analyses': {
                    'get': '/api/v1/analyses/{fen_string}',
                    'post': '/api/v1/analyses/{fen_string}',
                    'delete': '/api/v1/analyses/{fen_string}',
                    'stats': '/api/v1/analyses/stats',
                    'search': '/api/v1/analyses/search',
                    'recent': '/api/v1/analyses/recent'
                },
                'performance': {
                    'stats': '/api/v1/performance/stats',
                    'health': '/api/v1/performance/health',
                    'optimize': '/api/v1/performance/optimize (POST)',
                    'analytics': '/api/v1/performance/analytics',
                    'monitoring': '/api/v1/performance/monitoring'
                }
            },
            'documentation': 'See project README for API documentation'
        })
    
    # Web UI route
    @app.route('/')
    def index():
        ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui')
        return send_from_directory(ui_dir, 'index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    # Health check endpoint
    @app.route('/healthz')
    def healthz():
        """Health check endpoint for load balancers."""
        return jsonify({
            'status': 'healthy',
            'version': '0.1.0',
            'database': 'connected' if app.database else 'disabled'
        })
    
    return app


def create_test_app():
    """Create a test application with temporary database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    config = {
        'TESTING': True,
        'DATABASE_PATH': db_path,
        'RATE_LIMIT_ENABLED': True
    }
    
    app = create_app(config)
    
    # Cleanup function for tests
    def cleanup():
        try:
            os.unlink(db_path)
        except:
            pass
    
    app.cleanup = cleanup
    
    return app 