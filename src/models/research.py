"""
Research Data Models - Pydantic schemas for all research data.

Provides type-safe data models for Wikipedia, TMDB, IMDB research results
with validation, serialization, and JSON schema export.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class ResearchSource(str, Enum):
    """Research data sources."""
    WIKIPEDIA = "wikipedia"
    TMDB = "tmdb"
    IMDB = "imdb"


class CharacterData(BaseModel):
    """Character information from research."""
    name: str = Field(..., description="Character name")
    description: Optional[str] = Field(None, description="Character description")
    actor: Optional[str] = Field(None, description="Actor who played the character")
    traits: List[str] = Field(default_factory=list, description="Character traits")
    relationships: Dict[str, str] = Field(default_factory=dict, description="Character relationships")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lucy Ricardo",
                "description": "Ambitious housewife with dreams of stardom",
                "actor": "Lucille Ball",
                "traits": ["ambitious", "comedic", "determined"],
                "relationships": {"husband": "Ricky Ricardo"}
            }
        }


class EpisodeData(BaseModel):
    """Episode information."""
    season_number: int = Field(..., ge=1, description="Season number")
    episode_number: int = Field(..., ge=1, description="Episode number")
    title: Optional[str] = Field(None, description="Episode title")
    air_date: Optional[str] = Field(None, description="Original air date")
    rating: Optional[float] = Field(None, ge=0, le=10, description="Episode rating")
    description: Optional[str] = Field(None, description="Episode description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "season_number": 1,
                "episode_number": 1,
                "title": "The Diet",
                "air_date": "1951-10-15",
                "rating": 8.5,
                "description": "Lucy tries to lose weight to fit into a costume"
            }
        }


class WikipediaData(BaseModel):
    """Data extracted from Wikipedia."""
    title: str = Field(..., description="Show title from Wikipedia")
    years: str = Field(..., description="Years the show aired")
    network: Optional[str] = Field(None, description="Original network")
    genre: List[str] = Field(default_factory=list, description="Show genres")
    setting: Optional[str] = Field(None, description="Show setting (time/place)")
    premise: Optional[str] = Field(None, description="Show premise/summary")
    main_characters: List[CharacterData] = Field(default_factory=list, description="Main characters")
    plot_summary: Optional[str] = Field(None, description="Extended plot summary")
    cultural_impact: Optional[str] = Field(None, description="Cultural impact description")
    critical_reception: Optional[str] = Field(None, description="Critical reception summary")
    episode_count: Optional[int] = Field(None, ge=0, description="Total episode count")
    season_count: Optional[int] = Field(None, ge=0, description="Total season count")
    creators: List[str] = Field(default_factory=list, description="Show creators")
    themes: List[str] = Field(default_factory=list, description="Major themes")
    source_url: Optional[HttpUrl] = Field(None, description="Wikipedia URL")
    scraped_at: datetime = Field(default_factory=datetime.now, description="Scrape timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "I Love Lucy",
                "years": "1951-1957",
                "network": "CBS",
                "genre": ["Sitcom", "Comedy"],
                "setting": "1950s New York City",
                "premise": "A housewife dreams of show business stardom",
                "episode_count": 180,
                "season_count": 6
            }
        }


class TMDBData(BaseModel):
    """Data from The Movie Database (TMDB)."""
    tmdb_id: int = Field(..., description="TMDB show ID")
    title: str = Field(..., description="Show title")
    original_title: str = Field(..., description="Original title")
    overview: str = Field(..., description="Show overview/description")
    first_air_date: Optional[str] = Field(None, description="First air date")
    last_air_date: Optional[str] = Field(None, description="Last air date")
    status: Optional[str] = Field(None, description="Show status (Ended, Returning, etc)")
    vote_average: float = Field(default=0.0, ge=0, le=10, description="Average vote rating")
    vote_count: int = Field(default=0, ge=0, description="Number of votes")
    popularity: float = Field(default=0.0, ge=0, description="TMDB popularity score")
    genres: List[str] = Field(default_factory=list, description="Show genres")
    networks: List[str] = Field(default_factory=list, description="Broadcasting networks")
    creators: List[Dict[str, Any]] = Field(default_factory=list, description="Show creators")
    cast: List[Dict[str, Any]] = Field(default_factory=list, description="Main cast (top 15)")
    episode_count: int = Field(default=0, ge=0, description="Total episodes")
    season_count: int = Field(default=0, ge=0, description="Total seasons")
    seasons: List[Dict[str, Any]] = Field(default_factory=list, description="Season information")
    poster_path: Optional[HttpUrl] = Field(None, description="Poster image URL")
    backdrop_path: Optional[HttpUrl] = Field(None, description="Backdrop image URL")
    scraped_at: datetime = Field(default_factory=datetime.now, description="Scrape timestamp")
    
    @validator('vote_average', 'popularity')
    def round_floats(cls, v):
        """Round floats to 2 decimal places."""
        return round(v, 2) if v else 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "tmdb_id": 1447,
                "title": "I Love Lucy",
                "original_title": "I Love Lucy",
                "overview": "A classic American sitcom",
                "first_air_date": "1951-10-15",
                "last_air_date": "1957-05-06",
                "status": "Ended",
                "vote_average": 8.0,
                "vote_count": 234
            }
        }


class IMDBData(BaseModel):
    """Data from IMDB (ethically scraped)."""
    imdb_id: str = Field(..., pattern=r"^tt\d+$", description="IMDB ID (ttXXXXXXX)")
    title: str = Field(..., description="Show title")
    rating: Optional[float] = Field(None, ge=0, le=10, description="IMDB rating")
    rating_count: Optional[int] = Field(None, ge=0, description="Number of ratings")
    user_reviews: List[str] = Field(default_factory=list, description="Sample user reviews")
    episode_ratings: List[Dict[str, Any]] = Field(default_factory=list, description="Episode ratings")
    trivia: List[str] = Field(default_factory=list, description="Show trivia")
    goofs: List[str] = Field(default_factory=list, description="Show goofs")
    scraped_at: datetime = Field(default_factory=datetime.now, description="Scrape timestamp")
    
    @validator('imdb_id')
    def validate_imdb_id(cls, v):
        """Validate IMDB ID format."""
        if not v.startswith('tt'):
            raise ValueError('IMDB ID must start with "tt"')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "imdb_id": "tt0043208",
                "title": "I Love Lucy",
                "rating": 8.3,
                "rating_count": 15234,
                "trivia": ["First show to be filmed in front of a live audience"]
            }
        }


class ShowResearchData(BaseModel):
    """Unified research data for a TV show."""
    show_title: str = Field(..., description="Primary show title")
    research_sources: List[ResearchSource] = Field(default_factory=list, description="Sources used")
    
    # Source-specific data
    wikipedia: Optional[WikipediaData] = Field(None, description="Wikipedia data")
    tmdb: Optional[TMDBData] = Field(None, description="TMDB data")
    imdb: Optional[IMDBData] = Field(None, description="IMDB data")
    
    # Aggregated metadata
    genres: List[str] = Field(default_factory=list, description="Aggregated genres")
    years: Optional[str] = Field(None, description="Years aired")
    networks: List[str] = Field(default_factory=list, description="Broadcasting networks")
    creators: List[str] = Field(default_factory=list, description="Show creators")
    cast: List[Dict[str, Any]] = Field(default_factory=list, description="Main cast")
    characters: List[CharacterData] = Field(default_factory=list, description="Main characters")
    
    # Aggregated stats
    rating_average: Optional[float] = Field(None, ge=0, le=10, description="Average rating across sources")
    episode_count: Optional[int] = Field(None, ge=0, description="Total episodes")
    season_count: Optional[int] = Field(None, ge=0, description="Total seasons")
    
    # Metadata
    research_date: datetime = Field(default_factory=datetime.now, description="Research timestamp")
    research_duration_ms: Optional[int] = Field(None, ge=0, description="Research duration in milliseconds")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during research")
    
    def merge_data(self):
        """Merge data from all sources into aggregated fields."""
        # Aggregate genres
        all_genres = set()
        if self.wikipedia:
            all_genres.update(self.wikipedia.genre)
        if self.tmdb:
            all_genres.update(self.tmdb.genres)
        self.genres = sorted(list(all_genres))
        
        # Aggregate years
        if self.wikipedia and self.wikipedia.years:
            self.years = self.wikipedia.years
        elif self.tmdb and self.tmdb.first_air_date and self.tmdb.last_air_date:
            start = self.tmdb.first_air_date[:4]
            end = self.tmdb.last_air_date[:4]
            self.years = f"{start}-{end}"
        
        # Aggregate networks
        all_networks = set()
        if self.wikipedia and self.wikipedia.network:
            all_networks.add(self.wikipedia.network)
        if self.tmdb:
            all_networks.update(self.tmdb.networks)
        self.networks = sorted(list(all_networks))
        
        # Aggregate creators
        all_creators = set()
        if self.wikipedia:
            all_creators.update(self.wikipedia.creators)
        if self.tmdb:
            all_creators.update(c['name'] for c in self.tmdb.creators if 'name' in c)
        self.creators = sorted(list(all_creators))
        
        # Aggregate cast
        if self.tmdb and self.tmdb.cast:
            self.cast = self.tmdb.cast[:15]
        
        # Aggregate characters
        if self.wikipedia and self.wikipedia.main_characters:
            self.characters = self.wikipedia.main_characters
        
        # Aggregate ratings
        ratings = []
        if self.tmdb and self.tmdb.vote_average > 0:
            ratings.append(self.tmdb.vote_average)
        if self.imdb and self.imdb.rating:
            ratings.append(self.imdb.rating)
        if ratings:
            self.rating_average = round(sum(ratings) / len(ratings), 2)
        
        # Aggregate episode/season counts (prefer TMDB, fallback to Wikipedia)
        if self.tmdb and self.tmdb.episode_count > 0:
            self.episode_count = self.tmdb.episode_count
            self.season_count = self.tmdb.season_count
        elif self.wikipedia:
            self.episode_count = self.wikipedia.episode_count
            self.season_count = self.wikipedia.season_count
    
    class Config:
        json_schema_extra = {
            "example": {
                "show_title": "I Love Lucy",
                "research_sources": ["wikipedia", "tmdb", "imdb"],
                "genres": ["Sitcom", "Comedy"],
                "years": "1951-1957",
                "rating_average": 8.15
            }
        }


# Export models for easy import
__all__ = [
    'ResearchSource',
    'CharacterData',
    'EpisodeData',
    'WikipediaData',
    'TMDBData',
    'IMDBData',
    'ShowResearchData'
]
