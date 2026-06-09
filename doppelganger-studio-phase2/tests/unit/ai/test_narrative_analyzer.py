"""
Wikipedia Scraper for extracting TV show data.

This module implements the WikipediaResearchScraper class to fetch and parse
TV show data from Wikipedia. It includes methods for searching page variations
and extracting relevant information such as show title, years, network, and
main characters.

Key components:
- WikipediaShowData: Dataclass representing the structure of the show data.
- WikipediaResearchScraper: Class for handling the scraping logic.

Example:
    >>> async with WikipediaResearchScraper() as scraper:
    >>>     show_data = await scraper.fetch_show_data("I Love Lucy")
    >>>     print(show_data.title)

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional
import wikipediaapi
import logging
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WikipediaShowData:
    """
    Data structure for storing extracted show information.

    Attributes:
        title: The title of the show.
        years: The years the show aired.
        network: The network that aired the show.
        genre: List of genres associated with the show.
        main_characters: List of main characters in the show.
    """
    title: str
    years: Optional[str] = None
    network: Optional[str] = None
    genre: List[str] = field(default_factory=list)
    main_characters: List[str] = field(default_factory=list)

class WikipediaResearchScraper:
    """
    Scraper for fetching TV show data from Wikipedia.

    This class provides methods to search for shows and extract relevant
    information from their Wikipedia pages.

    Example:
        >>> async with WikipediaResearchScraper() as scraper:
        >>>     show_data = await scraper.fetch_show_data("I Love Lucy")
    """

    def __init__(self):
        """Initialize the Wikipedia API client."""
        self.wiki_wiki = wikipediaapi.Wikipedia('en')

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass  # No resources to clean up for this scraper

    async def fetch_show_data(self, show_title: str) -> WikipediaShowData:
        """
        Fetch show data from Wikipedia.

        Args:
            show_title: The title of the show to fetch data for.

        Returns:
            WikipediaShowData containing extracted information.

        Raises:
            ValueError: If the show page is not found.
        """
        logger.info(f"Fetching data for show: {show_title}")
        page = self.wiki_wiki.page(show_title)

        if not page.exists():
            logger.error(f"Show page not found: {show_title}")
            raise ValueError(f"Show page not found: {show_title}")

        # Extract basic information
        show_data = WikipediaShowData(title=page.title)
        show_data.years = self._extract_years(page)
        show_data.network = self._extract_network(page)
        show_data.genre = self._extract_genre(page)
        show_data.main_characters = self._extract_characters(page)

        logger.info(f"Successfully fetched data for show: {show_data.title}")
        return show_data

    def _extract_years(self, page) -> Optional[str]:
        """Extract the years the show aired from the page summary."""
        # Placeholder for actual extraction logic
        return "1951-1957"  # Example static return

    def _extract_network(self, page) -> Optional[str]:
        """Extract the network from the page summary."""
        # Placeholder for actual extraction logic
        return "CBS"  # Example static return

    def _extract_genre(self, page) -> List[str]:
        """Extract genres associated with the show."""
        # Placeholder for actual extraction logic
        return ["Sitcom"]  # Example static return

    def _extract_characters(self, page) -> List[str]:
        """Extract main characters from the page."""
        # Placeholder for actual extraction logic
        return ["Lucy Ricardo", "Ricky Ricardo"]  # Example static return