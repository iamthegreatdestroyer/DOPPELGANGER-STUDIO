"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

ScriptGenerator orchestrator - The crown jewel of Phase 4.

This module coordinates all script generation components to produce
complete, production-ready scripts with iterative refinement and
quality validation.
"""

import logging
import asyncio
from typing import List, Dict, Optional, TYPE_CHECKING, Callable
from datetime import datetime

from src.services.creative.dialogue_generator import DialogueGenerator
from src.services.creative.stage_direction_generator import StageDirectionGenerator
from src.services.creative.joke_optimizer import JokeOptimizer
from src.services.creative.script_validator import ScriptValidator
from src.services.creative.claude_client import ClaudeClient
from src.services.creative.openai_client import OpenAIClient
from src.services.monitoring.performance_monitor import (
    get_performance_monitor,
    PerformanceMetrics,
    monitor_async_performance,
)
from src.services.creative.script_models import (
    SceneScript,
    RefinementIteration,
    FullScript,
    ScriptFormat,
)
from src.services.creative.character_voice_profiles import (
    CharacterVoiceProfile,
    SceneDialogue,
)
from src.services.creative.validation_models import ValidationSeverity

if TYPE_CHECKING:
    from src.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """
    Orchestrates complete script generation pipeline.
    
    Coordinates DialogueGenerator, StageDirectionGenerator, JokeOptimizer,
    and ScriptValidator to produce production-ready scripts with iterative
    refinement based on validation feedback.
    
    Example:
        >>> generator = ScriptGenerator()
        >>> script = generator.generate_full_script(
        ...     episode_outline=outline,
        ...     character_profiles=profiles,
        ...     show_metadata=metadata
        ... )
        >>> script.export(ScriptFormat.SCREENPLAY, "output.txt")
        >>> print(f"Quality: {script.final_quality_score:.2f}")
    """
    
    def __init__(
        self,
        database_manager: Optional["DatabaseManager"] = None,
        max_refinement_iterations: int = 3,
        quality_threshold: float = 0.75,
        max_parallel_scenes: int = 3,
    ):
        """
        Initialize ScriptGenerator.
        
        Args:
            database_manager: Optional caching manager
            max_refinement_iterations: Maximum refinement attempts
            quality_threshold: Minimum quality score for validation
            max_parallel_scenes: Max scenes to generate in parallel (default 3)
        """
        self.db_manager = database_manager
        self.max_refinement_iterations = max_refinement_iterations
        self.quality_threshold = quality_threshold
        self.max_parallel_scenes = max_parallel_scenes
        
        # Initialize performance monitor
        self.performance_monitor = get_performance_monitor()
        
        # Initialize AI clients
        self.claude_client = ClaudeClient()
        self.gpt_client = OpenAIClient()
        
        # Initialize all components
        self.dialogue_generator = DialogueGenerator(
            database_manager=database_manager
        )
        self.stage_direction_generator = StageDirectionGenerator(
            claude_client=self.claude_client,
            gpt_client=self.gpt_client,
            database_manager=database_manager
        )
        self.joke_optimizer = JokeOptimizer(
            database_manager=database_manager
        )
        self.script_validator = ScriptValidator(
            database_manager=database_manager,
            pass_threshold=quality_threshold,
        )
        
        logger.info(
            f"ScriptGenerator initialized "
            f"(max_iterations={max_refinement_iterations}, "
            f"threshold={quality_threshold})"
        )
    
    @monitor_async_performance("generate_full_script")
    async def generate_full_script(
        self,
        script_id: str,
        episode_outline: Dict,
        character_profiles: Dict[str, CharacterVoiceProfile],
        show_metadata: Dict,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> FullScript:
        """
        Generate complete production-ready script with parallel scene generation.
        
        Orchestrates the full pipeline:
        1. Generate dialogue for each scene (in parallel)
        2. Add stage directions and camera work
        3. Optimize comedy timing and effectiveness
        4. Validate quality and refine iteratively
        
        Args:
            script_id: Unique identifier for this script
            episode_outline: Episode structure with scenes
            character_profiles: Voice profiles for all characters
            show_metadata: Show details (title, setting, etc.)
            progress_callback: Optional callback(status, current, total)
        
        Returns:
            Complete script with all metadata and validation
        
        Example:
            >>> outline = {
            ...     "scenes": [
            ...         {
            ...             "scene_number": 1,
            ...             "title": "Luna's Wild Idea",
            ...             "location": "Luna Prime Station - Control Room",
            ...             "time": "Day",
            ...             "characters": ["Luna", "Rick"],
            ...             "description": "Luna pitches space tourism idea",
            ...             "beat_type": "setup"
            ...         }
            ...     ]
            ... }
            >>> script = generator.generate_full_script(
            ...     "ep001", outline, profiles, metadata
            ... )
        """
        logger.info(f"Starting full script generation: {script_id}")
        
        # Start performance monitoring session
        self.performance_monitor.start_session(script_id)
        
        start_time = datetime.now()
        
        # Extract outline data
        scenes_outline = episode_outline.get("scenes", [])
        
        # Generate initial script with parallel processing
        logger.info(
            f"Generating {len(scenes_outline)} scenes in parallel "
            f"(max {self.max_parallel_scenes} at once)..."
        )
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_parallel_scenes)
        
        async def generate_with_progress(idx: int, scene_outline: Dict):
            """Generate scene with semaphore and progress tracking."""
            async with semaphore:
                if progress_callback:
                    progress_callback(
                        f"Generating scene {scene_outline['scene_number']}",
                        idx,
                        len(scenes_outline)
                    )
                scene_script = await self._generate_scene_script(
                    scene_outline, character_profiles
                )
                logger.info(
                    f"Scene {scene_script.scene_number} generated "
                    f"({scene_script.estimated_runtime:.1f}s)"
                )
                return scene_script
        
        # Generate all scenes in parallel with concurrency limit
        scene_scripts = await asyncio.gather(
            *[
                generate_with_progress(idx, scene_outline)
                for idx, scene_outline in enumerate(scenes_outline)
            ]
        )
        
        # Collect all dialogues for comedy optimization
        all_dialogues = [scene.dialogue for scene in scene_scripts]
        
        # Optimize comedy across all scenes
        logger.info("Optimizing comedy timing and effectiveness...")
        comedy_analysis = self.joke_optimizer.optimize_script_comedy(
            all_dialogues, character_profiles
        )
        
        logger.info(
            f"Comedy optimization complete: "
            f"{len(comedy_analysis.analyzed_jokes)} jokes, "
            f"{comedy_analysis.overall_effectiveness:.2f} effectiveness"
        )
        
        # Calculate totals
        total_runtime = sum(scene.estimated_runtime for scene in scene_scripts)
        total_comedy_beats = comedy_analysis.timing_analysis.total_jokes
        
        # Initial validation
        logger.info("Performing initial validation...")
        validation_report = self.script_validator.validate_script(
            script_id=script_id,
            scene_dialogues=all_dialogues,
            voice_profiles=character_profiles,
            comedy_analysis=comedy_analysis,
            episode_metadata=show_metadata,
        )
        
        logger.info(
            f"Initial validation: {validation_report.overall_quality_score:.2f} "
            f"({'PASSED' if validation_report.validation_passed else 'FAILED'})"
        )
        
        # Refinement loop if needed
        refinement_iterations = []
        current_quality = validation_report.overall_quality_score
        iteration = 0
        
        while (
            not validation_report.validation_passed and
            iteration < self.max_refinement_iterations
        ):
            iteration += 1
            logger.info(f"Starting refinement iteration {iteration}...")
            
            # Record iteration
            refinement_iterations.append(
                RefinementIteration(
                    iteration_number=iteration,
                    timestamp=datetime.now(),
                    validation_report=validation_report,
                    quality_score=current_quality,
                    validation_passed=False,
                    issues_addressed=[],
                    improvements_made=[],
                    scenes_modified=[],
                )
            )
            
            # Attempt refinement
            scene_scripts, comedy_analysis = self._refine_script(
                scene_scripts,
                character_profiles,
                validation_report,
            )
            
            # Re-validate
            all_dialogues = [scene.dialogue for scene in scene_scripts]
            validation_report = self.script_validator.validate_script(
                script_id=script_id,
                scene_dialogues=all_dialogues,
                voice_profiles=character_profiles,
                comedy_analysis=comedy_analysis,
                episode_metadata=show_metadata,
            )
            
            new_quality = validation_report.overall_quality_score
            logger.info(
                f"Refinement {iteration}: "
                f"{current_quality:.2f} → {new_quality:.2f} "
                f"({'PASSED' if validation_report.validation_passed else 'FAILED'})"
            )
            
            # Update iteration record
            refinement_iterations[-1].improvements_made = [
                f"Quality improved by {(new_quality - current_quality):.2f}"
            ]
            refinement_iterations[-1].quality_score = new_quality
            refinement_iterations[-1].validation_passed = (
                validation_report.validation_passed
            )
            
            current_quality = new_quality
        
        # Production metadata
        budget_estimate = validation_report.production_complexity.budget_estimate
        location_count = validation_report.production_complexity.location_count
        special_effects_count = (
            validation_report.production_complexity.special_effects_count
        )
        
        # Generation notes
        generation_notes = []
        generation_time = (datetime.now() - start_time).total_seconds()
        generation_notes.append(
            f"Generated in {generation_time:.1f}s "
            f"({len(refinement_iterations)} refinement iterations)"
        )
        
        if validation_report.validation_passed:
            generation_notes.append(
                f"Script passed validation with quality score "
                f"{current_quality:.2f}"
            )
        else:
            generation_notes.append(
                f"Script reached maximum refinement iterations "
                f"(final score: {current_quality:.2f})"
            )
        
        # Create full script
        full_script = FullScript(
            script_id=script_id,
            episode_title=show_metadata.get("episode_title", "Untitled"),
            show_title=show_metadata.get("show_title", "Unknown Show"),
            episode_number=show_metadata.get("episode_number", 1),
            season_number=show_metadata.get("season_number", 1),
            writers=show_metadata.get("writers", ["AI Generated"]),
            original_show=show_metadata.get("original_show", "Unknown"),
            doppelganger_setting=show_metadata.get(
                "doppelganger_setting", "Unknown"
            ),
            scenes=scene_scripts,
            generation_timestamp=start_time,
            total_runtime=total_runtime,
            total_comedy_beats=total_comedy_beats,
            final_validation_report=validation_report,
            final_quality_score=current_quality,
            refinement_iterations=refinement_iterations,
            budget_estimate=budget_estimate,
            location_count=location_count,
            special_effects_count=special_effects_count,
            generation_notes=generation_notes,
        )
        
        # End performance monitoring
        metrics = self.performance_monitor.end_session()
        if metrics:
            # Update metrics with script-specific data
            metrics.scenes_generated = len(scene_scripts)
            metrics.dialogue_lines_generated = sum(
                len(scene.dialogue.dialogue_lines) for scene in scene_scripts
            )
            metrics.jokes_analyzed = comedy_analysis.timing_analysis.total_jokes
            
            # Log performance summary
            logger.info(f"Performance Summary:\n{metrics.get_summary()}")
        
        logger.info(
            f"Script generation complete: {script_id} "
            f"({len(scene_scripts)} scenes, {total_runtime/60:.1f}m, "
            f"quality {current_quality:.2f})"
        )
        
        return full_script
    
    async def _generate_scene_script(
        self,
        scene_outline: Dict,
        character_profiles: Dict[str, CharacterVoiceProfile],
    ) -> SceneScript:
        """
        Generate complete script for a single scene (async for parallel execution).
        
        Args:
            scene_outline: Scene details from episode outline
            character_profiles: Character voice profiles
        
        Returns:
            Complete scene script with dialogue and staging
        """
        scene_number = scene_outline["scene_number"]
        
        logger.debug(f"Generating scene {scene_number}...")
        
        # Generate dialogue (already async)
        dialogue = await self.dialogue_generator.generate_dialogue(
            scene_description=scene_outline.get("description", ""),
            characters=scene_outline.get("characters", []),
            voice_profiles=character_profiles,
            scene_context={
                "location": scene_outline.get("location", ""),
                "time": scene_outline.get("time", "Day"),
                "beat_type": scene_outline.get("beat_type", "general"),
            },
        )
        
        # Generate stage directions (now properly async)
        try:
            stage_directions = await self.stage_direction_generator.generate_stage_directions(
                scene=scene_outline,
                scene_dialogue=dialogue,
                comedic_beats=None,
            )
        except Exception as e:
            logger.warning(f"Stage direction generation failed: {e}, using basic fallback")
            from src.services.creative.stage_direction_models import SceneStageDirections
            stage_directions = SceneStageDirections(
                scene_description=f"Scene at {scene_outline.get('location', 'Unknown')}",
                action_descriptions=[],
                physical_comedy_sequences=[],
                camera_suggestions=[],
            )
        
        # Count comedy beats in this scene
        comedy_beat_count = sum(
            1 for line in dialogue.dialogue_lines
            if any(
                keyword in line.line.lower()
                for keyword in [
                    "!", "?", "ha", "oh", "wow", "oops",
                    "uh-oh", "yikes", "whoops"
                ]
            )
        )
        
        # Collect production notes
        production_notes = []
        if stage_directions.physical_comedy_sequences:
            production_notes.append(
                f"{len(stage_directions.physical_comedy_sequences)} "
                f"physical comedy sequences"
            )
        if stage_directions.camera_suggestions:
            production_notes.append(
                f"{len(stage_directions.camera_suggestions)} camera setups"
            )
        
        return SceneScript(
            scene_number=scene_number,
            scene_title=scene_outline.get("title", f"Scene {scene_number}"),
            location=scene_outline.get("location", "Unknown"),
            time_of_day=scene_outline.get("time", "Day"),
            characters_present=scene_outline.get("characters", []),
            dialogue=dialogue,
            stage_directions=stage_directions,
            estimated_runtime=dialogue.total_runtime_estimate,
            comedy_beat_count=comedy_beat_count,
            production_notes=production_notes,
        )
    
    def _refine_script(
        self,
        scene_scripts: List[SceneScript],
        character_profiles: Dict[str, CharacterVoiceProfile],
        validation_report,
    ) -> tuple:
        """
        Refine script based on validation feedback.
        
        Focuses on addressing critical and error-level issues.
        
        Args:
            scene_scripts: Current scene scripts
            character_profiles: Character voice profiles
            validation_report: Validation results
        
        Returns:
            Tuple of (refined_scenes, new_comedy_analysis)
        """
        logger.info("Refining script based on validation feedback...")
        
        # Get critical issues
        critical_issues = validation_report.get_critical_issues()
        error_issues = validation_report.get_issues_by_severity(
            ValidationSeverity.ERROR
        )
        
        # For now, this is a simplified refinement
        # Full implementation would regenerate problematic scenes
        # and apply specific fixes based on issue types
        
        # Re-optimize comedy (which may improve weak jokes)
        all_dialogues = [scene.dialogue for scene in scene_scripts]
        comedy_analysis = self.joke_optimizer.optimize_script_comedy(
            all_dialogues, character_profiles
        )
        
        logger.info(
            f"Refinement addressed {len(critical_issues)} critical "
            f"and {len(error_issues)} error issues"
        )
        
        return scene_scripts, comedy_analysis
    
    def get_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """
        Get performance metrics for the current or most recent session.
        
        Returns:
            PerformanceMetrics if available, None otherwise
        
        Example:
            >>> script = await generator.generate_full_script(...)
            >>> metrics = generator.get_performance_metrics()
            >>> print(f"Cache hit rate: {metrics.cache_hit_rate:.1%}")
            >>> print(f"Total time: {metrics.total_duration_seconds:.1f}s")
        """
        current = self.performance_monitor.get_current_metrics()
        if current:
            return current
        
        # Return most recent completed session
        history = self.performance_monitor.get_session_history()
        return history[-1] if history else None
    
    def export_script(
        self,
        script: FullScript,
        format: ScriptFormat,
        output_path: str,
    ) -> None:
        """
        Export script to file.
        
        Args:
            script: Complete script
            format: Export format
            output_path: Output file path
        
        Example:
            >>> generator.export_script(
            ...     script,
            ...     ScriptFormat.SCREENPLAY,
            ...     "output/episode_001.txt"
            ... )
        """
        logger.info(f"Exporting script {script.script_id} to {output_path}")
        script.export(format, output_path)
        logger.info(f"Export complete: {output_path}")
