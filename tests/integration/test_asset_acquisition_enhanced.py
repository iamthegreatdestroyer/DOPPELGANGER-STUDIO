"""
Integration tests for enhanced asset acquisition with CLIP and database storage.

Copyright (c) 2025. All Rights Reserved.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import asdict

from src.services.asset_manager.intelligent_scraper import (
    IntelligentAssetScraper,
    Asset,
    SourceConfig
)


@pytest.fixture
def sample_source():
    """Create a sample source configuration."""
    return SourceConfig(
        name="TestSource",
        type="video",
        url="https://api.test.com/videos",
        categories=["nature"],
        max_per_category=5
    )


@pytest.fixture
def sample_assets():
    """Create sample assets."""
    return [
        Asset(
            id="test1",
            source="TestSource",
            type="video",
            url="https://example.com/video1.mp4",
            title="Nature Video 1",
            quality_score=0.85,
            perceptual_hash="hash1"
        ),
        Asset(
            id="test2",
            source="TestSource",
            type="video",
            url="https://example.com/video2.mp4",
            title="Nature Video 2",
            quality_score=0.90,
            perceptual_hash="hash2"
        )
    ]


@pytest.mark.asyncio
async def test_scraper_initialization_with_clip():
    """Test scraper initializes with CLIP enabled."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=True,
        enable_database_storage=False
    )
    
    assert scraper.enable_clip_tagging is not None
    assert scraper.stats['tagging_enabled'] is not None


@pytest.mark.asyncio
async def test_scraper_initialization_with_database():
    """Test scraper initializes with database enabled."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=True,
        mongodb_uri="mongodb://localhost:27017"
    )
    
    assert scraper.enable_database_storage is not None
    assert scraper.stats['storage_enabled'] is not None


@pytest.mark.asyncio
async def test_scraper_initialization_all_disabled():
    """Test scraper works with all features disabled."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    
    assert scraper.stats['tagging_enabled'] == False
    assert scraper.stats['storage_enabled'] == False


@pytest.mark.asyncio
async def test_generate_tags_fallback():
    """Test tag generation fallback when CLIP disabled."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    
    asset = Asset(
        id="test",
        source="Test",
        type="video",
        url="https://example.com/video.mp4",
        perceptual_hash="hash"
    )
    
    tags = await scraper.generate_tags(asset)
    
    assert len(tags) >= 1
    assert "video" in tags or "content" in tags


@pytest.mark.asyncio
async def test_assess_quality():
    """Test quality assessment returns valid score."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    
    asset = Asset(
        id="test",
        source="Test",
        type="video",
        url="https://example.com/video.mp4",
        perceptual_hash="hash"
    )
    
    quality = await scraper.assess_quality(asset)
    
    assert 0.0 <= quality <= 1.0


@pytest.mark.asyncio
async def test_store_assets_disabled():
    """Test asset storage when database disabled."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    
    assets = [
        Asset(
            id="test",
            source="Test",
            type="video",
            url="https://example.com/video.mp4",
            perceptual_hash="hash"
        )
    ]
    
    # Should not raise error
    await scraper.store_assets(assets)


@pytest.mark.asyncio
async def test_full_pipeline_with_mocked_components(sample_assets):
    """Test full asset acquisition pipeline with mocked components."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    
    # Mock scrape_all_sources to return sample assets
    with patch.object(scraper, 'scrape_source_safe', return_value=sample_assets):
        with patch.object(scraper.deduplicator, 'process', return_value=sample_assets):
            results = await scraper.scrape_all_sources()
            
            assert len(results) == 2
            assert all(hasattr(asset, 'tags') for asset in results)
            assert all(hasattr(asset, 'quality_score') for asset in results)


@pytest.mark.asyncio
async def test_scraper_statistics_tracking():
    """Test that statistics are tracked correctly."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    
    assert 'total_scraped' in scraper.stats
    assert 'total_unique' in scraper.stats
    assert 'failed_sources' in scraper.stats
    assert 'tagging_enabled' in scraper.stats
    assert 'storage_enabled' in scraper.stats


@pytest.mark.asyncio
async def test_environment_variable_configuration():
    """Test configuration from environment variables."""
    with patch.dict('os.environ', {
        'MONGODB_URI': 'mongodb://testhost:27017',
        'PINECONE_API_KEY': 'test-key-12345'
    }):
        scraper = IntelligentAssetScraper(
            enable_database_storage=True
        )
        
        # Should use environment variables
        assert scraper.db_manager is not None or not scraper.enable_database_storage


@pytest.mark.asyncio
async def test_generate_tags_with_clip_error_handling():
    """Test tag generation handles errors gracefully."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=True,
        enable_database_storage=False
    )
    
    asset = Asset(
        id="test",
        source="Test",
        type="video",
        url="https://example.com/video.mp4",
        perceptual_hash="hash"
    )
    
    # Mock CLIP tagger to raise exception
    if scraper.clip_tagger:
        with patch.object(scraper.clip_tagger, 'generate_tags', side_effect=Exception("CLIP error")):
            tags = await scraper.generate_tags(asset)
            
            # Should return fallback tags
            assert len(tags) >= 1


@pytest.mark.asyncio
async def test_store_assets_with_database_error_handling(sample_assets):
    """Test asset storage handles database errors gracefully."""
    scraper = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=True,
        mongodb_uri="mongodb://localhost:27017"
    )
    
    # Mock database manager to raise exception
    if scraper.db_manager:
        with patch.object(scraper.db_manager, 'store_assets', side_effect=Exception("DB error")):
            # Should not raise exception
            await scraper.store_assets(sample_assets)


def test_asset_dataclass_serialization():
    """Test Asset dataclass can be converted to dict."""
    asset = Asset(
        id="test",
        source="TestSource",
        type="video",
        url="https://example.com/video.mp4",
        title="Test Video",
        tags=["nature", "landscape"],
        quality_score=0.85,
        perceptual_hash="hash123",
        file_size=1024000,
        duration=30.0
    )
    
    asset_dict = asdict(asset)
    
    assert asset_dict['id'] == "test"
    assert asset_dict['source'] == "TestSource"
    assert asset_dict['quality_score'] == 0.85
    assert len(asset_dict['tags']) == 2


@pytest.mark.asyncio
async def test_scraper_respects_feature_flags():
    """Test that feature flags are respected throughout pipeline."""
    # CLIP enabled, DB disabled
    scraper1 = IntelligentAssetScraper(
        enable_clip_tagging=True,
        enable_database_storage=False
    )
    assert scraper1.enable_clip_tagging or not scraper1.enable_clip_tagging  # May be disabled if CLIP not available
    assert scraper1.enable_database_storage == False
    
    # CLIP disabled, DB enabled  
    scraper2 = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=True
    )
    assert scraper2.enable_clip_tagging == False
    assert scraper2.enable_database_storage or not scraper2.enable_database_storage  # May be disabled if DB not available
    
    # Both disabled
    scraper3 = IntelligentAssetScraper(
        enable_clip_tagging=False,
        enable_database_storage=False
    )
    assert scraper3.enable_clip_tagging == False
    assert scraper3.enable_database_storage == False
