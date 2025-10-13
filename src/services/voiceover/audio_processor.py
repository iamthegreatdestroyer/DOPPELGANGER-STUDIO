"""
Audio Processor - Audio effects and processing.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from pathlib import Path
import logging

try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Process and enhance audio files.
    
    Features:
    - Volume normalization
    - Silence trimming
    - Fade in/out
    - Format conversion
    """
    
    def __init__(self):
        """Initialize audio processor."""
        if not PYDUB_AVAILABLE:
            raise ImportError("Install: pip install pydub")
        
        logger.info("AudioProcessor initialized")
    
    def normalize_volume(self, audio_path: Path) -> AudioSegment:
        """
        Normalize audio volume.
        
        Args:
            audio_path: Input audio file
            
        Returns:
            Normalized AudioSegment
        """
        audio = AudioSegment.from_file(audio_path)
        return normalize(audio)
    
    def trim_silence(
        self,
        audio: AudioSegment,
        silence_thresh: int = -50
    ) -> AudioSegment:
        """
        Trim leading/trailing silence.
        
        Args:
            audio: Audio to process
            silence_thresh: Silence threshold in dB
            
        Returns:
            Trimmed audio
        """
        from pydub.silence import detect_leading_silence
        
        start_trim = detect_leading_silence(audio, silence_thresh)
        end_trim = detect_leading_silence(audio.reverse(), silence_thresh)
        
        duration = len(audio)
        return audio[start_trim:duration-end_trim]
    
    def add_fades(
        self,
        audio: AudioSegment,
        fade_in_ms: int = 50,
        fade_out_ms: int = 100
    ) -> AudioSegment:
        """
        Add fade in/out.
        
        Args:
            audio: Audio to process
            fade_in_ms: Fade in duration
            fade_out_ms: Fade out duration
            
        Returns:
            Audio with fades
        """
        return audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
    
    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        normalize: bool = True,
        trim: bool = True,
        fades: bool = True
    ) -> Path:
        """
        Complete audio processing pipeline.
        
        Args:
            input_path: Input file
            output_path: Output file
            normalize: Apply normalization
            trim: Trim silence
            fades: Add fades
            
        Returns:
            Path to processed file
        """
        audio = AudioSegment.from_file(input_path)
        
        if normalize:
            audio = self.normalize_volume(input_path)
        
        if trim:
            audio = self.trim_silence(audio)
        
        if fades:
            audio = self.add_fades(audio)
        
        audio.export(output_path, format="mp3")
        logger.info(f"Processed audio: {output_path.name}")
        
        return output_path
