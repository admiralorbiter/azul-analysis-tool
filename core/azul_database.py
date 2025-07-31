"""
Database integration for Azul Research Toolkit.

This module provides SQLite-based caching for game positions and analysis results,
enabling faster repeated analysis and historical tracking of search performance.
"""

import sqlite3
import json
import time
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .azul_model import AzulState
from .azul_move_generator import FastMove


@dataclass
class CachedAnalysis:
    """Represents a cached analysis result."""
    position_id: int
    agent_id: int
    search_type: str
    best_move: Optional[str]
    score: float
    search_time: float
    nodes_searched: int
    rollout_count: int
    created_at: datetime
    principal_variation: List[str] = None


class AzulDatabase:
    """
    SQLite database interface for caching Azul positions and analysis results.
    
    Provides efficient storage and retrieval of:
    - Game positions (FEN-like strings)
    - Analysis results (MCTS, Alpha-Beta)
    - Move sequences (Principal Variations)
    - Performance statistics
    """
    
    def __init__(self, db_path: str = "data/azul_research.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable named column access
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            conn.executescript("""
                -- Game positions table
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY,
                    fen_string TEXT UNIQUE NOT NULL,
                    player_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Analysis results table
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY,
                    position_id INTEGER NOT NULL,
                    agent_id INTEGER NOT NULL,
                    search_type TEXT NOT NULL,
                    best_move TEXT,
                    score REAL,
                    search_time REAL,
                    nodes_searched INTEGER,
                    rollout_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE
                );
                
                -- Move sequences for principal variations
                CREATE TABLE IF NOT EXISTS move_sequences (
                    id INTEGER PRIMARY KEY,
                    analysis_id INTEGER NOT NULL,
                    move_order INTEGER NOT NULL,
                    move_text TEXT NOT NULL,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
                );
                
                -- Performance statistics
                CREATE TABLE IF NOT EXISTS performance_stats (
                    id INTEGER PRIMARY KEY,
                    search_type TEXT NOT NULL,
                    total_searches INTEGER DEFAULT 0,
                    total_time REAL DEFAULT 0.0,
                    total_nodes INTEGER DEFAULT 0,
                    total_rollouts INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    cache_misses INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_positions_fen ON positions(fen_string);
                CREATE INDEX IF NOT EXISTS idx_analysis_position ON analysis_results(position_id);
                CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(search_type);
                CREATE INDEX IF NOT EXISTS idx_analysis_agent ON analysis_results(agent_id);
                CREATE INDEX IF NOT EXISTS idx_moves_analysis ON move_sequences(analysis_id);
                CREATE INDEX IF NOT EXISTS idx_stats_type ON performance_stats(search_type);
                
                -- Enable foreign key constraints
                PRAGMA foreign_keys = ON;
            """)
    
    def cache_position(self, fen_string: str, player_count: int) -> int:
        """
        Cache a position and return its ID.
        
        Args:
            fen_string: FEN-like string representation of position
            player_count: Number of players in the game
            
        Returns:
            Position ID (existing or newly created)
        """
        with self.get_connection() as conn:
            # Try to insert new position
            cursor = conn.execute(
                "INSERT OR IGNORE INTO positions (fen_string, player_count) VALUES (?, ?)",
                (fen_string, player_count)
            )
            conn.commit()
            
            # Get the position ID (either existing or newly created)
            cursor = conn.execute(
                "SELECT id FROM positions WHERE fen_string = ?",
                (fen_string,)
            )
            return cursor.fetchone()['id']
    
    def get_position_id(self, fen_string: str) -> Optional[int]:
        """
        Get position ID if it exists.
        
        Args:
            fen_string: FEN-like string representation
            
        Returns:
            Position ID if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM positions WHERE fen_string = ?",
                (fen_string,)
            )
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def cache_analysis(self, position_id: int, agent_id: int, search_type: str,
                      result: Dict[str, Any]) -> int:
        """
        Cache analysis results.
        
        Args:
            position_id: ID of the position
            agent_id: Agent ID that performed analysis
            search_type: Type of search ('mcts', 'alpha_beta')
            result: Analysis result dictionary
            
        Returns:
            Analysis result ID
        """
        with self.get_connection() as conn:
            # Insert analysis result
            cursor = conn.execute("""
                INSERT INTO analysis_results 
                (position_id, agent_id, search_type, best_move, score, 
                 search_time, nodes_searched, rollout_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                position_id, agent_id, search_type,
                str(result.get('best_move', '')),
                result.get('best_score', 0.0),
                result.get('search_time', 0.0),
                result.get('nodes_searched', 0),
                result.get('rollout_count', 0)
            ))
            analysis_id = cursor.lastrowid
            
            # Cache principal variation if available
            pv = result.get('principal_variation', [])
            if pv:
                for i, move in enumerate(pv):
                    conn.execute(
                        "INSERT INTO move_sequences (analysis_id, move_order, move_text) VALUES (?, ?, ?)",
                        (analysis_id, i, str(move))
                    )
            
            conn.commit()
            return analysis_id
    
    def get_cached_analysis(self, fen_string: str, agent_id: int, 
                           search_type: str) -> Optional[CachedAnalysis]:
        """
        Get cached analysis if available.
        
        Args:
            fen_string: FEN-like string representation
            agent_id: Agent ID
            search_type: Type of search ('mcts', 'alpha_beta')
            
        Returns:
            CachedAnalysis object if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT ar.*, p.fen_string FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                WHERE p.fen_string = ? AND ar.agent_id = ? AND ar.search_type = ?
                ORDER BY ar.created_at DESC LIMIT 1
            """, (fen_string, agent_id, search_type))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Get principal variation
            pv_cursor = conn.execute("""
                SELECT move_text FROM move_sequences 
                WHERE analysis_id = ? ORDER BY move_order
            """, (row['id'],))
            
            principal_variation = [move_row['move_text'] for move_row in pv_cursor.fetchall()]
            
            return CachedAnalysis(
                position_id=row['position_id'],
                agent_id=row['agent_id'],
                search_type=row['search_type'],
                best_move=row['best_move'],
                score=row['score'],
                search_time=row['search_time'],
                nodes_searched=row['nodes_searched'],
                rollout_count=row['rollout_count'],
                created_at=datetime.fromisoformat(row['created_at']),
                principal_variation=principal_variation
            )
    
    def update_performance_stats(self, search_type: str, search_time: float,
                               nodes_searched: int = 0, rollouts: int = 0,
                               cache_hit: bool = False):
        """
        Update performance statistics.
        
        Args:
            search_type: Type of search ('mcts', 'alpha_beta')
            search_time: Time taken for search
            nodes_searched: Number of nodes searched
            rollouts: Number of rollouts (for MCTS)
            cache_hit: Whether this was a cache hit
        """
        with self.get_connection() as conn:
            # Try to update existing stats
            cursor = conn.execute("""
                UPDATE performance_stats SET
                    total_searches = total_searches + 1,
                    total_time = total_time + ?,
                    total_nodes = total_nodes + ?,
                    total_rollouts = total_rollouts + ?,
                    cache_hits = cache_hits + ?,
                    cache_misses = cache_misses + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE search_type = ?
            """, (
                search_time, nodes_searched, rollouts,
                1 if cache_hit else 0, 0 if cache_hit else 1,
                search_type
            ))
            
            # If no rows were updated, insert new stats
            if cursor.rowcount == 0:
                conn.execute("""
                    INSERT INTO performance_stats 
                    (search_type, total_searches, total_time, total_nodes, 
                     total_rollouts, cache_hits, cache_misses)
                    VALUES (?, 1, ?, ?, ?, ?, ?)
                """, (
                    search_type, search_time, nodes_searched, rollouts,
                    1 if cache_hit else 0, 0 if cache_hit else 1
                ))
            
            conn.commit()
    
    def get_performance_stats(self, search_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get performance statistics.
        
        Args:
            search_type: Optional filter for specific search type
            
        Returns:
            List of performance statistics
        """
        with self.get_connection() as conn:
            if search_type:
                cursor = conn.execute(
                    "SELECT * FROM performance_stats WHERE search_type = ?",
                    (search_type,)
                )
            else:
                cursor = conn.execute("SELECT * FROM performance_stats")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.get_connection() as conn:
            # Count positions
            cursor = conn.execute("SELECT COUNT(*) as count FROM positions")
            position_count = cursor.fetchone()['count']
            
            # Count analysis results
            cursor = conn.execute("SELECT COUNT(*) as count FROM analysis_results")
            analysis_count = cursor.fetchone()['count']
            
            # Count by search type
            cursor = conn.execute("""
                SELECT search_type, COUNT(*) as count 
                FROM analysis_results 
                GROUP BY search_type
            """)
            by_type = {row['search_type']: row['count'] for row in cursor.fetchall()}
            
            # Get performance stats
            performance = self.get_performance_stats()
            
            return {
                'positions_cached': position_count,
                'analyses_cached': analysis_count,
                'by_search_type': by_type,
                'performance': performance
            }
    
    def clear_cache(self, search_type: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            search_type: Optional filter to clear only specific search type
        """
        with self.get_connection() as conn:
            if search_type:
                # Delete analysis results for specific search type
                conn.execute("""
                    DELETE FROM analysis_results WHERE search_type = ?
                """, (search_type,))
            else:
                # Clear all cache
                conn.execute("DELETE FROM analysis_results")
                conn.execute("DELETE FROM positions")
                conn.execute("DELETE FROM performance_stats")
            
            conn.commit()
    
    def get_recent_analyses(self, limit: int = 10) -> List[CachedAnalysis]:
        """
        Get recent analysis results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of recent CachedAnalysis objects
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT ar.*, p.fen_string FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                ORDER BY ar.created_at DESC LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                # Get principal variation
                pv_cursor = conn.execute("""
                    SELECT move_text FROM move_sequences 
                    WHERE analysis_id = ? ORDER BY move_order
                """, (row['id'],))
                
                principal_variation = [move_row['move_text'] for move_row in pv_cursor.fetchall()]
                
                results.append(CachedAnalysis(
                    position_id=row['position_id'],
                    agent_id=row['agent_id'],
                    search_type=row['search_type'],
                    best_move=row['best_move'],
                    score=row['score'],
                    search_time=row['search_time'],
                    nodes_searched=row['nodes_searched'],
                    rollout_count=row['rollout_count'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    principal_variation=principal_variation
                ))
            
            return results 