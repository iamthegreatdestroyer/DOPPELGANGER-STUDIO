# src/services/research/wikipedia_scraper.py

"""
Wikipedia scraper for extracting TV show data.

This module implements the WikipediaResearchScraper class to fetch and parse
TV show information from Wikipedia using the Wikipedia API.

Key components:
- WikipediaShowData: Dataclass for structured show data.
- WikipediaResearchScraper: Class for scraping and extracting data.

Example:
    >>> from wikipedia_scraper import WikipediaResearchScraper
    >>> async with WikipediaResearchScraper() as scraper:
    ...     show_data = await scraper.scrape("I Love Lucy")
    ...     print(show_data)

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional
from dataclasses import dataclass
import wikipediaapi
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class WikipediaShowData:
    """
    Data structure for storing TV show information extracted from Wikipedia.

    Attributes:
        title: The title of the show.
        summary: A brief summary of the show.
        years: The original airing years of the show.
        network: The network that aired the show.
        genre: A list of genres associated with the show.
        main_characters: A list of main characters in the show.
    """
    title: str
    summary: str
    years: str
    network: str
    genre: List[str]
    main_characters: List[str]