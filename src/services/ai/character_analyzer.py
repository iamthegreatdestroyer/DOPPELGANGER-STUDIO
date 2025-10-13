"""
Character Analyzer - Extract personality traits and patterns using AI.

Analyzes TV show characters to identify core traits, speech patterns,
relationships, and transformation opportunities for parody creation.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json
import logging

from src.services.ai.base_client import BaseAIClient
from src.models.research import CharacterData, WikipediaData

logger = logging.getLogger(__name__)


@dataclass
class CharacterAnalysis:
    """Comprehensive character analysis result."""
    character_name: str
    core_traits: List[str] = field(default_factory=list)
    speech_patterns: List[str] = field(default_factory=list)
    catchphrases: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    comedic_elements: List[str] = field(default_factory=list)
    character_arc: Optional[str] = None
    modern_equivalent: Optional[str] = None
    transformation_notes: List[str] = field(default_factory=list)


CHARACTER_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "core_traits": {
            "type": "array",
            "items": {"type": "string"},
            "description": "5-10 core personality traits"
        },
        "speech_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Distinctive speech patterns or mannerisms"
        },
        "catchphrases": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Famous catchphrases or quotes"
        },
        "relationships": {
            "type": "object",
            "description": "Key relationships (name: relationship description)"
        },
        "comedic_elements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "What makes this character funny"
        },
        "character_arc": {
            "type": "string",
            "description": "Character development over the series"
        },
        "modern_equivalent": {
            "type": "string",
            "description": "Modern 2025 equivalent of this character type"
        },
        "transformation_notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Ideas for modernizing this character"
        }
    },
    "required": ["core_traits", "comedic_elements", "modern_equivalent"]
}


class CharacterAnalyzer:
    """
    Analyze TV characters using AI.
    
    Extracts personality traits, speech patterns, relationships, and identifies
    opportunities for modern transformation in parody creation.
    
    Example:
        >>> from src.services.ai import ClaudeClient
        >>> analyzer = CharacterAnalyzer(ClaudeClient(api_key))
        >>> analysis = await analyzer.analyze_character(lucy_data, show_context)
        >>> print(f"Traits: {', '.join(analysis.core_traits)}")
    """
    
    SYSTEM_PROMPT = """You are an expert TV character analyst with deep knowledge of 
classic television and modern pop culture. Your task is to analyze characters from 
classic TV shows and identify:

1. Core personality traits that define the character
2. Distinctive speech patterns and mannerisms
3. Key relationships and how they drive comedy
4. What makes the character funny
5. How the character could be transformed for a modern 2025 parody

Be specific, insightful, and focus on elements that can be translated to modern contexts.
Output your analysis as structured JSON."""
    
    def __init__(self, ai_client: BaseAIClient):
        """
        Initialize character analyzer.
        
        Args:
            ai_client: AI client (Claude or GPT-4)
        """
        self.ai_client = ai_client
    
    async def analyze_character(
        self,
        character: CharacterData,
        show_context: WikipediaData
    ) -> CharacterAnalysis:
        """
        Analyze a single character.
        
        Args:
            character: Character data from research
            show_context: Show context for additional information
            
        Returns:
            Comprehensive character analysis
            
        Example:
            >>> lucy = CharacterData(name="Lucy Ricardo", description="...")
            >>> show = WikipediaData(title="I Love Lucy", ...)
            >>> analysis = await analyzer.analyze_character(lucy, show)
        """
        logger.info(f"Analyzing character: {character.name}")
        
        prompt = self._build_prompt(character, show_context)
        
        try:
            response = await self.ai_client.complete_json(
                prompt=prompt,
                schema=CHARACTER_ANALYSIS_SCHEMA,
                system=self.SYSTEM_PROMPT,
                max_tokens=2048
            )
            
            # Build analysis object
            analysis = CharacterAnalysis(
                character_name=character.name,
                core_traits=response.get('core_traits', []),
                speech_patterns=response.get('speech_patterns', []),
                catchphrases=response.get('catchphrases', []),
                relationships=response.get('relationships', {}),
                comedic_elements=response.get('comedic_elements', []),
                character_arc=response.get('character_arc'),
                modern_equivalent=response.get('modern_equivalent'),
                transformation_notes=response.get('transformation_notes', [])
            )
            
            logger.info(
                f"Analysis complete: {len(analysis.core_traits)} traits, "
                f"{len(analysis.comedic_elements)} comedic elements"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Character analysis failed: {e}")
            raise
    
    async def analyze_all_characters(
        self,
        characters: List[CharacterData],
        show_context: WikipediaData
    ) -> List[CharacterAnalysis]:
        """
        Analyze multiple characters from a show.
        
        Args:
            characters: List of character data
            show_context: Show context
            
        Returns:
            List of character analyses
        """
        import asyncio
        
        logger.info(f"Analyzing {len(characters)} characters")
        
        # Analyze in parallel for speed
        tasks = [
            self.analyze_character(char, show_context)
            for char in characters
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        analyses = [r for r in results if isinstance(r, CharacterAnalysis)]
        
        logger.info(f"Successfully analyzed {len(analyses)}/{len(characters)} characters")
        
        return analyses
    
    def _build_prompt(
        self,
        character: CharacterData,
        show_context: WikipediaData
    ) -> str:
        """Build analysis prompt from character and show data."""
        prompt = f"""Analyze this character from classic television:

**Show:** {show_context.title} ({show_context.years})
**Network:** {show_context.network}
**Setting:** {show_context.setting or 'Classic TV era'}

**Character:** {character.name}
**Description:** {character.description}

**Show Context:**
Genres: {', '.join(show_context.genre) if show_context.genre else 'Sitcom'}
Themes: {', '.join(show_context.themes) if show_context.themes else 'Family comedy'}

Provide a comprehensive analysis focusing on:
1. Core personality traits (5-10 traits)
2. Speech patterns and distinctive mannerisms
3. Famous catchphrases or recurring lines
4. Key relationships with other characters
5. What makes this character funny or memorable
6. Character development over the series
7. Modern 2025 equivalent (e.g., "1950s housewife → 2025 lifestyle influencer")
8. How to transform this character for a modern parody

Be specific and insightful. Focus on elements that translate to modern contexts."""
        
        return prompt


# Example usage
async def main():
    """Example character analysis."""
    import os
    from src.services.ai import ClaudeClient
    
    # Initialize AI client
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable")
        return
    
    client = ClaudeClient(api_key)
    analyzer = CharacterAnalyzer(client)
    
    # Create example character data
    lucy = CharacterData(
        name="Lucy Ricardo",
        description="""Lucy Ricardo is the main character, played by Lucille Ball. 
        She is a middle-class housewife who aspires to be in show business but is 
        constantly thwarted in her attempts. She is married to Ricky Ricardo, a 
        Cuban bandleader. Lucy is known for her elaborate schemes to break into 
        show business, often involving her best friend Ethel Mertz.""",
        traits=[],
        relationships={}
    )
    
    # Create show context
    show = WikipediaData(
        title="I Love Lucy",
        years="1951-1957",
        network="CBS",
        genre=["Sitcom", "Family"],
        setting="1950s Manhattan",
        themes=["Marriage", "Show Business", "Friendship"],
        main_characters=[],
        premise="A housewife aspires to perform on stage with her bandleader husband."
    )
    
    # Analyze character
    print("Analyzing Lucy Ricardo...")
    print("=" * 60)
    
    analysis = await analyzer.analyze_character(lucy, show)
    
    print(f"\nCharacter: {analysis.character_name}")
    print(f"\nCore Traits: {', '.join(analysis.core_traits)}")
    print(f"\nSpeech Patterns: {', '.join(analysis.speech_patterns)}")
    print(f"\nCatchphrases: {', '.join(analysis.catchphrases)}")
    print(f"\nComedic Elements:")
    for element in analysis.comedic_elements:
        print(f"  - {element}")
    print(f"\nModern Equivalent: {analysis.modern_equivalent}")
    print(f"\nTransformation Ideas:")
    for note in analysis.transformation_notes:
        print(f"  - {note}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
