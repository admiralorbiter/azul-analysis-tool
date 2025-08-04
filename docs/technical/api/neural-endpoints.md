# Neural API Endpoints

## Overview

The Neural API provides endpoints for training, evaluating, and integrating neural models for Azul game analysis. This includes training management, model evaluation, and integration with game analysis tools.

## Base URL

```
/api/v1/neural
```

## Authentication

All neural endpoints require authentication. Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### System Status

#### Get Neural System Status

**Endpoint:** `GET /api/v1/neural/status`

**Description:** Get the current status of the neural training system and PyTorch availability.

**Response:**
```json
{
    "pytorch_available": true,
    "cuda_available": false,
    "models_directory": "/path/to/models",
    "active_sessions": 2,
    "total_sessions": 15,
    "system_status": "ready"
}
```

### Model Management

#### List Available Models

**Endpoint:** `GET /api/v1/neural/models`

**Description:** Get a list of available trained neural models.

**Query Parameters:**
- `architecture` (optional): Filter by model architecture (small, medium, large)
- `include_metadata` (optional): Include model metadata (default: true)

**Response:**
```json
{
    "models": [
        {
            "filename": "azul_net_medium.pth",
            "architecture": "medium",
            "file_size": 20485760,
            "parameters": 5000000,
            "training_date": "2024-01-15T10:30:00Z",
            "metadata": {
                "win_rate": 0.75,
                "accuracy": 0.82,
                "training_epochs": 100
            }
        }
    ],
    "total_models": 3
}
```

### Training Configuration

#### Get Training Configuration

**Endpoint:** `GET /api/v1/neural/config`

**Description:** Get the current training configuration.

**Response:**
```json
{
    "model_size": "medium",
    "device": "cpu",
    "epochs": 100,
    "samples": 1000,
    "learning_rate": 0.001,
    "batch_size": 32,
    "save_interval": 10,
    "validation_split": 0.2
}
```

#### Save Training Configuration

**Endpoint:** `POST /api/v1/neural/config`

**Description:** Save a new training configuration.

**Request Body:**
```json
{
    "model_size": "medium",
    "device": "cpu",
    "epochs": 100,
    "samples": 1000,
    "learning_rate": 0.001,
    "batch_size": 32,
    "save_interval": 10,
    "validation_split": 0.2
}
```

**Response:**
```json
{
    "success": true,
    "message": "Configuration saved successfully",
    "config_id": "config_123"
}
```

### Training Sessions

#### Start Training

**Endpoint:** `POST /api/v1/neural/train`

**Description:** Start a new neural training session.

**Request Body:**
```json
{
    "model_size": "medium",
    "device": "cpu",
    "epochs": 100,
    "samples": 1000,
    "learning_rate": 0.001,
    "batch_size": 32,
    "save_interval": 10,
    "validation_split": 0.2
}
```

**Response:**
```json
{
    "session_id": "train_123",
    "status": "started",
    "message": "Training session started successfully",
    "estimated_duration": 3600
}
```

#### Get Training Status

**Endpoint:** `GET /api/v1/neural/status/{session_id}`

**Description:** Get the status of a specific training session.

**Response:**
```json
{
    "session_id": "train_123",
    "status": "running",
    "progress": 0.45,
    "current_epoch": 45,
    "total_epochs": 100,
    "loss_history": [0.85, 0.72, 0.68, 0.65],
    "validation_loss": 0.62,
    "elapsed_time": 1620,
    "estimated_remaining": 1980,
    "resource_usage": {
        "cpu_percent": 85.2,
        "memory_percent": 45.8
    }
}
```

#### Stop Training

**Endpoint:** `POST /api/v1/neural/stop/{session_id}`

**Description:** Stop a running training session.

**Response:**
```json
{
    "session_id": "train_123",
    "status": "stopped",
    "message": "Training session stopped successfully"
}
```

#### List Training Sessions

**Endpoint:** `GET /api/v1/neural/sessions`

**Description:** Get a list of all training sessions.

**Query Parameters:**
- `status` (optional): Filter by status (running, completed, failed)
- `limit` (optional): Maximum number of sessions to return (default: 50)
- `offset` (optional): Number of sessions to skip (default: 0)

**Response:**
```json
{
    "sessions": [
        {
            "session_id": "train_123",
            "status": "completed",
            "model_size": "medium",
            "device": "cpu",
            "epochs": 100,
            "progress": 1.0,
            "created_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T11:30:00Z",
            "final_loss": 0.45
        }
    ],
    "total_sessions": 15
}
```

#### Delete Training Session

**Endpoint:** `DELETE /api/v1/neural/sessions/{session_id}`

**Description:** Delete a training session and its associated data.

**Response:**
```json
{
    "session_id": "train_123",
    "status": "deleted",
    "message": "Training session deleted successfully"
}
```

### Model Evaluation

#### Start Model Evaluation

**Endpoint:** `POST /api/v1/neural/evaluate`

**Description:** Start a model evaluation session.

**Request Body:**
```json
{
    "model": "azul_net_medium.pth",
    "test_positions": 100,
    "games": 10,
    "search_time": 1.0,
    "rollouts": 100,
    "include_accuracy": true,
    "include_inference_time": true
}
```

**Response:**
```json
{
    "session_id": "eval_456",
    "status": "started",
    "message": "Evaluation session started successfully",
    "estimated_duration": 1800
}
```

#### Get Evaluation Status

**Endpoint:** `GET /api/v1/neural/evaluate/status/{session_id}`

**Description:** Get the status of a model evaluation session.

**Response:**
```json
{
    "session_id": "eval_456",
    "status": "running",
    "progress": 0.35,
    "positions_evaluated": 35,
    "total_positions": 100,
    "current_results": {
        "win_rate": 0.72,
        "accuracy": 0.78,
        "inference_time": 0.045
    },
    "elapsed_time": 630,
    "estimated_remaining": 1170
}
```

#### List Evaluation Sessions

**Endpoint:** `GET /api/v1/neural/evaluation-sessions`

**Description:** Get a list of all evaluation sessions.

**Query Parameters:**
- `status` (optional): Filter by status (running, completed, failed)
- `limit` (optional): Maximum number of sessions to return (default: 50)
- `offset` (optional): Number of sessions to skip (default: 0)

**Response:**
```json
{
    "sessions": [
        {
            "session_id": "eval_456",
            "status": "completed",
            "model": "azul_net_medium.pth",
            "test_positions": 100,
            "games": 10,
            "created_at": "2024-01-15T12:00:00Z",
            "completed_at": "2024-01-15T12:30:00Z",
            "results": {
                "win_rate": 0.75,
                "accuracy": 0.82,
                "inference_time": 0.045
            }
        }
    ],
    "total_sessions": 8
}
```

#### Delete Evaluation Session

**Endpoint:** `DELETE /api/v1/neural/evaluation-sessions/{session_id}`

**Description:** Delete an evaluation session and its results.

**Response:**
```json
{
    "session_id": "eval_456",
    "status": "deleted",
    "message": "Evaluation session deleted successfully"
}
```

### Training History

#### Get Training History

**Endpoint:** `GET /api/v1/neural/history`

**Description:** Get training session history with advanced filtering.

**Query Parameters:**
- `status` (optional): Filter by status (running, completed, failed)
- `device` (optional): Filter by device (cpu, cuda)
- `model_size` (optional): Filter by model size (small, medium, large)
- `date_from` (optional): Filter by start date (ISO format)
- `date_to` (optional): Filter by end date (ISO format)
- `sort_by` (optional): Sort field (created_at, progress, status)
- `sort_order` (optional): Sort order (asc, desc)
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Number to skip (default: 0)

**Response:**
```json
{
    "sessions": [
        {
            "session_id": "train_123",
            "status": "completed",
            "model_size": "medium",
            "device": "cpu",
            "epochs": 100,
            "progress": 1.0,
            "created_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T11:30:00Z",
            "final_loss": 0.45,
            "metadata": {
                "win_rate": 0.75,
                "accuracy": 0.82
            }
        }
    ],
    "total_sessions": 15,
    "filtered_count": 8
}
```

### Configuration Management

#### List Saved Configurations

**Endpoint:** `GET /api/v1/neural/configurations`

**Description:** Get a list of saved training configurations.

**Response:**
```json
{
    "configurations": [
        {
            "config_id": "config_123",
            "name": "Medium Model Training",
            "model_size": "medium",
            "device": "cpu",
            "epochs": 100,
            "samples": 1000,
            "learning_rate": 0.001,
            "batch_size": 32,
            "created_at": "2024-01-15T10:00:00Z"
        }
    ],
    "total_configurations": 5
}
```

#### Save Configuration Template

**Endpoint:** `POST /api/v1/neural/configurations`

**Description:** Save a new training configuration template.

**Request Body:**
```json
{
    "name": "Large Model Training",
    "model_size": "large",
    "device": "cuda",
    "epochs": 200,
    "samples": 5000,
    "learning_rate": 0.0005,
    "batch_size": 64,
    "save_interval": 20,
    "validation_split": 0.2
}
```

**Response:**
```json
{
    "config_id": "config_124",
    "success": true,
    "message": "Configuration template saved successfully"
}
```

#### Update Configuration Template

**Endpoint:** `PUT /api/v1/neural/configurations/{config_id}`

**Description:** Update an existing configuration template.

**Request Body:**
```json
{
    "name": "Updated Large Model Training",
    "model_size": "large",
    "device": "cuda",
    "epochs": 250,
    "samples": 6000,
    "learning_rate": 0.0004,
    "batch_size": 64
}
```

**Response:**
```json
{
    "config_id": "config_124",
    "success": true,
    "message": "Configuration template updated successfully"
}
```

#### Delete Configuration Template

**Endpoint:** `DELETE /api/v1/neural/configurations/{config_id}`

**Description:** Delete a configuration template.

**Response:**
```json
{
    "config_id": "config_124",
    "success": true,
    "message": "Configuration template deleted successfully"
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
    "error": "Invalid training configuration",
    "details": "Epochs must be between 1 and 1000"
}
```

#### 404 Not Found

```json
{
    "error": "Training session not found",
    "details": "Session train_999 does not exist"
}
```

#### 422 Unprocessable Entity

```json
{
    "error": "Model evaluation failed",
    "details": "Model file azul_net_invalid.pth not found"
}
```

#### 500 Internal Server Error

```json
{
    "error": "Training failed",
    "details": "PyTorch CUDA error: out of memory"
}
```

## Rate Limiting

Neural API endpoints are subject to rate limiting:

- **Training endpoints**: 5 requests per minute
- **Evaluation endpoints**: 10 requests per minute
- **Status endpoints**: 30 requests per minute
- **Configuration endpoints**: 20 requests per minute

## Performance Considerations

### Training Performance

- **CPU Training**: ~100-500 epochs per hour depending on model size
- **GPU Training**: ~500-2000 epochs per hour with CUDA
- **Memory Usage**: 2-8GB RAM depending on model size and batch size
- **Storage**: Model files range from 4MB (small) to 80MB (large)

### Evaluation Performance

- **Single Model**: ~100 positions per minute
- **Batch Evaluation**: ~50 positions per minute per model
- **Memory Usage**: 1-4GB RAM depending on model size
- **Storage**: Evaluation results ~1-10MB per session

## Related Documentation

- [Neural Training Guide](../../guides/neural/training.md) - User guide for training
- [Neural Evaluation Guide](../../guides/neural/evaluation.md) - User guide for evaluation
- [Neural Integration Guide](../../guides/neural/integration.md) - User guide for integration
- [Technical Implementation](../../implementation/neural-training.md) - Technical details 