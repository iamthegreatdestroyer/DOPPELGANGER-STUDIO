"""
Sound Effects Placement Engine.

Automatically places sound effects at precise timestamps based on
script analysis and timing requirements.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import re
from pydub import AudioSegment

from src.services.audio.sfx.library import SFXLibrary, SoundEffect

logger = logging.getLogger(__name__)


@dataclass
class SFXPlacement:
    """Sound effect placement at specific timestamp."""
    effect: SoundEffect
    timestamp_ms: int  # Milliseconds from start
    volume: float = 0.7  # 0.0-1.0
    description: str = ""  # Why this effect was placed


class SFXPlacer:
    """
    Automatic sound effects placement engine.
    
    Features:
    - Script analysis for SFX opportunities
    - Action verb detection
    - Character entrance/exit detection
    - Comedy beat identification
    - Precise timing calculation
    
    Example:
        >>> placer = SFXPlacer(sfx_library)
        >>> placements = await placer.analyze_script(script)
        >>> audio = await placer.render_effects(placements, duration)
    """
    
    # Action verbs to SFX category mapping
    ACTION_KEYWORDS = {
        'actions': ['opens', 'closes', 'walks', 'sits', 'stands', 'picks', 'puts', 
                    'pours', 'drinks', 'eats', 'knocks', 'rings'],
        'impacts': ['slams', 'crashes', 'bangs', 'thuds', 'hits', 'drops', 
                   'throws', 'falls', 'smashes'],
        'comedy': ['stumbles', 'trips', 'bonks', 'bounces', 'squeaks', 'honks']
    }
    
    # Door-related keywords
    DOOR_KEYWORDS = ['door', 'opens door', 'closes door', 'slams door', 'enters', 'exits']
    
    def __init__(self, library: SFXLibrary):
        """
        Initialize SFX placer.
        
        Args:
            library: SFXLibrary instance
        """
        self.library = library
        logger.info("SFX placer initialized")
    
    async def analyze_script(
        self,
        script_lines: List[Dict],
        line_duration_ms: int = 3000
    ) -> List[SFXPlacement]:
        """
        Analyze script and identify SFX opportunities.
        
        Args:
            script_lines: List of script lines with format:
                [{'character': 'LUCY', 'line': 'text', 'action': 'description'}]
            line_duration_ms: Estimated duration per line in milliseconds
            
        Returns:
            List of SFXPlacement objects
        """
        placements = []
        current_time_ms = 0
        
        for i, line_data in enumerate(script_lines):
            # Extract action description if present
            action = line_data.get('action', '')
            line = line_data.get('line', '')
            character = line_data.get('character', '')
            
            # Analyze for SFX opportunities
            line_placements = self._analyze_line(
                action=action,
                line=line,
                character=character,
                timestamp_ms=current_time_ms
            )
            
            placements.extend(line_placements)
            
            # Advance time
            current_time_ms += line_duration_ms
        
        logger.info(f"Analyzed script: found {len(placements)} SFX placements")
        return placements
    
    def _analyze_line(
        self,
        action: str,
        line: str,
        character: str,
        timestamp_ms: int
    ) -> List[SFXPlacement]:
        """
        Analyze a single line for SFX opportunities.
        
        Args:
            action: Action description
            line: Dialogue line
            character: Character name
            timestamp_ms: Current timestamp
            
        Returns:
            List of placements for this line
        """
        placements = []
        
        # Combine action and line for analysis
        text = f"{action} {line}".lower()
        
        # Check for door actions
        for keyword in self.DOOR_KEYWORDS:
            if keyword in text:
                effect = self._select_door_effect(keyword)
                if effect:
                    placements.append(SFXPlacement(
                        effect=effect,
                        timestamp_ms=timestamp_ms,
                        description=f"Door action: {keyword}"
                    ))
                break
        
        # Check for action keywords
        for category, keywords in self.ACTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    effects = self.library.search(category=category, tags=[keyword])
                    if not effects:
                        # Fallback to any effect in category
                        effects = self.library.get_by_category(category, limit=1)
                    
                    if effects:
                        placements.append(SFXPlacement(
                            effect=effects[0],
                            timestamp_ms=timestamp_ms,
                            description=f"Action: {keyword}"
                        ))
                    break
        
        # Character entrances (generic whoosh)
        if 'enters' in text or 'walks in' in text:
            effects = self.library.search(category='transitions', tags=['whoosh'])
            if effects:
                placements.append(SFXPlacement(
                    effect=effects[0],
                    timestamp_ms=timestamp_ms,
                    volume=0.5,
                    description="Character entrance"
                ))
        
        return placements
    
    def _select_door_effect(self, keyword: str) -> Optional[SoundEffect]:
        """
        Select appropriate door sound effect.
        
        Args:
            keyword: Door-related keyword
            
        Returns:
            SoundEffect or None
        """
        # Map keywords to tags
        if 'slams' in keyword or 'slam' in keyword:
            effects = self.library.search(category='impacts', tags=['door', 'slam'])
        elif 'closes' in keyword:
            effects = self.library.search(category='actions', tags=['door', 'close'])
        elif 'opens' in keyword:
            effects = self.library.search(category='actions', tags=['door', 'open'])
        else:
            effects = self.library.search(category='actions', tags=['door'])
        
        return effects[0] if effects else None
    
    async def render_effects(
        self,
        placements: List[SFXPlacement],
        total_duration_ms: int
    ) -> AudioSegment:
        """
        Render all sound effects into a single audio track.
        
        Args:
            placements: List of SFX placements
            total_duration_ms: Total duration of final audio
            
        Returns:
            AudioSegment with all effects mixed in
        """
        # Create silent base track
        base = AudioSegment.silent(duration=total_duration_ms)
        
        # Overlay each effect
        for placement in placements:
            try:
                # Load effect
                effect_audio = AudioSegment.from_file(placement.effect.file_path)
                
                # Apply volume
                effect_audio = effect_audio + (placement.volume * 20 - 20)  # Convert to dB
                
                # Overlay at timestamp
                base = base.overlay(effect_audio, position=placement.timestamp_ms)
                
                logger.debug(f"Placed effect '{placement.effect.name}' at {placement.timestamp_ms}ms")
                
            except Exception as e:
                logger.error(f"Failed to place effect '{placement.effect.name}': {e}")
                continue
        
        logger.info(f"Rendered {len(placements)} sound effects")
        return base
    
    def get_placement_report(self, placements: List[SFXPlacement]) -> str:
        """
        Generate human-readable report of placements.
        
        Args:
            placements: List of placements
            
        Returns:
            Formatted report string
        """
        if not placements:
            return "No sound effects placed."
        
        lines = [f"Sound Effects Report ({len(placements)} effects):", "="*50]
        
        for i, placement in enumerate(placements, 1):
            timestamp_sec = placement.timestamp_ms / 1000.0
            lines.append(
                f"{i}. {placement.effect.name} @ {timestamp_sec:.1f}s "
                f"(vol: {placement.volume:.0%}) - {placement.description}"
            )
        
        return "\n".join(lines)
