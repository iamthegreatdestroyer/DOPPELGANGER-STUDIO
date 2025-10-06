"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Stage direction generation system for visual choreography.

This module generates stage directions, physical comedy sequences,
and camera suggestions to bring scenes to life visually.
"""

import logging
from typing import List, Optional
import json

from src.services.ai.claude_client import ClaudeClient
from src.services.ai.openai_client import OpenAIClient
from src.services.research.database_manager import DatabaseManager
from src.services.creative.stage_direction_models import (
    StageDirection,
    PhysicalComedySequence,
    CameraSuggestion,
    SceneStageDirections
)
from src.services.creative.character_voice_profiles import SceneDialogue

logger = logging.getLogger(__name__)


class StageDirectionGenerator:
    """
    Generates stage directions and visual choreography.
    
    Features:
    - Opening scene establishment
    - Character action sequences
    - Physical comedy choreography
    - Camera/blocking suggestions
    - Visual gag timing
    
    Example:
        >>> from src.services.ai.claude_client import ClaudeClient
        >>> 
        >>> claude = ClaudeClient(api_key="...")
        >>> generator = StageDirectionGenerator(claude)
        >>> 
        >>> # Generate stage directions
        >>> directions = await generator.generate_stage_directions(
        ...     scene=scene_outline,
        ...     scene_dialogue=dialogue,
        ...     comedic_beats=["Ring light falls", "Luna trips"]
        ... )
    """
    
    def __init__(
        self,
        claude_client: ClaudeClient,
        gpt_client: Optional[OpenAIClient] = None,
        database_manager: Optional[DatabaseManager] = None
    ):
        """
        Initialize stage direction generator.
        
        Args:
            claude_client: Primary AI client
            gpt_client: Fallback AI client (optional)
            database_manager: For caching (optional)
        """
        self.claude = claude_client
        self.gpt = gpt_client
        self.db = database_manager
        
        logger.info("StageDirectionGenerator initialized")
    
    async def generate_stage_directions(
        self,
        scene: dict,
        scene_dialogue: SceneDialogue,
        comedic_beats: Optional[List[str]] = None
    ) -> SceneStageDirections:
        """
        Create complete stage directions for scene.
        
        Includes:
        - Opening visual description
        - Action beats between dialogue
        - Physical comedy sequences
        - Character reactions
        - Closing visual
        - Camera suggestions
        
        Args:
            scene: Scene outline from Phase 3
            scene_dialogue: Generated dialogue for scene
            comedic_beats: Physical comedy moments to choreograph
        
        Returns:
            Complete stage directions with camera work
        
        Example:
            >>> directions = await generator.generate_stage_directions(
            ...     scene=scene_1,
            ...     scene_dialogue=dialogue,
            ...     comedic_beats=["Luna trips over cables"]
            ... )
        """
        scene_number = scene.get('scene_number', 1)
        location = scene.get('location', 'Unknown')
        characters = scene.get('characters', [])
        
        logger.info(f"Generating stage directions for Scene {scene_number}")
        
        # Build prompt for AI
        prompt = self._build_stage_direction_prompt(
            scene=scene,
            scene_dialogue=scene_dialogue,
            comedic_beats=comedic_beats or []
        )
        
        try:
            # Generate directions
            response = await self.claude.generate(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.8
            )
            
            # Parse response
            data = json.loads(response)
            
            # Create action beats
            action_beats = []
            for beat_data in data.get('action_beats', []):
                camera = None
                if beat_data.get('camera_suggestion'):
                    cam_data = beat_data['camera_suggestion']
                    camera = CameraSuggestion(
                        shot_type=cam_data.get('shot_type', 'MEDIUM'),
                        focus=cam_data.get('focus', ''),
                        reasoning=cam_data.get('reasoning', ''),
                        movement=cam_data.get('movement'),
                        timing=cam_data.get('timing')
                    )
                
                beat = StageDirection(
                    timing=beat_data.get('timing', 'CONTINUOUS'),
                    description=beat_data.get('description', ''),
                    duration_estimate=beat_data.get('duration_estimate', 1.0),
                    involves_characters=beat_data.get('involves_characters', []),
                    visual_gag=beat_data.get('visual_gag', False),
                    camera_suggestion=camera
                )
                action_beats.append(beat)
            
            # Create physical comedy sequences
            comedy_sequences = []
            for seq_data in data.get('physical_comedy_sequences', []):
                # Parse setup actions
                setup_actions = [
                    StageDirection(
                        timing=a.get('timing', 'CONTINUOUS'),
                        description=a.get('description', ''),
                        duration_estimate=a.get('duration_estimate', 1.0),
                        involves_characters=a.get('involves_characters', []),
                        visual_gag=True
                    )
                    for a in seq_data.get('setup_actions', [])
                ]
                
                # Parse escalation actions
                escalation_actions = [
                    StageDirection(
                        timing=a.get('timing', 'CONTINUOUS'),
                        description=a.get('description', ''),
                        duration_estimate=a.get('duration_estimate', 1.0),
                        involves_characters=a.get('involves_characters', []),
                        visual_gag=True
                    )
                    for a in seq_data.get('escalation_actions', [])
                ]
                
                # Parse climax
                climax_data = seq_data.get('climax_action', {})
                climax = StageDirection(
                    timing=climax_data.get('timing', 'CONTINUOUS'),
                    description=climax_data.get('description', ''),
                    duration_estimate=climax_data.get('duration_estimate', 2.0),
                    involves_characters=climax_data.get('involves_characters', []),
                    visual_gag=True
                )
                
                # Parse resolution
                resolution_data = seq_data.get('resolution_action', {})
                resolution = StageDirection(
                    timing=resolution_data.get('timing', 'CONTINUOUS'),
                    description=resolution_data.get('description', ''),
                    duration_estimate=resolution_data.get('duration_estimate', 1.0),
                    involves_characters=resolution_data.get('involves_characters', []),
                    visual_gag=True
                )
                
                sequence = PhysicalComedySequence(
                    beat_name=seq_data.get('beat_name', 'Physical Comedy'),
                    setup_actions=setup_actions,
                    escalation_actions=escalation_actions,
                    climax_action=climax,
                    resolution_action=resolution,
                    total_duration=seq_data.get('total_duration', 10.0)
                )
                comedy_sequences.append(sequence)
            
            # Create camera suggestions
            camera_suggestions = []
            for cam_data in data.get('camera_suggestions', []):
                camera = CameraSuggestion(
                    shot_type=cam_data.get('shot_type', 'MEDIUM'),
                    focus=cam_data.get('focus', ''),
                    reasoning=cam_data.get('reasoning', ''),
                    movement=cam_data.get('movement'),
                    timing=cam_data.get('timing')
                )
                camera_suggestions.append(camera)
            
            # Calculate total runtime
            total_runtime = sum(b.duration_estimate for b in action_beats)
            total_runtime += sum(
                s.total_duration for s in comedy_sequences
            )
            
            # Create scene stage directions
            stage_directions = SceneStageDirections(
                scene_number=scene_number,
                opening_description=data.get(
                    'opening_description',
                    f'{location} - Characters present'
                ),
                action_beats=action_beats,
                physical_comedy_sequences=comedy_sequences,
                closing_description=data.get(
                    'closing_description',
                    'Scene continues'
                ),
                camera_suggestions=camera_suggestions,
                total_visual_runtime=total_runtime
            )
            
            logger.info(
                f"Generated stage directions for Scene {scene_number}: "
                f"{len(action_beats)} beats, {len(comedy_sequences)} sequences, "
                f"{total_runtime:.1f}s runtime"
            )
            
            return stage_directions
            
        except Exception as e:
            logger.error(f"Failed to generate stage directions: {e}")
            
            # Return minimal fallback
            return SceneStageDirections(
                scene_number=scene_number,
                opening_description=f'{location}',
                action_beats=[],
                physical_comedy_sequences=[],
                closing_description='',
                camera_suggestions=[],
                total_visual_runtime=0.0
            )
    
    async def _generate_physical_comedy_sequence(
        self,
        comedic_beat: str,
        characters: List[str],
        location: str
    ) -> PhysicalComedySequence:
        """
        Choreograph physical comedy moment.
        
        Example: "ring light falls" →
        - Setup: Luna adjusts ring light precariously
        - Escalation: It wobbles, she tries to steady it
        - Climax: Light crashes down narrowly missing her
        - Resolution: She looks at camera sheepishly
        
        Args:
            comedic_beat: Description of physical gag
            characters: Characters involved
            location: Where this happens
        
        Returns:
            Complete choreographed sequence
        """
        prompt = f"""
You are a physical comedy choreographer. Create a detailed sequence for this gag:

COMEDIC BEAT: {comedic_beat}
CHARACTERS: {', '.join(characters)}
LOCATION: {location}

Break down into:
1. SETUP: How the situation is established (2-3 actions)
2. ESCALATION: How it builds/gets worse (2-3 actions)
3. CLIMAX: The peak moment (1 action)
4. RESOLUTION: How it resolves (1 action)

Respond with JSON following this structure:
{{
  "beat_name": "Short name for this gag",
  "setup_actions": [
    {{
      "description": "What happens",
      "duration_estimate": 2.0,
      "involves_characters": ["Character"]
    }}
  ],
  "escalation_actions": [...],
  "climax_action": {{}},
  "resolution_action": {{}},
  "total_duration": 15.0
}}

Make it visual, funny, and clear!
"""
        
        try:
            response = await self.claude.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.8
            )
            
            data = json.loads(response)
            
            # Create sequence (simplified version)
            # TODO: Full implementation
            return PhysicalComedySequence(
                beat_name=data.get('beat_name', comedic_beat),
                setup_actions=[],
                escalation_actions=[],
                climax_action=StageDirection(
                    timing='CONTINUOUS',
                    description=comedic_beat,
                    duration_estimate=3.0,
                    involves_characters=characters,
                    visual_gag=True
                ),
                resolution_action=StageDirection(
                    timing='AFTER',
                    description='Characters react',
                    duration_estimate=1.0,
                    involves_characters=characters,
                    visual_gag=False
                ),
                total_duration=10.0
            )
            
        except Exception as e:
            logger.error(f"Failed to generate physical comedy: {e}")
            # Return basic sequence
            return PhysicalComedySequence(
                beat_name=comedic_beat,
                setup_actions=[],
                escalation_actions=[],
                climax_action=StageDirection(
                    timing='CONTINUOUS',
                    description=comedic_beat,
                    duration_estimate=2.0,
                    involves_characters=characters,
                    visual_gag=True
                ),
                resolution_action=StageDirection(
                    timing='AFTER',
                    description='Characters recover',
                    duration_estimate=1.0,
                    involves_characters=characters,
                    visual_gag=False
                ),
                total_duration=5.0
            )
    
    def _suggest_camera_work(
        self,
        action_type: str,
        emotional_beat: str
    ) -> CameraSuggestion:
        """Suggest camera movement/framing for moment."""
        # Simple rule-based suggestions
        # TODO: Make AI-powered for better suggestions
        
        if action_type == 'physical_comedy':
            return CameraSuggestion(
                shot_type='WIDE',
                focus='full action',
                reasoning='Show entire physical gag',
                movement=None,
                timing='During action'
            )
        elif emotional_beat in ['punchline', 'reaction']:
            return CameraSuggestion(
                shot_type='CLOSE-UP',
                focus='character face',
                reasoning='Capture reaction',
                movement=None,
                timing='On beat'
            )
        else:
            return CameraSuggestion(
                shot_type='MEDIUM',
                focus='characters',
                reasoning='Standard coverage',
                movement=None,
                timing='Continuous'
            )
    
    def _build_stage_direction_prompt(
        self,
        scene: dict,
        scene_dialogue: SceneDialogue,
        comedic_beats: List[str]
    ) -> str:
        """Build prompt for stage direction generation."""
        return f"""
You are a TV director creating stage directions. Generate visual choreography for this scene.

SCENE INFO:
{json.dumps(scene, indent=2)}

DIALOGUE:
{scene_dialogue.get_dialogue_text()}

PHYSICAL COMEDY BEATS:
{json.dumps(comedic_beats, indent=2)}

Create:
1. Opening visual description (set the scene)
2. Action beats between dialogue lines
3. Physical comedy sequences (if applicable)
4. Camera suggestions for key moments
5. Closing visual

Respond with JSON:
{{
  "opening_description": "Visual description of opening",
  "action_beats": [
    {{
      "timing": "BEFORE LINE|DURING LINE|AFTER LINE",
      "description": "What happens",
      "duration_estimate": 1.5,
      "involves_characters": ["Character"],
      "visual_gag": false,
      "camera_suggestion": {{
        "shot_type": "WIDE|MEDIUM|CLOSE-UP",
        "focus": "what to focus on",
        "reasoning": "why this shot",
        "movement": null
      }}
    }}
  ],
  "physical_comedy_sequences": [
    {{
      "beat_name": "Gag name",
      "setup_actions": [...],
      "escalation_actions": [...],
      "climax_action": {{}},
      "resolution_action": {{}},
      "total_duration": 10.0
    }}
  ],
  "camera_suggestions": [...],
  "closing_description": "How scene ends visually"
}}

Make it visual, dynamic, and production-ready!
"""
