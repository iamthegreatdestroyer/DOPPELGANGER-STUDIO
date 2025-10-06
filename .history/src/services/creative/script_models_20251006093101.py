"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Data models for complete script generation and orchestration.

This module defines the data structures for the final output of the
script generation pipeline, including complete scripts with all metadata,
refinement history, and export capabilities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

from src.services.creative.character_voice_profiles import SceneDialogue
from src.services.creative.stage_directions import SceneStageDirections
from src.services.creative.joke_models import OptimizedScriptComedy
from src.services.creative.validation_models import ScriptValidationReport


class ScriptFormat(Enum):
    """Export format options for scripts."""
    SCREENPLAY = "screenplay"  # Traditional screenplay format
    PRODUCTION = "production"  # Production script with technical details
    JSON = "json"  # JSON format for API consumption
    MARKDOWN = "markdown"  # Markdown format for documentation


@dataclass
class SceneScript:
    """
    Complete script for a single scene.
    
    Combines dialogue, stage directions, and metadata into a cohesive unit.
    """
    scene_number: int
    scene_title: str
    location: str
    time_of_day: str
    characters_present: List[str]
    
    # Core content
    dialogue: SceneDialogue
    stage_directions: SceneStageDirections
    
    # Metadata
    estimated_runtime: float  # In seconds
    comedy_beat_count: int
    production_notes: List[str] = field(default_factory=list)
    
    def to_screenplay_format(self) -> str:
        """
        Export scene in traditional screenplay format.
        
        Returns:
            Formatted screenplay text
        """
        lines = []
        
        # Scene header
        lines.append(f"\n\nSCENE {self.scene_number} - {self.scene_title.upper()}\n")
        lines.append(f"INT./EXT. {self.location.upper()} - {self.time_of_day.upper()}\n")
        
        # Stage directions
        if self.stage_directions.scene_description:
            lines.append(f"\n{self.stage_directions.scene_description}\n")
        
        # Dialogue with interleaved action
        for dialogue_line in self.dialogue.dialogue_lines:
            # Add any stage directions that occur at this timing
            for direction in self.stage_directions.action_descriptions:
                if direction.timing_in_scene == dialogue_line.timing_in_scene:
                    lines.append(f"\n{direction.action_description}\n")
            
            # Character name (centered in screenplay)
            lines.append(f"\n{dialogue_line.character.upper()}\n")
            
            # Parenthetical if present
            if dialogue_line.emotion:
                lines.append(f"({dialogue_line.emotion})\n")
            
            # Dialogue
            lines.append(f"{dialogue_line.line}\n")
        
        # Final stage directions
        for direction in self.stage_directions.action_descriptions:
            if direction.timing_in_scene >= self.dialogue.total_runtime_estimate:
                lines.append(f"\n{direction.action_description}\n")
        
        return "".join(lines)
    
    def to_production_format(self) -> str:
        """
        Export scene in production script format with technical details.
        
        Returns:
            Formatted production script text
        """
        lines = []
        
        # Production header
        lines.append(f"\n{'='*60}\n")
        lines.append(f"SCENE {self.scene_number}: {self.scene_title}\n")
        lines.append(f"{'='*60}\n")
        lines.append(f"Location: {self.location}\n")
        lines.append(f"Time: {self.time_of_day}\n")
        lines.append(f"Characters: {', '.join(self.characters_present)}\n")
        lines.append(f"Estimated Runtime: {self.estimated_runtime:.1f}s ({self.estimated_runtime/60:.1f}m)\n")
        lines.append(f"Comedy Beats: {self.comedy_beat_count}\n")
        
        # Production notes
        if self.production_notes:
            lines.append(f"\nPRODUCTION NOTES:\n")
            for note in self.production_notes:
                lines.append(f"  • {note}\n")
        
        # Camera suggestions
        if self.stage_directions.camera_suggestions:
            lines.append(f"\nCAMERA SETUP:\n")
            for cam in self.stage_directions.camera_suggestions:
                lines.append(f"  [{cam.shot_type.upper()}] {cam.shot_description}\n")
                if cam.movement_type:
                    lines.append(f"    Movement: {cam.movement_type}\n")
        
        # Physical comedy sequences
        if self.stage_directions.physical_comedy_sequences:
            lines.append(f"\nPHYSICAL COMEDY:\n")
            for seq in self.stage_directions.physical_comedy_sequences:
                lines.append(f"  • {seq.comedy_action} (Setup: {seq.setup_time:.1f}s, Execute: {seq.execution_time:.1f}s)\n")
        
        lines.append(f"\n{'-'*60}\n")
        lines.append(self.to_screenplay_format())
        
        return "".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "scene_number": self.scene_number,
            "scene_title": self.scene_title,
            "location": self.location,
            "time_of_day": self.time_of_day,
            "characters_present": self.characters_present,
            "dialogue": self.dialogue.to_dict(),
            "stage_directions": self.stage_directions.to_dict(),
            "estimated_runtime": self.estimated_runtime,
            "comedy_beat_count": self.comedy_beat_count,
            "production_notes": self.production_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneScript":
        """Deserialize from dictionary."""
        return cls(
            scene_number=data["scene_number"],
            scene_title=data["scene_title"],
            location=data["location"],
            time_of_day=data["time_of_day"],
            characters_present=data["characters_present"],
            dialogue=SceneDialogue.from_dict(data["dialogue"]),
            stage_directions=SceneStageDirections.from_dict(data["stage_directions"]),
            estimated_runtime=data["estimated_runtime"],
            comedy_beat_count=data["comedy_beat_count"],
            production_notes=data.get("production_notes", []),
        )


@dataclass
class RefinementIteration:
    """
    Record of a single script refinement iteration.
    
    Tracks validation results and improvements made.
    """
    iteration_number: int
    timestamp: datetime
    
    # Validation results
    validation_report: ScriptValidationReport
    quality_score: float
    validation_passed: bool
    
    # Changes made
    issues_addressed: List[str]
    improvements_made: List[str]
    scenes_modified: List[int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "iteration_number": self.iteration_number,
            "timestamp": self.timestamp.isoformat(),
            "validation_report": self.validation_report.to_dict(),
            "quality_score": self.quality_score,
            "validation_passed": self.validation_passed,
            "issues_addressed": self.issues_addressed,
            "improvements_made": self.improvements_made,
            "scenes_modified": self.scenes_modified,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RefinementIteration":
        """Deserialize from dictionary."""
        return cls(
            iteration_number=data["iteration_number"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            validation_report=ScriptValidationReport.from_dict(data["validation_report"]),
            quality_score=data["quality_score"],
            validation_passed=data["validation_passed"],
            issues_addressed=data["issues_addressed"],
            improvements_made=data["improvements_made"],
            scenes_modified=data["scenes_modified"],
        )


@dataclass
class FullScript:
    """
    Complete episode script with all metadata and refinement history.
    
    This is the final output of the script generation pipeline.
    """
    script_id: str
    episode_title: str
    show_title: str
    
    # Episode metadata
    episode_number: int
    season_number: int
    writers: List[str]
    original_show: str  # Source show that inspired this
    doppelganger_setting: str  # New setting/context
    
    # Script content
    scenes: List[SceneScript]
    
    # Generation metadata
    generation_timestamp: datetime
    total_runtime: float  # Total episode runtime in seconds
    total_comedy_beats: int
    
    # Quality metrics
    final_validation_report: ScriptValidationReport
    final_quality_score: float
    refinement_iterations: List[RefinementIteration] = field(default_factory=list)
    
    # Production metadata
    budget_estimate: str  # low/medium/high
    location_count: int
    special_effects_count: int
    
    # Additional metadata
    generation_notes: List[str] = field(default_factory=list)
    
    def get_scene(self, scene_number: int) -> Optional[SceneScript]:
        """Get scene by number."""
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None
    
    def get_scenes_by_character(self, character_name: str) -> List[SceneScript]:
        """Get all scenes featuring a character."""
        return [
            scene for scene in self.scenes
            if character_name in scene.characters_present
        ]
    
    def get_scenes_by_location(self, location: str) -> List[SceneScript]:
        """Get all scenes at a location."""
        return [
            scene for scene in self.scenes
            if scene.location.lower() == location.lower()
        ]
    
    def to_screenplay_format(self) -> str:
        """
        Export complete script in screenplay format.
        
        Returns:
            Full screenplay text
        """
        lines = []
        
        # Title page
        lines.append(f"\n\n\n")
        lines.append(f"{self.episode_title.upper()}\n")
        lines.append(f"\n")
        lines.append(f"A {self.show_title} Episode\n")
        lines.append(f"\n")
        lines.append(f"Season {self.season_number}, Episode {self.episode_number}\n")
        lines.append(f"\n")
        lines.append(f"Written by: {', '.join(self.writers)}\n")
        lines.append(f"\n")
        lines.append(f"Based on: {self.original_show}\n")
        lines.append(f"Setting: {self.doppelganger_setting}\n")
        lines.append(f"\n")
        lines.append(f"Generated: {self.generation_timestamp.strftime('%B %d, %Y')}\n")
        lines.append(f"\n\n")
        lines.append(f"{'='*60}\n")
        
        # All scenes
        for scene in self.scenes:
            lines.append(scene.to_screenplay_format())
            lines.append(f"\n")
        
        # End credits
        lines.append(f"\n\n{'='*60}\n")
        lines.append(f"FADE OUT.\n")
        lines.append(f"\nTHE END\n")
        lines.append(f"\nTotal Runtime: {self.total_runtime/60:.1f} minutes\n")
        lines.append(f"Quality Score: {self.final_quality_score:.2f}\n")
        
        return "".join(lines)
    
    def to_production_script(self) -> str:
        """
        Export complete script in production format.
        
        Returns:
            Full production script with technical details
        """
        lines = []
        
        # Production cover page
        lines.append(f"\n{'#'*60}\n")
        lines.append(f"# PRODUCTION SCRIPT\n")
        lines.append(f"{'#'*60}\n\n")
        lines.append(f"Title: {self.episode_title}\n")
        lines.append(f"Show: {self.show_title}\n")
        lines.append(f"Episode: S{self.season_number:02d}E{self.episode_number:02d}\n")
        lines.append(f"Writers: {', '.join(self.writers)}\n")
        lines.append(f"\n")
        lines.append(f"PRODUCTION DETAILS:\n")
        lines.append(f"  Total Runtime: {self.total_runtime/60:.1f} minutes\n")
        lines.append(f"  Total Scenes: {len(self.scenes)}\n")
        lines.append(f"  Comedy Beats: {self.total_comedy_beats}\n")
        lines.append(f"  Budget Estimate: {self.budget_estimate.upper()}\n")
        lines.append(f"  Locations: {self.location_count}\n")
        lines.append(f"  Special Effects: {self.special_effects_count}\n")
        lines.append(f"  Quality Score: {self.final_quality_score:.2f}/1.00\n")
        lines.append(f"\n")
        
        # Refinement history
        if self.refinement_iterations:
            lines.append(f"REFINEMENT HISTORY:\n")
            for iteration in self.refinement_iterations:
                lines.append(
                    f"  Iteration {iteration.iteration_number}: "
                    f"Score {iteration.quality_score:.2f} → "
                    f"{'PASSED' if iteration.validation_passed else 'FAILED'}\n"
                )
            lines.append(f"\n")
        
        # Validation summary
        lines.append(f"VALIDATION SUMMARY:\n")
        lines.append(f"{self.final_validation_report.summary}\n")
        lines.append(f"\n")
        
        if self.final_validation_report.recommendations:
            lines.append(f"RECOMMENDATIONS:\n")
            for rec in self.final_validation_report.recommendations:
                lines.append(f"  • {rec}\n")
            lines.append(f"\n")
        
        lines.append(f"{'#'*60}\n\n")
        
        # All scenes in production format
        for scene in self.scenes:
            lines.append(scene.to_production_format())
            lines.append(f"\n")
        
        # Production notes
        if self.generation_notes:
            lines.append(f"\n{'#'*60}\n")
            lines.append(f"# PRODUCTION NOTES\n")
            lines.append(f"{'#'*60}\n\n")
            for note in self.generation_notes:
                lines.append(f"• {note}\n")
        
        return "".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "script_id": self.script_id,
            "episode_title": self.episode_title,
            "show_title": self.show_title,
            "episode_number": self.episode_number,
            "season_number": self.season_number,
            "writers": self.writers,
            "original_show": self.original_show,
            "doppelganger_setting": self.doppelganger_setting,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "generation_timestamp": self.generation_timestamp.isoformat(),
            "total_runtime": self.total_runtime,
            "total_comedy_beats": self.total_comedy_beats,
            "final_validation_report": self.final_validation_report.to_dict(),
            "final_quality_score": self.final_quality_score,
            "refinement_iterations": [
                iteration.to_dict() for iteration in self.refinement_iterations
            ],
            "budget_estimate": self.budget_estimate,
            "location_count": self.location_count,
            "special_effects_count": self.special_effects_count,
            "generation_notes": self.generation_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FullScript":
        """Deserialize from dictionary."""
        return cls(
            script_id=data["script_id"],
            episode_title=data["episode_title"],
            show_title=data["show_title"],
            episode_number=data["episode_number"],
            season_number=data["season_number"],
            writers=data["writers"],
            original_show=data["original_show"],
            doppelganger_setting=data["doppelganger_setting"],
            scenes=[SceneScript.from_dict(s) for s in data["scenes"]],
            generation_timestamp=datetime.fromisoformat(data["generation_timestamp"]),
            total_runtime=data["total_runtime"],
            total_comedy_beats=data["total_comedy_beats"],
            final_validation_report=ScriptValidationReport.from_dict(
                data["final_validation_report"]
            ),
            final_quality_score=data["final_quality_score"],
            refinement_iterations=[
                RefinementIteration.from_dict(i)
                for i in data.get("refinement_iterations", [])
            ],
            budget_estimate=data["budget_estimate"],
            location_count=data["location_count"],
            special_effects_count=data["special_effects_count"],
            generation_notes=data.get("generation_notes", []),
        )
    
    def export(self, format: ScriptFormat, output_path: str) -> None:
        """
        Export script to file in specified format.
        
        Args:
            format: Export format
            output_path: Output file path
        """
        import json
        
        if format == ScriptFormat.SCREENPLAY:
            content = self.to_screenplay_format()
        elif format == ScriptFormat.PRODUCTION:
            content = self.to_production_script()
        elif format == ScriptFormat.JSON:
            content = json.dumps(self.to_dict(), indent=2)
        elif format == ScriptFormat.MARKDOWN:
            content = self._to_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _to_markdown(self) -> str:
        """Export in Markdown format for documentation."""
        lines = []
        
        # Title
        lines.append(f"# {self.episode_title}\n\n")
        lines.append(f"**Show:** {self.show_title}  \n")
        lines.append(f"**Episode:** S{self.season_number:02d}E{self.episode_number:02d}  \n")
        lines.append(f"**Writers:** {', '.join(self.writers)}  \n")
        lines.append(f"**Based on:** {self.original_show}  \n")
        lines.append(f"**Setting:** {self.doppelganger_setting}  \n\n")
        
        # Metadata
        lines.append(f"## Episode Details\n\n")
        lines.append(f"- **Runtime:** {self.total_runtime/60:.1f} minutes\n")
        lines.append(f"- **Scenes:** {len(self.scenes)}\n")
        lines.append(f"- **Comedy Beats:** {self.total_comedy_beats}\n")
        lines.append(f"- **Quality Score:** {self.final_quality_score:.2f}/1.00\n")
        lines.append(f"- **Budget:** {self.budget_estimate.title()}\n\n")
        
        # Scenes
        lines.append(f"## Scenes\n\n")
        for scene in self.scenes:
            lines.append(f"### Scene {scene.scene_number}: {scene.scene_title}\n\n")
            lines.append(f"**Location:** {scene.location}  \n")
            lines.append(f"**Characters:** {', '.join(scene.characters_present)}  \n")
            lines.append(f"**Runtime:** {scene.estimated_runtime:.1f}s  \n\n")
            lines.append(f"```\n{scene.to_screenplay_format()}\n```\n\n")
        
        return "".join(lines)
