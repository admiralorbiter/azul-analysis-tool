# Neural Evaluation Implementation

## Overview

This document describes the technical implementation of the neural model evaluation system. The system provides comprehensive evaluation of trained neural models against various test positions and comparison with other analysis methods.

## Architecture

### Core Components

#### Evaluation Engine

The evaluation system consists of several key components:

```python
class NeuralEvaluator:
    def __init__(self, model_path, device='cpu'):
        self.model = self.load_model(model_path)
        self.device = device
        self.model.to(device)
        self.model.eval()
        
    def load_model(self, model_path):
        """Load trained neural model"""
        model = AzulNet()
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        return model
    
    def evaluate_position(self, game_state):
        """Evaluate a single position"""
        with torch.no_grad():
            state_tensor = self.preprocess_state(game_state)
            policy_pred, value_pred = self.model(state_tensor)
            return {
                'policy': policy_pred.cpu().numpy(),
                'value': value_pred.cpu().numpy()[0]
            }
```

#### Test Position Management

```python
class TestPositionManager:
    def __init__(self):
        self.test_positions = {}
        self.load_test_positions()
    
    def load_test_positions(self):
        """Load predefined test positions"""
        # Strategic positions
        self.test_positions['strategic'] = [
            'opening_position_1',
            'midgame_position_1',
            'endgame_position_1'
        ]
        
        # Tactical positions
        self.test_positions['tactical'] = [
            'blocking_opportunity_1',
            'scoring_opportunity_1',
            'floor_line_risk_1'
        ]
        
        # Random positions
        self.test_positions['random'] = self.generate_random_positions(100)
    
    def get_position(self, position_id):
        """Get specific test position"""
        if position_id in self.test_positions:
            return self.load_position_from_file(position_id)
        else:
            return self.generate_position(position_id)
```

### Evaluation Metrics

#### Performance Metrics

```python
class EvaluationMetrics:
    def __init__(self):
        self.metrics = {
            'win_rate': 0.0,
            'accuracy': 0.0,
            'inference_time': 0.0,
            'consistency': 0.0,
            'strategic_accuracy': 0.0
        }
    
    def calculate_win_rate(self, games_results):
        """Calculate win rate from game results"""
        wins = sum(1 for result in games_results if result == 'win')
        return wins / len(games_results)
    
    def calculate_accuracy(self, predictions, targets):
        """Calculate move prediction accuracy"""
        correct = sum(1 for pred, target in zip(predictions, targets) 
                     if pred == target)
        return correct / len(predictions)
    
    def calculate_inference_time(self, inference_times):
        """Calculate average inference time"""
        return np.mean(inference_times)
    
    def calculate_consistency(self, predictions):
        """Calculate prediction consistency across similar positions"""
        # Group similar positions and check consistency
        consistency_scores = []
        for group in self.group_similar_positions(predictions):
            consistency = self.calculate_group_consistency(group)
            consistency_scores.append(consistency)
        return np.mean(consistency_scores)
```

## Evaluation Process

### Single Model Evaluation

#### Evaluation Workflow

```python
def evaluate_single_model(model_path, config):
    """Evaluate a single neural model"""
    
    # Initialize evaluator
    evaluator = NeuralEvaluator(model_path, config.device)
    
    # Load test positions
    position_manager = TestPositionManager()
    test_positions = position_manager.get_test_positions(config.test_positions)
    
    # Run evaluation
    results = {
        'model': model_path,
        'config': config,
        'metrics': {},
        'detailed_results': []
    }
    
    for position in test_positions:
        # Evaluate position
        start_time = time.time()
        evaluation = evaluator.evaluate_position(position)
        inference_time = time.time() - start_time
        
        # Compare with optimal move
        optimal_move = calculate_optimal_move(position)
        predicted_move = np.argmax(evaluation['policy'])
        
        results['detailed_results'].append({
            'position_id': position['id'],
            'predicted_move': predicted_move,
            'optimal_move': optimal_move,
            'accuracy': predicted_move == optimal_move,
            'inference_time': inference_time,
            'value_prediction': evaluation['value']
        })
    
    # Calculate aggregate metrics
    results['metrics'] = calculate_aggregate_metrics(results['detailed_results'])
    
    return results
```

#### Performance Analysis

```python
def analyze_model_performance(results):
    """Analyze model performance in detail"""
    
    analysis = {
        'overall_performance': {},
        'position_type_performance': {},
        'error_analysis': {},
        'recommendations': []
    }
    
    # Overall performance
    analysis['overall_performance'] = {
        'win_rate': results['metrics']['win_rate'],
        'accuracy': results['metrics']['accuracy'],
        'inference_time': results['metrics']['inference_time'],
        'consistency': results['metrics']['consistency']
    }
    
    # Performance by position type
    for position_type in ['strategic', 'tactical', 'random']:
        type_results = filter_results_by_type(results, position_type)
        analysis['position_type_performance'][position_type] = {
            'accuracy': calculate_accuracy(type_results),
            'avg_inference_time': np.mean([r['inference_time'] for r in type_results])
        }
    
    # Error analysis
    errors = [r for r in results['detailed_results'] if not r['accuracy']]
    analysis['error_analysis'] = {
        'total_errors': len(errors),
        'error_rate': len(errors) / len(results['detailed_results']),
        'common_error_patterns': identify_error_patterns(errors)
    }
    
    # Recommendations
    analysis['recommendations'] = generate_recommendations(analysis)
    
    return analysis
```

### Batch Model Comparison

#### Comparison Framework

```python
def compare_multiple_models(model_paths, config):
    """Compare multiple neural models"""
    
    comparison_results = {
        'models': {},
        'comparison_metrics': {},
        'ranking': [],
        'recommendations': []
    }
    
    # Evaluate each model
    for model_path in model_paths:
        results = evaluate_single_model(model_path, config)
        comparison_results['models'][model_path] = results
    
    # Calculate comparison metrics
    comparison_results['comparison_metrics'] = calculate_comparison_metrics(
        comparison_results['models']
    )
    
    # Rank models
    comparison_results['ranking'] = rank_models(comparison_results['models'])
    
    # Generate recommendations
    comparison_results['recommendations'] = generate_comparison_recommendations(
        comparison_results
    )
    
    return comparison_results
```

#### Ranking Algorithm

```python
def rank_models(model_results):
    """Rank models by performance"""
    
    # Define ranking criteria and weights
    criteria = {
        'accuracy': 0.4,
        'win_rate': 0.3,
        'inference_time': 0.2,
        'consistency': 0.1
    }
    
    rankings = []
    
    for model_path, results in model_results.items():
        score = 0
        for criterion, weight in criteria.items():
            if criterion == 'inference_time':
                # Lower is better for inference time
                normalized_score = 1.0 - min(results['metrics'][criterion] / 1.0, 1.0)
            else:
                normalized_score = results['metrics'][criterion]
            
            score += weight * normalized_score
        
        rankings.append({
            'model_path': model_path,
            'score': score,
            'metrics': results['metrics']
        })
    
    # Sort by score (descending)
    rankings.sort(key=lambda x: x['score'], reverse=True)
    
    return rankings
```

## Test Position Management

### Position Generation

#### Strategic Position Generation

```python
def generate_strategic_positions():
    """Generate strategic test positions"""
    
    positions = []
    
    # Opening positions
    opening_positions = [
        generate_opening_position('balanced'),
        generate_opening_position('aggressive'),
        generate_opening_position('defensive')
    ]
    
    # Midgame positions
    midgame_positions = [
        generate_midgame_position('scoring_opportunity'),
        generate_midgame_position('blocking_opportunity'),
        generate_midgame_position('floor_line_risk')
    ]
    
    # Endgame positions
    endgame_positions = [
        generate_endgame_position('wall_completion'),
        generate_endgame_position('color_set_completion'),
        generate_endgame_position('penalty_minimization')
    ]
    
    positions.extend(opening_positions)
    positions.extend(midgame_positions)
    positions.extend(endgame_positions)
    
    return positions
```

#### Random Position Generation

```python
def generate_random_positions(num_positions):
    """Generate random test positions"""
    
    positions = []
    
    for i in range(num_positions):
        # Generate random game state
        game_state = generate_random_game_state()
        
        # Ensure position is valid and interesting
        if is_valid_position(game_state) and has_interesting_features(game_state):
            positions.append({
                'id': f'random_position_{i}',
                'state': game_state,
                'difficulty': calculate_position_difficulty(game_state)
            })
    
    return positions
```

### Position Validation

```python
def validate_test_position(position):
    """Validate test position quality"""
    
    validation_results = {
        'is_valid': True,
        'issues': [],
        'quality_score': 0.0
    }
    
    # Check basic validity
    if not is_valid_game_state(position['state']):
        validation_results['is_valid'] = False
        validation_results['issues'].append('Invalid game state')
    
    # Check for interesting features
    if not has_interesting_features(position['state']):
        validation_results['issues'].append('Position lacks interesting features')
    
    # Check difficulty level
    difficulty = calculate_position_difficulty(position['state'])
    if difficulty < 0.3 or difficulty > 0.8:
        validation_results['issues'].append('Position difficulty outside optimal range')
    
    # Calculate quality score
    validation_results['quality_score'] = calculate_position_quality(position)
    
    return validation_results
```

## Performance Optimization

### Evaluation Optimization

#### Batch Processing

```python
def batch_evaluate_positions(model, positions, batch_size=32):
    """Evaluate multiple positions in batches"""
    
    results = []
    
    for i in range(0, len(positions), batch_size):
        batch = positions[i:i + batch_size]
        
        # Preprocess batch
        batch_tensors = [preprocess_position(pos) for pos in batch]
        batch_tensor = torch.stack(batch_tensors)
        
        # Evaluate batch
        with torch.no_grad():
            policy_preds, value_preds = model(batch_tensor)
        
        # Process results
        for j, (policy_pred, value_pred) in enumerate(zip(policy_preds, value_preds)):
            results.append({
                'position_id': batch[j]['id'],
                'policy_prediction': policy_pred.cpu().numpy(),
                'value_prediction': value_pred.cpu().numpy()[0]
            })
    
    return results
```

#### Caching System

```python
class EvaluationCache:
    def __init__(self, cache_size=1000):
        self.cache = {}
        self.cache_size = cache_size
    
    def get_cached_result(self, position_hash):
        """Get cached evaluation result"""
        return self.cache.get(position_hash)
    
    def cache_result(self, position_hash, result):
        """Cache evaluation result"""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[position_hash] = result
    
    def clear_cache(self):
        """Clear evaluation cache"""
        self.cache.clear()
```

## API Integration

### Evaluation API Endpoints

#### Start Evaluation

```python
@app.route('/api/v1/neural/evaluate', methods=['POST'])
def start_evaluation():
    """Start model evaluation"""
    
    data = request.get_json()
    
    # Validate request
    model_path = data.get('model')
    if not model_path or not os.path.exists(model_path):
        return jsonify({'error': 'Model file not found'}), 404
    
    # Create evaluation session
    session_id = generate_session_id()
    config = EvaluationConfig(
        model_path=model_path,
        test_positions=data.get('test_positions', 100),
        games=data.get('games', 10),
        search_time=data.get('search_time', 1.0)
    )
    
    # Save session
    db.save_evaluation_session(session_id, config)
    
    # Start evaluation in background
    thread = threading.Thread(
        target=run_evaluation,
        args=(session_id, config)
    )
    thread.start()
    
    return jsonify({
        'session_id': session_id,
        'status': 'started',
        'message': 'Evaluation started successfully'
    })
```

#### Get Evaluation Status

```python
@app.route('/api/v1/neural/evaluate/status/<session_id>', methods=['GET'])
def get_evaluation_status(session_id):
    """Get evaluation session status"""
    
    session_data = db.get_evaluation_session(session_id)
    
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'status': session_data['status'],
        'progress': session_data.get('progress', 0.0),
        'current_results': session_data.get('current_results', {}),
        'elapsed_time': calculate_elapsed_time(session_data['created_at'])
    })
```

## Error Handling

### Evaluation Error Recovery

```python
def handle_evaluation_errors(session_id, error):
    """Handle evaluation errors gracefully"""
    
    # Log error
    logging.error(f"Evaluation error in session {session_id}: {error}")
    
    # Update session status
    db.update_evaluation_session_status(session_id, 'failed', {
        'error': str(error),
        'failed_at': datetime.now()
    })
    
    # Clean up resources
    cleanup_evaluation_resources(session_id)
    
    # Notify user
    notify_evaluation_failure(session_id, error)
```

### Validation Error Handling

```python
def validate_evaluation_config(config):
    """Validate evaluation configuration"""
    
    errors = []
    
    if not os.path.exists(config.model_path):
        errors.append("Model file not found")
    
    if config.test_positions < 1 or config.test_positions > 10000:
        errors.append("Invalid number of test positions")
    
    if config.games < 1 or config.games > 1000:
        errors.append("Invalid number of games")
    
    if config.search_time <= 0 or config.search_time > 60:
        errors.append("Invalid search time")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return config
```

## Testing

### Unit Tests

```python
def test_neural_evaluation():
    """Test neural evaluation functionality"""
    
    # Test evaluator initialization
    evaluator = NeuralEvaluator('test_model.pth')
    assert evaluator is not None
    
    # Test position evaluation
    test_position = generate_test_position()
    result = evaluator.evaluate_position(test_position)
    assert 'policy' in result
    assert 'value' in result
    
    # Test metrics calculation
    metrics = EvaluationMetrics()
    accuracy = metrics.calculate_accuracy([1, 2, 3], [1, 2, 3])
    assert accuracy == 1.0
```

### Integration Tests

```python
def test_evaluation_api():
    """Test evaluation API endpoints"""
    
    # Test start evaluation
    response = client.post('/api/v1/neural/evaluate', json={
        'model': 'test_model.pth',
        'test_positions': 10,
        'games': 5
    })
    assert response.status_code == 200
    
    session_id = response.json['session_id']
    
    # Test status endpoint
    response = client.get(f'/api/v1/neural/evaluate/status/{session_id}')
    assert response.status_code == 200
    assert response.json['status'] in ['running', 'completed']
```

## Related Documentation

- [Neural Training Guide](../../guides/neural/training.md) - User guide for training
- [Neural Evaluation Guide](../../guides/neural/evaluation.md) - User guide for evaluation
- [Neural Integration Guide](../../guides/neural/integration.md) - User guide for integration
- [Neural API Reference](../api/neural-endpoints.md) - API documentation
- [System Architecture](../architecture.md) - System architecture overview 