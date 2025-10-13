"""
Intelligent Music Selection System.

Selects appropriate background music based on scene context,
mood, energy level, and duration requirements.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
import random
from dataclasses import dataclass
from pydub import AudioSegment

from src.services.audio.music.library import MusicLibrary, MusicTrack

logger = logging.getLogger(__name__)


@dataclass
class SceneContext:
    """Context information for scene."""
    mood: str  # happy, sad, tense, dramatic, comedic
    energy: int  # 1-10
    duration: float  # seconds
    genre: Optional[str] = None
    previous_track_id: Optional[str] = None  # For variety


class MusicSelector:
    """
    Intelligent music selection for scenes.
    
    Features:
    - Mood-based selection
    - Energy level matching
    - Duration handling (trim/loop)
    - Variety management
    - Fade in/out
    
    Example:
        >>> selector = MusicSelector(music_library)
        >>> context = SceneContext(
        ...     mood="happy",
        ...     energy=8,
        ...     duration=30.0
        ... )
        >>> audio = await selector.select_and_prepare(context)
    """
    
    # Mood to energy mapping
    MOOD_ENERGY_MAP = {
        'happy': (6, 10),
        'sad': (1, 4),
        'tense': (7, 10),
        'dramatic': (5, 8),
        'comedic': (6, 9),
        'calm': (1, 3),
        'upbeat': (7, 10),
        'melancholic': (2, 5),
        'suspenseful': (6, 9),
        'romantic': (3, 6)
    }
    
    def __init__(self, library: MusicLibrary):
        """
        Initialize music selector.
        
        Args:
            library: MusicLibrary instance
        """
        self.library = library
        self.selection_history: List[str] = []  # Track IDs
        self.max_history = 10  # Prevent repeats
        
        logger.info("Music selector initialized")
    
    async def select_track(
        self,
        context: SceneContext
    ) -> Optional[MusicTrack]:
        """
        Select appropriate music track for scene context.
        
        Args:
            context: Scene context with mood, energy, duration
            
        Returns:
            Selected MusicTrack or None if no match
        """
        # Get energy range for mood
        min_energy, max_energy = self._get_energy_range(context.mood, context.energy)
        
        # Search for matching tracks
        candidates = self.library.search(
            mood=context.mood,
            min_energy=min_energy,
            max_energy=max_energy
        )
        
        # Filter by genre if specified
        if context.genre:
            candidates = [
                t for t in candidates
                if context.genre in t.genre
            ]
        
        # Filter out recent selections for variety
        candidates = [
            t for t in candidates
            if t.id not in self.selection_history
        ]
        
        # If no candidates after filtering, allow repeats
        if not candidates:
            candidates = self.library.search(
                mood=context.mood,
                min_energy=min_energy,
                max_energy=max_energy
            )
        
        if not candidates:
            logger.warning(f"No tracks found for mood='{context.mood}', energy={context.energy}")
            return None
        
        # Select track (prefer those close to target duration)
        track = self._select_best_match(candidates, context)
        
        # Update history
        self.selection_history.append(track.id)
        if len(self.selection_history) > self.max_history:
            self.selection_history.pop(0)
        
        logger.info(f"Selected track: {track.title} for mood='{context.mood}'")
        return track
    
    def _get_energy_range(self, mood: str, target_energy: int) -> tuple:
        """
        Get energy range for mood.
        
        Args:
            mood: Target mood
            target_energy: Target energy level
            
        Returns:
            (min_energy, max_energy) tuple
        """
        # Use mood-based range if available
        if mood.lower() in self.MOOD_ENERGY_MAP:
            return self.MOOD_ENERGY_MAP[mood.lower()]
        
        # Otherwise use target_energy ±2
        return (max(1, target_energy - 2), min(10, target_energy + 2))
    
    def _select_best_match(
        self,
        candidates: List[MusicTrack],
        context: SceneContext
    ) -> MusicTrack:
        """
        Select best track from candidates.
        
        Prioritizes tracks with duration close to target.
        
        Args:
            candidates: List of candidate tracks
            context: Scene context
            
        Returns:
            Best matching track
        """
        if len(candidates) == 1:
            return candidates[0]
        
        # Score each candidate based on duration match
        scored = []
        for track in candidates:
            duration_diff = abs(track.duration - context.duration)
            
            # Prefer tracks slightly longer than needed (can trim)
            if track.duration >= context.duration:
                score = -duration_diff  # Higher score for closer match
            else:
                # Penalize tracks that are too short (need looping)
                score = -duration_diff * 2
            
            scored.append((score, track))
        
        # Sort by score (highest first)
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # Return best match
        return scored[0][1]
    
    async def select_and_prepare(
        self,
        context: SceneContext,
        fade_in_ms: int = 500,
        fade_out_ms: int = 1000
    ) -> Optional[AudioSegment]:
        """
        Select track and prepare audio for scene.
        
        Handles duration adjustment (trim or loop) and fades.
        
        Args:
            context: Scene context
            fade_in_ms: Fade in duration in milliseconds
            fade_out_ms: Fade out duration in milliseconds
            
        Returns:
            Prepared AudioSegment or None if no track found
        """
        # Select track
        track = await self.select_track(context)
        if not track:
            return None
        
        # Load audio
        try:
            audio = AudioSegment.from_file(track.file_path)
        except Exception as e:
            logger.error(f"Failed to load track {track.title}: {e}")
            return None
        
        # Adjust duration
        target_ms = int(context.duration * 1000)
        audio = self._adjust_duration(audio, target_ms)
        
        # Apply fades
        audio = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
        
        logger.debug(f"Prepared audio: {len(audio)/1000:.1f}s")
        return audio
    
    def _adjust_duration(
        self,
        audio: AudioSegment,
        target_ms: int
    ) -> AudioSegment:
        """
        Adjust audio duration to target.
        
        Trims if too long, loops if too short.
        
        Args:
            audio: Source audio
            target_ms: Target duration in milliseconds
            
        Returns:
            Adjusted audio
        """
        current_ms = len(audio)
        
        if current_ms > target_ms:
            # Trim to target duration
            return audio[:target_ms]
        
        elif current_ms < target_ms:
            # Loop to reach target duration
            loops_needed = (target_ms // current_ms) + 1
            looped = audio * loops_needed
            return looped[:target_ms]
        
        else:
            # Exact match
            return audio
    
    def get_selection_stats(self) -> Dict:
        """Get statistics about track selections."""
        return {
            'total_selections': len(self.selection_history),
            'unique_tracks': len(set(self.selection_history)),
            'recent_selections': self.selection_history[-5:]
        }
