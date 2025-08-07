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


@dataclass
class NeuralTrainingSession:
    """Represents a neural training session."""
    session_id: str
    status: str  # 'starting', 'running', 'completed', 'failed', 'stopped'
    progress: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    logs: Optional[List[str]] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    loss_history: Optional[List[float]] = None
    epoch_history: Optional[List[int]] = None
    timestamp_history: Optional[List[str]] = None
    cpu_usage: Optional[List[float]] = None
    memory_usage: Optional[List[float]] = None
    gpu_usage: Optional[List[float]] = None
    estimated_total_time: Optional[float] = None
    current_epoch: int = 0
    total_epochs: int = 0
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NeuralTrainingProgress:
    """Represents neural training progress for a specific epoch."""
    session_id: str
    epoch: int
    loss: float
    timestamp: datetime


@dataclass
class NeuralModel:
    """Represents a trained neural model."""
    model_id: str
    model_path: str
    config: Optional[Dict[str, Any]] = None
    training_session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    model_size_bytes: Optional[int] = None
    architecture: Optional[str] = None  # 'small', 'medium', 'large'
    device_used: Optional[str] = None  # 'cpu', 'cuda'


@dataclass
class NeuralConfiguration:
    """Represents a neural training configuration template."""
    config_id: str
    name: str
    config: Dict[str, Any]
    created_at: Optional[datetime] = None
    is_default: bool = False
    description: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class NeuralEvaluationSession:
    """Represents a neural evaluation session."""
    session_id: str
    status: str  # 'starting', 'running', 'completed', 'failed', 'stopped'
    progress: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class MoveQualityAnalysis:
    """Represents a comprehensive move quality analysis for a position."""
    position_id: int
    session_id: str
    game_phase: str
    total_moves_analyzed: int
    quality_distribution: Dict[str, int]
    average_quality_score: float
    best_move_score: float
    worst_move_score: float
    engine_consensus: Dict[str, float]
    disagreement_level: float
    position_complexity: float
    strategic_themes: List[str]
    tactical_opportunities: List[str]
    analysis_time: float
    created_at: Optional[datetime] = None


@dataclass
class ComprehensiveMoveAnalysis:
    """Represents a comprehensive analysis of a single move."""
    position_analysis_id: int
    move_data: Dict[str, Any]
    alpha_beta_score: Optional[float]
    mcts_score: Optional[float]
    neural_score: Optional[float]
    pattern_score: Optional[float]
    overall_quality_score: float
    quality_tier: str
    confidence_score: float
    strategic_value: float
    tactical_value: float
    risk_assessment: float
    opportunity_value: float
    blocking_score: float
    scoring_score: float
    floor_line_score: float
    timing_score: float
    analysis_time: float
    engines_used: List[str]
    explanation: str
    created_at: Optional[datetime] = None


@dataclass
class ExhaustiveAnalysisSession:
    """Represents an exhaustive analysis session."""
    session_id: str
    mode: str  # 'quick', 'standard', 'deep', 'exhaustive'
    positions_analyzed: int = 0
    total_moves_analyzed: int = 0
    total_analysis_time: float = 0.0
    successful_analyses: int = 0
    failed_analyses: int = 0
    engine_stats: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = 'running'  # 'running', 'completed', 'failed', 'stopped'


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
        
        # Ensure data directory exists (only if path has a directory component)
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create directory if there's a path component
            os.makedirs(db_dir, exist_ok=True)
        
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
                
                -- Neural training sessions table
                CREATE TABLE IF NOT EXISTS neural_training_sessions (
                    session_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL, -- 'starting', 'running', 'completed', 'failed', 'stopped'
                    progress INTEGER DEFAULT 0,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    config TEXT, -- JSON configuration
                    logs TEXT, -- JSON logs array
                    results TEXT, -- JSON results
                    error TEXT,
                    loss_history TEXT, -- JSON array of loss values
                    epoch_history TEXT, -- JSON array of epoch numbers
                    timestamp_history TEXT, -- JSON array of timestamps
                    cpu_usage TEXT, -- JSON array of CPU usage values
                    memory_usage TEXT, -- JSON array of memory usage values
                    gpu_usage TEXT, -- JSON array of GPU usage values
                    estimated_total_time REAL,
                    current_epoch INTEGER DEFAULT 0,
                    total_epochs INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT -- JSON metadata
                );
                
                -- Neural training progress table for detailed epoch tracking
                CREATE TABLE IF NOT EXISTS neural_training_progress (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    epoch INTEGER NOT NULL,
                    loss REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES neural_training_sessions(session_id) ON DELETE CASCADE
                );
                
                -- Neural models table for model versioning
                CREATE TABLE IF NOT EXISTS neural_models (
                    model_id TEXT PRIMARY KEY,
                    model_path TEXT NOT NULL,
                    config TEXT, -- JSON configuration
                    training_session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    performance_metrics TEXT, -- JSON performance metrics
                    model_size_bytes INTEGER,
                    architecture TEXT, -- 'small', 'medium', 'large'
                    device_used TEXT, -- 'cpu', 'cuda'
                    FOREIGN KEY (training_session_id) REFERENCES neural_training_sessions(session_id) ON DELETE SET NULL
                );
                
                -- Neural configurations table for template management
                CREATE TABLE IF NOT EXISTS neural_configurations (
                    config_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL, -- JSON configuration
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_default BOOLEAN DEFAULT FALSE,
                    description TEXT,
                    tags TEXT -- JSON array of tags
                );
                
                -- Neural evaluation sessions table
                CREATE TABLE IF NOT EXISTS neural_evaluation_sessions (
                    session_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL, -- 'starting', 'running', 'completed', 'failed', 'stopped'
                    progress INTEGER DEFAULT 0,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    config TEXT, -- JSON evaluation configuration
                    results TEXT, -- JSON evaluation results
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Move quality analysis tables for exhaustive search integration
                CREATE TABLE IF NOT EXISTS move_quality_analyses (
                    id INTEGER PRIMARY KEY,
                    position_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    game_phase TEXT NOT NULL,
                    total_moves_analyzed INTEGER NOT NULL,
                    quality_distribution TEXT, -- JSON distribution of quality tiers
                    average_quality_score REAL,
                    best_move_score REAL,
                    worst_move_score REAL,
                    engine_consensus TEXT, -- JSON engine agreement scores
                    disagreement_level REAL,
                    position_complexity REAL,
                    strategic_themes TEXT, -- JSON strategic themes identified
                    tactical_opportunities TEXT, -- JSON tactical opportunities
                    analysis_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE
                );
                
                -- Comprehensive move analyses table
                CREATE TABLE IF NOT EXISTS comprehensive_move_analyses (
                    id INTEGER PRIMARY KEY,
                    position_analysis_id INTEGER NOT NULL,
                    move_data TEXT NOT NULL, -- JSON move data
                    alpha_beta_score REAL,
                    mcts_score REAL,
                    neural_score REAL,
                    pattern_score REAL,
                    overall_quality_score REAL,
                    quality_tier TEXT,
                    confidence_score REAL,
                    strategic_value REAL,
                    tactical_value REAL,
                    risk_assessment REAL,
                    opportunity_value REAL,
                    blocking_score REAL,
                    scoring_score REAL,
                    floor_line_score REAL,
                    timing_score REAL,
                    analysis_time REAL,
                    engines_used TEXT, -- JSON list of engines used
                    explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_analysis_id) REFERENCES move_quality_analyses(id) ON DELETE CASCADE
                );
                
                -- Exhaustive analysis sessions table
                CREATE TABLE IF NOT EXISTS exhaustive_analysis_sessions (
                    session_id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL, -- 'quick', 'standard', 'deep', 'exhaustive'
                    positions_analyzed INTEGER DEFAULT 0,
                    total_moves_analyzed INTEGER DEFAULT 0,
                    total_analysis_time REAL DEFAULT 0.0,
                    successful_analyses INTEGER DEFAULT 0,
                    failed_analyses INTEGER DEFAULT 0,
                    engine_stats TEXT, -- JSON engine performance statistics
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'running' -- 'running', 'completed', 'failed', 'stopped'
                );
                
                -- Indexes for neural training tables
                CREATE INDEX IF NOT EXISTS idx_neural_sessions_status ON neural_training_sessions(status);
                CREATE INDEX IF NOT EXISTS idx_neural_sessions_created ON neural_training_sessions(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_neural_sessions_progress ON neural_training_sessions(progress DESC);
                CREATE INDEX IF NOT EXISTS idx_neural_progress_session ON neural_training_progress(session_id);
                CREATE INDEX IF NOT EXISTS idx_neural_progress_epoch ON neural_training_progress(epoch);
                CREATE INDEX IF NOT EXISTS idx_neural_models_session ON neural_models(training_session_id);
                CREATE INDEX IF NOT EXISTS idx_neural_models_created ON neural_models(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_neural_models_architecture ON neural_models(architecture);
                CREATE INDEX IF NOT EXISTS idx_neural_configs_default ON neural_configurations(is_default);
                CREATE INDEX IF NOT EXISTS idx_neural_configs_created ON neural_configurations(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_neural_eval_sessions_status ON neural_evaluation_sessions(status);
                CREATE INDEX IF NOT EXISTS idx_neural_eval_sessions_created ON neural_evaluation_sessions(created_at DESC);
                
                -- Composite indexes for common neural training queries
                CREATE INDEX IF NOT EXISTS idx_neural_sessions_status_created ON neural_training_sessions(status, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_neural_sessions_progress_status ON neural_training_sessions(progress DESC, status);
                CREATE INDEX IF NOT EXISTS idx_neural_models_session_created ON neural_models(training_session_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_neural_configs_default_created ON neural_configurations(is_default, created_at DESC);
                
                -- Indexes for move quality analysis tables
                CREATE INDEX IF NOT EXISTS idx_move_quality_position ON move_quality_analyses(position_id);
                CREATE INDEX IF NOT EXISTS idx_move_quality_session ON move_quality_analyses(session_id);
                CREATE INDEX IF NOT EXISTS idx_move_quality_phase ON move_quality_analyses(game_phase);
                CREATE INDEX IF NOT EXISTS idx_move_quality_created ON move_quality_analyses(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_move_quality_score ON move_quality_analyses(average_quality_score DESC);
                
                -- Indexes for comprehensive move analyses
                CREATE INDEX IF NOT EXISTS idx_comprehensive_position_analysis ON comprehensive_move_analyses(position_analysis_id);
                CREATE INDEX IF NOT EXISTS idx_comprehensive_quality_tier ON comprehensive_move_analyses(quality_tier);
                CREATE INDEX IF NOT EXISTS idx_comprehensive_score ON comprehensive_move_analyses(overall_quality_score DESC);
                CREATE INDEX IF NOT EXISTS idx_comprehensive_created ON comprehensive_move_analyses(created_at DESC);
                
                -- Indexes for exhaustive analysis sessions
                CREATE INDEX IF NOT EXISTS idx_exhaustive_sessions_status ON exhaustive_analysis_sessions(status);
                CREATE INDEX IF NOT EXISTS idx_exhaustive_sessions_mode ON exhaustive_analysis_sessions(mode);
                CREATE INDEX IF NOT EXISTS idx_exhaustive_sessions_created ON exhaustive_analysis_sessions(created_at DESC);
                
                -- Composite indexes for move quality analysis
                CREATE INDEX IF NOT EXISTS idx_move_quality_position_session ON move_quality_analyses(position_id, session_id);
                CREATE INDEX IF NOT EXISTS idx_move_quality_session_created ON move_quality_analyses(session_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_comprehensive_analysis_score ON comprehensive_move_analyses(position_analysis_id, overall_quality_score DESC);
                
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

    # ============================================================================
    # Neural Training Database Methods
    # ============================================================================

    def save_neural_training_session(self, session: NeuralTrainingSession) -> bool:
        """
        Save a neural training session to the database.
        
        Args:
            session: NeuralTrainingSession object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                # Convert lists to JSON strings for storage
                config_json = json.dumps(session.config) if session.config else None
                logs_json = json.dumps(session.logs) if session.logs else None
                results_json = json.dumps(session.results) if session.results else None
                loss_history_json = json.dumps(session.loss_history) if session.loss_history else None
                epoch_history_json = json.dumps(session.epoch_history) if session.epoch_history else None
                timestamp_history_json = json.dumps(session.timestamp_history) if session.timestamp_history else None
                cpu_usage_json = json.dumps(session.cpu_usage) if session.cpu_usage else None
                memory_usage_json = json.dumps(session.memory_usage) if session.memory_usage else None
                gpu_usage_json = json.dumps(session.gpu_usage) if session.gpu_usage else None
                
                metadata_json = json.dumps(session.metadata) if session.metadata else None
                
                cursor = self._execute_with_monitoring(conn, """
                    INSERT OR REPLACE INTO neural_training_sessions (
                        session_id, status, progress, start_time, end_time,
                        config, logs, results, error, loss_history, epoch_history,
                        timestamp_history, cpu_usage, memory_usage, gpu_usage,
                        estimated_total_time, current_epoch, total_epochs, created_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, session.status, session.progress,
                    session.start_time.isoformat() if session.start_time else None,
                    session.end_time.isoformat() if session.end_time else None,
                    config_json, logs_json, results_json, session.error,
                    loss_history_json, epoch_history_json, timestamp_history_json,
                    cpu_usage_json, memory_usage_json, gpu_usage_json,
                    session.estimated_total_time, session.current_epoch, session.total_epochs,
                    session.created_at.isoformat() if session.created_at else datetime.now().isoformat(),
                    metadata_json
                ), "save_neural_training_session")
                
                # Explicitly commit the transaction
                conn.commit()
                
                return True
        except Exception as e:
            print(f"Error saving neural training session: {e}")
            return False

    def get_neural_training_session(self, session_id: str) -> Optional[NeuralTrainingSession]:
        """
        Get a neural training session from the database.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            NeuralTrainingSession object or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = self._execute_with_monitoring(conn, """
                    SELECT * FROM neural_training_sessions WHERE session_id = ?
                """, (session_id,), "get_neural_training_session")
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Parse JSON fields
                config = json.loads(row['config']) if row['config'] else None
                logs = json.loads(row['logs']) if row['logs'] else []
                results = json.loads(row['results']) if row['results'] else None
                loss_history = json.loads(row['loss_history']) if row['loss_history'] else []
                epoch_history = json.loads(row['epoch_history']) if row['epoch_history'] else []
                timestamp_history = json.loads(row['timestamp_history']) if row['timestamp_history'] else []
                cpu_usage = json.loads(row['cpu_usage']) if row['cpu_usage'] else []
                memory_usage = json.loads(row['memory_usage']) if row['memory_usage'] else []
                gpu_usage = json.loads(row['gpu_usage']) if row['gpu_usage'] else []
                
                metadata = json.loads(row['metadata']) if row['metadata'] else None
                
                return NeuralTrainingSession(
                    session_id=row['session_id'],
                    status=row['status'],
                    progress=row['progress'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    config=config,
                    logs=logs,
                    results=results,
                    error=row['error'],
                    loss_history=loss_history,
                    epoch_history=epoch_history,
                    timestamp_history=timestamp_history,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    gpu_usage=gpu_usage,
                    estimated_total_time=row['estimated_total_time'],
                    current_epoch=row['current_epoch'],
                    total_epochs=row['total_epochs'],
                    metadata=metadata,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
        except Exception as e:
            print(f"Error getting neural training session: {e}")
            return None

    def get_all_neural_training_sessions(self, status: Optional[str] = None, 
                                       limit: int = 50) -> List[NeuralTrainingSession]:
        """
        Get all neural training sessions with optional filtering.
        
        Args:
            status: Optional status filter
            limit: Maximum number of sessions to return
            
        Returns:
            List of NeuralTrainingSession objects
        """
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT * FROM neural_training_sessions 
                    WHERE 1=1
                """
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor = self._execute_with_monitoring(conn, query, tuple(params), 
                                                    "get_all_neural_training_sessions")
                
                sessions = []
                for row in cursor.fetchall():
                    # Parse JSON fields
                    config = json.loads(row['config']) if row['config'] else None
                    logs = json.loads(row['logs']) if row['logs'] else []
                    results = json.loads(row['results']) if row['results'] else None
                    loss_history = json.loads(row['loss_history']) if row['loss_history'] else []
                    epoch_history = json.loads(row['epoch_history']) if row['epoch_history'] else []
                    timestamp_history = json.loads(row['timestamp_history']) if row['timestamp_history'] else []
                    cpu_usage = json.loads(row['cpu_usage']) if row['cpu_usage'] else []
                    memory_usage = json.loads(row['memory_usage']) if row['memory_usage'] else []
                    gpu_usage = json.loads(row['gpu_usage']) if row['gpu_usage'] else []
                    metadata = json.loads(row['metadata']) if row['metadata'] else None
                    
                    session = NeuralTrainingSession(
                        session_id=row['session_id'],
                        status=row['status'],
                        progress=row['progress'],
                        start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                        end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                        config=config,
                        logs=logs,
                        results=results,
                        error=row['error'],
                        loss_history=loss_history,
                        epoch_history=epoch_history,
                        timestamp_history=timestamp_history,
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        gpu_usage=gpu_usage,
                        estimated_total_time=row['estimated_total_time'],
                        current_epoch=row['current_epoch'],
                        total_epochs=row['total_epochs'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        metadata=metadata
                    )
                    sessions.append(session)
                
                return sessions
        except Exception as e:
            print(f"Error getting neural training sessions: {e}")
            return []

    def delete_neural_training_session(self, session_id: str) -> bool:
        """
        Delete a neural training session from the database.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = self._execute_with_monitoring(conn, """
                    DELETE FROM neural_training_sessions WHERE session_id = ?
                """, (session_id,), "delete_neural_training_session")
                
                # Explicitly commit the transaction
                conn.commit()
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting neural training session: {e}")
            return False

    def save_neural_model(self, model: NeuralModel) -> bool:
        """
        Save a neural model to the database.
        
        Args:
            model: NeuralModel object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                config_json = json.dumps(model.config) if model.config else None
                performance_metrics_json = json.dumps(model.performance_metrics) if model.performance_metrics else None
                
                cursor = self._execute_with_monitoring(conn, """
                    INSERT OR REPLACE INTO neural_models (
                        model_id, model_path, config, training_session_id,
                        created_at, performance_metrics, model_size_bytes,
                        architecture, device_used
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model.model_id, model.model_path, config_json, model.training_session_id,
                    model.created_at.isoformat() if model.created_at else datetime.now().isoformat(),
                    performance_metrics_json, model.model_size_bytes, model.architecture, model.device_used
                ), "save_neural_model")
                
                # Explicitly commit the transaction
                conn.commit()
                
                return True
        except Exception as e:
            print(f"Error saving neural model: {e}")
            return False

    def get_neural_models(self, architecture: Optional[str] = None) -> List[NeuralModel]:
        """
        Get neural models from the database.
        
        Args:
            architecture: Optional architecture filter
            
        Returns:
            List of NeuralModel objects
        """
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT * FROM neural_models 
                    WHERE 1=1
                """
                params = []
                
                if architecture:
                    query += " AND architecture = ?"
                    params.append(architecture)
                
                query += " ORDER BY created_at DESC"
                
                cursor = self._execute_with_monitoring(conn, query, tuple(params), "get_neural_models")
                
                models = []
                for row in cursor.fetchall():
                    config = json.loads(row['config']) if row['config'] else None
                    performance_metrics = json.loads(row['performance_metrics']) if row['performance_metrics'] else None
                    
                    model = NeuralModel(
                        model_id=row['model_id'],
                        model_path=row['model_path'],
                        config=config,
                        training_session_id=row['training_session_id'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        performance_metrics=performance_metrics,
                        model_size_bytes=row['model_size_bytes'],
                        architecture=row['architecture'],
                        device_used=row['device_used']
                    )
                    models.append(model)
                
                return models
        except Exception as e:
            print(f"Error getting neural models: {e}")
            return []

    def save_neural_configuration(self, config: NeuralConfiguration) -> bool:
        """
        Save a neural configuration template to the database.
        
        Args:
            config: NeuralConfiguration object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                config_json = json.dumps(config.config)
                tags_json = json.dumps(config.tags) if config.tags else None
                
                cursor = self._execute_with_monitoring(conn, """
                    INSERT OR REPLACE INTO neural_configurations (
                        config_id, name, config, created_at, is_default,
                        description, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    config.config_id, config.name, config_json,
                    config.created_at.isoformat() if config.created_at else datetime.now().isoformat(),
                    config.is_default, config.description, tags_json
                ), "save_neural_configuration")
                
                # Explicitly commit the transaction
                conn.commit()
                
                return True
        except Exception as e:
            print(f"Error saving neural configuration: {e}")
            return False

    def get_neural_configurations(self, is_default: Optional[bool] = None) -> List[NeuralConfiguration]:
        """
        Get neural configuration templates from the database.
        
        Args:
            is_default: Optional filter for default configurations
            
        Returns:
            List of NeuralConfiguration objects
        """
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT * FROM neural_configurations 
                    WHERE 1=1
                """
                params = []
                
                if is_default is not None:
                    query += " AND is_default = ?"
                    params.append(is_default)
                
                query += " ORDER BY created_at DESC"
                
                cursor = self._execute_with_monitoring(conn, query, tuple(params), "get_neural_configurations")
                
                configs = []
                for row in cursor.fetchall():
                    config_data = json.loads(row['config'])
                    tags = json.loads(row['tags']) if row['tags'] else None
                    
                    config = NeuralConfiguration(
                        config_id=row['config_id'],
                        name=row['name'],
                        config=config_data,
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        is_default=bool(row['is_default']),
                        description=row['description'],
                        tags=tags
                    )
                    configs.append(config)
                
                return configs
        except Exception as e:
            print(f"Error getting neural configurations: {e}")
            return []

    def get_neural_configuration(self, config_id: str) -> Optional[NeuralConfiguration]:
        """
        Get a specific neural configuration by ID.
        
        Args:
            config_id: Configuration ID to retrieve
            
        Returns:
            NeuralConfiguration object or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = self._execute_with_monitoring(conn, """
                    SELECT * FROM neural_configurations WHERE config_id = ?
                """, (config_id,), "get_neural_configuration")
                
                row = cursor.fetchone()
                if row:
                    config_data = json.loads(row['config'])
                    tags = json.loads(row['tags']) if row['tags'] else None
                    
                    return NeuralConfiguration(
                        config_id=row['config_id'],
                        name=row['name'],
                        config=config_data,
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        is_default=bool(row['is_default']),
                        description=row['description'],
                        tags=tags
                    )
                return None
        except Exception as e:
            print(f"Error getting neural configuration: {e}")
            return None

    def delete_neural_configuration(self, config_id: str) -> bool:
        """Delete a neural configuration."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                DELETE FROM neural_configurations WHERE config_id = ?
            """, (config_id,), "delete_neural_configuration")
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Move Quality Analysis Integration Methods
    
    def save_move_quality_analysis(self, analysis: MoveQualityAnalysis) -> int:
        """Save a move quality analysis to the database."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                INSERT INTO move_quality_analyses (
                    position_id, session_id, game_phase, total_moves_analyzed,
                    quality_distribution, average_quality_score, best_move_score,
                    worst_move_score, engine_consensus, disagreement_level,
                    position_complexity, strategic_themes, tactical_opportunities,
                    analysis_time, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.position_id, analysis.session_id, analysis.game_phase,
                analysis.total_moves_analyzed, json.dumps(analysis.quality_distribution),
                analysis.average_quality_score, analysis.best_move_score,
                analysis.worst_move_score, json.dumps(analysis.engine_consensus),
                analysis.disagreement_level, analysis.position_complexity,
                json.dumps(analysis.strategic_themes), json.dumps(analysis.tactical_opportunities),
                analysis.analysis_time, analysis.created_at or datetime.now()
            ), "save_move_quality_analysis")
            
            analysis_id = cursor.lastrowid
            conn.commit()
            return analysis_id
    
    def save_comprehensive_move_analysis(self, move_analysis: ComprehensiveMoveAnalysis) -> int:
        """Save a comprehensive move analysis to the database."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                INSERT INTO comprehensive_move_analyses (
                    position_analysis_id, move_data, alpha_beta_score, mcts_score,
                    neural_score, pattern_score, overall_quality_score, quality_tier,
                    confidence_score, strategic_value, tactical_value, risk_assessment,
                    opportunity_value, blocking_score, scoring_score, floor_line_score,
                    timing_score, analysis_time, engines_used, explanation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                move_analysis.position_analysis_id, json.dumps(move_analysis.move_data),
                move_analysis.alpha_beta_score, move_analysis.mcts_score,
                move_analysis.neural_score, move_analysis.pattern_score,
                move_analysis.overall_quality_score, move_analysis.quality_tier,
                move_analysis.confidence_score, move_analysis.strategic_value,
                move_analysis.tactical_value, move_analysis.risk_assessment,
                move_analysis.opportunity_value, move_analysis.blocking_score,
                move_analysis.scoring_score, move_analysis.floor_line_score,
                move_analysis.timing_score, move_analysis.analysis_time,
                json.dumps(move_analysis.engines_used), move_analysis.explanation,
                move_analysis.created_at or datetime.now()
            ), "save_comprehensive_move_analysis")
            
            move_analysis_id = cursor.lastrowid
            conn.commit()
            return move_analysis_id
    
    def save_exhaustive_analysis_session(self, session: ExhaustiveAnalysisSession) -> bool:
        """Save an exhaustive analysis session."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                INSERT OR REPLACE INTO exhaustive_analysis_sessions (
                    session_id, mode, positions_analyzed, total_moves_analyzed,
                    total_analysis_time, successful_analyses, failed_analyses,
                    engine_stats, created_at, completed_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.mode, session.positions_analyzed,
                session.total_moves_analyzed, session.total_analysis_time,
                session.successful_analyses, session.failed_analyses,
                json.dumps(session.engine_stats) if session.engine_stats else None,
                session.created_at or datetime.now(), session.completed_at, session.status
            ), "save_exhaustive_analysis_session")
            
            conn.commit()
            return True
    
    def get_move_quality_analysis(self, position_id: int, session_id: str) -> Optional[MoveQualityAnalysis]:
        """Get move quality analysis for a position and session."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                SELECT * FROM move_quality_analyses 
                WHERE position_id = ? AND session_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (position_id, session_id), "get_move_quality_analysis")
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return MoveQualityAnalysis(
                position_id=row['position_id'],
                session_id=row['session_id'],
                game_phase=row['game_phase'],
                total_moves_analyzed=row['total_moves_analyzed'],
                quality_distribution=json.loads(row['quality_distribution']),
                average_quality_score=row['average_quality_score'],
                best_move_score=row['best_move_score'],
                worst_move_score=row['worst_move_score'],
                engine_consensus=json.loads(row['engine_consensus']),
                disagreement_level=row['disagreement_level'],
                position_complexity=row['position_complexity'],
                strategic_themes=json.loads(row['strategic_themes']),
                tactical_opportunities=json.loads(row['tactical_opportunities']),
                analysis_time=row['analysis_time'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
    
    def get_comprehensive_move_analyses(self, position_analysis_id: int) -> List[ComprehensiveMoveAnalysis]:
        """Get all comprehensive move analyses for a position analysis."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                SELECT * FROM comprehensive_move_analyses 
                WHERE position_analysis_id = ?
                ORDER BY overall_quality_score DESC
            """, (position_analysis_id,), "get_comprehensive_move_analyses")
            
            results = []
            for row in cursor.fetchall():
                results.append(ComprehensiveMoveAnalysis(
                    position_analysis_id=row['position_analysis_id'],
                    move_data=json.loads(row['move_data']),
                    alpha_beta_score=row['alpha_beta_score'],
                    mcts_score=row['mcts_score'],
                    neural_score=row['neural_score'],
                    pattern_score=row['pattern_score'],
                    overall_quality_score=row['overall_quality_score'],
                    quality_tier=row['quality_tier'],
                    confidence_score=row['confidence_score'],
                    strategic_value=row['strategic_value'],
                    tactical_value=row['tactical_value'],
                    risk_assessment=row['risk_assessment'],
                    opportunity_value=row['opportunity_value'],
                    blocking_score=row['blocking_score'],
                    scoring_score=row['scoring_score'],
                    floor_line_score=row['floor_line_score'],
                    timing_score=row['timing_score'],
                    analysis_time=row['analysis_time'],
                    engines_used=json.loads(row['engines_used']),
                    explanation=row['explanation'],
                    created_at=datetime.fromisoformat(row['created_at'])
                ))
            
            return results
    
    def get_exhaustive_analysis_session(self, session_id: str) -> Optional[ExhaustiveAnalysisSession]:
        """Get an exhaustive analysis session."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                SELECT * FROM exhaustive_analysis_sessions WHERE session_id = ?
            """, (session_id,), "get_exhaustive_analysis_session")
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ExhaustiveAnalysisSession(
                session_id=row['session_id'],
                mode=row['mode'],
                positions_analyzed=row['positions_analyzed'],
                total_moves_analyzed=row['total_moves_analyzed'],
                total_analysis_time=row['total_analysis_time'],
                successful_analyses=row['successful_analyses'],
                failed_analyses=row['failed_analyses'],
                engine_stats=json.loads(row['engine_stats']) if row['engine_stats'] else None,
                created_at=datetime.fromisoformat(row['created_at']),
                completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                status=row['status']
            )
    
    def get_all_exhaustive_sessions(self, status: Optional[str] = None, limit: int = 50) -> List[ExhaustiveAnalysisSession]:
        """Get all exhaustive analysis sessions."""
        with self.get_connection() as conn:
            if status:
                cursor = self._execute_with_monitoring(conn, """
                    SELECT * FROM exhaustive_analysis_sessions 
                    WHERE status = ? ORDER BY created_at DESC LIMIT ?
                """, (status, limit), "get_all_exhaustive_sessions")
            else:
                cursor = self._execute_with_monitoring(conn, """
                    SELECT * FROM exhaustive_analysis_sessions 
                    ORDER BY created_at DESC LIMIT ?
                """, (limit,), "get_all_exhaustive_sessions")
            
            results = []
            for row in cursor.fetchall():
                results.append(ExhaustiveAnalysisSession(
                    session_id=row['session_id'],
                    mode=row['mode'],
                    positions_analyzed=row['positions_analyzed'],
                    total_moves_analyzed=row['total_moves_analyzed'],
                    total_analysis_time=row['total_analysis_time'],
                    successful_analyses=row['successful_analyses'],
                    failed_analyses=row['failed_analyses'],
                    engine_stats=json.loads(row['engine_stats']) if row['engine_stats'] else None,
                    created_at=datetime.fromisoformat(row['created_at']),
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                    status=row['status']
                ))
            
            return results
    
    def get_best_move_quality_analyses(self, limit: int = 10) -> List[MoveQualityAnalysis]:
        """Get the best move quality analyses (highest average scores)."""
        with self.get_connection() as conn:
            cursor = self._execute_with_monitoring(conn, """
                SELECT mqa.*, p.fen_string FROM move_quality_analyses mqa
                JOIN positions p ON mqa.position_id = p.id
                ORDER BY mqa.average_quality_score DESC LIMIT ?
            """, (limit,), "get_best_move_quality_analyses")
            
            results = []
            for row in cursor.fetchall():
                results.append(MoveQualityAnalysis(
                    position_id=row['position_id'],
                    session_id=row['session_id'],
                    game_phase=row['game_phase'],
                    total_moves_analyzed=row['total_moves_analyzed'],
                    quality_distribution=json.loads(row['quality_distribution']),
                    average_quality_score=row['average_quality_score'],
                    best_move_score=row['best_move_score'],
                    worst_move_score=row['worst_move_score'],
                    engine_consensus=json.loads(row['engine_consensus']),
                    disagreement_level=row['disagreement_level'],
                    position_complexity=row['position_complexity'],
                    strategic_themes=json.loads(row['strategic_themes']),
                    tactical_opportunities=json.loads(row['tactical_opportunities']),
                    analysis_time=row['analysis_time'],
                    created_at=datetime.fromisoformat(row['created_at'])
                ))
            
            return results 
    
    def save_neural_evaluation_session(self, session: NeuralEvaluationSession) -> bool:
        """Save a neural evaluation session to the database."""
        with self.get_connection() as conn:
            config_json = json.dumps(session.config) if session.config else None
            results_json = json.dumps(session.results) if session.results else None
            
            cursor = self._execute_with_monitoring(conn, """
                INSERT OR REPLACE INTO neural_evaluation_sessions (
                    session_id, status, progress, start_time, end_time,
                    config, results, error, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.status, session.progress,
                session.start_time.isoformat() if session.start_time else None,
                session.end_time.isoformat() if session.end_time else None,
                config_json, results_json, session.error,
                session.created_at.isoformat() if session.created_at else datetime.now().isoformat()
            ), "save_neural_evaluation_session")
            
            conn.commit()
            return True
    
    def get_neural_evaluation_sessions(self, status: Optional[str] = None, 
                                     limit: int = 50) -> List[NeuralEvaluationSession]:
        """Get neural evaluation sessions from the database."""
        with self.get_connection() as conn:
            if status:
                cursor = self._execute_with_monitoring(conn, """
                    SELECT * FROM neural_evaluation_sessions 
                    WHERE status = ? ORDER BY created_at DESC LIMIT ?
                """, (status, limit), "get_neural_evaluation_sessions")
            else:
                cursor = self._execute_with_monitoring(conn, """
                    SELECT * FROM neural_evaluation_sessions 
                    ORDER BY created_at DESC LIMIT ?
                """, (limit,), "get_neural_evaluation_sessions")
            
            sessions = []
            for row in cursor.fetchall():
                config = json.loads(row['config']) if row['config'] else None
                results = json.loads(row['results']) if row['results'] else None
                
                session = NeuralEvaluationSession(
                    session_id=row['session_id'],
                    status=row['status'],
                    progress=row['progress'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    config=config,
                    results=results,
                    error=row['error'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                sessions.append(session)
            
            return sessions 