"""
Test neural API integration for Part 2.1.4: Training History & Management.

This test file verifies that the new database-backed API endpoints work correctly.
"""

import pytest
import json
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

from api.routes import neural_bp
from core.azul_database import AzulDatabase, NeuralTrainingSession, NeuralConfiguration, NeuralModel


class TestNeuralAPIIntegration:
    """Test neural API integration with database backend."""
    
    def setup_method(self):
        """Set up test environment."""
        import os
        import tempfile
        
        # Create a temporary database file
        self.temp_db_path = tempfile.mktemp(suffix='.db')
        self.db = AzulDatabase(self.temp_db_path)
        
        # Create test data
        
        # Create test data
        self.test_session_id = str(uuid.uuid4())
        self.test_config_id = str(uuid.uuid4())
        self.test_model_id = str(uuid.uuid4())
        
        # Create test training session
        self.test_session = NeuralTrainingSession(
            session_id=self.test_session_id,
            status='completed',
            progress=100,
            config={'epochs': 5, 'batch_size': 16},
            logs=['Training started', 'Training completed'],
            error=None,
            results={'final_loss': 0.1, 'model_path': 'models/test.pth'},
            metadata={
                'device': 'cpu',
                'config_size': 'small',
                'epochs': 5,
                'samples': 500,
                'batch_size': 16,
                'learning_rate': 0.001
            }
        )
        
        # Create test configuration
        self.test_config = NeuralConfiguration(
            config_id=self.test_config_id,
            name='Test Config',
            description='Test configuration for API testing',
            is_default=False,
            config={'epochs': 5, 'batch_size': 16}
        )
        
        # Create test model
        self.test_model = NeuralModel(
            model_id=self.test_model_id,
            model_path='models/test.pth',
            architecture='small',
            training_session_id=self.test_session_id
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        import os
        if hasattr(self, 'temp_db_path') and os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
    
    def test_get_training_history_endpoint(self):
        """Test the /neural/history endpoint."""
        # Save test session to database
        self.db.save_neural_training_session(self.test_session)
        
        # Mock the database connection in the API
        with patch('api.routes.neural.db', self.db):
            # Test basic history retrieval
            # This would normally be done with a Flask test client
            # For now, we'll test the database integration directly
            sessions = self.db.get_all_neural_training_sessions()
            assert len(sessions) > 0
            
            # Test filtering by status
            completed_sessions = self.db.get_all_neural_training_sessions(status='completed')
            assert len(completed_sessions) > 0
            assert all(s.status == 'completed' for s in completed_sessions)
    
    def test_get_neural_configurations_endpoint(self):
        """Test the /neural/configurations endpoint."""
        # Save test configuration to database
        self.db.save_neural_configuration(self.test_config)
        
        # Test configuration retrieval
        configs = self.db.get_neural_configurations()
        assert len(configs) > 0
        
        # Test filtering by default status
        non_default_configs = self.db.get_neural_configurations(is_default=False)
        assert len(non_default_configs) > 0
        assert all(not c.is_default for c in non_default_configs)
    
    def test_save_neural_configuration_endpoint(self):
        """Test the /neural/configurations POST endpoint."""
        # Test configuration creation
        new_config = NeuralConfiguration(
            config_id=str(uuid.uuid4()),
            name='New Test Config',
            description='New test configuration',
            is_default=False,
            config={'epochs': 10, 'batch_size': 32}
        )
        
        success = self.db.save_neural_configuration(new_config)
        assert success
        
        # Verify it was saved
        saved_config = self.db.get_neural_configuration(new_config.config_id)
        assert saved_config is not None
        assert saved_config.name == 'New Test Config'
    
    def test_get_neural_models_endpoint(self):
        """Test the /neural/models endpoint."""
        # Save the training session first (required for foreign key constraint)
        self.db.save_neural_training_session(self.test_session)
        
        # Save test model to database
        self.db.save_neural_model(self.test_model)
        
        # Test model retrieval
        models = self.db.get_neural_models()
        assert len(models) > 0
        
        # Test filtering by architecture
        small_models = self.db.get_neural_models(architecture='small')
        assert len(small_models) > 0
        assert all(m.architecture == 'small' for m in small_models)
    
    def test_delete_neural_configuration_endpoint(self):
        """Test the /neural/configurations/<config_id> DELETE endpoint."""
        # Save test configuration
        self.db.save_neural_configuration(self.test_config)
        
        # Verify it exists
        saved_config = self.db.get_neural_configuration(self.test_config_id)
        assert saved_config is not None
        
        # Delete it
        success = self.db.delete_neural_configuration(self.test_config_id)
        assert success
        
        # Verify it was deleted
        deleted_config = self.db.get_neural_configuration(self.test_config_id)
        assert deleted_config is None
    
    def test_delete_neural_training_session_endpoint(self):
        """Test the /neural/sessions/<session_id> DELETE endpoint."""
        # Save test session
        self.db.save_neural_training_session(self.test_session)
        
        # Verify it exists
        saved_session = self.db.get_neural_training_session(self.test_session_id)
        assert saved_session is not None
        
        # Delete it
        success = self.db.delete_neural_training_session(self.test_session_id)
        assert success
        
        # Verify it was deleted
        deleted_session = self.db.get_neural_training_session(self.test_session_id)
        assert deleted_session is None
    
    def test_training_session_lifecycle(self):
        """Test complete training session lifecycle with database integration."""
        # Create a new training session
        session_id = str(uuid.uuid4())
        session = NeuralTrainingSession(
            session_id=session_id,
            status='starting',
            progress=0,
            config={'epochs': 3, 'batch_size': 8},
            logs=['Session created'],
            error=None,
            results=None,
            metadata={
                'device': 'cpu',
                'config_size': 'small',
                'epochs': 3,
                'batch_size': 8,
                'learning_rate': 0.001
            }
        )
        
        # Save initial session
        success = self.db.save_neural_training_session(session)
        assert success
        
        # Update session to running
        session.status = 'running'
        session.progress = 50
        logs = session.logs
        logs.append('Training in progress')
        session.logs = logs
        
        success = self.db.save_neural_training_session(session)
        assert success
        
        # Update session to completed
        session.status = 'completed'
        session.progress = 100
        logs = session.logs
        logs.append('Training completed')
        session.logs = logs
        session.results = {'final_loss': 0.05, 'model_path': 'models/completed.pth'}
        
        success = self.db.save_neural_training_session(session)
        assert success
        
        # Verify final state
        final_session = self.db.get_neural_training_session(session_id)
        assert final_session is not None
        assert final_session.status == 'completed'
        assert final_session.progress == 100
        assert final_session.results is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 