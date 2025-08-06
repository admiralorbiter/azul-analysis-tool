# Neural Model Evaluation Guide

## Overview

The Neural Model Evaluation system allows you to test trained neural models against various game positions and compare their performance. This guide covers how to evaluate models, interpret results, and compare different model architectures.

## Getting Started

### Prerequisites

- **Trained Models**: At least one trained neural model available
- **Test Positions**: Game positions for evaluation
- **Evaluation Interface**: Access to the Model Evaluation tab

### Accessing Model Evaluation

1. **Navigate to Neural Training**: Click "🧠 Neural Training" in the main navigation
2. **Model Evaluation Tab**: Click the "Model Evaluation" tab
3. **Evaluation Interface**: You'll see the model evaluation interface

## Model Selection

### Available Models

The system automatically detects trained models in the `models/` directory:

#### Model Information Displayed

- **Model Name**: File name of the trained model
- **Model Size**: Small, Medium, or Large architecture
- **File Size**: Size of the model file on disk
- **Training Date**: When the model was trained
- **Architecture**: Neural network architecture details

#### Model Types

| Model Size | Parameters | File Size | Use Case |
|------------|------------|-----------|----------|
| **Small** | ~1M | ~4MB | Quick testing, basic analysis |
| **Medium** | ~5M | ~20MB | Balanced performance |
| **Large** | ~20M | ~80MB | High accuracy, detailed analysis |

### Selecting Models for Evaluation

1. **Single Model**: Select one model for individual evaluation
2. **Multiple Models**: Select multiple models for comparison
3. **Model Details**: View model metadata and training information

## Evaluation Configuration

### Test Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| **Test Positions** | Number of positions to test | 100 | 10-1000 |
| **Games** | Number of games per position | 10 | 1-100 |
| **Search Time** | Time per move (seconds) | 1.0 | 0.1-10.0 |
| **Rollouts** | Monte Carlo rollouts | 100 | 10-1000 |

### Evaluation Settings

#### Test Position Types

- **Random Positions**: Randomly generated game states
- **Strategic Positions**: Positions with known strategic elements
- **Endgame Positions**: Late-game scenarios
- **Custom Positions**: User-defined test positions

#### Evaluation Metrics

- **Win Rate**: Percentage of games won
- **Accuracy**: Move prediction accuracy
- **Inference Time**: Time per move prediction
- **Parameter Count**: Model complexity

## Running Evaluations

### Single Model Evaluation

#### Basic Evaluation Workflow

1. **Select Model**: Choose a model from the dropdown
2. **Configure Parameters**: Set test positions, games, search time
3. **Start Evaluation**: Click "🚀 Start Evaluation"
4. **Monitor Progress**: Watch real-time progress updates
5. **View Results**: See detailed evaluation results

#### Evaluation Progress

- **Real-time Updates**: Progress bar and status updates
- **Time Estimation**: ETA for evaluation completion
- **Resource Usage**: CPU and memory consumption
- **Intermediate Results**: Partial results as evaluation progresses

### Batch Model Comparison

#### Comparing Multiple Models

1. **Select Models**: Choose multiple models for comparison
2. **Configure Evaluation**: Set evaluation parameters
3. **Start Comparison**: Click "📊 Compare Models"
4. **Monitor Progress**: Track evaluation of all models
5. **View Comparison**: See side-by-side results

#### Comparison Metrics

| Metric | Description | Importance |
|--------|-------------|------------|
| **Win Rate** | Percentage of games won | High |
| **Accuracy** | Move prediction accuracy | High |
| **Inference Time** | Speed of predictions | Medium |
| **Parameter Count** | Model complexity | Low |

## Understanding Results

### Performance Metrics

#### Win Rate Analysis

- **High Win Rate (>70%)**: Model performs well
- **Medium Win Rate (50-70%)**: Model has room for improvement
- **Low Win Rate (<50%)**: Model needs retraining

#### Accuracy Metrics

- **Move Agreement**: How often model agrees with expert moves
- **Position Accuracy**: Accuracy on specific position types
- **Strategic Accuracy**: Performance on strategic decisions

#### Speed Metrics

- **Inference Time**: Time per move prediction
- **Throughput**: Moves per second
- **Resource Usage**: CPU/memory consumption

### Result Interpretation

#### Good Performance Indicators

- **High Win Rate**: Model wins most games
- **Fast Inference**: Quick move predictions
- **Consistent Results**: Stable performance across positions
- **Low Resource Usage**: Efficient computation

#### Areas for Improvement

- **Low Win Rate**: Consider retraining with more data
- **Slow Inference**: Use smaller model or optimize
- **Inconsistent Results**: Check training data quality
- **High Resource Usage**: Optimize model architecture

## Advanced Evaluation

### Custom Test Positions

#### Creating Test Positions

1. **Position Editor**: Use the position editor to create custom positions
2. **Strategic Scenarios**: Design positions with specific strategic elements
3. **Save Positions**: Save positions for repeated evaluation
4. **Import Positions**: Import positions from external sources

#### Position Categories

- **Opening Positions**: Early game scenarios
- **Midgame Positions**: Strategic decision points
- **Endgame Positions**: Late game scenarios
- **Tactical Positions**: Specific tactical opportunities

### Evaluation Sessions

#### Session Management

- **Active Sessions**: View currently running evaluations
- **Session History**: Browse completed evaluations
- **Session Details**: View detailed results and configuration
- **Session Deletion**: Remove old evaluation sessions

#### Session Information

Each evaluation session includes:

- **Configuration**: Complete evaluation parameters
- **Progress**: Evaluation progress and duration
- **Results**: Performance metrics and analysis
- **Logs**: Detailed evaluation logs

## Exporting Results

### Result Formats

#### JSON Export

```json
{
    "evaluation_id": "eval_123",
    "timestamp": "2024-01-15T10:30:00Z",
    "model": "azul_net_medium.pth",
    "configuration": {
        "test_positions": 100,
        "games": 10,
        "search_time": 1.0
    },
    "results": {
        "win_rate": 0.75,
        "accuracy": 0.82,
        "inference_time": 0.045
    }
}
```

#### CSV Export

- **Summary Results**: High-level performance metrics
- **Detailed Results**: Position-by-position analysis
- **Comparison Results**: Side-by-side model comparison

### Export Options

1. **Download Results**: Export evaluation results as JSON
2. **Save Comparison**: Save model comparison data
3. **Share Results**: Share evaluation results with others
4. **Archive Results**: Store results for future reference

## Troubleshooting

### Common Issues

#### Evaluation Won't Start

**Problem**: "🚀 Start Evaluation" button doesn't respond
**Solutions**:
- Check model file exists and is valid
- Verify PyTorch installation
- Check console for error messages

#### Slow Evaluation

**Problem**: Evaluation is very slow
**Solutions**:
- Reduce number of test positions
- Decrease search time per move
- Use smaller model for faster inference
- Check CPU/memory usage

#### Memory Issues

**Problem**: Out of memory during evaluation
**Solutions**:
- Reduce batch size
- Use smaller model
- Close other applications
- Reduce number of concurrent evaluations

#### Inconsistent Results

**Problem**: Results vary significantly between runs
**Solutions**:
- Increase number of games per position
- Use more test positions
- Check for random seed issues
- Verify model stability

### Performance Optimization

#### For Faster Evaluation

1. **Reduce Test Positions**: Use fewer positions for quick testing
2. **Decrease Search Time**: Lower time per move
3. **Use Smaller Models**: Faster inference with smaller models
4. **Optimize Hardware**: Use GPU if available

#### For More Accurate Results

1. **Increase Test Positions**: More positions for better statistics
2. **More Games**: Higher number of games per position
3. **Longer Search Time**: More time for move analysis
4. **Use Larger Models**: Better accuracy with larger models

## Best Practices

### Evaluation Strategy

#### For Model Development

1. **Quick Testing**: Use small models and few positions for rapid iteration
2. **Comprehensive Testing**: Use large models and many positions for final validation
3. **A/B Testing**: Compare model versions systematically
4. **Regression Testing**: Ensure new models don't regress performance

#### For Production Models

1. **Thorough Evaluation**: Comprehensive testing across position types
2. **Performance Monitoring**: Track inference time and resource usage
3. **Regular Re-evaluation**: Periodically re-evaluate models
4. **Documentation**: Keep detailed evaluation records

### Result Analysis

#### Interpreting Win Rates

- **>80%**: Excellent performance
- **60-80%**: Good performance
- **40-60%**: Acceptable performance
- **<40%**: Needs improvement

#### Interpreting Accuracy

- **>90%**: Very accurate predictions
- **70-90%**: Good accuracy
- **50-70%**: Acceptable accuracy
- **<50%**: Needs improvement

## Related Documentation

- [Neural Training Guide](training.md) - How to train neural models
- [Neural Integration Guide](integration.md) - Using neural models in analysis
- [API Reference](../../technical/api/neural-endpoints.md) - Complete API documentation
- [Technical Implementation](../../technical/implementation/neural-evaluation.md) - Technical details 