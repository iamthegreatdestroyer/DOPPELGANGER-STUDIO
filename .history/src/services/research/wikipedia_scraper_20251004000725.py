"""
Wikipedia Research Scraper - Extract TV show data from Wikipedia.

This module scrapes Wikipedia for comprehensive TV show information including
plot summaries, character descriptions, episode guides, cultural context, and
production details.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import wikipediaapi
import logging
from dataclasses import dataclass, field
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class WikipediaShowData:
    """Container for Wikipedia-sourced show data."""
    title: str
    years: str
    network: Optional[str] = None
    genre: List[str] = field(default_factory=list)
    setting: Optional[str] = None
    premise: Optional[str] = None
    main_characters: List[Dict] = field(default_factory=list)
    plot_summary: Optional[str] = None
    cultural_impact: Optional[str] = None
    critical_reception: Optional[str] = None
    episode_count: Optional[int] = None
    season_count: Optional[int] = None
    creators: List[str] = field(default_factory=list)
    cast: List[Dict] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    notable_episodes: List[Dict] = field(default_factory=list)
    source_url: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


class WikipediaResearchScraper:
    """
    Scrapes Wikipedia for comprehensive TV show research data.
    
    Uses both the Wikipedia API and web scraping to gather:
    - Basic show information (years, network, creators)
    - Plot summaries and premise
    - Character descriptions and relationships
    - Episode guides and notable episodes
    - Cultural context and critical reception
    - Themes and storytelling patterns
    """
    
    def __init__(self, user_agent: str = "DoppelgangerStudio/0.1"):
        """
        Initialize Wikipedia scraper.
        
        Args:
            user_agent: Custom user agent for Wikipedia API
        """
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent=user_agent
        )
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def research_show(self, show_title: str) -> WikipediaShowData:
        """
        Comprehensive research on a TV show from Wikipedia.
        
        Args:
            show_title: Name of the TV show
            
        Returns:
            WikipediaShowData with all extracted information
            
        Example:
            >>> async with WikipediaResearchScraper() as scraper:
            ...     data = await scraper.research_show("I Love Lucy")
            ...     print(f"Found {len(data.main_characters)} characters")
        """
        logger.info(f"Researching show: {show_title}")
        
        # Get Wikipedia page
        page = self.wiki.page(show_title)
        
        if not page.exists():
            # Try variations
            page = await self._find_page_variations(show_title)
            if not page or not page.exists():
                raise ValueError(f"Wikipedia page not found for: {show_title}")
        
        logger.info(f"Found Wikipedia page: {page.title}")
        
        # Extract data using multiple methods
        data = WikipediaShowData(
            title=page.title,
            years=await self._extract_years(page),
            source_url=page.fullurl
        )
        
        # Parallel extraction for speed
        tasks = [
            self._extract_basic_info(page, data),
            self._extract_characters(page, data),
            self._extract_plot_info(page, data),
            self._extract_production_info(page, data),
            self._extract_themes(page, data),
            self._extract_episodes(page, data)
        ]
        
        await asyncio.gather(*tasks)
        
        logger.info(f"Research complete: {data.title}")
        logger.debug(
            f"Extracted {len(data.main_characters)} characters, "
            f"{len(data.themes)} themes"
        )
        
        return data
    
    async def _find_page_variations(
        self,
        title: str
    ) -> Optional[wikipediaapi.WikipediaPage]:
        """Try different title variations to find the page."""
        variations = [
            f"{title} (TV series)",
            f"{title} (American TV series)",
            f"The {title}",
            f"The {title} (TV series)",
            title.replace("'", "'"),  # Different apostrophe types
        ]
        
        for variation in variations:
            page = self.wiki.page(variation)
            if page.exists():
                logger.info(f"Found via variation: {variation}")
                return page
        
        return None
    
    async def _extract_years(self, page: wikipediaapi.WikipediaPage) -> str:
        """Extract years the show aired."""
        text = page.summary[:500]  # Check first paragraph
        
        # Pattern: (YYYY-YYYY) or YYYY-YYYY
        pattern = r'\(?(\d{4})[–-](\d{4})\)?'
        match = re.search(pattern, text)
        
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        
        # Pattern: Single year (YYYY)
        pattern = r'\(?(\d{4})\)?'
        match = re.search(pattern, text)
        
        if match:
            return match.group(1)
        
        return "Unknown"
    
    async def _extract_basic_info(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaShowData
    ):
        """Extract basic show information."""
        # Parse infobox if available (requires HTML scraping)
        if self.session:
            infobox = await self._scrape_infobox(page.fullurl)
            if infobox:
                data.network = infobox.get('network')
                data.genre = infobox.get('genre', [])
                data.creators = infobox.get('creators', [])
                data.episode_count = infobox.get('episodes')
                data.season_count = infobox.get('seasons')
        
        # Extract from summary
        data.premise = page.summary[:500] if page.summary else None
    
    async def _scrape_infobox(self, url: str) -> Optional[Dict]:
        """Scrape Wikipedia infobox for structured data."""
        if not self.session:
            return None
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                infobox = soup.find('table', class_='infobox')
                if not infobox:
                    return None
                
                data = {}
                
                # Extract network
                network_row = infobox.find('th', string='Network')
                if network_row:
                    network_cell = network_row.find_next('td')
                    if network_cell:
                        data['network'] = network_cell.get_text(strip=True)
                
                # Extract genre
                genre_row = infobox.find('th', string='Genre')
                if genre_row:
                    genre_cell = genre_row.find_next('td')
                    if genre_cell:
                        genres = [
                            g.strip()
                            for g in genre_cell.get_text().split('\n')
                            if g.strip()
                        ]
                        data['genre'] = genres
                
                # Extract creators
                creator_row = infobox.find('th', string='Created by')
                if creator_row:
                    creator_cell = creator_row.find_next('td')
                    if creator_cell:
                        creators = [
                            c.strip()
                            for c in creator_cell.get_text().split('\n')
                            if c.strip()
                        ]
                        data['creators'] = creators
                
                # Extract episode count
                episode_row = infobox.find('th', string='No. of episodes')
                if episode_row:
                    episode_cell = episode_row.find_next('td')
                    if episode_cell:
                        episode_text = episode_cell.get_text(strip=True)
                        match = re.search(r'(\d+)', episode_text)
                        if match:
                            data['episodes'] = int(match.group(1))
                
                # Extract season count
                season_row = infobox.find('th', string='No. of seasons')
                if season_row:
                    season_cell = season_row.find_next('td')
                    if season_cell:
                        season_text = season_cell.get_text(strip=True)
                        match = re.search(r'(\d+)', season_text)
                        if match:
                            data['seasons'] = int(match.group(1))
                
                return data
                
        except Exception as e:
            logger.error(f"Infobox scraping failed: {e}")
            return None
    
    async def _extract_characters(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaShowData
    ):
        """Extract main character information."""
        # Look for "Characters" or "Cast" sections
        sections_to_check = [
            'Characters',
            'Cast and characters',
            'Main characters',
            'Cast'
        ]
        
        for section_name in sections_to_check:
            section = self._find_section(page, section_name)
            if section:
                characters = await self._parse_character_section(section)
                if characters:
                    data.main_characters = characters
                    break
    
    def _find_section(
        self,
        page: wikipediaapi.WikipediaPage,
        section_name: str
    ) -> Optional[wikipediaapi.WikipediaPageSection]:
        """Find a section by name (case-insensitive)."""
        for section in page.sections:
            if section.title.lower() == section_name.lower():
                return section
            # Check subsections
            for subsection in section.sections:
                if subsection.title.lower() == section_name.lower():
                    return subsection
        return None
    
    async def _parse_character_section(
        self,
        section: wikipediaapi.WikipediaPageSection
    ) -> List[Dict]:
        """Parse character information from a section."""
        characters = []
        
        # Simple parsing - split by bullet points or paragraphs
        text = section.text
        
        # Pattern: Name followed by description
        paragraphs = text.split('\n\n')
        
        for para in paragraphs[:10]:  # Limit to first 10 characters
            if not para.strip():
                continue
            
            # Extract character name (often first few words)
            lines = para.split('\n')
            if lines:
                first_line = lines[0].strip()
                
                # Character name is often before first comma or dash
                name_match = re.match(r'^([^,\-–]+)', first_line)
                if name_match:
                    name = name_match.group(1).strip()
                    
                    # Get description
                    description = para[:300]  # First 300 chars
                    
                    characters.append({
                        'name': name,
                        'description': description,
                        'traits': [],  # To be extracted by AI later
                        'relationships': {}  # To be extracted by AI later
                    })
        
        return characters[:10]  # Return max 10 main characters
    
    async def _extract_plot_info(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaShowData
    ):
        """Extract plot summaries and setting information."""
        # Look for Plot or Premise section
        plot_section = (
            self._find_section(page, 'Plot')
            or self._find_section(page, 'Premise')
            or self._find_section(page, 'Synopsis')
        )
        
        if plot_section:
            data.plot_summary = plot_section.text[:1000]
        else:
            # Use summary if no plot section
            data.plot_summary = page.summary[:1000]
        
        # Extract setting from plot or summary
        data.setting = await self._extract_setting(
            data.plot_summary or page.summary
        )
    
    async def _extract_setting(self, text: str) -> Optional[str]:
        """Extract time period and location from text."""
        # Look for time periods
        time_patterns = [
            r'set in (the )?\d{4}s?',
            r'takes place in (the )?\d{4}s?',
            r'during (the )?\d{4}s?',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Look for locations (cities, states)
        location_keywords = [
            'New York', 'Los Angeles', 'Chicago', 'Hollywood',
            'California', 'Manhattan', 'suburban', 'small town'
        ]
        
        for keyword in location_keywords:
            if keyword.lower() in text.lower():
                return keyword
        
        return None
    
    async def _extract_production_info(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaShowData
    ):
        """Extract production and reception information."""
        # Cultural impact
        impact_section = (
            self._find_section(page, 'Cultural impact')
            or self._find_section(page, 'Legacy')
        )
        if impact_section:
            data.cultural_impact = impact_section.text[:500]
        
        # Critical reception
        reception_section = (
            self._find_section(page, 'Reception')
            or self._find_section(page, 'Critical response')
        )
        if reception_section:
            data.critical_reception = reception_section.text[:500]
    
    async def _extract_themes(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaShowData
    ):
        """Extract major themes from the show."""
        # Look for Themes section
        themes_section = self._find_section(page, 'Themes')
        
        if themes_section:
            text = themes_section.text
            # Simple extraction - look for common theme keywords
            theme_keywords = [
                'family', 'friendship', 'love', 'marriage', 'work',
                'ambition', 'identity', 'class', 'race', 'gender',
                'comedy', 'satire', 'social commentary', 'americana',
                'nostalgia', 'community', 'values', 'tradition'
            ]
            
            found_themes = []
            for keyword in theme_keywords:
                if keyword in text.lower():
                    found_themes.append(keyword.title())
            
            data.themes = found_themes[:10]  # Max 10 themes
    
    async def _extract_episodes(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaShowData
    ):
        """Extract notable episode information."""
        # Look for Episodes section
        episodes_section = (
            self._find_section(page, 'Episodes')
            or self._find_section(page, 'Notable episodes')
        )
        
        if episodes_section:
            # Placeholder for future sophisticated parsing
            logger.debug(f"Found episodes section for {data.title}")
            data.notable_episodes = []


# Example usage
async def main():
    """Example usage of Wikipedia research scraper."""
    async with WikipediaResearchScraper() as scraper:
        # Research I Love Lucy
        lucy_data = await scraper.research_show("I Love Lucy")
        
        print(f"Title: {lucy_data.title}")
        print(f"Years: {lucy_data.years}")
        print(f"Network: {lucy_data.network}")
        print(f"Characters: {len(lucy_data.main_characters)}")
        print(f"Themes: {', '.join(lucy_data.themes)}")
        print(f"\nPremise: {lucy_data.premise[:200] if lucy_data.premise else 'N/A'}...")


if __name__ == "__main__":
    asyncio.run(main())
