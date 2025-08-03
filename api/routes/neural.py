from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..models import NeuralTrainingRequest, NeuralEvaluationRequest
from ..utils import get_process_resources

# Create blueprint
neural_bp = Blueprint('neural', __name__)

# Global database reference (will be set by main app)
db = None

def init_neural_routes(database):
    """Initialize neural routes with database reference."""
    global db
    db = database

@neural_bp.route('/neural/train', methods=['POST'])
def start_neural_training():
    """Start neural network training in background with enhanced monitoring."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate request data
        try:
            training_request = NeuralTrainingRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid training configuration', 'details': e.errors()}), 400
        
        # Check if neural components are available
        try:
            from neural.train import TrainingConfig, AzulNetTrainer
        except ImportError:
            return jsonify({
                'error': 'Neural training not available',
                'message': 'PyTorch and neural components are not installed. Install with: pip install torch'
            }), 503
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create database session only (no in-memory session)
        from core.azul_database import NeuralTrainingSession
        db_session = NeuralTrainingSession(
            session_id=session_id,
            status='starting',
            progress=0,
            start_time=datetime.now(),
            config=training_request.dict(),
            logs=['Training session created'],
            error=None,
            results=None,
            loss_history=[],
            epoch_history=[],
            timestamp_history=[],
            cpu_usage=[],
            memory_usage=[],
            gpu_usage=[],
            estimated_total_time=None,
            current_epoch=0,
            total_epochs=training_request.epochs,
            created_at=datetime.now(),
            metadata={
                'device': training_request.device,
                'config_size': training_request.config,
                'epochs': training_request.epochs,
                'samples': training_request.samples,
                'batch_size': training_request.batch_size,
                'learning_rate': training_request.learning_rate
            }
        )
        db.save_neural_training_session(db_session)
        
        # Start training in background thread
        def train_in_background():
            try:
                # Update status to running
                db_session = db.get_neural_training_session(session_id)
                if not db_session:
                    return
                
                db_session.status = 'running'
                db_session.logs.append('Training started')
                db.save_neural_training_session(db_session)
                
                # Configuration based on size
                if training_request.config == 'small':
                    hidden_size = 64
                    num_layers = 2
                elif training_request.config == 'medium':
                    hidden_size = 128
                    num_layers = 3
                else:  # large
                    hidden_size = 256
                    num_layers = 4
                
                # Create training config
                train_config = TrainingConfig(
                    batch_size=training_request.batch_size,
                    learning_rate=training_request.learning_rate,
                    num_epochs=training_request.epochs,
                    num_samples=training_request.samples,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    device=training_request.device
                )
                
                # Create custom trainer with progress callbacks
                class MonitoredTrainer(AzulNetTrainer):
                    def __init__(self, config, session_id, db):
                        super().__init__(config)
                        self.session_id = session_id
                        self.db = db
                        self.epoch_count = 0
                    
                    def _train_epoch(self, states, policy_targets, value_targets):
                        """Override to add progress monitoring."""
                        # Get current session from database
                        db_session = self.db.get_neural_training_session(self.session_id)
                        if not db_session:
                            raise InterruptedError("Session not found")
                        
                        # Check if stop requested
                        if db_session.status == 'stopped':
                            raise InterruptedError("Training stopped by user")
                        
                        # Get resource usage
                        resources = get_process_resources()
                        db_session.cpu_usage.append(resources['cpu_percent'])
                        db_session.memory_usage.append(resources['memory_percent'])
                        
                        # Train epoch
                        loss = super()._train_epoch(states, policy_targets, value_targets)
                        
                        # Update progress
                        self.epoch_count += 1
                        progress = min(80, (self.epoch_count / train_config.num_epochs) * 80)
                        
                        # Update database session with progress
                        db_session.progress = int(progress)
                        db_session.current_epoch = self.epoch_count
                        db_session.loss_history.append(loss)
                        db_session.epoch_history.append(self.epoch_count)
                        db_session.timestamp_history.append(datetime.now().isoformat())
                        
                        # Save progress to database
                        self.db.save_neural_training_session(db_session)
                        
                        return loss
                
                # Train model with monitoring
                trainer = MonitoredTrainer(train_config, session_id, db)
                losses = trainer.train()
                
                # Get final session and update with completion
                db_session = db.get_neural_training_session(session_id)
                if db_session:
                    db_session.logs.append(f'Training completed with {len(losses)} epochs')
                    db_session.progress = 80
                    db.save_neural_training_session(db_session)
                
                # Evaluate
                eval_results = trainer.evaluate(num_samples=50)
                if db_session:
                    db_session.logs.append('Evaluation completed')
                    db_session.progress = 90
                    db.save_neural_training_session(db_session)
                
                # Save model
                import os
                os.makedirs("models", exist_ok=True)
                model_path = f"models/azul_net_{training_request.config}.pth"
                trainer.save_model(model_path)
                
                # Final update with completed status
                if db_session:
                    db_session.logs.append(f'Model saved to {model_path}')
                    db_session.progress = 100
                    db_session.status = 'completed'
                    db_session.end_time = datetime.now()
                    db_session.results = {
                        'final_loss': losses[-1] if losses else 0.0,
                        'evaluation_error': eval_results.get('avg_value_error', 0.0),
                        'model_path': model_path,
                        'config': training_request.config,
                        'epochs': training_request.epochs,
                        'samples': training_request.samples
                    }
                    
                    # Update metadata with final results
                    if not db_session.metadata:
                        db_session.metadata = {}
                    db_session.metadata.update({
                        'final_loss': losses[-1] if losses else 0.0,
                        'evaluation_error': eval_results.get('avg_value_error', 0.0),
                        'model_path': model_path
                    })
                    
                    db.save_neural_training_session(db_session)
                
            except InterruptedError:
                # Update database with stopped status
                db_session = db.get_neural_training_session(session_id)
                if db_session:
                    db_session.status = 'stopped'
                    db_session.logs.append('Training stopped by user')
                    db_session.end_time = datetime.now()
                    db.save_neural_training_session(db_session)
                
            except Exception as e:
                # Update database with failed status
                db_session = db.get_neural_training_session(session_id)
                if db_session:
                    db_session.status = 'failed'
                    db_session.error = str(e)
                    db_session.logs.append(f'Error: {str(e)}')
                    db_session.end_time = datetime.now()
                    db.save_neural_training_session(db_session)
        
        # Start background thread
        thread = threading.Thread(target=train_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Training started in background',
            'session_id': session_id,
            'status': 'starting'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/status/<session_id>', methods=['GET'])
def get_training_status(session_id):
    """Get enhanced training status for a session with loss history and resource monitoring."""
    try:
        # Get session from database
        db_session = db.get_neural_training_session(session_id)
        if not db_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Convert database session to API response format
        response_data = {
            'session_id': db_session.session_id,
            'status': db_session.status,
            'progress': db_session.progress,
            'start_time': db_session.start_time.isoformat() if db_session.start_time else None,
            'end_time': db_session.end_time.isoformat() if db_session.end_time else None,
            'config': db_session.config if isinstance(db_session.config, dict) else {},
            'logs': db_session.logs if isinstance(db_session.logs, list) else [],
            'error': db_session.error,
            'results': db_session.results if isinstance(db_session.results, dict) else None,
            'metadata': db_session.metadata if isinstance(db_session.metadata, dict) else {},
            # Enhanced monitoring fields
            'loss_history': db_session.loss_history if db_session.loss_history else [],
            'epoch_history': db_session.epoch_history if db_session.epoch_history else [],
            'timestamp_history': db_session.timestamp_history if db_session.timestamp_history else [],
            'cpu_usage': db_session.cpu_usage if db_session.cpu_usage else [],
            'memory_usage': db_session.memory_usage if db_session.memory_usage else [],
            'gpu_usage': db_session.gpu_usage if db_session.gpu_usage else [],
            'estimated_total_time': db_session.estimated_total_time,
            'current_epoch': db_session.current_epoch,
            'total_epochs': db_session.total_epochs
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get session status',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/stop/<session_id>', methods=['POST'])
def stop_training(session_id):
    """Stop training for a session."""
    try:
        # Get session from database
        db_session = db.get_neural_training_session(session_id)
        if not db_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update session status to stopped
        db_session.status = 'stopped'
        db_session.logs.append('Stop requested - training will terminate gracefully')
        
        # Save updated session to database
        db.save_neural_training_session(db_session)
        
        return jsonify({
            'success': True,
            'message': 'Training stop requested',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to stop training',
            'message': str(e)
        }), 500 