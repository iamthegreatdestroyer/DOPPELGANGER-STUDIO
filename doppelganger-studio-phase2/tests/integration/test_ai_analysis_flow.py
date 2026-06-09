# src/services/research/wikipedia_scraper.py

"""
Wikipedia scraper for extracting TV show data.

This module implements the WikipediaResearchScraper class to scrape
TV show data from Wikipedia, including show details, characters,
and other relevant information.

Key components:
- WikipediaShowData: Dataclass for structured show data.
- WikipediaResearchScraper: Class for scraping Wikipedia.

Example:
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
    Data structure for storing Wikipedia show data.

    Attributes:
        title: Title of the show.
        summary: Summary of the show.
        years: Original airing years.
        network: Network that aired the show.
        genre: List of genres associated with the show.
        main_characters: List of main characters in the show.
    """
    title: str
    summary: str
    years: Optional[str] = None
    network: Optional[str] = None
    genre: Optional[List[str]] = None
    main_characters: Optional[List[str]] = None