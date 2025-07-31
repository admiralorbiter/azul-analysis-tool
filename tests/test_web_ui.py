"""
Tests for the Web UI functionality.

This module tests the web UI routes and static file serving.
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from api.app import create_test_app


class TestWebUIRoutes:
    """Test web UI routes and static file serving."""
    
    def test_index_route(self):
        """Test that the index route serves the web UI."""
        app = create_test_app()
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            assert 'text/html' in response.content_type
            assert 'Azul Solver & Analysis Toolkit' in response.get_data(as_text=True)
    
    def test_ui_static_files(self):
        """Test that static files are served correctly."""
        app = create_test_app()
        
        # Create a temporary file in the ui directory
        with tempfile.NamedTemporaryFile(dir='ui', suffix='.test', delete=False) as tmp:
            tmp.write(b'test content')
            tmp.flush()
            filename = os.path.basename(tmp.name)
        
        try:
            with app.test_client() as client:
                response = client.get(f'/ui/{filename}')
                
                assert response.status_code == 200
                assert response.get_data() == b'test content'
        finally:
            # Clean up - handle Windows file locking
            try:
                os.unlink(tmp.name)
            except PermissionError:
                # On Windows, file might still be in use
                pass
    
    def test_ui_static_file_not_found(self):
        """Test that 404 is returned for non-existent static files."""
        app = create_test_app()
        
        with app.test_client() as client:
            response = client.get('/ui/nonexistent.txt')
            
            assert response.status_code == 404
    
    def test_healthz_endpoint(self):
        """Test the health check endpoint."""
        app = create_test_app()
        
        with app.test_client() as client:
            response = client.get('/healthz')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
            assert 'version' in data
            assert 'database' in data


class TestWebUIIntegration:
    """Test web UI integration with API endpoints."""
    
    def test_web_ui_with_api(self):
        """Test that web UI can communicate with API endpoints."""
        app = create_test_app()
        
        with app.test_client() as client:
            # Test that the web UI loads
            response = client.get('/')
            assert response.status_code == 200
            
            # Test that API endpoints are accessible
            response = client.get('/api/v1/health')
            assert response.status_code == 200
    
    def test_cors_enabled(self):
        """Test that CORS is enabled for web UI."""
        app = create_test_app()
        
        with app.test_client() as client:
            response = client.get('/')
            
            # Check that CORS headers are present
            assert 'Access-Control-Allow-Origin' in response.headers 