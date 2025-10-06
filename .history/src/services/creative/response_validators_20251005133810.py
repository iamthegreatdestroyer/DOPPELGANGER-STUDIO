"""
AI Response Validators - Pydantic schemas for structured AI outputs.

Validates that Claude and GPT-4 return properly structured JSON responses
for character analysis, narrative analysis, and transformations.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator, field_validator
import logging

logger = logging.getLogger(__name__)


# Character Analysis Schemas

class CharacterTrait(BaseModel):
    """Individual character trait."""
    trait: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    examples: List[str] = Field(default_factory=list, max_length=5)


class CharacterRelationship(BaseModel):
    """Relationship between two characters."""
    character_name: str
    relationship_type: str  # e.g., "spouse", "friend", "rival"
    description: str
    key_moments: List[str] = Field(default_factory=list, max_length=3)


class CharacterAnalysisResponse(BaseModel):
    """Complete character analysis from AI."""
    character_name: str = Field(..., min_length=1)
    core_traits: List[CharacterTrait] = Field(..., min_length=3, max_length=10)
    speech_patterns: List[str] = Field(default_factory=list, max_length=10)
    catchphrases: List[str] = Field(default_factory=list, max_length=5)
    relationships: List[CharacterRelationship] = Field(
        default_factory=list
    )
    character_arc: Optional[str] = None
    comedic_elements: List[str] = Field(default_factory=list, max_length=10)
    modern_parallels: List[str] = Field(default_factory=list, max_length=5)

    @field_validator('core_traits')
    @classmethod
    def validate_traits(cls, v):
        """Ensure at least 3 traits provided."""
        if len(v) < 3:
            raise ValueError("Must provide at least 3 core traits")
        return v


# Narrative Analysis Schemas

class PlotStructure(BaseModel):
    """Narrative plot structure."""
    structure_type: str  # "three-act", "episodic", "serialized"
    act_breakdown: Dict[str, str]
    typical_runtime: Optional[int] = None  # minutes


class RecurringPlotDevice(BaseModel):
    """Recurring narrative device."""
    device_name: str
    description: str
    frequency: str  # "every episode", "occasional", "rare"
    examples: List[str] = Field(default_factory=list, max_length=3)


class NarrativeAnalysisResponse(BaseModel):
    """Complete narrative analysis from AI."""
    show_title: str
    plot_structure: PlotStructure
    recurring_devices: List[RecurringPlotDevice] = Field(
        default_factory=list
    )
    opening_convention: Optional[str] = None
    closing_convention: Optional[str] = None
    b_plot_patterns: List[str] = Field(default_factory=list)
    pacing_notes: Optional[str] = None
    unique_signatures: List[str] = Field(default_factory=list, max_length=5)


# Transformation Rules Schemas

class SettingTransformation(BaseModel):
    """Transformation of setting/time period."""
    original_setting: str
    modern_equivalent: str
    justification: str
    cultural_references: List[str] = Field(
        default_factory=list, max_length=5
    )


class CharacterTransformation(BaseModel):
    """How a character transforms to modern context."""
    original_character: str
    original_archetype: str
    modern_archetype: str
    occupation_update: Optional[str] = None
    motivation_update: str
    technology_integration: List[str] = Field(default_factory=list)


class HumorTransformation(BaseModel):
    """Transformation of humor styles."""
    original_humor_type: str
    modern_humor_type: str
    example_transformations: List[Dict[str, str]] = Field(
        default_factory=list,
        max_length=5
    )


class TransformationRulesResponse(BaseModel):
    """Complete transformation ruleset from AI."""
    show_title: str
    setting_transformation: SettingTransformation
    character_transformations: List[CharacterTransformation] = Field(
        ...,
        min_length=1
    )
    humor_transformation: HumorTransformation
    cultural_updates: List[str] = Field(default_factory=list)
    technology_opportunities: List[str] = Field(default_factory=list)
    conflict_modernization: List[Dict[str, str]] = Field(
        default_factory=list
    )

    @field_validator('character_transformations')
    @classmethod
    def validate_characters(cls, v):
        """Ensure at least one character transformation."""
        if len(v) < 1:
            raise ValueError("Must transform at least one character")
        return v


# Validator Functions

class AIResponseValidator:
    """
    Validates AI responses against Pydantic schemas.

    Provides graceful error handling and logging for malformed responses.
    """

    @staticmethod
    def validate_character_analysis(
        response_data: Dict
    ) -> Optional[CharacterAnalysisResponse]:
        """
        Validate character analysis response.

        Args:
            response_data: Raw JSON from AI

        Returns:
            Validated CharacterAnalysisResponse or None if invalid

        Example:
            >>> validator = AIResponseValidator()
            >>> result = validator.validate_character_analysis(ai_json)
            >>> if result:
            ...     print(f"Valid: {len(result.core_traits)} traits")
            ... else:
            ...     print("Invalid response - retry needed")
        """
        try:
            validated = CharacterAnalysisResponse(**response_data)
            logger.info(
                f"Validated character analysis for "
                f"{validated.character_name}"
            )
            return validated

        except Exception as e:
            logger.error(f"Character analysis validation failed: {e}")
            logger.debug(f"Invalid data: {response_data}")
            return None

    @staticmethod
    def validate_narrative_analysis(
        response_data: Dict
    ) -> Optional[NarrativeAnalysisResponse]:
        """
        Validate narrative analysis response.

        Args:
            response_data: Raw JSON from AI

        Returns:
            Validated NarrativeAnalysisResponse or None if invalid
        """
        try:
            validated = NarrativeAnalysisResponse(**response_data)
            logger.info(
                f"Validated narrative analysis for {validated.show_title}"
            )
            return validated

        except Exception as e:
            logger.error(f"Narrative analysis validation failed: {e}")
            logger.debug(f"Invalid data: {response_data}")
            return None

    @staticmethod
    def validate_transformation_rules(
        response_data: Dict
    ) -> Optional[TransformationRulesResponse]:
        """
        Validate transformation rules response.

        Args:
            response_data: Raw JSON from AI

        Returns:
            Validated TransformationRulesResponse or None if invalid
        """
        try:
            validated = TransformationRulesResponse(**response_data)
            logger.info(
                f"Validated transformation rules for {validated.show_title}"
            )
            return validated

        except Exception as e:
            logger.error(f"Transformation rules validation failed: {e}")
            logger.debug(f"Invalid data: {response_data}")
            return None


# Example Usage
if __name__ == "__main__":
    # Example response data
    test_data = {
        "character_name": "Lucy Ricardo",
        "core_traits": [
            {
                "trait": "Ambitious",
                "description": "Always scheming to break into show business",
                "examples": [
                    "Auditions for Ricky's show",
                    "Hollywood episodes"
                ]
            },
            {
                "trait": "Creative",
                "description": "Thinks outside the box, often hilariously",
                "examples": ["Vitameatavegamin commercial", "Grape stomping"]
            },
            {
                "trait": "Loyal",
                "description": "Devoted to Ricky despite their differences",
                "examples": [
                    "Standing by Ricky's career",
                    "Supporting his dreams"
                ]
            }
        ],
        "speech_patterns": [
            "Whining voice when pleading",
            "Fast-talking when excited",
            "Elongated 'Ricky!' when upset"
        ],
        "catchphrases": [
            "Ricky!",
            "Waaah!",
            "I want to be in the show!"
        ],
        "comedic_elements": [
            "Physical comedy",
            "Facial expressions",
            "Slapstick situations"
        ]
    }

    validator = AIResponseValidator()
    result = validator.validate_character_analysis(test_data)

    if result:
        print(f"✅ Valid character analysis for {result.character_name}")
        print(f"   Traits: {len(result.core_traits)}")
        print(f"   Catchphrases: {len(result.catchphrases)}")
    else:
        print("❌ Validation failed")
