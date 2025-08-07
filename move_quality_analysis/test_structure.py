#!/usr/bin/env python3
"""
Test script to verify the move quality analysis structure works correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_structure():
    """Test that the new structure is working correctly."""
    print("🧪 Testing Move Quality Analysis Structure")
    print("=" * 50)
    
    # Test 1: Check if scripts exist
    print("\n1. Checking script files...")
    scripts_dir = Path(__file__).parent / "scripts"
    expected_scripts = ["analyze_moves.py", "generate_positions.py", "query_database.py"]
    
    for script in expected_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"   ✅ {script} exists")
        else:
            print(f"   ❌ {script} missing")
    
    # Test 2: Check if data files exist
    print("\n2. Checking data files...")
    data_dir = Path(__file__).parent / "data"
    expected_data = ["simple_move_quality.db", "diverse_positions_simple.json"]
    
    for data_file in expected_data:
        data_path = data_dir / data_file
        if data_path.exists():
            print(f"   ✅ {data_file} exists")
        else:
            print(f"   ❌ {data_file} missing")
    
    # Test 3: Check if docs exist
    print("\n3. Checking documentation...")
    docs_dir = Path(__file__).parent / "docs"
    if (docs_dir / "SCRIPTS_README.md").exists():
        print("   ✅ SCRIPTS_README.md exists")
    else:
        print("   ❌ SCRIPTS_README.md missing")
    
    # Test 4: Check if legacy folder exists
    print("\n4. Checking legacy folder...")
    legacy_dir = Path(__file__).parent / "legacy"
    if legacy_dir.exists():
        legacy_files = list(legacy_dir.glob("*.py"))
        print(f"   ✅ Legacy folder exists with {len(legacy_files)} files")
    else:
        print("   ❌ Legacy folder missing")
    
    # Test 5: Test import of main analyzer
    print("\n5. Testing imports...")
    try:
        sys.path.insert(0, str(scripts_dir))
        from analyze_moves import SimpleMoveQualityAnalyzer
        print("   ✅ SimpleMoveQualityAnalyzer imports successfully")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
    
    print("\n🎉 Structure test completed!")
    print("\n📋 Next steps:")
    print("   1. cd move_quality_analysis/scripts")
    print("   2. python generate_positions.py")
    print("   3. python analyze_moves.py")
    print("   4. python query_database.py")

if __name__ == "__main__":
    test_structure()
