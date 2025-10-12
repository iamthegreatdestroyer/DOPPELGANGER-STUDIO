"""
Unit tests for pattern integration module.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from src.services.creative.pattern_integration import (
    PatternIntegrator,
    PatternMatch,
    PatternAnalysisResult
)
from src.services.creative.humor_pattern_library import ComedyEra, ComedyType


class TestPatternIntegrator:
    """Test pattern integration functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.integrator = PatternIntegrator(confidence_threshold=0.5)
    
    def test_analyze_show_patterns(self):
        """Test pattern analysis for a show."""
        show_data = {
            "title": "I Love Lucy",
            "years": "1951-1957",
            "genre": ["Sitcom"],
            "themes": ["Marriage", "Ambition", "Comedy"],
            "premise": "A housewife schemes to break into show business"
        }
        
        result = self.integrator.analyze_show_patterns(show_data)
        
        assert isinstance(result, PatternAnalysisResult)
        assert result.show_title == "I Love Lucy"
        assert result.era == ComedyEra.GOLDEN_AGE_1950s
        assert len(result.detected_patterns) > 0
        assert result.confidence_score > 0
    
    def test_pattern_confidence_threshold(self):
        """Test confidence threshold filtering."""
        high_threshold_integrator = PatternIntegrator(confidence_threshold=0.9)
        
        show_data = {
            "title": "Test Show",
            "years": "1950-1955",
            "genre": ["Comedy"]
        }
        
        result = high_threshold_integrator.analyze_show_patterns(show_data)
        
        # High threshold should filter out low-confidence matches
        for match in result.detected_patterns:
            assert match.confidence >= 0.9
    
    def test_era_determination(self):
        """Test era determination from years."""
        integrator = PatternIntegrator()
        
        test_cases = [
            ("1951-1957", ComedyEra.GOLDEN_AGE_1950s),
            ("1965-1970", ComedyEra.RURAL_1960s),
            ("1975-1980", ComedyEra.RELEVANT_1970s),
            ("1985-1990", ComedyEra.FAMILY_1980s),
        ]
        
        for years, expected_era in test_cases:
            era = integrator._determine_era(years)
            assert era == expected_era
    
    def test_comedy_type_determination(self):
        """Test comedy type determination."""
        integrator = PatternIntegrator()
        
        # Physical comedy
        comedy_type = integrator._determine_comedy_type(
            ["Physical Comedy", "Slapstick"],
            ["Physical humor"]
        )
        assert comedy_type == ComedyType.PHYSICAL
        
        # Character comedy
        comedy_type = integrator._determine_comedy_type(
            ["Sitcom"],
            ["Family", "Relationships"]
        )
        assert comedy_type == ComedyType.CHARACTER
    
    def test_generate_transformation_guide(self):
        """Test transformation guide generation."""
        show_data = {
            "title": "I Love Lucy",
            "years": "1951-1957",
            "genre": ["Sitcom"],
            "premise": "Housewife schemes for show business"
        }
        
        result = self.integrator.analyze_show_patterns(show_data)
        guide = self.integrator.generate_transformation_guide(result)
        
        assert guide["show_title"] == "I Love Lucy"
        assert guide["total_patterns"] > 0
        assert "pattern_transformations" in guide
        assert len(guide["pattern_transformations"]) > 0
    
    def test_export_analysis_report(self):
        """Test analysis report export."""
        show_data = {
            "title": "Test Show",
            "years": "1950-1955",
            "genre": ["Comedy"]
        }
        
        result = self.integrator.analyze_show_patterns(show_data)
        report = self.integrator.export_analysis_report(result)
        
        assert "Test Show" in report
        assert "PATTERN ANALYSIS REPORT" in report
        assert "DETECTED PATTERNS" in report
        assert len(report) > 100


def test_pattern_match_dataclass():
    """Test PatternMatch dataclass."""
    match = PatternMatch(
        pattern_id="test_pattern",
        pattern_name="Test Pattern",
        confidence=0.85,
        evidence=["Evidence 1", "Evidence 2"],
        frequency_estimate="weekly",
        modernization_priority=3
    )
    
    assert match.pattern_id == "test_pattern"
    assert match.confidence == 0.85
    assert len(match.evidence) == 2
    assert match.modernization_priority == 3
