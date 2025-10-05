"""
Episode Script Generator - Creates episode outlines and scene structures.

Generates episode premises, scene breakdowns, and structural outlines
for modern TV parodies based on transformation rules.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.services.ai.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


@dataclass
class Scene:
    """Individual scene in an episode."""
    scene_number: int
    location: str
    characters: List[str]
    time_of_day: str
    description: str
    plot_relevance: str  # "A-plot", "B-plot", "both"
    comedic_beats: List[str]
    estimated_runtime: int  # seconds


@dataclass
class EpisodeOutline:
    """Complete episode outline."""
    episode_number: int
    title: str
    logline: str
    premise: str
    a_plot_summary: str
    b_plot_summary: Optional[str]
    scenes: List[Scene]
    total_runtime: int  # seconds
    opening_sequence: str
    closing_sequence: str
    key_comedic_moments: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


class EpisodeGenerator:
    """
    Generates episode outlines and scene structures.
    
    Uses AI and transformation rules to create episode premises
    and detailed scene breakdowns.
    """
    
    def __init__(
        self,
        claude_client: ClaudeClient,
        database_manager=None
    ):
        """
        Initialize episode generator.
        
        Args:
            claude_client: Claude AI client
            database_manager: Database for caching
        """
        self.claude_client = claude_client
        self.db_manager = database_manager
    
    async def generate_episode(
        self,
        show_title: str,
        transformation_rules: Dict,
        narrative_structure: Dict,
        episode_number: int = 1,
        user_prompt: Optional[str] = None
    ) -> Optional[EpisodeOutline]:
        """
        Generate a complete episode outline.
        
        Args:
            show_title: Name of the show
            transformation_rules: Transformation rules from engine
            narrative_structure: Narrative analysis results
            episode_number: Episode number
            user_prompt: Optional specific premise request
            
        Returns:
            EpisodeOutline with complete scene breakdown
            
        Example:
            >>> generator = EpisodeGenerator(claude_client)
            >>> outline = await generator.generate_episode(
            ...     "I Love Lucy 2025",
            ...     transformation_rules,
            ...     narrative_structure
            ... )
            >>> print(f"Title: {outline.title}")
            >>> print(f"Scenes: {len(outline.scenes)}")
        """
        logger.info(f"Generating episode {episode_number} for {show_title}")
        
        # Build generation prompt
        prompt = self._build_episode_prompt(
            show_title,
            transformation_rules,
            narrative_structure,
            episode_number,
            user_prompt
        )
        
        # Generate with Claude
        try:
            response_text = await self.claude_client.generate(
                prompt=prompt,
                system="You are a TV comedy writer. Create episode outlines in valid JSON format.",
                temperature=0.8,  # Higher for creativity
                max_tokens=4000
            )
            
            # Parse JSON
            response_json = json.loads(response_text)
            
            # Build outline
            outline = self._build_outline(response_json, episode_number, show_title)
            
            logger.info(f"Generated episode: {outline.title} ({len(outline.scenes)} scenes)")
            
            return outline
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Claude: {e}")
            return None
        except Exception as e:
            logger.error(f"Episode generation error: {e}")
            return None
    
    def _build_episode_prompt(
        self,
        show_title: str,
        transformation_rules: Dict,
        narrative_structure: Dict,
        episode_number: int,
        user_prompt: Optional[str]
    ) -> str:
        """Build comprehensive episode generation prompt."""
        
        prompt = f"""Create a complete episode outline for "{show_title}" - Episode {episode_number}.

## SHOW TRANSFORMATION RULES

**Modern Premise:**
{transformation_rules.get('modern_premise', 'Modern parody of classic sitcom')}

**Setting:**
- Original: {transformation_rules.get('setting', {}).get('original', 'Classic setting')}
- Modern: {transformation_rules.get('setting', {}).get('modern', '2025 setting')}

**Main Characters:**
"""
        
        for char in transformation_rules.get('character_transformations', []):
            prompt += f"- {char.get('original_name', 'Character')}: {char.get('modern_occupation', 'Modern occupation')}\n"
            prompt += f"  Motivation: {char.get('motivation_shift', 'Modern goals')}\n"
        
        prompt += f"""
**Humor Style:**
- Original: {transformation_rules.get('humor_transformation', {}).get('original_style', 'Classic comedy')}
- Modern: {transformation_rules.get('humor_transformation', {}).get('modern_style', 'Modern comedy')}

**Technology Opportunities:**
{', '.join(transformation_rules.get('technology_opportunities', [])[:5])}

## NARRATIVE STRUCTURE

**Structure Type:** {narrative_structure.get('structure_type', 'Episodic')}
**Opening Convention:** {narrative_structure.get('opening_convention', 'Standard opening')}
**Closing Convention:** {narrative_structure.get('closing_convention', 'Standard closing')}

**Recurring Devices:**
"""
        
        for device in narrative_structure.get('recurring_devices', [])[:3]:
            prompt += f"- {device.get('pattern_name', 'Device')}: {device.get('description', 'Description')}\n"
        
        if user_prompt:
            prompt += f"\n## SPECIFIC EPISODE REQUEST\n{user_prompt}\n"
        
        prompt += """
## EPISODE REQUIREMENTS

Create a complete episode outline with:

1. **Episode Title** - Funny, punny, or clever
2. **Logline** - One sentence premise
3. **Premise** - 2-3 sentence setup
4. **A-Plot** - Main story (200-300 words)
5. **B-Plot** - Subplot (100-150 words)
6. **Scene Breakdown** - 8-12 scenes, each with:
   - Scene number
   - Location
   - Characters present
   - Time of day
   - Description (2-3 sentences)
   - Plot relevance (A-plot, B-plot, or both)
   - Comedic beats (1-3 specific jokes or gags)
   - Estimated runtime (30-180 seconds)

7. **Opening Sequence** - How episode opens (following show convention)
8. **Closing Sequence** - How episode ends
9. **Key Comedic Moments** - 5-7 biggest laughs
10. **Total Runtime** - Should be ~1320 seconds (22 minutes for sitcom)

## CREATIVE GUIDELINES

- Use the transformation rules to modernize classic storylines
- Integrate technology naturally (social media fails, smart home chaos, etc.)
- Preserve character DNA while updating context
- Include callbacks to the original show for fans
- Build comedy through escalation
- Pay off setups in satisfying ways
- Balance nostalgia with fresh humor

## OUTPUT FORMAT

Return ONLY valid JSON:

{
  "title": "The One Where Lucy Goes Viral",
  "logline": "Lucy's innocent cooking video becomes a viral sensation for all the wrong reasons.",
  "premise": "Lucy tries to launch a cooking channel to compete with Ricky's successful YouTube channel, but her first video accidentally goes viral when...",
  "a_plot": "Lucy decides to start a cooking channel...",
  "b_plot": "Ethel gets addicted to a meditation app...",
  "scenes": [
    {
      "scene_number": 1,
      "location": "Living room - Morning",
      "characters": ["Lucy", "Ricky"],
      "time_of_day": "Morning",
      "description": "Lucy watches Ricky's latest YouTube video hit 1M views. She insists she could do that too.",
      "plot_relevance": "A-plot",
      "comedic_beats": [
        "Lucy mispronounces 'algorithm'",
        "Ricky's patronizing 'sure honey' response"
      ],
      "estimated_runtime": 90
    }
  ],
  "opening_sequence": "Cold open: Lucy records herself attempting TikTok dance, falls into Christmas tree",
  "closing_sequence": "Tag: Lucy's viral fail video gets her invited on Ellen (the 2025 podcast version)",
  "key_comedic_moments": [
    "Lucy sets kitchen on fire during live stream",
    "Comment section roasts her technique"
  ],
  "total_runtime": 1320
}

CRITICAL:
- Return ONLY valid JSON, no markdown
- Be specific and detailed
- Make it FUNNY
- Use the transformation rules
- Include modern references
- Build escalating comedy
"""
        
        return prompt
    
    def _build_outline(
        self,
        response_json: Dict,
        episode_number: int,
        show_title: str
    ) -> EpisodeOutline:
        """Build EpisodeOutline from AI response."""
        
        # Parse scenes
        scenes = [
            Scene(
                scene_number=s.get('scene_number', i+1),
                location=s.get('location', 'Unknown'),
                characters=s.get('characters', []),
                time_of_day=s.get('time_of_day', 'Day'),
                description=s.get('description', ''),
                plot_relevance=s.get('plot_relevance', 'A-plot'),
                comedic_beats=s.get('comedic_beats', []),
                estimated_runtime=s.get('estimated_runtime', 60)
            )
            for i, s in enumerate(response_json.get('scenes', []))
        ]
        
        return EpisodeOutline(
            episode_number=episode_number,
            title=response_json.get('title', f'{show_title} - Episode {episode_number}'),
            logline=response_json.get('logline', ''),
            premise=response_json.get('premise', ''),
            a_plot_summary=response_json.get('a_plot', ''),
            b_plot_summary=response_json.get('b_plot'),
            scenes=scenes,
            total_runtime=response_json.get('total_runtime', sum(s.estimated_runtime for s in scenes)),
            opening_sequence=response_json.get('opening_sequence', 'Standard opening'),
            closing_sequence=response_json.get('closing_sequence', 'Standard closing'),
            key_comedic_moments=response_json.get('key_comedic_moments', [])
        )


# Example usage
async def main():
    """Example episode generation."""
    from src.services.ai.claude_client import ClaudeClient
    
    claude_client = ClaudeClient()
    generator = EpisodeGenerator(claude_client)
    
    # Sample transformation rules
    transformation_rules = {
        'modern_premise': 'Lucy is now a wannabe influencer married to a YouTuber',
        'setting': {
            'original': '1950s NYC apartment',
            'modern': '2025 Brooklyn loft'
        },
        'character_transformations': [
            {
                'original_name': 'Lucy Ricardo',
                'modern_occupation': 'Content creator',
                'motivation_shift': 'Wants to go viral'
            }
        ],
        'humor_transformation': {
            'original_style': 'Physical comedy',
            'modern_style': 'Cringe comedy + social media fails'
        },
        'technology_opportunities': ['Instagram', 'TikTok', 'Smart home']
    }
    
    narrative_structure = {
        'structure_type': 'Episodic sitcom',
        'opening_convention': 'Cold open',
        'closing_convention': 'Tag scene',
        'recurring_devices': [
            {
                'pattern_name': 'Scheme Backfires',
                'description': "Lucy's plans always go wrong spectacularly"
            }
        ]
    }
    
    outline = await generator.generate_episode(
        show_title="I Love Lucy 2025",
        transformation_rules=transformation_rules,
        narrative_structure=narrative_structure,
        episode_number=1
    )
    
    if outline:
        print(f"\n✅ Episode Generated!")
        print(f"Title: {outline.title}")
        print(f"Logline: {outline.logline}")
        print(f"\nScenes: {len(outline.scenes)}")
        for scene in outline.scenes[:3]:  # Show first 3
            print(f"  {scene.scene_number}. {scene.location} - {scene.description[:60]}...")
        print(f"\nTotal Runtime: {outline.total_runtime}s ({outline.total_runtime // 60} minutes)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
