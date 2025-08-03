"""
API Request Models Package

This package contains all Pydantic request models used by the API endpoints.
Models are organized by functional area for better maintainability.
"""

# Import all models for easy access
from .analysis import (
    AnalysisRequest,
    HintRequest,
    AnalysisCacheRequest,
    AnalysisSearchRequest
)

from .position import (
    PositionCacheRequest,
    BulkPositionRequest,
    PositionDatabaseRequest,
    SimilarPositionRequest,
    ContinuationRequest
)

from .neural import (
    NeuralTrainingRequest,
    NeuralEvaluationRequest,
    NeuralConfigRequest
)

from .game import (
    GameCreationRequest,
    GameAnalysisRequest,
    GameLogUploadRequest,
    GameAnalysisSearchRequest,
    MoveExecutionRequest
)

from .validation import (
    BoardValidationRequest,
    PatternDetectionRequest,
    ScoringOptimizationRequest,
    FloorLinePatternRequest
)

from .performance import (
    PerformanceStatsRequest,
    SystemHealthRequest
)

# Export all models
__all__ = [
    # Analysis models
    'AnalysisRequest',
    'HintRequest', 
    'AnalysisCacheRequest',
    'AnalysisSearchRequest',
    
    # Position models
    'PositionCacheRequest',
    'BulkPositionRequest',
    'PositionDatabaseRequest',
    'SimilarPositionRequest',
    'ContinuationRequest',
    
    # Neural models
    'NeuralTrainingRequest',
    'NeuralEvaluationRequest',
    'NeuralConfigRequest',
    
    # Game models
    'GameCreationRequest',
    'GameAnalysisRequest',
    'GameLogUploadRequest',
    'GameAnalysisSearchRequest',
    'MoveExecutionRequest',
    
    # Validation models
    'BoardValidationRequest',
    'PatternDetectionRequest',
    'ScoringOptimizationRequest',
    'FloorLinePatternRequest',
    
    # Performance models
    'PerformanceStatsRequest',
    'SystemHealthRequest',
] 