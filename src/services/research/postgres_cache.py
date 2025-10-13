"""
PostgreSQL Research Cache - Cache research data to reduce API calls.

Provides efficient caching layer for Wikipedia, TMDB, and IMDB research data
with automatic expiration and cleanup.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Dict, Any
import asyncio
import asyncpg
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PostgresResearchCache:
    """
    PostgreSQL-based caching layer for research data.
    
    Features:
    - Automatic TTL (time-to-live) management
    - JSON data storage
    - Async connection pooling
    - Background cleanup of expired entries
    - Source-specific TTLs
    
    Example:
        >>> cache = PostgresResearchCache(connection_string)
        >>> await cache.initialize()
        >>> await cache.set('wikipedia', 'I Love Lucy', data, ttl_hours=24)
        >>> cached = await cache.get('wikipedia', 'I Love Lucy')
    """
    
    DEFAULT_TTLS = {
        'wikipedia': 24,  # 24 hours
        'tmdb': 24,       # 24 hours
        'imdb': 168       # 7 days (IMDB changes less frequently)
    }
    
    def __init__(self, connection_string: str, pool_size: int = 10):
        """
        Initialize PostgreSQL cache.
        
        Args:
            connection_string: PostgreSQL connection string
            pool_size: Connection pool size
        """
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool: Optional[asyncpg.Pool] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """
        Initialize connection pool and create tables.
        
        Raises:
            asyncpg.PostgresError: If connection fails
        """
        logger.info("Initializing PostgreSQL research cache")
        
        # Create connection pool
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=1,
            max_size=self.pool_size
        )
        
        # Create tables if not exists
        await self._create_tables()
        
        # Start background cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("PostgreSQL research cache initialized")
    
    async def close(self):
        """Close connection pool and stop cleanup task."""
        logger.info("Closing PostgreSQL research cache")
        
        # Stop cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close pool
        if self.pool:
            await self.pool.close()
        
        logger.info("PostgreSQL research cache closed")
    
    async def _create_tables(self):
        """Create cache tables if they don't exist."""
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS research_cache (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50) NOT NULL,
                    query VARCHAR(255) NOT NULL,
                    response JSONB NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(source, query)
                )
            """)
            
            # Create index for faster expiration checks
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expiry 
                ON research_cache(expires_at)
            """)
            
            # Create index for faster lookups
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_lookup 
                ON research_cache(source, query)
            """)
    
    async def get(self, source: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached research data.
        
        Args:
            source: Data source ('wikipedia', 'tmdb', 'imdb')
            query: Search query (e.g., show title)
            
        Returns:
            Cached data dict if found and not expired, None otherwise
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT response, expires_at
                FROM research_cache
                WHERE source = $1 AND query = $2
                """,
                source, query
            )
            
            if not row:
                logger.debug(f"Cache miss: {source}/{query}")
                return None
            
            # Check if expired
            if row['expires_at'] < datetime.now():
                logger.debug(f"Cache expired: {source}/{query}")
                # Delete expired entry
                await conn.execute(
                    "DELETE FROM research_cache WHERE source = $1 AND query = $2",
                    source, query
                )
                return None
            
            logger.debug(f"Cache hit: {source}/{query}")
            return json.loads(row['response'])
    
    async def set(
        self,
        source: str,
        query: str,
        data: Dict[str, Any],
        ttl_hours: Optional[int] = None
    ):
        """
        Store research data in cache.
        
        Args:
            source: Data source ('wikipedia', 'tmdb', 'imdb')
            query: Search query (e.g., show title)
            data: Data to cache
            ttl_hours: Time to live in hours. Uses default for source if None
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        # Get TTL
        if ttl_hours is None:
            ttl_hours = self.DEFAULT_TTLS.get(source, 24)
        
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO research_cache (source, query, response, expires_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (source, query)
                DO UPDATE SET
                    response = EXCLUDED.response,
                    expires_at = EXCLUDED.expires_at,
                    created_at = NOW()
                """,
                source, query, json_data, expires_at
            )
        
        logger.debug(f"Cached: {source}/{query} (TTL: {ttl_hours}h)")
    
    async def delete(self, source: str, query: str):
        """
        Delete cached entry.
        
        Args:
            source: Data source
            query: Search query
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM research_cache WHERE source = $1 AND query = $2",
                source, query
            )
        
        logger.debug(f"Deleted cache: {source}/{query}")
    
    async def clear_source(self, source: str):
        """
        Clear all cache entries for a source.
        
        Args:
            source: Data source to clear
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM research_cache WHERE source = $1",
                source
            )
        
        logger.info(f"Cleared {result} entries for source: {source}")
    
    async def clear_all(self):
        """Clear all cache entries."""
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM research_cache")
        
        logger.info(f"Cleared all cache: {result} entries")
    
    async def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM research_cache WHERE expires_at < NOW()"
            )
        
        # Extract count from result (format: "DELETE N")
        count = int(result.split()[-1]) if result != "DELETE 0" else 0
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired cache entries")
        
        return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache statistics
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        async with self.pool.acquire() as conn:
            # Total entries
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM research_cache"
            )
            
            # Entries by source
            by_source = await conn.fetch(
                "SELECT source, COUNT(*) as count FROM research_cache GROUP BY source"
            )
            
            # Expired entries
            expired = await conn.fetchval(
                "SELECT COUNT(*) FROM research_cache WHERE expires_at < NOW()"
            )
            
            # Average age
            avg_age = await conn.fetchval(
                "SELECT AVG(EXTRACT(EPOCH FROM (NOW() - created_at))) FROM research_cache"
            )
        
        return {
            'total_entries': total,
            'by_source': {row['source']: row['count'] for row in by_source},
            'expired_entries': expired,
            'average_age_seconds': float(avg_age) if avg_age else 0
        }
    
    async def _cleanup_loop(self):
        """
        Background task to periodically clean up expired entries.
        
        Runs every hour.
        """
        while True:
            try:
                await asyncio.sleep(3600)  # 1 hour
                await self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")


# Example usage
async def main():
    """Example usage of PostgreSQL research cache."""
    import os
    
    # Get connection string from environment
    conn_str = os.getenv('POSTGRES_URI', 'postgresql://user:pass@localhost/doppelganger')
    
    cache = PostgresResearchCache(conn_str)
    
    try:
        await cache.initialize()
        
        # Store some data
        test_data = {
            'title': 'I Love Lucy',
            'years': '1951-1957',
            'network': 'CBS'
        }
        
        await cache.set('wikipedia', 'I Love Lucy', test_data)
        print("Data cached")
        
        # Retrieve data
        cached = await cache.get('wikipedia', 'I Love Lucy')
        print(f"Retrieved: {cached}")
        
        # Get stats
        stats = await cache.get_stats()
        print(f"Cache stats: {stats}")
        
    finally:
        await cache.close()


if __name__ == "__main__":
    asyncio.run(main())
