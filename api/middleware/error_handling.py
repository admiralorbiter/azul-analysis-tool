"""
Error Handling Middleware

This module handles global error responses for the API.
"""

from flask import request, jsonify


def handle_bad_request(error):
    """Handle 400 Bad Request errors."""
    if request.is_json:
        return jsonify({'error': 'Invalid JSON format'}), 400
    return jsonify({'error': 'Bad request'}), 400


def handle_internal_error(error):
    """Handle 500 Internal Server errors."""
    if hasattr(error, 'description') and 'JSON' in error.description:
        return jsonify({'error': 'Invalid JSON format'}), 400
    return jsonify({'error': 'Internal server error'}), 500 