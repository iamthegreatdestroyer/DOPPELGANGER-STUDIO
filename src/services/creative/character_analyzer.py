"""
Character Analyzer - AI-powered character analysis and trait extraction.

Analyzes TV show characters to extract personality traits, motivations,
relationships, and behavioral patterns.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CharacterAnalysis:
    """Container for character analysis results."""
    name: str
    traits: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    signature_behaviors: List[str] = field(default_factory=list)
    catchphrases: List[str] = field(default_factory=list)
    arc_type: Optional[str] = None
    role: Optional[str] = None  # protagonist, sidekick, foil, etc.
    humor_style: Optional[str] = None


class CharacterAnalyzer:
    """
    Analyzes characters using AI to extract deep personality insights.
    
    Uses AI to identify:
    - Core personality traits
    - Motivations and desires
    - Relationship dynamics
    - Signature behaviors and quirks
    - Speech patterns and catchphrases
    """
    
    def __init__(self, ai_client):
        """
        Initialize character analyzer.
        
        Args:
            ai_client: AIOrchestrator instance
        """
        self.ai_client = ai_client
    
    async def analyze_character(
        self,
        character_name: str,
        character_description: str,
        show_context: Optional[str] = None
    ) -> CharacterAnalysis:
        """
        Perform deep analysis of a character.
        
        Args:
            character_name: Name of character
            character_description: Description from research
            show_context: Optional show context for better analysis
            
        Returns:
            CharacterAnalysis with extracted insights
        """
        logger.info(f"Analyzing character: {character_name}")
        
        prompt = self._build_analysis_prompt(
            character_name, character_description, show_context
        )
        
        try:
            result = await self.ai_client.generate_json(
                prompt=prompt,
                system_prompt="You are an expert TV character psychologist.",
                temperature=0.3  # Lower for more consistent analysis
            )
            
            return CharacterAnalysis(
                name=character_name,
                traits=result.get('traits', []),
                motivations=result.get('motivations', []),
                relationships=result.get('relationships', {}),
                signature_behaviors=result.get('behaviors', []),
                catchphrases=result.get('catchphrases', []),
                arc_type=result.get('arc_type'),
                role=result.get('role'),
                humor_style=result.get('humor_style')
            )
            
        except Exception as e:
            logger.error(f"Character analysis failed: {e}")
            raise
    
    def _build_analysis_prompt(
        self,
        name: str,
        description: str,
        context: Optional[str]
    ) -> str:
        """Build optimized prompt for character analysis."""
        prompt = f"""Analyze this TV character in depth:

CHARACTER: {name}

DESCRIPTION:
{description}
"""
        
        if context:
            prompt += f"\nSHOW CONTEXT:\n{context}\n"
        
        prompt += """
Extract the following in JSON format:
{
  "traits": ["list of 5-7 core personality traits"],
  "motivations": ["list of 3-5 key motivations"],
  "relationships": {"character_name": "relationship type"},
  "behaviors": ["3-5 signature behaviors or quirks"],
  "catchphrases": ["any memorable catchphrases or speech patterns"],
  "arc_type": "character arc type (growth/fall/flat/etc)",
  "role": "narrative role (protagonist/sidekick/foil/etc)",
  "humor_style": "comedy style if applicable"
}

Be specific and insightful. Focus on defining characteristics."""
        
        return prompt
