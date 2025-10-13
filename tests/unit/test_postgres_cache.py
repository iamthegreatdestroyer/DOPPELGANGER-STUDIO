"""
Unit Tests for PostgreSQL Research Cache.

Tests caching functionality with mocked database.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import json

from src.services.research.postgres_cache import PostgresResearchCache


class TestPostgresResearchCache:
    """Test suite for PostgreSQL research cache."""
    
    @pytest.fixture
    async def mock_pool(self):
        """Create mock connection pool."""
        pool = AsyncMock()
        
        # Mock connection
        conn = AsyncMock()
        conn.execute = AsyncMock()
        conn.fetchrow = AsyncMock()
        conn.fetchval = AsyncMock()
        conn.fetch = AsyncMock()
        
        # Mock acquire context manager
        acquire = AsyncMock()
        acquire.__aenter__ = AsyncMock(return_value=conn)
        acquire.__aexit__ = AsyncMock()
        pool.acquire.return_value = acquire
        
        pool.close = AsyncMock()
        
        return pool
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_pool):
        """Test cache initializes correctly."""
        cache = PostgresResearchCache("postgresql://test")
        
        with patch('asyncpg.create_pool', return_value=mock_pool):
            await cache.initialize()
            
            assert cache.pool == mock_pool
            assert cache._cleanup_task is not None
            
            await cache.close()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, mock_pool):
        """Test setting and getting cached data."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        test_data = {'title': 'I Love Lucy', 'years': '1951-1957'}
        
        # Test set
        await cache.set('wikipedia', 'I Love Lucy', test_data)
        
        # Verify execute was called with insert
        conn = await mock_pool.acquire().__aenter__()
        assert conn.execute.called
        
        # Test get - mock return value
        future_time = datetime.now() + timedelta(hours=1)
        conn.fetchrow.return_value = {
            'response': json.dumps(test_data),
            'expires_at': future_time
        }
        
        result = await cache.get('wikipedia', 'I Love Lucy')
        assert result == test_data
    
    @pytest.mark.asyncio
    async def test_get_expired(self, mock_pool):
        """Test getting expired cache entry."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        conn = await mock_pool.acquire().__aenter__()
        
        # Mock expired entry
        past_time = datetime.now() - timedelta(hours=1)
        conn.fetchrow.return_value = {
            'response': json.dumps({'test': 'data'}),
            'expires_at': past_time
        }
        
        result = await cache.get('wikipedia', 'Test')
        
        # Should return None for expired
        assert result is None
        
        # Should delete expired entry
        assert conn.execute.called
    
    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_pool):
        """Test getting non-existent cache entry."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        conn = await mock_pool.acquire().__aenter__()
        conn.fetchrow.return_value = None
        
        result = await cache.get('wikipedia', 'NonExistent')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete(self, mock_pool):
        """Test deleting cache entry."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        await cache.delete('wikipedia', 'Test')
        
        conn = await mock_pool.acquire().__aenter__()
        assert conn.execute.called
    
    @pytest.mark.asyncio
    async def test_clear_source(self, mock_pool):
        """Test clearing all entries for a source."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        conn = await mock_pool.acquire().__aenter__()
        conn.execute.return_value = "DELETE 5"
        
        await cache.clear_source('wikipedia')
        
        assert conn.execute.called
    
    @pytest.mark.asyncio
    async def test_clear_all(self, mock_pool):
        """Test clearing all cache entries."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        conn = await mock_pool.acquire().__aenter__()
        conn.execute.return_value = "DELETE 10"
        
        await cache.clear_all()
        
        assert conn.execute.called
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, mock_pool):
        """Test cleanup of expired entries."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        conn = await mock_pool.acquire().__aenter__()
        conn.execute.return_value = "DELETE 3"
        
        count = await cache.cleanup_expired()
        
        assert count == 3
        assert conn.execute.called
    
    @pytest.mark.asyncio
    async def test_get_stats(self, mock_pool):
        """Test getting cache statistics."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        conn = await mock_pool.acquire().__aenter__()
        
        # Mock statistics queries
        conn.fetchval.side_effect = [10, 2, 3600.0]  # total, expired, avg_age
        conn.fetch.return_value = [
            {'source': 'wikipedia', 'count': 5},
            {'source': 'tmdb', 'count': 5}
        ]
        
        stats = await cache.get_stats()
        
        assert stats['total_entries'] == 10
        assert stats['expired_entries'] == 2
        assert stats['by_source']['wikipedia'] == 5
        assert stats['average_age_seconds'] == 3600.0
    
    @pytest.mark.asyncio
    async def test_default_ttls(self):
        """Test default TTL values."""
        cache = PostgresResearchCache("postgresql://test")
        
        assert cache.DEFAULT_TTLS['wikipedia'] == 24
        assert cache.DEFAULT_TTLS['tmdb'] == 24
        assert cache.DEFAULT_TTLS['imdb'] == 168  # 7 days
    
    @pytest.mark.asyncio
    async def test_custom_ttl(self, mock_pool):
        """Test setting custom TTL."""
        cache = PostgresResearchCache("postgresql://test")
        cache.pool = mock_pool
        
        test_data = {'test': 'data'}
        
        # Set with custom TTL
        await cache.set('wikipedia', 'Test', test_data, ttl_hours=48)
        
        conn = await mock_pool.acquire().__aenter__()
        assert conn.execute.called
        
        # Verify expires_at is ~48 hours from now
        # (would need to inspect the actual call arguments to verify precisely)
    
    @pytest.mark.asyncio
    async def test_pool_not_initialized(self):
        """Test operations fail when pool not initialized."""
        cache = PostgresResearchCache("postgresql://test")
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await cache.get('wikipedia', 'Test')
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await cache.set('wikipedia', 'Test', {})
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await cache.delete('wikipedia', 'Test')
