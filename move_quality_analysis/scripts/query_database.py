#!/usr/bin/env python3
"""
Query Move Quality Database

This script queries and displays the data stored in the move quality database.
It provides various views of the data including:
- Summary statistics
- Quality tier distribution
- Sample move analyses
- Pattern analysis results
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
import json
from typing import List, Dict, Any

def query_database(db_path: str = "../data/simple_move_quality.db"):
    """Query and display the move quality database."""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Run analyze_move_quality_simple.py first!")
        return
    
    print(f"📊 Querying database: {db_path}")
    print("=" * 60)
    
    with sqlite3.connect(db_path) as conn:
        # Get total count
        cursor = conn.execute("SELECT COUNT(*) FROM move_quality_data")
        total_moves = cursor.fetchone()[0]
        print(f"📈 Total moves analyzed: {total_moves}")
        
        # Get quality tier distribution
        print("\n🏆 Quality Tier Distribution:")
        cursor = conn.execute("""
            SELECT quality_tier, COUNT(*) as count, 
                   AVG(quality_score) as avg_score,
                   MIN(quality_score) as min_score,
                   MAX(quality_score) as max_score
            FROM move_quality_data 
            GROUP BY quality_tier 
            ORDER BY avg_score DESC
        """)
        
        for row in cursor.fetchall():
            tier, count, avg_score, min_score, max_score = row
            percentage = (count / total_moves) * 100
            print(f"  {tier}: {count} moves ({percentage:.1f}%) - Score: {avg_score:.1f} ({min_score:.1f}-{max_score:.1f})")
        
        # Get pattern analysis summary
        print("\n🎯 Pattern Analysis Summary:")
        cursor = conn.execute("""
            SELECT 
                AVG(blocking_opportunities) as avg_blocking,
                AVG(scoring_opportunities) as avg_scoring,
                AVG(floor_line_risks) as avg_floor_risks,
                AVG(strategic_value) as avg_strategic_value
            FROM move_quality_data
        """)
        
        row = cursor.fetchone()
        if row:
            avg_blocking, avg_scoring, avg_floor_risks, avg_strategic = row
            print(f"  Average blocking opportunities: {avg_blocking:.2f}")
            print(f"  Average scoring opportunities: {avg_scoring:.2f}")
            print(f"  Average floor line risks: {avg_floor_risks:.2f}")
            print(f"  Average strategic value: {avg_strategic:.2f}")
        
        # Get game phase distribution
        print("\n🎮 Game Phase Distribution:")
        cursor = conn.execute("""
            SELECT game_phase, COUNT(*) as count
            FROM move_quality_data 
            GROUP BY game_phase 
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            phase, count = row
            percentage = (count / total_moves) * 100
            print(f"  {phase}: {count} moves ({percentage:.1f}%)")
        
        # Show sample moves from each quality tier
        print("\n📋 Sample Moves by Quality Tier:")
        for tier in ["!!", "!", "=", "?!", "?"]:
            cursor = conn.execute("""
                SELECT position_fen, neural_score, strategic_reasoning, 
                       blocking_opportunities, scoring_opportunities, floor_line_risks,
                       quality_score, educational_explanation
                FROM move_quality_data 
                WHERE quality_tier = ? 
                ORDER BY quality_score DESC 
                LIMIT 2
            """, (tier,))
            
            rows = cursor.fetchall()
            if rows:
                print(f"\n  {tier} Tier Examples:")
                for i, row in enumerate(rows, 1):
                    fen, neural_score, reasoning, blocking, scoring, floor_risks, quality_score, explanation = row
                    print(f"    {i}. Score: {quality_score:.1f} | Neural: {neural_score:.1f}")
                    print(f"       Blocking: {blocking}, Scoring: {scoring}, Floor Risks: {floor_risks}")
                    print(f"       Reasoning: {reasoning[:100]}...")
        
        # Show top moves by quality score
        print("\n🥇 Top 10 Moves by Quality Score:")
        cursor = conn.execute("""
            SELECT quality_tier, quality_score, neural_score, strategic_reasoning,
                   blocking_opportunities, scoring_opportunities, floor_line_risks
            FROM move_quality_data 
            ORDER BY quality_score DESC 
            LIMIT 10
        """)
        
        for i, row in enumerate(cursor.fetchall(), 1):
            tier, quality_score, neural_score, reasoning, blocking, scoring, floor_risks = row
            print(f"  {i}. {tier} (Score: {quality_score:.1f}) | Neural: {neural_score:.1f}")
            print(f"     Blocking: {blocking}, Scoring: {scoring}, Floor Risks: {floor_risks}")
            print(f"     Reasoning: {reasoning[:80]}...")
        
        # Show complexity analysis
        print("\n🧮 Complexity Analysis:")
        cursor = conn.execute("""
            SELECT 
                AVG(complexity_score) as avg_complexity,
                MIN(complexity_score) as min_complexity,
                MAX(complexity_score) as max_complexity
            FROM move_quality_data
        """)
        
        row = cursor.fetchone()
        if row:
            avg_comp, min_comp, max_comp = row
            print(f"  Average complexity: {avg_comp:.3f}")
            print(f"  Complexity range: {min_comp:.3f} - {max_comp:.3f}")
        
        # Show correlation between neural score and quality score
        print("\n🔗 Neural Score vs Quality Score Correlation:")
        cursor = conn.execute("""
            SELECT 
                AVG(neural_score) as avg_neural,
                AVG(quality_score) as avg_quality,
                COUNT(*) as count
            FROM move_quality_data 
            WHERE neural_score IS NOT NULL
        """)
        
        row = cursor.fetchone()
        if row:
            avg_neural, avg_quality, count = row
            print(f"  Average neural score: {avg_neural:.2f}")
            print(f"  Average quality score: {avg_quality:.2f}")
            print(f"  Moves with neural analysis: {count}")

def main():
    """Main function to query the database."""
    query_database()

if __name__ == "__main__":
    main()
