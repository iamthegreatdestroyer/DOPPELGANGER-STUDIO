"""
Wikipedia Research Scraper - Extract TV show data from Wikipedia.

Provides comprehensive extraction of TV show information including plot summaries,
character descriptions, episode guides, and cultural context using async operations.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, List, Dict
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import wikipediaapi
import logging
import re
from datetime import datetime

from src.models.research import WikipediaData, CharacterData

logger = logging.getLogger(__name__)


class WikipediaResearchScraper:
    """
    Scrapes Wikipedia for comprehensive TV show research data.
    
    Features:
    - Async operations for performance
    - Multiple page variation attempts
    - Infobox parsing for structured data
    - Character extraction from dedicated sections
    - Rate limiting (1 request/second)
    - Comprehensive error handling
    
    Example:
        >>> async with WikipediaResearchScraper() as scraper:
        ...     data = await scraper.research_show("I Love Lucy")
        ...     print(f"Found {len(data.main_characters)} characters")
    """
    
    def __init__(self, user_agent: str = "DoppelgangerStudio/0.2 (Educational Research)"):
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
        self._last_request_time: float = 0
        self._rate_limit_delay: float = 1.0  # 1 second between requests
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _respect_rate_limit(self):
        """Ensure we respect Wikipedia's rate limits."""
        import time
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    async def research_show(self, show_title: str) -> WikipediaData:
        """
        Comprehensive research on a TV show from Wikipedia.
        
        Args:
            show_title: Name of the TV show
            
        Returns:
            WikipediaData with all extracted information
            
        Raises:
            ValueError: If Wikipedia page not found
            
        Example:
            >>> async with WikipediaResearchScraper() as scraper:
            ...     data = await scraper.research_show("I Love Lucy")
            ...     print(f"Years: {data.years}")
        """
        logger.info(f"Researching show on Wikipedia: {show_title}")
        
        await self._respect_rate_limit()
        
        # Find Wikipedia page
        page = await self._find_page(show_title)
        
        if not page or not page.exists():
            raise ValueError(f"Wikipedia page not found for: {show_title}")
        
        logger.info(f"Found Wikipedia page: {page.title}")
        
        # Extract basic data
        data = WikipediaData(
            title=page.title,
            years=self._extract_years(page),
            premise=page.summary[:500] if page.summary else None,
            source_url=page.fullurl,
            scraped_at=datetime.now()
        )
        
        # Extract structured data in parallel
        await asyncio.gather(
            self._extract_infobox_data(page, data),
            self._extract_characters(page, data),
            self._extract_plot_info(page, data),
            self._extract_production_info(page, data),
            self._extract_themes(page, data)
        )
        
        logger.info(f"Research complete: {data.title}")
        logger.debug(f"Extracted {len(data.main_characters)} characters, {len(data.themes)} themes")
        
        return data
    
    async def _find_page(self, title: str) -> Optional[wikipediaapi.WikipediaPage]:
        """
        Find Wikipedia page by trying multiple title variations.
        
        Args:
            title: Show title to search for
            
        Returns:
            WikipediaPage if found, None otherwise
        """
        # Try variations in order of likelihood
        variations = [
            title,
            f"{title} (TV series)",
            f"{title} (American TV series)",
            f"The {title}",
            f"The {title} (TV series)",
            title.replace("'", "'"),  # Different apostrophe type
            title.replace("'", "'"),  # Smart quote
        ]
        
        for variation in variations:
            await self._respect_rate_limit()
            page = self.wiki.page(variation)
            if page.exists():
                logger.info(f"Found page with variation: {variation}")
                return page
        
        logger.warning(f"No Wikipedia page found for: {title}")
        return None
    
    def _extract_years(self, page: wikipediaapi.WikipediaPage) -> str:
        """Extract years the show aired from page summary."""
        text = page.summary[:500] if page.summary else ""
        
        # Pattern: (YYYY-YYYY) or YYYY-YYYY
        pattern = r'\(?(\d{4})[–\-](\d{4})\)?'
        match = re.search(pattern, text)
        
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        
        # Pattern: Single year (YYYY)
        pattern = r'\(?(\d{4})\)?'
        match = re.search(pattern, text)
        
        if match:
            return match.group(1)
        
        return "Unknown"
    
    async def _extract_infobox_data(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaData
    ):
        """Extract structured data from Wikipedia infobox."""
        if not self.session:
            return
        
        try:
            await self._respect_rate_limit()
            
            async with self.session.get(page.fullurl) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch page HTML: {response.status}")
                    return
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                infobox = soup.find('table', class_='infobox')
                if not infobox:
                    logger.debug("No infobox found")
                    return
                
                # Extract network
                network_row = infobox.find('th', string=re.compile(r'Network', re.I))
                if network_row:
                    network_cell = network_row.find_next('td')
                    if network_cell:
                        data.network = network_cell.get_text(strip=True).split('\n')[0]
                
                # Extract genre
                genre_row = infobox.find('th', string=re.compile(r'Genre', re.I))
                if genre_row:
                    genre_cell = genre_row.find_next('td')
                    if genre_cell:
                        genres = [g.strip() for g in genre_cell.get_text().split('\n') if g.strip()]
                        data.genre = genres[:5]  # Limit to 5 genres
                
                # Extract creators
                creator_row = infobox.find('th', string=re.compile(r'Created by', re.I))
                if creator_row:
                    creator_cell = creator_row.find_next('td')
                    if creator_cell:
                        creators = [c.strip() for c in creator_cell.get_text().split('\n') if c.strip()]
                        data.creators = creators[:5]  # Limit to 5 creators
                
                # Extract episode count
                episode_row = infobox.find('th', string=re.compile(r'No\. of episodes', re.I))
                if episode_row:
                    episode_cell = episode_row.find_next('td')
                    if episode_cell:
                        episode_text = episode_cell.get_text(strip=True)
                        match = re.search(r'(\d+)', episode_text)
                        if match:
                            data.episode_count = int(match.group(1))
                
                # Extract season count
                season_row = infobox.find('th', string=re.compile(r'No\. of seasons', re.I))
                if season_row:
                    season_cell = season_row.find_next('td')
                    if season_cell:
                        season_text = season_cell.get_text(strip=True)
                        match = re.search(r'(\d+)', season_text)
                        if match:
                            data.season_count = int(match.group(1))
                
                logger.debug(f"Extracted infobox data: network={data.network}, genres={len(data.genre)}")
                
        except Exception as e:
            logger.error(f"Infobox extraction failed: {e}")
    
    async def _extract_characters(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaData
    ):
        """Extract main character information."""
        # Look for character sections
        section_names = [
            'Characters',
            'Cast and characters',
            'Main characters',
            'Cast',
            'Main cast'
        ]
        
        for section_name in section_names:
            section = self._find_section(page, section_name)
            if section:
                characters = self._parse_character_section(section)
                if characters:
                    data.main_characters = characters
                    logger.debug(f"Extracted {len(characters)} characters from '{section_name}' section")
                    return
        
        logger.debug("No character section found")
    
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
    
    def _parse_character_section(
        self,
        section: wikipediaapi.WikipediaPageSection
    ) -> List[CharacterData]:
        """Parse character information from section text."""
        characters = []
        text = section.text
        
        # Split by double newlines (paragraph breaks)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for para in paragraphs[:10]:  # Limit to first 10 to get main characters
            if len(para) < 20:  # Skip very short paragraphs
                continue
            
            # Extract character name (usually first phrase before comma, dash, or parenthesis)
            first_line = para.split('\n')[0].strip()
            name_match = re.match(r'^([^,\-–\(]+)', first_line)
            
            if name_match:
                name = name_match.group(1).strip()
                
                # Clean up name (remove common prefixes like "The character")
                name = re.sub(r'^(The character|Character)\s+', '', name, flags=re.I)
                
                # Skip if name is too long (likely not a name)
                if len(name) > 50:
                    continue
                
                character = CharacterData(
                    name=name,
                    description=para[:300],  # First 300 chars
                    traits=[],  # To be extracted by AI later
                    relationships={}
                )
                characters.append(character)
        
        return characters[:10]  # Return max 10 main characters
    
    async def _extract_plot_info(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaData
    ):
        """Extract plot summaries and setting information."""
        # Look for plot sections
        plot_section = (
            self._find_section(page, 'Plot') or
            self._find_section(page, 'Premise') or
            self._find_section(page, 'Synopsis') or
            self._find_section(page, 'Format')
        )
        
        if plot_section:
            data.plot_summary = plot_section.text[:1000]
        else:
            # Use summary if no dedicated plot section
            data.plot_summary = page.summary[:1000] if page.summary else None
        
        # Extract setting
        if data.plot_summary:
            data.setting = self._extract_setting(data.plot_summary)
    
    def _extract_setting(self, text: str) -> Optional[str]:
        """Extract time period and location from text."""
        # Look for time periods
        time_patterns = [
            r'set in (the )?\d{4}s?',
            r'takes place in (the )?\d{4}s?',
            r'during (the )?\d{4}s?',
            r'in (the )?\d{4}s?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Look for locations
        location_keywords = [
            'New York', 'Los Angeles', 'Chicago', 'Hollywood',
            'California', 'Manhattan', 'suburban', 'small town',
            'New York City', 'San Francisco'
        ]
        
        for keyword in location_keywords:
            if keyword.lower() in text.lower():
                return keyword
        
        return None
    
    async def _extract_production_info(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaData
    ):
        """Extract production and reception information."""
        # Cultural impact
        impact_section = (
            self._find_section(page, 'Cultural impact') or
            self._find_section(page, 'Legacy') or
            self._find_section(page, 'Influence')
        )
        if impact_section:
            data.cultural_impact = impact_section.text[:500]
        
        # Critical reception
        reception_section = (
            self._find_section(page, 'Reception') or
            self._find_section(page, 'Critical response') or
            self._find_section(page, 'Reviews')
        )
        if reception_section:
            data.critical_reception = reception_section.text[:500]
    
    async def _extract_themes(
        self,
        page: wikipediaapi.WikipediaPage,
        data: WikipediaData
    ):
        """Extract major themes from the show."""
        # Look for Themes section
        themes_section = self._find_section(page, 'Themes')
        
        if themes_section:
            text = themes_section.text
            
            # Common theme keywords to look for
            theme_keywords = [
                'family', 'friendship', 'love', 'marriage', 'work',
                'ambition', 'identity', 'class', 'race', 'gender',
                'comedy', 'satire', 'social commentary', 'americana',
                'nostalgia', 'community', 'values', 'tradition',
                'relationships', 'career', 'dreams', 'success'
            ]
            
            found_themes = []
            text_lower = text.lower()
            
            for keyword in theme_keywords:
                if keyword in text_lower:
                    found_themes.append(keyword.title())
            
            data.themes = found_themes[:10]  # Max 10 themes
        else:
            # Try to extract from plot summary
            if data.plot_summary:
                data.themes = self._infer_themes_from_text(data.plot_summary)
    
    def _infer_themes_from_text(self, text: str) -> List[str]:
        """Infer themes from plot text using keyword matching."""
        themes = []
        text_lower = text.lower()
        
        theme_patterns = {
            'Family': ['family', 'household', 'domestic'],
            'Comedy': ['comedy', 'sitcom', 'humorous', 'funny'],
            'Marriage': ['marriage', 'husband', 'wife', 'spouse'],
            'Career': ['career', 'job', 'work', 'profession'],
            'Dreams': ['dreams', 'aspirations', 'ambitions']
        }
        
        for theme, keywords in theme_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Max 5 inferred themes


# Example usage
async def main():
    """Example usage of Wikipedia research scraper."""
    async with WikipediaResearchScraper() as scraper:
        try:
            # Research I Love Lucy
            data = await scraper.research_show("I Love Lucy")
            
            print(f"Title: {data.title}")
            print(f"Years: {data.years}")
            print(f"Network: {data.network}")
            print(f"Genres: {', '.join(data.genre)}")
            print(f"Characters: {len(data.main_characters)}")
            for char in data.main_characters[:3]:
                print(f"  - {char.name}")
            print(f"Themes: {', '.join(data.themes)}")
            print(f"Episodes: {data.episode_count}")
            print(f"Seasons: {data.season_count}")
            print(f"\nPremise: {data.premise[:200]}...")
            
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
