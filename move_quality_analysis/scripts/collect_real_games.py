#!/usr/bin/env python3
"""
Real Game Data Collection

This script collects and analyzes real games from strong players to enhance
the move quality database with actual human play patterns.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent  # Go up one more level to reach the main project root
sys.path.insert(0, str(project_root))

import json
import sqlite3
import time
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from core.azul_model import AzulState
from analysis_engine.move_quality.azul_move_quality_assessor import AzulMoveQualityAssessor
from api.utils.state_parser import parse_fen_string, state_to_fen

@dataclass
class GameRecord:
    """Data structure for a complete game record."""
    game_id: str
    platform: str  # 'bga', 'local', 'tournament', etc.
    players: List[str]
    player_ratings: List[int]
    game_date: datetime
    moves: List[Dict[str, Any]]
    final_scores: List[int]
    winner: int
    game_length: int
    metadata: Dict[str, Any]

class RealGameCollector:
    """Collect and analyze real games from various sources."""
    
    def __init__(self, db_path: str = "../data/real_games.db"):
        self.db_path = db_path
        self._init_real_games_database()
        self.assessor = AzulMoveQualityAssessor()
    
    def _init_real_games_database(self):
        """Initialize database for real game data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Real games table
                CREATE TABLE IF NOT EXISTS real_games (
                    id INTEGER PRIMARY KEY,
                    game_id TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    players TEXT NOT NULL,  -- JSON array
                    player_ratings TEXT,  -- JSON array
                    game_date TIMESTAMP,
                    moves TEXT NOT NULL,  -- JSON array
                    final_scores TEXT NOT NULL,  -- JSON array
                    winner INTEGER NOT NULL,
                    game_length INTEGER NOT NULL,
                    metadata TEXT,  -- JSON metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Game analysis results
                CREATE TABLE IF NOT EXISTS game_analysis_results (
                    id INTEGER PRIMARY KEY,
                    game_id TEXT NOT NULL,
                    total_moves INTEGER NOT NULL,
                    blunder_count INTEGER DEFAULT 0,
                    average_quality REAL DEFAULT 0.0,
                    quality_distribution TEXT,  -- JSON distribution
                    move_analyses TEXT,  -- JSON detailed analyses
                    insights TEXT,  -- JSON insights
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES real_games(game_id)
                );
                
                -- Player performance tracking
                CREATE TABLE IF NOT EXISTS player_performance (
                    id INTEGER PRIMARY KEY,
                    player_name TEXT NOT NULL,
                    games_played INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    average_quality REAL DEFAULT 0.0,
                    blunder_rate REAL DEFAULT 0.0,
                    best_quality_move REAL DEFAULT 0.0,
                    worst_quality_move REAL DEFAULT 100.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_real_games_platform ON real_games(platform);
                CREATE INDEX IF NOT EXISTS idx_real_games_date ON real_games(game_date);
                CREATE INDEX IF NOT EXISTS idx_real_games_winner ON real_games(winner);
                CREATE INDEX IF NOT EXISTS idx_analysis_game_id ON game_analysis_results(game_id);
                CREATE INDEX IF NOT EXISTS idx_player_name ON player_performance(player_name);
            """)
    
    def collect_bga_games(self, username: str, api_key: str, limit: int = 50) -> List[GameRecord]:
        """Collect games from BoardGameArena API."""
        print(f"🎮 Collecting BGA games for user: {username}")
        
        # BGA API endpoint (example - would need actual BGA API access)
        url = f"https://boardgamearena.com/api/games.php"
        params = {
            'username': username,
            'api_key': api_key,
            'game': 'azul',
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                games_data = response.json()
                return self._parse_bga_games(games_data)
            else:
                print(f"❌ Failed to fetch BGA games: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error collecting BGA games: {e}")
            return []
    
    def collect_local_games(self, games_file: str) -> List[GameRecord]:
        """Collect games from local file (JSON format)."""
        print(f"📁 Collecting local games from: {games_file}")
        
        try:
            with open(games_file, 'r') as f:
                games_data = json.load(f)
            
            game_records = []
            for game_data in games_data:
                game_record = self._parse_local_game(game_data)
                if game_record:
                    game_records.append(game_record)
            
            print(f"✅ Collected {len(game_records)} local games")
            return game_records
            
        except Exception as e:
            print(f"❌ Error reading local games file: {e}")
            return []
    
    def collect_tournament_games(self, tournament_id: str) -> List[GameRecord]:
        """Collect games from tournament data."""
        print(f"🏆 Collecting tournament games: {tournament_id}")
        
        # This would integrate with tournament data sources
        # For now, return empty list as placeholder
        return []
    
    def analyze_game(self, game_record: GameRecord) -> Dict[str, Any]:
        """Analyze a single game for move quality."""
        print(f"🔍 Analyzing game: {game_record.game_id}")
        
        analysis_data = {
            'move_analyses': [],
            'blunder_count': 0,
            'average_quality': 0.0,
            'quality_distribution': {'!!': 0, '!': 0, '=': 0, '?!': 0, '?': 0},
            'player_performance': {},
            'insights': []
        }
        
        total_quality = 0.0
        move_count = 0
        
        # Analyze each move in the game
        for i, move_data in enumerate(game_record.moves):
            try:
                position_fen = move_data.get('position_fen')
                player_id = move_data.get('player_id', 0)
                
                if position_fen:
                    state = parse_fen_string(position_fen)
                    if state:
                        # Analyze the move quality
                        move_analyses = self.assessor.evaluate_all_moves(state, player_id)
                        
                        # Find the specific move in the analysis
                        if move_analyses and move_analyses.all_moves_quality:
                            # Get the best move quality as a reference
                            best_move_key = move_analyses.best_moves[0] if move_analyses.best_moves else list(move_analyses.all_moves_quality.keys())[0]
                            best_move_quality = move_analyses.all_moves_quality[best_move_key]
                            
                            move_analysis = {
                                'move_index': i,
                                'player_id': player_id,
                                'quality_tier': best_move_quality.quality_tier.value,
                                'quality_score': best_move_quality.overall_score,
                                'explanation': best_move_quality.explanation,
                                'is_blunder': best_move_quality.overall_score < 25,
                                'position_fen': position_fen
                            }
                            
                            analysis_data['move_analyses'].append(move_analysis)
                            analysis_data['quality_distribution'][best_move_quality.quality_tier.value] += 1
                            
                            if best_move_quality.overall_score < 25:
                                analysis_data['blunder_count'] += 1
                            
                            total_quality += best_move_quality.overall_score
                            move_count += 1
                            
                            # Track player performance
                            player_name = game_record.players[player_id]
                            if player_name not in analysis_data['player_performance']:
                                analysis_data['player_performance'][player_name] = {
                                    'moves': 0,
                                    'total_quality': 0.0,
                                    'blunders': 0,
                                    'best_move': 0.0,
                                    'worst_move': 100.0
                                }
                            
                            player_perf = analysis_data['player_performance'][player_name]
                            player_perf['moves'] += 1
                            player_perf['total_quality'] += best_move_quality.overall_score
                            if best_move_quality.overall_score < 25:
                                player_perf['blunders'] += 1
                            player_perf['best_move'] = max(player_perf['best_move'], best_move_quality.overall_score)
                            player_perf['worst_move'] = min(player_perf['worst_move'], best_move_quality.overall_score)
                            break
                                
            except Exception as e:
                print(f"⚠️ Error analyzing move {i} in game {game_record.game_id}: {e}")
        
        # Calculate averages and insights
        if move_count > 0:
            analysis_data['average_quality'] = total_quality / move_count
        
        # Generate insights
        analysis_data['insights'] = self._generate_game_insights(analysis_data)
        
        return analysis_data
    
    def save_game_record(self, game_record: GameRecord):
        """Save game record to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO real_games
                (game_id, platform, players, player_ratings, game_date, moves,
                 final_scores, winner, game_length, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_record.game_id,
                game_record.platform,
                json.dumps(game_record.players),
                json.dumps(game_record.player_ratings) if game_record.player_ratings else None,
                game_record.game_date.isoformat() if game_record.game_date else None,
                json.dumps(game_record.moves),
                json.dumps(game_record.final_scores),
                game_record.winner,
                game_record.game_length,
                json.dumps(game_record.metadata),
                datetime.now().isoformat()
            ))
    
    def save_game_analysis(self, game_id: str, analysis_data: Dict[str, Any]):
        """Save game analysis results to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO game_analysis_results
                (game_id, total_moves, blunder_count, average_quality,
                 quality_distribution, move_analyses, insights, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_id,
                len(analysis_data['move_analyses']),
                analysis_data['blunder_count'],
                analysis_data['average_quality'],
                json.dumps(analysis_data['quality_distribution']),
                json.dumps(analysis_data['move_analyses']),
                json.dumps(analysis_data['insights']),
                datetime.now().isoformat()
            ))
    
    def update_player_performance(self, analysis_data: Dict[str, Any]):
        """Update player performance statistics."""
        with sqlite3.connect(self.db_path) as conn:
            for player_name, performance in analysis_data['player_performance'].items():
                conn.execute("""
                    INSERT OR REPLACE INTO player_performance
                    (player_name, games_played, games_won, average_quality,
                     blunder_rate, best_quality_move, worst_quality_move, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_name,
                    1,  # games_played (would need to track properly)
                    0,  # games_won (would need to track properly)
                    performance['total_quality'] / performance['moves'] if performance['moves'] > 0 else 0.0,
                    performance['blunders'] / performance['moves'] if performance['moves'] > 0 else 0.0,
                    performance['best_move'],
                    performance['worst_move'],
                    datetime.now().isoformat()
                ))
    
    def _parse_bga_games(self, games_data: List[Dict[str, Any]]) -> List[GameRecord]:
        """Parse BGA API response into GameRecord objects."""
        game_records = []
        
        for game_data in games_data:
            try:
                game_record = GameRecord(
                    game_id=game_data.get('game_id', f"bga_{int(time.time())}"),
                    platform='bga',
                    players=game_data.get('players', ['Unknown']),
                    player_ratings=game_data.get('ratings', []),
                    game_date=datetime.fromisoformat(game_data.get('date', datetime.now().isoformat())),
                    moves=game_data.get('moves', []),
                    final_scores=game_data.get('final_scores', [0, 0]),
                    winner=game_data.get('winner', 0),
                    game_length=len(game_data.get('moves', [])),
                    metadata=game_data.get('metadata', {})
                )
                game_records.append(game_record)
            except Exception as e:
                print(f"⚠️ Error parsing BGA game: {e}")
        
        return game_records
    
    def _parse_local_game(self, game_data: Dict[str, Any]) -> Optional[GameRecord]:
        """Parse local game data into GameRecord object."""
        try:
            return GameRecord(
                game_id=game_data.get('game_id', f"local_{int(time.time())}"),
                platform='local',
                players=game_data.get('players', ['Player 1', 'Player 2']),
                player_ratings=game_data.get('ratings', []),
                game_date=datetime.fromisoformat(game_data.get('date', datetime.now().isoformat())),
                moves=game_data.get('moves', []),
                final_scores=game_data.get('final_scores', [0, 0]),
                winner=game_data.get('winner', 0),
                game_length=len(game_data.get('moves', [])),
                metadata=game_data.get('metadata', {})
            )
        except Exception as e:
            print(f"⚠️ Error parsing local game: {e}")
            return None
    
    def _matches_move(self, analysis_move: Dict[str, Any], game_move: Dict[str, Any]) -> bool:
        """Check if analysis move matches game move."""
        # Enhanced matching logic
        return (analysis_move.get('move_type') == game_move.get('move_type') and
                analysis_move.get('tile_color') == game_move.get('tile_color') and
                analysis_move.get('row') == game_move.get('row'))
    
    def _generate_game_insights(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate insights from game analysis."""
        insights = []
        
        # Quality distribution insights
        quality_dist = analysis_data['quality_distribution']
        total_moves = sum(quality_dist.values())
        
        if quality_dist['!!'] > 0:
            insights.append(f"Game featured {quality_dist['!!']} brilliant moves")
        
        if quality_dist['?'] > total_moves * 0.3:
            insights.append("High number of poor moves suggests challenging position")
        
        if analysis_data['blunder_count'] > 0:
            blunder_rate = analysis_data['blunder_count'] / total_moves
            insights.append(f"Blunder rate: {blunder_rate:.1%}")
        
        # Player performance insights
        for player_name, performance in analysis_data['player_performance'].items():
            avg_quality = performance['total_quality'] / performance['moves']
            blunder_rate = performance['blunders'] / performance['moves']
            
            if avg_quality > 70:
                insights.append(f"{player_name} played very well (avg quality: {avg_quality:.1f})")
            elif blunder_rate > 0.2:
                insights.append(f"{player_name} made several mistakes (blunder rate: {blunder_rate:.1%})")
        
        return insights

def main():
    """Main function to demonstrate real game collection."""
    print("🎮 Real Game Data Collection")
    print("=" * 40)
    
    collector = RealGameCollector()
    
    # Example: Collect local games
    print("\n📁 Collecting local games...")
    local_games = collector.collect_local_games("../data/sample_games.json")
    
    if local_games:
        print(f"✅ Collected {len(local_games)} local games")
        
        # Analyze each game
        for game_record in local_games:
            print(f"\n🔍 Analyzing game: {game_record.game_id}")
            
            # Save game record
            collector.save_game_record(game_record)
            
            # Analyze game
            analysis_data = collector.analyze_game(game_record)
            
            # Save analysis
            collector.save_game_analysis(game_record.game_id, analysis_data)
            
            # Update player performance
            collector.update_player_performance(analysis_data)
            
            print(f"   Average quality: {analysis_data['average_quality']:.1f}")
            print(f"   Blunders: {analysis_data['blunder_count']}")
            print(f"   Quality distribution: {analysis_data['quality_distribution']}")
    
    print("\n🎯 Real game collection complete!")
    print("Next steps:")
    print("1. Collect more games from various sources")
    print("2. Analyze player performance trends")
    print("3. Generate insights and recommendations")
    print("4. Integrate with enhanced database")

if __name__ == "__main__":
    main()
