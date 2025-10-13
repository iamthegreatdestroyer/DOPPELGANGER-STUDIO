"""
Voice Manager - Manage character voice profiles.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Optional
import logging

from src.models.voice_profile import VoiceProfile

logger = logging.getLogger(__name__)


class VoiceManager:
    """
    Manages voice profiles for characters.
    
    Stores and retrieves voice configurations, handles fallbacks.
    
    Example:
        >>> manager = VoiceManager()
        >>> manager.add_profile(lucy_profile)
        >>> profile = manager.get_profile("Lucy Ricardo")
    """
    
    def __init__(self):
        """Initialize voice manager."""
        self.profiles: Dict[str, VoiceProfile] = {}
        logger.info("VoiceManager initialized")
    
    def add_profile(self, profile: VoiceProfile):
        """
        Add voice profile.
        
        Args:
            profile: VoiceProfile to add
        """
        self.profiles[profile.character_name] = profile
        logger.debug(f"Added voice profile: {profile.character_name}")
    
    def get_profile(self, character_name: str) -> Optional[VoiceProfile]:
        """
        Get voice profile for character.
        
        Args:
            character_name: Character name
            
        Returns:
            VoiceProfile if found
        """
        return self.profiles.get(character_name)
    
    def list_profiles(self) -> Dict[str, VoiceProfile]:
        """Get all profiles."""
        return self.profiles.copy()
    
    def create_default_profiles(self) -> Dict[str, VoiceProfile]:
        """
        Create default voice profiles for common characters.
        
        Returns:
            Dictionary of default profiles
        """
        defaults = {
            "Lucy Ricardo": VoiceProfile(
                character_name="Lucy Ricardo",
                voice_id="rachel",
                engine="elevenlabs",
                settings={
                    "stability": 0.7,
                    "similarity_boost": 0.8,
                },
                description="Enthusiastic 1950s housewife"
            ),
            "Ricky Ricardo": VoiceProfile(
                character_name="Ricky Ricardo",
                voice_id="adam",
                engine="elevenlabs",
                settings={
                    "stability": 0.75,
                    "similarity_boost": 0.75,
                },
                description="Warm Cuban bandleader"
            ),
        }
        
        for profile in defaults.values():
            self.add_profile(profile)
        
        return defaults
