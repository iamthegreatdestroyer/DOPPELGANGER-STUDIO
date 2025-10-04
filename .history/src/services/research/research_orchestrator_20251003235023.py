"""
Research Orchestrator - Coordinate multiple data sources for comprehensive TV show research.

This module manages the research workflow, merging data from Wikipedia, TMDB,
and other sources into a unified research profile.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime

from .wikipedia_scraper import WikipediaResearchScraper, WikipediaShowData
from .tmdb_scraper import TMDBResearchScraper, TMDBShowData

logger = logging.getLogger(__name__)


@dataclass
class UnifiedShowResearch:
    """Merged research data from multiple sources."""
    title: str
    years: str
    
    # Basic Information
    network: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    creators: List[str] = field(default_factory=list)
    setting: Optional[str] = None
    
    # Content Information
    premise: Optional[str] = None
    plot_summary: Optional[str] = None
    themes: List[str] = field(default_factory=list)
    
    # Production Information
    episode_count: Optional[int] = None
    season_count: Optional[int] = None
    status: Optional[str] = None
    
    # Cast & Characters
    main_characters: List[Dict] = field(default_factory=list)
    cast: List[Dict] = field(default_factory=list)
    
    # Reception
    cultural_impact: Optional[str] = None
    critical_reception: Optional[str] = None
    rating: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None
    
    # Media
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    
    # Metadata
    sources: List[str] = field(default_factory=list)
    tmdb_id: Optional[int] = None
    wikipedia_url: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    
    # Confidence scores (0-1)
    data_completeness: float = 0.0
    source_agreement: float = 0.0


class ResearchOrchestrator:
    """
    Orchestrates research from multiple sources and merges results intelligently.
    
    Features:
    - Parallel scraping from multiple sources
    - Intelligent data merging with conflict resolution
    - Data quality scoring and validation
    - Fallback mechanisms for failed sources
    """
    
    def __init__(self, tmdb_api_key: Optional[str] = None):
        """
        Initialize research orchestrator.
        
        Args:
            tmdb_api_key: Optional TMDB API key for enhanced data
        """
        self.tmdb_api_key = tmdb_api_key
    
    async def research_show(self, show_title: str) -> UnifiedShowResearch:
        """
        Perform comprehensive research on a TV show.
        
        Args:
            show_title: Name of the TV show
            
        Returns:
            UnifiedShowResearch with merged data from all sources
            
        Example:
            >>> orchestrator = ResearchOrchestrator(tmdb_api_key="key")
            >>> research = await orchestrator.research_show("I Love Lucy")
            >>> print(f"Completeness: {research.data_completeness:.0%}")
        """
        logger.info(f"Starting comprehensive research: {show_title}")
        
        # Gather data from all available sources in parallel
        results = await self._gather_all_sources(show_title)
        
        # Merge data intelligently
        merged = await self._merge_research_data(show_title, results)
        
        # Calculate quality metrics
        merged.data_completeness = self._calculate_completeness(merged)
        merged.source_agreement = self._calculate_agreement(results)
        
        logger.info(
            f"Research complete: {merged.title} "
            f"({len(merged.sources)} sources, "
            f"{merged.data_completeness:.0%} complete)"
        )
        
        return merged
    
    async def _gather_all_sources(
        self,
        show_title: str
    ) -> Dict[str, Optional[object]]:
        """Gather data from all sources in parallel."""
        results = {}
        
        # Wikipedia
        try:
            async with WikipediaResearchScraper() as wiki_scraper:
                results['wikipedia'] = await wiki_scraper.research_show(show_title)
                logger.info("Wikipedia research successful")
        except Exception as e:
            logger.error(f"Wikipedia research failed: {e}")
            results['wikipedia'] = None
        
        # TMDB
        if self.tmdb_api_key:
            try:
                async with TMDBResearchScraper(self.tmdb_api_key) as tmdb_scraper:
                    results['tmdb'] = await tmdb_scraper.research_show(show_title)
                    logger.info("TMDB research successful")
            except Exception as e:
                logger.error(f"TMDB research failed: {e}")
                results['tmdb'] = None
        else:
            logger.warning("TMDB API key not provided, skipping TMDB research")
            results['tmdb'] = None
        
        return results
    
    async def _merge_research_data(
        self,
        show_title: str,
        results: Dict[str, Optional[object]]
    ) -> UnifiedShowResearch:
        """Merge data from multiple sources intelligently."""
        wiki_data: Optional[WikipediaShowData] = results.get('wikipedia')
        tmdb_data: Optional[TMDBShowData] = results.get('tmdb')
        
        # Determine primary title
        title = self._merge_titles(show_title, wiki_data, tmdb_data)
        
        # Build merged object
        merged = UnifiedShowResearch(
            title=title,
            years=self._merge_years(wiki_data, tmdb_data),
            network=self._merge_network(wiki_data, tmdb_data),
            genres=self._merge_genres(wiki_data, tmdb_data),
            creators=self._merge_creators(wiki_data, tmdb_data),
            setting=wiki_data.setting if wiki_data else None,
            premise=self._merge_premise(wiki_data, tmdb_data),
            plot_summary=wiki_data.plot_summary if wiki_data else None,
            themes=wiki_data.themes if wiki_data else [],
            episode_count=self._merge_episode_count(wiki_data, tmdb_data),
            season_count=self._merge_season_count(wiki_data, tmdb_data),
            status=tmdb_data.status if tmdb_data else None,
            main_characters=wiki_data.main_characters if wiki_data else [],
            cast=self._merge_cast(wiki_data, tmdb_data),
            cultural_impact=wiki_data.cultural_impact if wiki_data else None,
            critical_reception=wiki_data.critical_reception if wiki_data else None,
            rating=tmdb_data.vote_average if tmdb_data else None,
            vote_count=tmdb_data.vote_count if tmdb_data else None,
            popularity=tmdb_data.popularity if tmdb_data else None,
            poster_url=tmdb_data.poster_path if tmdb_data else None,
            backdrop_url=tmdb_data.backdrop_path if tmdb_data else None,
            sources=self._get_successful_sources(results),
            tmdb_id=tmdb_data.tmdb_id if tmdb_data else None,
            wikipedia_url=wiki_data.source_url if wiki_data else None
        )
        
        return merged
    
    def _merge_titles(
        self,
        original: str,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> str:
        """Merge titles from multiple sources."""
        if tmdb_data and tmdb_data.title:
            return tmdb_data.title
        if wiki_data and wiki_data.title:
            return wiki_data.title
        return original
    
    def _merge_years(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> str:
        """Merge year information."""
        if wiki_data and wiki_data.years != "Unknown":
            return wiki_data.years
        if tmdb_data and tmdb_data.first_air_date:
            year = tmdb_data.first_air_date[:4]
            if tmdb_data.last_air_date:
                end_year = tmdb_data.last_air_date[:4]
                return f"{year}-{end_year}"
            return year
        return "Unknown"
    
    def _merge_network(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> Optional[str]:
        """Merge network information."""
        if wiki_data and wiki_data.network:
            return wiki_data.network
        if tmdb_data and tmdb_data.networks:
            return tmdb_data.networks[0]
        return None
    
    def _merge_genres(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> List[str]:
        """Merge genre information."""
        genres = set()
        
        if wiki_data and wiki_data.genre:
            genres.update(wiki_data.genre)
        
        if tmdb_data and tmdb_data.genres:
            genres.update(tmdb_data.genres)
        
        return list(genres)
    
    def _merge_creators(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> List[str]:
        """Merge creator information."""
        creators = set()
        
        if wiki_data and wiki_data.creators:
            creators.update(wiki_data.creators)
        
        if tmdb_data and tmdb_data.creators:
            creators.update(c['name'] for c in tmdb_data.creators)
        
        return list(creators)
    
    def _merge_premise(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> Optional[str]:
        """Merge premise/overview."""
        # Prefer longer, more detailed version
        wiki_premise = wiki_data.premise if wiki_data else None
        tmdb_overview = tmdb_data.overview if tmdb_data else None
        
        if not wiki_premise:
            return tmdb_overview
        if not tmdb_overview:
            return wiki_premise
        
        # Return longer version
        return wiki_premise if len(wiki_premise) > len(tmdb_overview) else tmdb_overview
    
    def _merge_episode_count(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> Optional[int]:
        """Merge episode count."""
        # Prefer TMDB (more accurate)
        if tmdb_data and tmdb_data.episode_count:
            return tmdb_data.episode_count
        if wiki_data and wiki_data.episode_count:
            return wiki_data.episode_count
        return None
    
    def _merge_season_count(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> Optional[int]:
        """Merge season count."""
        # Prefer TMDB (more accurate)
        if tmdb_data and tmdb_data.season_count:
            return tmdb_data.season_count
        if wiki_data and wiki_data.season_count:
            return wiki_data.season_count
        return None
    
    def _merge_cast(
        self,
        wiki_data: Optional[WikipediaShowData],
        tmdb_data: Optional[TMDBShowData]
    ) -> List[Dict]:
        """Merge cast information."""
        # Prefer TMDB cast (more structured)
        if tmdb_data and tmdb_data.cast:
            return tmdb_data.cast
        if wiki_data and wiki_data.cast:
            return wiki_data.cast
        return []
    
    def _get_successful_sources(
        self,
        results: Dict[str, Optional[object]]
    ) -> List[str]:
        """Get list of sources that returned data."""
        return [
            source
            for source, data in results.items()
            if data is not None
        ]
    
    def _calculate_completeness(self, merged: UnifiedShowResearch) -> float:
        """Calculate data completeness score (0-1)."""
        # Define key fields and their weights
        fields = {
            'title': 1.0,
            'years': 0.8,
            'network': 0.5,
            'genres': 0.5,
            'premise': 0.8,
            'episode_count': 0.5,
            'season_count': 0.5,
            'main_characters': 0.7,
            'cast': 0.6,
        }
        
        total_weight = sum(fields.values())
        earned_weight = 0.0
        
        for field, weight in fields.items():
            value = getattr(merged, field, None)
            if value:
                # Check if it's a list
                if isinstance(value, list):
                    if len(value) > 0:
                        earned_weight += weight
                else:
                    earned_weight += weight
        
        return earned_weight / total_weight if total_weight > 0 else 0.0
    
    def _calculate_agreement(
        self,
        results: Dict[str, Optional[object]]
    ) -> float:
        """Calculate source agreement score (0-1)."""
        # Simplified: just check if multiple sources returned data
        successful_sources = sum(1 for data in results.values() if data is not None)
        
        if successful_sources == 0:
            return 0.0
        elif successful_sources == 1:
            return 0.5  # Only one source, no way to verify
        else:
            return 1.0  # Multiple sources agree show exists


# Example usage
async def main():
    """Example usage of research orchestrator."""
    import os
    
    tmdb_key = os.getenv('TMDB_API_KEY')
    
    orchestrator = ResearchOrchestrator(tmdb_api_key=tmdb_key)
    research = await orchestrator.research_show("I Love Lucy")
    
    print(f"Title: {research.title}")
    print(f"Years: {research.years}")
    print(f"Network: {research.network}")
    print(f"Genres: {', '.join(research.genres)}")
    print(f"Seasons: {research.season_count}, Episodes: {research.episode_count}")
    print(f"Rating: {research.rating}/10" if research.rating else "Rating: N/A")
    print(f"\nSources: {', '.join(research.sources)}")
    print(f"Data Completeness: {research.data_completeness:.0%}")
    print(f"Source Agreement: {research.source_agreement:.0%}")


if __name__ == "__main__":
    asyncio.run(main())
