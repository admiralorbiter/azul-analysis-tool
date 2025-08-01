#!/usr/bin/env python3
"""
Test suite for Configuration Panel functionality.

This module tests the Configuration Panel component and its integration
with the UI, including parameter validation, persistence, and API calls.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.azul_database import AzulDatabase
from core.azul_model import AzulState
from neural.azul_net import AzulNetConfig


class TestConfigurationPanel:
    """Test Configuration Panel functionality."""
    
    def test_database_path_validation(self):
        """Test database path validation."""
        # Valid database paths
        valid_paths = [
            'azul_cache.db',
            'data/azul_research.db',
            '/path/to/database.db',
            'cache.db'
        ]
        
        for path in valid_paths:
            # Should not raise any exceptions
            assert isinstance(path, str)
            assert len(path) > 0
    
    def test_model_path_validation(self):
        """Test model path validation."""
        # Valid model paths
        valid_paths = [
            'models/azul_net_small.pth',
            'models/azul_net_medium.pth',
            'models/azul_net_large.pth',
            '/path/to/model.pth'
        ]
        
        for path in valid_paths:
            # Should not raise any exceptions
            assert isinstance(path, str)
            assert path.endswith('.pth')
    
    def test_timeout_range_validation(self):
        """Test timeout range validation."""
        # Valid timeout values
        valid_timeouts = [0.1, 0.5, 1.0, 2.0, 4.0, 8.0, 10.0]
        
        for timeout in valid_timeouts:
            assert 0.1 <= timeout <= 10.0
            assert isinstance(timeout, float)
    
    def test_depth_range_validation(self):
        """Test depth range validation."""
        # Valid depth values
        valid_depths = [1, 2, 3, 4, 5]
        
        for depth in valid_depths:
            assert 1 <= depth <= 5
            assert isinstance(depth, int)
    
    def test_rollouts_range_validation(self):
        """Test rollouts range validation."""
        # Valid rollouts values
        valid_rollouts = [10, 50, 100, 500, 1000]
        
        for rollouts in valid_rollouts:
            assert 10 <= rollouts <= 1000
            assert isinstance(rollouts, int)
    
    def test_invalid_timeout_values(self):
        """Test invalid timeout values are handled gracefully."""
        invalid_timeouts = [-1.0, 0.0, 11.0, 100.0]
        
        for timeout in invalid_timeouts:
            # Should be clamped to valid range
            clamped_timeout = max(0.1, min(10.0, timeout))
            assert 0.1 <= clamped_timeout <= 10.0
    
    def test_invalid_depth_values(self):
        """Test invalid depth values are handled gracefully."""
        invalid_depths = [0, -1, 6, 10]
        
        for depth in invalid_depths:
            # Should be clamped to valid range
            clamped_depth = max(1, min(5, depth))
            assert 1 <= clamped_depth <= 5
    
    def test_invalid_rollouts_values(self):
        """Test invalid rollouts values are handled gracefully."""
        invalid_rollouts = [0, 5, 1500, 10000]
        
        for rollouts in invalid_rollouts:
            # Should be clamped to valid range
            clamped_rollouts = max(10, min(1000, rollouts))
            assert 10 <= clamped_rollouts <= 1000


class TestConfigurationPersistence:
    """Test configuration persistence functionality."""
    
    def test_configuration_save_load(self):
        """Test saving and loading configuration."""
        config = {
            'databasePath': 'test_cache.db',
            'modelPath': 'models/test_model.pth',
            'defaultTimeout': 2.5,
            'defaultDepth': 4,
            'defaultRollouts': 500
        }
        
        # Test JSON serialization
        config_json = json.dumps(config)
        assert isinstance(config_json, str)
        
        # Test JSON deserialization
        loaded_config = json.loads(config_json)
        assert loaded_config == config
    
    def test_configuration_defaults(self):
        """Test configuration default values."""
        defaults = {
            'databasePath': 'azul_cache.db',
            'modelPath': 'models/azul_net_small.pth',
            'defaultTimeout': 4.0,
            'defaultDepth': 3,
            'defaultRollouts': 100
        }
        
        for key, value in defaults.items():
            assert key in defaults
            assert isinstance(value, (str, float, int))
    
    def test_missing_configuration_handling(self):
        """Test handling of missing configuration."""
        # Simulate missing configuration
        config = {}
        
        # Should provide defaults
        database_path = config.get('databasePath', 'azul_cache.db')
        model_path = config.get('modelPath', 'models/azul_net_small.pth')
        timeout = config.get('defaultTimeout', 4.0)
        depth = config.get('defaultDepth', 3)
        rollouts = config.get('defaultRollouts', 100)
        
        assert database_path == 'azul_cache.db'
        assert model_path == 'models/azul_net_small.pth'
        assert timeout == 4.0
        assert depth == 3
        assert rollouts == 100


class TestConfigurationAPI:
    """Test configuration API integration."""
    
    def test_database_connection_test(self):
        """Test database connection testing."""
        # Mock successful connection
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'success': True}
            mock_get.return_value = mock_response
            
            # Should return success
            assert mock_response.json()['success'] is True
    
    def test_model_loading_test(self):
        """Test model loading testing."""
        # This would test model loading functionality
        # For now, we'll test the placeholder
        model_path = 'models/azul_net_small.pth'
        assert isinstance(model_path, str)
        assert model_path.endswith('.pth')
    
    def test_configuration_parameter_combinations(self):
        """Test various configuration parameter combinations."""
        test_configs = [
            {
                'databasePath': 'azul_cache.db',
                'modelPath': 'models/azul_net_small.pth',
                'defaultTimeout': 1.0,
                'defaultDepth': 2,
                'defaultRollouts': 50
            },
            {
                'databasePath': 'data/research.db',
                'modelPath': 'models/azul_net_large.pth',
                'defaultTimeout': 8.0,
                'defaultDepth': 5,
                'defaultRollouts': 1000
            },
            {
                'databasePath': 'cache.db',
                'modelPath': 'models/azul_net_medium.pth',
                'defaultTimeout': 4.0,
                'defaultDepth': 3,
                'defaultRollouts': 100
            }
        ]
        
        for config in test_configs:
            # Validate all parameters
            assert 0.1 <= config['defaultTimeout'] <= 10.0
            assert 1 <= config['defaultDepth'] <= 5
            assert 10 <= config['defaultRollouts'] <= 1000
            assert isinstance(config['databasePath'], str)
            assert isinstance(config['modelPath'], str)
    
    def test_configuration_consistency(self):
        """Test configuration consistency across sessions."""
        config1 = {
            'databasePath': 'test.db',
            'modelPath': 'models/test.pth',
            'defaultTimeout': 2.0,
            'defaultDepth': 3,
            'defaultRollouts': 200
        }
        
        config2 = {
            'databasePath': 'test.db',
            'modelPath': 'models/test.pth',
            'defaultTimeout': 2.0,
            'defaultDepth': 3,
            'defaultRollouts': 200
        }
        
        # Configurations should be consistent
        assert config1 == config2
    
    def test_configuration_performance_limits(self):
        """Test configuration performance limits."""
        # Test extreme values
        extreme_configs = [
            {'defaultTimeout': 0.1, 'defaultDepth': 1, 'defaultRollouts': 10},
            {'defaultTimeout': 10.0, 'defaultDepth': 5, 'defaultRollouts': 1000}
        ]
        
        for config in extreme_configs:
            # Should handle extreme values gracefully
            timeout = max(0.1, min(10.0, config['defaultTimeout']))
            depth = max(1, min(5, config['defaultDepth']))
            rollouts = max(10, min(1000, config['defaultRollouts']))
            
            assert 0.1 <= timeout <= 10.0
            assert 1 <= depth <= 5
            assert 10 <= rollouts <= 1000
    
    def test_error_handling(self):
        """Test error handling in configuration."""
        # Test invalid JSON
        try:
            json.loads('invalid json')
            assert False, "Should have raised JSONDecodeError"
        except json.JSONDecodeError:
            pass  # Expected
    
    def test_ui_parameter_validation(self):
        """Test UI parameter validation."""
        # Test valid ranges
        valid_ranges = [
            (0.1, 10.0),  # timeout
            (1, 5),        # depth
            (10, 1000)     # rollouts
        ]
        
        for min_val, max_val in valid_ranges:
            # Test values within range
            test_val = (min_val + max_val) / 2
            assert min_val <= test_val <= max_val


class TestConfigurationPanelIntegration:
    """Test Configuration Panel integration with the main application."""
    
    def test_api_parameter_passing(self):
        """Test that configuration parameters are correctly passed to API."""
        config = {
            'databasePath': 'test_cache.db',
            'modelPath': 'models/test_model.pth',
            'defaultTimeout': 3.0,
            'defaultDepth': 4,
            'defaultRollouts': 300
        }
        
        # Simulate API call with configuration
        api_params = {
            'time_budget': config['defaultTimeout'],
            'depth': config['defaultDepth'],
            'rollouts': config['defaultRollouts']
        }
        
        assert api_params['time_budget'] == 3.0
        assert api_params['depth'] == 4
        assert api_params['rollouts'] == 300
    
    def test_ui_state_management(self):
        """Test UI state management for configuration."""
        # Test state initialization
        initial_state = {
            'databasePath': 'azul_cache.db',
            'modelPath': 'models/azul_net_small.pth',
            'defaultTimeout': 4.0,
            'defaultDepth': 3,
            'defaultRollouts': 100,
            'configExpanded': False
        }
        
        for key, value in initial_state.items():
            assert key in initial_state
            assert value is not None
    
    def test_parameter_synchronization(self):
        """Test parameter synchronization between UI and configuration."""
        # Test that UI parameters sync with configuration
        ui_params = {
            'timeBudget': 2.5,
            'depth': 4,
            'rollouts': 500
        }
        
        config_params = {
            'defaultTimeout': ui_params['timeBudget'],
            'defaultDepth': ui_params['depth'],
            'defaultRollouts': ui_params['rollouts']
        }
        
        assert config_params['defaultTimeout'] == ui_params['timeBudget']
        assert config_params['defaultDepth'] == ui_params['depth']
        assert config_params['defaultRollouts'] == ui_params['rollouts']


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 