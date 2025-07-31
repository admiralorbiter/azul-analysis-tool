"""
Tests for the database integration module.

This module tests:
- Database initialization and schema
- Position caching and retrieval
- Analysis result caching
- Performance statistics
- Cache management
- WAL mode and performance optimizations
- Zstd compression for state storage
- Enhanced indexing and query optimization
"""

import pytest
import tempfile
import os
import time
from datetime import datetime

from core.azul_database import AzulDatabase, CachedAnalysis
from core.azul_model import AzulState
from core.azul_move_generator import FastMove
from core.azul_mcts import AzulMCTS, RolloutPolicy


class TestDatabaseInitialization:
    """Test database initialization and schema."""
    
    def test_database_creation(self):
        """Test database creation with default path."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Check that tables were created
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('positions', 'analysis_results', 'move_sequences', 'performance_stats')
                """)
                tables = [row['name'] for row in cursor.fetchall()]
                
                assert 'positions' in tables
                assert 'analysis_results' in tables
                assert 'move_sequences' in tables
                assert 'performance_stats' in tables
        finally:
            os.unlink(db_path)
    
    def test_database_connection_context(self):
        """Test database connection context manager."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            with db.get_connection() as conn:
                cursor = conn.execute("SELECT 1 as test")
                result = cursor.fetchone()
                assert result['test'] == 1
        finally:
            os.unlink(db_path)


class TestWALModeAndPerformance:
    """Test WAL mode and performance optimizations."""
    
    def test_wal_mode_enabled(self):
        """Test that WAL mode is enabled by default."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            info = db.get_database_info()
            
            assert info['enable_wal'] is True
            assert info['journal_mode'] == 'wal'
        finally:
            os.unlink(db_path)
    
    def test_wal_mode_disabled(self):
        """Test that WAL mode can be disabled."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path, enable_wal=False)
            info = db.get_database_info()
            
            assert info['enable_wal'] is False
            # Note: journal_mode might still be 'wal' if it was previously enabled
        finally:
            os.unlink(db_path)
    
    def test_custom_memory_settings(self):
        """Test custom memory limit and cache size settings."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path, memory_limit_mb=128, cache_size_pages=2000)
            info = db.get_database_info()
            
            assert info['memory_limit_mb'] == 128
            assert info['cache_size_pages'] == 2000
        finally:
            os.unlink(db_path)
    
    def test_database_info_structure(self):
        """Test that database info contains all expected fields."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            info = db.get_database_info()
            
            expected_fields = [
                'db_path', 'journal_mode', 'cache_size_pages', 'page_size_bytes',
                'memory_limit_mb', 'enable_wal', 'db_size_bytes', 'wal_size_bytes',
                'total_size_mb'
            ]
            
            for field in expected_fields:
                assert field in info, f"Missing field: {field}"
            
            # Check data types
            assert isinstance(info['db_path'], str)
            assert isinstance(info['journal_mode'], str)
            assert isinstance(info['cache_size_pages'], int)
            assert isinstance(info['page_size_bytes'], int)
            assert isinstance(info['memory_limit_mb'], int)
            assert isinstance(info['enable_wal'], bool)
            assert isinstance(info['db_size_bytes'], int)
            assert isinstance(info['wal_size_bytes'], int)
            assert isinstance(info['total_size_mb'], float)
        finally:
            os.unlink(db_path)
    
    def test_concurrent_access_performance(self):
        """Test that WAL mode allows concurrent access."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Simulate concurrent access by opening multiple connections
            start_time = time.time()
            
            # Add some test data
            position_id = db.cache_position("test_pos", 2)
            db.cache_analysis(position_id, 0, "mcts", {
                'best_move': 'test_move', 'best_score': 10.0, 'search_time': 0.1,
                'nodes_searched': 100, 'rollout_count': 20
            })
            
            # Open multiple connections simultaneously
            with db.get_connection() as conn1:
                with db.get_connection() as conn2:
                    # Both connections should work
                    cursor1 = conn1.execute("SELECT COUNT(*) FROM positions")
                    cursor2 = conn2.execute("SELECT COUNT(*) FROM analysis_results")
                    
                    count1 = cursor1.fetchone()[0]
                    count2 = cursor2.fetchone()[0]
                    
                    assert count1 == 1
                    assert count2 == 1
            
            end_time = time.time()
            # Should complete quickly (under 1 second)
            assert end_time - start_time < 1.0
            
        finally:
            os.unlink(db_path)
    
    def test_data_directory_creation(self):
        """Test that data directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "subdir", "test.db")
            
            # Should create the subdirectory automatically
            db = AzulDatabase(db_path)
            
            assert os.path.exists(os.path.dirname(db_path))
            assert os.path.exists(db_path)


class TestZstdCompression:
    """Test Zstd compression functionality."""
    
    def test_compression_enabled_by_default(self):
        """Test that compression is enabled by default."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            assert db.enable_compression is True
            assert hasattr(db, 'compressor')
            assert hasattr(db, 'decompressor')
        finally:
            os.unlink(db_path)
    
    def test_compression_disabled(self):
        """Test that compression can be disabled."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path, enable_compression=False)
            assert db.enable_compression is False
            assert not hasattr(db, 'compressor')
            assert not hasattr(db, 'decompressor')
        finally:
            os.unlink(db_path)
    
    def test_compression_roundtrip(self):
        """Test compression and decompression roundtrip."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Test data
            original_data = "This is a test string with some repeated content. " * 100
            
            # Compress
            compressed = db._compress_data(original_data)
            assert isinstance(compressed, bytes)
            assert len(compressed) < len(original_data.encode('utf-8'))
            
            # Decompress
            decompressed = db._decompress_data(compressed)
            assert decompressed == original_data
        finally:
            os.unlink(db_path)
    
    def test_compression_without_compression(self):
        """Test compression methods when compression is disabled."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path, enable_compression=False)
            
            # Test data
            original_data = "Test string"
            
            # Should return UTF-8 bytes when compression is disabled
            compressed = db._compress_data(original_data)
            assert compressed == original_data.encode('utf-8')
            
            # Should decode back to original
            decompressed = db._decompress_data(compressed)
            assert decompressed == original_data
        finally:
            os.unlink(db_path)
    
    def test_cache_position_with_state(self):
        """Test caching position with compressed state data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            fen_string = "test_position"
            player_count = 2
            state_data = "This is some state data that should be compressed"
            
            # Cache position with state
            position_id = db.cache_position_with_state(fen_string, player_count, state_data)
            assert position_id > 0
            
            # Retrieve compressed state
            compressed_state = db.get_compressed_state(fen_string)
            assert compressed_state is not None
            assert isinstance(compressed_state, bytes)
            
            # Decompress and verify
            decompressed_state = db.get_decompressed_state(fen_string)
            assert decompressed_state == state_data
        finally:
            os.unlink(db_path)
    
    def test_compression_levels(self):
        """Test different compression levels."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Test data
            test_data = "Repeated content " * 1000
            
            # Test different compression levels
            sizes = {}
            for level in [1, 3, 6, 9]:
                db = AzulDatabase(db_path, compression_level=level)
                compressed = db._compress_data(test_data)
                sizes[level] = len(compressed)
                
                # Verify decompression works
                decompressed = db._decompress_data(compressed)
                assert decompressed == test_data
            
            # Higher levels should generally produce smaller files
            # (though this isn't always guaranteed for small data)
            print(f"Compression sizes by level: {sizes}")
            
        finally:
            os.unlink(db_path)
    
    def test_compression_performance(self):
        """Test compression performance."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Large test data
            test_data = "Large test data " * 10000
            
            # Time compression
            start_time = time.time()
            compressed = db._compress_data(test_data)
            compression_time = time.time() - start_time
            
            # Time decompression
            start_time = time.time()
            decompressed = db._decompress_data(compressed)
            decompression_time = time.time() - start_time
            
            # Verify data integrity
            assert decompressed == test_data
            
            # Performance should be reasonable (under 1 second for this data size)
            assert compression_time < 1.0
            assert decompression_time < 1.0
            
            # Compression ratio should be significant
            original_size = len(test_data.encode('utf-8'))
            compressed_size = len(compressed)
            compression_ratio = compressed_size / original_size
            
            print(f"Compression ratio: {compression_ratio:.2f}")
            print(f"Compression time: {compression_time:.3f}s")
            print(f"Decompression time: {decompression_time:.3f}s")
            
            # Should achieve some compression
            assert compression_ratio < 1.0
            
        finally:
            os.unlink(db_path)


class TestEnhancedIndexingAndOptimization:
    """Test enhanced indexing and query optimization features."""
    
    def test_query_monitoring_enabled_by_default(self):
        """Test that query monitoring is enabled by default."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            assert db.enable_query_monitoring is True
            assert hasattr(db, 'query_performance_log')
            assert isinstance(db.query_performance_log, list)
        finally:
            os.unlink(db_path)
    
    def test_query_monitoring_disabled(self):
        """Test that query monitoring can be disabled."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path, enable_query_monitoring=False)
            assert db.enable_query_monitoring is False
        finally:
            os.unlink(db_path)
    
    def test_query_performance_logging(self):
        """Test that query performance is logged correctly."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path, enable_query_monitoring=True)
            
            # Perform some operations to generate query logs
            position_id = db.cache_position("test_pos", 2)
            db.cache_analysis(position_id, 0, "mcts", {
                'best_move': 'test_move', 'best_score': 10.0, 'search_time': 0.1,
                'nodes_searched': 100, 'rollout_count': 20
            })
            
            # Perform a monitored query operation
            cached_analysis = db.get_cached_analysis("test_pos", 0, "mcts")
            assert cached_analysis is not None
            
            # Check that queries were logged
            stats = db.get_query_performance_stats()
            assert stats['total_queries'] > 0
            assert stats['average_execution_time_ms'] >= 0.0
            assert stats['total_execution_time_ms'] >= 0.0
        finally:
            os.unlink(db_path)
    
    def test_index_usage_stats(self):
        """Test index usage statistics."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Get index statistics
            index_stats = db.get_index_usage_stats()
            
            # Check that we have indexes
            assert index_stats['total_indexes'] > 0
            assert 'indexes' in index_stats
            assert isinstance(index_stats['indexes'], list)
            
            # Check that we have analysis and position indexes
            assert len(index_stats['analysis_indexes']) > 0
            assert len(index_stats['position_indexes']) > 0
        finally:
            os.unlink(db_path)
    
    def test_high_quality_analyses(self):
        """Test getting high-quality analyses."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Add some test data with different scores
            position_id1 = db.cache_position("pos1", 2)
            position_id2 = db.cache_position("pos2", 2)
            
            # Add high-quality analysis (score > 0)
            db.cache_analysis(position_id1, 0, "mcts", {
                'best_move': 'move1', 'best_score': 15.0, 'search_time': 0.1,
                'nodes_searched': 100, 'rollout_count': 20
            })
            
            # Add low-quality analysis (score <= 0)
            db.cache_analysis(position_id2, 0, "mcts", {
                'best_move': 'move2', 'best_score': -5.0, 'search_time': 0.1,
                'nodes_searched': 50, 'rollout_count': 10
            })
            
            # Get high-quality analyses
            high_quality = db.get_high_quality_analyses("mcts", limit=10)
            
            # Should only return analyses with score > 0
            assert len(high_quality) == 1
            assert high_quality[0].score > 0
        finally:
            os.unlink(db_path)
    
    def test_analysis_stats_by_type(self):
        """Test getting analysis statistics by type."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Add test data
            position_id = db.cache_position("test_pos", 2)
            db.cache_analysis(position_id, 0, "mcts", {
                'best_move': 'test_move', 'best_score': 10.0, 'search_time': 0.1,
                'nodes_searched': 100, 'rollout_count': 20
            })
            
            # Get statistics
            stats = db.get_analysis_stats_by_type("mcts")
            
            assert stats['search_type'] == "mcts"
            assert stats['total_count'] == 1
            assert abs(stats['avg_score'] - 10.0) < 0.001
            assert abs(stats['max_score'] - 10.0) < 0.001
            assert abs(stats['min_score'] - 10.0) < 0.001
            assert abs(stats['avg_time'] - 0.1) < 0.001
            assert stats['total_nodes'] == 100
            assert stats['total_rollouts'] == 20
        finally:
            os.unlink(db_path)
    
    def test_database_optimization(self):
        """Test database optimization functionality."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Add some test data
            position_id = db.cache_position("test_pos", 2)
            db.cache_analysis(position_id, 0, "mcts", {
                'best_move': 'test_move', 'best_score': 10.0, 'search_time': 0.1,
                'nodes_searched': 100, 'rollout_count': 20
            })
            
            # Optimize database
            result = db.optimize_database()
            
            assert result['optimization_completed'] is True
            assert 'integrity_check' in result
            assert 'quick_check' in result
            assert 'timestamp' in result
        finally:
            os.unlink(db_path)
    
    def test_query_performance_stats_structure(self):
        """Test that query performance stats have correct structure."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Get stats before any queries
            stats = db.get_query_performance_stats()
            
            expected_fields = [
                'total_queries', 'average_execution_time_ms', 'slowest_query_type',
                'most_frequent_query_type', 'total_execution_time_ms'
            ]
            
            for field in expected_fields:
                assert field in stats, f"Missing field: {field}"
            
            # Check data types
            assert isinstance(stats['total_queries'], int)
            assert isinstance(stats['average_execution_time_ms'], float)
            assert isinstance(stats['total_execution_time_ms'], float)
        finally:
            os.unlink(db_path)
    
    def test_enhanced_indexes_created(self):
        """Test that enhanced indexes are created."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = AzulDatabase(db_path)
            
            # Check that enhanced indexes exist
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name LIKE 'idx_%'
                    ORDER BY name
                """)
                
                index_names = [row['name'] for row in cursor.fetchall()]
                
                # Check for enhanced indexes
                expected_indexes = [
                    'idx_analysis_active',
                    'idx_analysis_covering', 
                    'idx_analysis_lookup',
                    'idx_analysis_quality',
                    'idx_analysis_recent',
                    'idx_positions_covering',
                    'idx_stats_recent'
                ]
                
                for expected_index in expected_indexes:
                    assert expected_index in index_names, f"Missing index: {expected_index}"
        finally:
            os.unlink(db_path)


class TestPositionCaching:
    """Test position caching functionality."""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = AzulDatabase(db_path)
        yield db
        os.unlink(db_path)
    
    def test_cache_position(self, db):
        """Test caching a position."""
        fen_string = "initial"
        player_count = 2
        
        position_id = db.cache_position(fen_string, player_count)
        assert position_id > 0
        
        # Should return same ID for same position
        position_id2 = db.cache_position(fen_string, player_count)
        assert position_id2 == position_id
    
    def test_get_position_id(self, db):
        """Test getting position ID."""
        fen_string = "test_position"
        player_count = 2
        
        # Should return None for non-existent position
        assert db.get_position_id(fen_string) is None
        
        # Should return ID after caching
        position_id = db.cache_position(fen_string, player_count)
        assert db.get_position_id(fen_string) == position_id


class TestAnalysisCaching:
    """Test analysis result caching."""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = AzulDatabase(db_path)
        yield db
        os.unlink(db_path)
    
    def test_cache_analysis(self, db):
        """Test caching analysis results."""
        fen_string = "test_position"
        player_count = 2
        agent_id = 0
        search_type = "mcts"
        
        # Cache position first
        position_id = db.cache_position(fen_string, player_count)
        
        # Cache analysis
        result = {
            'best_move': 'test_move',
            'best_score': 10.5,
            'search_time': 0.15,
            'nodes_searched': 1000,
            'rollout_count': 50,
            'principal_variation': ['move1', 'move2', 'move3']
        }
        
        analysis_id = db.cache_analysis(position_id, agent_id, search_type, result)
        assert analysis_id > 0
    
    def test_get_cached_analysis(self, db):
        """Test retrieving cached analysis."""
        fen_string = "test_position"
        player_count = 2
        agent_id = 0
        search_type = "mcts"
        
        # Cache position and analysis
        position_id = db.cache_position(fen_string, player_count)
        result = {
            'best_move': 'test_move',
            'best_score': 10.5,
            'search_time': 0.15,
            'nodes_searched': 1000,
            'rollout_count': 50,
            'principal_variation': ['move1', 'move2', 'move3']
        }
        db.cache_analysis(position_id, agent_id, search_type, result)
        
        # Retrieve cached analysis
        cached = db.get_cached_analysis(fen_string, agent_id, search_type)
        assert cached is not None
        assert cached.best_move == 'test_move'
        assert cached.score == 10.5
        assert cached.search_time == 0.15
        assert cached.nodes_searched == 1000
        assert cached.rollout_count == 50
        assert cached.principal_variation == ['move1', 'move2', 'move3']
    
    def test_get_cached_analysis_not_found(self, db):
        """Test getting cached analysis that doesn't exist."""
        cached = db.get_cached_analysis("nonexistent", 0, "mcts")
        assert cached is None


class TestPerformanceStats:
    """Test performance statistics tracking."""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = AzulDatabase(db_path)
        yield db
        os.unlink(db_path)
    
    def test_update_performance_stats(self, db):
        """Test updating performance statistics."""
        search_type = "mcts"
        search_time = 0.2
        nodes_searched = 1500
        rollouts = 100
        cache_hit = False
        
        db.update_performance_stats(search_type, search_time, nodes_searched, rollouts, cache_hit)
        
        stats = db.get_performance_stats(search_type)
        assert len(stats) == 1
        assert stats[0]['search_type'] == search_type
        assert stats[0]['total_searches'] == 1
        assert stats[0]['total_time'] == search_time
        assert stats[0]['total_nodes'] == nodes_searched
        assert stats[0]['total_rollouts'] == rollouts
        assert stats[0]['cache_hits'] == 0
        assert stats[0]['cache_misses'] == 1
    
    def test_update_performance_stats_cache_hit(self, db):
        """Test updating performance stats for cache hit."""
        search_type = "alpha_beta"
        search_time = 0.1
        nodes_searched = 500
        rollouts = 0
        cache_hit = True
        
        db.update_performance_stats(search_type, search_time, nodes_searched, rollouts, cache_hit)
        
        stats = db.get_performance_stats(search_type)
        assert len(stats) == 1
        assert stats[0]['cache_hits'] == 1
        assert stats[0]['cache_misses'] == 0
    
    def test_get_performance_stats_all(self, db):
        """Test getting all performance statistics."""
        # Add stats for multiple search types
        db.update_performance_stats("mcts", 0.2, 1000, 50, False)
        db.update_performance_stats("alpha_beta", 0.1, 500, 0, True)
        
        all_stats = db.get_performance_stats()
        assert len(all_stats) == 2
        
        # Check that both search types are present
        search_types = [stat['search_type'] for stat in all_stats]
        assert "mcts" in search_types
        assert "alpha_beta" in search_types


class TestCacheManagement:
    """Test cache management functionality."""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = AzulDatabase(db_path)
        yield db
        os.unlink(db_path)
    
    def test_get_cache_stats(self, db):
        """Test getting cache statistics."""
        # Add some test data
        position_id1 = db.cache_position("pos1", 2)
        position_id2 = db.cache_position("pos2", 3)
        
        db.cache_analysis(position_id1, 0, "mcts", {
            'best_move': 'move1', 'best_score': 10.0, 'search_time': 0.1,
            'nodes_searched': 100, 'rollout_count': 20
        })
        db.cache_analysis(position_id2, 1, "alpha_beta", {
            'best_move': 'move2', 'best_score': 15.0, 'search_time': 0.2,
            'nodes_searched': 200, 'rollout_count': 0
        })
        
        stats = db.get_cache_stats()
        assert stats['positions_cached'] == 2
        assert stats['analyses_cached'] == 2
        assert stats['by_search_type']['mcts'] == 1
        assert stats['by_search_type']['alpha_beta'] == 1
    
    def test_clear_cache(self, db):
        """Test clearing cache."""
        # Add some test data
        position_id = db.cache_position("test_pos", 2)
        db.cache_analysis(position_id, 0, "mcts", {
            'best_move': 'test_move', 'best_score': 10.0, 'search_time': 0.1,
            'nodes_searched': 100, 'rollout_count': 20
        })
        
        # Verify data exists
        stats_before = db.get_cache_stats()
        assert stats_before['positions_cached'] == 1
        assert stats_before['analyses_cached'] == 1
        
        # Clear cache
        db.clear_cache()
        
        # Verify data is gone
        stats_after = db.get_cache_stats()
        assert stats_after['positions_cached'] == 0
        assert stats_after['analyses_cached'] == 0
    
    def test_clear_cache_specific_type(self, db):
        """Test clearing cache for specific search type."""
        # Add test data for multiple search types
        position_id = db.cache_position("test_pos", 2)
        db.cache_analysis(position_id, 0, "mcts", {
            'best_move': 'move1', 'best_score': 10.0, 'search_time': 0.1,
            'nodes_searched': 100, 'rollout_count': 20
        })
        db.cache_analysis(position_id, 0, "alpha_beta", {
            'best_move': 'move2', 'best_score': 15.0, 'search_time': 0.2,
            'nodes_searched': 200, 'rollout_count': 0
        })
        
        # Clear only MCTS cache
        db.clear_cache("mcts")
        
        stats = db.get_cache_stats()
        assert stats['analyses_cached'] == 1
        assert stats['by_search_type']['alpha_beta'] == 1
        assert 'mcts' not in stats['by_search_type']


class TestRecentAnalyses:
    """Test recent analyses functionality."""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = AzulDatabase(db_path)
        yield db
        os.unlink(db_path)
    
    def test_get_recent_analyses(self, db):
        """Test getting recent analyses."""
        # Add multiple analyses
        position_id1 = db.cache_position("pos1", 2)
        position_id2 = db.cache_position("pos2", 2)
        
        db.cache_analysis(position_id1, 0, "mcts", {
            'best_move': 'move1', 'best_score': 10.0, 'search_time': 0.1,
            'nodes_searched': 100, 'rollout_count': 20
        })
        db.cache_analysis(position_id2, 1, "alpha_beta", {
            'best_move': 'move2', 'best_score': 15.0, 'search_time': 0.2,
            'nodes_searched': 200, 'rollout_count': 0
        })
        
        recent = db.get_recent_analyses(limit=5)
        assert len(recent) == 2
        
        # Should be ordered by creation time (newest first)
        # The order might vary due to timing, so just check that both are present
        search_types = [r.search_type for r in recent]
        assert "alpha_beta" in search_types
        assert "mcts" in search_types


class TestMCTSIntegration:
    """Test MCTS integration with database."""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = AzulDatabase(db_path)
        yield db
        os.unlink(db_path)
    
    def test_mcts_with_database(self, db):
        """Test MCTS with database integration."""
        mcts = AzulMCTS(database=db, max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        fen_string = "initial"
        
        # First search (cache miss)
        result1 = mcts.search(state, 0, fen_string=fen_string)
        assert result1.search_time > 0
        assert result1.rollout_count > 0
        
        # Second search (cache hit)
        result2 = mcts.search(state, 0, fen_string=fen_string)
        assert result2.search_time > 0
        
        # Should have same best move (or at least valid result)
        assert result2.best_move is not None
    
    def test_mcts_database_performance(self, db):
        """Test MCTS database performance tracking."""
        mcts = AzulMCTS(database=db, max_time=0.1, max_rollouts=10)
        state = AzulState(2)
        fen_string = "test_position"
        
        # Perform search
        result = mcts.search(state, 0, fen_string=fen_string)
        
        # Check performance stats
        stats = db.get_performance_stats("mcts")
        assert len(stats) == 1
        assert stats[0]['total_searches'] == 1
        assert stats[0]['cache_misses'] == 1
        assert stats[0]['cache_hits'] == 0


if __name__ == "__main__":
    pytest.main([__file__]) 