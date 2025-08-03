"""
Neural training-related request models for the API.

This module contains Pydantic models for neural network training endpoints including
training configuration, evaluation, and model management.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class NeuralTrainingRequest(BaseModel):
    """Request model for neural training."""
    config: str = 'small'  # 'small', 'medium', 'large'
    modelSize: Optional[str] = None  # Frontend sends this field name
    device: str = 'cpu'  # 'cpu', 'cuda'
    epochs: int = 5
    samples: int = 500
    batch_size: int = 16
    learning_rate: float = 0.001
    
    def __init__(self, **data):
        super().__init__(**data)
        # Handle field name mismatch between frontend and backend
        if self.modelSize and not data.get('config'):
            self.config = self.modelSize


class NeuralEvaluationRequest(BaseModel):
    """Request model for neural evaluation."""
    model: str = 'models/azul_net_small.pth'
    positions: int = 50
    games: int = 20
    device: str = 'cpu'


class NeuralConfigRequest(BaseModel):
    """Request model for neural configuration."""
    config: Optional[str] = None
    device: Optional[str] = None
    epochs: Optional[int] = None
    samples: Optional[int] = None
    batch_size: Optional[int] = None
    learning_rate: Optional[float] = None 