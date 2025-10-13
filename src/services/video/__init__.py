"""
Video Services - Composition, Effects, and Export.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from src.services.video.composition.compositor import VideoCompositor
from src.services.video.composition.scene_assembler import SceneAssembler
from src.services.video.graphics.title_cards import TitleCardGenerator, TitleCardConfig
from src.services.video.graphics.credits import CreditsGenerator, CreditsConfig
from src.services.video.transitions.transition_engine import TransitionEngine
from src.services.video.effects.visual_effects import VisualEffects
from src.services.video.effects.color_grading import ColorGrading
from src.services.video.export.optimizer import ExportOptimizer
from src.services.video.export.youtube import YouTubeFormatter, YouTubeMetadata
from src.services.video.pipeline.video_pipeline import VideoPipeline

__all__ = [
    'VideoCompositor',
    'SceneAssembler',
    'TitleCardGenerator',
    'TitleCardConfig',
    'CreditsGenerator',
    'CreditsConfig',
    'TransitionEngine',
    'VisualEffects',
    'ColorGrading',
    'ExportOptimizer',
    'YouTubeFormatter',
    'YouTubeMetadata',
    'VideoPipeline',
]
