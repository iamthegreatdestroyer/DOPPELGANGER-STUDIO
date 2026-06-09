"""
Tests for Asset Database Manager.

Copyright (c) 2025. All Rights Reserved.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock


class _AsyncCursor:
    """Async-iterable mock cursor that wraps a list of documents."""
    def __init__(self, items):
        self._items = list(items)

    def limit(self, _):
        return self

    def __aiter__(self):
        self._it = iter(self._items)
        return self

    async def __anext__(self):
        try:
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration
import numpy as np

from src.services.asset_manager.asset_database import AssetDatabaseManager
from src.services.asset_manager.intelligent_scraper import Asset


@pytest.fixture
def sample_assets():
    """Create sample assets for testing."""
    return [
        Asset(
            id="asset1",
            source="Pexels",
            type="video",
            url="https://example.com/video1.mp4",
            title="Nature Video",
            tags=["nature", "landscape"],
            quality_score=0.9,
            perceptual_hash="phash_v_abc123",
            file_size=1024000,
            duration=30.0
        ),
        Asset(
            id="asset2",
            source="Pixabay",
            type="video",
            url="https://example.com/video2.mp4",
            title="City Video",
            tags=["city", "urban"],
            quality_score=0.85,
            perceptual_hash="phash_v_def456",
            file_size=2048000,
            duration=45.0
        )
    ]


@pytest_asyncio.fixture
async def db_manager():
    """Create database manager with mocked MongoDB."""
    manager = AssetDatabaseManager(
        mongodb_uri="mongodb://localhost:27017",
        database_name="test_db"
    )
    
    # Mock MongoDB client
    mock_client = AsyncMock()
    mock_db = Mock()
    mock_collection = AsyncMock()
    mock_analytics = AsyncMock()
    
    manager.client = mock_client
    manager.db = mock_db
    manager.assets_collection = mock_collection
    manager.analytics_collection = mock_analytics
    manager._initialized = True
    
    return manager


@pytest.mark.asyncio
async def test_initialization():
    """Test database manager initializes correctly."""
    manager = AssetDatabaseManager()

    mock_collection = AsyncMock()
    mock_collection.create_index = AsyncMock(return_value="idx_0")
    mock_db = MagicMock()
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    mock_client = MagicMock()
    mock_client.__getitem__ = Mock(return_value=mock_db)

    with patch("src.services.asset_manager.asset_database.AsyncIOMotorClient",
               return_value=mock_client):
        await manager.initialize()

        assert manager._initialized
        assert manager.assets_collection is not None


@pytest.mark.asyncio
async def test_create_indexes():
    """Test index creation on initialization."""
    manager = AssetDatabaseManager()
    
    mock_collection = AsyncMock()
    manager.assets_collection = mock_collection
    manager.analytics_collection = AsyncMock()
    
    await manager._create_indexes()
    
    # Verify indexes were created
    assert mock_collection.create_index.call_count >= 4


@pytest.mark.asyncio
async def test_store_assets(db_manager, sample_assets):
    """Test storing assets in database."""
    # Mock find_one to return no duplicates
    db_manager.assets_collection.find_one = AsyncMock(return_value=None)
    db_manager.assets_collection.insert_one = AsyncMock(
        return_value=Mock(inserted_id="123")
    )
    
    stats = await db_manager.store_assets(sample_assets)
    
    assert stats["stored"] == 2
    assert stats["duplicates"] == 0
    assert stats["errors"] == 0


@pytest.mark.asyncio
async def test_store_assets_with_duplicates(db_manager, sample_assets):
    """Test duplicate detection during storage."""
    # Mock first asset as duplicate
    db_manager.assets_collection.find_one = AsyncMock(
        side_effect=[
            {"id": "existing"},  # First is duplicate
            None  # Second is unique
        ]
    )
    db_manager.assets_collection.insert_one = AsyncMock()
    
    stats = await db_manager.store_assets(sample_assets)
    
    assert stats["stored"] == 1
    assert stats["duplicates"] == 1
    assert stats["errors"] == 0


@pytest.mark.asyncio
async def test_store_assets_with_embeddings(db_manager, sample_assets):
    """Test storing assets with CLIP embeddings."""
    embeddings = {
        "asset1": np.random.randn(512),
        "asset2": np.random.randn(512)
    }
    
    db_manager.assets_collection.find_one = AsyncMock(return_value=None)
    db_manager.assets_collection.insert_one = AsyncMock()
    
    # Mock Pinecone
    db_manager.pinecone_index = Mock()
    db_manager.pinecone_index.upsert = Mock()
    
    stats = await db_manager.store_assets(sample_assets, embeddings)
    
    assert stats["stored"] == 2
    # Verify Pinecone upsert was called
    assert db_manager.pinecone_index.upsert.call_count == 2


@pytest.mark.asyncio
async def test_search_by_tags(db_manager):
    """Test tag-based asset search."""
    cursor = _AsyncCursor([
        {
            "id": "asset1",
            "source": "Pexels",
            "type": "video",
            "url": "https://example.com/video.mp4",
            "tags": ["nature", "landscape"],
            "quality_score": 0.9,
            "perceptual_hash": "hash123",
            "file_size": 1024,
            "duration": 30.0,
            "metadata": {},
            "created_at": datetime.now()
        }
    ])
    db_manager.assets_collection.find = Mock(return_value=cursor)
    
    results = await db_manager.search_by_tags(["nature"], min_quality=0.8)
    
    assert len(results) == 1
    assert results[0].id == "asset1"


@pytest.mark.asyncio
async def test_search_by_embedding(db_manager):
    """Test vector similarity search."""
    query_embedding = np.random.randn(512)
    
    # Mock Pinecone results
    mock_match = Mock()
    mock_match.id = "asset1"
    mock_results = Mock()
    mock_results.matches = [mock_match]
    
    db_manager.pinecone_index = Mock()
    db_manager.pinecone_index.query = Mock(return_value=mock_results)
    
    # Mock MongoDB cursor
    cursor = _AsyncCursor([
        {
            "id": "asset1",
            "source": "Pexels",
            "type": "video",
            "url": "https://example.com/video.mp4",
            "tags": ["nature"],
            "quality_score": 0.9,
            "perceptual_hash": "hash",
            "file_size": 1024,
            "duration": 30.0,
            "metadata": {},
            "created_at": datetime.now()
        }
    ])
    db_manager.assets_collection.find = Mock(return_value=cursor)
    
    results = await db_manager.search_by_embedding(query_embedding, top_k=10)
    
    assert len(results) == 1


@pytest.mark.asyncio
async def test_get_asset_by_id(db_manager):
    """Test retrieving asset by ID."""
    db_manager.assets_collection.find_one = AsyncMock(return_value={
        "id": "asset1",
        "source": "Pexels",
        "type": "video",
        "url": "https://example.com/video.mp4",
        "tags": ["nature"],
        "quality_score": 0.9,
        "perceptual_hash": "hash",
        "file_size": 1024,
        "duration": 30.0,
        "metadata": {},
        "created_at": datetime.now()
    })
    
    asset = await db_manager.get_asset_by_id("asset1")
    
    assert asset is not None
    assert asset.id == "asset1"


@pytest.mark.asyncio
async def test_get_asset_by_id_not_found(db_manager):
    """Test retrieving non-existent asset."""
    db_manager.assets_collection.find_one = AsyncMock(return_value=None)
    
    asset = await db_manager.get_asset_by_id("nonexistent")
    
    assert asset is None


@pytest.mark.asyncio
async def test_update_usage(db_manager):
    """Test usage statistics update."""
    db_manager.assets_collection.update_one = AsyncMock()
    db_manager.analytics_collection.insert_one = AsyncMock()
    
    await db_manager.update_usage("asset1")
    
    # Verify both collections were updated
    assert db_manager.assets_collection.update_one.called
    assert db_manager.analytics_collection.insert_one.called


@pytest.mark.asyncio
async def test_get_usage_stats(db_manager):
    """Test retrieving usage statistics."""
    mock_aggregate = AsyncMock()
    mock_aggregate.to_list = AsyncMock(return_value=[
        {"_id": "asset1", "count": 10},
        {"_id": "asset2", "count": 5}
    ])
    
    db_manager.analytics_collection.aggregate = Mock(return_value=mock_aggregate)
    db_manager.assets_collection.count_documents = AsyncMock(return_value=100)
    
    stats = await db_manager.get_usage_stats()
    
    assert stats["total_assets"] == 100
    assert len(stats["top_used_assets"]) == 2


@pytest.mark.asyncio
async def test_delete_asset(db_manager):
    """Test asset deletion."""
    # Mock asset retrieval
    mock_asset = Asset(
        id="asset1",
        source="Pexels",
        type="video",
        url="https://example.com/video.mp4",
        local_path=Path("/tmp/video.mp4"),
        tags=["nature"],
        quality_score=0.9,
        perceptual_hash="hash",
        file_size=1024,
        duration=30.0
    )
    
    db_manager.get_asset_by_id = AsyncMock(return_value=mock_asset)
    db_manager.assets_collection.delete_one = AsyncMock(
        return_value=Mock(deleted_count=1)
    )
    
    # Mock file deletion
    with patch.object(Path, "exists", return_value=False):
        result = await db_manager.delete_asset("asset1")
    
    assert result is True


@pytest.mark.asyncio
async def test_delete_asset_with_pinecone(db_manager):
    """Test asset deletion includes Pinecone cleanup."""
    mock_asset = Asset(
        id="asset1",
        source="Pexels",
        type="video",
        url="https://example.com/video.mp4",
        tags=["nature"],
        quality_score=0.9,
        perceptual_hash="hash",
        file_size=1024,
        duration=30.0
    )
    
    db_manager.get_asset_by_id = AsyncMock(return_value=mock_asset)
    db_manager.assets_collection.delete_one = AsyncMock(
        return_value=Mock(deleted_count=1)
    )
    
    # Mock Pinecone
    db_manager.pinecone_index = Mock()
    db_manager.pinecone_index.delete = Mock()
    
    result = await db_manager.delete_asset("asset1")
    
    assert result is True
    assert db_manager.pinecone_index.delete.called


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager protocol."""
    manager = AssetDatabaseManager()
    
    with patch.object(manager, "initialize") as mock_init:
        with patch.object(manager, "close") as mock_close:
            async with manager as db:
                assert db == manager
            
            assert mock_init.called
            assert mock_close.called


@pytest.mark.asyncio
async def test_local_storage_path_creation():
    """Test local storage directory is created."""
    with patch.object(Path, "mkdir") as mock_mkdir:
        manager = AssetDatabaseManager()
        
        assert mock_mkdir.called


@pytest.mark.asyncio
async def test_pinecone_initialization_optional(db_manager):
    """Test Pinecone initialization is optional."""
    db_manager.pinecone_api_key = None
    
    await db_manager._initialize_pinecone()
    
    # Should complete without errors
    assert db_manager.pinecone_index is None
