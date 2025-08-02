"""
Test suite for Enhanced Neural Training Features (Part 2.1.2)

Tests the enhanced neural training interface with:
- Live loss visualization
- Resource monitoring (CPU/GPU usage)
- Training time estimation
- Multiple concurrent training sessions
"""

import unittest
import json
import time
import threading
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.routes import (
    get_system_resources, 
    get_process_resources
)
from core.azul_database import NeuralTrainingSession, AzulDatabase


class TestEnhancedNeuralTraining(unittest.TestCase):
    """Test cases for enhanced neural training features."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test database
        self.test_db_path = "test_azul_research.db"
        self.db = AzulDatabase(self.test_db_path)
        
        # Sample training configuration
        self.sample_config = {
            'config': 'small',
            'device': 'cpu',
            'epochs': 5,
            'samples': 500,
            'batch_size': 16,
            'learning_rate': 0.001
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_neural_training_session_creation(self):
        """Test enhanced training session creation."""
        session_id = "test-session-123"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='starting',
            progress=0,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=['Training session created'],
            loss_history=[],
            epoch_history=[],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            current_epoch=0,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        self.assertEqual(session.session_id, session_id)
        self.assertEqual(session.status, 'starting')
        self.assertEqual(session.progress, 0)
        self.assertEqual(session.config, self.sample_config)
        self.assertEqual(session.total_epochs, 5)
        self.assertEqual(session.current_epoch, 0)
        self.assertIsNotNone(session.created_at)
    
    def test_neural_training_session_save_and_retrieve(self):
        """Test saving and retrieving training sessions from database."""
        session_id = "test-session-456"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=25,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=['Training started', 'Epoch 1 completed'],
            loss_history=[0.5, 0.3],
            epoch_history=[1, 2],
            timestamp_history=['2024-01-01 10:00:00', '2024-01-01 10:05:00'],
            cpu_usage=[25.5, 30.1],
            memory_usage=[45.2, 48.7],
            gpu_usage=[60.0, 65.2],
            current_epoch=2,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        # Save to database
        success = self.db.save_neural_training_session(session)
        self.assertTrue(success)
        
        # Retrieve from database
        retrieved_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session_id)
        self.assertEqual(retrieved_session.status, 'running')
        self.assertEqual(retrieved_session.progress, 25)
        self.assertEqual(retrieved_session.current_epoch, 2)
        self.assertEqual(retrieved_session.loss_history, [0.5, 0.3])
        self.assertEqual(retrieved_session.cpu_usage, [25.5, 30.1])
    
    def test_neural_training_session_progress_tracking(self):
        """Test training progress updates with loss tracking."""
        session_id = "test-session-progress"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=0,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=[],
            loss_history=[],
            epoch_history=[],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            current_epoch=0,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        # Save initial session
        self.db.save_neural_training_session(session)
        
        # Simulate training progress updates
        for epoch in range(1, 4):
            # Retrieve current session
            current_session = self.db.get_neural_training_session(session_id)
            if current_session:
                # Update progress
                current_session.current_epoch = epoch
                current_session.progress = epoch * 20
                current_session.loss_history.append(0.5 / epoch)
                current_session.epoch_history.append(epoch)
                current_session.timestamp_history.append(datetime.now().isoformat())
                
                # Save updated session
                self.db.save_neural_training_session(current_session)
        
        # Verify final state
        final_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(final_session)
        self.assertEqual(final_session.current_epoch, 3)
        self.assertEqual(final_session.progress, 60)
        self.assertEqual(len(final_session.loss_history), 3)
        self.assertEqual(final_session.epoch_history, [1, 2, 3])
    
    def test_resource_monitoring(self):
        """Test resource usage monitoring."""
        session_id = "test-session-resources"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=0,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=[],
            loss_history=[],
            epoch_history=[],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            current_epoch=0,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        # Save initial session
        self.db.save_neural_training_session(session)
        
        # Simulate resource updates
        resource_updates = [
            {'cpu': 25.5, 'memory': 45.2, 'gpu': 60.0},
            {'cpu': 30.1, 'memory': 48.7, 'gpu': 65.2},
            {'cpu': 28.3, 'memory': 47.1, 'gpu': 62.8}
        ]
        
        for update in resource_updates:
            current_session = self.db.get_neural_training_session(session_id)
            if current_session:
                current_session.cpu_usage.append(update['cpu'])
                current_session.memory_usage.append(update['memory'])
                current_session.gpu_usage.append(update['gpu'])
                self.db.save_neural_training_session(current_session)
        
        # Verify resource tracking
        final_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(final_session)
        self.assertEqual(len(final_session.cpu_usage), 3)
        self.assertEqual(len(final_session.memory_usage), 3)
        self.assertEqual(len(final_session.gpu_usage), 3)
        self.assertEqual(final_session.cpu_usage, [25.5, 30.1, 28.3])
        self.assertEqual(final_session.memory_usage, [45.2, 48.7, 47.1])
        self.assertEqual(final_session.gpu_usage, [60.0, 65.2, 62.8])
    
    def test_session_completion(self):
        """Test training session completion."""
        session_id = "test-session-complete"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=80,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=['Training in progress'],
            loss_history=[0.5, 0.3, 0.2, 0.1],
            epoch_history=[1, 2, 3, 4],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            current_epoch=4,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        # Save session
        self.db.save_neural_training_session(session)
        
        # Complete the session
        current_session = self.db.get_neural_training_session(session_id)
        if current_session:
            current_session.status = 'completed'
            current_session.progress = 100
            current_session.end_time = datetime.now()
            current_session.results = {
                'final_loss': 0.1,
                'total_epochs': 5,
                'training_time': 300.5
            }
            self.db.save_neural_training_session(current_session)
        
        # Verify completion
        final_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(final_session)
        self.assertEqual(final_session.status, 'completed')
        self.assertEqual(final_session.progress, 100)
        self.assertIsNotNone(final_session.end_time)
        self.assertIsNotNone(final_session.results)
        self.assertEqual(final_session.results['final_loss'], 0.1)
    
    def test_session_error_handling(self):
        """Test training session error handling."""
        session_id = "test-session-error"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=30,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=['Training started'],
            loss_history=[0.5, 0.3],
            epoch_history=[1, 2],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            current_epoch=2,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        # Save session
        self.db.save_neural_training_session(session)
        
        # Simulate error
        current_session = self.db.get_neural_training_session(session_id)
        if current_session:
            current_session.status = 'failed'
            current_session.end_time = datetime.now()
            current_session.error = 'CUDA out of memory'
            current_session.logs.append('Training failed: CUDA out of memory')
            self.db.save_neural_training_session(current_session)
        
        # Verify error state
        final_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(final_session)
        self.assertEqual(final_session.status, 'failed')
        self.assertIsNotNone(final_session.error)
        self.assertEqual(final_session.error, 'CUDA out of memory')
        self.assertIsNotNone(final_session.end_time)
    
    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent training sessions."""
        sessions = []
        
        # Create multiple sessions
        for i in range(3):
            session_id = f"test-session-{i}"
            session = NeuralTrainingSession(
                session_id=session_id,
                status='running',
                progress=i * 25,
                start_time=datetime.now(),
                config=self.sample_config,
                logs=[f'Session {i} started'],
                loss_history=[0.5 + i * 0.1],
                epoch_history=[i + 1],
                timestamp_history=[],
                cpu_usage=[25.0 + i * 5],
                memory_usage=[45.0 + i * 3],
                gpu_usage=[60.0 + i * 2],
                current_epoch=i + 1,
                total_epochs=5,
                created_at=datetime.now()
            )
            sessions.append(session)
            self.db.save_neural_training_session(session)
        
        # Retrieve all sessions
        all_sessions = self.db.get_all_neural_training_sessions()
        self.assertEqual(len(all_sessions), 3)
        
        # Verify each session (order may vary, so check all sessions exist)
        session_ids = [session.session_id for session in all_sessions]
        expected_ids = [f"test-session-{i}" for i in range(3)]
        self.assertEqual(set(session_ids), set(expected_ids))
        
        for session in all_sessions:
            session_num = int(session.session_id.split('-')[-1])
            self.assertEqual(session.status, 'running')
            self.assertEqual(session.progress, session_num * 25)
            self.assertEqual(session.current_epoch, session_num + 1)
    
    @patch('api.routes.psutil.cpu_percent')
    @patch('api.routes.psutil.virtual_memory')
    def test_system_resources_monitoring(self, mock_memory, mock_cpu):
        """Test system resources monitoring."""
        # Mock system resources
        mock_cpu.return_value = 25.5
        mock_memory.return_value = MagicMock(percent=45.2)
        
        # Test system resources function
        resources = get_system_resources()
        
        self.assertIn('cpu_percent', resources)
        self.assertIn('memory_percent', resources)
        self.assertEqual(resources['cpu_percent'], 25.5)
        self.assertEqual(resources['memory_percent'], 45.2)
    
    @patch('api.routes.psutil.Process')
    def test_process_resources_monitoring(self, mock_process):
        """Test process resources monitoring."""
        # Mock process resources
        mock_process_instance = MagicMock()
        mock_process_instance.cpu_percent.return_value = 15.3
        mock_process_instance.memory_percent.return_value = 12.7
        mock_process.return_value = mock_process_instance
        
        # Test process resources function
        resources = get_process_resources()
        
        self.assertIn('cpu_percent', resources)
        self.assertIn('memory_percent', resources)
        self.assertEqual(resources['cpu_percent'], 15.3)
        self.assertEqual(resources['memory_percent'], 12.7)


class TestEnhancedNeuralTrainingAPI(unittest.TestCase):
    """Test cases for enhanced neural training API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test database
        self.test_db_path = "test_azul_api.db"
        self.db = AzulDatabase(self.test_db_path)
        
        # Sample training configuration
        self.sample_config = {
            'config': 'small',
            'device': 'cpu',
            'epochs': 5,
            'samples': 500,
            'batch_size': 16,
            'learning_rate': 0.001
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    @patch('api.routes.get_process_resources')
    def test_enhanced_training_status_endpoint(self, mock_resources):
        """Test enhanced training status endpoint."""
        # Mock process resources
        mock_resources.return_value = {
            'cpu_percent': 25.5,
            'memory_percent': 45.2
        }
        
        # Create a test session
        session_id = "test-api-session"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=60,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=['Training in progress'],
            loss_history=[0.5, 0.3, 0.2],
            epoch_history=[1, 2, 3],
            timestamp_history=[],
            cpu_usage=[25.0, 30.0, 28.0],
            memory_usage=[45.0, 48.0, 47.0],
            gpu_usage=[60.0, 65.0, 62.0],
            current_epoch=3,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        self.db.save_neural_training_session(session)
        
        # Note: This test would require a Flask app context to test the actual endpoint
        # For now, we just verify the session was saved correctly
        retrieved_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.status, 'running')
        self.assertEqual(retrieved_session.progress, 60)
        self.assertEqual(len(retrieved_session.loss_history), 3)
    
    def test_all_sessions_endpoint_data(self):
        """Test data structure for all sessions endpoint."""
        # Create multiple sessions with different statuses
        sessions_data = [
            {'session_id': 'session-1', 'status': 'completed', 'progress': 100},
            {'session_id': 'session-2', 'status': 'running', 'progress': 50},
            {'session_id': 'session-3', 'status': 'failed', 'progress': 25}
        ]
        
        for data in sessions_data:
            session = NeuralTrainingSession(
                session_id=data['session_id'],
                status=data['status'],
                progress=data['progress'],
                start_time=datetime.now(),
                config=self.sample_config,
                logs=[],
                loss_history=[],
                epoch_history=[],
                timestamp_history=[],
                cpu_usage=[],
                memory_usage=[],
                gpu_usage=[],
                current_epoch=0,
                total_epochs=5,
                created_at=datetime.now()
            )
            self.db.save_neural_training_session(session)
        
        # Retrieve all sessions
        all_sessions = self.db.get_all_neural_training_sessions()
        self.assertEqual(len(all_sessions), 3)
        
        # Verify session data
        for session in all_sessions:
            self.assertIn(session.session_id, ['session-1', 'session-2', 'session-3'])
            self.assertIn(session.status, ['completed', 'running', 'failed'])
            self.assertIn(session.progress, [100, 50, 25])
    
    def test_session_deletion(self):
        """Test session deletion functionality."""
        session_id = "test-delete-session"
        session = NeuralTrainingSession(
            session_id=session_id,
            status='running',
            progress=30,
            start_time=datetime.now(),
            config=self.sample_config,
            logs=[],
            loss_history=[],
            epoch_history=[],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            current_epoch=1,
            total_epochs=5,
            created_at=datetime.now()
        )
        
        # Save session
        self.db.save_neural_training_session(session)
        
        # Verify session exists
        retrieved_session = self.db.get_neural_training_session(session_id)
        self.assertIsNotNone(retrieved_session)
        
        # Delete session
        success = self.db.delete_neural_training_session(session_id)
        self.assertTrue(success)
        
        # Verify session is deleted
        deleted_session = self.db.get_neural_training_session(session_id)
        self.assertIsNone(deleted_session)


if __name__ == '__main__':
    unittest.main() 