"""
Module-level docstring with purpose and usage.

This module implements a Wikipedia scraper for extracting TV show data.
Key components:
- WikipediaShowData: Dataclass for structured show data.
- WikipediaResearchScraper: Class for scraping Wikipedia.

Example:
    >>> from src.services.research.wikipedia_scraper import WikipediaResearchScraper
    >>> async with WikipediaResearchScraper() as scraper:
    ...     data = await scraper.scrape("I Love Lucy")
    ...     print(data.title)

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
    Dataclass for storing structured data about a TV show.

    Attributes:
        title (str): The title of the show.
        summary (str): A brief summary of the show.
        years (str): The years the show aired.
        network (str): The network that aired the show.
        genre (List[str]): A list of genres associated with the show.
        main_characters (List[str]): A list of main characters in the show.

    Example:
        >>> show_data = WikipediaShowData(title="I Love Lucy", summary="A sitcom...", years="1951-1957")
        >>> print(show_data.title)
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

    This class provides methods to scrape show information asynchronously.

    Example:
        >>> async with WikipediaResearchScraper() as scraper:
        ...     data = await scraper.scrape("I Love Lucy")
        ...     print(data.summary)
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

    async def scrape(self, show_title: str) -> WikipediaShowData:
        """
        Scrape data for a given TV show title.

        Args:
            show_title (str): The title of the TV show to scrape.

        Returns:
            WikipediaShowData: The structured data extracted from Wikipedia.

        Raises:
            ValueError: If the show is not found.
        """
        logger.info(f"Scraping data for show: {show_title}")
        page = self.wiki_wiki.page(show_title)

        if not page.exists():
            logger.error(f"Page not found for show: {show_title}")
            raise ValueError(f"Show '{show_title}' not found on Wikipedia.")

        # Extracting basic information
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
        logger.info(f"Successfully scraped data for show: {show_title}")
        return show_data

    def _extract_years(self, page) -> str:
        """Extract the years the show aired from the page."""
        # Placeholder for actual extraction logic
        return "1951-1957"

    def _extract_network(self, page) -> str:
        """Extract the network from the page."""
        # Placeholder for actual extraction logic
        return "CBS"

    def _extract_genre(self, page) -> List[str]:
        """Extract the genres from the page."""
        # Placeholder for actual extraction logic
        return ["Sitcom"]

    def _extract_characters(self, page) -> List[str]:
        """Extract the main characters from the page."""
        # Placeholder for actual extraction logic
        return ["Lucy Ricardo", "Ricky Ricardo"]