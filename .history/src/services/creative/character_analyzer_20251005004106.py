"""
Character Analyzer - AI-powered character analysis and trait extraction.

Analyzes TV show characters to extract personality traits, motivations,
relationships, and behavioral patterns.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field
import json

from .response_validators import (
    AIResponseValidator,
    CharacterAnalysisResponse
)

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
    ) -> Optional[CharacterAnalysisResponse]:
        """
        Perform deep analysis of a character with validation.
        
        Args:
            character_name: Name of character
            character_description: Description from research
            show_context: Optional show context for better analysis
            
        Returns:
            Validated CharacterAnalysisResponse or None if failed
        """
        logger.info(f"Analyzing character: {character_name}")
        
        prompt = self._build_analysis_prompt(
            character_name, character_description, show_context
        )
        
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Call AI
                raw_response = await self.ai_client.generate(
                    prompt=prompt,
                    system_prompt=(
                        "You are an expert TV character psychologist. "
                        "Return ONLY valid JSON matching the character "
                        "analysis schema."
                    ),
                    temperature=0.3
                )
                
                # Parse JSON
                response_json = json.loads(raw_response)
                
                # Validate
                validator = AIResponseValidator()
                validated = validator.validate_character_analysis(
                    response_json
                )
                
                if validated:
                    logger.info(
                        f"Character analysis validated (attempt {attempt + 1})"
                    )
                    return validated
                else:
                    logger.warning(
                        f"Validation failed (attempt {attempt + 1})"
                    )
                    if attempt < max_attempts - 1:
                        # Make prompt stricter
                        prompt += (
                            "\n\nIMPORTANT: Your previous response had "
                            "validation errors. Ensure all required fields "
                            "are present."
                        )
                        
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                if attempt < max_attempts - 1:
                    prompt += (
                        "\n\nIMPORTANT: Response must be ONLY valid JSON, "
                        "no markdown or extra text."
                    )
                    
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                if attempt == max_attempts - 1:
                    raise
        
        logger.error("Character analysis failed after all retries")
        return None
    
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
