#!/usr/bin/env python3
"""
Pipeline Runner - Test the Complete Pipeline

This script runs the complete pipeline with smaller targets for testing.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipeline_orchestrator import PipelineOrchestrator, PipelineConfig

def main():
    """Run the pipeline with test configuration."""
    print("🚀 Starting Move Quality Analysis Pipeline Test")
    print("=" * 50)
    
    # Create test configuration (smaller targets for testing)
    config = PipelineConfig(
        target_positions=100,      # Reduced from 1000 for testing
        target_moves=2000,         # Reduced from 20000 for testing
        max_workers=2,             # Reduced for testing
        batch_size=25,             # Smaller batches for testing
        cache_enabled=True,
        parallel_processing=True
    )
    
    print(f"Configuration:")
    print(f"  Target positions: {config.target_positions}")
    print(f"  Target moves: {config.target_moves}")
    print(f"  Max workers: {config.max_workers}")
    print(f"  Batch size: {config.batch_size}")
    print()
    
    try:
        # Create and run pipeline
        orchestrator = PipelineOrchestrator(config)
        results = orchestrator.run_pipeline()
        
        # Print results
        print("\n" + "=" * 50)
        print("📊 Pipeline Results")
        print("=" * 50)
        
        successful_stages = sum(1 for r in results if r.status.value == "completed")
        failed_stages = sum(1 for r in results if r.status.value == "failed")
        total_duration = sum(r.duration for r in results)
        
        print(f"✅ Successful stages: {successful_stages}")
        print(f"❌ Failed stages: {failed_stages}")
        print(f"⏱️  Total duration: {total_duration:.2f} seconds")
        
        print(f"\n📋 Stage Details:")
        for result in results:
            status_icon = "✅" if result.status.value == "completed" else "❌"
            print(f"  {status_icon} {result.stage.value}: {result.duration:.2f}s")
            if result.error_message:
                print(f"     Error: {result.error_message}")
        
        if failed_stages == 0:
            print(f"\n🎉 Pipeline completed successfully!")
        else:
            print(f"\n⚠️  Pipeline completed with {failed_stages} failed stages")
            
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
