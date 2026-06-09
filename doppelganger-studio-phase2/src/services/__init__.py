"""
Wikipedia data extraction module.

This module implements the WikipediaShowData dataclass and the WikipediaResearchScraper class.
Key components:
- WikipediaShowData: Data structure for show information.
- WikipediaResearchScraper: Class for scraping Wikipedia data asynchronously.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional
from dataclasses import dataclass

@dataclass
class WikipediaShowData:
    """
    Data structure for storing information about a TV show from Wikipedia.

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