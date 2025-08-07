#!/usr/bin/env python3
"""
Machine Learning Integration for Move Quality

This script integrates machine learning with the move quality database to:
- Train models on move quality data
- Predict move quality for new positions
- Continuously improve models with new data
- Generate insights and recommendations
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import sqlite3
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pickle
import joblib

# Machine learning imports
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, r2_score, classification_report
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.neural_network import MLPRegressor
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    print("⚠️ Machine learning libraries not available. Install with: pip install scikit-learn xgboost")
    ML_AVAILABLE = False

from core.azul_model import AzulState
from analysis_engine.move_quality.azul_move_quality_assessor import AzulMoveQualityAssessor
from api.utils.state_parser import parse_fen_string

@dataclass
class MLModel:
    """Data structure for a trained ML model."""
    model_id: str
    model_type: str
    model_path: str
    training_data_size: int
    accuracy_score: float
    feature_importance: Dict[str, float]
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class PredictionResult:
    """Data structure for ML prediction results."""
    position_fen: str
    move_data: Dict[str, Any]
    predicted_quality: float
    confidence: float
    feature_values: Dict[str, float]
    model_used: str
    created_at: datetime

class MoveQualityML:
    """Machine learning integration for move quality prediction."""
    
    def __init__(self, db_path: str = "../data/ml_move_quality.db"):
        self.db_path = db_path
        self._init_ml_database()
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
    def _init_ml_database(self):
        """Initialize database for ML models and predictions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- ML models table
                CREATE TABLE IF NOT EXISTS ml_models (
                    id INTEGER PRIMARY KEY,
                    model_id TEXT UNIQUE NOT NULL,
                    model_type TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    training_data_size INTEGER NOT NULL,
                    accuracy_score REAL NOT NULL,
                    feature_importance TEXT,  -- JSON feature importance
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT  -- JSON metadata
                );
                
                -- Training data table
                CREATE TABLE IF NOT EXISTS ml_training_data (
                    id INTEGER PRIMARY KEY,
                    position_fen TEXT NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON move data
                    quality_score REAL NOT NULL,
                    features TEXT NOT NULL,  -- JSON feature vector
                    target_label TEXT NOT NULL,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Predictions table
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY,
                    position_fen TEXT NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON move data
                    predicted_quality REAL NOT NULL,
                    confidence REAL,
                    feature_values TEXT,  -- JSON feature values
                    model_used TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Model performance tracking
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY,
                    model_id TEXT NOT NULL,
                    test_accuracy REAL NOT NULL,
                    test_mse REAL NOT NULL,
                    cross_val_score REAL,
                    prediction_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_models_type ON ml_models(model_type);
                CREATE INDEX IF NOT EXISTS idx_models_accuracy ON ml_models(accuracy_score DESC);
                CREATE INDEX IF NOT EXISTS idx_training_position ON ml_training_data(position_fen);
                CREATE INDEX IF NOT EXISTS idx_predictions_position ON ml_predictions(position_fen);
                CREATE INDEX IF NOT EXISTS idx_performance_model ON model_performance(model_id);
            """)
    
    def prepare_training_data(self, num_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from the move quality database."""
        print(f"📊 Preparing training data ({num_samples} samples)...")
        
        # Load data from enhanced database
        enhanced_db_path = "../data/enhanced_move_quality.db"
        if not os.path.exists(enhanced_db_path):
            print(f"❌ Enhanced database not found: {enhanced_db_path}")
            print("Run enhance_database.py first!")
            return np.array([]), np.array([])
        
        with sqlite3.connect(enhanced_db_path) as conn:
            cursor = conn.execute("""
                SELECT neural_score, pattern_score, strategic_score, tactical_score,
                       risk_score, opportunity_score, blocking_opportunities,
                       scoring_opportunities, floor_line_risks, strategic_value,
                       quality_score
                FROM enhanced_move_quality
                WHERE quality_score IS NOT NULL
                ORDER BY RANDOM()
                LIMIT ?
            """, (num_samples,))
            
            data = cursor.fetchall()
        
        if not data:
            print("❌ No training data found!")
            return np.array([]), np.array([])
        
        # Convert to numpy arrays
        features = []
        targets = []
        
        for row in data:
            feature_vector = [
                row[0] or 0.0,  # neural_score
                row[1] or 0.0,  # pattern_score
                row[2] or 0.0,  # strategic_score
                row[3] or 0.0,  # tactical_score
                row[4] or 0.0,  # risk_score
                row[5] or 0.0,  # opportunity_score
                row[6] or 0,    # blocking_opportunities
                row[7] or 0,    # scoring_opportunities
                row[8] or 0,    # floor_line_risks
                row[9] or 0.0   # strategic_value
            ]
            
            features.append(feature_vector)
            targets.append(row[10])  # quality_score
        
        X = np.array(features)
        y = np.array(targets)
        
        print(f"✅ Prepared {len(X)} training samples")
        return X, y
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, MLModel]:
        """Train multiple ML models on the data."""
        if not ML_AVAILABLE:
            print("❌ Machine learning libraries not available!")
            return {}
        
        print("🤖 Training ML models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        if 'xgboost' in globals():
            models['xgboost'] = xgb.XGBRegressor(n_estimators=100, random_state=42)
        
        trained_models = {}
        
        for model_name, model in models.items():
            print(f"  Training {model_name}...")
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Get feature importance
                feature_names = [
                    'neural_score', 'pattern_score', 'strategic_score', 'tactical_score',
                    'risk_score', 'opportunity_score', 'blocking_opportunities',
                    'scoring_opportunities', 'floor_line_risks', 'strategic_value'
                ]
                
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(feature_names, model.feature_importances_))
                else:
                    feature_importance = dict(zip(feature_names, [0.1] * len(feature_names)))
                
                # Save model
                model_id = f"{model_name}_{int(datetime.now().timestamp())}"
                model_path = f"../models/{model_id}.joblib"
                os.makedirs("../models", exist_ok=True)
                joblib.dump(model, model_path)
                
                # Create MLModel object
                ml_model = MLModel(
                    model_id=model_id,
                    model_type=model_name,
                    model_path=model_path,
                    training_data_size=len(X_train),
                    accuracy_score=r2,
                    feature_importance=feature_importance,
                    created_at=datetime.now(),
                    metadata={
                        'mse': mse,
                        'r2_score': r2,
                        'test_size': len(X_test)
                    }
                )
                
                trained_models[model_name] = ml_model
                self.models[model_name] = model
                
                print(f"    ✅ {model_name}: R² = {r2:.3f}, MSE = {mse:.3f}")
                
            except Exception as e:
                print(f"    ❌ Error training {model_name}: {e}")
        
        # Save models to database
        for model in trained_models.values():
            self._save_model(model)
        
        return trained_models
    
    def predict_move_quality(self, position_fen: str, move_data: Dict[str, Any], 
                           model_name: str = 'random_forest') -> Optional[PredictionResult]:
        """Predict move quality for a given position and move."""
        if model_name not in self.models:
            print(f"❌ Model {model_name} not found!")
            return None
        
        try:
            # Extract features from the position and move
            features = self._extract_features(position_fen, move_data)
            
            if features is None:
                return None
            
            # Make prediction
            model = self.models[model_name]
            predicted_quality = model.predict([features])[0]
            
            # Calculate confidence (simplified)
            confidence = 0.8  # Could be enhanced with uncertainty estimation
            
            # Create prediction result
            prediction = PredictionResult(
                position_fen=position_fen,
                move_data=move_data,
                predicted_quality=predicted_quality,
                confidence=confidence,
                feature_values=dict(zip([
                    'neural_score', 'pattern_score', 'strategic_score', 'tactical_score',
                    'risk_score', 'opportunity_score', 'blocking_opportunities',
                    'scoring_opportunities', 'floor_line_risks', 'strategic_value'
                ], features)),
                model_used=model_name,
                created_at=datetime.now()
            )
            
            # Save prediction
            self._save_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return None
    
    def _extract_features(self, position_fen: str, move_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features from position and move data."""
        try:
            # Parse position
            state = parse_fen_string(position_fen)
            if not state:
                return None
            
            # Use existing analysis engine to get features
            assessor = AzulMoveQualityAssessor()
            move_analyses = assessor.analyze_position(state, 0)
            
            # Find the specific move
            for analysis in move_analyses:
                if self._matches_move(analysis.move_data, move_data):
                    # Extract features from the analysis
                    features = [
                        getattr(analysis.neural_analysis, 'best_score', 0.0) if analysis.neural_analysis else 0.0,
                        analysis.pattern_analysis.strategic_value,
                        analysis.pattern_analysis.strategic_value,  # strategic_score
                        analysis.pattern_analysis.strategic_value,  # tactical_score
                        1.0 - analysis.pattern_analysis.strategic_value,  # risk_score
                        analysis.pattern_analysis.strategic_value * 0.1,  # opportunity_score
                        analysis.pattern_analysis.blocking_opportunities,
                        analysis.pattern_analysis.scoring_opportunities,
                        analysis.pattern_analysis.floor_line_risks,
                        analysis.pattern_analysis.strategic_value
                    ]
                    return np.array(features)
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting features: {e}")
            return None
    
    def _matches_move(self, analysis_move: Dict[str, Any], move_data: Dict[str, Any]) -> bool:
        """Check if analysis move matches move data."""
        return (analysis_move.get('move_type') == move_data.get('move_type') and
                analysis_move.get('tile_color') == move_data.get('tile_color'))
    
    def _save_model(self, model: MLModel):
        """Save model to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO ml_models
                (model_id, model_type, model_path, training_data_size, accuracy_score,
                 feature_importance, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model.model_id,
                model.model_type,
                model.model_path,
                model.training_data_size,
                model.accuracy_score,
                json.dumps(model.feature_importance),
                model.created_at.isoformat(),
                json.dumps(model.metadata)
            ))
    
    def _save_prediction(self, prediction: PredictionResult):
        """Save prediction to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO ml_predictions
                (position_fen, move_data, predicted_quality, confidence,
                 feature_values, model_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.position_fen,
                json.dumps(prediction.move_data),
                prediction.predicted_quality,
                prediction.confidence,
                json.dumps(prediction.feature_values),
                prediction.model_used,
                prediction.created_at.isoformat()
            ))
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get performance statistics for all models."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT model_type, AVG(accuracy_score) as avg_accuracy,
                       COUNT(*) as model_count, MAX(created_at) as latest_training
                FROM ml_models
                GROUP BY model_type
                ORDER BY avg_accuracy DESC
            """)
            
            performance = {}
            for row in cursor.fetchall():
                performance[row[0]] = {
                    'avg_accuracy': row[1],
                    'model_count': row[2],
                    'latest_training': row[3]
                }
            
            return performance
    
    def generate_insights(self) -> List[str]:
        """Generate insights from ML models and predictions."""
        insights = []
        
        # Get model performance
        performance = self.get_model_performance()
        
        if performance:
            best_model = max(performance.items(), key=lambda x: x[1]['avg_accuracy'])
            insights.append(f"Best performing model: {best_model[0]} (R² = {best_model[1]['avg_accuracy']:.3f})")
        
        # Get prediction statistics
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as total_predictions,
                       AVG(predicted_quality) as avg_predicted_quality,
                       AVG(confidence) as avg_confidence
                FROM ml_predictions
            """)
            
            row = cursor.fetchone()
            if row and row[0] > 0:
                insights.append(f"Total predictions: {row[0]}")
                insights.append(f"Average predicted quality: {row[1]:.1f}")
                insights.append(f"Average confidence: {row[2]:.1f}")
        
        return insights

def main():
    """Main function to demonstrate ML integration."""
    print("🤖 Machine Learning Integration for Move Quality")
    print("=" * 50)
    
    if not ML_AVAILABLE:
        print("❌ Machine learning libraries not available!")
        print("Install with: pip install scikit-learn xgboost")
        return
    
    ml_system = MoveQualityML()
    
    # Prepare training data
    X, y = ml_system.prepare_training_data(500)
    
    if len(X) == 0:
        print("❌ No training data available!")
        return
    
    # Train models
    trained_models = ml_system.train_models(X, y)
    
    if trained_models:
        print(f"\n✅ Trained {len(trained_models)} models")
        
        # Test prediction
        print("\n🔮 Testing prediction...")
        test_position = "initial"  # Example position
        test_move = {
            'move_type': 'factory_to_pattern',
            'tile_color': 'blue',
            'row': 0
        }
        
        prediction = ml_system.predict_move_quality(test_position, test_move)
        if prediction:
            print(f"   Predicted quality: {prediction.predicted_quality:.1f}")
            print(f"   Confidence: {prediction.confidence:.1f}")
        
        # Generate insights
        print("\n💡 Generating insights...")
        insights = ml_system.generate_insights()
        for insight in insights:
            print(f"   {insight}")
    
    print("\n🎯 ML integration complete!")
    print("Next steps:")
    print("1. Collect more training data")
    print("2. Experiment with different model architectures")
    print("3. Implement ensemble methods")
    print("4. Create real-time prediction API")

if __name__ == "__main__":
    main()
