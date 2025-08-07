#!/usr/bin/env python3
"""
Enhanced Move Quality Database Development

This script provides tools to expand and enhance the move quality database with:
- Real game analysis from strong players
- Engine self-play games for validation
- Machine learning model training
- Advanced analytics and insights
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import sqlite3
import time
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator
from analysis_engine.move_quality.azul_move_quality_assessor import AzulMoveQualityAssessor

@dataclass
class GameAnalysis:
    """Data structure for analyzing complete games."""
    game_id: str
    players: List[str]
    moves: List[Dict[str, Any]]
    final_scores: List[int]
    winner: int
    analysis_data: Dict[str, Any]
    created_at: datetime

@dataclass
class EngineSelfPlayGame:
    """Data structure for engine vs engine games."""
    game_id: str
    engine_config: Dict[str, Any]
    moves: List[Dict[str, Any]]
    final_scores: List[int]
    winner: int
    quality_metrics: Dict[str, float]
    created_at: datetime

class EnhancedMoveQualityDatabase:
    """Enhanced move quality database with advanced features."""
    
    def __init__(self, db_path: str = "../data/enhanced_move_quality.db"):
        self.db_path = db_path
        self._init_enhanced_database()
        
    def _init_enhanced_database(self):
        """Initialize enhanced database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Enhanced move quality data table
                CREATE TABLE IF NOT EXISTS enhanced_move_quality (
                    id INTEGER PRIMARY KEY,
                    position_fen TEXT NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON move data
                    quality_tier TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    neural_score REAL,
                    pattern_score REAL,
                    strategic_score REAL,
                    tactical_score REAL,
                    risk_score REAL,
                    opportunity_score REAL,
                    blocking_opportunities INTEGER,
                    scoring_opportunities INTEGER,
                    floor_line_risks INTEGER,
                    strategic_value REAL,
                    tactical_factors TEXT,  -- JSON array
                    risk_assessment TEXT,
                    educational_explanation TEXT,
                    game_phase TEXT,
                    complexity_score REAL,
                    engine_consensus TEXT,  -- JSON consensus data
                    confidence_level REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Real game analysis table
                CREATE TABLE IF NOT EXISTS real_game_analysis (
                    id INTEGER PRIMARY KEY,
                    game_id TEXT UNIQUE NOT NULL,
                    players TEXT NOT NULL,  -- JSON array
                    total_moves INTEGER NOT NULL,
                    blunder_count INTEGER DEFAULT 0,
                    average_blunder_severity REAL DEFAULT 0.0,
                    game_data TEXT NOT NULL,  -- JSON game log
                    analysis_data TEXT,  -- JSON analysis results
                    quality_metrics TEXT,  -- JSON quality metrics
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Engine self-play games table
                CREATE TABLE IF NOT EXISTS engine_self_play_games (
                    id INTEGER PRIMARY KEY,
                    game_id TEXT UNIQUE NOT NULL,
                    engine_config TEXT NOT NULL,  -- JSON config
                    moves TEXT NOT NULL,  -- JSON moves array
                    final_scores TEXT NOT NULL,  -- JSON scores array
                    winner INTEGER NOT NULL,
                    quality_metrics TEXT,  -- JSON metrics
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Machine learning training data table
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
                
                -- Advanced analytics table
                CREATE TABLE IF NOT EXISTS advanced_analytics (
                    id INTEGER PRIMARY KEY,
                    analysis_type TEXT NOT NULL,
                    metrics TEXT NOT NULL,  -- JSON metrics
                    insights TEXT,  -- JSON insights
                    recommendations TEXT,  -- JSON recommendations
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_enhanced_quality_position ON enhanced_move_quality(position_fen);
                CREATE INDEX IF NOT EXISTS idx_enhanced_quality_tier ON enhanced_move_quality(quality_tier);
                CREATE INDEX IF NOT EXISTS idx_enhanced_quality_score ON enhanced_move_quality(quality_score DESC);
                CREATE INDEX IF NOT EXISTS idx_real_game_id ON real_game_analysis(game_id);
                CREATE INDEX IF NOT EXISTS idx_engine_game_id ON engine_self_play_games(game_id);
                CREATE INDEX IF NOT EXISTS idx_ml_training_position ON ml_training_data(position_fen);
                CREATE INDEX IF NOT EXISTS idx_analytics_type ON advanced_analytics(analysis_type);
            """)
    
    def analyze_real_game(self, game_data: Dict[str, Any]) -> GameAnalysis:
        """Analyze a real game from strong players."""
        game_id = game_data.get('game_id', f"game_{int(time.time())}")
        players = game_data.get('players', ['Player 1', 'Player 2'])
        moves = game_data.get('moves', [])
        final_scores = game_data.get('final_scores', [0, 0])
        
        # Analyze each move in the game
        analysis_data = {
            'move_analyses': [],
            'blunder_count': 0,
            'average_quality': 0.0,
            'quality_distribution': {'!!': 0, '!': 0, '=': 0, '?!': 0, '?': 0}
        }
        
        assessor = AzulMoveQualityAssessor()
        total_quality = 0.0
        
        for i, move_data in enumerate(moves):
            try:
                # Parse position and analyze move
                position_fen = move_data.get('position_fen')
                if position_fen:
                    state = parse_fen_string(position_fen)
                    if state:
                        # Analyze the move quality
                        move_analysis = assessor.analyze_position(state, move_data.get('player_id', 0))
                        
                        # Find the specific move in the analysis
                        for analysis in move_analysis:
                            if self._matches_move(analysis.move_data, move_data):
                                move_analysis_data = {
                                    'move_index': i,
                                    'quality_tier': analysis.quality_tier.value,
                                    'quality_score': analysis.quality_score,
                                    'explanation': analysis.educational_explanation,
                                    'is_blunder': analysis.quality_score < 25
                                }
                                
                                analysis_data['move_analyses'].append(move_analysis_data)
                                analysis_data['quality_distribution'][analysis.quality_tier.value] += 1
                                
                                if analysis.quality_score < 25:
                                    analysis_data['blunder_count'] += 1
                                
                                total_quality += analysis.quality_score
                                break
            except Exception as e:
                print(f"Error analyzing move {i}: {e}")
        
        # Calculate averages
        if analysis_data['move_analyses']:
            analysis_data['average_quality'] = total_quality / len(analysis_data['move_analyses'])
        
        # Determine winner
        winner = 0 if final_scores[0] > final_scores[1] else 1
        
        game_analysis = GameAnalysis(
            game_id=game_id,
            players=players,
            moves=moves,
            final_scores=final_scores,
            winner=winner,
            analysis_data=analysis_data,
            created_at=datetime.now()
        )
        
        # Save to database
        self._save_game_analysis(game_analysis)
        
        return game_analysis
    
    def generate_engine_self_play_game(self, engine_config: Dict[str, Any]) -> EngineSelfPlayGame:
        """Generate a game between engines for validation."""
        game_id = f"engine_game_{int(time.time())}"
        
        # Initialize game state
        game_rule = AzulGameRule()
        state = game_rule.get_init_state()
        
        moves = []
        current_player = 0
        
        # Play the game
        while not game_rule.is_terminal(state):
            # Generate moves for current player
            move_generator = FastMoveGenerator()
            possible_moves = move_generator.get_all_moves(state, current_player)
            
            if not possible_moves:
                break
            
            # Evaluate moves using the engine
            evaluator = AzulEvaluator()
            best_move = None
            best_score = float('-inf')
            
            for move in possible_moves:
                # Apply move temporarily
                temp_state = game_rule.apply_move(state, move, current_player)
                score = evaluator.evaluate_position(temp_state, current_player)
                
                if score > best_score:
                    best_score = score
                    best_move = move
            
            if best_move:
                # Record the move
                move_data = {
                    'player_id': current_player,
                    'move': best_move,
                    'score': best_score,
                    'position_fen': state_to_fen(state)
                }
                moves.append(move_data)
                
                # Apply the move
                state = game_rule.apply_move(state, best_move, current_player)
                current_player = (current_player + 1) % len(state.agents)
            else:
                break
        
        # Calculate final scores
        final_scores = [agent.score for agent in state.agents]
        winner = final_scores.index(max(final_scores))
        
        # Calculate quality metrics
        quality_metrics = self._calculate_game_quality_metrics(moves)
        
        engine_game = EngineSelfPlayGame(
            game_id=game_id,
            engine_config=engine_config,
            moves=moves,
            final_scores=final_scores,
            winner=winner,
            quality_metrics=quality_metrics,
            created_at=datetime.now()
        )
        
        # Save to database
        self._save_engine_game(engine_game)
        
        return engine_game
    
    def generate_ml_training_data(self, num_positions: int = 1000) -> List[Dict[str, Any]]:
        """Generate machine learning training data from existing database."""
        training_data = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT position_fen, move_data, quality_score, quality_tier,
                       neural_score, pattern_score, strategic_score, tactical_score,
                       risk_score, opportunity_score, blocking_opportunities,
                       scoring_opportunities, floor_line_risks, strategic_value
                FROM enhanced_move_quality
                WHERE quality_score IS NOT NULL
                ORDER BY RANDOM()
                LIMIT ?
            """, (num_positions,))
            
            for row in cursor.fetchall():
                # Extract features
                features = {
                    'neural_score': row[4] or 0.0,
                    'pattern_score': row[5] or 0.0,
                    'strategic_score': row[6] or 0.0,
                    'tactical_score': row[7] or 0.0,
                    'risk_score': row[8] or 0.0,
                    'opportunity_score': row[9] or 0.0,
                    'blocking_opportunities': row[10] or 0,
                    'scoring_opportunities': row[11] or 0,
                    'floor_line_risks': row[12] or 0,
                    'strategic_value': row[13] or 0.0
                }
                
                training_data.append({
                    'position_fen': row[0],
                    'move_data': row[1],
                    'quality_score': row[2],
                    'features': features,
                    'target_label': row[3],
                    'confidence': 1.0
                })
        
        return training_data
    
    def _matches_move(self, analysis_move: Dict[str, Any], game_move: Dict[str, Any]) -> bool:
        """Check if analysis move matches game move."""
        # Simple matching - can be enhanced
        return analysis_move.get('move_type') == game_move.get('move_type')
    
    def _calculate_game_quality_metrics(self, moves: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate quality metrics for an engine game."""
        if not moves:
            return {}
        
        quality_scores = [move.get('score', 0) for move in moves]
        
        return {
            'average_quality': sum(quality_scores) / len(quality_scores),
            'max_quality': max(quality_scores),
            'min_quality': min(quality_scores),
            'quality_variance': self._calculate_variance(quality_scores),
            'total_moves': len(moves)
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _save_game_analysis(self, game_analysis: GameAnalysis):
        """Save game analysis to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO real_game_analysis 
                (game_id, players, total_moves, blunder_count, average_blunder_severity,
                 game_data, analysis_data, quality_metrics, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_analysis.game_id,
                json.dumps(game_analysis.players),
                len(game_analysis.moves),
                game_analysis.analysis_data.get('blunder_count', 0),
                game_analysis.analysis_data.get('average_blunder_severity', 0.0),
                json.dumps(game_analysis.moves),
                json.dumps(game_analysis.analysis_data),
                json.dumps(game_analysis.analysis_data.get('quality_distribution', {})),
                game_analysis.created_at.isoformat()
            ))
    
    def _save_engine_game(self, engine_game: EngineSelfPlayGame):
        """Save engine self-play game to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO engine_self_play_games
                (game_id, engine_config, moves, final_scores, winner, quality_metrics, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                engine_game.game_id,
                json.dumps(engine_game.engine_config),
                json.dumps(engine_game.moves),
                json.dumps(engine_game.final_scores),
                engine_game.winner,
                json.dumps(engine_game.quality_metrics),
                engine_game.created_at.isoformat()
            ))

def main():
    """Main function to demonstrate enhanced database features."""
    print("🚀 Enhanced Move Quality Database Development")
    print("=" * 50)
    
    # Initialize enhanced database
    db = EnhancedMoveQualityDatabase()
    
    # Example: Generate ML training data
    print("\n📊 Generating ML training data...")
    training_data = db.generate_ml_training_data(100)
    print(f"✅ Generated {len(training_data)} training examples")
    
    # Example: Generate engine self-play game
    print("\n🤖 Generating engine self-play game...")
    engine_config = {
        'evaluation_depth': 3,
        'search_algorithm': 'alpha_beta',
        'time_limit': 1.0
    }
    engine_game = db.generate_engine_self_play_game(engine_config)
    print(f"✅ Generated engine game with {len(engine_game.moves)} moves")
    print(f"   Winner: Player {engine_game.winner}")
    print(f"   Final scores: {engine_game.final_scores}")
    
    print("\n🎯 Enhanced database development complete!")
    print("Next steps:")
    print("1. Collect real game data from strong players")
    print("2. Train ML models on the generated data")
    print("3. Implement advanced analytics and insights")
    print("4. Create visualization tools for the enhanced data")

if __name__ == "__main__":
    main()
