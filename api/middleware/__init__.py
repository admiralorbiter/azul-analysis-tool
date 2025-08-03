"""
Middleware package for the Azul Solver & Analysis Toolkit API.

This package contains middleware components for CORS, error handling, and other cross-cutting concerns.
"""

from .cors import add_cors_headers, handle_options
from .error_handling import handle_bad_request, handle_internal_error

__all__ = [
    'add_cors_headers',
    'handle_options', 
    'handle_bad_request',
    'handle_internal_error'
] 