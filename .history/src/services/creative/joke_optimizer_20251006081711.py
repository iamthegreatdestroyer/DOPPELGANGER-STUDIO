"""
Copyright (c) 2025 DOPPELGANGER STUDIO. All Rights Reserved.

JokeOptimizer component for comedy refinement and analysis.

This module provides AI-powered joke analysis, structure validation,
alternative punchline generation, and callback detection to optimize
the comedic effectiveness of generated scripts.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from src.services.creative.joke_models import (
    JokeStructure,
    JokeType,
    JokeTiming,
    AlternativePunchline,
    CallbackOpportunity,
    ComedyTimingAnalysis,
    OptimizedScriptComedy,
)
from src.services.creative.character_voice_profiles import (
    SceneDialogue,
    CharacterVoiceProfile,
)
from src.services.creative.claude_client import ClaudeClient
from src.services.creative.openai_client import OpenAIClient

if TYPE_CHECKING:
    from src.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class JokeOptimizer:
    """
    AI-powered comedy optimization system.
    
    Analyzes jokes in a script for structure, effectiveness, and timing.
    Generates alternative punchlines and identifies callback opportunities.
    Provides comprehensive comedy analysis for script refinement.
    
    Example:
        >>> optimizer = JokeOptimizer(claude_client, gpt_client)
        >>> scene_dialogues = [scene1_dialogue, scene2_dialogue]
        >>> comedic_beats = episode_structure.comedic_beats
        >>> result = await optimizer.optimize_script_comedy(
        ...     scene_dialogues, comedic_beats, voice_profiles
        ... )
        >>> print(f"Overall effectiveness: {result.overall_effectiveness}")
        >>> weak_jokes = result.get_weak_jokes(threshold=0.6)
    """
    
    def __init__(
        self,
        claude_client: ClaudeClient,
        openai_client: OpenAIClient,
        database_manager: Optional["DatabaseManager"] = None,
    ):
        """
        Initialize JokeOptimizer.
        
        Args:
            claude_client: Primary AI client for analysis
            openai_client: Fallback AI client
            database_manager: Optional caching for joke patterns
        """
        self.claude_client = claude_client
        self.openai_client = openai_client
        self.db_manager = database_manager
        
        logger.info("JokeOptimizer initialized")
    
    async def optimize_script_comedy(
        self,
        scene_dialogues: List[SceneDialogue],
        comedic_beats: List[Dict],
        voice_profiles: Dict[str, CharacterVoiceProfile],
        script_id: str = "unknown",
    ) -> OptimizedScriptComedy:
        """
        Analyze and optimize all comedy in a script.
        
        Args:
            scene_dialogues: Dialogue for all scenes
            comedic_beats: Comedic beat metadata from episode structure
            voice_profiles: Character voice profiles for consistency checking
            script_id: Identifier for this script
        
        Returns:
            Complete comedy analysis with optimization suggestions
        
        Example:
            >>> result = await optimizer.optimize_script_comedy(
            ...     dialogues, beats, profiles, "episode_001"           ... )
            >>> print(result.optimization_summary)
        """
        logger.info(f"Starting comedy optimization for script: {script_id}")
        
        try:
            # Analyze joke structures
            analyzed_jokes = await self._analyze_all_jokes(
                scene_dialogues, comedic_beats
            )
            
            logger.info(f"Analyzed {len(analyzed_jokes)} jokes")
            
            # Generate alternatives for weak jokes
            weak_jokes = [j for j in analyzed_jokes if j.effectiveness_score < 0.7]
            alternative_punchlines = await self._generate_alternatives_for_jokes(
                weak_jokes, voice_profiles
            )
            
            logger.info(f"Generated {len(alternative_punchlines)} alternatives")
            
            # Detect callback opportunities
            callback_opportunities = self._detect_callback_opportunities(
                analyzed_jokes, scene_dialogues
            )
            
            logger.info(f"Found {len(callback_opportunities)} callback opportunities")
            
            # Analyze timing and distribution
            timing_analysis = self._analyze_comedy_timing(
                analyzed_jokes, scene_dialogues
            )
            
            # Calculate overall effectiveness
            overall_effectiveness = self._calculate_overall_effectiveness(
                analyzed_jokes
            )
            
            # Generate optimization summary
            optimization_summary = self._generate_optimization_summary(
                analyzed_jokes,
                alternative_punchlines,
                callback_opportunities,
                timing_analysis,
            )
            
            result = OptimizedScriptComedy(
                script_id=script_id,
                analyzed_jokes=analyzed_jokes,
                alternative_punchlines=alternative_punchlines,
                callback_opportunities=callback_opportunities,
                timing_analysis=timing_analysis,
                overall_effectiveness=overall_effectiveness,
                optimization_summary=optimization_summary,
                confidence_score=0.85,
            )
            
            logger.info(
                f"Comedy optimization complete. Overall effectiveness: "
                f"{overall_effectiveness:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Comedy optimization failed: {e}", exc_info=True)
            # Return minimal result on failure
            return OptimizedScriptComedy(
                script_id=script_id,
                analyzed_jokes=[],
                alternative_punchlines=[],
                callback_opportunities=[],
                timing_analysis=ComedyTimingAnalysis(
                    total_jokes=0,
                    average_spacing=0.0,
                    timing_category=JokeTiming.WELL_SPACED,
                ),
                overall_effectiveness=0.0,
                optimization_summary="Analysis failed",
                confidence_score=0.0,
            )
    
    async def _analyze_all_jokes(
        self,
        scene_dialogues: List[SceneDialogue],
        comedic_beats: List[Dict],
    ) -> List[JokeStructure]:
        """
        Analyze all jokes in the script.
        
        Args:
            scene_dialogues: All scene dialogues
            comedic_beats: Comedic beat metadata
        
        Returns:
            List of analyzed joke structures
        """
        analyzed_jokes = []
        
        for idx, beat in enumerate(comedic_beats):
            try:
                joke = await self._analyze_joke_structure(
                    beat, scene_dialogues, idx
                )
                analyzed_jokes.append(joke)
            except Exception as e:
                logger.warning(f"Failed to analyze joke {idx}: {e}")
                continue
        
        return analyzed_jokes
    
    async def _analyze_joke_structure(
        self,
        comedic_beat: Dict,
        scene_dialogues: List[SceneDialogue],
        joke_index: int,
    ) -> JokeStructure:
        """
        Analyze the structure of a single joke.
        
        Validates setup/payoff, identifies joke type, scores effectiveness.
        
        Args:
            comedic_beat: Metadata about the comedic moment
            scene_dialogues: Context from scene dialogues
            joke_index: Index of this joke in the script
        
        Returns:
            Analyzed joke structure with effectiveness score
        """
        prompt = self._build_joke_analysis_prompt(comedic_beat, scene_dialogues)
        
        try:
            # Try Claude first
            response = await self.claude_client.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for analytical task
            )
            analysis = json.loads(response)
            
        except Exception as e:
            logger.warning(f"Claude analysis failed: {e}, trying GPT-4")
            try:
                response = await self.openai_client.generate(
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.3,
                )
                analysis = json.loads(response)
            except Exception as e2:
                logger.error(f"GPT-4 analysis also failed: {e2}")
                # Fallback to basic structure
                return self._create_fallback_joke_structure(
                    comedic_beat, joke_index
                )
        
        # Build JokeStructure from AI response
        joke_id = f"joke_{joke_index:03d}"
        
        return JokeStructure(
            joke_id=joke_id,
            joke_type=JokeType(analysis.get("joke_type", "situational")),
            setup=analysis.get("setup", comedic_beat.get("setup", "")),
            misdirection=analysis.get("misdirection"),
            punchline=analysis.get("punchline", comedic_beat.get("payoff", "")),
            timing_position=comedic_beat.get("timing", 0.0),
            characters_involved=comedic_beat.get("characters", []),
            effectiveness_score=analysis.get("effectiveness_score", 0.5),
            improvement_suggestions=analysis.get("improvement_suggestions", []),
            callback_potential=analysis.get("callback_potential", False),
        )
    
    def _build_joke_analysis_prompt(
        self,
        comedic_beat: Dict,
        scene_dialogues: List[SceneDialogue],
    ) -> str:
        """Build prompt for AI joke analysis."""
        return f"""
You are a comedy analysis expert. Analyze this comedic beat:

COMEDIC BEAT:
Type: {comedic_beat.get('type', 'unknown')}
Setup: {comedic_beat.get('setup', 'N/A')}
Payoff: {comedic_beat.get('payoff', 'N/A')}
Characters: {', '.join(comedic_beat.get('characters', []))}
Context: {comedic_beat.get('context', 'N/A')}

TASK: Analyze this joke's structure and effectiveness.

RESPOND IN JSON:
{{
  "joke_type": "wordplay|situational|physical|callback|character|misdirection|running_gag",
  "setup": "the setup text",
  "misdirection": "optional misdirection element",
  "punchline": "the payoff/punchline",
  "effectiveness_score": 0.0-1.0,
  "improvement_suggestions": ["suggestion 1", "suggestion 2"],
  "callback_potential": true|false
}}

SCORING CRITERIA:
- Setup clarity: Is the setup clear and concise?
- Misdirection: Is there effective misdirection?
- Payoff surprise: Is the punchline unexpected but logical?
- Character consistency: Does it fit the character?
- Timing: Is the setup-to-payoff timing good?

Score 0.8+ for excellent jokes, 0.6-0.8 for good, 0.4-0.6 for mediocre, <0.4 for weak.
"""
    
    def _create_fallback_joke_structure(
        self,
        comedic_beat: Dict,
        joke_index: int,
    ) -> JokeStructure:
        """Create basic joke structure when AI analysis fails."""
        return JokeStructure(
            joke_id=f"joke_{joke_index:03d}",
            joke_type=JokeType.SITUATIONAL,
            setup=comedic_beat.get("setup", ""),
            punchline=comedic_beat.get("payoff", ""),
            timing_position=comedic_beat.get("timing", 0.0),
            characters_involved=comedic_beat.get("characters", []),
            effectiveness_score=0.5,
            improvement_suggestions=["AI analysis unavailable"],
        )
    
    async def _generate_alternatives_for_jokes(
        self,
        weak_jokes: List[JokeStructure],
        voice_profiles: Dict[str, CharacterVoiceProfile],
    ) -> List[AlternativePunchline]:
        """
        Generate alternative punchlines for weak jokes.
        
        Args:
            weak_jokes: Jokes with low effectiveness scores
            voice_profiles: Character voices for consistency
        
        Returns:
            List of alternative punchlines
        """
        alternatives = []
        
        for joke in weak_jokes:
            try:
                alts = await self._generate_alternative_punchlines(
                    joke, voice_profiles
                )
                alternatives.extend(alts)
            except Exception as e:
                logger.warning(
                    f"Failed to generate alternatives for {joke.joke_id}: {e}"
                )
                continue
        
        return alternatives
    
    async def _generate_alternative_punchlines(
        self,
        joke: JokeStructure,
        voice_profiles: Dict[str, CharacterVoiceProfile],
    ) -> List[AlternativePunchline]:
        """
        Generate alternative punchlines for a specific joke.
        
        Uses AI to create 2-3 alternative versions that might be more effective.
        
        Args:
            joke: Original joke to improve
            voice_profiles: Character voices
        
        Returns:
            List of alternative punchlines (2-3)
        """
        # Get voice profile for main character
        main_character = joke.characters_involved[0] if joke.characters_involved else None
        voice_context = ""
        if main_character and main_character in voice_profiles:
            profile = voice_profiles[main_character]
            voice_context = f"""
CHARACTER VOICE:
- Vocabulary: {profile.vocabulary_level}
- Catchphrases: {', '.join(profile.catchphrases[:3])}
- Verbal tics: {', '.join(profile.verbal_tics[:3])}
"""
        
        prompt = f"""
You are a comedy writer improving jokes. Generate alternative punchlines.

ORIGINAL JOKE:
Type: {joke.joke_type.value}
Setup: {joke.setup}
Original Punchline: {joke.punchline}
Current Score: {joke.effectiveness_score:.2f}
Issues: {', '.join(joke.improvement_suggestions)}

{voice_context}

TASK: Generate 2-3 alternative punchlines that:
1. Address the identified issues
2. Maintain character voice
3. Keep the same setup
4. Increase comedic effectiveness

RESPOND IN JSON:
{{
  "alternatives": [
    {{
      "punchline": "alternative punchline text",
      "reasoning": "why this works better",
      "estimated_effectiveness": 0.0-1.0,
      "maintains_character": true|false
    }}
  ]
}}
"""
        
        try:
            response = await self.claude_client.generate(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7,  # Higher temp for creative alternatives
            )
            data = json.loads(response)
            
            return [
                AlternativePunchline(
                    original_joke_id=joke.joke_id,
                    punchline=alt["punchline"],
                    reasoning=alt["reasoning"],
                    estimated_effectiveness=alt["estimated_effectiveness"],
                    maintains_character=alt.get("maintains_character", True),
                )
                for alt in data.get("alternatives", [])
            ]
            
        except Exception as e:
            logger.error(f"Failed to generate alternatives: {e}")
            return []
    
    def _detect_callback_opportunities(
        self,
        analyzed_jokes: List[JokeStructure],
        scene_dialogues: List[SceneDialogue],
    ) -> List[CallbackOpportunity]:
        """
        Detect opportunities for callback comedy.
        
        Identifies jokes with callback potential and suggests where/how
        to reference them later in the script.
        
        Args:
            analyzed_jokes: All analyzed jokes
            scene_dialogues: Scene context
        
        Returns:
            List of callback opportunities
        """
        opportunities = []
        
        # Find jokes with callback potential
        callback_sources = [
            joke for joke in analyzed_jokes
            if joke.callback_potential and joke.effectiveness_score > 0.6
        ]
        
        for source_joke in callback_sources:
            # Look for natural callback points later in the script
            source_position = source_joke.timing_position
            
            for target_idx, scene in enumerate(scene_dialogues):
                # Only look for callbacks in later scenes
                if target_idx * 180 <= source_position:  # Assume 3min scenes
                    continue
                
                # Simple heuristic: suggest callback if characters overlap
                scene_characters = {line.character for line in scene.dialogue_lines}
                if any(char in scene_characters for char in source_joke.characters_involved):
                    opportunity = CallbackOpportunity(
                        source_joke_id=source_joke.joke_id,
                        target_scene=f"scene_{target_idx:02d}",
                        target_timing=target_idx * 180.0,  # Rough estimate
                        callback_suggestion=f"Reference '{source_joke.punchline}' in context of current situation",
                        comedic_payoff="Rewards attentive viewers, creates cohesion",
                        risk_level=0.3 if target_idx <= 3 else 0.6,  # Early callbacks safer
                    )
                    opportunities.append(opportunity)
        
        # Limit to top 3-5 most promising callbacks
        return opportunities[:5]
    
    def _analyze_comedy_timing(
        self,
        analyzed_jokes: List[JokeStructure],
        scene_dialogues: List[SceneDialogue],
    ) -> ComedyTimingAnalysis:
        """
        Analyze comedy distribution and pacing.
        
        Checks for clusters (too many jokes close together) and dead zones
        (long stretches without comedy).
        
        Args:
            analyzed_jokes: All jokes in the script
            scene_dialogues: Scene context for runtime estimation
        
        Returns:
            Timing analysis with pacing recommendations
        """
        if not analyzed_jokes:
            return ComedyTimingAnalysis(
                total_jokes=0,
                average_spacing=0.0,
                timing_category=JokeTiming.WELL_SPACED,
            )
        
        # Sort jokes by timing
        sorted_jokes = sorted(analyzed_jokes, key=lambda j: j.timing_position)
        
        # Calculate spacing between jokes
        spacings = []
        for i in range(len(sorted_jokes) - 1):
            spacing = sorted_jokes[i + 1].timing_position - sorted_jokes[i].timing_position
            spacings.append(spacing)
        
        average_spacing = sum(spacings) / len(spacings) if spacings else 0.0
        
        # Determine timing category
        if average_spacing < 30:
            timing_category = JokeTiming.RAPID_FIRE
        elif average_spacing <= 90:
            timing_category = JokeTiming.WELL_SPACED
        else:
            timing_category = JokeTiming.SLOW_BURN
        
        # Find clusters (< 20 seconds between jokes)
        clusters = []
        for i, spacing in enumerate(spacings):
            if spacing < 20:
                scene_idx = int(sorted_jokes[i].timing_position / 180)
                scene_id = f"scene_{scene_idx:02d}"
                if scene_id not in clusters:
                    clusters.append(scene_id)
        
        # Find dead zones (> 120 seconds without a joke)
        dead_zones = []
        for i, spacing in enumerate(spacings):
            if spacing > 120:
                scene_idx = int(sorted_jokes[i + 1].timing_position / 180)
                scene_id = f"scene_{scene_idx:02d}"
                if scene_id not in dead_zones:
                    dead_zones.append(scene_id)
        
        # Calculate pacing score
        pacing_score = self._calculate_pacing_score(
            average_spacing, len(clusters), len(dead_zones)
        )
        
        return ComedyTimingAnalysis(
            total_jokes=len(analyzed_jokes),
            average_spacing=average_spacing,
            timing_category=timing_category,
            clusters=clusters,
            dead_zones=dead_zones,
            optimal_spacing=45.0,
            pacing_score=pacing_score,
        )
    
    def _calculate_pacing_score(
        self,
        average_spacing: float,
        num_clusters: int,
        num_dead_zones: int,
    ) -> float:
        """Calculate how well-paced the comedy is."""
        # Ideal spacing is around 45 seconds
        spacing_score = 1.0 - min(abs(average_spacing - 45) / 45, 1.0)
        
        # Penalize clusters and dead zones
        cluster_penalty = min(num_clusters * 0.1, 0.4)
        dead_zone_penalty = min(num_dead_zones * 0.15, 0.5)
        
        pacing_score = max(spacing_score - cluster_penalty - dead_zone_penalty, 0.0)
        
        return pacing_score
    
    def _calculate_overall_effectiveness(
        self,
        analyzed_jokes: List[JokeStructure],
    ) -> float:
        """Calculate average effectiveness across all jokes."""
        if not analyzed_jokes:
            return 0.0
        
        total_score = sum(joke.effectiveness_score for joke in analyzed_jokes)
        return total_score / len(analyzed_jokes)
    
    def _generate_optimization_summary(
        self,
        analyzed_jokes: List[JokeStructure],
        alternative_punchlines: List[AlternativePunchline],
        callback_opportunities: List[CallbackOpportunity],
        timing_analysis: ComedyTimingAnalysis,
    ) -> str:
        """Generate human-readable optimization summary."""
        weak_count = sum(1 for j in analyzed_jokes if j.effectiveness_score < 0.6)
        strong_count = sum(1 for j in analyzed_jokes if j.effectiveness_score >= 0.8)
        
        summary_parts = [
            f"Analyzed {len(analyzed_jokes)} jokes.",
            f"Strong jokes: {strong_count}, Weak jokes: {weak_count}.",
            f"Generated {len(alternative_punchlines)} alternative punchlines.",
            f"Found {len(callback_opportunities)} callback opportunities.",
            f"Pacing: {timing_analysis.timing_category.value} "
            f"(avg {timing_analysis.average_spacing:.1f}s between jokes).",
        ]
        
        if timing_analysis.clusters:
            summary_parts.append(
                f"WARNING: {len(timing_analysis.clusters)} scenes with joke clusters."
            )
        
        if timing_analysis.dead_zones:
            summary_parts.append(
                f"WARNING: {len(timing_analysis.dead_zones)} scenes with dead zones."
            )
        
        return " ".join(summary_parts)
