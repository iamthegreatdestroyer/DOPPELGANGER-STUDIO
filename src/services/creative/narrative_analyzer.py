"""
Narrative Structure Analyzer - AI-powered analysis of TV show storytelling patterns.

Identifies plot structures, recurring devices, narrative conventions, and
pacing patterns from classic TV shows for transformation into modern parodies.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.services.creative.claude_client import ClaudeClient
from src.services.creative.openai_client import OpenAIClient as GPTClient
from src.services.creative.response_validators import (
    AIResponseValidator,
    NarrativeAnalysisResponse
)

logger = logging.getLogger(__name__)


@dataclass
class EpisodeStructure:
    """Structure of a typical episode."""
    total_runtime: int  # minutes
    act_count: int
    act_lengths: List[int]  # minutes per act
    commercial_breaks: int
    opening_length: int  # seconds
    closing_length: int  # seconds


@dataclass
class NarrativePattern:
    """Recurring narrative pattern."""
    pattern_name: str
    description: str
    frequency: str  # "every episode", "weekly", "occasional"
    examples: List[str]
    purpose: str  # narrative function


@dataclass
class NarrativeAnalysis:
    """Complete narrative analysis of a TV show."""
    show_title: str
    structure_type: str  # "three-act", "episodic", "serialized"
    episode_structure: EpisodeStructure
    opening_convention: str
    closing_convention: str
    a_plot_pattern: str
    b_plot_patterns: List[str]
    recurring_devices: List[NarrativePattern]
    pacing_notes: str
    cliffhanger_usage: str
    seasonal_arc: Optional[str]
    unique_signatures: List[str]
    analyzed_at: datetime = field(default_factory=datetime.now)
    model_used: str = "claude-sonnet-4"
    confidence_score: float = 0.0


class NarrativeAnalyzer:
    """
    Analyzes narrative structures and storytelling patterns using AI.
    
    Uses Claude Sonnet 4.5 to identify plot structures, recurring devices,
    and narrative conventions from TV show research data.
    """
    
    def __init__(
        self,
        claude_client: Optional[ClaudeClient] = None,
        gpt_client: Optional[GPTClient] = None,
        database_manager=None
    ):
        """
        Initialize narrative analyzer.
        
        Args:
            claude_client: Claude AI client (primary)
            gpt_client: GPT-4 client (fallback)
            database_manager: Database manager for caching
        """
        self.claude_client = claude_client
        self.gpt_client = gpt_client
        self.db_manager = database_manager
        self.validator = AIResponseValidator()
    
    async def analyze_narrative(
        self,
        show_data: Dict,
        episode_data: Optional[List[Dict]] = None
    ) -> Optional[NarrativeAnalysis]:
        """
        Analyze narrative structure of a TV show.
        
        Args:
            show_data: Research data from Wikipedia, TMDB, IMDB
            episode_data: Optional episode guide data
            
        Returns:
            NarrativeAnalysis with complete structural analysis
            
        Example:
            >>> analyzer = NarrativeAnalyzer(claude_client, db_manager)
            >>> analysis = await analyzer.analyze_narrative(lucy_data)
            >>> print(f"Structure: {analysis.structure_type}")
            >>> print(f"Devices: {len(analysis.recurring_devices)}")
        """
        logger.info(f"Analyzing narrative structure: {show_data.get('title')}")
        
        # Check cache
        cached = await self._get_from_cache(show_data.get('title'))
        if cached:
            logger.info("Using cached narrative analysis")
            return cached
        
        # Build analysis prompt
        prompt = self._build_narrative_prompt(show_data, episode_data)
        
        # Get AI analysis with retry
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Try Claude first
                if self.claude_client:
                    response = await self._analyze_with_claude(prompt, attempt)
                    if response:
                        logger.info(f"Narrative analysis complete (Claude, attempt {attempt + 1})")
                        await self._save_to_cache(show_data.get('title'), response)
                        return response
                
                # Fallback to GPT-4
                if self.gpt_client:
                    response = await self._analyze_with_gpt(prompt, attempt)
                    if response:
                        logger.info(f"Narrative analysis complete (GPT-4, attempt {attempt + 1})")
                        await self._save_to_cache(show_data.get('title'), response)
                        return response
                
            except Exception as e:
                logger.error(f"Narrative analysis error (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    raise
        
        logger.error("Narrative analysis failed after all retries")
        return None
    
    def _build_narrative_prompt(
        self,
        show_data: Dict,
        episode_data: Optional[List[Dict]] = None
    ) -> str:
        """
        Build comprehensive prompt for narrative analysis.
        
        Args:
            show_data: Research data about the show
            episode_data: Optional episode information
            
        Returns:
            Detailed prompt for AI analysis
        """
        prompt = f"""Analyze the narrative structure and storytelling patterns of the TV show "{show_data.get('title')}".

## SHOW INFORMATION

**Title:** {show_data.get('title')}
**Years:** {show_data.get('years', 'Unknown')}
**Network:** {show_data.get('network', 'Unknown')}
**Genre:** {', '.join(show_data.get('genre', []))}
**Episodes:** {show_data.get('episode_count', 'Unknown')}
**Seasons:** {show_data.get('season_count', 'Unknown')}

**Premise:**
{show_data.get('premise', show_data.get('plot_summary', 'No premise available'))}

**Setting:** {show_data.get('setting', 'Unknown')}

**Themes:** {', '.join(show_data.get('themes', []))}

**Cultural Impact:**
{show_data.get('cultural_impact', 'Not available')}

"""
        
        if episode_data:
            prompt += f"\n**Episode Data Available:** {len(episode_data)} episodes\n"
        
        prompt += """
## ANALYSIS REQUIREMENTS

Provide a comprehensive narrative structure analysis including:

1. **Plot Structure Type**
   - Identify: three-act, episodic, serialized, anthology, or hybrid
   - Explain the structural pattern and why it fits

2. **Episode Structure**
   - Typical runtime (e.g., 22 minutes for sitcom, 48 for drama)
   - Number of acts (usually 2-4)
   - Act lengths in minutes
   - Commercial break count
   - Opening sequence length (seconds)
   - Closing sequence length (seconds)

3. **Opening Convention**
   - How does each episode typically open?
   - Cold open? Recap? Theme song? Direct into story?
   - Purpose and style

4. **Closing Convention**
   - How do episodes end?
   - Tag scene? Cliffhanger? Resolution? Credits gag?
   - Typical emotional tone

5. **A-Plot Pattern**
   - What is the typical main story structure?
   - Setup-complication-resolution beats
   - Character focus patterns

6. **B-Plot Patterns**
   - Are there typically subplots?
   - How do they relate to A-plot?
   - Common B-plot themes or character combinations

7. **Recurring Narrative Devices** (at least 3-7)
   - Identify recurring storytelling techniques
   - Examples: "misunderstanding cascade", "scheme backfires", "fish out of water"
   - For each device provide:
     - Name
     - Description
     - Frequency (every episode, weekly, occasional)
     - 2-3 specific examples
     - Narrative purpose

8. **Pacing Notes**
   - Fast or slow paced?
   - Where are the energy peaks?
   - How is tension built and released?

9. **Cliffhanger Usage**
   - Does the show use cliffhangers?
   - Episode-level or season-level?
   - Style and purpose

10. **Seasonal Arc** (if applicable)
    - Is there serialization across seasons?
    - Recurring seasonal themes or patterns?

11. **Unique Narrative Signatures** (3-5)
    - What storytelling techniques are unique to this show?
    - Signature moves that define the show's narrative style

## OUTPUT FORMAT

Return ONLY a valid JSON object matching this structure:

```json
{
  "show_title": "Show Name",
  "plot_structure": {
    "structure_type": "episodic",
    "act_breakdown": {
      "act_1": "Setup and complication",
      "act_2": "Escalation and climax",
      "act_3": "Resolution and tag"
    },
    "typical_runtime": 22
  },
  "recurring_devices": [
    {
      "device_name": "Scheme Backfires",
      "description": "Lucy devises a plan to get what she wants, but it spectacularly backfires",
      "frequency": "every episode",
      "examples": ["Vitameatavegamin", "Candy factory", "Grape stomping"]
    }
  ],
  "opening_convention": "Description of how episodes open",
  "closing_convention": "Description of how episodes end",
  "b_plot_patterns": ["Pattern 1", "Pattern 2"],
  "pacing_notes": "Fast-paced with physical comedy peaks",
  "unique_signatures": ["Signature 1", "Signature 2"]
}
```

CRITICAL:
- Return ONLY valid JSON, no markdown, no extra text
- Include all required fields
- Be specific with examples from the show
- Base analysis on the show information provided
- If information is limited, make educated inferences based on genre and era conventions
"""
        
        return prompt
    
    async def _analyze_with_claude(
        self,
        prompt: str,
        attempt: int
    ) -> Optional[NarrativeAnalysis]:
        """Analyze narrative using Claude Sonnet 4.5."""
        
        try:
            # Add retry guidance to prompt
            if attempt > 0:
                prompt += f"\n\nIMPORTANT: Previous attempt had validation errors. Ensure all required fields are present and properly formatted."
            
            # Call Claude
            response_text = await self.claude_client.generate(
                prompt=prompt,
                system="You are an expert TV narrative analyst. Return ONLY valid JSON.",
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse JSON
            response_json = json.loads(response_text)
            
            # Validate
            validated = self.validator.validate_narrative_analysis(response_json)
            
            if not validated:
                logger.warning("Claude response failed validation")
                return None
            
            # Convert to NarrativeAnalysis
            return self._build_narrative_analysis(validated, "claude-sonnet-4")
            
        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return None
    
    async def _analyze_with_gpt(
        self,
        prompt: str,
        attempt: int
    ) -> Optional[NarrativeAnalysis]:
        """Analyze narrative using GPT-4 (fallback)."""
        
        try:
            if attempt > 0:
                prompt += f"\n\nIMPORTANT: Previous attempt had validation errors. Ensure all required fields are present."
            
            response_text = await self.gpt_client.generate(
                prompt=prompt,
                system="You are an expert TV narrative analyst. Return ONLY valid JSON.",
                temperature=0.3,
                max_tokens=3000
            )
            
            response_json = json.loads(response_text)
            validated = self.validator.validate_narrative_analysis(response_json)
            
            if not validated:
                logger.warning("GPT-4 response failed validation")
                return None
            
            return self._build_narrative_analysis(validated, "gpt-4-turbo")
            
        except json.JSONDecodeError as e:
            logger.error(f"GPT-4 returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"GPT-4 analysis error: {e}")
            return None
    
    def _build_narrative_analysis(
        self,
        validated_response: NarrativeAnalysisResponse,
        model: str
    ) -> NarrativeAnalysis:
        """Build NarrativeAnalysis from validated response."""
        
        # Extract episode structure
        plot_structure = validated_response.plot_structure
        episode_structure = EpisodeStructure(
            total_runtime=plot_structure.typical_runtime or 30,
            act_count=len(plot_structure.act_breakdown),
            act_lengths=[10, 12, 8],  # Default for 3-act
            commercial_breaks=2,
            opening_length=30,
            closing_length=15
        )
        
        # Convert recurring devices
        recurring_devices = [
            NarrativePattern(
                pattern_name=device.device_name,
                description=device.description,
                frequency=device.frequency,
                examples=device.examples,
                purpose="Comedic/narrative device"
            )
            for device in validated_response.recurring_devices
        ]
        
        # Build analysis
        return NarrativeAnalysis(
            show_title=validated_response.show_title,
            structure_type=plot_structure.structure_type,
            episode_structure=episode_structure,
            opening_convention=validated_response.opening_convention or "Standard opening",
            closing_convention=validated_response.closing_convention or "Standard closing",
            a_plot_pattern="Main storyline follows protagonist",
            b_plot_patterns=validated_response.b_plot_patterns,
            recurring_devices=recurring_devices,
            pacing_notes=validated_response.pacing_notes or "Standard pacing",
            cliffhanger_usage="Minimal for episodic format",
            seasonal_arc=None,
            unique_signatures=validated_response.unique_signatures,
            model_used=model,
            confidence_score=0.85
        )
    
    async def _get_from_cache(self, show_title: str) -> Optional[NarrativeAnalysis]:
        """Get cached narrative analysis from MongoDB."""
        if not self.db_manager:
            return None
        
        try:
            result = await self.db_manager.mongodb['ai_analysis'].find_one({
                'show_title': show_title,
                'analysis_type': 'narrative',
                'expires_at': {'$gt': datetime.now()}
            })
            
            if result:
                # Reconstruct NarrativeAnalysis from cached data
                return self._deserialize_analysis(result['output_data'])
            
        except Exception as e:
            logger.error(f"Cache read error: {e}")
        
        return None
    
    async def _save_to_cache(self, show_title: str, analysis: NarrativeAnalysis):
        """Save narrative analysis to MongoDB cache."""
        if not self.db_manager:
            return
        
        try:
            from datetime import timedelta
            
            cache_doc = {
                'show_title': show_title,
                'analysis_type': 'narrative',
                'model': analysis.model_used,
                'output_data': self._serialize_analysis(analysis),
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(days=30)
            }
            
            await self.db_manager.mongodb['ai_analysis'].update_one(
                {'show_title': show_title, 'analysis_type': 'narrative'},
                {'$set': cache_doc},
                upsert=True
            )
            
            logger.info(f"Cached narrative analysis for {show_title}")
            
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def _serialize_analysis(self, analysis: NarrativeAnalysis) -> Dict:
        """Convert NarrativeAnalysis to dict for caching."""
        return {
            'show_title': analysis.show_title,
            'structure_type': analysis.structure_type,
            'episode_structure': {
                'total_runtime': analysis.episode_structure.total_runtime,
                'act_count': analysis.episode_structure.act_count,
                'act_lengths': analysis.episode_structure.act_lengths,
                'commercial_breaks': analysis.episode_structure.commercial_breaks,
                'opening_length': analysis.episode_structure.opening_length,
                'closing_length': analysis.episode_structure.closing_length
            },
            'opening_convention': analysis.opening_convention,
            'closing_convention': analysis.closing_convention,
            'a_plot_pattern': analysis.a_plot_pattern,
            'b_plot_patterns': analysis.b_plot_patterns,
            'recurring_devices': [
                {
                    'pattern_name': d.pattern_name,
                    'description': d.description,
                    'frequency': d.frequency,
                    'examples': d.examples,
                    'purpose': d.purpose
                }
                for d in analysis.recurring_devices
            ],
            'pacing_notes': analysis.pacing_notes,
            'cliffhanger_usage': analysis.cliffhanger_usage,
            'seasonal_arc': analysis.seasonal_arc,
            'unique_signatures': analysis.unique_signatures,
            'confidence_score': analysis.confidence_score
        }
    
    def _deserialize_analysis(self, data: Dict) -> NarrativeAnalysis:
        """Convert cached dict to NarrativeAnalysis."""
        episode_structure = EpisodeStructure(**data['episode_structure'])
        
        recurring_devices = [
            NarrativePattern(**device)
            for device in data['recurring_devices']
        ]
        
        return NarrativeAnalysis(
            show_title=data['show_title'],
            structure_type=data['structure_type'],
            episode_structure=episode_structure,
            opening_convention=data['opening_convention'],
            closing_convention=data['closing_convention'],
            a_plot_pattern=data['a_plot_pattern'],
            b_plot_patterns=data['b_plot_patterns'],
            recurring_devices=recurring_devices,
            pacing_notes=data['pacing_notes'],
            cliffhanger_usage=data['cliffhanger_usage'],
            seasonal_arc=data.get('seasonal_arc'),
            unique_signatures=data['unique_signatures'],
            confidence_score=data.get('confidence_score', 0.0)
        )


# Example usage
async def main():
    """Example usage of narrative analyzer."""
    from src.services.creative.claude_client import ClaudeClient
    from src.services.database.database_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    claude_client = ClaudeClient()
    
    analyzer = NarrativeAnalyzer(
        claude_client=claude_client,
        database_manager=db_manager
    )
    
    # Sample show data
    show_data = {
        'title': 'I Love Lucy',
        'years': '1951-1957',
        'network': 'CBS',
        'genre': ['Sitcom', 'Comedy'],
        'episode_count': 180,
        'season_count': 6,
        'premise': 'A wacky redhead schemes to break into show business while her Cuban bandleader husband tries to keep her grounded.',
        'setting': '1950s New York',
        'themes': ['Marriage', 'Ambition', 'Comedy', 'Show Business']
    }
    
    analysis = await analyzer.analyze_narrative(show_data)
    
    if analysis:
        print(f"Structure Type: {analysis.structure_type}")
        print(f"Recurring Devices: {len(analysis.recurring_devices)}")
        for device in analysis.recurring_devices:
            print(f"  - {device.pattern_name}: {device.frequency}")
        print(f"Opening: {analysis.opening_convention}")
        print(f"Closing: {analysis.closing_convention}")
    
    await db_manager.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



