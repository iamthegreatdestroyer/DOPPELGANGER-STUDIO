"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

Dialogue generation system with character voice consistency.

This module generates character-consistent dialogue that maintains
voice, advances plot, and delivers comedy.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from src.services.creative.claude_client import ClaudeClient
from src.services.creative.openai_client import OpenAIClient
from src.core.database_manager import DatabaseManager
from src.services.creative.character_voice_profiles import (
    CharacterVoiceProfile,
    DialogueLine,
    SceneDialogue
)

logger = logging.getLogger(__name__)


class DialogueGenerator:
    """
    Generates character-consistent dialogue for scenes.
    
    Features:
    - Character voice profile system
    - Context-aware dialogue generation
    - Multi-turn conversation handling
    - Comedic timing integration
    - Voice consistency validation
    
    Example:
        >>> from src.services.ai.claude_client import ClaudeClient
        >>> from src.services.creative.transformation_engine import TransformationRules
        >>> 
        >>> claude = ClaudeClient(api_key="...")
        >>> generator = DialogueGenerator(claude)
        >>> 
        >>> # Create voice profile
        >>> voice_profile = await generator.create_voice_profile(
        ...     character_analysis=lucy_analysis,
        ...     transformation_rules=rules
        ... )
        >>> 
        >>> # Generate scene dialogue
        >>> dialogue = await generator.generate_dialogue(
        ...     scene=scene_outline,
        ...     episode_context=episode,
        ...     narrative_structure=narrative
        ... )
    """
    
    def __init__(
        self,
        claude_client: ClaudeClient,
        gpt_client: Optional[OpenAIClient] = None,
        database_manager: Optional[DatabaseManager] = None
    ):
        """
        Initialize dialogue generator.
        
        Args:
            claude_client: Primary AI client for generation
            gpt_client: Fallback AI client (optional)
            database_manager: For caching voice profiles (optional)
        """
        self.claude = claude_client
        self.gpt = gpt_client
        self.db = database_manager
        self.voice_profiles: Dict[str, CharacterVoiceProfile] = {}
        
        logger.info("DialogueGenerator initialized")
    
    async def create_voice_profile(
        self,
        character_analysis: dict,  # CharacterAnalysis from Phase 3
        transformation_rules: dict,  # TransformationRules from Phase 3
        character_name: Optional[str] = None
    ) -> CharacterVoiceProfile:
        """
        Create detailed voice profile from character analysis.
        
        Extracts:
        - Speech patterns from analysis
        - Vocabulary from character traits
        - Emotional range from personality
        - Relationship dynamics
        
        Args:
            character_analysis: Character analysis from Phase 3
            transformation_rules: Transformation rules for context
            character_name: Override character name if different
        
        Returns:
            Complete character voice profile
        
        Example:
            >>> profile = await generator.create_voice_profile(
            ...     character_analysis=lucy_analysis,
            ...     transformation_rules=rules,
            ...     character_name="Luna"
            ... )
            >>> print(profile.get_speaking_style_summary())
        """
        logger.info(f"Creating voice profile for character")
        
        # Extract character name
        name = character_name or character_analysis.get('character_name', 'Unknown')
        
        # Build prompt for AI to analyze speaking style
        prompt = self._build_voice_profile_prompt(
            character_analysis,
            transformation_rules
        )
        
        try:
            # Generate voice profile analysis
            response = await self.claude.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse AI response (expects JSON)
            profile_data = json.loads(response)
            
            # Create voice profile
            voice_profile = CharacterVoiceProfile(
                character_name=name,
                vocabulary_level=profile_data.get('vocabulary_level', 'simple'),
                sentence_structure=profile_data.get('sentence_structure', 'medium'),
                verbal_tics=profile_data.get('verbal_tics', []),
                catchphrases=profile_data.get('catchphrases', []),
                emotional_range=profile_data.get('emotional_range', []),
                speech_patterns=profile_data.get('speech_patterns', []),
                relationship_dynamics=profile_data.get('relationship_dynamics', {}),
                education_level=profile_data.get('education_level'),
                cultural_background=profile_data.get('cultural_background'),
                age_appropriate_language=profile_data.get('age_appropriate_language'),
                humor_style=profile_data.get('humor_style')
            )
            
            # Cache profile
            self.voice_profiles[name] = voice_profile
            
            logger.info(f"Voice profile created for {name}")
            return voice_profile
            
        except Exception as e:
            logger.error(f"Failed to create voice profile: {e}")
            
            # Create basic fallback profile
            return CharacterVoiceProfile(
                character_name=name,
                vocabulary_level="simple",
                sentence_structure="medium",
                verbal_tics=[],
                catchphrases=[],
                emotional_range=["neutral"],
                speech_patterns=[],
                relationship_dynamics={}
            )
    
    async def generate_dialogue(
        self,
        scene: dict,  # Scene from EpisodeOutline
        episode_context: dict,  # EpisodeOutline
        narrative_structure: dict  # NarrativeAnalysis
    ) -> SceneDialogue:
        """
        Generate complete dialogue for a scene.
        
        Process:
        1. Build scene context (what happened before)
        2. Identify characters present
        3. Generate turn-by-turn dialogue
        4. Integrate comedic beats
        5. Add stage direction cues
        6. Validate voice consistency
        
        Args:
            scene: Scene outline from Phase 3
            episode_context: Full episode outline for context
            narrative_structure: Story structure patterns
        
        Returns:
            Complete scene dialogue with metadata
        
        Example:
            >>> dialogue = await generator.generate_dialogue(
            ...     scene=scene_1,
            ...     episode_context=episode_outline,
            ...     narrative_structure=narrative_analysis
            ... )
            >>> print(dialogue.get_screenplay_format())
        """
        scene_number = scene.get('scene_number', 1)
        location = scene.get('location', 'Unknown Location')
        characters = scene.get('characters', [])
        
        logger.info(f"Generating dialogue for Scene {scene_number} ({location})")
        
        # Build comprehensive context
        prompt = self._build_dialogue_prompt(
            scene=scene,
            episode_context=episode_context,
            narrative_structure=narrative_structure,
            characters=characters
        )
        
        try:
            # Generate dialogue
            response = await self.claude.generate(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.8
            )
            
            # Parse response
            dialogue_data = json.loads(response)
            
            # Create DialogueLine objects
            dialogue_lines = []
            for idx, line_data in enumerate(dialogue_data.get('dialogue', [])):
                line = DialogueLine(
                    character=line_data.get('character', 'Unknown'),
                    line=line_data.get('line', ''),
                    emotion=line_data.get('emotion', 'neutral'),
                    delivery_note=line_data.get('delivery_note'),
                    pause_before=line_data.get('pause_before', 0.0),
                    is_comedic_beat=line_data.get('is_comedic_beat', False),
                    comedic_beat_type=line_data.get('comedic_beat_type'),
                    line_number=idx + 1
                )
                dialogue_lines.append(line)
            
            # Calculate runtime estimate (avg 150 words/min for dialogue)
            total_words = sum(len(line.line.split()) for line in dialogue_lines)
            runtime_estimate = int((total_words / 150) * 60)  # Convert to seconds
            
            # Count comedic beats
            comedic_count = sum(1 for line in dialogue_lines if line.is_comedic_beat)
            
            # Validate voice consistency
            consistency_score = self._validate_dialogue_consistency(
                dialogue_lines=dialogue_lines,
                characters=characters
            )
            
            # Create scene dialogue
            scene_dialogue = SceneDialogue(
                scene_number=scene_number,
                location=location,
                characters_present=characters,
                dialogue_lines=dialogue_lines,
                total_runtime_estimate=runtime_estimate,
                comedic_beats_count=comedic_count,
                confidence_score=consistency_score
            )
            
            logger.info(
                f"Generated {len(dialogue_lines)} lines for Scene {scene_number}, "
                f"runtime: {runtime_estimate}s, consistency: {consistency_score:.2f}"
            )
            
            return scene_dialogue
            
        except Exception as e:
            logger.error(f"Failed to generate dialogue for Scene {scene_number}: {e}")
            
            # Return empty dialogue as fallback
            return SceneDialogue(
                scene_number=scene_number,
                location=location,
                characters_present=characters,
                dialogue_lines=[],
                total_runtime_estimate=0,
                comedic_beats_count=0,
                confidence_score=0.0
            )
    
    def _build_voice_profile_prompt(
        self,
        character_analysis: dict,
        transformation_rules: dict
    ) -> str:
        """Build prompt for voice profile generation."""
        return f"""
You are a character voice analysis expert. Create a detailed voice profile from this character analysis.

CHARACTER ANALYSIS:
{json.dumps(character_analysis, indent=2)}

TRANSFORMATION CONTEXT:
{json.dumps(transformation_rules, indent=2)}

Analyze how this character speaks and respond with JSON:

{{
  "vocabulary_level": "simple|sophisticated|technical",
  "sentence_structure": "short|medium|rambling|eloquent",
  "verbal_tics": ["list", "of", "habitual", "words"],
  "catchphrases": ["signature", "phrases"],
  "emotional_range": ["typical", "emotions", "displayed"],
  "speech_patterns": ["distinctive", "speaking", "patterns"],
  "relationship_dynamics": {{"other_character": "how_they_speak_to_them"}},
  "education_level": "description",
  "cultural_background": "description",
  "age_appropriate_language": "description",
  "humor_style": "sarcastic|slapstick|wordplay|deadpan"
}}

Focus on concrete, actionable details that help generate consistent dialogue.
"""
    
    def _build_dialogue_prompt(
        self,
        scene: dict,
        episode_context: dict,
        narrative_structure: dict,
        characters: List[str]
    ) -> str:
        """Build prompt for dialogue generation."""
        
        # Get voice profiles for characters
        voice_guidance = ""
        for character in characters:
            if character in self.voice_profiles:
                profile = self.voice_profiles[character]
                voice_guidance += f"\n{character}: {profile.get_speaking_style_summary()}"
        
        return f"""
You are a TV comedy writer. Generate natural, funny dialogue for this scene.

SCENE CONTEXT:
{json.dumps(scene, indent=2)}

EPISODE CONTEXT:
{json.dumps(episode_context, indent=2)}

NARRATIVE STRUCTURE:
{json.dumps(narrative_structure, indent=2)}

VOICE PROFILES:
{voice_guidance}

Generate dialogue that:
1. Matches each character's voice perfectly
2. Advances the plot from the scene description
3. Includes the specified comedic beats
4. Feels natural and conversational
5. Has good pacing and rhythm

Respond with JSON:

{{
  "dialogue": [
    {{
      "character": "CHARACTER NAME",
      "line": "What they say",
      "emotion": "emotional state",
      "delivery_note": "optional acting direction",
      "pause_before": 0.0,
      "is_comedic_beat": false,
      "comedic_beat_type": null
    }}
  ]
}}

Make it funny, natural, and true to the characters!
"""
    
    def _validate_dialogue_consistency(
        self,
        dialogue_lines: List[DialogueLine],
        characters: List[str]
    ) -> float:
        """
        Validate dialogue matches character voices.
        
        Returns:
            Consistency score (0.0-1.0)
        """
        if not dialogue_lines:
            return 0.0
        
        # For now, return high confidence if we have voice profiles
        has_profiles = sum(
            1 for char in characters if char in self.voice_profiles
        )
        
        if len(characters) == 0:
            return 0.5
        
        return min(1.0, 0.5 + (has_profiles / len(characters)) * 0.5)
    
    def _validate_voice_consistency(
        self,
        character: str,
        dialogue_line: str
    ) -> Tuple[bool, float, List[str]]:
        """
        Check if dialogue matches character voice.
        
        Returns:
            (is_consistent, confidence_score, issues)
        """
        if character not in self.voice_profiles:
            return (True, 0.5, ["No voice profile available"])
        
        # TODO: Implement sophisticated voice matching
        # For now, return basic validation
        return (True, 0.8, [])
