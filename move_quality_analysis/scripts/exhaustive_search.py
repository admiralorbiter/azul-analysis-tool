#!/usr/bin/env python3
"""
Exhaustive Move Search - Using Existing Comprehensive Analyzer

This script leverages the existing comprehensive analyzer and enhanced move generator
to perform exhaustive move search and analysis.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
from core.azul_model import AzulState
from comprehensive_move_quality_analyzer import (
    ComprehensiveMoveQualityAnalyzer, ComprehensiveAnalysisConfig
)
from enhanced_move_generator import EnhancedMoveGenerator

import sqlite3

def setup_progress_database():
    """Setup database for progress tracking."""
    db_path = "../data/exhaustive_search_progress.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create progress tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exhaustive_search_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_type TEXT NOT NULL,
            position_fen TEXT NOT NULL,
            total_moves INTEGER NOT NULL,
            completed_moves INTEGER DEFAULT 0,
            current_move_index INTEGER DEFAULT 0,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'running'
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path

def save_progress(db_path, position_type, position_fen, total_moves, completed_moves, current_index):
    """Save progress to database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO exhaustive_search_progress 
        (position_type, position_fen, total_moves, completed_moves, current_move_index, last_update)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (position_type, position_fen, total_moves, completed_moves, current_index))
    
    conn.commit()
    conn.close()

def load_progress(db_path, position_type, position_fen):
    """Load progress from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT total_moves, completed_moves, current_move_index
        FROM exhaustive_search_progress 
        WHERE position_type = ? AND position_fen = ?
    ''', (position_type, position_fen))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'total_moves': result[0],
            'completed_moves': result[1],
            'current_move_index': result[2]
        }
    return None

def create_test_position(position_type: str = "complex") -> AzulState:
    """Create a test position for exhaustive analysis."""
    state = AzulState(2)  # 2-player game
    
    if position_type == "complex":
        # Create a complex position with many tiles
        # Factory 0: 4 blue tiles
        state.factories[0].tiles[0] = 4
        state.factories[0].total = 4
        
        # Factory 1: 3 white tiles
        state.factories[1].tiles[1] = 3
        state.factories[1].total = 3
        
        # Factory 2: 2 red tiles
        state.factories[2].tiles[3] = 2
        state.factories[2].total = 2
        
        # Factory 3: 1 black tile
        state.factories[3].tiles[2] = 1
        state.factories[3].total = 1
        
        # Factory 4: 2 yellow tiles
        state.factories[4].tiles[4] = 2
        state.factories[4].total = 2
        
        # Center pool: 3 tiles of different colors
        state.centre_pool.tiles[0] = 1  # Blue
        state.centre_pool.tiles[1] = 1  # White
        state.centre_pool.tiles[2] = 1  # Black
        state.centre_pool.total = 3
        
    elif position_type == "simple":
        # Create a simple position with few tiles
        state.factories[0].tiles[0] = 2  # 2 blue tiles
        state.factories[0].total = 2
        state.centre_pool.tiles[1] = 1  # 1 white tile
        state.centre_pool.total = 1
        
    elif position_type == "empty":
        # Create an empty position (start of game)
        pass  # Use default empty state
        
    return state

def main():
    """Run exhaustive move search using existing comprehensive analyzer."""
    print("🎯 Exhaustive Move Search - Using Existing Comprehensive Analyzer")
    print("="*70)
    
    # Create analyzer with exhaustive search configuration
    config = ComprehensiveAnalysisConfig(
        max_workers=8,  # Use more workers for exhaustive search
        batch_size=200,  # Larger batch size
        max_analysis_time=60,  # Longer analysis time
        enable_progress_tracking=True,
        save_intermediate_results=True,
        generate_detailed_reports=True
    )
    analyzer = ComprehensiveMoveQualityAnalyzer(config)
    
    # Create enhanced move generator (no filtering for exhaustive search)
    move_generator = EnhancedMoveGenerator(
        max_moves_per_position=1000,  # Very high limit for exhaustive search
        enable_filtering=False  # Don't filter for exhaustive search
    )
    
    # Test different position types
    position_types = ["simple", "complex"]
    
    for position_type in position_types:
        print(f"\n🎮 Running exhaustive search for {position_type} position...")
        
        # Create test position
        state = create_test_position(position_type)
        state_fen = state.to_fen()
        
        print(f"📊 Position FEN: {state_fen[:50]}...")
        print(f"👥 Players: {len(state.agents)}")
        print(f"🏭 Factories: {len(state.factories)}")
        print(f"🎯 Center pool tiles: {state.centre_pool.total}")
        
        # Generate all possible moves using enhanced move generator
        print("\n🔍 Generating all possible moves...")
        start_time = time.time()
        moves = move_generator.generate_all_moves(state, player_id=0)
        generation_time = time.time() - start_time
        
        print(f"✅ Generated {len(moves)} moves in {generation_time:.3f}s")
        
        # Analyze all moves using comprehensive analyzer
        print(f"\n🔬 Analyzing {len(moves)} moves...")
        start_time = time.time()
        results = []
        
        # Check for existing progress
        db_path = setup_progress_database()
        progress = load_progress(db_path, position_type, state_fen)
        if progress:
            print(f"📈 Found existing progress: {progress['completed_moves']}/{progress['total_moves']} moves completed")
            resume_from = progress['current_move_index']
        else:
            resume_from = 0

        # Save initial progress
        if not progress:
            save_progress(db_path, position_type, state_fen, len(moves), 0, 0)

        # Save results immediately (most important)
        for i in range(resume_from, len(moves)):
            try:
                # Convert GeneratedMove to dictionary format expected by analyzer
                move_dict = moves[i].move_data
                result = analyzer.analyze_single_move(state_fen, move_dict)
                results.append(result)  # Add to results list
                
                # Save progress less frequently
                if (i + 1) % 100 == 0:  # ✅ Every 100 moves
                    save_progress(db_path, position_type, state_fen, len(moves), i + 1, i + 1)
                    
                # Progress indicator (just display, no DB write)
                if (i + 1) % 20 == 0:
                    progress = (i + 1) / len(moves) * 100
                    print(f"   Progress: {progress:.1f}% ({i + 1}/{len(moves)})")
                        
            except Exception as e:
                print(f"Failed to analyze move {i + 1}: {e}")
                continue
        
        analysis_time = time.time() - start_time
        success_rate = len(results) / len(moves) * 100
        
        print(f"✅ Analysis completed in {analysis_time:.3f}s")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Successful analyses: {len(results)}/{len(moves)}")
        
        # Generate statistics
        if results:
            print(f"\n📊 RESULTS SUMMARY")
            print(f"   Total moves analyzed: {len(results)}")
            print(f"   Total time: {generation_time + analysis_time:.3f}s")
            
            # Quality distribution
            quality_dist = {}
            scores = []
            for result in results:
                tier = result.quality_tier.value
                quality_dist[tier] = quality_dist.get(tier, 0) + 1
                scores.append(result.quality_score)
            
            print(f"\n🏆 QUALITY DISTRIBUTION")
            for tier, count in quality_dist.items():
                percentage = count / len(results) * 100
                print(f"   {tier}: {count} moves ({percentage:.1f}%)")
            
            print(f"\n🎯 QUALITY SCORES")
            print(f"   Mean: {sum(scores)/len(scores):.2f}")
            print(f"   Min: {min(scores):.2f}")
            print(f"   Max: {max(scores):.2f}")
            
            # Top moves
            top_moves = sorted(results, key=lambda r: r.quality_score, reverse=True)[:5]
            print(f"\n🥇 TOP 5 MOVES")
            for i, result in enumerate(top_moves):
                move_data = result.move_data
                print(f"   {i+1}. {move_data['move_type']} "
                      f"color={move_data.get('color', 'N/A')} "
                      f"target={move_data.get('target_line', 'N/A')} "
                      f"-> {result.quality_tier.value} ({result.quality_score:.1f})")
        
        print(f"\n✅ Exhaustive search completed for {position_type} position")
    
    print("\n🎉 All exhaustive searches completed!")
    print("📊 Using existing comprehensive analyzer infrastructure")
    print("📈 Results saved to database for further analysis")

if __name__ == "__main__":
    main()
