#!/usr/bin/env python3
"""
Simple test for neural integration.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_neural_imports():
    """Test that all neural modules can be imported."""
    print("=== Neural Integration Import Test ===")
    
    try:
        # Test basic neural imports
        from neural.azul_net import AzulNetConfig, AzulNet, AzulTensorEncoder, create_azul_net
        print("✅ Basic neural imports: PASSED")
        
        # Test move encoding
        from neural.move_encoding import MoveEncoder
        print("✅ Move encoding import: PASSED")
        
        # Test policy mapping
        from neural.policy_mapping import PolicyMapper
        print("✅ Policy mapping import: PASSED")
        
        # Test batch evaluator
        from neural.batch_evaluator import BatchNeuralEvaluator, BatchConfig
        print("✅ Batch evaluator import: PASSED")
        
        # Test RTX optimizer
        from neural.gpu_optimizer import RTX30xxOptimizer, GPUOptimizationConfig
        print("✅ RTX optimizer import: PASSED")
        
        # Test model evaluation
        from neural.model_evaluation import NeuralModelEvaluator, EvaluationConfig
        print("✅ Model evaluation import: PASSED")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_neural_creation():
    """Test that neural components can be created."""
    print("\n=== Neural Component Creation Test ===")
    
    try:
        # Test model creation
        from neural.azul_net import create_azul_net
        model, encoder = create_azul_net()
        print(f"✅ Model created: {sum(p.numel() for p in model.parameters())} parameters")
        
        # Test move encoder
        from neural.move_encoding import MoveEncoder
        move_encoder = MoveEncoder()
        print(f"✅ Move encoder created: {move_encoder.get_move_space_size()} move space")
        
        # Test policy mapper
        from neural.policy_mapping import PolicyMapper
        policy_mapper = PolicyMapper()
        print("✅ Policy mapper created")
        
        # Test batch evaluator
        from neural.batch_evaluator import BatchNeuralEvaluator, BatchConfig
        config = BatchConfig(default_batch_size=4)
        batch_evaluator = BatchNeuralEvaluator(model, encoder, config)
        print(f"✅ Batch evaluator created: {batch_evaluator.device}")
        
        # Test RTX optimizer
        from neural.gpu_optimizer import RTX30xxOptimizer
        rtx_optimizer = RTX30xxOptimizer()
        print(f"✅ RTX optimizer created: {rtx_optimizer.device}")
        
        return True
        
    except Exception as e:
        print(f"❌ Creation failed: {e}")
        return False

def test_neural_functionality():
    """Test basic neural functionality."""
    print("\n=== Neural Functionality Test ===")
    
    try:
        from core.azul_model import AzulState
        from neural.azul_net import create_azul_net
        from neural.batch_evaluator import BatchNeuralEvaluator, BatchConfig
        
        # Create components
        model, encoder = create_azul_net()
        config = BatchConfig(default_batch_size=2)
        evaluator = BatchNeuralEvaluator(model, encoder, config)
        
        # Create test state
        state = AzulState(2)
        test_states = [state]
        test_agent_ids = [0]
        
        # Test batch evaluation
        scores = evaluator.evaluate_batch(test_states, test_agent_ids)
        print(f"✅ Batch evaluation: {len(scores)} scores generated")
        print(f"   Average score: {sum(scores)/len(scores):.3f}")
        
        # Test performance stats
        stats = evaluator.get_performance_stats()
        print(f"✅ Performance stats: {len(stats)} metrics tracked")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all neural tests."""
    print("🧠 NEURAL INTEGRATION SIMPLE TEST")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Import Test", test_neural_imports),
        ("Creation Test", test_neural_creation),
        ("Functionality Test", test_neural_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📋 SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Neural integration is working correctly.")
        print("\n📚 Next Steps:")
        print("1. Run comprehensive tests: python -m pytest tests/test_*neural*.py -v")
        print("2. Test GPU optimization: python -c \"from neural.gpu_optimizer import RTX30xxOptimizer; print(RTX30xxOptimizer().device)\"")
        print("3. Test batch inference: python -m pytest tests/test_batch_inference.py -v")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Check that all dependencies are installed: pip install torch numpy")
        print("2. Verify Python path includes project root")
        print("3. Check for import errors in neural modules")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 