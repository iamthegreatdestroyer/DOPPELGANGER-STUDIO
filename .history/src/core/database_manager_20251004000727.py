"""
Database Manager - Unified database access for PostgreSQL, MongoDB, and Redis.

Manages connections and provides simple interfaces for all databases.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Dict, Any
import logging
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database connections.
    
    Provides unified access to:
    - PostgreSQL (structured data)
    - MongoDB (document storage)
    - Redis (caching)
    """
    
    def __init__(
        self,
        postgres_url: Optional[str] = None,
        mongodb_url: Optional[str] = None,
        redis_url: Optional[str] = None
    ):
        """
        Initialize database manager.
        
        Args:
            postgres_url: PostgreSQL connection URL
            mongodb_url: MongoDB connection URL
            redis_url: Redis connection URL
        """
        self.postgres_url = postgres_url
        self.mongodb_url = mongodb_url
        self.redis_url = redis_url
        
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db = None
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to all databases."""
        logger.info("Connecting to databases...")
        
        # PostgreSQL
        if self.postgres_url:
            try:
                self.postgres_pool = await asyncpg.create_pool(
                    self.postgres_url,
                    min_size=2,
                    max_size=10
                )
                logger.info("PostgreSQL connected")
            except Exception as e:
                logger.error(f"PostgreSQL connection failed: {e}")
        
        # MongoDB
        if self.mongodb_url:
            try:
                self.mongo_client = AsyncIOMotorClient(self.mongodb_url)
                self.mongo_db = self.mongo_client.get_default_database()
                # Test connection
                await self.mongo_client.admin.command('ping')
                logger.info("MongoDB connected")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {e}")
        
        # Redis
        if self.redis_url:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    decode_responses=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis connected")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from all databases."""
        logger.info("Disconnecting from databases...")
        
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.redis_client:
            await self.redis_client.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    # PostgreSQL Methods
    async def pg_execute(self, query: str, *args) -> str:
        """Execute PostgreSQL query."""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL not connected")
        async with self.postgres_pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def pg_fetch(self, query: str, *args) -> list:
        """Fetch rows from PostgreSQL."""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL not connected")
        async with self.postgres_pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def pg_fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row from PostgreSQL."""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL not connected")
        async with self.postgres_pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    # MongoDB Methods
    def get_collection(self, name: str):
        """Get MongoDB collection."""
        if not self.mongo_db:
            raise RuntimeError("MongoDB not connected")
        return self.mongo_db[name]
    
    async def mongo_insert(
        self,
        collection: str,
        document: Dict
    ) -> Any:
        """Insert document into MongoDB."""
        coll = self.get_collection(collection)
        result = await coll.insert_one(document)
        return result.inserted_id
    
    async def mongo_find(
        self,
        collection: str,
        query: Dict,
        limit: int = 100
    ) -> list:
        """Find documents in MongoDB."""
        coll = self.get_collection(collection)
        cursor = coll.find(query).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def mongo_find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find single document in MongoDB."""
        coll = self.get_collection(collection)
        return await coll.find_one(query)
    
    # Redis Methods
    async def cache_get(self, key: str) -> Optional[str]:
        """Get value from Redis cache."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        return await self.redis_client.get(key)
    
    async def cache_set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ):
        """Set value in Redis cache."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        if ttl:
            await self.redis_client.setex(key, ttl, value)
        else:
            await self.redis_client.set(key, value)
    
    async def cache_delete(self, key: str):
        """Delete key from Redis cache."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        await self.redis_client.delete(key)


# Example usage
async def main():
    """Example database usage."""
    async with DatabaseManager(
        postgres_url="postgresql://user:pass@localhost/db",
        mongodb_url="mongodb://localhost:27017/db",
        redis_url="redis://localhost:6379/0"
    ) as db:
        # PostgreSQL
        shows = await db.pg_fetch("SELECT * FROM shows LIMIT 5")
        print(f"Found {len(shows)} shows")
        
        # MongoDB
        research = await db.mongo_find("research_data", {}, limit=5)
        print(f"Found {len(research)} research docs")
        
        # Redis
        await db.cache_set("test_key", "test_value", ttl=60)
        value = await db.cache_get("test_key")
        print(f"Cached value: {value}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
