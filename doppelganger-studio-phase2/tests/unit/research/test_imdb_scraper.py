# src/services/research/wikipedia_scraper.py

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class WikipediaShowData:
    """
    Data structure for storing extracted Wikipedia show data.

    Attributes:
        title (str): The title of the show.
        summary (str): A brief summary of the show.
        years (str): The original airing years of the show.
        network (str): The network that aired the show.
        genre (List[str]): A list of genres associated with the show.
        main_characters (List[dict]): A list of main characters with their details.
        
    Example:
        >>> show_data = WikipediaShowData(
        ...     title="I Love Lucy",
        ...     summary="I Love Lucy is an American sitcom...",
        ...     years="1951-1957",
        ...     network="CBS",
        ...     genre=["Sitcom"],
        ...     main_characters=[{"name": "Lucy Ricardo", "actor": "Lucille Ball"}]
        ... )
    """
    title: str
    summary: str
    years: str
    network: str
    genre: List[str]
    main_characters: List[dict]