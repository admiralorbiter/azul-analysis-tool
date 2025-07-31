"""
Database integration for Azul Research Toolkit.

This module provides SQLite-based caching for game positions and analysis results,
enabling faster repeated analysis and historical tracking of search performance.
"""

import sqlite3
import json
import time
import os
import zstandard as zstd
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


@dataclass
class QueryPerformance:
    """Represents query performance metrics."""
    query_type: str
    execution_time_ms: float
    rows_returned: int
    index_used: Optional[str]
    timestamp: datetime


class AzulDatabase:
    """
    SQLite database interface for caching Azul positions and analysis results.
    
    Provides efficient storage and retrieval of:
    - Game positions (FEN-like strings)
    - Analysis results (MCTS, Alpha-Beta)
    - Move sequences (Principal Variations)
    - Performance statistics
    
    Features:
    - WAL mode for concurrent access
    - Optimized memory settings
    - Performance monitoring
    - Cache statistics
    - Zstd compression for state storage
    - Enhanced indexing and query optimization
    """
    
    def __init__(self, db_path: str = "data/azul_research.db", 
                 enable_wal: bool = True, 
                 memory_limit_mb: int = 64,
                 cache_size_pages: int = 1000,
                 enable_compression: bool = True,
                 compression_level: int = 3,
                 enable_query_monitoring: bool = True):
        """
        Initialize database connection with performance optimizations.
        
        Args:
            db_path: Path to SQLite database file
            enable_wal: Enable WAL mode for better concurrency
            memory_limit_mb: Memory limit in MB for SQLite
            cache_size_pages: Number of pages for SQLite cache
            enable_compression: Enable Zstd compression for state storage
            compression_level: Zstd compression level (1-22, higher = smaller but slower)
            enable_query_monitoring: Enable query performance monitoring
        """
        self.db_path = db_path
        self.enable_wal = enable_wal
        self.memory_limit_mb = memory_limit_mb
        self.cache_size_pages = cache_size_pages
        self.enable_compression = enable_compression
        self.compression_level = compression_level
        self.enable_query_monitoring = enable_query_monitoring
        
        # Initialize Zstd compressor/decompressor
        if self.enable_compression:
            self.compressor = zstd.ZstdCompressor(level=compression_level)
            self.decompressor = zstd.ZstdDecompressor()
        
        # Query performance tracking
        self.query_performance_log: List[QueryPerformance] = []
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_db()
    
    def _compress_data(self, data: str) -> bytes:
        """Compress string data using Zstd."""
        if not self.enable_compression:
            return data.encode('utf-8')
        return self.compressor.compress(data.encode('utf-8'))
    
    def _decompress_data(self, compressed_data: bytes) -> str:
        """Decompress bytes data using Zstd."""
        if not self.enable_compression:
            return compressed_data.decode('utf-8')
        return self.decompressor.decompress(compressed_data).decode('utf-8')
    
    def _log_query_performance(self, query_type: str, execution_time_ms: float, 
                              rows_returned: int, index_used: Optional[str] = None):
        """Log query performance metrics."""
        if self.enable_query_monitoring:
            self.query_performance_log.append(QueryPerformance(
                query_type=query_type,
                execution_time_ms=execution_time_ms,
                rows_returned=rows_returned,
                index_used=index_used,
                timestamp=datetime.now()
            ))
            
            # Keep only last 1000 entries to prevent memory bloat
            if len(self.query_performance_log) > 1000:
                self.query_performance_log = self.query_performance_log[-1000:]
    
    def _execute_with_monitoring(self, conn: sqlite3.Connection, query: str, 
                                params: Tuple = (), query_type: str = "unknown") -> sqlite3.Cursor:
        """Execute query with performance monitoring."""
        start_time = time.time()
        
        # Execute query
        cursor = conn.execute(query, params)
        
        # Get execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Log performance (don't fetch rows here to avoid consuming the cursor)
        self._log_query_performance(query_type, execution_time_ms, 0)  # Will be updated after fetch
        
        # Return cursor without consuming it
        return cursor
    
    @contextmanager
    def get_connection(self):
        """Get database connection with performance optimizations."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable named column access
        
        # Apply performance optimizations
        self._configure_connection(conn)
        
        try:
            yield conn
        finally:
            conn.close()
    
    def _configure_connection(self, conn: sqlite3.Connection):
        """Configure connection with performance optimizations."""
        # Enable WAL mode for better concurrency
        if self.enable_wal:
            conn.execute("PRAGMA journal_mode = WAL")
        
        # Set memory limits
        conn.execute(f"PRAGMA cache_size = {self.cache_size_pages}")
        conn.execute(f"PRAGMA mmap_size = {self.memory_limit_mb * 1024 * 1024}")
        
        # Performance optimizations
        conn.execute("PRAGMA synchronous = NORMAL")  # Faster than FULL, still safe
        conn.execute("PRAGMA temp_store = MEMORY")   # Store temp tables in memory
        conn.execute("PRAGMA foreign_keys = ON")     # Enable foreign key constraints
        
        # Query optimization hints
        conn.execute("PRAGMA optimize")  # Optimize for read-heavy workloads
        conn.execute("PRAGMA analysis_limit = 1000")  # Limit analysis for large tables
    
    def _init_db(self):
        """Initialize database schema with enhanced indexing."""
        with self.get_connection() as conn:
            conn.executescript("""
                -- Game positions table with compression support
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY,
                    fen_string TEXT UNIQUE NOT NULL,
                    compressed_state BLOB,
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
                
                -- Game analyses table for D5: Replay Annotator
                CREATE TABLE IF NOT EXISTS game_analyses (
                    id INTEGER PRIMARY KEY,
                    game_id TEXT UNIQUE NOT NULL,
                    players TEXT NOT NULL,  -- JSON array of player names
                    total_moves INTEGER NOT NULL,
                    blunder_count INTEGER DEFAULT 0,
                    average_blunder_severity REAL DEFAULT 0.0,
                    game_data TEXT NOT NULL,  -- JSON game log data
                    analysis_data TEXT,  -- JSON analysis results
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Position database table for D6: Opening Explorer
                CREATE TABLE IF NOT EXISTS position_database (
                    id INTEGER PRIMARY KEY,
                    fen_string TEXT UNIQUE NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    metadata TEXT,  -- JSON metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Position continuations table for D6: Opening Explorer
                CREATE TABLE IF NOT EXISTS position_continuations (
                    id INTEGER PRIMARY KEY,
                    position_id INTEGER NOT NULL,
                    move_data TEXT NOT NULL,  -- JSON move data
                    frequency INTEGER DEFAULT 1,
                    win_rate REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_id) REFERENCES position_database(id) ON DELETE CASCADE
                );
                
                -- Basic indexes for performance
                CREATE INDEX IF NOT EXISTS idx_positions_fen ON positions(fen_string);
                CREATE INDEX IF NOT EXISTS idx_analysis_position ON analysis_results(position_id);
                CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(search_type);
                CREATE INDEX IF NOT EXISTS idx_analysis_agent ON analysis_results(agent_id);
                CREATE INDEX IF NOT EXISTS idx_moves_analysis ON move_sequences(analysis_id);
                CREATE INDEX IF NOT EXISTS idx_stats_type ON performance_stats(search_type);
                CREATE INDEX IF NOT EXISTS idx_analysis_created ON analysis_results(created_at);
                CREATE INDEX IF NOT EXISTS idx_positions_created ON positions(created_at);
                
                -- Enhanced composite indexes for common query patterns
                -- Composite index for analysis lookup by position_id + agent_id + search_type
                CREATE INDEX IF NOT EXISTS idx_analysis_lookup ON analysis_results(position_id, agent_id, search_type, created_at DESC);
                
                -- Composite index for recent analyses by created_at
                CREATE INDEX IF NOT EXISTS idx_analysis_recent ON analysis_results(created_at DESC, position_id);
                
                -- Composite index for performance stats by search_type and updated_at
                CREATE INDEX IF NOT EXISTS idx_stats_recent ON performance_stats(search_type, updated_at DESC);
                
                -- Composite index for analysis results with all commonly accessed columns
                CREATE INDEX IF NOT EXISTS idx_analysis_covering ON analysis_results(
                    position_id, agent_id, search_type, created_at DESC, 
                    best_move, score, search_time, nodes_searched, rollout_count
                );
                
                -- Composite index for positions with all commonly accessed columns
                CREATE INDEX IF NOT EXISTS idx_positions_covering ON positions(
                    fen_string, created_at DESC, id, player_count, compressed_state
                );
                
                -- Partial index for active analyses (non-null best_move)
                CREATE INDEX IF NOT EXISTS idx_analysis_active ON analysis_results(created_at DESC)
                WHERE best_move IS NOT NULL;
                
                -- Partial index for high-quality analyses (score > 0)
                CREATE INDEX IF NOT EXISTS idx_analysis_quality ON analysis_results(search_type, score DESC)
                WHERE score > 0;
                
                -- Indexes for game analyses table
                CREATE INDEX IF NOT EXISTS idx_game_analyses_id ON game_analyses(game_id);
                CREATE INDEX IF NOT EXISTS idx_game_analyses_created ON game_analyses(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_game_analyses_blunders ON game_analyses(blunder_count DESC);
                CREATE INDEX IF NOT EXISTS idx_game_analyses_severity ON game_analyses(average_blunder_severity DESC);
                
                -- Indexes for position database table
                CREATE INDEX IF NOT EXISTS idx_position_database_fen ON position_database(fen_string);
                CREATE INDEX IF NOT EXISTS idx_position_database_frequency ON position_database(frequency DESC);
                CREATE INDEX IF NOT EXISTS idx_position_database_created ON position_database(created_at DESC);
                
                -- Indexes for position continuations table
                CREATE INDEX IF NOT EXISTS idx_position_continuations_position ON position_continuations(position_id);
                CREATE INDEX IF NOT EXISTS idx_position_continuations_frequency ON position_continuations(frequency DESC);
                CREATE INDEX IF NOT EXISTS idx_position_continuations_win_rate ON position_continuations(win_rate DESC);
                
                -- Enable foreign key constraints
                PRAGMA foreign_keys = ON;
            """)
            
            # Analyze tables for query optimization
            conn.execute("ANALYZE")
    
    def cache_position(self, fen_string: str, player_count: int, 
                      compressed_state: Optional[bytes] = None) -> int:
        """
        Cache a position and return its ID.
        
        Args:
            fen_string: FEN-like string representation of position
            player_count: Number of players in the game
            compressed_state: Optional compressed state data
            
        Returns:
            Position ID (existing or newly created)
        """
        with self.get_connection() as conn:
            # Try to insert new position
            cursor = conn.execute(
                "INSERT OR IGNORE INTO positions (fen_string, compressed_state, player_count) VALUES (?, ?, ?)",
                (fen_string, compressed_state, player_count)
            )
            conn.commit()
            
            # Get the position ID (either existing or newly created)
            cursor = conn.execute(
                "SELECT id FROM positions WHERE fen_string = ?",
                (fen_string,)
            )
            return cursor.fetchone()['id']
    
    def cache_position_with_state(self, fen_string: str, player_count: int, 
                                state_data: str) -> int:
        """
        Cache a position with compressed state data.
        
        Args:
            fen_string: FEN-like string representation of position
            player_count: Number of players in the game
            state_data: State data to compress and store
            
        Returns:
            Position ID (existing or newly created)
        """
        compressed_state = self._compress_data(state_data) if self.enable_compression else None
        return self.cache_position(fen_string, player_count, compressed_state)
    
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
    
    def get_compressed_state(self, fen_string: str) -> Optional[bytes]:
        """
        Get compressed state data for a position.
        
        Args:
            fen_string: FEN-like string representation
            
        Returns:
            Compressed state data if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT compressed_state FROM positions WHERE fen_string = ?",
                (fen_string,)
            )
            row = cursor.fetchone()
            return row['compressed_state'] if row else None
    
    def get_decompressed_state(self, fen_string: str) -> Optional[str]:
        """
        Get decompressed state data for a position.
        
        Args:
            fen_string: FEN-like string representation
            
        Returns:
            Decompressed state data if found, None otherwise
        """
        compressed_data = self.get_compressed_state(fen_string)
        if compressed_data is None:
            return None
        return self._decompress_data(compressed_data)
    
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
            # Use optimized query with monitoring
            cursor = self._execute_with_monitoring(conn, """
                SELECT ar.*, p.fen_string FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                WHERE p.fen_string = ? AND ar.agent_id = ? AND ar.search_type = ?
                ORDER BY ar.created_at DESC LIMIT 1
            """, (fen_string, agent_id, search_type), "get_cached_analysis")
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Get principal variation with monitoring
            pv_cursor = self._execute_with_monitoring(conn, """
                SELECT move_text FROM move_sequences 
                WHERE analysis_id = ? ORDER BY move_order
            """, (row['id'],), "get_principal_variation")
            
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
            # Use optimized query with monitoring
            cursor = self._execute_with_monitoring(conn, """
                SELECT ar.*, p.fen_string FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                ORDER BY ar.created_at DESC LIMIT ?
            """, (limit,), "get_recent_analyses")
            
            results = []
            for row in cursor.fetchall():
                # Get principal variation with monitoring
                pv_cursor = self._execute_with_monitoring(conn, """
                    SELECT move_text FROM move_sequences 
                    WHERE analysis_id = ? ORDER BY move_order
                """, (row['id'],), "get_principal_variation")
                
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

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database configuration and performance information.
        
        Returns:
            Dictionary with database configuration and stats
        """
        with self.get_connection() as conn:
            # Get WAL mode status
            cursor = conn.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            # Get cache size
            cursor = conn.execute("PRAGMA cache_size")
            cache_size = cursor.fetchone()[0]
            
            # Get page size
            cursor = conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            # Get database size
            if os.path.exists(self.db_path):
                db_size = os.path.getsize(self.db_path)
                wal_size = os.path.getsize(self.db_path + "-wal") if os.path.exists(self.db_path + "-wal") else 0
            else:
                db_size = wal_size = 0
            
            return {
                'db_path': self.db_path,
                'journal_mode': journal_mode,
                'cache_size_pages': cache_size,
                'page_size_bytes': page_size,
                'memory_limit_mb': self.memory_limit_mb,
                'enable_wal': self.enable_wal,
                'db_size_bytes': db_size,
                'wal_size_bytes': wal_size,
                'total_size_mb': (db_size + wal_size) / (1024 * 1024)
            }
    
    def get_high_quality_analyses(self, search_type: str, limit: int = 10) -> List[CachedAnalysis]:
        """
        Get high-quality analyses (score > 0) for a specific search type.
        
        Args:
            search_type: Type of search ('mcts', 'alpha_beta')
            limit: Maximum number of results to return
            
        Returns:
            List of high-quality CachedAnalysis objects
        """
        with self.get_connection() as conn:
            # Use optimized query with quality index
            cursor = self._execute_with_monitoring(conn, """
                SELECT ar.*, p.fen_string FROM analysis_results ar
                JOIN positions p ON ar.position_id = p.id
                WHERE ar.search_type = ? AND ar.score > 0
                ORDER BY ar.score DESC, ar.created_at DESC LIMIT ?
            """, (search_type, limit), "get_high_quality_analyses")
            
            results = []
            for row in cursor.fetchall():
                # Get principal variation with monitoring
                pv_cursor = self._execute_with_monitoring(conn, """
                    SELECT move_text FROM move_sequences 
                    WHERE analysis_id = ? ORDER BY move_order
                """, (row['id'],), "get_principal_variation")
                
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
    
    def get_analysis_stats_by_type(self, search_type: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific search type.
        
        Args:
            search_type: Type of search ('mcts', 'alpha_beta')
            
        Returns:
            Dictionary with detailed statistics
        """
        with self.get_connection() as conn:
            # Count total analyses
            cursor = self._execute_with_monitoring(conn, """
                SELECT COUNT(*) as total_count,
                       AVG(score) as avg_score,
                       MAX(score) as max_score,
                       MIN(score) as min_score,
                       AVG(search_time) as avg_time,
                       SUM(nodes_searched) as total_nodes,
                       SUM(rollout_count) as total_rollouts
                FROM analysis_results 
                WHERE search_type = ?
            """, (search_type,), "get_analysis_stats_by_type")
            
            row = cursor.fetchone()
            if not row or row['total_count'] == 0:
                return {
                    'search_type': search_type,
                    'total_count': 0,
                    'avg_score': 0.0,
                    'max_score': 0.0,
                    'min_score': 0.0,
                    'avg_time': 0.0,
                    'total_nodes': 0,
                    'total_rollouts': 0
                }
            
            return {
                'search_type': search_type,
                'total_count': row['total_count'],
                'avg_score': row['avg_score'] or 0.0,
                'max_score': row['max_score'] or 0.0,
                'min_score': row['min_score'] or 0.0,
                'avg_time': row['avg_time'] or 0.0,
                'total_nodes': row['total_nodes'] or 0,
                'total_rollouts': row['total_rollouts'] or 0
            }
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        Perform database optimization tasks.
        
        Returns:
            Dictionary with optimization results
        """
        with self.get_connection() as conn:
            # Vacuum database to reclaim space
            conn.execute("VACUUM")
            
            # Analyze tables for better query planning
            conn.execute("ANALYZE")
            
            # Update statistics
            conn.execute("PRAGMA optimize")
            
            # Get optimization results
            cursor = conn.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            cursor = conn.execute("PRAGMA quick_check")
            quick_check_result = cursor.fetchone()[0]
            
            return {
                'integrity_check': integrity_result,
                'quick_check': quick_check_result,
                'optimization_completed': True,
                'timestamp': datetime.now().isoformat()
            } 

    def get_query_performance_stats(self) -> Dict[str, Any]:
        """
        Get query performance statistics.
        
        Returns:
            Dictionary with query performance statistics
        """
        if not self.query_performance_log:
            return {
                'total_queries': 0,
                'average_execution_time_ms': 0.0,
                'slowest_query_type': None,
                'most_frequent_query_type': None,
                'total_execution_time_ms': 0.0
            }
        
        # Calculate statistics
        total_queries = len(self.query_performance_log)
        total_time = sum(q.execution_time_ms for q in self.query_performance_log)
        avg_time = total_time / total_queries if total_queries > 0 else 0.0
        
        # Find slowest query type
        slowest = max(self.query_performance_log, key=lambda q: q.execution_time_ms)
        
        # Find most frequent query type
        query_types = {}
        for query in self.query_performance_log:
            query_types[query.query_type] = query_types.get(query.query_type, 0) + 1
        
        most_frequent = max(query_types.items(), key=lambda x: x[1])[0] if query_types else None
        
        return {
            'total_queries': total_queries,
            'average_execution_time_ms': avg_time,
            'slowest_query_type': slowest.query_type,
            'slowest_execution_time_ms': slowest.execution_time_ms,
            'most_frequent_query_type': most_frequent,
            'total_execution_time_ms': total_time,
            'query_type_counts': query_types
        }
    
    def get_index_usage_stats(self) -> Dict[str, Any]:
        """
        Get index usage statistics.
        
        Returns:
            Dictionary with index usage information
        """
        with self.get_connection() as conn:
            # Get index information
            cursor = conn.execute("""
                SELECT 
                    name,
                    tbl_name,
                    sql
                FROM sqlite_master 
                WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            indexes = []
            for row in cursor.fetchall():
                indexes.append({
                    'name': row['name'],
                    'table': row['tbl_name'],
                    'sql': row['sql']
                })
            
            # Get index usage statistics (if available)
            try:
                cursor = conn.execute("PRAGMA index_list(analysis_results)")
                analysis_indexes = [row['name'] for row in cursor.fetchall()]
            except:
                analysis_indexes = []
            
            try:
                cursor = conn.execute("PRAGMA index_list(positions)")
                position_indexes = [row['name'] for row in cursor.fetchall()]
            except:
                position_indexes = []
            
            return {
                'total_indexes': len(indexes),
                'indexes': indexes,
                'analysis_indexes': analysis_indexes,
                'position_indexes': position_indexes
            } 