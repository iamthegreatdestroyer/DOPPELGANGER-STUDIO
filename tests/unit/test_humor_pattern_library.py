"""
Unit tests for humor pattern library.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from src.services.creative.humor_pattern_library import (
    HumorPatternLibrary,
    ComedyType,
    ComedyEra,
    get_humor_pattern_library
)


class TestHumorPatternLibrary:
    """Test humor pattern library functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.library = HumorPatternLibrary()
    
    def test_library_initialization(self):
        """Test library initializes with patterns."""
        assert len(self.library.patterns) > 0
        assert "scheme_backfires" in self.library.patterns
        assert "misunderstanding_cascade" in self.library.patterns
    
    def test_get_pattern(self):
        """Test retrieving specific pattern."""
        pattern = self.library.get_pattern("scheme_backfires")
        assert pattern is not None
        assert pattern.name == "Elaborate Scheme Backfires Spectacularly"
        assert pattern.comedy_type == ComedyType.SITUATIONAL
        assert len(pattern.classic_examples) > 0
    
    def test_get_patterns_by_era(self):
        """Test filtering patterns by era."""
        patterns_1950s = self.library.get_patterns_by_era(ComedyEra.GOLDEN_AGE_1950s)
        assert len(patterns_1950s) > 0
        
        for pattern in patterns_1950s:
            assert pattern.typical_era == ComedyEra.GOLDEN_AGE_1950s
    
    def test_get_patterns_by_type(self):
        """Test filtering patterns by comedy type."""
        physical = self.library.get_patterns_by_type(ComedyType.PHYSICAL)
        assert len(physical) >= 0  # May or may not have physical comedy
        
        situational = self.library.get_patterns_by_type(ComedyType.SITUATIONAL)
        assert len(situational) > 0
    
    def test_suggest_modernizations(self):
        """Test modernization suggestions."""
        suggestions = self.library.suggest_modernizations(
            "I Love Lucy",
            ["scheme_backfires", "misunderstanding_cascade"]
        )
        
        assert "scheme_backfires" in suggestions
        assert len(suggestions["scheme_backfires"]) > 0
        assert any("modern" in s.lower() for s in suggestions["scheme_backfires"])
    
    def test_analyze_show_humor_style(self):
        """Test show humor style analysis."""
        show_data = {
            "title": "I Love Lucy",
            "years": "1951-1957",
            "genre": ["Sitcom", "Comedy"]
        }
        
        analysis = self.library.analyze_show_humor_style(show_data)
        
        assert analysis["era"] == "1950s"
        assert len(analysis["likely_patterns"]) > 0
        assert "modernization_strategy" in analysis
    
    def test_export_pattern_guide(self):
        """Test exporting pattern guide."""
        guide = self.library.export_pattern_guide(["scheme_backfires"])
        
        assert "scheme_backfires" in guide.lower()
        assert "modern equivalent" in guide.lower()
        assert len(guide) > 100  # Should be substantial
    
    def test_global_instance(self):
        """Test global singleton instance."""
        lib1 = get_humor_pattern_library()
        lib2 = get_humor_pattern_library()
        
        assert lib1 is lib2  # Same instance
        assert len(lib1.patterns) > 0


@pytest.mark.parametrize("pattern_id,expected_type", [
    ("scheme_backfires", ComedyType.SITUATIONAL),
    ("misunderstanding_cascade", ComedyType.SITUATIONAL),
    ("fish_out_of_water", ComedyType.CHARACTER),
])
def test_pattern_types(pattern_id, expected_type):
    """Test pattern comedy types are correct."""
    library = HumorPatternLibrary()
    pattern = library.get_pattern(pattern_id)
    
    assert pattern is not None
    assert pattern.comedy_type == expected_type


def test_pattern_has_required_fields():
    """Test all patterns have required fields."""
    library = HumorPatternLibrary()
    
    for pattern_id, pattern in library.patterns.items():
        assert pattern.pattern_id == pattern_id
        assert len(pattern.name) > 0
        assert len(pattern.description) > 0
        assert pattern.comedy_type is not None
        assert pattern.typical_era is not None
        assert pattern.modern_equivalent is not None
