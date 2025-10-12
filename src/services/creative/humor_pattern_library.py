"""
Humor Pattern Library - Comprehensive catalog of classic TV comedy patterns.

Provides pattern recognition, modern equivalents, and transformation guidance
for adapting classic comedy to contemporary contexts while preserving timing
and effectiveness.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ComedyType(Enum):
    """Types of comedy patterns."""
    PHYSICAL = "physical"
    VERBAL = "verbal"
    SITUATIONAL = "situational"
    CHARACTER = "character"
    OBSERVATIONAL = "observational"
    ABSURD = "absurd"
    SATIRE = "satire"
    CRINGE = "cringe"
    META = "meta"


class ComedyEra(Enum):
    """TV comedy eras."""
    GOLDEN_AGE_1950s = "1950s"  # I Love Lucy, Honeymooners
    RURAL_1960s = "1960s"  # Andy Griffith, Beverly Hillbillies
    RELEVANT_1970s = "1970s"  # All in the Family, M*A*S*H
    FAMILY_1980s = "1980s"  # Cosby, Family Ties
    IRONIC_1990s = "1990s"  # Seinfeld, Friends
    CRINGE_2000s = "2000s"  # Office, Arrested Development
    STREAMING_2010s = "2010s"  # Modern streaming era


@dataclass
class HumorPattern:
    """A catalogued comedy pattern."""
    pattern_id: str
    name: str
    description: str
    comedy_type: ComedyType
    typical_era: ComedyEra
    classic_examples: List[Dict[str, str]]  # show, episode, description
    modern_equivalent: str
    transformation_notes: str
    timing_requirements: str
    setup_requirements: List[str]
    payoff_characteristics: List[str]
    modernization_challenges: List[str]
    recommended_updates: List[str]
    tags: Set[str] = field(default_factory=set)


class HumorPatternLibrary:
    """
    Comprehensive library of TV comedy patterns.
    
    Catalogs classic TV comedy techniques with guidance on modernizing
    them while preserving effectiveness. Used by narrative analyzer
    and transformation engine.
    
    Example:
        >>> library = HumorPatternLibrary()
        >>> pattern = library.get_pattern("scheme_backfires")
        >>> print(f"Modern: {pattern.modern_equivalent}")
        >>> suggestions = library.suggest_modernizations(
        ...     "I Love Lucy", ["scheme_backfires", "misunderstanding"]
        ... )
    """
    
    def __init__(self):
        """Initialize pattern library with comprehensive catalog."""
        self.patterns: Dict[str, HumorPattern] = {}
        self._initialize_patterns()
        logger.info(f"Humor pattern library initialized: {len(self.patterns)} patterns")
    
    def _initialize_patterns(self):
        """Load all comedy pattern definitions."""
        
        # Pattern 1: Scheme Backfires
        self.patterns["scheme_backfires"] = HumorPattern(
            pattern_id="scheme_backfires",
            name="Elaborate Scheme Backfires Spectacularly",
            description=(
                "Character devises intricate plan to achieve goal, but "
                "cascading complications cause spectacular failure"
            ),
            comedy_type=ComedyType.SITUATIONAL,
            typical_era=ComedyEra.GOLDEN_AGE_1950s,
            classic_examples=[
                {
                    "show": "I Love Lucy",
                    "episode": "Job Switching",
                    "description": "Lucy and Ethel work at candy factory, can't keep up with conveyor belt"
                },
                {
                    "show": "I Love Lucy",
                    "episode": "Lucy Does a TV Commercial",
                    "description": "Lucy gets drunk on Vitameatavegamin during rehearsal"
                }
            ],
            modern_equivalent=(
                "Social media plan goes viral for wrong reasons, MLM scheme "
                "exposed, elaborate surprise party ruined by Ring doorbell"
            ),
            transformation_notes=(
                "Replace physical labor jobs with gig economy tasks. "
                "Update product endorsement to influencer sponsorship. "
                "Add technology layer that amplifies failure publicly."
            ),
            timing_requirements="Long setup (2-3 minutes), escalating complications, explosive payoff",
            setup_requirements=[
                "Character's strong motivation established",
                "Plan seems plausible initially",
                "Stakes are clear",
                "Audience sees potential problems character misses"
            ],
            payoff_characteristics=[
                "Physical comedy or public embarrassment",
                "Original goal completely unachieved",
                "Lesson learned (usually)",
                "Other characters react to aftermath"
            ],
            modernization_challenges=[
                "Modern technology might solve problem too easily",
                "Physical labor jobs less common",
                "Audience may be less sympathetic to wealthy characters failing"
            ],
            recommended_updates=[
                "Use social media as amplifier of embarrassment",
                "Replace factory work with gig economy tasks",
                "Add 'goes viral' element for modern stakes",
                "Make failure more relatable (everyone has phone mishaps)"
            ],
            tags={"physical", "escalation", "hubris", "lucy_specialty"}
        )
        
        # Pattern 2: Misunderstanding Cascade
        self.patterns["misunderstanding_cascade"] = HumorPattern(
            pattern_id="misunderstanding_cascade",
            name="Misunderstanding Cascade",
            description=(
                "Small miscommunication snowballs into elaborate confusion "
                "as each character acts on incomplete information"
            ),
            comedy_type=ComedyType.SITUATIONAL,
            typical_era=ComedyEra.FAMILY_1980s,
            classic_examples=[
                {
                    "show": "Three's Company",
                    "episode": "Various",
                    "description": "Jack's comments overheard out of context"
                },
                {
                    "show": "Frasier",
                    "episode": "The Innkeepers",
                    "description": "Restaurant opening miscommunications escalate"
                }
            ],
            modern_equivalent=(
                "Text message taken out of context, autocorrect disaster, "
                "group chat confusion, social media misinterpretation"
            ),
            transformation_notes=(
                "Perfect for modern communication technology. Texts, DMs, "
                "voice notes, video calls all create new misunderstanding "
                "opportunities. Add 'typing...' anxiety, message deletion, "
                "wrong chat window."
            ),
            timing_requirements="Progressive escalation with reveals every 30-60 seconds",
            setup_requirements=[
                "Plausible initial miscommunication",
                "Each character has reason not to clarify",
                "Stakes increase with each misunderstanding"
            ],
            payoff_characteristics=[
                "Confrontation where all misunderstandings revealed",
                "Absurdity of situation becomes apparent",
                "Often resolved with simple clarification",
                "Characters reflect on communication failures"
            ],
            modernization_challenges=[
                "Modern communication should make clarification easier",
                "Audience may find it frustrating if easily solvable"
            ],
            recommended_updates=[
                "Use technology to create new barriers (texts without tone)",
                "Add time pressure (messages can't be unsent)",
                "Make clarification attempts fail humorously",
                "Include modern communication anxiety (read receipts)"
            ],
            tags={"verbal", "escalation", "communication", "farce"}
        )
        
        # Pattern 3: Fish Out of Water
        self.patterns["fish_out_of_water"] = HumorPattern(
            pattern_id="fish_out_of_water",
            name="Fish Out of Water",
            description=(
                "Character placed in unfamiliar situation or culture, "
                "struggles comedically with new norms and expectations"
            ),
            comedy_type=ComedyType.CHARACTER,
            typical_era=ComedyEra.RURAL_1960s,
            classic_examples=[
                {
                    "show": "The Beverly Hillbillies",
                    "episode": "Various",
                    "description": "Rural family adapts to Beverly Hills wealth"
                },
                {
                    "show": "Perfect Strangers",
                    "episode": "Various",
                    "description": "Balki adapts to American culture"
                }
            ],
            modern_equivalent=(
                "Boomer navigating Gen Z trends, rural influencer in NYC, "
                "tech worker in wilderness, American in foreign country"
            ),
            transformation_notes=(
                "Update from geographic/class fish-out-of-water to "
                "generational, technological, or subcultural. Modern "
                "version can be more nuanced and less stereotypical."
            ),
            timing_requirements="Multiple small moments building to major cultural clash",
            setup_requirements=[
                "Clear baseline showing character's normal environment",
                "New environment established as alien to character",
                "Character's attempts to adapt shown failing"
            ],
            payoff_characteristics=[
                "Character eventually finds their niche",
                "Audience learns to appreciate character's perspective",
                "New environment changes slightly to accommodate them"
            ],
            modernization_challenges=[
                "Risk of stereotyping or cultural insensitivity",
                "Audiences more sophisticated about cultural differences"
            ],
            recommended_updates=[
                "Focus on generational or technological gaps",
                "Make both cultures/contexts look absurd",
                "Give character valuable outside perspective",
                "Avoid mean-spirited mockery"
            ],
            tags={"character", "culture_clash", "adaptation", "satire"}
        )
        
        # Pattern 4: Jealousy/Competition Spiral
        self.patterns["jealousy_spiral"] = HumorPattern(
            pattern_id="jealousy_spiral",
            name="Jealousy/Competition Spiral",
            description=(
                "Minor competitive feeling escalates into elaborate "
                "one-upmanship and increasingly absurd attempts to win"
            ),
            comedy_type=ComedyType.CHARACTER,
            typical_era=ComedyEra.FAMILY_1980s,
            classic_examples=[
                {
                    "show": "I Love Lucy",
                    "episode": "Lucy and Ethel Buy the Same Dress",
                    "description": "Best friends compete over identical dress"
                },
                {
                    "show": "The Honeymooners",
                    "episode": "The Golfer",
                    "description": "Ralph tries to outdo coworker at golf"
                }
            ],
            modern_equivalent=(
                "Social media one-upmanship, follower count competition, "
                "vacation flex wars, LinkedIn humble-bragging contest"
            ),
            transformation_notes=(
                "Perfect for social media era. Replace physical displays "
                "with online performance. Add analytics, metrics, viral "
                "potential. Make competition more public and embarrassing."
            ),
            timing_requirements="Escalating reveals of competitive moves, surprise topper",
            setup_requirements=[
                "Initial competitive moment seems reasonable",
                "Both parties commit to winning",
                "Stakes become increasingly absurd"
            ],
            payoff_characteristics=[
                "One competitor clearly goes too far",
                "Competition exposed as meaningless",
                "Friendship/relationship reaffirmed",
                "Both learn to laugh at themselves"
            ],
            modernization_challenges=[
                "Social media makes competition more visible and permanent"
            ],
            recommended_updates=[
                "Use social media as primary competition arena",
                "Add screenshot evidence, comment sections",
                "Include algorithm manipulation attempts",
                "Make resolution involve going offline"
            ],
            tags={"character", "escalation", "relationships", "social_media"}
        )
        
        # Pattern 5: Well-Intentioned Deception
        self.patterns["well_intentioned_lie"] = HumorPattern(
            pattern_id="well_intentioned_lie",
            name="Well-Intentioned Deception",
            description=(
                "Character lies to spare feelings or avoid conflict, "
                "but must maintain increasingly elaborate fiction"
            ),
            comedy_type=ComedyType.SITUATIONAL,
            typical_era=ComedyEra.FAMILY_1980s,
            classic_examples=[
                {
                    "show": "I Love Lucy",
                    "episode": "The Benefit",
                    "description": "Lucy pretends friend is talented performer"
                },
                {
                    "show": "Frasier",
                    "episode": "The Matchmaker",
                    "description": "Frasier assumes wrong person is date"
                }
            ],
            modern_equivalent=(
                "Fake Instagram relationship, exaggerated LinkedIn experience, "
                "catfish situation, fake Yelp review that spirals"
            ),
            transformation_notes=(
                "Update white lies to digital lies. Add complication of "
                "digital evidence, screenshots, timestamps. Make exposure "
                "more public and permanent."
            ),
            timing_requirements="Progressive complications, near-exposures, ultimate reveal",
            setup_requirements=[
                "Character's good intentions are clear",
                "Initial lie seems harmless",
                "Circumstances force elaboration"
            ],
            payoff_characteristics=[
                "Truth revealed in embarrassing way",
                "Character apologizes and learns lesson",
                "Damaged relationship repaired",
                "Humor in how elaborate the lie became"
            ],
            modernization_challenges=[
                "Digital evidence makes lies harder to maintain",
                "Audience may be less forgiving of dishonesty"
            ],
            recommended_updates=[
                "Add digital paper trail complication",
                "Use social media to expose lie publicly",
                "Make lie more relatable (everyone curates online)",
                "Focus on anxiety of maintaining digital persona"
            ],
            tags={"deception", "escalation", "good_intentions", "farce"}
        )
        
        # Pattern 6: Authority Figure Misunderstanding
        self.patterns["authority_misunderstanding"] = HumorPattern(
            pattern_id="authority_misunderstanding",
            name="Authority Figure Misunderstanding",
            description=(
                "Character's innocent actions misinterpreted by authority "
                "figure as rule-breaking or suspicious behavior"
            ),
            comedy_type=ComedyType.SITUATIONAL,
            typical_era=ComedyEra.RURAL_1960s,
            classic_examples=[
                {
                    "show": "The Andy Griffith Show",
                    "episode": "Various",
                    "description": "Barney misreads innocent situations"
                },
                {
                    "show": "I Love Lucy",
                    "episode": "Various",
                    "description": "Ricky thinks Lucy is up to something"
                }
            ],
            modern_equivalent=(
                "HR misinterprets Slack message, TSA flags innocent item, "
                "algorithm flags normal behavior, Ring doorbell captures "
                "out-of-context moment"
            ),
            transformation_notes=(
                "Update authority from person to system. Modern authorities "
                "include algorithms, automated systems, surveillance. "
                "Add layer of trying to explain to unhelpful AI."
            ),
            timing_requirements="Building suspicion, failed explanations, comedic revelation",
            setup_requirements=[
                "Character's innocent intent is clear to audience",
                "Authority figure's suspicion is somewhat reasonable",
                "Attempts to explain make things worse"
            ],
            payoff_characteristics=[
                "Truth revealed through unexpected means",
                "Authority figure embarrassed",
                "Character vindicated but exhausted",
                "System shown to be flawed"
            ],
            modernization_challenges=[
                "Surveillance state implications less funny",
                "Authorities more sophisticated today"
            ],
            recommended_updates=[
                "Make authority a system not a person (algorithm)",
                "Add bureaucratic absurdity to resolution attempts",
                "Include digital evidence that misleads",
                "Keep human authority figure but add tech layer"
            ],
            tags={"authority", "misunderstanding", "innocent", "system"}
        )
        
        # Add more patterns (7-20) for comprehensive coverage
        self._add_additional_patterns()
    
    def _add_additional_patterns(self):
        """Add additional comedy patterns for comprehensive coverage."""
        
        # Pattern 7: Surprise Visitor Crisis
        self.patterns["surprise_visitor"] = HumorPattern(
            pattern_id="surprise_visitor",
            name="Surprise Visitor Creates Crisis",
            description="Unexpected guest arrives when character least prepared",
            comedy_type=ComedyType.SITUATIONAL,
            typical_era=ComedyEra.FAMILY_1980s,
            classic_examples=[
                {"show": "I Love Lucy", "episode": "Lucy Meets the Moustache", "description": "VIP shows up unexpectedly"}
            ],
            modern_equivalent="Video call catches unprepared, Ring doorbell shows visitor arriving",
            transformation_notes="Add smart home, delivery tracking, social media spoilers",
            timing_requirements="Frantic preparation, near-misses, reveal",
            setup_requirements=["Clear stakes for visit", "Character unprepared shown"],
            payoff_characteristics=["Scramble mostly successful", "Truth partially revealed"],
            modernization_challenges=["Harder to be truly surprised today"],
            recommended_updates=["Use smart home alerts", "Add delivery tracking complications"],
            tags={"situational", "panic", "guests"}
        )
        
        # Pattern 8: Hobby/Skill Overconfidence
        self.patterns["overconfident_hobby"] = HumorPattern(
            pattern_id="overconfident_hobby",
            name="Overconfident Amateur",
            description="Character believes they're skilled, reality proves otherwise",
            comedy_type=ComedyType.CHARACTER,
            typical_era=ComedyEra.GOLDEN_AGE_1950s,
            classic_examples=[
                {"show": "I Love Lucy", "episode": "Lucy Learns to Drive", "description": "Lucy overconfident behind wheel"}
            ],
            modern_equivalent="YouTube tutorial overconfidence, DIY disaster, crypto day-trading",
            transformation_notes="Replace physical skills with digital ones, add YouTube/TikTok learning",
            timing_requirements="Confidence display, first failure, escalating disasters",
            setup_requirements=["Character's belief in ability established", "Stakes for failure"],
            payoff_characteristics=["Spectacular failure", "Expert shows proper way", "Humility learned"],
            modernization_challenges=["Modern tutorials are actually helpful"],
            recommended_updates=["Add influencer fake confidence", "Include editing tricks exposure"],
            tags={"character", "hubris", "physical", "skills"}
        )
        
        # Patterns 9-20: Add abbreviated entries for remaining common patterns
        additional_patterns = {
            "role_reversal": "Traditional roles swap with comedic results",
            "double_booking": "Accidentally committed to two simultaneous events",
            "eavesdropping_misinterpretation": "Overheard conversation misunderstood",
            "gift_disaster": "Well-meaning gift goes terribly wrong",
            "white_elephant": "Unwanted item impossible to get rid of",
            "secret_revealed": "Carefully guarded secret accidentally exposed",
            "impersonation_necessary": "Must pretend to be someone else",
            "chain_of_favors": "Small favor spirals into major obligation",
            "equipment_malfunction": "Technology fails at worst possible moment",
            "outdated_advice": "Following obsolete guidance causes problems",
            "trophy_wife_syndrome": "Partner embarrasses in social situation",
            "urban_legend_believed": "Character believes and acts on false information"
        }
        
        for pattern_id, description in additional_patterns.items():
            self.patterns[pattern_id] = HumorPattern(
                pattern_id=pattern_id,
                name=pattern_id.replace("_", " ").title(),
                description=description,
                comedy_type=ComedyType.SITUATIONAL,
                typical_era=ComedyEra.FAMILY_1980s,
                classic_examples=[],
                modern_equivalent="To be specified",
                transformation_notes="To be specified",
                timing_requirements="Standard sitcom pacing",
                setup_requirements=[],
                payoff_characteristics=[],
                modernization_challenges=[],
                recommended_updates=[],
                tags=set()
            )
    
    def get_pattern(self, pattern_id: str) -> Optional[HumorPattern]:
        """
        Get a specific pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            HumorPattern if found, None otherwise
        """
        return self.patterns.get(pattern_id)
    
    def get_patterns_by_era(self, era: ComedyEra) -> List[HumorPattern]:
        """Get all patterns typical of a specific era."""
        return [
            pattern for pattern in self.patterns.values()
            if pattern.typical_era == era
        ]
    
    def get_patterns_by_type(self, comedy_type: ComedyType) -> List[HumorPattern]:
        """Get all patterns of a specific comedy type."""
        return [
            pattern for pattern in self.patterns.values()
            if pattern.comedy_type == comedy_type
        ]
    
    def suggest_modernizations(
        self,
        show_title: str,
        identified_patterns: List[str]
    ) -> Dict[str, List[str]]:
        """
        Suggest modern equivalents for identified patterns.
        
        Args:
            show_title: Original show name
            identified_patterns: List of pattern IDs found in show
            
        Returns:
            Dict mapping pattern_id to list of modernization suggestions
        """
        suggestions = {}
        
        for pattern_id in identified_patterns:
            pattern = self.get_pattern(pattern_id)
            if pattern:
                suggestions[pattern_id] = [
                    f"Modern equivalent: {pattern.modern_equivalent}",
                    f"Transformation: {pattern.transformation_notes}",
                    *[f"Update: {update}" for update in pattern.recommended_updates[:3]]
                ]
        
        return suggestions
    
    def analyze_show_humor_style(
        self,
        show_data: Dict
    ) -> Dict[str, any]:
        """
        Analyze a show's likely humor patterns based on era and genre.
        
        Args:
            show_data: Show information (years, genre, etc.)
            
        Returns:
            Analysis with predicted patterns and suggestions
        """
        # Extract show era
        years = show_data.get("years", "")
        if "195" in years:
            era = ComedyEra.GOLDEN_AGE_1950s
        elif "196" in years:
            era = ComedyEra.RURAL_1960s
        elif "197" in years:
            era = ComedyEra.RELEVANT_1970s
        elif "198" in years:
            era = ComedyEra.FAMILY_1980s
        elif "199" in years:
            era = ComedyEra.IRONIC_1990s
        elif "200" in years:
            era = ComedyEra.CRINGE_2000s
        else:
            era = ComedyEra.STREAMING_2010s
        
        # Get patterns for this era
        likely_patterns = self.get_patterns_by_era(era)
        
        # Extract genre
        genres = show_data.get("genre", [])
        if isinstance(genres, str):
            genres = [genres]
        
        return {
            "era": era.value,
            "likely_patterns": [
                {
                    "id": p.pattern_id,
                    "name": p.name,
                    "type": p.comedy_type.value
                }
                for p in likely_patterns[:10]
            ],
            "modernization_strategy": self._get_era_modernization_strategy(era),
            "suggested_pattern_updates": len(likely_patterns)
        }
    
    def _get_era_modernization_strategy(self, era: ComedyEra) -> List[str]:
        """Get general modernization strategy for an era."""
        strategies = {
            ComedyEra.GOLDEN_AGE_1950s: [
                "Replace physical labor with gig economy",
                "Add social media amplification to embarrassment",
                "Update gender roles to modern equality",
                "Replace TV with streaming/YouTube"
            ],
            ComedyEra.RURAL_1960s: [
                "Replace rural/urban divide with digital/analog divide",
                "Update class dynamics to wealth inequality",
                "Modernize fish-out-of-water to generational gaps",
                "Replace geographic displacement with cultural shift"
            ],
            ComedyEra.FAMILY_1980s: [
                "Update family dynamics to modern structures",
                "Replace phone misunderstandings with text mishaps",
                "Add smart home and surveillance complications",
                "Update workplace to remote work scenarios"
            ]
        }
        return strategies.get(era, ["Standard modernization approach"])
    
    def export_pattern_guide(self, pattern_ids: Optional[List[str]] = None) -> str:
        """
        Export pattern guide for writers.
        
        Args:
            pattern_ids: Specific patterns to export, or None for all
            
        Returns:
            Formatted guide text
        """
        if pattern_ids:
            patterns = [self.get_pattern(pid) for pid in pattern_ids if self.get_pattern(pid)]
        else:
            patterns = list(self.patterns.values())
        
        guide = "# COMEDY PATTERN MODERNIZATION GUIDE\n\n"
        guide += f"Total Patterns: {len(patterns)}\n\n"
        
        for pattern in patterns:
            guide += f"## {pattern.name}\n"
            guide += f"**ID:** {pattern.pattern_id}\n"
            guide += f"**Type:** {pattern.comedy_type.value}\n"
            guide += f"**Description:** {pattern.description}\n\n"
            guide += f"**Modern Equivalent:**\n{pattern.modern_equivalent}\n\n"
            guide += f"**Transformation Notes:**\n{pattern.transformation_notes}\n\n"
            if pattern.recommended_updates:
                guide += "**Recommended Updates:**\n"
                for update in pattern.recommended_updates:
                    guide += f"- {update}\n"
            guide += "\n---\n\n"
        
        return guide


# Global singleton instance
_humor_library_instance = None


def get_humor_pattern_library() -> HumorPatternLibrary:
    """Get global humor pattern library instance."""
    global _humor_library_instance
    if _humor_library_instance is None:
        _humor_library_instance = HumorPatternLibrary()
    return _humor_library_instance


# Example usage
if __name__ == "__main__":
    library = HumorPatternLibrary()
    
    # Get specific pattern
    pattern = library.get_pattern("scheme_backfires")
    print(f"Pattern: {pattern.name}")
    print(f"Modern: {pattern.modern_equivalent}\n")
    
    # Analyze show
    show_data = {"title": "I Love Lucy", "years": "1951-1957", "genre": ["Sitcom"]}
    analysis = library.analyze_show_humor_style(show_data)
    print(f"Era: {analysis['era']}")
    print(f"Likely patterns: {len(analysis['likely_patterns'])}")
    
    # Get suggestions
    suggestions = library.suggest_modernizations(
        "I Love Lucy",
        ["scheme_backfires", "misunderstanding_cascade"]
    )
    for pattern_id, recs in suggestions.items():
        print(f"\n{pattern_id}:")
        for rec in recs:
            print(f"  - {rec}")
