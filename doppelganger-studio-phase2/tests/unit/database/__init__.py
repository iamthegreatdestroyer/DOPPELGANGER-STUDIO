# src/services/research/wikipedia_scraper.py

"""
Wikipedia scraper for extracting TV show data.

This module implements the WikipediaShowData dataclass and the 
WikipediaResearchScraper class for scraping TV show information from Wikipedia.

Key components:
- WikipediaShowData: Dataclass for structured show data.
- WikipediaResearchScraper: Class for performing the scraping operations.

Example:
    >>> scraper = WikipediaResearchScraper()
    >>> show_data = await scraper.scrape("I Love Lucy")
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
    Data structure for holding TV show information from Wikipedia.

    Attributes:
        title (str): The title of the show.
        summary (str): A brief summary of the show.
        years (str): The years the show aired.
        network (str): The network that aired the show.
        genre (List[str]): List of genres associated with the show.
        main_characters (List[dict]): List of main characters with their details.
    """
    title: str
    summary: str
    years: str
    network: str
    genre: List[str]
    main_characters: List[dict]