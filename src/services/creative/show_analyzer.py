"""
Show Analyzer - Unified orchestrator for complete TV show analysis.

Coordinates Research, Character, Narrative, and Transformation systems
to perform comprehensive analysis of classic TV shows.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio

from src.services.research.research_orchestrator import ResearchOrchestrator
from src.services.creative.character_analyzer import CharacterAnalyzer
from src.services.creative.narrative_analyzer import NarrativeAnalyzer
from src.services.creative.transformation_engine import TransformationEngine

logger = logging.getLogger(__name__)


@dataclass
class AnalysisProgress:
    """Track analysis progress."""
    total_steps: int = 4
    completed_steps: int = 0
    current_step: str = ""
    research_complete: bool = False
    character_analysis_complete: bool = False
    narrative_analysis_complete: bool = False
    transformation_complete: bool = False
    errors: List[str] = field(default_factory=list)


@dataclass
class CompleteShowAnalysis:
    """Complete analysis results for a TV show."""
    show_title: str
    research_data: Dict
    character_analyses: List[Dict]
    narrative_analysis: Optional[Dict]
    transformation_rules: Optional[Dict]
    completeness_score: float
    analysis_time_seconds: float
    generated_at: datetime = field(default_factory=datetime.now)


class ShowAnalyzer:
    """
    Unified orchestrator for complete TV show analysis.
    
    Coordinates all analysis systems to transform classic TV shows
    into modern parody specifications.
    """
    
    def __init__(
        self,
        research_orchestrator: ResearchOrchestrator,
        character_analyzer: CharacterAnalyzer,
        narrative_analyzer: NarrativeAnalyzer,
        transformation_engine: TransformationEngine,
        database_manager=None
    ):
        """
        Initialize show analyzer with all component systems.
        
        Args:
            research_orchestrator: Research system
            character_analyzer: Character analysis system
            narrative_analyzer: Narrative analysis system
            transformation_engine: Transformation system
            database_manager: Database for caching results
        """
        self.research = research_orchestrator
        self.character_analyzer = character_analyzer
        self.narrative_analyzer = narrative_analyzer
        self.transformer = transformation_engine
        self.db_manager = database_manager
    
    async def analyze_show(
        self,
        show_title: str,
        tmdb_id: Optional[int] = None,
        imdb_id: Optional[str] = None,
        progress_callback=None
    ) -> CompleteShowAnalysis:
        """
        Perform complete analysis of a TV show.
        
        Args:
            show_title: Name of the TV show
            tmdb_id: Optional TMDB ID if known
            imdb_id: Optional IMDB ID if known
            progress_callback: Optional async callback(progress: AnalysisProgress)
            
        Returns:
            CompleteShowAnalysis with all results
            
        Example:
            >>> analyzer = ShowAnalyzer(research, char_analyzer, ...)
            >>> analysis = await analyzer.analyze_show("I Love Lucy")
            >>> print(f"Completeness: {analysis.completeness_score * 100}%")
            >>> print(f"Modern premise: {analysis.transformation_rules['modern_premise']}")
        """
        logger.info(f"Starting complete analysis: {show_title}")
        start_time = datetime.now()
        
        progress = AnalysisProgress()
        
        # Step 1: Research
        progress.current_step = "Researching show data"
        if progress_callback:
            await progress_callback(progress)
        
        research_data = await self._research_show(
            show_title, 
            tmdb_id, 
            imdb_id,
            progress
        )
        
        progress.research_complete = True
        progress.completed_steps += 1
        if progress_callback:
            await progress_callback(progress)
        
        # Step 2: Character Analysis
        progress.current_step = "Analyzing characters"
        if progress_callback:
            await progress_callback(progress)
        
        character_analyses = await self._analyze_characters(
            research_data,
            progress
        )
        
        progress.character_analysis_complete = True
        progress.completed_steps += 1
        if progress_callback:
            await progress_callback(progress)
        
        # Step 3: Narrative Analysis
        progress.current_step = "Analyzing narrative structure"
        if progress_callback:
            await progress_callback(progress)
        
        narrative_analysis = await self._analyze_narrative(
            research_data,
            progress
        )
        
        progress.narrative_analysis_complete = True
        progress.completed_steps += 1
        if progress_callback:
            await progress_callback(progress)
        
        # Step 4: Transformation Rules
        progress.current_step = "Generating transformation rules"
        if progress_callback:
            await progress_callback(progress)
        
        transformation_rules = await self._generate_transformations(
            research_data,
            character_analyses,
            narrative_analysis,
            progress
        )
        
        progress.transformation_complete = True
        progress.completed_steps += 1
        if progress_callback:
            await progress_callback(progress)
        
        # Calculate completeness
        completeness = self._calculate_completeness(
            research_data,
            character_analyses,
            narrative_analysis,
            transformation_rules
        )
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        # Build complete analysis
        complete_analysis = CompleteShowAnalysis(
            show_title=show_title,
            research_data=research_data,
            character_analyses=character_analyses,
            narrative_analysis=narrative_analysis,
            transformation_rules=transformation_rules,
            completeness_score=completeness,
            analysis_time_seconds=analysis_time
        )
        
        # Cache complete analysis
        if self.db_manager:
            await self._cache_analysis(complete_analysis)
        
        logger.info(f"Analysis complete in {analysis_time:.1f}s - "
                   f"Completeness: {completeness * 100:.1f}%")
        
        return complete_analysis
    
    async def _research_show(
        self,
        show_title: str,
        tmdb_id: Optional[int],
        imdb_id: Optional[str],
        progress: AnalysisProgress
    ) -> Dict:
        """Research show from all sources."""
        try:
            research_data = await self.research.research_show(
                show_title=show_title,
                tmdb_id=tmdb_id,
                imdb_id=imdb_id
            )
            
            logger.info(f"Research complete: {research_data.get('completeness_score', 0) * 100}% data")
            return research_data
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            progress.errors.append(f"Research: {str(e)}")
            # Return minimal data to continue
            return {
                'title': show_title,
                'error': str(e)
            }
    
    async def _analyze_characters(
        self,
        research_data: Dict,
        progress: AnalysisProgress
    ) -> List[Dict]:
        """Analyze all main characters."""
        character_analyses = []
        
        characters = research_data.get('characters', [])
        if not characters:
            logger.warning("No characters found in research data")
            progress.errors.append("No characters to analyze")
            return []
        
        logger.info(f"Analyzing {len(characters)} characters")
        
        # Analyze characters in parallel (up to 3 at a time)
        semaphore = asyncio.Semaphore(3)
        
        async def analyze_one(character):
            async with semaphore:
                try:
                    analysis = await self.character_analyzer.analyze_character(
                        character_name=character.get('name', 'Unknown'),
                        character_data=character,
                        show_context=research_data
                    )
                    
                    if analysis:
                        # Convert Pydantic model to dict
                        return {
                            'character_name': analysis.character_name,
                            'core_traits': [
                                {
                                    'trait': t.trait,
                                    'description': t.description,
                                    'examples': t.examples
                                }
                                for t in analysis.core_traits
                            ],
                            'speech_patterns': analysis.speech_patterns,
                            'catchphrases': analysis.catchphrases,
                            'comedic_elements': analysis.comedic_elements
                        }
                    return None
                    
                except Exception as e:
                    logger.error(f"Character analysis failed for {character.get('name')}: {e}")
                    progress.errors.append(f"Character {character.get('name')}: {str(e)}")
                    return None
        
        # Analyze all characters
        results = await asyncio.gather(*[analyze_one(char) for char in characters])
        character_analyses = [r for r in results if r is not None]
        
        logger.info(f"Successfully analyzed {len(character_analyses)}/{len(characters)} characters")
        
        return character_analyses
    
    async def _analyze_narrative(
        self,
        research_data: Dict,
        progress: AnalysisProgress
    ) -> Optional[Dict]:
        """Analyze narrative structure."""
        try:
            narrative = await self.narrative_analyzer.analyze_narrative(
                show_data=research_data
            )
            
            if narrative:
                # Convert to dict
                return {
                    'structure_type': narrative.structure_type,
                    'opening_convention': narrative.opening_convention,
                    'closing_convention': narrative.closing_convention,
                    'recurring_devices': [
                        {
                            'pattern_name': d.pattern_name,
                            'description': d.description,
                            'frequency': d.frequency,
                            'examples': d.examples
                        }
                        for d in narrative.recurring_devices
                    ],
                    'pacing_notes': narrative.pacing_notes,
                    'unique_signatures': narrative.unique_signatures
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Narrative analysis failed: {e}")
            progress.errors.append(f"Narrative: {str(e)}")
            return None
    
    async def _generate_transformations(
        self,
        research_data: Dict,
        character_analyses: List[Dict],
        narrative_analysis: Optional[Dict],
        progress: AnalysisProgress
    ) -> Optional[Dict]:
        """Generate transformation rules."""
        try:
            rules = await self.transformer.generate_transformation_rules(
                show_data=research_data,
                character_analysis={'characters': character_analyses},
                narrative_analysis=narrative_analysis
            )
            
            if rules:
                # Convert to dict
                return {
                    'modern_premise': rules.modern_premise,
                    'setting': {
                        'original': rules.setting_transformation.original_location,
                        'modern': rules.setting_transformation.modern_location,
                        'justification': rules.setting_transformation.justification
                    },
                    'character_transformations': [
                        {
                            'original_name': ct.original_name,
                            'modern_occupation': ct.modern_occupation,
                            'motivation_shift': ct.motivation_shift,
                            'technology': ct.technology_integration
                        }
                        for ct in rules.character_transformations
                    ],
                    'humor_transformation': {
                        'original_style': rules.humor_transformation.original_style,
                        'modern_style': rules.humor_transformation.modern_style,
                        'device_mappings': rules.humor_transformation.device_mappings
                    },
                    'cultural_updates': rules.cultural_updates,
                    'technology_opportunities': rules.technology_opportunities
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            progress.errors.append(f"Transformation: {str(e)}")
            return None
    
    def _calculate_completeness(
        self,
        research_data: Dict,
        character_analyses: List[Dict],
        narrative_analysis: Optional[Dict],
        transformation_rules: Optional[Dict]
    ) -> float:
        """Calculate overall analysis completeness score."""
        score = 0.0
        
        # Research data (25%)
        if research_data and 'error' not in research_data:
            research_score = research_data.get('completeness_score', 0.5)
            score += 0.25 * research_score
        
        # Character analyses (25%)
        if character_analyses:
            char_score = len(character_analyses) / max(len(research_data.get('characters', [])), 1)
            score += 0.25 * min(char_score, 1.0)
        
        # Narrative analysis (25%)
        if narrative_analysis:
            score += 0.25
        
        # Transformation rules (25%)
        if transformation_rules:
            score += 0.25
        
        return min(score, 1.0)
    
    async def _cache_analysis(self, analysis: CompleteShowAnalysis):
        """Cache complete analysis in MongoDB."""
        if not self.db_manager:
            return
        
        try:
            cache_doc = {
                'show_title': analysis.show_title,
                'analysis_type': 'complete',
                'research_data': analysis.research_data,
                'character_analyses': analysis.character_analyses,
                'narrative_analysis': analysis.narrative_analysis,
                'transformation_rules': analysis.transformation_rules,
                'completeness_score': analysis.completeness_score,
                'analysis_time': analysis.analysis_time_seconds,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(days=30)
            }
            
            await self.db_manager.mongodb['ai_analysis'].update_one(
                {'show_title': analysis.show_title, 'analysis_type': 'complete'},
                {'$set': cache_doc},
                upsert=True
            )
            
            logger.info(f"Cached complete analysis for {analysis.show_title}")
            
        except Exception as e:
            logger.error(f"Cache write error: {e}")


# Example usage
async def main():
    """Example usage of show analyzer."""
    from src.services.research.research_orchestrator import ResearchOrchestrator
    from src.services.creative.character_analyzer import CharacterAnalyzer
    from src.services.creative.narrative_analyzer import NarrativeAnalyzer
    from src.services.creative.transformation_engine import TransformationEngine
    from src.services.database.database_manager import DatabaseManager
    from src.services.creative.claude_client import ClaudeClient
    
    # Initialize all components
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    claude_client = ClaudeClient()
    
    research = ResearchOrchestrator(db_manager)
    char_analyzer = CharacterAnalyzer(claude_client, None, db_manager)
    narrative_analyzer = NarrativeAnalyzer(claude_client, None, db_manager)
    transformer = TransformationEngine(claude_client, None, db_manager)
    
    # Create show analyzer
    analyzer = ShowAnalyzer(
        research_orchestrator=research,
        character_analyzer=char_analyzer,
        narrative_analyzer=narrative_analyzer,
        transformation_engine=transformer,
        database_manager=db_manager
    )
    
    # Progress callback
    async def on_progress(progress: AnalysisProgress):
        print(f"[{progress.completed_steps}/{progress.total_steps}] {progress.current_step}")
    
    # Analyze show
    analysis = await analyzer.analyze_show(
        show_title="I Love Lucy",
        tmdb_id=1668,
        imdb_id="tt0043208",
        progress_callback=on_progress
    )
    
    print(f"\n✅ Analysis Complete!")
    print(f"Completeness: {analysis.completeness_score * 100:.1f}%")
    print(f"Time: {analysis.analysis_time_seconds:.1f}s")
    print(f"Characters analyzed: {len(analysis.character_analyses)}")
    print(f"Modern premise: {analysis.transformation_rules.get('modern_premise', 'N/A')}")
    
    await db_manager.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

