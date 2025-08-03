from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import uuid
import threading
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from ..models import NeuralTrainingRequest, NeuralEvaluationRequest
from ..utils import get_process_resources, get_system_resources

# Create blueprint
neural_bp = Blueprint('neural', __name__)

# Global database reference (will be set by main app)
db = None

# Global evaluation sessions storage (temporary until database integration)
evaluation_sessions = {}

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


# Neural Evaluation Endpoints

@neural_bp.route('/neural/evaluate', methods=['POST'])
def evaluate_neural_model():
    """Evaluate a trained neural model."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate request data
        try:
            eval_request = NeuralEvaluationRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid evaluation configuration', 'details': e.errors()}), 400
        
        # Check if neural components are available
        try:
            from neural.evaluate import EvaluationConfig, AzulModelEvaluator
        except ImportError:
            return jsonify({
                'error': 'Neural evaluation not available',
                'message': 'PyTorch and neural components are not installed. Install with: pip install torch'
            }), 503
        
        # Check if model exists
        import os
        if not os.path.exists(eval_request.model):
            return jsonify({
                'error': 'Model not found',
                'message': f'Model file {eval_request.model} does not exist'
            }), 404
        
        # Create evaluation configuration
        config = EvaluationConfig(
            num_positions=eval_request.positions,
            num_games=eval_request.games,
            search_time=0.5,
            max_rollouts=50,
            model_path=eval_request.model,
            device=eval_request.device,
            compare_heuristic=True,
            compare_random=True
        )
        
        # Generate session ID for this evaluation
        session_id = f"eval_{uuid.uuid4().hex[:8]}"
        
        # Create evaluation session
        # Convert config to dict and remove non-serializable fields
        config_dict = asdict(config)
        if 'progress_callback' in config_dict:
            del config_dict['progress_callback']
        
        # Store in global sessions (temporary until we move to database)
        global evaluation_sessions
        evaluation_sessions[session_id] = {
            'status': 'running',
            'progress': 0,
            'start_time': time.time(),
            'config': config_dict,
            'results': None,
            'error': None
        }
        
        # Run evaluation in background
        def evaluate_in_background():
            try:
                def progress_callback(percent):
                    evaluation_sessions[session_id]['progress'] = percent
                config.progress_callback = progress_callback
                evaluator = AzulModelEvaluator(config)
                results = evaluator.evaluate_model()
                evaluation_sessions[session_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'results': results,
                    'end_time': time.time()
                })
            except Exception as e:
                evaluation_sessions[session_id].update({
                    'status': 'failed',
                    'error': str(e),
                    'end_time': time.time()
                })
        
        # Start background thread
        thread = threading.Thread(target=evaluate_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Evaluation started in background',
            'session_id': session_id,
            'status_url': f'/api/v1/neural/evaluate/status/{session_id}'
        })
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/evaluate/status/<session_id>', methods=['GET'])
def get_evaluation_status(session_id):
    """Get evaluation status for a session."""
    try:
        # Get session from global storage (temporary)
        global evaluation_sessions
        session = evaluation_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Evaluation session not found'}), 404
        
        response_data = {
            'session_id': session_id,
            'status': session['status'],
            'progress': session['progress'],
            'start_time': session['start_time'],
            'end_time': session.get('end_time'),
            'config': session['config'],
            'results': session['results'],
            'error': session['error']
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get evaluation status',
            'message': str(e)
        }), 500


# Neural Session Management Endpoints

@neural_bp.route('/neural/sessions', methods=['GET'])
def get_all_training_sessions():
    """Get all training sessions from database."""
    try:
        # Get query parameters for filtering
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get sessions from database
        db_sessions = db.get_all_neural_training_sessions(
            status=status,
            limit=limit
        )
        
        # Convert database sessions to API response format
        sessions = []
        for db_session in db_sessions:
            session_data = {
                'session_id': db_session.session_id,
                'status': db_session.status,
                'progress': db_session.progress,
                'start_time': db_session.start_time.isoformat() if db_session.start_time else None,
                'end_time': db_session.end_time.isoformat() if db_session.end_time else None,
                'config': db_session.config if db_session.config else {},
                'logs': db_session.logs if db_session.logs else [],
                'error': db_session.error,
                'results': db_session.results if db_session.results else None,
                'metadata': db_session.metadata if db_session.metadata else {}
            }
            sessions.append(session_data)
        
        # Get total count for pagination
        all_sessions = db.get_all_neural_training_sessions()
        total_count = len(all_sessions)
        active_count = len([s for s in all_sessions if s.status in ['starting', 'running']])
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions),
            'total_count': total_count,
            'active_count': active_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get sessions',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/sessions/<session_id>', methods=['DELETE'])
def delete_training_session(session_id):
    """Delete a training session from database."""
    try:
        # Check if session exists
        db_session = db.get_neural_training_session(session_id)
        if not db_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Delete session from database
        success = db.delete_neural_training_session(session_id)
        if not success:
            return jsonify({'error': 'Failed to delete session'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Session deleted',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete session',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/evaluation-sessions', methods=['GET'])
def get_all_evaluation_sessions():
    """Get all active evaluation sessions."""
    try:
        sessions = []
        for session_id, session in evaluation_sessions.items():
            # Calculate elapsed time
            elapsed_time = None
            if 'start_time' in session:
                start_time = session['start_time']
                if isinstance(start_time, (int, float)):
                    elapsed_time = time.time() - start_time
                else:
                    # Handle string timestamps
                    try:
                        import datetime
                        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        elapsed_time = (datetime.datetime.now() - start_dt).total_seconds()
                    except:
                        elapsed_time = 0
            
            session_data = {
                'session_id': session_id,
                'status': session.get('status', 'unknown'),
                'progress': session.get('progress', 0),
                'start_time': session.get('start_time'),
                'end_time': session.get('end_time'),
                'elapsed_time': elapsed_time,
                'config': session.get('config'),
                'error': session.get('error'),
                'results': session.get('results')
            }
            sessions.append(session_data)
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions),
            'active_count': len([s for s in sessions if s['status'] in ['starting', 'running']])
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get evaluation sessions',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/evaluation-sessions/<session_id>', methods=['DELETE'])
def delete_evaluation_session(session_id):
    """Delete an evaluation session."""
    if session_id not in evaluation_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    del evaluation_sessions[session_id]
    
    return jsonify({
        'success': True,
        'message': 'Evaluation session deleted',
        'session_id': session_id
    })


@neural_bp.route('/neural/training-history', methods=['GET'])
def get_training_history():
    """Get historical training data with advanced filtering and sorting."""
    try:
        # Get query parameters
        status = request.args.get('status')
        config_size = request.args.get('config_size')  # small, medium, large
        device = request.args.get('device')  # cpu, cuda
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, progress, status
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        # Get sessions from database with filtering
        db_sessions = db.get_all_neural_training_sessions(
            status=status,
            limit=limit
        )
        
        # Apply additional filtering
        filtered_sessions = []
        for session in db_sessions:
            # Parse metadata for additional filtering
            metadata = session.metadata if session.metadata else {}
            
            # Filter by config size
            if config_size and metadata.get('config_size') != config_size:
                continue
                
            # Filter by device
            if device and metadata.get('device') != device:
                continue
                
            # Filter by date range
            if date_from and session.created_at:
                from datetime import datetime
                try:
                    date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    if session.created_at < date_from_dt:
                        continue
                except:
                    pass
                    
            if date_to and session.created_at:
                from datetime import datetime
                try:
                    date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    if session.created_at > date_to_dt:
                        continue
                except:
                    pass
            
            filtered_sessions.append(session)
        
        # Sort sessions
        if sort_by == 'created_at':
            filtered_sessions.sort(key=lambda x: x.created_at or datetime.min, reverse=(sort_order == 'desc'))
        elif sort_by == 'progress':
            filtered_sessions.sort(key=lambda x: x.progress or 0, reverse=(sort_order == 'desc'))
        elif sort_by == 'status':
            filtered_sessions.sort(key=lambda x: x.status or '', reverse=(sort_order == 'desc'))
        
        # Convert to API response format
        sessions = []
        for db_session in filtered_sessions:
            session_data = {
                'session_id': db_session.session_id,
                'status': db_session.status,
                'progress': db_session.progress,
                'start_time': db_session.start_time.isoformat() if db_session.start_time else None,
                'end_time': db_session.end_time.isoformat() if db_session.end_time else None,
                'config': db_session.config if db_session.config else {},
                'logs': db_session.logs if db_session.logs else [],
                'error': db_session.error,
                'results': db_session.results if db_session.results else None,
                'metadata': db_session.metadata if db_session.metadata else {}
            }
            sessions.append(session_data)
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions),
            'total_count': len(filtered_sessions),
            'filters': {
                'status': status,
                'config_size': config_size,
                'device': device,
                'date_from': date_from,
                'date_to': date_to
            },
            'sorting': {
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get training history',
            'message': str(e)
        }), 500


# Neural Model Management Endpoints

@neural_bp.route('/neural/models', methods=['GET'])
def get_available_models():
    """Get list of available trained models."""
    try:
        import os
        import glob
        
        models_dir = "models"
        if not os.path.exists(models_dir):
            return jsonify({
                'models': [],
                'message': 'No models directory found'
            })
        
        # Find all .pth files
        model_files = glob.glob(os.path.join(models_dir, "*.pth"))
        models = []
        
        for model_path in model_files:
            filename = os.path.basename(model_path)
            size = os.path.getsize(model_path)
            models.append({
                'name': filename,
                'path': model_path,
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2)
            })
        
        return jsonify({
            'models': models,
            'count': len(models)
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get models',
            'message': str(e)
        }), 500


# Neural Configuration Endpoints

@neural_bp.route('/neural/config', methods=['GET'])
def get_neural_config():
    """Get current neural training configuration."""
    try:
        # Return default configuration
        config = {
            'config': 'small',
            'device': 'cpu',
            'epochs': 5,
            'samples': 500,
            'batch_size': 16,
            'learning_rate': 0.001,
            'available_configs': ['small', 'medium', 'large'],
            'available_devices': ['cpu', 'cuda']
        }
        
        return jsonify(config)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get configuration',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/config', methods=['POST'])
def save_neural_config():
    """Save neural training configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate request data
        try:
            from ..models import NeuralConfigRequest
            config_request = NeuralConfigRequest(**data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid configuration', 'details': e.errors()}), 400
        
        # In a real implementation, this would save to a config file or database
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to save configuration',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/configurations', methods=['GET'])
def get_neural_configurations():
    """Get all saved neural training configurations."""
    try:
        # Get query parameters
        is_default = request.args.get('is_default', type=bool)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get configurations from database
        db_configs = db.get_neural_configurations(
            is_default=is_default
        )
        
        # Convert to API response format
        configurations = []
        for db_config in db_configs:
            config_data = {
                'config_id': db_config.config_id,
                'name': db_config.name,
                'description': db_config.description,
                'is_default': db_config.is_default,
                'config': json.loads(db_config.config) if db_config.config else {},
                'metadata': json.loads(db_config.metadata) if db_config.metadata else {},
                'created_at': db_config.created_at.isoformat() if db_config.created_at else None,
                'updated_at': db_config.updated_at.isoformat() if db_config.updated_at else None
            }
            configurations.append(config_data)
        
        return jsonify({
            'configurations': configurations,
            'count': len(configurations),
            'filters': {
                'is_default': is_default
            },
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get configurations',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/configurations', methods=['POST'])
def save_neural_configuration():
    """Save a new neural training configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'config']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create configuration object
        from core.azul_database import NeuralConfiguration
        db_config = NeuralConfiguration(
            config_id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description', ''),
            is_default=data.get('is_default', False),
            config=json.dumps(data['config']),
            metadata=json.dumps(data.get('metadata', {}))
        )
        
        # Save to database
        success = db.save_neural_configuration(db_config)
        if not success:
            return jsonify({'error': 'Failed to save configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration saved',
            'config_id': db_config.config_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to save configuration',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/configurations/<config_id>', methods=['PUT'])
def update_neural_configuration(config_id):
    """Update an existing neural training configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get existing configuration
        db_config = db.get_neural_configuration(config_id)
        if not db_config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Update fields
        if 'name' in data:
            db_config.name = data['name']
        if 'description' in data:
            db_config.description = data['description']
        if 'is_default' in data:
            db_config.is_default = data['is_default']
        if 'config' in data:
            db_config.config = json.dumps(data['config'])
        if 'metadata' in data:
            db_config.metadata = json.dumps(data['metadata'])
        
        # Save updated configuration
        success = db.save_neural_configuration(db_config)
        if not success:
            return jsonify({'error': 'Failed to update configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated',
            'config_id': config_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update configuration',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/configurations/<config_id>', methods=['DELETE'])
def delete_neural_configuration(config_id):
    """Delete a neural training configuration."""
    try:
        # Check if configuration exists
        db_config = db.get_neural_configuration(config_id)
        if not db_config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Delete configuration
        success = db.delete_neural_configuration(config_id)
        if not success:
            return jsonify({'error': 'Failed to delete configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration deleted',
            'config_id': config_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete configuration',
            'message': str(e)
        }), 500


@neural_bp.route('/neural/status', methods=['GET'])
def get_neural_status():
    """Get overall neural system status."""
    try:
        # Check if neural components are available
        neural_available = True
        try:
            import torch
            from neural.azul_net import AzulNet
        except ImportError:
            neural_available = False
        
        # Get system resources
        try:
            from ..utils import get_process_resources, get_system_resources
            process_resources = get_process_resources()
            system_resources = get_system_resources()
        except Exception:
            process_resources = {'error': 'Failed to get process resources'}
            system_resources = {'error': 'Failed to get system resources'}
        
        # Check for available models
        import os
        import glob
        models_dir = "models"
        available_models = []
        if os.path.exists(models_dir):
            model_files = glob.glob(os.path.join(models_dir, "*.pth"))
            available_models = [os.path.basename(f) for f in model_files]
        
        status = {
            'neural_available': neural_available,
            'available_models': available_models,
            'model_count': len(available_models),
            'process_resources': process_resources,
            'system_resources': system_resources,
            'timestamp': time.time()
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get neural status',
            'message': str(e)
        }), 500 