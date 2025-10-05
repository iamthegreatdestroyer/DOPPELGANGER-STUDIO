"""
Transformation Engine - Maps classic TV elements to modern contexts.

Generates transformation rules for adapting classic TV shows into
contemporary parodies while preserving narrative DNA and comedic essence.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from src.services.ai.claude_client import ClaudeClient
from src.services.ai.gpt_client import GPTClient
from src.services.creative.response_validators import (
    AIResponseValidator,
    TransformationRulesResponse
)

logger = logging.getLogger(__name__)


@dataclass
class SettingTransformation:
    """Transformation of time period and location."""
    original_era: str
    original_location: str
    modern_era: str = "2025"
    modern_location: str = ""
    justification: str = ""
    visual_changes: List[str] = field(default_factory=list)
    cultural_shifts: List[str] = field(default_factory=list)


@dataclass
class CharacterTransformation:
    """Transformation of a character archetype."""
    original_name: str
    original_archetype: str
    original_occupation: str
    modern_archetype: str
    modern_occupation: str
    personality_retention: List[str]  # Traits that stay the same
    personality_updates: List[str]  # Traits that change
    relationship_dynamics: Dict[str, str]
    technology_integration: List[str]
    motivation_shift: str


@dataclass
class HumorTransformation:
    """Transformation of comedy style."""
    original_style: str
    modern_style: str
    device_mappings: List[Dict[str, str]]  # Original → Modern
    preserved_elements: List[str]
    updated_elements: List[str]
    tone_guidance: str


@dataclass
class TransformationRules:
    """Complete transformation ruleset for a show."""
    show_title: str
    original_premise: str
    modern_premise: str
    setting_transformation: SettingTransformation
    character_transformations: List[CharacterTransformation]
    humor_transformation: HumorTransformation
    cultural_updates: List[Dict[str, str]]
    technology_opportunities: List[str]
    conflict_modernization: List[Dict[str, str]]
    taboo_updates: List[str]  # Things that were OK then, not now
    reverse_taboos: List[str]  # Things that are OK now, not then
    generated_at: datetime = field(default_factory=datetime.now)
    model_used: str = "claude-sonnet-4"


class TransformationEngine:
    """
    Generates transformation rules for adapting classic TV to modern contexts.
    
    Uses AI to intelligently map 1950s-1990s elements to 2025 equivalents
    while preserving the narrative essence and comedic DNA.
    """
    
    def __init__(
        self,
        claude_client: Optional[ClaudeClient] = None,
        gpt_client: Optional[GPTClient] = None,
        database_manager=None
    ):
        """
        Initialize transformation engine.
        
        Args:
            claude_client: Claude AI client (primary)
            gpt_client: GPT-4 client (fallback)
            database_manager: Database manager for caching
        """
        self.claude_client = claude_client
        self.gpt_client = gpt_client
        self.db_manager = database_manager
        self.validator = AIResponseValidator()
    
    async def generate_transformation_rules(
        self,
        show_data: Dict,
        character_analysis: Optional[Dict] = None,
        narrative_analysis: Optional[Dict] = None
    ) -> Optional[TransformationRules]:
        """
        Generate comprehensive transformation rules for a show.
        
        Args:
            show_data: Research data about the original show
            character_analysis: Character analysis results
            narrative_analysis: Narrative structure analysis
            
        Returns:
            TransformationRules with complete mapping
            
        Example:
            >>> engine = TransformationEngine(claude_client, db_manager)
            >>> rules = await engine.generate_transformation_rules(lucy_data)
            >>> print(f"Modern premise: {rules.modern_premise}")
        """
        logger.info(f"Generating transformation rules: {show_data.get('title')}")
        
        # Check cache
        cached = await self._get_from_cache(show_data.get('title'))
        if cached:
            logger.info("Using cached transformation rules")
            return cached
        
        # Build transformation prompt
        prompt = self._build_transformation_prompt(
            show_data,
            character_analysis,
            narrative_analysis
        )
        
        # Get AI-generated rules with retry
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Try Claude first
                if self.claude_client:
                    rules = await self._transform_with_claude(prompt, attempt)
                    if rules:
                        logger.info(f"Transformation complete (Claude, attempt {attempt + 1})")
                        await self._save_to_cache(show_data.get('title'), rules)
                        return rules
                
                # Fallback to GPT-4
                if self.gpt_client:
                    rules = await self._transform_with_gpt(prompt, attempt)
                    if rules:
                        logger.info(f"Transformation complete (GPT-4, attempt {attempt + 1})")
                        await self._save_to_cache(show_data.get('title'), rules)
                        return rules
                
            except Exception as e:
                logger.error(f"Transformation error (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    raise
        
        logger.error("Transformation failed after all retries")
        return None
    
    def _build_transformation_prompt(
        self,
        show_data: Dict,
        character_analysis: Optional[Dict],
        narrative_analysis: Optional[Dict]
    ) -> str:
        """Build comprehensive transformation prompt."""
        
        prompt = f"""Transform the classic TV show "{show_data.get('title')}" into a modern 2025 parody.

## ORIGINAL SHOW INFORMATION

**Title:** {show_data.get('title')}
**Original Years:** {show_data.get('years', 'Unknown')}
**Network:** {show_data.get('network', 'Unknown')}
**Genre:** {', '.join(show_data.get('genre', []))}

**Original Premise:**
{show_data.get('premise', show_data.get('plot_summary', ''))}

**Setting:** {show_data.get('setting', 'Unknown')}
**Themes:** {', '.join(show_data.get('themes', []))}

"""
        
        if character_analysis:
            prompt += "\n## CHARACTER ANALYSIS\n\n"
            prompt += f"Main characters analyzed: {len(character_analysis.get('characters', []))}\n"
        
        if narrative_analysis:
            prompt += "\n## NARRATIVE STRUCTURE\n\n"
            prompt += f"Structure type: {narrative_analysis.get('structure_type', 'Unknown')}\n"
        
        prompt += """
## TRANSFORMATION REQUIREMENTS

Create a comprehensive transformation plan that:

1. **Preserves the Essence**
   - Keep the core DNA of characters and relationships
   - Maintain the comedic spirit and tone
   - Preserve narrative patterns that work

2. **Modernizes Context**
   - Update to 2025 setting (or contemporary equivalent)
   - Adapt occupations to modern equivalents
   - Integrate current technology and social media
   - Update cultural references and humor
   - Address modern social norms and sensitivities

3. **Enhances for Parody**
   - Amplify absurdities for comedic effect
   - Add meta-commentary on the original show
   - Create contrasts between original and modern eras
   - Play with audience expectations and nostalgia

## OUTPUT FORMAT

Return ONLY a valid JSON object with ALL required fields:

```json
{
  "show_title": "Show Name",
  "setting_transformation": {
    "original_setting": "1950s New York apartment",
    "modern_equivalent": "2025 Brooklyn loft",
    "justification": "Preserves cramped NYC living while updating to trendy modern area",
    "cultural_references": ["Social media", "Gig economy"]
  },
  "character_transformations": [
    {
      "original_character": "Lucy Ricardo",
      "original_archetype": "Ambitious housewife",
      "modern_archetype": "Aspiring influencer",
      "occupation_update": "Content creator",
      "motivation_update": "Wants to go viral instead of being in Ricky's show",
      "technology_integration": ["Instagram", "TikTok", "Ring light"]
    }
  ],
  "humor_transformation": {
    "original_humor_type": "Physical comedy",
    "modern_humor_type": "Cringe comedy and viral fails",
    "example_transformations": [
      {"original": "Gets drunk on Vitameatavegamin", "modern": "Accidentally goes live while drunk"}
    ]
  },
  "cultural_updates": [
    {"original": "TV variety show", "modern": "Netflix special"}
  ],
  "technology_opportunities": ["Smartphones", "Smart home", "Social media"],
  "conflict_modernization": [
    {"original": "Can't get into husband's show", "modern": "Can't get featured in partner's viral videos"}
  ]
}
```

CRITICAL:
- Return ONLY valid JSON
- Include ALL required fields
- Be specific and creative
- Ground transformations in real 2025 culture
"""
        
        return prompt
    
    async def _transform_with_claude(
        self,
        prompt: str,
        attempt: int
    ) -> Optional[TransformationRules]:
        """Generate transformation rules using Claude."""
        
        try:
            if attempt > 0:
                prompt += "\n\nIMPORTANT: Previous response had validation errors. Ensure all required fields present."
            
            response_text = await self.claude_client.generate(
                prompt=prompt,
                system="You are a creative TV adaptation expert. Return ONLY valid JSON.",
                temperature=0.7,
                max_tokens=4000
            )
            
            response_json = json.loads(response_text)
            validated = self.validator.validate_transformation_rules(response_json)
            
            if not validated:
                logger.warning("Claude transformation failed validation")
                return None
            
            return self._build_transformation_rules(validated, "claude-sonnet-4")
            
        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Claude transformation error: {e}")
            return None
    
    async def _transform_with_gpt(
        self,
        prompt: str,
        attempt: int
    ) -> Optional[TransformationRules]:
        """Generate transformation rules using GPT-4."""
        
        try:
            if attempt > 0:
                prompt += "\n\nIMPORTANT: Previous response had validation errors."
            
            response_text = await self.gpt_client.generate(
                prompt=prompt,
                system="You are a creative TV adaptation expert. Return ONLY valid JSON.",
                temperature=0.7,
                max_tokens=4000
            )
            
            response_json = json.loads(response_text)
            validated = self.validator.validate_transformation_rules(response_json)
            
            if not validated:
                logger.warning("GPT-4 transformation failed validation")
                return None
            
            return self._build_transformation_rules(validated, "gpt-4-turbo")
            
        except json.JSONDecodeError as e:
            logger.error(f"GPT-4 returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"GPT-4 transformation error: {e}")
            return None
    
    def _build_transformation_rules(
        self,
        validated_response: TransformationRulesResponse,
        model: str
    ) -> TransformationRules:
        """Build TransformationRules from validated response."""
        
        # Build setting transformation
        setting_transform = SettingTransformation(
            original_era=validated_response.setting_transformation.original_setting.split()[0] if validated_response.setting_transformation.original_setting else "1950s",
            original_location=validated_response.setting_transformation.original_setting,
            modern_location=validated_response.setting_transformation.modern_equivalent,
            justification=validated_response.setting_transformation.justification,
            cultural_shifts=validated_response.setting_transformation.cultural_references
        )
        
        # Build character transformations
        char_transforms = [
            CharacterTransformation(
                original_name=ct.original_character,
                original_archetype=ct.original_archetype,
                original_occupation=ct.original_archetype.split()[-1],
                modern_archetype=ct.modern_archetype,
                modern_occupation=ct.occupation_update or ct.modern_archetype,
                personality_retention=[],
                personality_updates=[],
                relationship_dynamics={},
                technology_integration=ct.technology_integration,
                motivation_shift=ct.motivation_update or "Modernized goals"
            )
            for ct in validated_response.character_transformations
        ]
        
        # Build humor transformation
        humor_transform = HumorTransformation(
            original_style=validated_response.humor_transformation.original_humor_type,
            modern_style=validated_response.humor_transformation.modern_humor_type,
            device_mappings=validated_response.humor_transformation.example_transformations,
            preserved_elements=[],
            updated_elements=[],
            tone_guidance="Maintain comedic spirit while updating context"
        )
        
        # Build complete rules
        return TransformationRules(
            show_title=validated_response.show_title,
            original_premise="Classic TV premise",
            modern_premise="Modern parody adaptation",
            setting_transformation=setting_transform,
            character_transformations=char_transforms,
            humor_transformation=humor_transform,
            cultural_updates=validated_response.cultural_updates,
            technology_opportunities=validated_response.technology_opportunities,
            conflict_modernization=validated_response.conflict_modernization,
            taboo_updates=[],
            reverse_taboos=[],
            model_used=model
        )
    
    async def _get_from_cache(self, show_title: str) -> Optional[TransformationRules]:
        """Get cached transformation rules from MongoDB."""
        if not self.db_manager:
            return None
        
        try:
            result = await self.db_manager.mongodb['ai_analysis'].find_one({
                'show_title': show_title,
                'analysis_type': 'transformation',
                'expires_at': {'$gt': datetime.now()}
            })
            
            if result:
                return self._deserialize_rules(result['output_data'])
            
        except Exception as e:
            logger.error(f"Cache read error: {e}")
        
        return None
    
    async def _save_to_cache(self, show_title: str, rules: TransformationRules):
        """Save transformation rules to MongoDB cache."""
        if not self.db_manager:
            return
        
        try:
            cache_doc = {
                'show_title': show_title,
                'analysis_type': 'transformation',
                'model': rules.model_used,
                'output_data': self._serialize_rules(rules),
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(days=30)
            }
            
            await self.db_manager.mongodb['ai_analysis'].update_one(
                {'show_title': show_title, 'analysis_type': 'transformation'},
                {'$set': cache_doc},
                upsert=True
            )
            
            logger.info(f"Cached transformation rules for {show_title}")
            
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def _serialize_rules(self, rules: TransformationRules) -> Dict:
        """Serialize TransformationRules for caching."""
        return {
            'show_title': rules.show_title,
            'modern_premise': rules.modern_premise,
            'setting_transformation': {
                'original_era': rules.setting_transformation.original_era,
                'modern_location': rules.setting_transformation.modern_location
            },
            'character_transformations': [
                {
                    'original_name': ct.original_name,
                    'modern_occupation': ct.modern_occupation,
                    'motivation_shift': ct.motivation_shift
                }
                for ct in rules.character_transformations
            ],
            'cultural_updates': rules.cultural_updates,
            'technology_opportunities': rules.technology_opportunities
        }
    
    def _deserialize_rules(self, data: Dict) -> TransformationRules:
        """Deserialize cached data to TransformationRules."""
        setting = SettingTransformation(
            original_era=data['setting_transformation']['original_era'],
            original_location="Original location",
            modern_location=data['setting_transformation']['modern_location']
        )
        
        characters = [
            CharacterTransformation(
                original_name=ct['original_name'],
                original_archetype="Original archetype",
                original_occupation="Original occupation",
                modern_archetype="Modern archetype",
                modern_occupation=ct['modern_occupation'],
                personality_retention=[],
                personality_updates=[],
                relationship_dynamics={},
                technology_integration=[],
                motivation_shift=ct['motivation_shift']
            )
            for ct in data['character_transformations']
        ]
        
        humor = HumorTransformation(
            original_style="Original humor",
            modern_style="Modern humor",
            device_mappings=[],
            preserved_elements=[],
            updated_elements=[],
            tone_guidance=""
        )
        
        return TransformationRules(
            show_title=data['show_title'],
            original_premise="",
            modern_premise=data['modern_premise'],
            setting_transformation=setting,
            character_transformations=characters,
            humor_transformation=humor,
            cultural_updates=data['cultural_updates'],
            technology_opportunities=data['technology_opportunities'],
            conflict_modernization=[],
            taboo_updates=[],
            reverse_taboos=[]
        )


# Example usage
async def main():
    """Example usage of transformation engine."""
    from src.services.ai.claude_client import ClaudeClient
    from src.services.database.database_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    claude_client = ClaudeClient()
    
    engine = TransformationEngine(
        claude_client=claude_client,
        database_manager=db_manager
    )
    
    show_data = {
        'title': 'I Love Lucy',
        'years': '1951-1957',
        'genre': ['Sitcom'],
        'premise': 'A housewife schemes to break into show business.',
        'setting': '1950s New York'
    }
    
    rules = await engine.generate_transformation_rules(show_data)
    
    if rules:
        print(f"Modern Premise: {rules.modern_premise}")
        print(f"Setting: {rules.setting_transformation.modern_location}")
        print("\nCharacter Transformations:")
        for char in rules.character_transformations:
            print(f"  {char.original_name} → {char.modern_occupation}")
    
    await db_manager.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
