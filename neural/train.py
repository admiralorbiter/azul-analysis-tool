"""
Training script for AzulNet.

This module provides:
- Synthetic data generation for training
- Training loop for AzulNet
- Model saving and loading
- Performance evaluation
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
import time
import os

from .azul_net import AzulNet, AzulNetConfig, AzulTensorEncoder, create_azul_net
from ..core.azul_model import AzulState
from ..core.azul_evaluator import AzulEvaluator
from ..core.azul_move_generator import FastMoveGenerator


@dataclass
class TrainingConfig:
    """Configuration for training."""
    # Training parameters
    batch_size: int = 32
    learning_rate: float = 0.001
    num_epochs: int = 10
    num_samples: int = 1000
    
    # Model parameters
    hidden_size: int = 128
    num_layers: int = 3
    dropout_rate: float = 0.1
    
    # Data generation
    max_depth: int = 10
    min_score: float = -50.0
    max_score: float = 50.0
    
    # Device
    device: str = "cpu"


class SyntheticDataGenerator:
    """Generate synthetic training data for AzulNet."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.evaluator = AzulEvaluator()
        self.move_generator = FastMoveGenerator()
        self.encoder = AzulTensorEncoder(AzulNetConfig(
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            dropout_rate=config.dropout_rate
        ))
    
    def generate_training_data(self) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Generate synthetic training data.
        
        Returns:
            Tuple of (states, policy_targets, value_targets)
        """
        states = []
        policy_targets = []
        value_targets = []
        
        print(f"Generating {self.config.num_samples} training samples...")
        
        for i in range(self.config.num_samples):
            if i % 100 == 0:
                print(f"Generated {i}/{self.config.num_samples} samples")
            
            # Generate random state
            state = self._generate_random_state()
            
            # Encode state
            state_tensor = self.encoder.encode_state(state, agent_id=0)
            
            # Generate policy target (simplified - uniform distribution)
            policy_target = self._generate_policy_target(state)
            
            # Generate value target using evaluator
            value_target = self._generate_value_target(state)
            
            states.append(state_tensor)
            policy_targets.append(policy_target)
            value_targets.append(value_target)
        
        # Stack tensors
        states_tensor = torch.cat(states, dim=0)
        policy_tensor = torch.stack(policy_targets, dim=0)
        value_tensor = torch.stack(value_targets, dim=0)
        
        print(f"Generated training data: {states_tensor.shape}, {policy_tensor.shape}, {value_tensor.shape}")
        
        return states_tensor, policy_tensor, value_tensor
    
    def _generate_random_state(self) -> AzulState:
        """Generate a random Azul state."""
        state = AzulState(2)
        
        # Randomly populate factories
        for i in range(len(state.factories)):
            for j in range(6):
                if random.random() < 0.3:  # 30% chance of tile
                    tile_type = random.randint(0, 4)  # 0-4 for tile types
                    state.factories[i][j] = tile_type
        
        # Randomly populate center
        num_center_tiles = random.randint(0, 10)
        state.center = []
        for _ in range(num_center_tiles):
            tile_type = random.randint(0, 4)
            state.center.append(tile_type)
        
        # Randomly populate player boards
        for agent_id in range(2):
            agent = state.agents[agent_id]
            
            # Random wall
            for i in range(5):
                for j in range(5):
                    if random.random() < 0.2:  # 20% chance of tile
                        agent.wall[i][j] = True
            
            # Random pattern lines
            for i in range(5):
                num_tiles = random.randint(0, i + 1)
                for j in range(num_tiles):
                    tile_type = random.randint(0, 4)
                    agent.pattern_lines[i][j] = tile_type
            
            # Random floor line
            num_floor_tiles = random.randint(0, 7)
            for j in range(num_floor_tiles):
                tile_type = random.randint(0, 4)
                agent.floor_line[j] = tile_type
            
            # Random score
            agent.score = random.randint(-20, 50)
        
        return state
    
    def _generate_policy_target(self, state: AzulState) -> torch.Tensor:
        """Generate policy target (simplified)."""
        # For now, use uniform distribution
        # TODO: Implement proper policy generation based on move quality
        num_actions = 100  # Match model output size
        policy = torch.ones(num_actions) / num_actions
        return policy
    
    def _generate_value_target(self, state: AzulState) -> torch.Tensor:
        """Generate value target using evaluator."""
        # Use evaluator to get position value
        value = self.evaluator.evaluate_position(state, agent_id=0)
        
        # Normalize to [-1, 1] range
        normalized_value = np.tanh(value / 50.0)  # Scale by 50
        
        return torch.tensor([normalized_value], dtype=torch.float32)


class AzulNetTrainer:
    """Trainer for AzulNet."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Create model and move to device
        self.model, self.encoder = create_azul_net(
            AzulNetConfig(
                hidden_size=config.hidden_size,
                num_layers=config.num_layers,
                dropout_rate=config.dropout_rate
            ),
            device=config.device
        )
        
        # Setup optimizer and loss functions
        self.optimizer = optim.Adam(self.model.parameters(), lr=config.learning_rate)
        self.policy_loss_fn = nn.CrossEntropyLoss()
        self.value_loss_fn = nn.MSELoss()
        
        # Data generator
        self.data_generator = SyntheticDataGenerator(config)
    
    def train(self) -> List[float]:
        """
        Train the model.
        
        Returns:
            List of training losses
        """
        print(f"Starting training on {self.device}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters())}")
        
        # Generate training data
        states, policy_targets, value_targets = self.data_generator.generate_training_data()
        
        # Move data to device
        states = states.to(self.device)
        policy_targets = policy_targets.to(self.device)
        value_targets = value_targets.to(self.device)
        
        losses = []
        
        for epoch in range(self.config.num_epochs):
            epoch_loss = self._train_epoch(states, policy_targets, value_targets)
            losses.append(epoch_loss)
            
            print(f"Epoch {epoch + 1}/{self.config.num_epochs}, Loss: {epoch_loss:.4f}")
        
        return losses
    
    def _train_epoch(self, states: torch.Tensor, policy_targets: torch.Tensor, 
                     value_targets: torch.Tensor) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        # Create batches
        dataset_size = len(states)
        indices = torch.randperm(dataset_size)
        
        for i in range(0, dataset_size, self.config.batch_size):
            batch_indices = indices[i:i + self.config.batch_size]
            
            batch_states = states[batch_indices]
            batch_policy_targets = policy_targets[batch_indices]
            batch_value_targets = value_targets[batch_indices]
            
            # Forward pass
            policy_logits, value_pred = self.model(batch_states)
            
            # Calculate losses
            policy_loss = self.policy_loss_fn(policy_logits, batch_policy_targets.argmax(dim=1))
            value_loss = self.value_loss_fn(value_pred.squeeze(), batch_value_targets.squeeze())
            
            total_loss_batch = policy_loss + value_loss
            
            # Backward pass
            self.optimizer.zero_grad()
            total_loss_batch.backward()
            self.optimizer.step()
            
            total_loss += total_loss_batch.item()
            num_batches += 1
        
        return total_loss / num_batches
    
    def evaluate(self, num_samples: int = 100) -> dict:
        """Evaluate the trained model."""
        self.model.eval()
        
        evaluator = AzulEvaluator()
        total_error = 0.0
        num_evaluations = 0
        
        with torch.no_grad():
            for _ in range(num_samples):
                # Generate random state
                state = self.data_generator._generate_random_state()
                
                # Get neural prediction
                state_tensor = self.encoder.encode_state(state, agent_id=0).to(self.device)
                _, value_pred = self.model.get_policy_and_value(state_tensor)
                neural_value = value_pred.item()
                
                # Get evaluator prediction
                evaluator_value = evaluator.evaluate_position(state, agent_id=0)
                evaluator_value_normalized = np.tanh(evaluator_value / 50.0)
                
                # Calculate error
                error = abs(neural_value - evaluator_value_normalized)
                total_error += error
                num_evaluations += 1
        
        avg_error = total_error / num_evaluations
        
        return {
            'avg_value_error': avg_error,
            'num_evaluations': num_evaluations
        }
    
    def save_model(self, path: str):
        """Save the trained model."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'encoder_config': self.encoder.config
        }, path)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a trained model."""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Model loaded from {path}")


def main():
    """Main training function."""
    # Configuration
    config = TrainingConfig(
        batch_size=16,
        learning_rate=0.001,
        num_epochs=5,
        num_samples=500,
        hidden_size=64,
        num_layers=2,
        device="cpu"
    )
    
    # Create trainer
    trainer = AzulNetTrainer(config)
    
    # Train model
    print("Starting training...")
    losses = trainer.train()
    
    # Evaluate model
    print("Evaluating model...")
    eval_results = trainer.evaluate(num_samples=50)
    print(f"Evaluation results: {eval_results}")
    
    # Save model
    trainer.save_model("models/azul_net_v1.pth")
    
    print("Training complete!")


if __name__ == "__main__":
    main() 