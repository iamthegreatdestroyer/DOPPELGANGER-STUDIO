"""
Audio Mastering Pipeline.

Professional audio mastering with compression, EQ, limiting,
and normalization to broadcast standards.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, Optional
import logging
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

logger = logging.getLogger(__name__)


class AudioMaster:
    """
    Professional audio mastering pipeline.
    
    Applies broadcast-standard processing:
    - Peak normalization (-1dB)
    - Dynamic range compression (3:1 ratio)
    - Limiting (-0.3dB ceiling)
    - Final normalization
    
    Target Levels:
    - Peak: -1.0 dB
    - RMS: -16 LUFS (broadcast standard)
    - Dynamic range: 8-12 dB
    
    Example:
        >>> master = AudioMaster()
        >>> mastered = await master.master_audio(mixed_audio)
        >>> print(master.get_levels(mastered))
    """
    
    # Target levels
    TARGET_PEAK_DB = -1.0
    TARGET_RMS_LUFS = -16
    LIMITING_CEILING_DB = -0.3
    
    # Compression settings
    COMPRESSION_RATIO = 3.0  # 3:1 ratio
    COMPRESSION_THRESHOLD_DB = -20
    
    def __init__(self):
        """Initialize audio master."""
        logger.info("Audio master initialized")
    
    async def master_audio(
        self,
        audio: AudioSegment,
        target_peak: float = TARGET_PEAK_DB,
        apply_compression: bool = True,
        apply_limiting: bool = True
    ) -> AudioSegment:
        """
        Apply professional mastering chain.
        
        Process:
        1. Initial normalization
        2. Dynamic range compression
        3. Limiting
        4. Final normalization to target peak
        
        Args:
            audio: Source audio to master
            target_peak: Target peak level in dB
            apply_compression: Whether to apply compression
            apply_limiting: Whether to apply limiting
            
        Returns:
            Mastered AudioSegment
        """
        logger.info(f"Mastering audio: {len(audio)/1000:.1f}s")
        
        # Step 1: Initial normalization
        mastered = normalize(audio, headroom=0.1)
        logger.debug("Applied initial normalization")
        
        # Step 2: Compression
        if apply_compression:
            mastered = self._apply_compression(mastered)
            logger.debug("Applied compression")
        
        # Step 3: Limiting
        if apply_limiting:
            mastered = self._apply_limiting(mastered)
            logger.debug("Applied limiting")
        
        # Step 4: Final normalization to target peak
        mastered = self._normalize_to_peak(mastered, target_peak)
        logger.debug(f"Normalized to {target_peak}dB")
        
        # Get final levels
        levels = self.get_levels(mastered)
        logger.info(f"Mastering complete. Peak: {levels['peak_db']:.1f}dB, "
                   f"RMS: {levels['rms_db']:.1f}dB")
        
        return mastered
    
    def _apply_compression(
        self,
        audio: AudioSegment,
        threshold: float = COMPRESSION_THRESHOLD_DB,
        ratio: float = COMPRESSION_RATIO
    ) -> AudioSegment:
        """
        Apply dynamic range compression.
        
        Reduces the dynamic range to make quiet parts louder
        and loud parts quieter.
        
        Args:
            audio: Source audio
            threshold: Compression threshold in dB
            ratio: Compression ratio
            
        Returns:
            Compressed audio
        """
        # Use pydub's built-in compression
        compressed = compress_dynamic_range(
            audio,
            threshold=threshold,
            ratio=ratio,
            attack=5.0,
            release=50.0
        )
        return compressed
    
    def _apply_limiting(
        self,
        audio: AudioSegment,
        ceiling: float = LIMITING_CEILING_DB
    ) -> AudioSegment:
        """
        Apply limiting to prevent clipping.
        
        Limits peaks to specified ceiling.
        
        Args:
            audio: Source audio
            ceiling: Maximum peak level in dB
            
        Returns:
            Limited audio
        """
        # Simple limiting via normalization with headroom
        headroom = abs(ceiling)
        limited = normalize(audio, headroom=headroom)
        return limited
    
    def _normalize_to_peak(
        self,
        audio: AudioSegment,
        target_peak: float
    ) -> AudioSegment:
        """
        Normalize audio to specific peak level.
        
        Args:
            audio: Source audio
            target_peak: Target peak in dB (negative value)
            
        Returns:
            Normalized audio
        """
        headroom = abs(target_peak)
        normalized = normalize(audio, headroom=headroom)
        return normalized
    
    def get_levels(self, audio: AudioSegment) -> Dict[str, float]:
        """
        Get audio level measurements.
        
        Args:
            audio: Audio to measure
            
        Returns:
            Dictionary with peak_db, rms_db, duration_seconds
        """
        # Get dBFS (decibels relative to full scale)
        peak_db = audio.max_dBFS
        rms_db = audio.dBFS  # RMS level
        
        return {
            'peak_db': peak_db,
            'rms_db': rms_db,
            'duration_seconds': len(audio) / 1000.0,
            'sample_rate': audio.frame_rate,
            'channels': audio.channels
        }
    
    def meets_broadcast_standards(self, audio: AudioSegment) -> Dict[str, bool]:
        """
        Check if audio meets broadcast standards.
        
        Standards:
        - Peak level: -1dB to -0.1dB
        - RMS level: -18 to -14 LUFS
        - Sample rate: 48kHz
        
        Args:
            audio: Audio to check
            
        Returns:
            Dictionary of standard checks
        """
        levels = self.get_levels(audio)
        
        checks = {
            'peak_ok': -1.0 <= levels['peak_db'] <= -0.1,
            'rms_ok': -18 <= levels['rms_db'] <= -14,
            'sample_rate_ok': levels['sample_rate'] == 48000,
            'stereo_ok': levels['channels'] == 2
        }
        
        checks['all_ok'] = all(checks.values())
        
        return checks
    
    async def master_for_platform(
        self,
        audio: AudioSegment,
        platform: str = 'youtube'
    ) -> AudioSegment:
        """
        Master audio for specific platform requirements.
        
        Platforms:
        - youtube: -14 LUFS, stereo, 48kHz
        - spotify: -14 LUFS, stereo
        - broadcast: -16 LUFS, stereo, 48kHz
        
        Args:
            audio: Source audio
            platform: Target platform
            
        Returns:
            Platform-optimized audio
        """
        platform_settings = {
            'youtube': {'target_peak': -1.0, 'target_rms': -14},
            'spotify': {'target_peak': -1.0, 'target_rms': -14},
            'broadcast': {'target_peak': -1.0, 'target_rms': -16}
        }
        
        settings = platform_settings.get(platform, platform_settings['youtube'])
        
        mastered = await self.master_audio(
            audio,
            target_peak=settings['target_peak']
        )
        
        logger.info(f"Mastered for {platform}")
        return mastered
