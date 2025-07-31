"""
Authentication and session management for the Azul API.

This module provides session-based authentication with rate limiting
and user management for the REST API endpoints.
"""

import secrets
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from flask import Blueprint, request, session, jsonify, current_app
from functools import wraps


@dataclass
class SessionData:
    """Session data structure."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    user_agent: str
    ip_address: str
    request_count: int = 0


class SessionManager:
    """
    Manages user sessions for the API.
    
    Provides session creation, validation, and cleanup functionality
    with automatic session expiration.
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        """Initialize the session manager."""
        self.session_timeout_minutes = session_timeout_minutes
        self._sessions: Dict[str, SessionData] = {}
        self._cleanup_interval = 300  # Clean up every 5 minutes
        self._last_cleanup = time.time()
    
    def create_session(self, user_agent: str, ip_address: str) -> str:
        """
        Create a new session for a user.
        
        Args:
            user_agent: User agent string
            ip_address: Client IP address
            
        Returns:
            Session ID string
        """
        session_id = secrets.token_urlsafe(32)
        now = datetime.now()
        
        self._sessions[session_id] = SessionData(
            session_id=session_id,
            created_at=now,
            last_activity=now,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[SessionData]:
        """
        Validate a session ID and return session data if valid.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            SessionData if valid, None if invalid or expired
        """
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        if session_id not in self._sessions:
            return None
        
        session_data = self._sessions[session_id]
        
        # Check if session has expired
        if (datetime.now() - session_data.last_activity).total_seconds() > (self.session_timeout_minutes * 60):
            del self._sessions[session_id]
            return None
        
        # Update last activity
        session_data.last_activity = datetime.now()
        session_data.request_count += 1
        
        return session_data
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        
        # Only cleanup every 5 minutes to avoid performance impact
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self._sessions.items():
            if (now - session_data.last_activity).total_seconds() > (self.session_timeout_minutes * 60):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about active sessions.
        
        Returns:
            Dictionary with session statistics
        """
        self._cleanup_expired_sessions()
        
        return {
            "active_sessions": len(self._sessions),
            "session_timeout_minutes": self.session_timeout_minutes,
            "total_sessions_created": sum(1 for s in self._sessions.values()),
            "average_requests_per_session": sum(s.request_count for s in self._sessions.values()) / max(1, len(self._sessions))
        }


# Global session manager instance
session_manager = SessionManager()


def require_session(f):
    """
    Decorator to require a valid session for API endpoints.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({
                'error': 'Session ID required',
                'message': 'Include X-Session-ID header in request'
            }), 401
        
        session_data = session_manager.validate_session(session_id)
        
        if not session_data:
            return jsonify({
                'error': 'Invalid or expired session',
                'message': 'Session has expired or is invalid'
            }), 401
        
        # Add session data to request context
        request.session_data = session_data
        
        return f(*args, **kwargs)
    
    return decorated_function


def create_session_endpoint():
    """Create a new session endpoint."""
    user_agent = request.headers.get('User-Agent', 'Unknown')
    ip_address = request.remote_addr
    
    session_id = session_manager.create_session(user_agent, ip_address)
    
    return jsonify({
        'session_id': session_id,
        'expires_in_minutes': session_manager.session_timeout_minutes,
        'message': 'Session created successfully'
    })


def session_stats_endpoint():
    """Get session statistics endpoint."""
    return jsonify({
        'session_stats': session_manager.get_session_stats(),
        'rate_limit_stats': current_app.rate_limiter.get_session_stats(
            request.headers.get('X-Session-ID', 'unknown')
        ) if hasattr(current_app, 'rate_limiter') else {}
    })


# Create Flask blueprint for authentication endpoints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/session', methods=['POST'])
def create_session():
    """Create a new session."""
    return create_session_endpoint()

@auth_bp.route('/stats', methods=['GET'])
@require_session
def get_stats():
    """Get session and rate limit statistics."""
    return session_stats_endpoint() 