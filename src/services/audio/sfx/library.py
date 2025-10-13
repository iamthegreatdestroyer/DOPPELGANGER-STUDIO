"""
Sound Effects Library Management System.

Manages sound effects with categorization, search, and metadata.

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

logger = logging.getLogger(__name__)


@dataclass
class SoundEffect:
    """Sound effect with metadata."""
    id: str
    name: str
    file_path: Path
    category: str  # actions, impacts, ambience, ui, comedy, transitions
    subcategory: Optional[str] = None
    duration: float = 0.0  # seconds
    tags: List[str] = field(default_factory=list)
    volume_default: float = 0.7  # 0.0-1.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'name': self.name,
            'file_path': str(self.file_path),
            'category': self.category,
            'subcategory': self.subcategory,
            'duration': self.duration,
            'tags': self.tags,
            'volume_default': self.volume_default,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SoundEffect':
        """Create from dictionary."""
        data['file_path'] = Path(data['file_path'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class SFXLibrary:
    """
    Sound effects library management.
    
    Categories:
    - actions: door, footsteps, pour, etc.
    - impacts: crash, bang, thud, slam
    - ambience: crowd, traffic, nature, office
    - ui: whoosh, ding, pop, swoosh
    - comedy: boing, kazoo, slide_whistle, rimshot
    - transitions: swoosh, whoosh, zap
    
    Example:
        >>> library = SFXLibrary("sfx_library")
        >>> await library.import_effect(
        ...     "door_slam.wav",
        ...     category="actions",
        ...     tags=["door", "slam", "loud"]
        ... )
        >>> effects = library.search(category="actions", tags=["door"])
    """
    
    # Valid categories
    CATEGORIES = {
        'actions': ['door', 'footsteps', 'pour', 'pick_up', 'put_down'],
        'impacts': ['crash', 'bang', 'thud', 'slam', 'hit'],
        'ambience': ['crowd', 'traffic', 'nature', 'office', 'home'],
        'ui': ['whoosh', 'ding', 'pop', 'swoosh', 'click'],
        'comedy': ['boing', 'kazoo', 'slide_whistle', 'rimshot', 'honk'],
        'transitions': ['swoosh', 'whoosh', 'zap', 'glitch', 'zoom']
    }
    
    def __init__(self, library_path: Path):
        """
        Initialize SFX library.
        
        Args:
            library_path: Root directory for SFX library
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        self.effects: Dict[str, SoundEffect] = {}
        self.index_path = self.library_path / "sfx_index.json"
        
        self._load_index()
        
        logger.info(f"SFX library initialized with {len(self.effects)} effects")
    
    def _load_index(self):
        """Load SFX index from disk."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    data = json.load(f)
                    self.effects = {
                        effect_id: SoundEffect.from_dict(effect_data)
                        for effect_id, effect_data in data.items()
                    }
                logger.info(f"Loaded {len(self.effects)} effects from index")
            except Exception as e:
                logger.error(f"Failed to load SFX index: {e}")
                self.effects = {}
    
    def _save_index(self):
        """Save SFX index to disk."""
        try:
            data = {
                effect_id: effect.to_dict()
                for effect_id, effect in self.effects.items()
            }
            with open(self.index_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("SFX index saved")
        except Exception as e:
            logger.error(f"Failed to save SFX index: {e}")
    
    async def import_effect(
        self,
        file_path: Path,
        category: str,
        name: Optional[str] = None,
        subcategory: Optional[str] = None,
        tags: Optional[List[str]] = None,
        volume_default: float = 0.7
    ) -> SoundEffect:
        """
        Import a sound effect into the library.
        
        Args:
            file_path: Path to audio file
            category: Effect category
            name: Effect name (defaults to filename)
            subcategory: Optional subcategory
            tags: List of tags for search
            volume_default: Default volume (0.0-1.0)
            
        Returns:
            SoundEffect object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If category invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"SFX file not found: {file_path}")
        
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {list(self.CATEGORIES.keys())}")
        
        # Generate unique ID
        effect_id = self._generate_effect_id(file_path)
        
        # Extract duration
        duration = self._get_duration(file_path)
        
        # Create effect object
        effect = SoundEffect(
            id=effect_id,
            name=name or file_path.stem,
            file_path=file_path,
            category=category,
            subcategory=subcategory,
            duration=duration,
            tags=tags or [],
            volume_default=max(0.0, min(1.0, volume_default))
        )
        
        # Add to library
        self.effects[effect_id] = effect
        self._save_index()
        
        logger.info(f"Imported effect: {effect.name} ({effect.duration:.2f}s)")
        
        return effect
    
    def _generate_effect_id(self, file_path: Path) -> str:
        """Generate unique ID for effect."""
        path_str = str(file_path.absolute())
        return hashlib.md5(path_str.encode()).hexdigest()[:16]
    
    def _get_duration(self, file_path: Path) -> float:
        """Get audio duration in seconds."""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception as e:
            logger.error(f"Failed to get duration: {e}")
            return 0.0
    
    def get_effect(self, effect_id: str) -> Optional[SoundEffect]:
        """Get effect by ID."""
        return self.effects.get(effect_id)
    
    def search(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_duration: Optional[float] = None
    ) -> List[SoundEffect]:
        """
        Search for effects matching criteria.
        
        Args:
            name: Name contains string (case-insensitive)
            category: Has this category
            subcategory: Has this subcategory
            tags: Has any of these tags
            max_duration: Maximum duration in seconds
            
        Returns:
            List of matching effects
        """
        results = []
        
        for effect in self.effects.values():
            if name and name.lower() not in effect.name.lower():
                continue
            
            if category and effect.category != category:
                continue
            
            if subcategory and effect.subcategory != subcategory:
                continue
            
            if tags and not any(tag in effect.tags for tag in tags):
                continue
            
            if max_duration and effect.duration > max_duration:
                continue
            
            results.append(effect)
        
        logger.debug(f"Search found {len(results)} effects")
        return results
    
    def get_by_category(self, category: str, limit: int = 10) -> List[SoundEffect]:
        """Get effects by category."""
        effects = self.search(category=category)
        return effects[:limit]
    
    def get_random(self, category: Optional[str] = None, count: int = 1) -> List[SoundEffect]:
        """Get random effects, optionally filtered by category."""
        import random
        
        if category:
            pool = [e for e in self.effects.values() if e.category == category]
        else:
            pool = list(self.effects.values())
        
        return random.sample(pool, min(count, len(pool)))
    
    def get_all_categories(self) -> Set[str]:
        """Get all unique categories in library."""
        return set(e.category for e in self.effects.values())
    
    def get_stats(self) -> Dict:
        """Get library statistics."""
        if not self.effects:
            return {
                'total_effects': 0,
                'categories': {},
                'avg_duration': 0.0
            }
        
        # Count by category
        category_counts = {}
        for effect in self.effects.values():
            category_counts[effect.category] = category_counts.get(effect.category, 0) + 1
        
        total_duration = sum(e.duration for e in self.effects.values())
        
        return {
            'total_effects': len(self.effects),
            'categories': category_counts,
            'avg_duration': total_duration / len(self.effects),
            'total_duration': total_duration
        }
