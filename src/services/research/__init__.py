"""
Research Services Package - TV show data collection and caching.

Provides scrapers for Wikipedia, TMDB, and IMDB with PostgreSQL caching.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from src.services.research.wikipedia_scraper import WikipediaResearchScraper
from src.services.research.tmdb_scraper import TMDBResearchScraper
from src.services.research.postgres_cache import PostgresResearchCache

__all__ = [
    'WikipediaResearchScraper',
    'TMDBResearchScraper',
    'PostgresResearchCache',
]
