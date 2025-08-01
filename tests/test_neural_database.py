"""
Tests for neural training database integration.

This module tests:
- Neural training session storage and retrieval
- Neural model storage and retrieval
- Neural configuration template storage and retrieval
- Neural evaluation session storage and retrieval
- Database schema creation and validation
"""

import pytest
import tempfile
import os
import json
from datetime import datetime

from core.azul_database import (
    AzulDatabase, NeuralTrainingSession, NeuralModel, 
    NeuralConfiguration, NeuralEvaluationSession
)


class TestNeuralDatabaseIntegration:
    """Test neural training database integration."""
    
    def test_database_creation_with_neural_tables(self):
        """Test that neural training tables are created correctly."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Check that neural tables were created
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'neural_%'
                """)
                tables = [row['name'] for row in cursor.fetchall()]
                
                expected_tables = [
                    'neural_training_sessions',
                    'neural_training_progress', 
                    'neural_models',
                    'neural_configurations',
                    'neural_evaluation_sessions'
                ]
                
                for table in expected_tables:
                    assert table in tables, f"Table {table} was not created"
                
                # Check that indexes were created
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name LIKE 'idx_neural_%'
                """)
                indexes = [row['name'] for row in cursor.fetchall()]
                
                assert len(indexes) > 0, "No neural indexes were created"
                
        finally:
            os.unlink(db_path)
    
    def test_neural_training_session_storage(self):
        """Test saving and retrieving neural training sessions."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Create a test session
            session = NeuralTrainingSession(
                session_id="test-session-1",
                status="running",
                progress=50,
                start_time=datetime.now(),
                config={"epochs": 10, "batch_size": 16},
                logs=["Starting training...", "Epoch 1 complete"],
                loss_history=[0.5, 0.4, 0.3],
                epoch_history=[1, 2, 3],
                cpu_usage=[0.8, 0.7, 0.6],
                memory_usage=[0.6, 0.5, 0.4],
                current_epoch=3,
                total_epochs=10
            )
            
            # Save session
            assert db.save_neural_training_session(session)
            
            # Retrieve session
            retrieved = db.get_neural_training_session("test-session-1")
            assert retrieved is not None
            assert retrieved.session_id == "test-session-1"
            assert retrieved.status == "running"
            assert retrieved.progress == 50
            assert retrieved.config == {"epochs": 10, "batch_size": 16}
            assert retrieved.logs == ["Starting training...", "Epoch 1 complete"]
            assert retrieved.loss_history == [0.5, 0.4, 0.3]
            assert retrieved.epoch_history == [1, 2, 3]
            assert retrieved.cpu_usage == [0.8, 0.7, 0.6]
            assert retrieved.memory_usage == [0.6, 0.5, 0.4]
            assert retrieved.current_epoch == 3
            assert retrieved.total_epochs == 10
            
        finally:
            os.unlink(db_path)
    
    def test_neural_model_storage(self):
        """Test saving and retrieving neural models."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # First create a training session that the model can reference
            session = NeuralTrainingSession(
                session_id="test-session-1",
                status="completed",
                progress=100
            )
            assert db.save_neural_training_session(session)
            
            # Create a test model
            model = NeuralModel(
                model_id="test-model-1",
                model_path="models/test_model.pth",
                config={"architecture": "small", "device": "cpu"},
                training_session_id="test-session-1",  # Now this session exists
                performance_metrics={"accuracy": 0.85, "loss": 0.15},
                model_size_bytes=1024 * 1024,  # 1MB
                architecture="small",
                device_used="cpu"
            )
            
            # Save model
            assert db.save_neural_model(model)
            
            # Retrieve models
            models = db.get_neural_models()
            assert len(models) == 1
            
            retrieved = models[0]
            assert retrieved.model_id == "test-model-1"
            assert retrieved.model_path == "models/test_model.pth"
            assert retrieved.config == {"architecture": "small", "device": "cpu"}
            assert retrieved.training_session_id == "test-session-1"
            assert retrieved.performance_metrics == {"accuracy": 0.85, "loss": 0.15}
            assert retrieved.model_size_bytes == 1024 * 1024
            assert retrieved.architecture == "small"
            assert retrieved.device_used == "cpu"
            
        finally:
            os.unlink(db_path)
    
    def test_neural_configuration_storage(self):
        """Test saving and retrieving neural configurations."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Create a test configuration
            config = NeuralConfiguration(
                config_id="test-config-1",
                name="Small Model Config",
                config={"epochs": 5, "batch_size": 16, "learning_rate": 0.001},
                description="Configuration for small model training",
                tags=["small", "quick", "baseline"],
                is_default=True
            )
            
            # Save configuration
            assert db.save_neural_configuration(config)
            
            # Retrieve configurations
            configs = db.get_neural_configurations()
            assert len(configs) == 1
            
            retrieved = configs[0]
            assert retrieved.config_id == "test-config-1"
            assert retrieved.name == "Small Model Config"
            assert retrieved.config == {"epochs": 5, "batch_size": 16, "learning_rate": 0.001}
            assert retrieved.description == "Configuration for small model training"
            assert retrieved.tags == ["small", "quick", "baseline"]
            assert retrieved.is_default == True
            
        finally:
            os.unlink(db_path)
    
    def test_neural_evaluation_session_storage(self):
        """Test saving and retrieving neural evaluation sessions."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Create a test evaluation session
            session = NeuralEvaluationSession(
                session_id="test-eval-1",
                status="completed",
                progress=100,
                start_time=datetime.now(),
                end_time=datetime.now(),
                config={"model": "test-model-1", "positions": 100},
                results={"accuracy": 0.85, "win_rate": 0.72}
            )
            
            # Save session
            assert db.save_neural_evaluation_session(session)
            
            # Retrieve sessions
            sessions = db.get_neural_evaluation_sessions()
            assert len(sessions) == 1
            
            retrieved = sessions[0]
            assert retrieved.session_id == "test-eval-1"
            assert retrieved.status == "completed"
            assert retrieved.progress == 100
            assert retrieved.config == {"model": "test-model-1", "positions": 100}
            assert retrieved.results == {"accuracy": 0.85, "win_rate": 0.72}
            
        finally:
            os.unlink(db_path)
    
    def test_session_filtering_and_limiting(self):
        """Test filtering and limiting of sessions."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Create multiple sessions
            sessions = [
                NeuralTrainingSession(session_id="session-1", status="completed", progress=100),
                NeuralTrainingSession(session_id="session-2", status="running", progress=50),
                NeuralTrainingSession(session_id="session-3", status="completed", progress=100),
                NeuralTrainingSession(session_id="session-4", status="failed", progress=25)
            ]
            
            # Save all sessions
            for session in sessions:
                assert db.save_neural_training_session(session)
            
            # Test filtering by status
            completed = db.get_all_neural_training_sessions(status="completed")
            assert len(completed) == 2
            
            running = db.get_all_neural_training_sessions(status="running")
            assert len(running) == 1
            
            failed = db.get_all_neural_training_sessions(status="failed")
            assert len(failed) == 1
            
            # Test limiting
            limited = db.get_all_neural_training_sessions(limit=2)
            assert len(limited) == 2
            
        finally:
            os.unlink(db_path)
    
    def test_session_deletion(self):
        """Test deleting neural training sessions."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Create and save a session
            session = NeuralTrainingSession(
                session_id="test-delete-session",
                status="completed",
                progress=100
            )
            assert db.save_neural_training_session(session)
            
            # Verify it exists
            retrieved = db.get_neural_training_session("test-delete-session")
            assert retrieved is not None
            
            # Delete it
            assert db.delete_neural_training_session("test-delete-session")
            
            # Verify it's gone
            retrieved = db.get_neural_training_session("test-delete-session")
            assert retrieved is None
            
        finally:
            os.unlink(db_path)
    
    def test_model_filtering_by_architecture(self):
        """Test filtering neural models by architecture."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # First create training sessions for the models to reference
            sessions = [
                NeuralTrainingSession(session_id="session-1", status="completed", progress=100),
                NeuralTrainingSession(session_id="session-2", status="completed", progress=100),
                NeuralTrainingSession(session_id="session-3", status="completed", progress=100),
                NeuralTrainingSession(session_id="session-4", status="completed", progress=100)
            ]
            
            for session in sessions:
                assert db.save_neural_training_session(session)
            
            # Create models with different architectures
            models = [
                NeuralModel(model_id="model-1", model_path="path1", architecture="small", training_session_id="session-1"),
                NeuralModel(model_id="model-2", model_path="path2", architecture="medium", training_session_id="session-2"),
                NeuralModel(model_id="model-3", model_path="path3", architecture="large", training_session_id="session-3"),
                NeuralModel(model_id="model-4", model_path="path4", architecture="small", training_session_id="session-4")
            ]
            
            # Save all models
            for model in models:
                assert db.save_neural_model(model)
            
            # Test filtering
            small_models = db.get_neural_models(architecture="small")
            assert len(small_models) == 2
            
            medium_models = db.get_neural_models(architecture="medium")
            assert len(medium_models) == 1
            
            large_models = db.get_neural_models(architecture="large")
            assert len(large_models) == 1
            
        finally:
            os.unlink(db_path)
    
    def test_configuration_filtering_by_default(self):
        """Test filtering neural configurations by default status."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Create configurations
            configs = [
                NeuralConfiguration(config_id="config-1", name="Default", config={}, is_default=True),
                NeuralConfiguration(config_id="config-2", name="Custom", config={}, is_default=False),
                NeuralConfiguration(config_id="config-3", name="Another Default", config={}, is_default=True)
            ]
            
            # Save all configurations
            for config in configs:
                assert db.save_neural_configuration(config)
            
            # Test filtering
            default_configs = db.get_neural_configurations(is_default=True)
            assert len(default_configs) == 2
            
            non_default_configs = db.get_neural_configurations(is_default=False)
            assert len(non_default_configs) == 1
            
        finally:
            os.unlink(db_path) 