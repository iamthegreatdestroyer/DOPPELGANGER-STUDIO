# src/services/research/wikipedia_scraper.py

"""
Wikipedia scraper for extracting TV show data.

This module implements the WikipediaResearchScraper class to extract
comprehensive TV show data from Wikipedia, including show details,
characters, and other relevant information.

Key components:
- WikipediaShowData: Dataclass for structured show data.
- WikipediaResearchScraper: Class for scraping Wikipedia.

Example:
    >>> scraper = WikipediaResearchScraper("I Love Lucy")
    >>> show_data = await scraper.scrape()
    >>> print(show_data.title)

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
    Data structure for storing extracted show data from Wikipedia.

    Attributes:
        title: The title of the show.
        summary: A brief summary of the show.
        years: The years the show aired.
        network: The network that aired the show.
        genre: List of genres associated with the show.
        main_characters: List of main characters in the show.
    """
    title: str
    summary: str
    years: str
    network: str
    genre: List[str]
    main_characters: List[str]