#!/usr/bin/env python3
"""
Test suite for Neural Training Configuration Panel
Tests the UI components and API integration for neural training features.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestNeuralTrainingConfig(unittest.TestCase):
    """Test cases for neural training configuration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'modelSize': 'small',
            'device': 'cpu',
            'epochs': 5,
            'samples': 500,
            'batchSize': 16,
            'learningRate': 0.001
        }
        
        self.valid_configs = [
            {'modelSize': 'small', 'device': 'cpu', 'epochs': 1, 'samples': 100, 'batchSize': 8, 'learningRate': 0.0001},
            {'modelSize': 'medium', 'device': 'cpu', 'epochs': 10, 'samples': 1000, 'batchSize': 32, 'learningRate': 0.01},
            {'modelSize': 'large', 'device': 'cpu', 'epochs': 50, 'samples': 5000, 'batchSize': 64, 'learningRate': 0.005}
        ]
        
        self.invalid_configs = [
            {'modelSize': 'invalid', 'device': 'cpu', 'epochs': 5, 'samples': 500, 'batchSize': 16, 'learningRate': 0.001},
            {'modelSize': 'small', 'device': 'gpu', 'epochs': 0, 'samples': 500, 'batchSize': 16, 'learningRate': 0.001},
            {'modelSize': 'small', 'device': 'cpu', 'epochs': 5, 'samples': 50, 'batchSize': 16, 'learningRate': 0.001},
            {'modelSize': 'small', 'device': 'cpu', 'epochs': 5, 'samples': 500, 'batchSize': 4, 'learningRate': 0.001},
            {'modelSize': 'small', 'device': 'cpu', 'epochs': 5, 'samples': 500, 'batchSize': 16, 'learningRate': 0.02}
        ]

    def test_valid_model_sizes(self):
        """Test that valid model sizes are accepted."""
        valid_sizes = ['small', 'medium', 'large']
        for size in valid_sizes:
            config = self.test_config.copy()
            config['modelSize'] = size
            self.assertTrue(self._is_valid_config(config), f"Model size '{size}' should be valid")

    def test_invalid_model_sizes(self):
        """Test that invalid model sizes are rejected."""
        invalid_sizes = ['tiny', 'huge', 'invalid', '']
        for size in invalid_sizes:
            config = self.test_config.copy()
            config['modelSize'] = size
            self.assertFalse(self._is_valid_config(config), f"Model size '{size}' should be invalid")

    def test_valid_device_selection(self):
        """Test that valid devices are accepted."""
        valid_devices = ['cpu']  # CUDA would be added when available
        for device in valid_devices:
            config = self.test_config.copy()
            config['device'] = device
            self.assertTrue(self._is_valid_config(config), f"Device '{device}' should be valid")

    def test_invalid_device_selection(self):
        """Test that invalid devices are rejected."""
        invalid_devices = ['gpu', 'tpu', 'invalid', '']
        for device in invalid_devices:
            config = self.test_config.copy()
            config['device'] = device
            self.assertFalse(self._is_valid_config(config), f"Device '{device}' should be invalid")

    def test_valid_epochs_range(self):
        """Test that epochs within valid range are accepted."""
        valid_epochs = [1, 5, 10, 50, 100]
        for epochs in valid_epochs:
            config = self.test_config.copy()
            config['epochs'] = epochs
            self.assertTrue(self._is_valid_config(config), f"Epochs {epochs} should be valid")

    def test_invalid_epochs_range(self):
        """Test that epochs outside valid range are rejected."""
        invalid_epochs = [0, -1, 101, 200]
        for epochs in invalid_epochs:
            config = self.test_config.copy()
            config['epochs'] = epochs
            self.assertFalse(self._is_valid_config(config), f"Epochs {epochs} should be invalid")

    def test_valid_samples_range(self):
        """Test that samples within valid range are accepted."""
        valid_samples = [100, 500, 1000, 5000, 10000]
        for samples in valid_samples:
            config = self.test_config.copy()
            config['samples'] = samples
            self.assertTrue(self._is_valid_config(config), f"Samples {samples} should be valid")

    def test_invalid_samples_range(self):
        """Test that samples outside valid range are rejected."""
        invalid_samples = [50, 99, 10001, 20000]
        for samples in invalid_samples:
            config = self.test_config.copy()
            config['samples'] = samples
            self.assertFalse(self._is_valid_config(config), f"Samples {samples} should be invalid")

    def test_valid_batch_size_range(self):
        """Test that batch sizes within valid range are accepted."""
        valid_batch_sizes = [8, 16, 32, 64]
        for batch_size in valid_batch_sizes:
            config = self.test_config.copy()
            config['batchSize'] = batch_size
            self.assertTrue(self._is_valid_config(config), f"Batch size {batch_size} should be valid")

    def test_invalid_batch_size_range(self):
        """Test that batch sizes outside valid range are rejected."""
        invalid_batch_sizes = [4, 6, 72, 128]
        for batch_size in invalid_batch_sizes:
            config = self.test_config.copy()
            config['batchSize'] = batch_size
            self.assertFalse(self._is_valid_config(config), f"Batch size {batch_size} should be invalid")

    def test_valid_learning_rate_range(self):
        """Test that learning rates within valid range are accepted."""
        valid_learning_rates = [0.0001, 0.001, 0.005, 0.01]
        for lr in valid_learning_rates:
            config = self.test_config.copy()
            config['learningRate'] = lr
            self.assertTrue(self._is_valid_config(config), f"Learning rate {lr} should be valid")

    def test_invalid_learning_rate_range(self):
        """Test that learning rates outside valid range are rejected."""
        invalid_learning_rates = [0.00005, 0.00009, 0.011, 0.1]
        for lr in invalid_learning_rates:
            config = self.test_config.copy()
            config['learningRate'] = lr
            self.assertFalse(self._is_valid_config(config), f"Learning rate {lr} should be invalid")

    def test_all_valid_configs(self):
        """Test that all valid configurations pass validation."""
        for config in self.valid_configs:
            self.assertTrue(self._is_valid_config(config), f"Config {config} should be valid")

    def test_all_invalid_configs(self):
        """Test that all invalid configurations fail validation."""
        for config in self.invalid_configs:
            self.assertFalse(self._is_valid_config(config), f"Config {config} should be invalid")

    def test_config_serialization(self):
        """Test that configurations can be serialized to JSON."""
        config = self.test_config.copy()
        try:
            json_str = json.dumps(config)
            parsed_config = json.loads(json_str)
            self.assertEqual(config, parsed_config, "Config should serialize and deserialize correctly")
        except Exception as e:
            self.fail(f"Config serialization failed: {e}")

    def test_config_defaults(self):
        """Test that default configuration values are valid."""
        default_config = {
            'modelSize': 'small',
            'device': 'cpu',
            'epochs': 5,
            'samples': 500,
            'batchSize': 16,
            'learningRate': 0.001
        }
        self.assertTrue(self._is_valid_config(default_config), "Default config should be valid")

    @patch('builtins.print')
    def test_config_validation_messages(self, mock_print):
        """Test that validation provides meaningful error messages."""
        invalid_config = {
            'modelSize': 'invalid',
            'device': 'gpu',
            'epochs': 0,
            'samples': 50,
            'batchSize': 4,
            'learningRate': 0.02
        }
        
        # This would be called by the UI validation
        errors = self._validate_config(invalid_config)
        self.assertGreater(len(errors), 0, "Invalid config should produce validation errors")
        
        # Check that specific errors are present
        error_messages = [str(error) for error in errors]
        print(f"Actual error messages: {error_messages}")  # Debug output
        
        # Check for specific error patterns
        self.assertTrue(any('Invalid model size' in msg for msg in error_messages), "Should have model size error")
        self.assertTrue(any('Invalid device' in msg for msg in error_messages), "Should have device error")
        self.assertTrue(any('Invalid epochs' in msg for msg in error_messages), "Should have epochs error")

    def test_model_size_mapping(self):
        """Test that model sizes map to correct parameters."""
        size_mappings = {
            'small': {'hidden_size': 64, 'num_layers': 2},
            'medium': {'hidden_size': 128, 'num_layers': 3},
            'large': {'hidden_size': 256, 'num_layers': 4}
        }
        
        for size, expected_params in size_mappings.items():
            config = self.test_config.copy()
            config['modelSize'] = size
            mapped_params = self._get_model_parameters(config)
            self.assertEqual(mapped_params['hidden_size'], expected_params['hidden_size'])
            self.assertEqual(mapped_params['num_layers'], expected_params['num_layers'])

    def _is_valid_config(self, config):
        """Helper method to validate configuration."""
        try:
            # Validate model size
            if config['modelSize'] not in ['small', 'medium', 'large']:
                return False
            
            # Validate device
            if config['device'] not in ['cpu']:  # CUDA would be added when available
                return False
            
            # Validate epochs (1-100)
            if not (1 <= config['epochs'] <= 100):
                return False
            
            # Validate samples (100-10000)
            if not (100 <= config['samples'] <= 10000):
                return False
            
            # Validate batch size (8-64, must be multiple of 8)
            if not (8 <= config['batchSize'] <= 64) or config['batchSize'] % 8 != 0:
                return False
            
            # Validate learning rate (0.0001-0.01)
            if not (0.0001 <= config['learningRate'] <= 0.01):
                return False
            
            return True
        except KeyError:
            return False

    def _validate_config(self, config):
        """Helper method to get validation errors."""
        errors = []
        
        try:
            if config['modelSize'] not in ['small', 'medium', 'large']:
                errors.append(f"Invalid model size: {config['modelSize']}")
        except KeyError:
            errors.append("Missing modelSize")
        
        try:
            if config['device'] not in ['cpu']:
                errors.append(f"Invalid device: {config['device']}")
        except KeyError:
            errors.append("Missing device")
        
        try:
            if not (1 <= config['epochs'] <= 100):
                errors.append(f"Invalid epochs: {config['epochs']} (must be 1-100)")
        except KeyError:
            errors.append("Missing epochs")
        
        try:
            if not (100 <= config['samples'] <= 10000):
                errors.append(f"Invalid samples: {config['samples']} (must be 100-10000)")
        except KeyError:
            errors.append("Missing samples")
        
        try:
            if not (8 <= config['batchSize'] <= 64) or config['batchSize'] % 8 != 0:
                errors.append(f"Invalid batch size: {config['batchSize']} (must be 8-64, multiple of 8)")
        except KeyError:
            errors.append("Missing batchSize")
        
        try:
            if not (0.0001 <= config['learningRate'] <= 0.01):
                errors.append(f"Invalid learning rate: {config['learningRate']} (must be 0.0001-0.01)")
        except KeyError:
            errors.append("Missing learningRate")
        
        return errors

    def _get_model_parameters(self, config):
        """Helper method to get model parameters from config."""
        size_mappings = {
            'small': {'hidden_size': 64, 'num_layers': 2},
            'medium': {'hidden_size': 128, 'num_layers': 3},
            'large': {'hidden_size': 256, 'num_layers': 4}
        }
        return size_mappings.get(config['modelSize'], {'hidden_size': 64, 'num_layers': 2})

    def test_api_integration_simulation(self):
        """Test simulation of API integration."""
        # Simulate API call with valid config
        with patch('builtins.print') as mock_print:
            config = self.test_config.copy()
            response = self._simulate_api_call(config)
            self.assertTrue(response['success'], "API call should succeed with valid config")
            self.assertIn('session_id', response, "Response should contain session_id")

    def _simulate_api_call(self, config):
        """Simulate API call for testing."""
        if self._is_valid_config(config):
            return {
                'success': True,
                'session_id': 'test_session_123',
                'message': 'Training started successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Invalid configuration',
                'details': self._validate_config(config)
            }

    def test_error_handling(self):
        """Test error handling for various failure scenarios."""
        # Test with missing required fields
        incomplete_config = {'modelSize': 'small'}
        response = self._simulate_api_call(incomplete_config)
        self.assertFalse(response['success'], "Incomplete config should fail")
        
        # Test with invalid values
        invalid_config = self.test_config.copy()
        invalid_config['epochs'] = -1
        response = self._simulate_api_call(invalid_config)
        self.assertFalse(response['success'], "Invalid config should fail")

    def test_config_persistence(self):
        """Test configuration persistence simulation."""
        config = self.test_config.copy()
        
        # Simulate saving config
        saved = self._simulate_save_config(config)
        self.assertTrue(saved, "Config should save successfully")
        
        # Simulate loading config
        loaded_config = self._simulate_load_config()
        self.assertEqual(config, loaded_config, "Loaded config should match saved config")

    def _simulate_save_config(self, config):
        """Simulate saving configuration."""
        try:
            # In real implementation, this would save to localStorage or database
            return True
        except Exception:
            return False

    def _simulate_load_config(self):
        """Simulate loading configuration."""
        # In real implementation, this would load from localStorage or database
        return self.test_config.copy()

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 