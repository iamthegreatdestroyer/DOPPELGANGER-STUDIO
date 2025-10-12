"""
Pattern Integration Module - Connects humor pattern library to analysis systems.

Provides seamless integration between the humor pattern library and the
narrative analyzer and transformation engine, enabling automatic pattern
detection, matching, and transformation suggestions.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Set, Tuple
import logging
from dataclasses import dataclass, field

from src.services.creative.humor_pattern_library import (
    HumorPatternLibrary,
    HumorPattern,
    ComedyType,
    ComedyEra,
    get_humor_pattern_library
)

logger = logging.getLogger(__name__)


@dataclass
class PatternMatch:
    """A detected pattern match in show analysis."""
    pattern_id: str
    pattern_name: str
    confidence: float  # 0.0-1.0
    evidence: List[str]  # Text snippets that suggest this pattern
    frequency_estimate: str  # "every episode", "weekly", "occasional"
    modernization_priority: int  # 1-5, higher = more important


@dataclass
class PatternAnalysisResult:
    """Complete pattern analysis for a show."""
    show_title: str
    detected_patterns: List[PatternMatch]
    era: ComedyEra
    primary_comedy_type: ComedyType
    modernization_suggestions: Dict[str, List[str]]
    transformation_priorities: List[str]
    pattern_count: int
    confidence_score: float


class PatternIntegrator:
    """
    Integrates humor pattern library with narrative and transformation systems.
    
    Provides automatic pattern detection, matching, and transformation
    suggestion generation based on show analysis data.
    
    Example:
        >>> integrator = PatternIntegrator()
        >>> result = integrator.analyze_show_patterns(show_data, narrative_analysis)
        >>> print(f"Found {len(result.detected_patterns)} patterns")
        >>> suggestions = integrator.generate_transformation_suggestions(result)
    """
    
    def __init__(
        self,
        humor_library: Optional[HumorPatternLibrary] = None,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize pattern integrator.
        
        Args:
            humor_library: Humor pattern library instance (or use global)
            confidence_threshold: Minimum confidence for pattern matches
        """
        self.humor_library = humor_library or get_humor_pattern_library()
        self.confidence_threshold = confidence_threshold
        logger.info(f"PatternIntegrator initialized (threshold={confidence_threshold})")
    
    def analyze_show_patterns(
        self,
        show_data: Dict,
        narrative_analysis: Optional[Dict] = None,
        character_analysis: Optional[Dict] = None
    ) -> PatternAnalysisResult:
        """
        Analyze show to detect comedy patterns.
        
        Combines show metadata, narrative analysis, and character analysis
        to identify likely comedy patterns and their modernization needs.
        
        Args:
            show_data: Show information (title, years, genre, themes, etc.)
            narrative_analysis: Optional narrative structure analysis
            character_analysis: Optional character analysis results
            
        Returns:
            PatternAnalysisResult with detected patterns and suggestions
            
        Example:
            >>> show_data = {
            ...     "title": "I Love Lucy",
            ...     "years": "1951-1957",
            ...     "genre": ["Sitcom"],
            ...     "themes": ["Marriage", "Ambition", "Show Business"],
            ...     "premise": "Housewife schemes to break into showbiz"
            ... }
            >>> result = integrator.analyze_show_patterns(show_data)
            >>> for match in result.detected_patterns:
            ...     print(f"{match.pattern_name}: {match.confidence:.2f}")
        """
        logger.info(f"Analyzing patterns for: {show_data.get('title')}")
        
        # Determine era from years
        era = self._determine_era(show_data.get('years', ''))
        
        # Determine primary comedy type from genre and themes
        comedy_type = self._determine_comedy_type(
            show_data.get('genre', []),
            show_data.get('themes', [])
        )
        
        # Get candidate patterns for this era
        candidate_patterns = self.humor_library.get_patterns_by_era(era)
        
        # Match patterns against show data
        detected_patterns = self._match_patterns(
            show_data,
            candidate_patterns,
            narrative_analysis,
            character_analysis
        )
        
        # Filter by confidence
        detected_patterns = [
            p for p in detected_patterns
            if p.confidence >= self.confidence_threshold
        ]
        
        # Sort by confidence
        detected_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        # Generate modernization suggestions
        modernization_suggestions = self.humor_library.suggest_modernizations(
            show_data.get('title', 'Unknown'),
            [p.pattern_id for p in detected_patterns]
        )
        
        # Prioritize transformations
        transformation_priorities = self._prioritize_transformations(
            detected_patterns,
            era,
            comedy_type
        )
        
        # Calculate overall confidence
        overall_confidence = (
            sum(p.confidence for p in detected_patterns) / len(detected_patterns)
            if detected_patterns else 0.0
        )
        
        result = PatternAnalysisResult(
            show_title=show_data.get('title', 'Unknown'),
            detected_patterns=detected_patterns,
            era=era,
            primary_comedy_type=comedy_type,
            modernization_suggestions=modernization_suggestions,
            transformation_priorities=transformation_priorities,
            pattern_count=len(detected_patterns),
            confidence_score=overall_confidence
        )
        
        logger.info(
            f"Pattern analysis complete: {len(detected_patterns)} patterns detected "
            f"(confidence: {overall_confidence:.2f})"
        )
        
        return result
    
    def _determine_era(self, years: str) -> ComedyEra:
        """Determine comedy era from year string."""
        if "195" in years:
            return ComedyEra.GOLDEN_AGE_1950s
        elif "196" in years:
            return ComedyEra.RURAL_1960s
        elif "197" in years:
            return ComedyEra.RELEVANT_1970s
        elif "198" in years:
            return ComedyEra.FAMILY_1980s
        elif "199" in years:
            return ComedyEra.IRONIC_1990s
        elif "200" in years:
            return ComedyEra.CRINGE_2000s
        else:
            return ComedyEra.STREAMING_2010s
    
    def _determine_comedy_type(
        self,
        genres: List[str],
        themes: List[str]
    ) -> ComedyType:
        """Determine primary comedy type from genres and themes."""
        genre_str = " ".join(genres).lower() if genres else ""
        theme_str = " ".join(themes).lower() if themes else ""
        combined = f"{genre_str} {theme_str}"
        
        # Check for physical comedy indicators
        if any(keyword in combined for keyword in ["physical", "slapstick", "farce"]):
            return ComedyType.PHYSICAL
        
        # Check for character comedy
        if any(keyword in combined for keyword in ["character", "family", "relationships"]):
            return ComedyType.CHARACTER
        
        # Check for verbal comedy
        if any(keyword in combined for keyword in ["wit", "wordplay", "dialogue"]):
            return ComedyType.VERBAL
        
        # Check for satire
        if any(keyword in combined for keyword in ["satire", "political", "social"]):
            return ComedyType.SATIRE
        
        # Default to situational
        return ComedyType.SITUATIONAL
    
    def _match_patterns(
        self,
        show_data: Dict,
        candidate_patterns: List[HumorPattern],
        narrative_analysis: Optional[Dict],
        character_analysis: Optional[Dict]
    ) -> List[PatternMatch]:
        """
        Match candidate patterns against show data.
        
        Uses multiple signals to determine pattern presence:
        - Genre and theme keywords
        - Narrative structure indicators
        - Character trait patterns
        - Era-typical patterns
        """
        matches = []
        
        # Extract searchable text
        premise = show_data.get('premise', '') + show_data.get('plot_summary', '')
        themes = " ".join(show_data.get('themes', []))
        
        # Add narrative analysis text if available
        narrative_text = ""
        if narrative_analysis:
            narrative_text = narrative_analysis.get('pacing_notes', '')
            if 'recurring_devices' in narrative_analysis:
                for device in narrative_analysis.get('recurring_devices', []):
                    if isinstance(device, dict):
                        narrative_text += " " + device.get('description', '')
        
        # Add character analysis text if available
        character_text = ""
        if character_analysis:
            for char in character_analysis.get('characters', []):
                if isinstance(char, dict):
                    character_text += " " + char.get('description', '')
                    traits = char.get('traits', [])
                    if isinstance(traits, list):
                        character_text += " " + " ".join(traits)
        
        # Combine all searchable text
        searchable = f"{premise} {themes} {narrative_text} {character_text}".lower()
        
        for pattern in candidate_patterns:
            confidence, evidence = self._calculate_pattern_confidence(
                pattern,
                searchable,
                show_data
            )
            
            if confidence > 0:
                matches.append(PatternMatch(
                    pattern_id=pattern.pattern_id,
                    pattern_name=pattern.name,
                    confidence=confidence,
                    evidence=evidence,
                    frequency_estimate=self._estimate_frequency(confidence),
                    modernization_priority=self._calculate_priority(
                        pattern,
                        confidence
                    )
                ))
        
        return matches
    
    def _calculate_pattern_confidence(
        self,
        pattern: HumorPattern,
        searchable_text: str,
        show_data: Dict
    ) -> Tuple[float, List[str]]:
        """
        Calculate confidence that pattern is present in show.
        
        Returns:
            Tuple of (confidence_score, evidence_snippets)
        """
        confidence = 0.0
        evidence = []
        
        # Check pattern keywords in description
        pattern_keywords = self._extract_keywords(pattern.description)
        keyword_matches = sum(
            1 for keyword in pattern_keywords
            if keyword in searchable_text
        )
        
        if keyword_matches > 0:
            confidence += min(0.3, keyword_matches * 0.1)
            evidence.append(f"Keyword matches: {keyword_matches}")
        
        # Check pattern tags
        if pattern.tags:
            tag_matches = sum(
                1 for tag in pattern.tags
                if tag in searchable_text
            )
            if tag_matches > 0:
                confidence += min(0.2, tag_matches * 0.1)
                evidence.append(f"Tag matches: {tag_matches}")
        
        # Check classic examples match
        for example in pattern.classic_examples:
            example_show = example.get('show', '').lower()
            if example_show in show_data.get('title', '').lower():
                confidence += 0.4
                evidence.append(f"Classic example match: {example_show}")
                break
        
        # Boost confidence for era match
        show_years = show_data.get('years', '')
        if str(pattern.typical_era.value) in show_years:
            confidence += 0.1
            evidence.append(f"Era match: {pattern.typical_era.value}")
        
        return min(confidence, 1.0), evidence
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction (could be enhanced with NLP)
        stopwords = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'
        }
        
        words = text.lower().split()
        keywords = [
            word.strip('.,!?;:') for word in words
            if len(word) > 3 and word not in stopwords
        ]
        
        return keywords
    
    def _estimate_frequency(self, confidence: float) -> str:
        """Estimate how often pattern appears based on confidence."""
        if confidence >= 0.8:
            return "every episode"
        elif confidence >= 0.6:
            return "weekly"
        else:
            return "occasional"
    
    def _calculate_priority(
        self,
        pattern: HumorPattern,
        confidence: float
    ) -> int:
        """Calculate modernization priority (1-5)."""
        # Start with confidence-based priority
        if confidence >= 0.9:
            base_priority = 5
        elif confidence >= 0.8:
            base_priority = 4
        elif confidence >= 0.7:
            base_priority = 3
        elif confidence >= 0.6:
            base_priority = 2
        else:
            base_priority = 1
        
        # Boost for patterns with modernization challenges
        if pattern.modernization_challenges:
            base_priority = min(5, base_priority + 1)
        
        return base_priority
    
    def _prioritize_transformations(
        self,
        detected_patterns: List[PatternMatch],
        era: ComedyEra,
        comedy_type: ComedyType
    ) -> List[str]:
        """Generate prioritized list of transformation focuses."""
        priorities = []
        
        # High-confidence patterns first
        high_confidence = [
            p for p in detected_patterns
            if p.confidence >= 0.8
        ]
        
        if high_confidence:
            priorities.append(
                f"Modernize {len(high_confidence)} high-confidence patterns first"
            )
        
        # Era-specific priorities
        if era == ComedyEra.GOLDEN_AGE_1950s:
            priorities.append("Update gender dynamics and social roles")
            priorities.append("Replace physical labor with digital equivalents")
        elif era == ComedyEra.RURAL_1960s:
            priorities.append("Transform rural/urban divide to digital/analog divide")
        elif era == ComedyEra.FAMILY_1980s:
            priorities.append("Modernize family structures and communication")
        
        # Comedy type priorities
        if comedy_type == ComedyType.PHYSICAL:
            priorities.append("Adapt physical comedy to viral video context")
        elif comedy_type == ComedyType.VERBAL:
            priorities.append("Update wordplay and references for modern audience")
        
        # Pattern-specific priorities
        pattern_ids = [p.pattern_id for p in detected_patterns]
        if "scheme_backfires" in pattern_ids:
            priorities.append("Add social media amplification to schemes")
        if "misunderstanding_cascade" in pattern_ids:
            priorities.append("Leverage text/DM miscommunication")
        
        return priorities[:5]  # Top 5 priorities
    
    def generate_transformation_guide(
        self,
        analysis_result: PatternAnalysisResult
    ) -> Dict[str, any]:
        """
        Generate comprehensive transformation guide.
        
        Creates detailed recommendations for adapting the show's
        comedy patterns to modern contexts.
        
        Args:
            analysis_result: Pattern analysis results
            
        Returns:
            Dict with transformation guide details
        """
        guide = {
            'show_title': analysis_result.show_title,
            'total_patterns': analysis_result.pattern_count,
            'confidence': analysis_result.confidence_score,
            'era': analysis_result.era.value,
            'primary_type': analysis_result.primary_comedy_type.value,
            'priorities': analysis_result.transformation_priorities,
            'pattern_transformations': []
        }
        
        for match in analysis_result.detected_patterns:
            pattern = self.humor_library.get_pattern(match.pattern_id)
            if pattern:
                guide['pattern_transformations'].append({
                    'pattern_name': match.pattern_name,
                    'confidence': match.confidence,
                    'frequency': match.frequency_estimate,
                    'priority': match.modernization_priority,
                    'modern_equivalent': pattern.modern_equivalent,
                    'transformation_notes': pattern.transformation_notes,
                    'recommended_updates': pattern.recommended_updates[:3]
                })
        
        return guide
    
    def export_analysis_report(
        self,
        analysis_result: PatternAnalysisResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export pattern analysis as formatted report.
        
        Args:
            analysis_result: Pattern analysis results
            output_path: Optional file path to save report
            
        Returns:
            Formatted report text
        """
        report = f"# PATTERN ANALYSIS REPORT: {analysis_result.show_title}\n\n"
        
        report += f"**Era:** {analysis_result.era.value}\n"
        report += f"**Primary Comedy Type:** {analysis_result.primary_comedy_type.value}\n"
        report += f"**Patterns Detected:** {analysis_result.pattern_count}\n"
        report += f"**Overall Confidence:** {analysis_result.confidence_score:.2f}\n\n"
        
        report += "## DETECTED PATTERNS\n\n"
        for i, match in enumerate(analysis_result.detected_patterns, 1):
            report += f"### {i}. {match.pattern_name}\n"
            report += f"- **Confidence:** {match.confidence:.2f}\n"
            report += f"- **Frequency:** {match.frequency_estimate}\n"
            report += f"- **Priority:** {match.modernization_priority}/5\n"
            report += f"- **Evidence:** {', '.join(match.evidence)}\n\n"
        
        report += "## TRANSFORMATION PRIORITIES\n\n"
        for i, priority in enumerate(analysis_result.transformation_priorities, 1):
            report += f"{i}. {priority}\n"
        
        report += "\n## MODERNIZATION SUGGESTIONS\n\n"
        for pattern_id, suggestions in analysis_result.modernization_suggestions.items():
            pattern = self.humor_library.get_pattern(pattern_id)
            if pattern:
                report += f"### {pattern.name}\n"
                for suggestion in suggestions:
                    report += f"- {suggestion}\n"
                report += "\n"
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Analysis report exported to: {output_path}")
        
        return report


# Example usage
if __name__ == "__main__":
    integrator = PatternIntegrator()
    
    # Example show data
    show_data = {
        "title": "I Love Lucy",
        "years": "1951-1957",
        "genre": ["Sitcom", "Comedy"],
        "themes": ["Marriage", "Ambition", "Show Business", "Friendship"],
        "premise": (
            "A wacky redhead schemes to break into show business while "
            "her Cuban bandleader husband tries to keep her grounded."
        ),
        "setting": "1950s New York"
    }
    
    # Analyze patterns
    result = integrator.analyze_show_patterns(show_data)
    
    print(f"\n{'='*60}")
    print(f"PATTERN ANALYSIS: {result.show_title}")
    print(f"{'='*60}\n")
    print(f"Era: {result.era.value}")
    print(f"Comedy Type: {result.primary_comedy_type.value}")
    print(f"Patterns Detected: {result.pattern_count}")
    print(f"Confidence: {result.confidence_score:.2f}\n")
    
    print("TOP DETECTED PATTERNS:")
    for i, match in enumerate(result.detected_patterns[:5], 1):
        print(f"{i}. {match.pattern_name} ({match.confidence:.2f})")
        print(f"   Frequency: {match.frequency_estimate}")
        print(f"   Priority: {match.modernization_priority}/5\n")
    
    print("TRANSFORMATION PRIORITIES:")
    for priority in result.transformation_priorities:
        print(f"- {priority}")
    
    # Generate transformation guide
    guide = integrator.generate_transformation_guide(result)
    print(f"\nGenerated transformation guide with {len(guide['pattern_transformations'])} patterns")
