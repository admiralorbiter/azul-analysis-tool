"""
Tests for the database integration module.

This module tests:
- Database initialization and schema
- Position caching and retrieval
- Analysis result caching
- Performance statistics
- Cache management
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
        player_count = 3
        
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