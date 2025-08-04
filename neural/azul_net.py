"""
Azul Neural Network Module

This module provides:
- Tensor encoding for Azul game states
- Small PyTorch MLP for policy and value prediction
- Integration with MCTS rollout policies
- GPU batching support with CPU fallback
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

try:
    from ..core.azul_model import AzulState
    from ..core.azul_utils import Tile, Action
except ImportError:
    # Fallback for direct import
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.azul_model import AzulState
    from core.azul_utils import Tile, Action


@dataclass
class AzulNetConfig:
    """Configuration for AzulNet."""
    # Model architecture
    hidden_size: int = 128
    num_layers: int = 3
    dropout_rate: float = 0.1
    
    # Input encoding
    max_factories: int = 9
    max_center_tiles: int = 20
    max_pattern_lines: int = 5
    max_wall_size: int = 5
    max_floor_size: int = 7
    
    # Output
    num_tile_types: int = 5  # Blue, Yellow, Red, Black, White
    num_actions: int = 100   # Approximate max legal moves per position


class AzulTensorEncoder:
    """Encodes Azul game states into tensors for neural networks."""
    
    def __init__(self, config: AzulNetConfig):
        self.config = config
        
    def encode_state(self, state: AzulState, agent_id: int = 0) -> torch.Tensor:
        """
        Encode an Azul state into a tensor representation.
        
        Args:
            state: The Azul game state
            agent_id: The agent to encode for (0 or 1)
            
        Returns:
            Tensor of shape [batch_size, feature_dim]
        """
        features = []
        
        # Encode factories (9 factories × 6 tiles each)
        factory_features = self._encode_factories(state.factories)
        features.append(factory_features)
        
        # Encode center tiles
        center_features = self._encode_center(state.centre_pool)
        features.append(center_features)
        
        # Encode player boards (grid state, pattern lines, floor)
        grid_features = self._encode_wall(state.agents[agent_id].grid_state)
        pattern_features = self._encode_pattern_lines(state.agents[agent_id].lines_tile)
        floor_features = self._encode_floor(state.agents[agent_id].floor_tiles)
        features.extend([grid_features, pattern_features, floor_features])
        
        # Encode opponent board (simplified)
        opponent_id = 1 - agent_id
        opponent_grid = self._encode_wall(state.agents[opponent_id].grid_state)
        opponent_pattern = self._encode_pattern_lines(state.agents[opponent_id].lines_tile)
        opponent_floor = self._encode_floor(state.agents[opponent_id].floor_tiles)
        features.extend([opponent_grid, opponent_pattern, opponent_floor])
        
        # Encode scores
        score_features = self._encode_scores(state.agents)
        features.append(score_features)
        
        # Concatenate all features
        return torch.cat(features, dim=-1)
    
    def _encode_factories(self, factories) -> torch.Tensor:
        """Encode factory tiles as one-hot vectors."""
        # factories is a list of TileDisplay objects
        batch_size = 1
        encoded = torch.zeros(batch_size, self.config.max_factories, 6, self.config.num_tile_types)
        
        for i, factory in enumerate(factories):
            if i >= self.config.max_factories:
                break
            # Access the tiles dict from TileDisplay
            for tile_type, count in factory.tiles.items():
                if count > 0 and tile_type in [Tile.BLUE, Tile.YELLOW, Tile.RED, Tile.BLACK, Tile.WHITE]:
                    # Distribute tiles across the 6 positions
                    for j in range(min(count, 6)):
                        encoded[0, i, j, tile_type] = 1.0
        
        return encoded.flatten(1)  # [batch_size, max_factories * 6 * num_tile_types]
    
    def _encode_center(self, center) -> torch.Tensor:
        """Encode center tiles as one-hot vectors."""
        # center is a TileDisplay object
        batch_size = 1
        encoded = torch.zeros(batch_size, self.config.max_center_tiles, self.config.num_tile_types)
        
        # Access the tiles dict from TileDisplay
        for tile_type, count in center.tiles.items():
            if count > 0 and tile_type in [Tile.BLUE, Tile.YELLOW, Tile.RED, Tile.BLACK, Tile.WHITE]:
                for i in range(min(count, self.config.max_center_tiles)):
                    encoded[0, i, tile_type] = 1.0
        
        return encoded.flatten(1)  # [batch_size, max_center_tiles * num_tile_types]
    
    def _encode_wall(self, wall: np.ndarray) -> torch.Tensor:
        """Encode wall as binary matrix."""
        batch_size = 1
        encoded = torch.zeros(batch_size, self.config.max_wall_size, self.config.max_wall_size)
        
        for i in range(min(wall.shape[0], self.config.max_wall_size)):
            for j in range(min(wall.shape[1], self.config.max_wall_size)):
                if wall[i, j]:
                    encoded[0, i, j] = 1.0
        
        return encoded.flatten(1)  # [batch_size, max_wall_size * max_wall_size]
    
    def _encode_pattern_lines(self, lines_tile: list) -> torch.Tensor:
        """Encode pattern lines as one-hot vectors."""
        # lines_tile is a list of 5 integers, where -1 means no tile
        batch_size = 1
        encoded = torch.zeros(batch_size, self.config.max_pattern_lines, self.config.num_tile_types)
        
        for i, tile_type in enumerate(lines_tile):
            if i >= self.config.max_pattern_lines:
                break
            if tile_type != -1 and tile_type in [Tile.BLUE, Tile.YELLOW, Tile.RED, Tile.BLACK, Tile.WHITE]:
                encoded[0, i, tile_type] = 1.0
        
        return encoded.flatten(1)  # [batch_size, max_pattern_lines * num_tile_types]
    
    def _encode_floor(self, floor_tiles: list) -> torch.Tensor:
        """Encode floor line as one-hot vector."""
        # floor_tiles is a list of tile types
        batch_size = 1
        encoded = torch.zeros(batch_size, self.config.max_floor_size, self.config.num_tile_types)
        
        for i, tile in enumerate(floor_tiles):
            if i >= self.config.max_floor_size:
                break
            if tile in [Tile.BLUE, Tile.YELLOW, Tile.RED, Tile.BLACK, Tile.WHITE]:
                encoded[0, i, tile] = 1.0
        
        return encoded.flatten(1)  # [batch_size, max_floor_size * num_tile_types]
    
    def _encode_scores(self, agents: list) -> torch.Tensor:
        """Encode player scores."""
        batch_size = 1
        encoded = torch.zeros(batch_size, 2)  # 2 players
        
        for i, agent in enumerate(agents):
            if i < 2:
                encoded[0, i] = float(agent.score)
        
        return encoded  # [batch_size, 2]


class AzulNet(nn.Module):
    """Small neural network for Azul policy and value prediction."""
    
    def __init__(self, config: AzulNetConfig):
        super().__init__()
        self.config = config
        
        # Calculate input size from encoder
        self._calculate_input_size()
        
        # Shared layers
        self.shared_layers = nn.ModuleList()
        input_size = self.input_size
        
        for i in range(config.num_layers):
            layer = nn.Linear(input_size, config.hidden_size)
            self.shared_layers.append(layer)
            input_size = config.hidden_size
        
        # Policy head (action probabilities)
        self.policy_head = nn.Linear(config.hidden_size, config.num_actions)
        
        # Value head (position evaluation)
        self.value_head = nn.Linear(config.hidden_size, 1)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(config.dropout_rate)
        
        # Initialize weights
        self._init_weights()
    
    def _calculate_input_size(self):
        """Calculate the total input size from the encoder."""
        # Calculate based on actual encoder output
        factory_size = self.config.max_factories * 6 * self.config.num_tile_types  # 9 * 6 * 5 = 270
        center_size = self.config.max_center_tiles * self.config.num_tile_types  # 20 * 5 = 100
        wall_size = self.config.max_wall_size * self.config.max_wall_size  # 5 * 5 = 25
        pattern_size = self.config.max_pattern_lines * self.config.num_tile_types  # 5 * 5 = 25
        floor_size = self.config.max_floor_size * self.config.num_tile_types  # 7 * 5 = 35
        score_size = 2
        
        # Multiply by 2 for both players (wall, pattern, floor)
        self.input_size = (factory_size + center_size + wall_size * 2 + pattern_size * 2 + floor_size * 2 + score_size)
        # = 270 + 100 + 25*2 + 25*2 + 35*2 + 2 = 270 + 100 + 50 + 50 + 70 + 2 = 542
    
    def _init_weights(self):
        """Initialize network weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor of shape [batch_size, input_size]
            
        Returns:
            Tuple of (policy_logits, value)
        """
        # Shared layers
        for layer in self.shared_layers:
            x = F.relu(layer(x))
            x = self.dropout(x)
        
        # Policy head
        policy_logits = self.policy_head(x)
        
        # Value head
        value = torch.tanh(self.value_head(x))
        
        return policy_logits, value
    
    def get_policy_and_value(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get policy probabilities and value.
        
        Args:
            x: Input tensor
            
        Returns:
            Tuple of (policy_probs, value)
        """
        policy_logits, value = self.forward(x)
        policy_probs = F.softmax(policy_logits, dim=-1)
        return policy_probs, value


class AzulNeuralRolloutPolicy:
    """Neural network-based rollout policy for MCTS."""
    
    def __init__(self, model: AzulNet, encoder: AzulTensorEncoder, 
                 evaluator, move_generator, device: str = "cpu"):
        self.model = model
        self.encoder = encoder
        self.evaluator = evaluator
        self.move_generator = move_generator
        self.device = device
        
        # Move model to device
        self.model.to(device)
        self.model.eval()
    
    def rollout(self, state: AzulState, agent_id: int, max_depth: int = 50) -> float:
        """Perform a neural-guided rollout."""
        current_state = state
        current_agent = agent_id
        depth = 0
        
        while depth < max_depth:
            # Check for terminal state
            if self._is_terminal(current_state):
                return self._evaluate_terminal(current_state, agent_id)
            
            # Generate moves
            moves = self.move_generator.generate_moves_fast(current_state, current_agent)
            if not moves:
                return self._evaluate_terminal(current_state, agent_id)
            
            # Use neural network to select move
            move = self._select_neural_move(current_state, moves, current_agent)
            
            # Apply move
            new_state = self._apply_move(current_state, move, current_agent)
            if new_state is None:
                return self._evaluate_terminal(current_state, agent_id)
            
            current_state = new_state
            current_agent = self._get_next_agent(current_agent, current_state)
            depth += 1
        
        # Return neural evaluation if we reached max depth
        return self._evaluate_neural(current_state, agent_id)
    
    def _select_neural_move(self, state: AzulState, moves: list, agent_id: int):
        """Select move using neural network policy."""
        if not moves:
            return None
            
        # Encode state
        state_tensor = self.encoder.encode_state(state, agent_id).to(self.device)
        
        # Get policy probabilities
        with torch.no_grad():
            policy_probs, _ = self.model.get_policy_and_value(state_tensor)
        
        # Use policy mapper to select move from policy
        from neural.policy_mapping import create_policy_mapper, SelectionMethod
        policy_mapper = create_policy_mapper()
        
        # Select move using policy probabilities
        selected_move = policy_mapper.select_move(
            policy_probs, moves, method=SelectionMethod.STOCHASTIC, temperature=1.0
        )
        
        # Get confidence in the selected move
        confidence = policy_mapper.get_move_confidence(policy_probs, selected_move, moves)
        
        # Fallback to heuristic if neural selection fails or confidence is low
        if selected_move is None or policy_mapper.should_use_fallback(confidence):
            selected_move = self._select_best_move_heuristic(moves, state, agent_id)
        
        return selected_move
    
    def _encode_moves_for_policy(self, moves: list, state: AzulState, agent_id: int) -> torch.Tensor:
        """Encode moves for policy mapping (legacy method - now using MoveEncoder)."""
        # This method is kept for backward compatibility
        # The actual encoding is now handled by the MoveEncoder class
        from neural.move_encoding import create_move_encoder
        move_encoder = create_move_encoder()
        
        # Get policy indices for legal moves
        indices = move_encoder.get_legal_move_indices(moves)
        
        # Create encoding tensor
        num_moves = len(moves)
        move_encoding = torch.zeros(num_moves, self.encoder.config.num_actions)
        
        for i, (move, index) in enumerate(zip(moves, indices)):
            if 0 <= index < self.encoder.config.num_actions:
                move_encoding[i, index] = 1.0
        
        return move_encoding
    
    def _select_best_move_heuristic(self, moves: list, state: AzulState, agent_id: int):
        """Select best move using heuristic evaluation."""
        if not moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        for move in moves:
            # Evaluate move using existing evaluator
            score = self._evaluate_move_heuristic(move, state, agent_id)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _evaluate_move_heuristic(self, move, state: AzulState, agent_id: int) -> float:
        """Evaluate a move using heuristic rules."""
        # Simple heuristic: prefer moves that complete patterns
        # This is a placeholder - in practice, you'd use the evaluator
        return 0.0  # Placeholder
    
    def _evaluate_neural(self, state: AzulState, agent_id: int) -> float:
        """Evaluate position using neural network."""
        # Encode state
        state_tensor = self.encoder.encode_state(state, agent_id).to(self.device)
        
        # Get value prediction
        with torch.no_grad():
            _, value = self.model.get_policy_and_value(state_tensor)
        
        return value.item()
    
    def _is_terminal(self, state: AzulState) -> bool:
        """Check if state is terminal."""
        # Simplified terminal check
        return False
    
    def _evaluate_terminal(self, state: AzulState, agent_id: int) -> float:
        """Evaluate terminal state."""
        return self.evaluator.evaluate_position(state, agent_id)
    
    def _apply_move(self, state: AzulState, move, agent_id: int):
        """Apply move to state."""
        # Simplified move application
        # TODO: Implement proper move application
        return state
    
    def _get_next_agent(self, agent_id: int, state: AzulState) -> int:
        """Get next agent ID."""
        return (agent_id + 1) % len(state.agents)


def create_azul_net(config: Optional[AzulNetConfig] = None, 
                    device: str = "cpu") -> Tuple[AzulNet, AzulTensorEncoder]:
    """
    Create an AzulNet model and encoder.
    
    Args:
        config: Model configuration
        device: Device to place model on
        
    Returns:
        Tuple of (model, encoder)
    """
    if config is None:
        config = AzulNetConfig()
    
    encoder = AzulTensorEncoder(config)
    model = AzulNet(config)
    
    return model, encoder


def count_parameters(model: nn.Module) -> int:
    """Count the number of parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad) 