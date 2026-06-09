"""
Unit tests for WikipediaResearchScraper.

Tests:
- Successful research
- Page not found
- Page variations
- Mock Wikipedia API responses

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.services.research.wikipedia_scraper import WikipediaResearchScraper
from src.models.research import WikipediaData

@pytest.mark.asyncio
async def test_extract_characters_and_plot(monkeypatch):
    """Test character and plot extraction from Wikipedia page sections."""
    mock_section = MagicMock()
    mock_section.text = "Lucy Ricardo, the main character.\n\nRicky Ricardo, her husband."
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.title = "I Love Lucy"
    mock_page.summary = "I Love Lucy is an American sitcom (1951-1957)."
    mock_page.fullurl = "https://en.wikipedia.org/wiki/I_Love_Lucy"
    mock_page.sections = [mock_section]
    
    async def mock_find_page(self, title):
        return mock_page
    
    with patch.object(WikipediaResearchScraper, "_find_page", new=mock_find_page):
        async with WikipediaResearchScraper() as scraper:
            # Patch _find_section to always return mock_section
            with patch.object(scraper, "_find_section", return_value=mock_section):
                data = await scraper.research_show("I Love Lucy")
                assert len(data.main_characters) >= 2
                assert any("Lucy" in c.name for c in data.main_characters)
                assert data.plot_summary is not None

@pytest.mark.asyncio
async def test_extract_infobox(monkeypatch):
    """Test infobox HTML parsing for network, genre, creators, episodes, seasons."""
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.title = "I Love Lucy"
    mock_page.summary = "I Love Lucy is an American sitcom (1951-1957)."
    mock_page.fullurl = "https://en.wikipedia.org/wiki/I_Love_Lucy"

    # Patch aiohttp session.get to return a mock HTML response
    class MockResponse:
        status = 200
        async def text(self):
            return '''<table class="infobox">
                <tr><th>Network</th><td>CBS</td></tr>
                <tr><th>Genre</th><td>Sitcom\nComedy</td></tr>
                <tr><th>Created by</th><td>Lucille Ball\nDesi Arnaz</td></tr>
                <tr><th>No. of episodes</th><td>181</td></tr>
                <tr><th>No. of seasons</th><td>6</td></tr>
            </table>'''
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc_val, exc_tb): pass

    class MockSession:
        def get(self, url):
            return MockResponse()
        async def close(self): pass

    async def mock_find_page(self, title):
        return mock_page

    with patch.object(WikipediaResearchScraper, "_find_page", new=mock_find_page):
        async with WikipediaResearchScraper() as scraper:
            scraper.session = MockSession()
            from datetime import datetime
            data = WikipediaData(
                title="I Love Lucy", years="1951-1957", premise="", 
                source_url="https://en.wikipedia.org/wiki/I_Love_Lucy", 
                scraped_at=datetime.now()
            )
            await scraper._extract_infobox_data(mock_page, data)
            assert data.network == "CBS"
            assert "Sitcom" in data.genre
            assert "Comedy" in data.genre
            assert "Lucille Ball" in data.creators
            assert data.episode_count == 181
            assert data.season_count == 6

@pytest.mark.asyncio
async def test_extract_themes_and_production(monkeypatch):
    """Test theme and production info extraction from sections and plot."""
    mock_section = MagicMock()
    mock_section.text = "The show explores family, marriage, and comedy."
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.title = "I Love Lucy"
    mock_page.summary = "I Love Lucy is an American sitcom (1951-1957)."
    mock_page.fullurl = "https://en.wikipedia.org/wiki/I_Love_Lucy"
    mock_page.sections = [mock_section]

    async def mock_find_page(self, title):
        return mock_page

    with patch.object(WikipediaResearchScraper, "_find_page", new=mock_find_page):
        async with WikipediaResearchScraper() as scraper:
            with patch.object(scraper, "_find_section", return_value=mock_section):
                from datetime import datetime
                data = WikipediaData(
                    title="I Love Lucy", years="1951-1957", premise="", 
                    source_url="https://en.wikipedia.org/wiki/I_Love_Lucy",
                    scraped_at=datetime.now()
                )
                await scraper._extract_themes(mock_page, data)
                assert "Family" in data.themes or "Marriage" in data.themes or "Comedy" in data.themes
                await scraper._extract_production_info(mock_page, data)
                # Should not raise and should set attributes (may be None if not found)

@pytest.mark.asyncio
async def test_research_show_success():
    """Test successful research returns WikipediaData."""
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.title = "I Love Lucy"
    mock_page.summary = "I Love Lucy is an American sitcom (1951-1957)."
    mock_page.fullurl = "https://en.wikipedia.org/wiki/I_Love_Lucy"

    async def mock_find_page(self, title):
        return mock_page

    with patch.object(WikipediaResearchScraper, "_find_page", new=mock_find_page):
        async with WikipediaResearchScraper() as scraper:
            data = await scraper.research_show("I Love Lucy")
            assert isinstance(data, WikipediaData)
            assert data.title == "I Love Lucy"
            assert data.years == "1951-1957"
            assert data.premise.startswith("I Love Lucy is an American sitcom")
            assert str(data.source_url) == "https://en.wikipedia.org/wiki/I_Love_Lucy"

@pytest.mark.asyncio
async def test_research_show_page_not_found():
    """Test ValueError is raised if Wikipedia page not found."""
    async def mock_find_page(self, title):
        return None

    with patch.object(WikipediaResearchScraper, "_find_page", new=mock_find_page):
        async with WikipediaResearchScraper() as scraper:
            with pytest.raises(ValueError):
                await scraper.research_show("Nonexistent Show")

@pytest.mark.asyncio
async def test_find_page_variations():
    """Test that _find_page tries variations and returns the first found."""
    found_titles = []
    class DummyPage:
        def __init__(self, title, exists):
            self.title = title
            self._exists = exists
        def exists(self):
            return self._exists

    class DummyWiki:
        def page(self, title):
            found_titles.append(title)
            if title == "I Love Lucy (TV series)":
                return DummyPage(title, True)
            return DummyPage(title, False)

    scraper = WikipediaResearchScraper()
    scraper.wiki = DummyWiki()
    result = await scraper._find_page("I Love Lucy")
    assert result.title == "I Love Lucy (TV series)"
    assert "I Love Lucy (TV series)" in found_titles
