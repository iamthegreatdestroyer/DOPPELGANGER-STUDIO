"""
Unit tests for input validation.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from src.services.creative.input_validation import (
    InputValidator,
    ValidationSeverity,
    get_input_validator
)


class TestInputValidator:
    """Test input validation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.validator = InputValidator()
    
    def test_valid_show_data(self):
        """Test validation of valid show data."""
        show_data = {
            "title": "I Love Lucy",
            "years": "1951-1957",
            "genre": ["Sitcom"],
            "premise": "A housewife schemes to break into show business"
        }
        
        result = self.validator.validate_show_data(show_data)
        
        assert result.valid
        assert len(result.issues) == 0
    
    def test_missing_title(self):
        """Test validation fails without title."""
        show_data = {"years": "1950-1955"}
        
        result = self.validator.validate_show_data(show_data)
        
        assert not result.valid
        assert result.has_errors()
        assert any(i.field == "title" for i in result.issues)
    
    def test_invalid_years_format(self):
        """Test warning for invalid years format."""
        show_data = {
            "title": "Test Show",
            "years": "195X-196X"  # Invalid format
        }
        
        result = self.validator.validate_show_data(show_data)
        
        # Should be valid (just warning)
        assert result.valid
        assert result.has_warnings()
    
    def test_genre_sanitization(self):
        """Test genre conversion to list."""
        show_data = {
            "title": "Test Show",
            "genre": "Comedy"  # String instead of list
        }
        
        result = self.validator.validate_show_data(show_data)
        
        assert result.valid
        assert isinstance(result.sanitized_data["genre"], list)
        assert result.sanitized_data["genre"] == ["Comedy"]
    
    def test_title_truncation(self):
        """Test long title truncation."""
        long_title = "A" * 300
        show_data = {"title": long_title}
        
        result = self.validator.validate_show_data(show_data)
        
        assert result.valid  # Valid after sanitization
        assert len(result.sanitized_data["title"]) <= self.validator.max_title_length
    
    def test_validate_character_profiles(self):
        """Test character profile validation."""
        profiles = {
            "Lucy": {"traits": ["ambitious"]},
            "Ricky": {"traits": ["patient"]}
        }
        
        result = self.validator.validate_character_profiles(profiles)
        
        assert result.valid
        assert len(result.issues) == 0
    
    def test_empty_profiles(self):
        """Test validation fails with empty profiles."""
        result = self.validator.validate_character_profiles({})
        
        assert not result.valid
        assert result.has_errors()
    
    def test_validate_episode_outline(self):
        """Test episode outline validation."""
        outline = {
            "scenes": [
                {
                    "scene_number": 1,
                    "location": "Living Room",
                    "characters": ["Lucy", "Ricky"],
                    "description": "Lucy has an idea"
                }
            ]
        }
        
        result = self.validator.validate_episode_outline(outline)
        
        assert result.valid
    
    def test_missing_scenes(self):
        """Test validation fails without scenes."""
        outline = {}
        
        result = self.validator.validate_episode_outline(outline)
        
        assert not result.valid
        assert any(i.field == "scenes" for i in result.issues)
    
    def test_incomplete_scene(self):
        """Test validation fails with incomplete scene."""
        outline = {
            "scenes": [
                {"scene_number": 1}  # Missing required fields
            ]
        }
        
        result = self.validator.validate_episode_outline(outline)
        
        assert not result.valid
        assert result.has_errors()
    
    def test_sanitize_text_input(self):
        """Test text sanitization."""
        # Text with control characters and extra whitespace
        dirty_text = "Test\x00text  with\x0Bcontrol   chars"
        
        clean = self.validator.sanitize_text_input(dirty_text)
        
        assert "\x00" not in clean
        assert "\x0B" not in clean
        assert "  " not in clean  # Normalized whitespace
    
    def test_text_truncation(self):
        """Test text truncation during sanitization."""
        long_text = "A" * 1000
        
        clean = self.validator.sanitize_text_input(long_text, max_length=100)
        
        assert len(clean) == 100
    
    def test_global_instance(self):
        """Test global validator instance."""
        v1 = get_input_validator()
        v2 = get_input_validator()
        
        assert v1 is v2  # Same instance
