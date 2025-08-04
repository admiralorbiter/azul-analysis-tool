# Neural Training Guide

## Overview

The Neural Training system allows you to train machine learning models to analyze Azul game positions and make strategic decisions. This guide covers how to configure, start, and monitor neural training sessions.

## Getting Started

### Prerequisites

- **PyTorch**: Neural training requires PyTorch to be installed
- **GPU Support**: Optional but recommended for faster training
- **Database**: Training sessions are stored in the local SQLite database

### Accessing Neural Training

1. **Navigate to Neural Training**: Click "🧠 Neural Training" in the main navigation
2. **Training Interface**: You'll see the dedicated neural training page with multiple tabs

## Training Configuration

### Model Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| **Model Size** | Neural network architecture size | Small | Small, Medium, Large |
| **Device** | Training device (CPU/GPU) | CPU | CPU, CUDA |
| **Epochs** | Number of training epochs | 100 | 1-1000 |
| **Samples** | Training samples per epoch | 1000 | 100-10000 |
| **Learning Rate** | Training learning rate | 0.001 | 0.0001-0.01 |
| **Batch Size** | Training batch size | 32 | 8-128 |

### Configuration Options

#### Model Size Options

- **Small**: Fast training, lower accuracy (~1M parameters)
- **Medium**: Balanced performance (~5M parameters) 
- **Large**: High accuracy, slower training (~20M parameters)

#### Device Selection

- **CPU**: Universal compatibility, slower training
- **CUDA**: GPU acceleration, much faster training (requires NVIDIA GPU)

### Saving Configurations

1. **Configure Parameters**: Set your desired training parameters
2. **Save Configuration**: Click "💾 Save Configuration" to persist settings
3. **Load Configurations**: Use saved configurations for consistent training

## Starting Training

### Basic Training Workflow

1. **Configure Training**: Set model size, device, epochs, and other parameters
2. **Start Training**: Click the prominent "🚀 Start Training" button
3. **Monitor Progress**: Switch to "Training Monitor" tab for live updates
4. **View Results**: Check training history and model evaluation

### Training Session Management

#### Starting a New Session

```javascript
// Example API call
const response = await fetch('/api/v1/neural/train', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        model_size: 'medium',
        device: 'cpu',
        epochs: 100,
        samples: 1000,
        learning_rate: 0.001,
        batch_size: 32
    })
});
```

#### Monitoring Active Sessions

- **Real-time Status**: View current training progress
- **Loss Visualization**: See training loss over epochs
- **Resource Usage**: Monitor CPU and memory consumption
- **Time Estimation**: View ETA for training completion

## Training Monitor

### Live Visualization

The Training Monitor tab provides real-time insights into your training session:

#### Loss Curve Display

- **Real-time Updates**: Loss values update as training progresses
- **Epoch Tracking**: See loss progression over training epochs
- **Trend Analysis**: Identify overfitting or convergence issues

#### Resource Monitoring

- **CPU Usage**: Real-time CPU utilization with progress bar
- **Memory Usage**: Current memory consumption and trends
- **Performance Metrics**: Training speed and efficiency indicators

### Session Management

#### Active Sessions

- **Session List**: View all active training sessions
- **Stop Training**: Gracefully stop running sessions
- **Session Details**: View detailed configuration and progress

#### Historical Sessions

- **Training History**: Browse completed training sessions
- **Session Details**: View logs, results, and configuration
- **Session Deletion**: Remove old sessions to free space

## Training History

### Viewing Historical Data

1. **Navigate to History**: Click "Training History" tab
2. **Filter Sessions**: Use status, device, and date filters
3. **Sort Results**: Sort by creation date, progress, or status
4. **View Details**: Click on sessions for detailed information

### Advanced Filtering

| Filter | Options | Description |
|--------|---------|-------------|
| **Status** | Running, Completed, Failed | Filter by training status |
| **Device** | CPU, CUDA | Filter by training device |
| **Model Size** | Small, Medium, Large | Filter by model architecture |
| **Date Range** | Custom range | Filter by creation date |

### Session Details

Each training session includes:

- **Configuration**: Complete training parameters
- **Progress**: Training progress and duration
- **Results**: Final model performance metrics
- **Logs**: Detailed training logs and errors

## Configuration Management

### Saved Configurations

#### Creating Templates

1. **Configure Parameters**: Set up your desired training configuration
2. **Save Template**: Click "Save Configuration" with a descriptive name
3. **Reuse**: Load saved configurations for consistent training

#### Managing Templates

- **Edit Configurations**: Modify saved training templates
- **Delete Templates**: Remove unused configurations
- **Share Configurations**: Export/import configuration files

### Configuration Best Practices

#### For Beginners

- **Start Small**: Use small model size for initial experiments
- **CPU Training**: Begin with CPU to avoid GPU setup issues
- **Few Epochs**: Start with 10-50 epochs to test setup
- **Small Samples**: Use 100-500 samples for quick testing

#### For Advanced Users

- **GPU Training**: Use CUDA for faster training on large datasets
- **Large Models**: Use large model size for best accuracy
- **Many Epochs**: Train for 200+ epochs for convergence
- **Large Datasets**: Use 5000+ samples for robust training

## Troubleshooting

### Common Issues

#### Training Won't Start

**Problem**: "🚀 Start Training" button doesn't respond
**Solutions**:
- Check PyTorch installation: `python -c "import torch; print(torch.__version__)"`
- Verify database connection
- Check console for error messages

#### Slow Training

**Problem**: Training is very slow
**Solutions**:
- Switch to GPU if available
- Reduce model size or batch size
- Check CPU/memory usage in monitor

#### Training Fails

**Problem**: Training session fails with errors
**Solutions**:
- Check training logs in session details
- Reduce batch size or learning rate
- Verify sufficient disk space for model files

#### Memory Issues

**Problem**: Out of memory errors
**Solutions**:
- Reduce batch size
- Use smaller model size
- Switch to CPU training
- Close other applications

### Performance Optimization

#### For Faster Training

1. **Use GPU**: Switch to CUDA device if available
2. **Increase Batch Size**: Larger batches train faster (if memory allows)
3. **Reduce Model Size**: Smaller models train faster
4. **Optimize Data**: Use efficient data loading

#### For Better Accuracy

1. **Use Large Model**: Larger models generally achieve better accuracy
2. **Train Longer**: More epochs often improve performance
3. **More Data**: Increase samples per epoch
4. **Fine-tune Learning Rate**: Experiment with different learning rates

## Related Documentation

- [Neural Evaluation Guide](evaluation.md) - How to evaluate trained models
- [Neural Integration Guide](integration.md) - Using neural models in analysis
- [API Reference](../../technical/api/neural-endpoints.md) - Complete API documentation
- [Technical Implementation](../../technical/implementation/neural-training.md) - Technical details 