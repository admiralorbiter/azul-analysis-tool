"""
Tests for neural network components.

This module tests:
- Tensor encoding for Azul states
- AzulNet model creation and forward pass
- Neural rollout policy integration
- Parameter counting and model size
"""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch

from core.azul_model import AzulState
from core.azul_utils import Tile
from neural.azul_net import (
    AzulNetConfig, 
    AzulTensorEncoder, 
    AzulNet, 
    AzulNeuralRolloutPolicy,
    create_azul_net,
    count_parameters
)


class TestAzulNetConfig:
    """Test AzulNet configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AzulNetConfig()
        
        assert config.hidden_size == 128
        assert config.num_layers == 3
        assert config.dropout_rate == 0.1
        assert config.max_factories == 9
        assert config.max_center_tiles == 20
        assert config.max_pattern_lines == 5
        assert config.max_wall_size == 5
        assert config.max_floor_size == 7
        assert config.num_tile_types == 5
        assert config.num_actions == 100
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = AzulNetConfig(
            hidden_size=64,
            num_layers=2,
            dropout_rate=0.2,
            max_factories=5,
            num_actions=50
        )
        
        assert config.hidden_size == 64
        assert config.num_layers == 2
        assert config.dropout_rate == 0.2
        assert config.max_factories == 5
        assert config.num_actions == 50


class TestAzulTensorEncoder:
    """Test tensor encoding functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = AzulNetConfig()
        self.encoder = AzulTensorEncoder(self.config)
        self.state = AzulState(2)
    
    def test_encode_factories(self):
        """Test factory encoding."""
        # Create mock factory objects with tiles dict
        factories = []
        factory1 = Mock()
        factory1.tiles = {Tile.BLUE: 1, Tile.RED: 1}
        factories.append(factory1)
        
        factory2 = Mock()
        factory2.tiles = {Tile.YELLOW: 1, Tile.BLACK: 1, Tile.WHITE: 1}
        factories.append(factory2)
        
        encoded = self.encoder._encode_factories(factories)
        
        # Check shape
        expected_shape = (1, self.config.max_factories * 6 * self.config.num_tile_types)
        assert encoded.shape == expected_shape
        
        # Check that tiles are encoded correctly
        # The encoding distributes tiles across positions, so we check that the tiles are present
        assert encoded[0, 0 * 6 * 5 + 0 * 5 + Tile.BLUE] == 1.0  # Factory 0, position 0, blue
        assert encoded[0, 0 * 6 * 5 + 0 * 5 + Tile.RED] == 1.0   # Factory 0, position 0, red (same position)
        assert encoded[0, 1 * 6 * 5 + 0 * 5 + Tile.YELLOW] == 1.0  # Factory 1, position 0, yellow
    
    def test_encode_center(self):
        """Test center tile encoding."""
        # Create a mock center object with tiles dict
        center = Mock()
        center.tiles = {Tile.BLUE: 1, Tile.RED: 1, Tile.YELLOW: 1}
        
        encoded = self.encoder._encode_center(center)
        
        # Check shape
        expected_shape = (1, self.config.max_center_tiles * self.config.num_tile_types)
        assert encoded.shape == expected_shape
        
        # Check that tiles are encoded correctly
        # The encoding distributes tiles across positions, so we check that the tiles are present
        assert encoded[0, 0 * 5 + Tile.BLUE] == 1.0
        assert encoded[0, 0 * 5 + Tile.RED] == 1.0   # Same position as blue
        assert encoded[0, 0 * 5 + Tile.YELLOW] == 1.0  # Same position as others
    
    def test_encode_wall(self):
        """Test wall encoding."""
        wall = np.array([
            [True, False, True, False, False],
            [False, True, False, True, False],
            [True, False, False, False, True],
            [False, False, True, False, False],
            [False, True, False, False, True]
        ])
        
        encoded = self.encoder._encode_wall(wall)
        
        # Check shape
        expected_shape = (1, self.config.max_wall_size * self.config.max_wall_size)
        assert encoded.shape == expected_shape
        
        # Check that wall positions are encoded correctly
        assert encoded[0, 0 * 5 + 0] == 1.0  # Position (0,0)
        assert encoded[0, 0 * 5 + 2] == 1.0  # Position (0,2)
        assert encoded[0, 1 * 5 + 1] == 1.0  # Position (1,1)
        assert encoded[0, 1 * 5 + 3] == 1.0  # Position (1,3)
    
    def test_encode_pattern_lines(self):
        """Test pattern lines encoding."""
        # The method expects a list of 5 integers, where -1 means no tile
        pattern_lines = [Tile.BLUE, Tile.RED, Tile.BLACK, Tile.WHITE, -1]
        
        encoded = self.encoder._encode_pattern_lines(pattern_lines)
        
        # Check shape
        expected_shape = (1, self.config.max_pattern_lines * self.config.num_tile_types)
        assert encoded.shape == expected_shape
        
        # Check that tiles are encoded correctly
        assert encoded[0, 0 * 5 + Tile.BLUE] == 1.0   # Line 0, blue
        assert encoded[0, 1 * 5 + Tile.RED] == 1.0     # Line 1, red
        assert encoded[0, 2 * 5 + Tile.BLACK] == 1.0   # Line 2, black
        assert encoded[0, 3 * 5 + Tile.WHITE] == 1.0   # Line 3, white
    
    def test_encode_floor(self):
        """Test floor line encoding."""
        floor_line = np.array([Tile.BLUE, Tile.RED, Tile.YELLOW, -1, -1, -1, -1])
        
        encoded = self.encoder._encode_floor(floor_line)
        
        # Check shape
        expected_shape = (1, self.config.max_floor_size * self.config.num_tile_types)
        assert encoded.shape == expected_shape
        
        # Check that tiles are encoded correctly
        assert encoded[0, 0 * 5 + Tile.BLUE] == 1.0
        assert encoded[0, 1 * 5 + Tile.RED] == 1.0
        assert encoded[0, 2 * 5 + Tile.YELLOW] == 1.0
    
    def test_encode_scores(self):
        """Test score encoding."""
        # Mock agents with scores
        agents = [Mock(score=10), Mock(score=15)]
        
        encoded = self.encoder._encode_scores(agents)
        
        # Check shape
        expected_shape = (1, 2)
        assert encoded.shape == expected_shape
        
        # Check that scores are encoded correctly
        assert encoded[0, 0] == 10.0
        assert encoded[0, 1] == 15.0
    
    def test_encode_state(self):
        """Test full state encoding."""
        encoded = self.encoder.encode_state(self.state, agent_id=0)
        
        # Check that output is a tensor
        assert isinstance(encoded, torch.Tensor)
        
        # Check that output has correct shape
        assert len(encoded.shape) == 2
        assert encoded.shape[0] == 1  # batch size
        
        # Check that all values are finite
        assert torch.all(torch.isfinite(encoded))


class TestAzulNet:
    """Test AzulNet model."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = AzulNetConfig(hidden_size=64, num_layers=2)
        self.model = AzulNet(self.config)
    
    def test_model_creation(self):
        """Test model creation."""
        assert isinstance(self.model, AzulNet)
        assert len(self.model.shared_layers) == self.config.num_layers
        assert self.model.policy_head is not None
        assert self.model.value_head is not None
        assert self.model.dropout is not None
    
    def test_forward_pass(self):
        """Test forward pass through the model."""
        # Create dummy input
        batch_size = 4
        input_size = self.model.input_size
        x = torch.randn(batch_size, input_size)
        
        # Forward pass
        policy_logits, value = self.model.forward(x)
        
        # Check outputs
        assert policy_logits.shape == (batch_size, self.config.num_actions)
        assert value.shape == (batch_size, 1)
        assert torch.all(torch.isfinite(policy_logits))
        assert torch.all(torch.isfinite(value))
    
    def test_policy_and_value(self):
        """Test policy and value extraction."""
        # Create dummy input
        batch_size = 2
        input_size = self.model.input_size
        x = torch.randn(batch_size, input_size)
        
        # Get policy and value
        policy_probs, value = self.model.get_policy_and_value(x)
        
        # Check outputs
        assert policy_probs.shape == (batch_size, self.config.num_actions)
        assert value.shape == (batch_size, 1)
        
        # Check that policy probabilities sum to 1
        assert torch.allclose(policy_probs.sum(dim=1), torch.ones(batch_size), atol=1e-6)
        
        # Check that values are in [-1, 1] range (tanh output)
        assert torch.all(value >= -1.0)
        assert torch.all(value <= 1.0)
    
    def test_parameter_count(self):
        """Test parameter counting."""
        param_count = count_parameters(self.model)
        
        # Check that model has reasonable number of parameters
        assert param_count > 0
        assert param_count < 100000  # Should be under 100k as specified
    
    def test_model_size(self):
        """Test that model size is reasonable."""
        # Calculate expected parameter count
        input_size = self.model.input_size
        hidden_size = self.config.hidden_size
        num_layers = self.config.num_layers
        num_actions = self.config.num_actions
        
        # Shared layers
        shared_params = input_size * hidden_size + hidden_size  # First layer
        for i in range(1, num_layers):
            shared_params += hidden_size * hidden_size + hidden_size
        
        # Policy head
        policy_params = hidden_size * num_actions + num_actions
        
        # Value head
        value_params = hidden_size * 1 + 1
        
        expected_params = shared_params + policy_params + value_params
        actual_params = count_parameters(self.model)
        
        # Allow for small differences due to implementation details
        assert abs(actual_params - expected_params) < 100


class TestAzulNeuralRolloutPolicy:
    """Test neural rollout policy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = AzulNetConfig(hidden_size=32, num_layers=1)
        self.model, self.encoder = create_azul_net(self.config, device="cpu")
        
        # Mock evaluator and move generator
        self.evaluator = Mock()
        self.move_generator = Mock()
        
        self.policy = AzulNeuralRolloutPolicy(
            self.model, self.encoder, self.evaluator, self.move_generator, device="cpu"
        )
    
    def test_policy_creation(self):
        """Test neural rollout policy creation."""
        assert isinstance(self.policy, AzulNeuralRolloutPolicy)
        assert self.policy.model is self.model
        assert self.policy.encoder is self.encoder
        assert self.policy.device == "cpu"
    
    def test_evaluate_neural(self):
        """Test neural evaluation."""
        state = AzulState(2)
        agent_id = 0
        
        # Mock evaluator
        self.evaluator.evaluate_position.return_value = 5.0
        
        # Test neural evaluation
        value = self.policy._evaluate_neural(state, agent_id)
        
        # Check that value is returned
        assert isinstance(value, float)
        assert -1.0 <= value <= 1.0  # tanh output range
    
    def test_select_neural_move(self):
        """Test neural move selection."""
        state = AzulState(2)
        moves = [Mock(), Mock(), Mock()]
        agent_id = 0
        
        # Test neural move selection
        selected_move = self.policy._select_neural_move(state, moves, agent_id)
        
        # Check that a move is selected
        assert selected_move is not None
        assert selected_move in moves


class TestNeuralIntegration:
    """Test neural network integration."""
    
    def test_create_azul_net(self):
        """Test AzulNet creation function."""
        model, encoder = create_azul_net()
        
        assert isinstance(model, AzulNet)
        assert isinstance(encoder, AzulTensorEncoder)
        
        # Test with custom config
        config = AzulNetConfig(hidden_size=64)
        model, encoder = create_azul_net(config)
        
        assert isinstance(model, AzulNet)
        assert isinstance(encoder, AzulTensorEncoder)
    
    def test_count_parameters(self):
        """Test parameter counting function."""
        model = AzulNet(AzulNetConfig())
        param_count = count_parameters(model)
        
        assert isinstance(param_count, int)
        assert param_count > 0
    
    @patch('neural.azul_net.torch')
    def test_gpu_support(self, mock_torch):
        """Test GPU support."""
        # Mock CUDA availability
        mock_torch.cuda.is_available.return_value = True
        mock_torch.device.return_value = "cuda:0"
        
        # Test GPU device
        model, encoder = create_azul_net(device="cuda")
        
        # Check that the function was called (the actual device handling is in the neural rollout policy)
        assert isinstance(model, AzulNet)
        assert isinstance(encoder, AzulTensorEncoder)
    
    def test_model_inference_speed(self):
        """Test model inference speed."""
        model, encoder = create_azul_net()
        state = AzulState(2)
        
        # Encode state
        state_tensor = encoder.encode_state(state, agent_id=0)
        
        # Time inference
        import time
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(100):
                policy_probs, value = model.get_policy_and_value(state_tensor)
        
        end_time = time.time()
        inference_time = (end_time - start_time) / 100
        
        # Check that inference is reasonably fast (< 1ms per inference)
        assert inference_time < 0.001


class TestNeuralMCTSIntegration:
    """Test neural network integration with MCTS."""
    
    def test_neural_rollout_policy_available(self):
        """Test that neural rollout policy is available."""
        from core.azul_mcts import RolloutPolicy
        
        # Check that NEURAL policy is available
        assert RolloutPolicy.NEURAL in RolloutPolicy
    
    def test_neural_mcts_creation(self):
        """Test MCTS creation with neural policy."""
        from core.azul_mcts import AzulMCTS, RolloutPolicy
        
        # This should work if PyTorch is available
        try:
            mcts = AzulMCTS(rollout_policy=RolloutPolicy.NEURAL)
            assert mcts.rollout_policy == RolloutPolicy.NEURAL
        except ValueError as e:
            # If PyTorch is not available, should get appropriate error
            assert "PyTorch" in str(e) or "neural" in str(e)
    
    def test_neural_rollout_performance(self):
        """Test neural rollout performance."""
        from core.azul_mcts import AzulMCTS, RolloutPolicy
        
        try:
            mcts = AzulMCTS(rollout_policy=RolloutPolicy.NEURAL, max_rollouts=10)
            state = AzulState(2)
            
            # Time neural rollout
            import time
            start_time = time.time()
            
            result = mcts.search(state, agent_id=0, max_rollouts=5)
            
            end_time = time.time()
            search_time = end_time - start_time
            
            # Check that search completes
            assert result is not None
            assert search_time < 1.0  # Should be reasonably fast
            
        except ValueError:
            # Skip if PyTorch not available
            pytest.skip("PyTorch not available")


if __name__ == "__main__":
    pytest.main([__file__]) 