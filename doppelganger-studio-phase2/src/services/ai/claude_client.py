"""
Wikipedia Scraper for extracting TV show data.

This module implements the WikipediaResearchScraper class to fetch and parse
TV show data from Wikipedia, including show details, characters, and plot summaries.
Key components:
- WikipediaShowData: Dataclass for structured show data.
- WikipediaResearchScraper: Class for scraping and extracting data.

Example:
    >>> from src.services.research.wikipedia_scraper import WikipediaResearchScraper
    >>> async with WikipediaResearchScraper() as scraper:
    ...     show_data = await scraper.fetch_show_data("I Love Lucy")
    ...     print(show_data)

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional
import wikipediaapi
import logging
import asyncio
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class WikipediaShowData:
    """
    Data structure for storing Wikipedia show data.

    Attributes:
        title: Title of the show.
        summary: Summary of the show.
        years: Original airing years.
        network: Network the show aired on.
        genre: List of genres associated with the show.
        main_characters: List of main characters in the show.
    """
    title: str
    summary: str
    years: str
    network: str
    genre: List[str]
    main_characters: List[str] = field(default_factory=list)

class WikipediaResearchScraper:
    """
    Scraper for extracting TV show data from Wikipedia.

    This class provides methods to fetch and parse show data from Wikipedia.
    
    Example:
        >>> async with WikipediaResearchScraper() as scraper:
        ...     show_data = await scraper.fetch_show_data("I Love Lucy")
    """
    
    def __init__(self):
        """Initialize the Wikipedia API client."""
        self.wiki_wiki = wikipediaapi.Wikipedia('en')

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass  # No resources to clean up

    async def fetch_show_data(self, show_title: str) -> Optional[WikipediaShowData]:
        """
        Fetch show data from Wikipedia.

        Args:
            show_title: The title of the show to fetch data for.

        Returns:
            WikipediaShowData containing the extracted information, or None if not found.
        """
        logger.info(f"Fetching data for show: {show_title}")
        page = self.wiki_wiki.page(show_title)

        if not page.exists():
            logger.warning(f"Show '{show_title}' not found on Wikipedia.")
            return None

        summary = page.summary
        years = self._extract_years(page)
        network = self._extract_network(page)
        genre = self._extract_genre(page)
        main_characters = self._extract_characters(page)

        show_data = WikipediaShowData(
            title=show_title,
            summary=summary,
            years=years,
            network=network,
            genre=genre,
            main_characters=main_characters
        )
        
        logger.info(f"Successfully fetched data for show: {show_data.title}")
        return show_data

    def _extract_years(self, page) -> str:
        """Extract the original airing years from the page."""
        # Placeholder for actual extraction logic
        return "1951-1957"

    def _extract_network(self, page) -> str:
        """Extract the network from the page."""
        # Placeholder for actual extraction logic
        return "CBS"

    def _extract_genre(self, page) -> List[str]:
        """Extract the genre from the page."""
        # Placeholder for actual extraction logic
        return ["Sitcom"]

    def _extract_characters(self, page) -> List[str]:
        """Extract main characters from the page."""
        # Placeholder for actual extraction logic
        return ["Lucy Ricardo", "Ricky Ricardo"]