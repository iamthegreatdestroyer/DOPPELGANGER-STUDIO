"""
Input Validation & Sanitization - Comprehensive input validation for all components.

Provides validation utilities for show data, analysis inputs, script generation
parameters, and API inputs to prevent errors and ensure data quality.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Any, Set
import re
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity."""
    ERROR = "error"  # Invalid, cannot proceed
    WARNING = "warning"  # Problematic but usable
    INFO = "info"  # Informational note


@dataclass
class ValidationIssue:
    """A validation issue."""
    field: str
    message: str
    severity: ValidationSeverity
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    issues: List[ValidationIssue]
    sanitized_data: Optional[Dict] = None
    
    def has_errors(self) -> bool:
        return any(i.severity == ValidationSeverity.ERROR for i in self.issues)
    
    def has_warnings(self) -> bool:
        return any(i.severity == ValidationSeverity.WARNING for i in self.issues)


class InputValidator:
    """
    Comprehensive input validation system.
    
    Validates and sanitizes inputs for all system components to prevent
    errors and ensure data quality.
    """
    
    def __init__(self):
        self.min_title_length = 1
        self.max_title_length = 200
        self.min_premise_length = 10
        self.max_premise_length = 5000
        
    def validate_show_data(self, show_data: Dict) -> ValidationResult:
        """Validate show research data."""
        issues = []
        sanitized = show_data.copy()
        
        # Required fields
        if not show_data.get('title'):
            issues.append(ValidationIssue(
                'title', 'Title is required', ValidationSeverity.ERROR,
                'Provide show title'
            ))
        elif len(show_data['title']) < self.min_title_length:
            issues.append(ValidationIssue(
                'title', f'Title too short (min {self.min_title_length})',
                ValidationSeverity.ERROR
            ))
        elif len(show_data['title']) > self.max_title_length:
            sanitized['title'] = show_data['title'][:self.max_title_length]
            issues.append(ValidationIssue(
                'title', 'Title truncated to max length',
                ValidationSeverity.WARNING
            ))
        
        # Validate years format
        years = show_data.get('years', '')
        if years and not re.match(r'^\d{4}(-\d{4})?$', years):
            issues.append(ValidationIssue(
                'years', f'Invalid years format: {years}',
                ValidationSeverity.WARNING,
                'Use format YYYY or YYYY-YYYY'
            ))
        
        # Validate genres
        if 'genre' in show_data:
            if isinstance(show_data['genre'], str):
                sanitized['genre'] = [show_data['genre']]
            elif not isinstance(show_data['genre'], list):
                issues.append(ValidationIssue(
                    'genre', 'Genre must be string or list',
                    ValidationSeverity.ERROR
                ))
        
        return ValidationResult(
            valid=not any(i.severity == ValidationSeverity.ERROR for i in issues),
            issues=issues,
            sanitized_data=sanitized
        )
    
    def validate_character_profiles(self, profiles: Dict) -> ValidationResult:
        """Validate character voice profiles."""
        issues = []
        
        if not profiles:
            issues.append(ValidationIssue(
                'profiles', 'No character profiles provided',
                ValidationSeverity.ERROR
            ))
            return ValidationResult(valid=False, issues=issues)
        
        for name, profile in profiles.items():
            if not isinstance(profile, dict):
                issues.append(ValidationIssue(
                    f'profile.{name}', 'Profile must be dict',
                    ValidationSeverity.ERROR
                ))
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )
    
    def validate_episode_outline(self, outline: Dict) -> ValidationResult:
        """Validate episode outline structure."""
        issues = []
        
        if 'scenes' not in outline:
            issues.append(ValidationIssue(
                'scenes', 'Episode must have scenes',
                ValidationSeverity.ERROR
            ))
            return ValidationResult(valid=False, issues=issues)
        
        scenes = outline['scenes']
        if not isinstance(scenes, list) or len(scenes) == 0:
            issues.append(ValidationIssue(
                'scenes', 'Must have at least one scene',
                ValidationSeverity.ERROR
            ))
        
        # Validate each scene
        for i, scene in enumerate(scenes):
            required = ['scene_number', 'location', 'characters', 'description']
            for field in required:
                if field not in scene:
                    issues.append(ValidationIssue(
                        f'scene[{i}].{field}',
                        f'Scene {i+1} missing required field',
                        ValidationSeverity.ERROR
                    ))
        
        return ValidationResult(
            valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            issues=issues
        )
    
    def sanitize_text_input(self, text: str, max_length: Optional[int] = None) -> str:
        """Sanitize text input by removing problematic characters."""
        # Remove control characters except newlines/tabs
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()


# Global validator instance
_validator_instance = None

def get_input_validator() -> InputValidator:
    """Get global input validator."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = InputValidator()
    return _validator_instance
