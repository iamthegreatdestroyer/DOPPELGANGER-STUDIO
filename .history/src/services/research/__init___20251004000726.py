"""
Research Service - TV show data gathering and analysis.

This service coordinates multiple data sources to build comprehensive
research profiles for classic TV shows.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from .wikipedia_scraper import WikipediaResearchScraper, WikipediaShowData
from .tmdb_scraper import TMDBResearchScraper, TMDBShowData

__all__ = [
    'WikipediaResearchScraper',
    'WikipediaShowData',
    'TMDBResearchScraper',
    'TMDBShowData',
]
