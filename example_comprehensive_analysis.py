#!/usr/bin/env python3
"""
Example: Comprehensive Move Quality Analysis

This script demonstrates how to use the comprehensive move quality analyzer
with a real Azul game position.
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

def create_sample_position():
    """Create a sample game position for analysis."""
    # Create a 2-player game
    state = AzulState(2)
    
    # Add some tiles to factories to make the position more interesting
    # Factory 0: 4 blue tiles
    state.factories[0].tiles[0] = 4  # Blue tiles
    state.factories[0].total = 4
    
    # Factory 1: 3 white tiles
    state.factories[1].tiles[1] = 3  # White tiles
    state.factories[1].total = 3
    
    # Factory 2: 2 red tiles
    state.factories[2].tiles[3] = 2  # Red tiles
    state.factories[2].total = 2
    
    # Add some tiles to center pool
    state.centre_pool.tiles[2] = 2  # Black tiles
    state.centre_pool.total = 2
    
    # Add some tiles to player 0's pattern lines
    player = state.agents[0]
    player.lines_number[0] = 1  # 1 tile in pattern line 0
    player.lines_tile[0] = 0    # Blue tile
    player.lines_number[1] = 2  # 2 tiles in pattern line 1
    player.lines_tile[1] = 1    # White tile
    
    # Add some tiles to player 0's wall
    player.grid_state[0][0] = 1  # Blue tile on wall
    player.grid_state[1][1] = 1  # White tile on wall
    
    return state

def analyze_position_comprehensive():
    """Analyze a position comprehensively."""
    print("=== Comprehensive Move Quality Analysis Example ===\n")
    
    # Create sample position
    state = create_sample_position()
    state_fen = state.to_fen()
    
    print(f"Game State FEN: {state_fen[:100]}...")
    print(f"Player 0 Score: {state.agents[0].score}")
    print(f"Player 1 Score: {state.agents[1].score}")
    print()
    
    # Initialize components
    config = ComprehensiveAnalysisConfig(
        max_workers=2,
        batch_size=20,
        max_analysis_time=15,
        enable_progress_tracking=True
    )
    
    analyzer = ComprehensiveMoveQualityAnalyzer(config)
    move_generator = EnhancedMoveGenerator(
        max_moves_per_position=50,
        enable_filtering=True
    )
    
    # Generate all possible moves
    print("Generating moves...")
    start_time = time.time()
    moves = move_generator.generate_all_moves(state, player_id=0)
    generation_time = time.time() - start_time
    
    print(f"Generated {len(moves)} moves in {generation_time:.3f}s")
    
    # Generate move summary
    move_summary = move_generator.generate_move_summary(moves)
    print(f"Move types: {move_summary['type_distribution']}")
    print(f"Priority distribution: {move_summary['priority_distribution']}")
    print()
    
    # Analyze moves
    print("Analyzing moves...")
    start_time = time.time()
    analysis_results = []
    
    for i, move in enumerate(moves):
        try:
            result = analyzer.analyze_single_move(state_fen, move.move_data)
            analysis_results.append(result)
            
            # Print top moves
            if i < 10:  # Show first 10 moves
                print(f"Move {i+1}: {move.move_type.value} "
                      f"color={move.color} target={move.target_line} "
                      f"-> {result.quality_tier.value} ({result.quality_score:.1f})")
        
        except Exception as e:
            print(f"Failed to analyze move {i+1}: {e}")
    
    analysis_time = time.time() - start_time
    print(f"Analysis completed in {analysis_time:.3f}s")
    print()
    
    # Generate analysis summary
    summary = analyzer.generate_analysis_summary(analysis_results)
    
    print("=== Analysis Summary ===")
    print(f"Total moves analyzed: {summary['total_analyses']}")
    print(f"Success rate: {summary['success_rate']:.1%}")
    print()
    
    print("Quality Score Statistics:")
    quality_stats = summary['quality_score_stats']
    print(f"  Mean: {quality_stats['mean']:.1f}")
    print(f"  Median: {quality_stats['median']:.1f}")
    print(f"  Min: {quality_stats['min']:.1f}")
    print(f"  Max: {quality_stats['max']:.1f}")
    print()
    
    print("Quality Tier Distribution:")
    tier_dist = summary['quality_tier_distribution']
    for tier, count in tier_dist.items():
        if count > 0:
            print(f"  {tier}: {count} moves")
    print()
    
    # Show best moves
    print("=== Top 5 Moves ===")
    sorted_results = sorted(analysis_results, key=lambda r: r.quality_score, reverse=True)
    
    for i, result in enumerate(sorted_results[:5]):
        move_data = result.move_data
        print(f"{i+1}. {move_data['move_type']} "
              f"color={move_data['color']} target={move_data['target_line']} "
              f"-> {result.quality_tier.value} ({result.quality_score:.1f})")
        print(f"   Strategic: {result.strategic_score:.1f}, "
              f"Pattern: {result.pattern_score:.1f}, "
              f"Risk: {result.risk_score:.1f}")
        print(f"   Reasoning: {result.strategic_reasoning[:100]}...")
        print()
    
    # Show detailed analysis of best move
    if sorted_results:
        best_move = sorted_results[0]
        print("=== Best Move Detailed Analysis ===")
        print(f"Move: {best_move.move_data}")
        print(f"Quality: {best_move.quality_tier.value} ({best_move.quality_score:.1f})")
        print(f"Strategic Score: {best_move.strategic_score:.1f}")
        print(f"Pattern Score: {best_move.pattern_score:.1f}")
        print(f"Risk Score: {best_move.risk_score:.1f}")
        print(f"Board State Impact: {best_move.board_state_impact:.1f}")
        print(f"Opponent Denial: {best_move.opponent_denial_score:.1f}")
        print(f"Timing Score: {best_move.timing_score:.1f}")
        print(f"Risk-Reward Ratio: {best_move.risk_reward_ratio:.2f}")
        print()
        print("Strategic Reasoning:")
        print(best_move.strategic_reasoning)
        print()
        print("Tactical Insights:")
        print(best_move.tactical_insights)
        print()
        print("Educational Explanation:")
        print(best_move.educational_explanation)
    
    return analysis_results

def demonstrate_api_usage():
    """Demonstrate API usage."""
    print("\n=== API Usage Example ===")
    
    # This would typically be done via HTTP requests
    # For demonstration, we'll show the expected request/response format
    
    sample_request = {
        "state_fen": "your_fen_string_here",
        "player_id": 0,
        "config_overrides": {
            "processing": {"max_workers": 4},
            "move_generation": {"max_moves_per_position": 100}
        }
    }
    
    sample_response = {
        "success": True,
        "analysis_results": [
            {
                "move_data": {"move_type": "factory_to_pattern", "color": 0, "target_line": 1},
                "quality_score": 85.0,
                "quality_tier": "!!",
                "pattern_score": 80.0,
                "strategic_score": 75.0,
                "risk_score": 30.0,
                "strategic_reasoning": "This move completes a pattern line...",
                "tactical_insights": "Strong blocking move with high strategic value",
                "educational_explanation": "This is an excellent move because..."
            }
        ],
        "summary": {
            "total_moves": 50,
            "quality_distribution": {"!!": 5, "!": 10, "=": 20, "?!": 10, "?": 5},
            "analysis_time": 25.0
        }
    }
    
    print("Sample API Request:")
    print(json.dumps(sample_request, indent=2))
    print()
    print("Sample API Response:")
    print(json.dumps(sample_response, indent=2))

def main():
    """Main function."""
    try:
        # Run comprehensive analysis
        results = analyze_position_comprehensive()
        
        # Demonstrate API usage
        demonstrate_api_usage()
        
        print("\n=== Example Completed Successfully! ===")
        print("The comprehensive analyzer is working correctly.")
        print("You can now use it for advanced move quality analysis.")
        
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 