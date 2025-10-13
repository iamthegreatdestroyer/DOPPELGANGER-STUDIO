"""
Music Library Management System.

Manages background music tracks with metadata extraction,
categorization, and search capabilities.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import hashlib
import logging
from pydub import AudioSegment
from pydub.utils import mediainfo

logger = logging.getLogger(__name__)


@dataclass
class MusicTrack:
    """Music track with comprehensive metadata."""
    id: str
    title: str
    file_path: Path
    duration: float  # seconds
    bpm: Optional[int] = None
    key: Optional[str] = None  # Musical key (C, Am, etc.)
    genre: List[str] = field(default_factory=list)
    mood: List[str] = field(default_factory=list)  # happy, sad, tense, etc.
    energy_level: int = 5  # 1-10 scale
    instrumentation: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    sample_rate: int = 44100
    channels: int = 2
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'file_path': str(self.file_path),
            'duration': self.duration,
            'bpm': self.bpm,
            'key': self.key,
            'genre': self.genre,
            'mood': self.mood,
            'energy_level': self.energy_level,
            'instrumentation': self.instrumentation,
            'tags': self.tags,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MusicTrack':
        """Create from dictionary."""
        data['file_path'] = Path(data['file_path'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class MusicLibrary:
    """
    Music library management system.
    
    Features:
    - Import music files (MP3, WAV, FLAC, OGG)
    - Extract metadata automatically
    - Categorize by genre, mood, energy
    - Search and filter capabilities
    - Persistent storage
    
    Example:
        >>> library = MusicLibrary("music_library")
        >>> await library.import_track(
        ...     "happy_theme.mp3",
        ...     genre=["comedy"],
        ...     mood=["happy", "upbeat"],
        ...     energy_level=8
        ... )
        >>> tracks = library.search(mood="happy", min_energy=7)
    """
    
    def __init__(self, library_path: Path):
        """
        Initialize music library.
        
        Args:
            library_path: Root directory for music library
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        self.tracks: Dict[str, MusicTrack] = {}
        self.index_path = self.library_path / "music_index.json"
        
        self._load_index()
        
        logger.info(f"Music library initialized with {len(self.tracks)} tracks")
    
    def _load_index(self):
        """Load music index from disk."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    data = json.load(f)
                    self.tracks = {
                        track_id: MusicTrack.from_dict(track_data)
                        for track_id, track_data in data.items()
                    }
                logger.info(f"Loaded {len(self.tracks)} tracks from index")
            except Exception as e:
                logger.error(f"Failed to load music index: {e}")
                self.tracks = {}
    
    def _save_index(self):
        """Save music index to disk."""
        try:
            data = {
                track_id: track.to_dict()
                for track_id, track in self.tracks.items()
            }
            with open(self.index_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Music index saved")
        except Exception as e:
            logger.error(f"Failed to save music index: {e}")
    
    async def import_track(
        self,
        file_path: Path,
        title: Optional[str] = None,
        genre: Optional[List[str]] = None,
        mood: Optional[List[str]] = None,
        energy_level: int = 5,
        **kwargs
    ) -> MusicTrack:
        """
        Import a music track into the library.
        
        Args:
            file_path: Path to audio file
            title: Track title (defaults to filename)
            genre: List of genres
            mood: List of moods
            energy_level: Energy level 1-10
            **kwargs: Additional metadata
            
        Returns:
            MusicTrack object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format unsupported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Music file not found: {file_path}")
        
        # Generate unique ID
        track_id = self._generate_track_id(file_path)
        
        # Extract audio metadata
        metadata = self._extract_metadata(file_path)
        
        # Create track object
        track = MusicTrack(
            id=track_id,
            title=title or file_path.stem,
            file_path=file_path,
            duration=metadata['duration'],
            genre=genre or [],
            mood=mood or [],
            energy_level=max(1, min(10, energy_level)),
            sample_rate=metadata.get('sample_rate', 44100),
            channels=metadata.get('channels', 2),
            **kwargs
        )
        
        # Add to library
        self.tracks[track_id] = track
        self._save_index()
        
        logger.info(f"Imported track: {track.title} ({track.duration:.1f}s)")
        
        return track
    
    def _generate_track_id(self, file_path: Path) -> str:
        """Generate unique ID for track."""
        # Use file path hash
        path_str = str(file_path.absolute())
        return hashlib.md5(path_str.encode()).hexdigest()[:16]
    
    def _extract_metadata(self, file_path: Path) -> Dict:
        """
        Extract audio metadata from file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with duration, sample_rate, channels
        """
        try:
            # Use pydub to load and extract metadata
            audio = AudioSegment.from_file(file_path)
            
            metadata = {
                'duration': len(audio) / 1000.0,  # Convert ms to seconds
                'sample_rate': audio.frame_rate,
                'channels': audio.channels
            }
            
            logger.debug(f"Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            # Return defaults
            return {
                'duration': 0.0,
                'sample_rate': 44100,
                'channels': 2
            }
    
    def get_track(self, track_id: str) -> Optional[MusicTrack]:
        """Get track by ID."""
        return self.tracks.get(track_id)
    
    def search(
        self,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        min_energy: Optional[int] = None,
        max_energy: Optional[int] = None,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[MusicTrack]:
        """
        Search for tracks matching criteria.
        
        Args:
            title: Title contains string (case-insensitive)
            genre: Has genre in list
            mood: Has mood in list
            min_energy: Minimum energy level
            max_energy: Maximum energy level
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            tags: Has any of these tags
            
        Returns:
            List of matching tracks
        """
        results = []
        
        for track in self.tracks.values():
            # Check all criteria
            if title and title.lower() not in track.title.lower():
                continue
            
            if genre and genre not in track.genre:
                continue
            
            if mood and mood not in track.mood:
                continue
            
            if min_energy and track.energy_level < min_energy:
                continue
            
            if max_energy and track.energy_level > max_energy:
                continue
            
            if min_duration and track.duration < min_duration:
                continue
            
            if max_duration and track.duration > max_duration:
                continue
            
            if tags and not any(tag in track.tags for tag in tags):
                continue
            
            results.append(track)
        
        logger.debug(f"Search found {len(results)} tracks")
        return results
    
    def get_by_mood(self, mood: str, limit: int = 10) -> List[MusicTrack]:
        """Get tracks by mood, sorted by relevance."""
        tracks = self.search(mood=mood)
        return tracks[:limit]
    
    def get_by_energy(self, min_energy: int, max_energy: int, limit: int = 10) -> List[MusicTrack]:
        """Get tracks by energy level range."""
        tracks = self.search(min_energy=min_energy, max_energy=max_energy)
        return tracks[:limit]
    
    def get_random(self, count: int = 1) -> List[MusicTrack]:
        """Get random tracks from library."""
        import random
        tracks = list(self.tracks.values())
        return random.sample(tracks, min(count, len(tracks)))
    
    def get_all_genres(self) -> Set[str]:
        """Get all unique genres in library."""
        genres = set()
        for track in self.tracks.values():
            genres.update(track.genre)
        return genres
    
    def get_all_moods(self) -> Set[str]:
        """Get all unique moods in library."""
        moods = set()
        for track in self.tracks.values():
            moods.update(track.mood)
        return moods
    
    def get_stats(self) -> Dict:
        """Get library statistics."""
        if not self.tracks:
            return {
                'total_tracks': 0,
                'total_duration': 0.0,
                'genres': [],
                'moods': [],
                'avg_duration': 0.0
            }
        
        total_duration = sum(t.duration for t in self.tracks.values())
        
        return {
            'total_tracks': len(self.tracks),
            'total_duration': total_duration,
            'total_duration_hours': total_duration / 3600,
            'genres': sorted(self.get_all_genres()),
            'moods': sorted(self.get_all_moods()),
            'avg_duration': total_duration / len(self.tracks),
            'energy_distribution': self._get_energy_distribution()
        }
    
    def _get_energy_distribution(self) -> Dict[int, int]:
        """Get distribution of energy levels."""
        distribution = {i: 0 for i in range(1, 11)}
        for track in self.tracks.values():
            distribution[track.energy_level] += 1
        return distribution
