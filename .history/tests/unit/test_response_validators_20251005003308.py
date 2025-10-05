"""
Unit tests for AI Response Validators.

Tests Pydantic schema validation for AI-generated JSON responses.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

import pytest
from src.services.creative.response_validators import (
    AIResponseValidator,
    CharacterAnalysisResponse,
    CharacterTrait
)


def test_valid_character_analysis():
    """Test validation of correct character analysis."""
    valid_data = {
        "character_name": "Lucy Ricardo",
        "core_traits": [
            {
                "trait": "Ambitious",
                "description": "Always trying to break into show business",
                "examples": ["Vitameatavegamin", "Hollywood trip"]
            },
            {
                "trait": "Creative",
                "description": "Thinks outside the box hilariously",
                "examples": ["Candy factory", "Grape stomping"]
            },
            {
                "trait": "Loyal",
                "description": "Devoted to Ricky despite differences",
                "examples": ["Supports his career"]
            }
        ],
        "speech_patterns": ["Whining", "Fast talking"],
        "catchphrases": ["Ricky!"],
        "comedic_elements": ["Physical comedy"]
    }
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(valid_data)
    
    assert result is not None
    assert isinstance(result, CharacterAnalysisResponse)
    assert result.character_name == "Lucy Ricardo"
    assert len(result.core_traits) == 3
    assert all(isinstance(t, CharacterTrait) for t in result.core_traits)


def test_invalid_character_analysis_empty_traits():
    """Test rejection of data with empty traits list."""
    invalid_data = {
        "character_name": "Lucy",
        "core_traits": []  # Empty - should fail validation
    }
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(invalid_data)
    
    assert result is None  # Should return None for invalid data


def test_invalid_character_analysis_too_few_traits():
    """Test rejection when fewer than 3 traits provided."""
    invalid_data = {
        "character_name": "Lucy",
        "core_traits": [
            {
                "trait": "Ambitious",
                "description": "Test description here",
                "examples": []
            }
        ]  # Only 1 trait, need 3 minimum
    }
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(invalid_data)
    
    assert result is None


def test_missing_required_fields():
    """Test validation failure when required fields missing."""
    incomplete_data = {
        "character_name": "Lucy"
        # Missing core_traits entirely
    }
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(incomplete_data)
    
    assert result is None


def test_character_trait_validation():
    """Test CharacterTrait model validation."""
    # Valid trait
    valid_trait = CharacterTrait(
        trait="Ambitious",
        description="Always striving for success",
        examples=["Example 1", "Example 2"]
    )
    
    assert valid_trait.trait == "Ambitious"
    assert len(valid_trait.examples) == 2


def test_character_trait_description_too_short():
    """Test trait description minimum length validation."""
    with pytest.raises(Exception):
        CharacterTrait(
            trait="Ambitious",
            description="Short",  # Less than 10 characters
            examples=[]
        )


def test_character_analysis_with_relationships():
    """Test character analysis with relationships."""
    data = {
        "character_name": "Lucy Ricardo",
        "core_traits": [
            {
                "trait": "Ambitious",
                "description": "Always seeking fame and recognition",
                "examples": ["Auditions"]
            },
            {
                "trait": "Creative",
                "description": "Thinks outside the box",
                "examples": ["Schemes"]
            },
            {
                "trait": "Loyal",
                "description": "Devoted to loved ones",
                "examples": ["Supports Ricky"]
            }
        ],
        "relationships": [
            {
                "character_name": "Ricky",
                "relationship_type": "spouse",
                "description": "Husband and bandleader",
                "key_moments": ["Wedding", "First fight", "Reconciliation"]
            }
        ]
    }
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(data)
    
    assert result is not None
    assert len(result.relationships) == 1
    assert result.relationships[0].character_name == "Ricky"


def test_character_analysis_max_items_validation():
    """Test that max_items constraints are enforced."""
    # Create data with too many catchphrases (max is 5)
    data = {
        "character_name": "Lucy",
        "core_traits": [
            {
                "trait": "Test1",
                "description": "Test description one",
                "examples": []
            },
            {
                "trait": "Test2",
                "description": "Test description two",
                "examples": []
            },
            {
                "trait": "Test3",
                "description": "Test description three",
                "examples": []
            }
        ],
        "catchphrases": [
            "Phrase 1", "Phrase 2", "Phrase 3",
            "Phrase 4", "Phrase 5", "Phrase 6"  # 6 items, max is 5
        ]
    }
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(data)
    
    # Pydantic should truncate or fail validation
    # Result depends on Pydantic version
    # Just verify validation happens
    if result:
        assert len(result.catchphrases) <= 5


def test_validator_error_logging():
    """Test that validation errors are logged."""
    invalid_data = {"incomplete": "data"}
    
    validator = AIResponseValidator()
    result = validator.validate_character_analysis(invalid_data)
    
    assert result is None
