"""
Audio Cache - Cache generated audio files.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional
from pathlib import Path
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class AudioCache:
    """
    Cache TTS-generated audio files.
    
    Uses content-based keys to avoid regenerating identical audio.
    """
    
    def __init__(self, cache_dir: Path = Path(".cache/audio")):
        """
        Initialize audio cache.
        
        Args:
            cache_dir: Directory for cached files
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
        logger.info(f"AudioCache initialized: {cache_dir}")
    
    def generate_key(
        self,
        text: str,
        voice_id: str,
        settings: dict
    ) -> str:
        """
        Generate cache key from content.
        
        Args:
            text: Dialogue text
            voice_id: Voice identifier
            settings: Voice settings
            
        Returns:
            SHA256 hash key
        """
        content = f"{text}:{voice_id}:{json.dumps(settings, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Path]:
        """
        Get cached audio file.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cached file if exists
        """
        if key in self.metadata:
            cached_path = Path(self.metadata[key]['path'])
            if cached_path.exists():
                logger.debug(f"Cache hit: {key[:8]}")
                return cached_path
        
        logger.debug(f"Cache miss: {key[:8]}")
        return None
    
    def set(self, key: str, audio_path: Path):
        """
        Store audio file in cache.
        
        Args:
            key: Cache key
            audio_path: Audio file to cache
        """
        # Copy to cache directory
        cached_path = self.cache_dir / f"{key}.mp3"
        
        import shutil
        shutil.copy(audio_path, cached_path)
        
        # Update metadata
        self.metadata[key] = {
            'path': str(cached_path),
            'original': str(audio_path)
        }
        
        self._save_metadata()
        logger.debug(f"Cached: {key[:8]}")
    
    def _load_metadata(self) -> dict:
        """Load cache metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save cache metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'total_entries': len(self.metadata),
            'cache_dir': str(self.cache_dir),
        }
