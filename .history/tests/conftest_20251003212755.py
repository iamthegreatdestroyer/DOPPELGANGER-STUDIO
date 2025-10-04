"""
Test configuration and shared fixtures for DOPPELGANGER STUDIO.

This module provides pytest configuration and fixtures that are shared
across all test modules.
"""

import pytest
import asyncio
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, AsyncMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def sample_video_path(test_data_dir: Path) -> Path:
    """Provide path to sample video file."""
    return test_data_dir / "sample_video.mp4"


@pytest.fixture
def sample_audio_path(test_data_dir: Path) -> Path:
    """Provide path to sample audio file."""
    return test_data_dir / "sample_audio.mp3"


@pytest.fixture
def mock_db_connection():
    """Provide a mock database connection."""
    mock_db = Mock()
    mock_db.execute = AsyncMock()
    mock_db.fetch = AsyncMock(return_value=[])
    mock_db.fetchrow = AsyncMock(return_value=None)
    return mock_db


@pytest.fixture
def mock_redis_client():
    """Provide a mock Redis client."""
    mock_redis = Mock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    return mock_redis


@pytest.fixture
def mock_ai_client():
    """Provide a mock AI client (Claude/GPT)."""
    mock_client = Mock()
    mock_client.generate = AsyncMock(
        return_value="Mock AI generated response"
    )
    mock_client.generate_with_schema = AsyncMock(
        return_value={"mock": "data"}
    )
    return mock_client


@pytest.fixture
def sample_character_data():
    """Provide sample character data for testing."""
    return {
        "name": "Lucy Ricardo",
        "traits": ["ambitious", "scheming", "endearing"],
        "relationships": {
            "Ricky": "husband",
            "Ethel": "best friend"
        },
        "signature_behaviors": [
            "harebrained schemes",
            "physical comedy"
        ],
        "catchphrases": ["Oh, Ricky!"]
    }


@pytest.fixture
def sample_setting_data():
    """Provide sample setting data for testing."""
    return {
        "type": "space_colony",
        "year": 2157,
        "location": "Luna Prime Station",
        "description": "Bustling space tourism hub on the moon"
    }


@pytest.fixture
def sample_asset_data():
    """Provide sample asset data for testing."""
    return {
        "id": "test-asset-001",
        "source": "Pexels",
        "type": "video",
        "url": "https://example.com/video.mp4",
        "title": "Beautiful Space Scene",
        "tags": ["space", "stars", "nebula"],
        "quality_score": 0.95,
        "duration": 10.5
    }


@pytest.fixture
def temp_storage_dir(tmp_path: Path) -> Path:
    """Provide temporary storage directory for tests."""
    storage_dir = tmp_path / "test_storage"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir


@pytest.fixture
def mock_config():
    """Provide mock configuration."""
    return {
        "PEXELS_API_KEY": "test_pexels_key",
        "PIXABAY_API_KEY": "test_pixabay_key",
        "CLAUDE_API_KEY": "test_claude_key",
        "DATABASE_URL": "postgresql://test:test@localhost/test_db",
        "REDIS_URL": "redis://localhost:6379/0"
    }


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks after each test."""
    yield
    # Cleanup code here if needed


# Mark all tests as asyncio-compatible by default
def pytest_collection_modifyitems(items):
    """Modify test items to add asyncio marker where needed."""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
