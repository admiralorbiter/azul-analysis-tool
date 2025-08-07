#!/usr/bin/env python3
"""
Test Comprehensive Analyzer

This script tests the comprehensive move quality analyzer to ensure it integrates
correctly with the existing infrastructure.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import json
import time
from core.azul_model import AzulState
from move_quality_analysis.scripts.comprehensive_move_quality_analyzer import (
    ComprehensiveMoveQualityAnalyzer, ComprehensiveAnalysisConfig
)
from move_quality_analysis.scripts.enhanced_move_generator import (
    EnhancedMoveGenerator
)
from move_quality_analysis.scripts.analysis_config import ConfigurationManager

def test_basic_functionality():
    """Test basic functionality of the comprehensive analyzer."""
    print("Testing comprehensive analyzer...")
    
    # Create a simple game state
    state = AzulState(2)  # 2-player game
    
    # Initialize components
    config = ComprehensiveAnalysisConfig(
        max_workers=2,
        batch_size=10,
        max_analysis_time=10,
        enable_progress_tracking=True
    )
    
    analyzer = ComprehensiveMoveQualityAnalyzer(config)
    move_generator = EnhancedMoveGenerator(max_moves_per_position=20, enable_filtering=True)
    
    # Generate moves
    print("Generating moves...")
    moves = move_generator.generate_all_moves(state, 0)
    print(f"Generated {len(moves)} moves")
    
    # Test move generation summary
    summary = move_generator.generate_move_summary(moves)
    print(f"Move summary: {json.dumps(summary, indent=2)}")
    
    # Test analyzing a few moves
    print("Analyzing moves...")
    state_fen = state.to_fen()
    analysis_results = []
    
    for i, move in enumerate(moves[:5]):  # Test first 5 moves
        try:
            result = analyzer.analyze_single_move(state_fen, move.move_data)
            analysis_results.append(result)
            print(f"Analyzed move {i+1}: {result.quality_tier.value} ({result.quality_score:.1f})")
        except Exception as e:
            print(f"Failed to analyze move {i+1}: {e}")
    
    # Test analysis summary
    if analysis_results:
        summary = analyzer.generate_analysis_summary(analysis_results)
        print(f"Analysis summary: {json.dumps(summary, indent=2)}")
    
    print("Basic functionality test completed!")

def test_configuration_system():
    """Test the configuration system."""
    print("\nTesting configuration system...")
    
    # Create configuration manager
    manager = ConfigurationManager()
    
    # Test loading default configuration
    config = manager.load_configuration()
    print(f"Loaded configuration with {config.processing.max_workers} workers")
    
    # Test configuration presets
    presets = manager.get_mode_presets()
    for mode, preset_config in presets.items():
        print(f"{mode} mode: {preset_config.processing.max_workers} workers, "
              f"{preset_config.processing.max_analysis_time}s max time")
    
    print("Configuration system test completed!")

def test_api_integration():
    """Test API integration."""
    print("\nTesting API integration...")
    
    # Import the API route
    try:
        from api.routes.comprehensive_analysis import comprehensive_analysis_bp
        print("✓ Comprehensive analysis blueprint imported successfully")
        
        # Test the blueprint registration
        from api.app import create_app
        app = create_app()
        print("✓ Flask app created with comprehensive analysis routes")
        
        # Test configuration endpoint
        with app.test_client() as client:
            response = client.get('/api/v1/config')
            if response.status_code == 200:
                print("✓ Configuration endpoint working")
            else:
                print(f"✗ Configuration endpoint failed: {response.status_code}")
        
    except Exception as e:
        print(f"✗ API integration test failed: {e}")
    
    print("API integration test completed!")

def test_database_integration():
    """Test database integration."""
    print("\nTesting database integration...")
    
    try:
        # Create analyzer with database
        config = ComprehensiveAnalysisConfig(
            save_intermediate_results=True,
            generate_detailed_reports=True
        )
        
        analyzer = ComprehensiveMoveQualityAnalyzer(config)
        
        # Create a test state and analyze a move
        state = AzulState(2)
        state_fen = state.to_fen()
        
        test_move = {
            'move_type': 'factory_to_pattern',
            'factory_id': 0,
            'color': 0,
            'count': 4,
            'target_line': 1
        }
        
        result = analyzer.analyze_single_move(state_fen, test_move)
        
        # Check if database was created
        db_path = "../data/comprehensive_analysis_results.db"
        if os.path.exists(db_path):
            print("✓ Database created successfully")
        else:
            print("✗ Database not created")
        
    except Exception as e:
        print(f"✗ Database integration test failed: {e}")
    
    print("Database integration test completed!")

def main():
    """Run all tests."""
    print("=== Comprehensive Analyzer Test Suite ===\n")
    
    # Create necessary directories
    os.makedirs("../data", exist_ok=True)
    os.makedirs("../logs", exist_ok=True)
    os.makedirs("../config", exist_ok=True)
    
    # Run tests
    test_basic_functionality()
    test_configuration_system()
    test_api_integration()
    test_database_integration()
    
    print("\n=== All tests completed! ===")

if __name__ == "__main__":
    main() 