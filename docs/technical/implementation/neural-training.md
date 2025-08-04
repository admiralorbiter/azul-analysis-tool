# Neural Training Implementation

## Overview

This document describes the technical implementation of the neural training system for Azul game analysis. The system uses PyTorch to train neural networks that can evaluate game positions and suggest optimal moves.

## Architecture

### Core Components

#### Neural Network Architecture

The neural network uses a convolutional architecture optimized for Azul game states:

```python
class AzulNet(nn.Module):
    def __init__(self, model_size='medium'):
        super(AzulNet, self).__init__()
        
        # Model size determines architecture complexity
        if model_size == 'small':
            self.feature_dim = 64
            self.num_layers = 3
        elif model_size == 'medium':
            self.feature_dim = 128
            self.num_layers = 5
        else:  # large
            self.feature_dim = 256
            self.num_layers = 7
            
        # Input processing layers
        self.input_conv = nn.Conv2d(6, self.feature_dim, 3, padding=1)
        self.batch_norm = nn.BatchNorm2d(self.feature_dim)
        self.relu = nn.ReLU()
        
        # Hidden layers
        self.hidden_layers = nn.ModuleList([
            nn.Conv2d(self.feature_dim, self.feature_dim, 3, padding=1)
            for _ in range(self.num_layers - 1)
        ])
        
        # Output layers
        self.policy_head = nn.Linear(self.feature_dim * 25, 60)  # Move probabilities
        self.value_head = nn.Linear(self.feature_dim * 25, 1)    # Position evaluation
```

#### Training Pipeline

The training system implements a complete pipeline for neural model development:

1. **Data Generation**: Synthetic game positions for training
2. **Model Initialization**: Architecture setup and parameter initialization
3. **Training Loop**: Epoch-based training with loss optimization
4. **Validation**: Regular validation on test positions
5. **Model Persistence**: Trained models saved with metadata

### Training Configuration

#### Model Parameters

```python
class TrainingConfig:
    def __init__(self):
        # Model architecture
        self.model_size = 'medium'  # small, medium, large
        self.device = 'cpu'         # cpu, cuda
        
        # Training parameters
        self.epochs = 100
        self.samples_per_epoch = 1000
        self.learning_rate = 0.001
        self.batch_size = 32
        
        # Validation
        self.validation_split = 0.2
        self.save_interval = 10
        
        # Advanced settings
        self.weight_decay = 1e-4
        self.dropout_rate = 0.1
        self.gradient_clip = 1.0
```

#### Loss Functions

The training uses a combination of losses:

```python
class AzulLoss(nn.Module):
    def __init__(self, policy_weight=1.0, value_weight=1.0):
        super(AzulLoss, self).__init__()
        self.policy_weight = policy_weight
        self.value_weight = value_weight
        self.policy_loss = nn.CrossEntropyLoss()
        self.value_loss = nn.MSELoss()
    
    def forward(self, policy_pred, value_pred, policy_target, value_target):
        policy_loss = self.policy_loss(policy_pred, policy_target)
        value_loss = self.value_loss(value_pred, value_target)
        
        total_loss = (self.policy_weight * policy_loss + 
                     self.value_weight * value_loss)
        return total_loss, policy_loss, value_loss
```

## Data Management

### Training Data Generation

#### Position Generation

```python
def generate_training_positions(num_positions):
    """Generate synthetic training positions"""
    positions = []
    
    for _ in range(num_positions):
        # Generate random game state
        game_state = generate_random_game_state()
        
        # Calculate target values
        policy_target = calculate_optimal_moves(game_state)
        value_target = evaluate_position(game_state)
        
        positions.append({
            'state': game_state,
            'policy_target': policy_target,
            'value_target': value_target
        })
    
    return positions
```

#### Data Augmentation

The system uses data augmentation to improve training:

```python
def augment_training_data(positions):
    """Apply data augmentation techniques"""
    augmented = []
    
    for pos in positions:
        # Original position
        augmented.append(pos)
        
        # Rotated positions
        for rotation in [90, 180, 270]:
            rotated_state = rotate_game_state(pos['state'], rotation)
            augmented.append({
                'state': rotated_state,
                'policy_target': rotate_policy(pos['policy_target'], rotation),
                'value_target': pos['value_target']  # Value unchanged
            })
        
        # Color permutations
        for perm in generate_color_permutations():
            permuted_state = permute_colors(pos['state'], perm)
            augmented.append({
                'state': permuted_state,
                'policy_target': permute_policy(pos['policy_target'], perm),
                'value_target': pos['value_target']
            })
    
    return augmented
```

### Database Integration

#### Training Session Storage

```python
class NeuralTrainingDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS neural_training_sessions (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT UNIQUE,
                    model_size TEXT,
                    device TEXT,
                    epochs INTEGER,
                    status TEXT,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata TEXT
                )
            """)
    
    def save_session(self, session_data):
        """Save training session data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO neural_training_sessions 
                (session_id, model_size, device, epochs, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                session_data['model_size'],
                session_data['device'],
                session_data['epochs'],
                session_data['status'],
                datetime.now()
            ))
```

## Training Process

### Training Loop Implementation

```python
def train_neural_model(config, session_id):
    """Main training function"""
    
    # Initialize model
    model = AzulNet(config.model_size)
    model.to(config.device)
    
    # Initialize optimizer and loss
    optimizer = torch.optim.Adam(
        model.parameters(), 
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    criterion = AzulLoss()
    
    # Generate training data
    train_data = generate_training_positions(config.samples_per_epoch)
    val_data = generate_training_positions(config.samples_per_epoch // 5)
    
    # Training loop
    for epoch in range(config.epochs):
        model.train()
        total_loss = 0
        
        for batch in create_batches(train_data, config.batch_size):
            # Forward pass
            states = batch['states'].to(config.device)
            policy_targets = batch['policy_targets'].to(config.device)
            value_targets = batch['value_targets'].to(config.device)
            
            policy_pred, value_pred = model(states)
            
            # Calculate loss
            loss, policy_loss, value_loss = criterion(
                policy_pred, value_pred, policy_targets, value_targets
            )
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clip)
            optimizer.step()
            
            total_loss += loss.item()
        
        # Validation
        if epoch % config.save_interval == 0:
            val_loss = validate_model(model, val_data, config.device)
            save_checkpoint(model, session_id, epoch, val_loss)
        
        # Update progress
        update_training_progress(session_id, epoch, total_loss / len(train_data))
    
    # Save final model
    save_final_model(model, session_id)
```

### Progress Tracking

#### Real-time Updates

```python
def update_training_progress(session_id, epoch, loss):
    """Update training progress in database"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE neural_training_sessions 
            SET metadata = json_set(metadata, '$.current_epoch', ?)
            WHERE session_id = ?
        """, (epoch, session_id))
        
        # Store loss history
        conn.execute("""
            UPDATE neural_training_sessions 
            SET metadata = json_set(metadata, '$.loss_history', 
                json_insert(metadata->'$.loss_history', '$[#]', ?))
            WHERE session_id = ?
        """, (loss, session_id))
```

## Model Evaluation

### Performance Metrics

#### Evaluation Functions

```python
def evaluate_model_performance(model, test_positions):
    """Evaluate model performance on test positions"""
    model.eval()
    results = {
        'win_rate': 0.0,
        'accuracy': 0.0,
        'inference_time': 0.0
    }
    
    correct_moves = 0
    total_moves = 0
    inference_times = []
    
    with torch.no_grad():
        for position in test_positions:
            start_time = time.time()
            
            # Model prediction
            policy_pred, value_pred = model(position['state'])
            predicted_move = torch.argmax(policy_pred).item()
            
            inference_time = time.time() - start_time
            inference_times.append(inference_time)
            
            # Compare with optimal move
            if predicted_move == position['optimal_move']:
                correct_moves += 1
            total_moves += 1
    
    results['accuracy'] = correct_moves / total_moves
    results['inference_time'] = np.mean(inference_times)
    
    return results
```

### Model Comparison

```python
def compare_models(model_paths, test_positions):
    """Compare multiple models"""
    results = {}
    
    for model_path in model_paths:
        model = load_model(model_path)
        performance = evaluate_model_performance(model, test_positions)
        results[model_path] = performance
    
    return results
```

## API Integration

### Training API Endpoints

#### Start Training

```python
@app.route('/api/v1/neural/train', methods=['POST'])
def start_training():
    """Start a new training session"""
    data = request.get_json()
    
    # Validate configuration
    config = validate_training_config(data)
    
    # Create session
    session_id = generate_session_id()
    session_data = {
        'session_id': session_id,
        'config': config,
        'status': 'started',
        'created_at': datetime.now()
    }
    
    # Save to database
    db.save_session(session_data)
    
    # Start training in background
    thread = threading.Thread(
        target=train_neural_model,
        args=(config, session_id)
    )
    thread.start()
    
    return jsonify({
        'session_id': session_id,
        'status': 'started',
        'message': 'Training session started successfully'
    })
```

#### Get Training Status

```python
@app.route('/api/v1/neural/status/<session_id>', methods=['GET'])
def get_training_status(session_id):
    """Get training session status"""
    session_data = db.get_session(session_id)
    
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'status': session_data['status'],
        'progress': session_data.get('progress', 0.0),
        'current_epoch': session_data.get('current_epoch', 0),
        'loss_history': session_data.get('loss_history', []),
        'elapsed_time': calculate_elapsed_time(session_data['created_at'])
    })
```

## Performance Optimization

### Training Optimization

#### Memory Management

```python
def optimize_memory_usage(config):
    """Optimize memory usage for training"""
    if config.device == 'cuda':
        # Clear GPU cache
        torch.cuda.empty_cache()
        
        # Use mixed precision training
        scaler = torch.cuda.amp.GradScaler()
        return scaler
    return None
```

#### Batch Processing

```python
def create_optimized_batches(data, batch_size):
    """Create memory-efficient batches"""
    batches = []
    
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i + batch_size]
        
        # Convert to tensors efficiently
        states = torch.stack([item['state'] for item in batch_data])
        policy_targets = torch.stack([item['policy_target'] for item in batch_data])
        value_targets = torch.stack([item['value_target'] for item in batch_data])
        
        batches.append({
            'states': states,
            'policy_targets': policy_targets,
            'value_targets': value_targets
        })
    
    return batches
```

### Inference Optimization

#### Model Optimization

```python
def optimize_model_for_inference(model):
    """Optimize model for fast inference"""
    # Enable inference mode
    model.eval()
    
    # Use TorchScript for faster inference
    scripted_model = torch.jit.script(model)
    
    # Quantize model for smaller size
    quantized_model = torch.quantization.quantize_dynamic(
        scripted_model, {torch.nn.Linear}, dtype=torch.qint8
    )
    
    return quantized_model
```

## Error Handling

### Training Error Recovery

```python
def handle_training_errors(session_id, error):
    """Handle training errors gracefully"""
    # Log error
    logging.error(f"Training error in session {session_id}: {error}")
    
    # Update session status
    db.update_session_status(session_id, 'failed', {
        'error': str(error),
        'failed_at': datetime.now()
    })
    
    # Clean up resources
    cleanup_training_resources(session_id)
    
    # Notify user
    notify_training_failure(session_id, error)
```

### Validation Error Handling

```python
def validate_training_config(config):
    """Validate training configuration"""
    errors = []
    
    if config.model_size not in ['small', 'medium', 'large']:
        errors.append("Invalid model size")
    
    if config.device not in ['cpu', 'cuda']:
        errors.append("Invalid device")
    
    if config.epochs < 1 or config.epochs > 1000:
        errors.append("Invalid number of epochs")
    
    if config.learning_rate <= 0 or config.learning_rate > 1:
        errors.append("Invalid learning rate")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return config
```

## Testing

### Unit Tests

```python
def test_neural_training():
    """Test neural training functionality"""
    # Test model initialization
    model = AzulNet('small')
    assert model is not None
    
    # Test training configuration
    config = TrainingConfig()
    config.model_size = 'small'
    config.epochs = 1
    assert config.epochs == 1
    
    # Test data generation
    positions = generate_training_positions(10)
    assert len(positions) == 10
    
    # Test training loop
    session_id = 'test_session'
    train_neural_model(config, session_id)
    
    # Verify model was saved
    assert os.path.exists(f'models/{session_id}.pth')
```

### Integration Tests

```python
def test_training_api():
    """Test training API endpoints"""
    # Test start training
    response = client.post('/api/v1/neural/train', json={
        'model_size': 'small',
        'epochs': 1,
        'device': 'cpu'
    })
    assert response.status_code == 200
    
    session_id = response.json['session_id']
    
    # Test status endpoint
    response = client.get(f'/api/v1/neural/status/{session_id}')
    assert response.status_code == 200
    assert response.json['status'] in ['running', 'completed']
```

## Related Documentation

- [Neural Training Guide](../../guides/neural/training.md) - User guide for training
- [Neural Evaluation Guide](../../guides/neural/evaluation.md) - User guide for evaluation
- [Neural Integration Guide](../../guides/neural/integration.md) - User guide for integration
- [Neural API Reference](../api/neural-endpoints.md) - API documentation
- [System Architecture](../architecture.md) - System architecture overview 