"""
TMDB Research Scraper - Extract TV show data from The Movie Database.

Provides structured data including cast, crew, episode information,
ratings, and production details.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional
import asyncio
import aiohttp
import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TMDBShowData:
    """Container for TMDB-sourced show data."""
    tmdb_id: int
    title: str
    original_title: str
    overview: str
    first_air_date: Optional[str] = None
    last_air_date: Optional[str] = None
    status: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    genres: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    creators: List[Dict] = field(default_factory=list)
    cast: List[Dict] = field(default_factory=list)
    episode_count: int = 0
    season_count: int = 0
    seasons: List[Dict] = field(default_factory=list)
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


class TMDBResearchScraper:
    """
    Scrapes The Movie Database (TMDB) for TV show information.
    
    Requires TMDB API key (free from themoviedb.org).
    Enhanced with Redis-based rate limiting (40 requests per 10 seconds).
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"
    RATE_LIMIT_WINDOW = 10  # seconds
    RATE_LIMIT_MAX = 40  # requests per window
    
    def __init__(self, api_key: str, redis_client=None):
        """
        Initialize TMDB scraper.
        
        Args:
            api_key: TMDB API key from themoviedb.org
            redis_client: Redis client from DatabaseManager for rate limiting
        """
        self.api_key = api_key
        self.redis = redis_client
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def research_show(self, show_title: str) -> TMDBShowData:
        """
        Research a TV show using TMDB API.
        
        Args:
            show_title: Name of the TV show
            
        Returns:
            TMDBShowData with comprehensive information
            
        Example:
            >>> scraper = TMDBResearchScraper(api_key="your_key")
            >>> async with scraper:
            ...     data = await scraper.research_show("I Love Lucy")
            ...     print(f"Rating: {data.vote_average}/10")
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
        
        return data
    
    async def _search_show(self, query: str) -> Optional[int]:
        """Search for a TV show and return its TMDB ID."""
        url = f"{self.BASE_URL}/search/tv"
        params = {
            'api_key': self.api_key,
            'query': query,
            'page': 1
        }
        
        data = await self._make_request(url, params)
        results = data.get('results', [])
        
        if not results:
            return None
        
        # Return first result's ID
        return results[0]['id']
    
    async def _get_show_details(self, show_id: int) -> Dict:
        """Get detailed information about a show."""
        url = f"{self.BASE_URL}/tv/{show_id}"
        params = {
            'api_key': self.api_key,
            'append_to_response': 'content_ratings,external_ids'
        }
        
        return await self._make_request(url, params)
    
    async def _get_credits(self, show_id: int) -> Dict:
        """Get cast and crew information."""
        url = f"{self.BASE_URL}/tv/{show_id}/credits"
        params = {'api_key': self.api_key}
        
        try:
            return await self._make_request(url, params)
        except Exception as e:
            logger.warning(f"Failed to get credits: {e}")
            return {'cast': [], 'crew': []}
    
    async def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits using Redis.
        
        Returns:
            True if request can proceed, False if rate limited
        """
        if not self.redis:
            return True  # No Redis = no rate limiting (fallback)
        
        key = "ratelimit:tmdb:requests"
        now = datetime.now().timestamp()
        window_start = now - self.RATE_LIMIT_WINDOW
        
        try:
            # Remove old entries outside window
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            count = await self.redis.zcard(key)
            
            if count >= self.RATE_LIMIT_MAX:
                # Get oldest entry in window
                oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    wait_time = (
                        oldest[0][1] + self.RATE_LIMIT_WINDOW - now
                    )
                    logger.warning(
                        f"TMDB rate limit reached, waiting {wait_time:.2f}s"
                    )
                    await asyncio.sleep(wait_time)
                    # Recursive check after waiting
                    return await self._check_rate_limit()
            
            # Add current request
            await self.redis.zadd(key, {str(now): now})
            await self.redis.expire(key, self.RATE_LIMIT_WINDOW * 2)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Fail open
    
    async def _make_request(self, url: str, params: Dict) -> Dict:
        """
        Make API request with rate limiting and retry logic.
        
        Args:
            url: API endpoint
            params: Query parameters
            
        Returns:
            JSON response
            
        Raises:
            Exception if request fails after retries
        """
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        max_retries = 3
        retry_delay = 1.0  # Initial delay in seconds
        
        for attempt in range(max_retries):
            # Check rate limit
            await self._check_rate_limit()
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 429:
                        # Rate limited - exponential backoff
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(
                            f"TMDB rate limited, waiting {wait_time}s"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status == 200:
                        return await response.json()
                    
                    # Other errors
                    logger.error(f"TMDB API error {response.status}")
                    if attempt == max_retries - 1:
                        raise Exception(
                            f"TMDB API failed: {response.status}"
                        )
                    
                    await asyncio.sleep(retry_delay)
                    
            except asyncio.TimeoutError:
                logger.error(f"TMDB timeout (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay)
        
        raise Exception("TMDB API request failed after retries")
    
    async def _search_show_old(self, query: str) -> Optional[int]:
        """Search for a TV show and return its TMDB ID."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = f"{self.BASE_URL}/search/tv"
        params = {
            'api_key': self.api_key,
            'query': query,
            'page': 1
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                logger.error(f"TMDB search failed: {response.status}")
                return None
            
            data = await response.json()
            results = data.get('results', [])
            
            if not results:
                return None
            
            # Return first result's ID
            return results[0]['id']
    
    async def _get_show_details(self, show_id: int) -> Dict:
        """Get detailed information about a show."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = f"{self.BASE_URL}/tv/{show_id}"
        params = {
            'api_key': self.api_key,
            'append_to_response': 'content_ratings,external_ids'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise ValueError(
                    f"Failed to get show details: {response.status}"
                )
            
            return await response.json()
    
    async def _get_credits(self, show_id: int) -> Dict:
        """Get cast and crew information."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = f"{self.BASE_URL}/tv/{show_id}/credits"
        params = {'api_key': self.api_key}
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                logger.warning(f"Failed to get credits: {response.status}")
                return {'cast': [], 'crew': []}
            
            return await response.json()
    
    def _build_show_data(self, details: Dict, credits: Dict) -> TMDBShowData:
        """Build TMDBShowData from API responses."""
        return TMDBShowData(
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
            cast=[
                {
                    'name': actor['name'],
                    'character': actor.get('character', ''),
                    'order': actor.get('order', 999)
                }
                for actor in credits.get('cast', [])[:15]  # Top 15 cast
            ],
            episode_count=details.get('number_of_episodes', 0),
            season_count=details.get('number_of_seasons', 0),
            seasons=[
                {
                    'season_number': s['season_number'],
                    'episode_count': s['episode_count'],
                    'name': s.get('name', f"Season {s['season_number']}")
                }
                for s in details.get('seasons', [])
            ],
            poster_path=self._build_image_url(details.get('poster_path')),
            backdrop_path=self._build_image_url(details.get('backdrop_path'))
        )
    
    def _build_image_url(self, path: Optional[str]) -> Optional[str]:
        """Build full image URL from TMDB path."""
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}{path}"


# Example usage
async def main():
    """Example usage of TMDB scraper."""
    import os
    
    api_key = os.getenv('TMDB_API_KEY', 'your_key_here')
    
    async with TMDBResearchScraper(api_key) as scraper:
        data = await scraper.research_show("I Love Lucy")
        
        print(f"Title: {data.title}")
        print(f"Years: {data.first_air_date} to {data.last_air_date}")
        print(f"Rating: {data.vote_average}/10")
        print(f"Seasons: {data.season_count}")
        print(f"Episodes: {data.episode_count}")
        print(f"\nTop Cast:")
        for actor in data.cast[:5]:
            print(f"  - {actor['name']} as {actor['character']}")


if __name__ == "__main__":
    asyncio.run(main())
