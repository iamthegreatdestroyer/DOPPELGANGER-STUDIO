"""
Asset Database Manager - MongoDB storage for media assets.

This module implements comprehensive asset storage with:
1. MongoDB for asset metadata and search
2. Pinecone for vector similarity search
3. Local file management with download tracking
4. Usage analytics and performance metrics
5. Automatic cleanup of expired/unused assets

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from dataclasses import asdict
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import numpy as np

logger = logging.getLogger(__name__)

# Import Asset dataclass from intelligent_scraper
import sys
sys.path.append(str(Path(__file__).parent))
from intelligent_scraper import Asset


class AssetDatabaseManager:
    """
    MongoDB-based asset storage with vector search.
    
    Features:
    - Asset metadata storage in MongoDB
    - Vector similarity search with Pinecone
    - Local file download and caching
    - Usage analytics tracking
    - Automatic TTL-based cleanup
    - Duplicate detection across storage
    
    Example:
        >>> db = AssetDatabaseManager()
        >>> await db.initialize()
        >>> await db.store_assets(assets)
        >>> results = await db.search_by_tags(['nature', 'landscape'])
    """
    
    def __init__(
        self,
        mongodb_uri: str = "mongodb://localhost:27017",
        database_name: str = "doppelganger_assets",
        local_storage_path: Optional[Path] = None,
        pinecone_api_key: Optional[str] = None,
        pinecone_environment: str = "us-west1-gcp",
        pinecone_index_name: str = "asset-embeddings"
    ):
        """
        Initialize asset database manager.
        
        Args:
            mongodb_uri: MongoDB connection string
            database_name: Database name
            local_storage_path: Path for local file storage
            pinecone_api_key: Pinecone API key (optional)
            pinecone_environment: Pinecone environment
            pinecone_index_name: Pinecone index name
        """
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.local_storage_path = local_storage_path or Path.home() / ".doppelganger" / "assets"
        
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.assets_collection = None
        self.analytics_collection = None
        
        # Pinecone configuration (optional)
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.pinecone_index_name = pinecone_index_name
        self.pinecone_index = None
        
        self._initialized = False
        
        # Ensure local storage directory exists
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Asset database configured: {database_name}")
    
    async def initialize(self):
        """Initialize database connections and indexes."""
        if self._initialized:
            return
        
        logger.info("Initializing asset database...")
        
        # Connect to MongoDB
        self.client = AsyncIOMotorClient(self.mongodb_uri)
        self.db = self.client[self.database_name]
        self.assets_collection = self.db["assets"]
        self.analytics_collection = self.db["analytics"]
        
        # Create indexes
        await self._create_indexes()
        
        # Initialize Pinecone if configured
        if self.pinecone_api_key:
            await self._initialize_pinecone()
        
        self._initialized = True
        logger.info("Asset database initialized successfully")
    
    async def _create_indexes(self):
        """Create MongoDB indexes for efficient queries."""
        logger.info("Creating MongoDB indexes...")
        
        # Compound index for source + type queries
        await self.assets_collection.create_index([
            ("source", 1),
            ("type", 1)
        ])
        
        # Index for tag-based search
        await self.assets_collection.create_index([("tags", 1)])
        
        # Index for quality filtering
        await self.assets_collection.create_index([("quality_score", -1)])
        
        # Index for perceptual hash (duplicate detection)
        await self.assets_collection.create_index([("perceptual_hash", 1)])
        
        # TTL index for automatic cleanup (30 days)
        await self.assets_collection.create_index(
            [("created_at", 1)],
            expireAfterSeconds=30 * 24 * 60 * 60  # 30 days
        )
        
        # Index for usage tracking
        await self.analytics_collection.create_index([
            ("asset_id", 1),
            ("timestamp", -1)
        ])
        
        logger.info("Indexes created successfully")
    
    async def _initialize_pinecone(self):
        """Initialize Pinecone vector database."""
        try:
            import pinecone
            
            logger.info("Initializing Pinecone...")
            
            # Initialize Pinecone
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                pinecone.init,
                self.pinecone_api_key,
                self.pinecone_environment
            )
            
            # Check if index exists
            indexes = await loop.run_in_executor(None, pinecone.list_indexes)
            
            if self.pinecone_index_name not in indexes:
                # Create index (CLIP ViT-B/32 has 512 dimensions)
                logger.info(f"Creating Pinecone index: {self.pinecone_index_name}")
                await loop.run_in_executor(
                    None,
                    pinecone.create_index,
                    self.pinecone_index_name,
                    512,
                    "cosine"
                )
            
            # Connect to index
            self.pinecone_index = await loop.run_in_executor(
                None,
                pinecone.Index,
                self.pinecone_index_name
            )
            
            logger.info("Pinecone initialized successfully")
        
        except ImportError:
            logger.warning("Pinecone not installed, vector search disabled")
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
    
    async def store_assets(
        self,
        assets: List[Asset],
        embeddings: Optional[Dict[str, np.ndarray]] = None
    ) -> Dict[str, Any]:
        """
        Store assets in database.
        
        Args:
            assets: List of assets to store
            embeddings: Optional dict mapping asset IDs to CLIP embeddings
        
        Returns:
            Statistics about storage operation
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"Storing {len(assets)} assets...")
        
        stats = {
            "stored": 0,
            "duplicates": 0,
            "errors": 0
        }
        
        for asset in assets:
            try:
                # Check for duplicates
                existing = await self.assets_collection.find_one({
                    "perceptual_hash": asset.perceptual_hash
                })
                
                if existing:
                    logger.debug(f"Duplicate asset: {asset.id}")
                    stats["duplicates"] += 1
                    continue
                
                # Convert asset to dict
                asset_dict = asdict(asset)
                
                # Convert Path to string
                if asset_dict.get("local_path"):
                    asset_dict["local_path"] = str(asset_dict["local_path"])
                
                # Add metadata
                asset_dict["inserted_at"] = datetime.now()
                asset_dict["usage_count"] = 0
                asset_dict["last_used"] = None
                
                # Insert into MongoDB
                result = await self.assets_collection.insert_one(asset_dict)
                
                # Store embedding in Pinecone if available
                if embeddings and asset.id in embeddings and self.pinecone_index:
                    await self._store_embedding(
                        asset.id,
                        embeddings[asset.id],
                        asset_dict
                    )
                
                stats["stored"] += 1
                logger.debug(f"Stored asset: {asset.id}")
            
            except Exception as e:
                logger.error(f"Failed to store asset {asset.id}: {e}")
                stats["errors"] += 1
        
        logger.info(f"Storage complete: {stats}")
        return stats
    
    async def _store_embedding(
        self,
        asset_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ):
        """Store embedding in Pinecone."""
        try:
            # Prepare metadata (Pinecone has limits)
            pinecone_metadata = {
                "source": metadata.get("source", ""),
                "type": metadata.get("type", ""),
                "tags": ",".join(metadata.get("tags", [])),
                "quality_score": metadata.get("quality_score", 0.0)
            }
            
            # Upsert to Pinecone
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.pinecone_index.upsert,
                [(asset_id, embedding.tolist(), pinecone_metadata)]
            )
            
            logger.debug(f"Stored embedding for {asset_id}")
        
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
    
    async def search_by_tags(
        self,
        tags: List[str],
        min_quality: float = 0.0,
        max_results: int = 50
    ) -> List[Asset]:
        """
        Search assets by tags.
        
        Args:
            tags: List of tags to search for
            min_quality: Minimum quality score
            max_results: Maximum number of results
        
        Returns:
            List of matching assets
        """
        if not self._initialized:
            await self.initialize()
        
        query = {
            "tags": {"$in": tags},
            "quality_score": {"$gte": min_quality}
        }
        
        cursor = self.assets_collection.find(query).limit(max_results)
        
        assets = []
        async for doc in cursor:
            asset = self._doc_to_asset(doc)
            assets.append(asset)
        
        logger.info(f"Found {len(assets)} assets for tags: {tags}")
        return assets
    
    async def search_by_embedding(
        self,
        query_embedding: np.ndarray,
        top_k: int = 50,
        min_quality: float = 0.0
    ) -> List[Asset]:
        """
        Search assets by vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            min_quality: Minimum quality score filter
        
        Returns:
            List of similar assets
        """
        if not self.pinecone_index:
            logger.warning("Pinecone not configured, falling back to tag search")
            return []
        
        try:
            # Query Pinecone
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.pinecone_index.query,
                query_embedding.tolist(),
                top_k,
                None,
                None,
                True  # include_metadata
            )
            
            # Retrieve full assets from MongoDB
            asset_ids = [match.id for match in results.matches]
            
            cursor = self.assets_collection.find({
                "id": {"$in": asset_ids},
                "quality_score": {"$gte": min_quality}
            })
            
            assets = []
            async for doc in cursor:
                asset = self._doc_to_asset(doc)
                assets.append(asset)
            
            logger.info(f"Found {len(assets)} similar assets")
            return assets
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def get_asset_by_id(self, asset_id: str) -> Optional[Asset]:
        """Retrieve asset by ID."""
        if not self._initialized:
            await self.initialize()
        
        doc = await self.assets_collection.find_one({"id": asset_id})
        
        if doc:
            return self._doc_to_asset(doc)
        
        return None
    
    async def update_usage(self, asset_id: str):
        """Update usage statistics for asset."""
        if not self._initialized:
            await self.initialize()
        
        # Update asset usage count
        await self.assets_collection.update_one(
            {"id": asset_id},
            {
                "$inc": {"usage_count": 1},
                "$set": {"last_used": datetime.now()}
            }
        )
        
        # Record analytics event
        await self.analytics_collection.insert_one({
            "asset_id": asset_id,
            "event_type": "usage",
            "timestamp": datetime.now()
        })
        
        logger.debug(f"Updated usage for {asset_id}")
    
    async def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            Dictionary with usage statistics
        """
        if not self._initialized:
            await self.initialize()
        
        # Default to last 30 days
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Aggregate usage data
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$asset_id",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 100
            }
        ]
        
        top_assets = await self.analytics_collection.aggregate(pipeline).to_list(100)
        
        # Get total asset count
        total_assets = await self.assets_collection.count_documents({})
        
        stats = {
            "total_assets": total_assets,
            "top_used_assets": top_assets,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        logger.info(f"Usage stats: {total_assets} total assets")
        return stats
    
    async def delete_asset(self, asset_id: str) -> bool:
        """
        Delete asset from database and storage.
        
        Args:
            asset_id: ID of asset to delete
        
        Returns:
            True if deleted, False otherwise
        """
        if not self._initialized:
            await self.initialize()
        
        # Get asset to find local file
        asset = await self.get_asset_by_id(asset_id)
        
        if not asset:
            return False
        
        # Delete from MongoDB
        result = await self.assets_collection.delete_one({"id": asset_id})
        
        # Delete from Pinecone
        if self.pinecone_index:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    self.pinecone_index.delete,
                    [asset_id]
                )
            except Exception as e:
                logger.error(f"Failed to delete from Pinecone: {e}")
        
        # Delete local file if exists
        if asset.local_path and Path(asset.local_path).exists():
            try:
                Path(asset.local_path).unlink()
                logger.debug(f"Deleted local file: {asset.local_path}")
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")
        
        logger.info(f"Deleted asset: {asset_id}")
        return result.deleted_count > 0
    
    def _doc_to_asset(self, doc: Dict[str, Any]) -> Asset:
        """Convert MongoDB document to Asset object."""
        # Remove MongoDB _id
        doc.pop("_id", None)
        
        # Remove extra fields
        doc.pop("inserted_at", None)
        doc.pop("usage_count", None)
        doc.pop("last_used", None)
        
        # Convert local_path back to Path
        if doc.get("local_path"):
            doc["local_path"] = Path(doc["local_path"])
        
        return Asset(**doc)
    
    async def close(self):
        """Close database connections."""
        if self.client:
            self.client.close()
            logger.info("Database connections closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
