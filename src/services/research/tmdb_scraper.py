"""
TMDB Research Scraper - Extract TV show data from The Movie Database.

Provides structured data including cast, crew, episode information,
ratings, and production details via official TMDB API.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, List, Dict
import asyncio
import aiohttp
import logging
import os
from datetime import datetime

from src.models.research import TMDBData, CastMember, SeasonData

logger = logging.getLogger(__name__)


class TMDBResearchScraper:
    """
    Scrapes The Movie Database (TMDB) for TV show information.
    
    Features:
    - Official TMDB API integration
    - Async operations for performance
    - Rate limiting (40 requests/10 seconds)
    - Automatic retry on rate limit
    - Comprehensive error handling
    - Image URL generation
    
    Requires:
        TMDB API key from themoviedb.org (free tier)
        
    Example:
        >>> api_key = os.getenv('TMDB_API_KEY')
        >>> async with TMDBResearchScraper(api_key) as scraper:
        ...     data = await scraper.research_show("I Love Lucy")
        ...     print(f"Rating: {data.vote_average}/10")
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDB scraper.
        
        Args:
            api_key: TMDB API key. If None, loads from TMDB_API_KEY env var
            
        Raises:
            ValueError: If API key not provided and not in environment
        """
        self.api_key = api_key or os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError(
                "TMDB API key required. Set TMDB_API_KEY environment variable "
                "or pass api_key parameter. Get free key at themoviedb.org"
            )
        
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_times: List[float] = []
        self._rate_limit_window = 10.0  # 10 seconds
        self._rate_limit_max = 40  # 40 requests per window
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _respect_rate_limit(self):
        """
        Ensure we respect TMDB's rate limits (40 requests/10 seconds).
        
        Uses sliding window algorithm to track requests.
        """
        import time
        current_time = time.time()
        
        # Remove requests outside the window
        self._request_times = [
            t for t in self._request_times
            if current_time - t < self._rate_limit_window
        ]
        
        # If at limit, wait until oldest request expires
        if len(self._request_times) >= self._rate_limit_max:
            oldest = self._request_times[0]
            sleep_time = self._rate_limit_window - (current_time - oldest) + 0.1
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                # Refresh current time after sleep
                current_time = time.time()
        
        # Record this request
        self._request_times.append(current_time)
    
    async def research_show(self, show_title: str) -> TMDBData:
        """
        Research a TV show using TMDB API.
        
        Args:
            show_title: Name of the TV show
            
        Returns:
            TMDBData with comprehensive information
            
        Raises:
            ValueError: If show not found on TMDB
            aiohttp.ClientError: If API request fails
            
        Example:
            >>> async with TMDBResearchScraper(api_key) as scraper:
            ...     data = await scraper.research_show("I Love Lucy")
            ...     print(f"Episodes: {data.episode_count}")
        """
        logger.info(f"Researching show on TMDB: {show_title}")
        
        # Search for show
        show_id = await self._search_show(show_title)
        if not show_id:
            raise ValueError(f"Show not found on TMDB: {show_title}")
        
        # Get detailed information
        details = await self._get_show_details(show_id)
        
        # Get cast and crew
        credits = await self._get_credits(show_id)
        
        # Build data object
        data = self._build_show_data(details, credits)
        
        logger.info(f"TMDB research complete: {data.title}")
        logger.debug(f"Found {len(data.cast)} cast members, {data.season_count} seasons")
        
        return data
    
    async def _search_show(self, query: str) -> Optional[int]:
        """
        Search for a TV show and return its TMDB ID.
        
        Args:
            query: Show title to search for
            
        Returns:
            TMDB ID if found, None otherwise
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager")
        
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/search/tv"
        params = {
            'api_key': self.api_key,
            'query': query,
            'page': 1
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 429:  # Rate limited
                    logger.warning("Rate limited by TMDB, retrying...")
                    await asyncio.sleep(10)
                    return await self._search_show(query)  # Retry
                
                if response.status != 200:
                    logger.error(f"TMDB search failed: {response.status}")
                    return None
                
                data = await response.json()
                results = data.get('results', [])
                
                if not results:
                    logger.warning(f"No TMDB results for: {query}")
                    return None
                
                # Return first result's ID
                show_id = results[0]['id']
                logger.info(f"Found TMDB ID {show_id} for '{query}'")
                return show_id
                
        except aiohttp.ClientError as e:
            logger.error(f"TMDB search error: {e}")
            raise
    
    async def _get_show_details(self, show_id: int) -> Dict:
        """
        Get detailed information about a show.
        
        Args:
            show_id: TMDB show ID
            
        Returns:
            Dict with show details
            
        Raises:
            ValueError: If show details cannot be retrieved
        """
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/tv/{show_id}"
        params = {
            'api_key': self.api_key,
            'append_to_response': 'content_ratings,external_ids'
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    logger.warning("Rate limited, retrying...")
                    await asyncio.sleep(10)
                    return await self._get_show_details(show_id)
                
                if response.status != 200:
                    raise ValueError(
                        f"Failed to get show details: HTTP {response.status}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching show details: {e}")
            raise
    
    async def _get_credits(self, show_id: int) -> Dict:
        """
        Get cast and crew information.
        
        Args:
            show_id: TMDB show ID
            
        Returns:
            Dict with cast and crew data
        """
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/tv/{show_id}/credits"
        params = {'api_key': self.api_key}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    logger.warning("Rate limited, retrying...")
                    await asyncio.sleep(10)
                    return await self._get_credits(show_id)
                
                if response.status != 200:
                    logger.warning(f"Failed to get credits: HTTP {response.status}")
                    return {'cast': [], 'crew': []}
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.warning(f"Error fetching credits: {e}")
            return {'cast': [], 'crew': []}
    
    def _build_show_data(self, details: Dict, credits: Dict) -> TMDBData:
        """
        Build TMDBData from API responses.
        
        Args:
            details: Show details from API
            credits: Cast and crew from API
            
        Returns:
            Complete TMDBData object
        """
        # Extract cast (top 15)
        cast = [
            CastMember(
                name=actor['name'],
                character=actor.get('character', ''),
                order=actor.get('order', 999),
                profile_path=self._build_image_url(actor.get('profile_path'))
            )
            for actor in credits.get('cast', [])[:15]
        ]
        
        # Extract seasons
        seasons = [
            SeasonData(
                season_number=s['season_number'],
                episode_count=s['episode_count'],
                name=s.get('name', f"Season {s['season_number']}"),
                air_date=s.get('air_date'),
                poster_path=self._build_image_url(s.get('poster_path'))
            )
            for s in details.get('seasons', [])
            if s['season_number'] > 0  # Skip "Season 0" (specials)
        ]
        
        # Build complete data object
        return TMDBData(
            tmdb_id=details['id'],
            title=details['name'],
            original_title=details.get('original_name', details['name']),
            overview=details.get('overview', ''),
            first_air_date=details.get('first_air_date'),
            last_air_date=details.get('last_air_date'),
            status=details.get('status'),
            vote_average=details.get('vote_average', 0.0),
            vote_count=details.get('vote_count', 0),
            popularity=details.get('popularity', 0.0),
            genres=[g['name'] for g in details.get('genres', [])],
            networks=[n['name'] for n in details.get('networks', [])],
            creators=[
                {
                    'name': c['name'],
                    'id': c['id']
                }
                for c in details.get('created_by', [])
            ],
            cast=cast,
            episode_count=details.get('number_of_episodes', 0),
            season_count=details.get('number_of_seasons', 0),
            seasons=seasons,
            poster_path=self._build_image_url(details.get('poster_path')),
            backdrop_path=self._build_image_url(details.get('backdrop_path')),
            scraped_at=datetime.now()
        )
    
    def _build_image_url(self, path: Optional[str]) -> Optional[str]:
        """
        Build full image URL from TMDB path.
        
        Args:
            path: TMDB image path (e.g., "/abc123.jpg")
            
        Returns:
            Full URL or None if path is None
        """
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}{path}"


# Example usage
async def main():
    """Example usage of TMDB scraper."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB_API_KEY environment variable not set")
        print("Get free API key at: https://www.themoviedb.org/settings/api")
        return
    
    async with TMDBResearchScraper(api_key) as scraper:
        try:
            data = await scraper.research_show("I Love Lucy")
            
            print(f"Title: {data.title}")
            print(f"Years: {data.first_air_date} to {data.last_air_date}")
            print(f"Status: {data.status}")
            print(f"Rating: {data.vote_average}/10 ({data.vote_count} votes)")
            print(f"Popularity: {data.popularity:.1f}")
            print(f"Genres: {', '.join(data.genres)}")
            print(f"Networks: {', '.join(data.networks)}")
            print(f"Seasons: {data.season_count}")
            print(f"Episodes: {data.episode_count}")
            print(f"\nTop Cast:")
            for actor in data.cast[:5]:
                print(f"  - {actor.name} as {actor.character}")
            print(f"\nOverview: {data.overview[:200]}...")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
