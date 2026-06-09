"""
Tests for CLIP Semantic Tagger.

Copyright (c) 2025. All Rights Reserved.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import numpy as np
import torch
from PIL import Image

from src.services.asset_manager.clip_tagger import CLIPSemanticTagger


@pytest.fixture
def mock_clip_model():
    """Create mock CLIP model."""
    model = Mock()
    model.eval = Mock()
    model.encode_text = Mock(return_value=torch.randn(1, 512))
    model.encode_image = Mock(return_value=torch.randn(1, 512))
    return model


@pytest.fixture
def mock_preprocess():
    """Create mock CLIP preprocessing function."""
    def preprocess(image):
        return torch.randn(3, 224, 224)
    return preprocess


@pytest.fixture
async def tagger(mock_clip_model, mock_preprocess):
    """Create CLIP tagger with mocked model."""
    tagger = CLIPSemanticTagger()
    
    with patch("src.services.asset_manager.clip_tagger.clip.load") as mock_load:
        mock_load.return_value = (mock_clip_model, mock_preprocess)
        await tagger.initialize()
    
    return tagger


@pytest.mark.asyncio
async def test_initialization(tagger):
    """Test CLIP tagger initializes correctly."""
    assert tagger._initialized
    assert tagger.model is not None
    assert tagger.preprocess is not None
    assert len(tagger.tag_embeddings) > 0


@pytest.mark.asyncio
async def test_tag_embeddings_computed():
    """Test that tag embeddings are pre-computed."""
    tagger = CLIPSemanticTagger()
    
    with patch("src.services.asset_manager.clip_tagger.clip.load"):
        await tagger.initialize()
    
    # Check all tag categories are included
    all_tags = (
        CLIPSemanticTagger.GENERAL_TAGS +
        CLIPSemanticTagger.MOOD_TAGS +
        CLIPSemanticTagger.TECHNICAL_TAGS
    )
    
    assert len(tagger.tag_embeddings) == len(all_tags)


@pytest.mark.asyncio
async def test_generate_tags_with_video(tagger):
    """Test tag generation for video."""
    # Mock keyframe extraction
    mock_frames = [
        Image.new("RGB", (224, 224), color="blue"),
        Image.new("RGB", (224, 224), color="green")
    ]
    
    with patch.object(tagger, "_extract_keyframes", return_value=mock_frames):
        with patch.object(tagger, "_compute_similarities") as mock_sim:
            # Mock similarity scores
            mock_sim.side_effect = [
                {"nature": 0.8, "landscape": 0.7, "sky": 0.6},
                {"nature": 0.75, "landscape": 0.65, "ocean": 0.55}
            ]
            
            tags = await tagger.generate_tags(
                video_url="https://example.com/video.mp4",
                top_k=3,
                threshold=0.5
            )
            
            assert len(tags) <= 3
            assert "nature" in tags  # High score in both frames


@pytest.mark.asyncio
async def test_generate_tags_no_keyframes(tagger):
    """Test fallback when no keyframes extracted."""
    with patch.object(tagger, "_extract_keyframes", return_value=[]):
        tags = await tagger.generate_tags(
            video_url="https://example.com/video.mp4"
        )
        
        assert len(tags) == 3
        assert "video" in tags
        assert "content" in tags


@pytest.mark.asyncio
async def test_keyframe_extraction_ffmpeg(tagger):
    """Test FFmpeg keyframe extraction."""
    with patch("subprocess.run") as mock_subprocess:
        mock_subprocess.return_value = Mock(returncode=0)
        
        # Create temporary directory mock
        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            tmpdir_path = Path("/tmp/test")
            mock_tmpdir.return_value.__enter__.return_value = str(tmpdir_path)
            
            # Mock frame files
            with patch.object(Path, "glob") as mock_glob:
                mock_glob.return_value = []
                
                frames = await tagger._extract_keyframes(
                    "video.mp4",
                    max_frames=5
                )
                
                assert isinstance(frames, list)


@pytest.mark.asyncio
async def test_compute_similarities(tagger):
    """Test similarity computation for single image."""
    test_image = Image.new("RGB", (224, 224), color="red")
    
    similarities = await tagger._compute_similarities(test_image)
    
    assert isinstance(similarities, dict)
    assert len(similarities) > 0
    assert all(isinstance(v, float) for v in similarities.values())


@pytest.mark.asyncio
async def test_generate_embeddings(tagger):
    """Test embedding generation for vector search."""
    mock_frames = [
        Image.new("RGB", (224, 224), color="blue"),
        Image.new("RGB", (224, 224), color="green")
    ]
    
    with patch.object(tagger, "_extract_keyframes", return_value=mock_frames):
        embeddings = await tagger.generate_embeddings(
            video_url="https://example.com/video.mp4"
        )
        
        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.ndim == 1  # Flattened


@pytest.mark.asyncio
async def test_generate_embeddings_no_keyframes(tagger):
    """Test embedding generation when no keyframes available."""
    with patch.object(tagger, "_extract_keyframes", return_value=[]):
        embeddings = await tagger.generate_embeddings(
            video_url="https://example.com/video.mp4"
        )
        
        assert embeddings is None


@pytest.mark.asyncio
async def test_batch_generate_tags(tagger):
    """Test batch tag generation for multiple videos."""
    videos = [
        ("https://example.com/video1.mp4", None),
        ("https://example.com/video2.mp4", None),
        ("https://example.com/video3.mp4", None)
    ]
    
    with patch.object(tagger, "generate_tags") as mock_generate:
        mock_generate.side_effect = [
            ["nature", "landscape"],
            ["city", "urban"],
            ["ocean", "water"]
        ]
        
        results = await tagger.batch_generate_tags(videos, top_k=5)
        
        assert len(results) == 3
        assert all(isinstance(tags, list) for tags in results)


@pytest.mark.asyncio
async def test_batch_generate_tags_with_errors(tagger):
    """Test batch processing handles errors gracefully."""
    videos = [
        ("https://example.com/video1.mp4", None),
        ("https://example.com/video2.mp4", None)
    ]
    
    with patch.object(tagger, "generate_tags") as mock_generate:
        mock_generate.side_effect = [
            ["nature", "landscape"],
            Exception("Processing failed")
        ]
        
        results = await tagger.batch_generate_tags(videos)
        
        assert len(results) == 2
        assert isinstance(results[0], list)
        assert results[1] == []  # Exception converted to empty list


@pytest.mark.asyncio
async def test_threshold_filtering(tagger):
    """Test that low-confidence tags are filtered out."""
    mock_frames = [Image.new("RGB", (224, 224))]
    
    with patch.object(tagger, "_extract_keyframes", return_value=mock_frames):
        with patch.object(tagger, "_compute_similarities") as mock_sim:
            # Mix of high and low confidence scores
            mock_sim.return_value = {
                "nature": 0.9,
                "landscape": 0.8,
                "abstract": 0.3,
                "pattern": 0.2
            }
            
            tags = await tagger.generate_tags(
                video_url="https://example.com/video.mp4",
                threshold=0.5  # Should filter out 0.3 and 0.2
            )
            
            assert "nature" in tags
            assert "landscape" in tags
            assert "abstract" not in tags
            assert "pattern" not in tags


@pytest.mark.asyncio
async def test_device_selection():
    """Test device selection (CPU vs CUDA)."""
    with patch("torch.cuda.is_available", return_value=True):
        tagger_cuda = CLIPSemanticTagger()
        assert tagger_cuda.device == "cuda"
    
    with patch("torch.cuda.is_available", return_value=False):
        tagger_cpu = CLIPSemanticTagger()
        assert tagger_cpu.device == "cpu"


def test_tag_vocabularies():
    """Test that tag vocabularies are comprehensive."""
    assert len(CLIPSemanticTagger.GENERAL_TAGS) > 50
    assert len(CLIPSemanticTagger.MOOD_TAGS) > 10
    assert len(CLIPSemanticTagger.TECHNICAL_TAGS) > 10
    
    # Check for key categories
    general = CLIPSemanticTagger.GENERAL_TAGS
    assert "nature" in general
    assert "technology" in general
    assert "people" in general
    
    mood = CLIPSemanticTagger.MOOD_TAGS
    assert "peaceful" in mood
    assert "energetic" in mood
    
    technical = CLIPSemanticTagger.TECHNICAL_TAGS
    assert "aerial" in technical
    assert "closeup" in technical
