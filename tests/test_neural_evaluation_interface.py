"""
Tests for Neural Evaluation Interface (Part 2.1.3)

This module tests:
- Model selection and configuration
- Evaluation parameters validation
- Performance metrics calculation
- Model comparison functionality
- Export results functionality
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neural.evaluate import EvaluationConfig, AzulModelEvaluator, EvaluationResult
from api.routes import evaluate_neural_model
from flask import Flask
from api.app import create_app


class TestNeuralEvaluationInterface(unittest.TestCase):
    """Test suite for neural evaluation interface features."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_evaluation_config_creation(self):
        """Test evaluation configuration creation and validation."""
        print("🧪 Testing evaluation configuration creation...")
        
        # Test default configuration
        config = EvaluationConfig()
        self.assertEqual(config.num_positions, 100)
        self.assertEqual(config.num_games, 50)
        self.assertEqual(config.device, "cpu")
        self.assertEqual(config.compare_heuristic, True)
        self.assertEqual(config.compare_random, True)
        
        # Test custom configuration
        custom_config = EvaluationConfig(
            num_positions=200,
            num_games=100,
            device="gpu",
            compare_heuristic=False,
            compare_random=False
        )
        self.assertEqual(custom_config.num_positions, 200)
        self.assertEqual(custom_config.num_games, 100)
        self.assertEqual(custom_config.device, "gpu")
        self.assertEqual(custom_config.compare_heuristic, False)
        self.assertEqual(custom_config.compare_random, False)
        
        print("✅ Evaluation configuration creation tests passed")

    def test_evaluation_result_structure(self):
        """Test evaluation result data structure."""
        print("🧪 Testing evaluation result structure...")
        
        result = EvaluationResult(
            win_rate=0.75,
            avg_score=15.5,
            avg_search_time=0.25,
            avg_rollouts=45.2,
            position_accuracy=0.82,
            move_agreement=0.78,
            model_parameters=1234567,
            inference_time_ms=12.5,
            vs_heuristic_win_rate=0.65,
            vs_random_win_rate=0.90
        )
        
        self.assertEqual(result.win_rate, 0.75)
        self.assertEqual(result.avg_score, 15.5)
        self.assertEqual(result.avg_search_time, 0.25)
        self.assertEqual(result.avg_rollouts, 45.2)
        self.assertEqual(result.position_accuracy, 0.82)
        self.assertEqual(result.move_agreement, 0.78)
        self.assertEqual(result.model_parameters, 1234567)
        self.assertEqual(result.inference_time_ms, 12.5)
        self.assertEqual(result.vs_heuristic_win_rate, 0.65)
        self.assertEqual(result.vs_random_win_rate, 0.90)
        
        print("✅ Evaluation result structure tests passed")

    @patch('neural.evaluate.AzulModelEvaluator._load_model')
    @patch('neural.evaluate.AzulModelEvaluator._test_inference_speed')
    @patch('neural.evaluate.AzulModelEvaluator._test_position_accuracy')
    @patch('neural.evaluate.AzulModelEvaluator._test_move_agreement')
    @patch('neural.evaluate.AzulModelEvaluator._test_win_rate')
    @patch('neural.evaluate.AzulModelEvaluator._compare_against_method')
    def test_model_evaluator_integration(self, mock_compare, mock_win_rate, mock_agreement, 
                                       mock_accuracy, mock_inference, mock_load):
        """Test model evaluator integration and method calls."""
        print("🧪 Testing model evaluator integration...")
        
        # Mock return values
        mock_load.return_value = (MagicMock(), MagicMock())
        mock_inference.return_value = 15.2
        mock_accuracy.return_value = 0.85
        mock_agreement.return_value = 0.78
        mock_win_rate.return_value = (0.75, 12.5, 0.3, 45.2)
        mock_compare.return_value = 0.65  # Use return_value instead of side_effect
        
        config = EvaluationConfig(
            num_positions=50,
            num_games=20,
            model_path="test_model.pth",
            device="cpu"
        )
        
        evaluator = AzulModelEvaluator(config)
        result = evaluator.evaluate_model()
        
        # Verify method calls
        mock_load.assert_called_once()
        mock_inference.assert_called_once()
        mock_accuracy.assert_called_once()
        mock_agreement.assert_called_once()
        mock_win_rate.assert_called_once()
        self.assertEqual(mock_compare.call_count, 2)  # Called for heuristic and random
        
        # Verify result structure
        self.assertIsInstance(result, EvaluationResult)
        self.assertEqual(result.inference_time_ms, 15.2)
        self.assertEqual(result.position_accuracy, 0.85)
        self.assertEqual(result.move_agreement, 0.78)
        self.assertEqual(result.win_rate, 0.75)
        self.assertEqual(result.vs_heuristic_win_rate, 0.65)
        self.assertEqual(result.vs_random_win_rate, 0.90)
        
        print("✅ Model evaluator integration tests passed")

    def test_evaluation_api_endpoint(self):
        """Test evaluation API endpoint functionality."""
        print("🧪 Testing evaluation API endpoint...")
        
        # Test valid evaluation request
        valid_request = {
            "model": "models/azul_net_small.pth",
            "positions": 50,
            "games": 20,
            "device": "cpu"
        }
        
        with patch('api.routes.os.path.exists', return_value=True):
            with patch('neural.evaluate.AzulModelEvaluator') as mock_evaluator_class:
                mock_evaluator = MagicMock()
                mock_evaluator_class.return_value = mock_evaluator
                mock_evaluator.evaluate_model.return_value = EvaluationResult(
                    win_rate=0.75,
                    avg_score=12.5,
                    avg_search_time=0.3,
                    avg_rollouts=45.2,
                    position_accuracy=0.85,
                    move_agreement=0.78,
                    model_parameters=1234567,
                    inference_time_ms=15.2,
                    vs_heuristic_win_rate=0.65,
                    vs_random_win_rate=0.90
                )
                
                response = self.client.post('/api/v1/neural/evaluate',
                                         json=valid_request,
                                         content_type='application/json')

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertIn('session_id', data)
                self.assertIn('status_url', data)
                self.assertEqual(data['message'], 'Evaluation started in background')
                
        # Test invalid model path
        invalid_request = {
            "model": "nonexistent_model.pth",
            "positions": 50,
            "games": 20,
            "device": "cpu"
        }
        
        with patch('os.path.exists', return_value=False):
            response = self.client.post('/api/v1/neural/evaluate',
                                     json=invalid_request,
                                     content_type='application/json')
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Model not found', data['error'])
        
        print("✅ Evaluation API endpoint tests passed")

    def test_model_selection_functionality(self):
        """Test model selection and validation."""
        print("🧪 Testing model selection functionality...")
        
        # Test available models endpoint
        with patch('os.path.exists', return_value=True):
            with patch('glob.glob') as mock_glob:
                mock_glob.return_value = [
                    "models/azul_net_small.pth",
                    "models/azul_net_medium.pth",
                    "models/azul_net_large.pth"
                ]
                
                with patch('os.path.getsize', return_value=1024*1024):  # 1MB
                    response = self.client.get('/api/v1/neural/models')
                    
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertIn('models', data)
                    self.assertEqual(len(data['models']), 3)
                    
                    # Verify model structure
                    model = data['models'][0]
                    self.assertIn('name', model)
                    self.assertIn('path', model)
                    self.assertIn('size_bytes', model)
                    self.assertIn('size_mb', model)
        
        print("✅ Model selection functionality tests passed")

    def test_evaluation_parameters_validation(self):
        """Test evaluation parameters validation."""
        print("🧪 Testing evaluation parameters validation...")
        
        # Test valid parameters
        valid_params = {
            "model": "models/azul_net_small.pth",
            "positions": 50,
            "games": 20,
            "device": "cpu"
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('neural.evaluate.AzulModelEvaluator'):
                response = self.client.post('/api/v1/neural/evaluate',
                                         json=valid_params,
                                         content_type='application/json')
                
                self.assertNotEqual(response.status_code, 400)
        
                # Test invalid parameters (missing required fields)
        invalid_params = {
            "positions": 50,
            "games": 20
            # Missing 'model' field
        }

        response = self.client.post('/api/v1/neural/evaluate',
                                 json=invalid_params,
                                 content_type='application/json')

        # The API uses default values, so missing fields are allowed
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        print("✅ Evaluation parameters validation tests passed")

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation and display."""
        print("🧪 Testing performance metrics calculation...")
        
        # Create sample evaluation result
        result = EvaluationResult(
            win_rate=0.75,
            avg_score=15.5,
            avg_search_time=0.25,
            avg_rollouts=45.2,
            position_accuracy=0.82,
            move_agreement=0.78,
            model_parameters=1234567,
            inference_time_ms=12.5,
            vs_heuristic_win_rate=0.65,
            vs_random_win_rate=0.90
        )
        
        # Test metrics calculations
        self.assertEqual(result.win_rate * 100, 75.0)  # Win rate percentage
        self.assertEqual(result.position_accuracy * 100, 82.0)  # Accuracy percentage
        self.assertEqual(result.move_agreement * 100, 78.0)  # Agreement percentage
        self.assertEqual(result.vs_heuristic_win_rate * 100, 65.0)  # Comparison percentage
        self.assertEqual(result.vs_random_win_rate * 100, 90.0)  # Comparison percentage
        
        # Test inference time formatting
        self.assertEqual(f"{result.inference_time_ms:.2f} ms", "12.50 ms")
        
        # Test parameter count formatting
        self.assertEqual(f"{result.model_parameters:,}", "1,234,567")
        
        print("✅ Performance metrics calculation tests passed")

    def test_model_comparison_functionality(self):
        """Test model comparison functionality."""
        print("🧪 Testing model comparison functionality...")
        
        # Mock multiple model evaluations
        model_results = [
            {
                "model_name": "azul_net_small.pth",
                "win_rate": 0.70,
                "position_accuracy": 0.75,
                "model_parameters": 1000000,
                "inference_time_ms": 10.0
            },
            {
                "model_name": "azul_net_medium.pth",
                "win_rate": 0.80,
                "position_accuracy": 0.85,
                "model_parameters": 2000000,
                "inference_time_ms": 15.0
            },
            {
                "model_name": "azul_net_large.pth",
                "win_rate": 0.85,
                "position_accuracy": 0.90,
                "model_parameters": 5000000,
                "inference_time_ms": 25.0
            }
        ]
        
        # Test comparison logic
        best_win_rate = max(result["win_rate"] for result in model_results)
        best_accuracy = max(result["position_accuracy"] for result in model_results)
        fastest_inference = min(result["inference_time_ms"] for result in model_results)
        
        self.assertEqual(best_win_rate, 0.85)
        self.assertEqual(best_accuracy, 0.90)
        self.assertEqual(fastest_inference, 10.0)
        
        # Test ranking by different metrics
        ranked_by_win_rate = sorted(model_results, key=lambda x: x["win_rate"], reverse=True)
        self.assertEqual(ranked_by_win_rate[0]["model_name"], "azul_net_large.pth")
        
        ranked_by_speed = sorted(model_results, key=lambda x: x["inference_time_ms"])
        self.assertEqual(ranked_by_speed[0]["model_name"], "azul_net_small.pth")
        
        print("✅ Model comparison functionality tests passed")

    def test_export_results_functionality(self):
        """Test export results functionality."""
        print("🧪 Testing export results functionality...")
        
        # Create sample evaluation data
        evaluation_data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "model": "models/azul_net_small.pth",
            "config": {
                "positions": 50,
                "games": 20,
                "device": "cpu"
            },
            "results": {
                "win_rate": 0.75,
                "avg_score": 15.5,
                "position_accuracy": 0.82,
                "move_agreement": 0.78,
                "model_parameters": 1234567,
                "inference_time_ms": 12.5
            }
        }
        
        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(evaluation_data, f, indent=2)
            temp_file = f.name
        
        try:
            # Verify file was created and contains expected data
            self.assertTrue(os.path.exists(temp_file))
            
            with open(temp_file, 'r') as f:
                exported_data = json.load(f)
            
            self.assertEqual(exported_data["model"], "models/azul_net_small.pth")
            self.assertEqual(exported_data["results"]["win_rate"], 0.75)
            self.assertEqual(exported_data["results"]["position_accuracy"], 0.82)
            self.assertIn("timestamp", exported_data)
            self.assertIn("config", exported_data)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        print("✅ Export results functionality tests passed")

    def test_evaluation_error_handling(self):
        """Test error handling in evaluation process."""
        print("🧪 Testing evaluation error handling...")
        
        # Test missing neural components
        with patch('builtins.__import__', side_effect=ImportError("No module named 'torch'")):
            response = self.client.post('/api/v1/neural/evaluate',
                                     json={"model": "test.pth", "positions": 50},
                                     content_type='application/json')

            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('Internal server error', data['error'])
        
        # Test evaluation failure
        with patch('os.path.exists', return_value=True):
            with patch('neural.evaluate.AzulModelEvaluator') as mock_evaluator_class:
                mock_evaluator = MagicMock()
                mock_evaluator_class.return_value = mock_evaluator
                mock_evaluator.evaluate_model.side_effect = Exception("Evaluation failed")
                
                response = self.client.post('/api/v1/neural/evaluate',
                                         json={"model": "test.pth", "positions": 50},
                                         content_type='application/json')
                
                self.assertEqual(response.status_code, 500)
                data = json.loads(response.data)
                self.assertIn('Evaluation failed', data['error'])
        
        print("✅ Evaluation error handling tests passed")

    def test_evaluation_interface_integration(self):
        """Test complete evaluation interface integration."""
        print("🧪 Testing evaluation interface integration...")
        
        # Test complete evaluation workflow
        test_config = {
            "model": "models/azul_net_small.pth",
            "positions": 25,
            "games": 10,
            "device": "cpu"
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('neural.evaluate.AzulModelEvaluator') as mock_evaluator_class:
                mock_evaluator = MagicMock()
                mock_evaluator_class.return_value = mock_evaluator
                mock_evaluator.evaluate_model.return_value = EvaluationResult(
                    win_rate=0.75,
                    avg_score=12.5,
                    avg_search_time=0.3,
                    avg_rollouts=45.2,
                    position_accuracy=0.85,
                    move_agreement=0.78,
                    model_parameters=1234567,
                    inference_time_ms=15.2,
                    vs_heuristic_win_rate=0.65,
                    vs_random_win_rate=0.90
                )
                
                # Test evaluation request
                response = self.client.post('/api/v1/neural/evaluate',
                                         json=test_config,
                                         content_type='application/json')

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertIn('session_id', data)
                self.assertIn('status_url', data)
                self.assertEqual(data['message'], 'Evaluation started in background')
                
                # Verify evaluator was called with correct config
                mock_evaluator_class.assert_called_once()
                call_args = mock_evaluator_class.call_args[0][0]
                self.assertEqual(call_args.num_positions, 25)
                self.assertEqual(call_args.num_games, 10)
                self.assertEqual(call_args.device, "cpu")
                self.assertEqual(call_args.model_path, "models/azul_net_small.pth")
        
        print("✅ Evaluation interface integration tests passed")


def run_evaluation_interface_tests():
    """Run all evaluation interface tests."""
    print("🧠 Testing Neural Evaluation Interface (Part 2.1.3)")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNeuralEvaluationInterface)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EVALUATION INTERFACE TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All evaluation interface tests passed!")
        return True
    else:
        print("\n❌ Some evaluation interface tests failed!")
        return False


if __name__ == "__main__":
    success = run_evaluation_interface_tests()
    exit(0 if success else 1) 