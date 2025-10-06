"""
Tests for DialogueGenerator component.

Tests voice profile creation, dialogue generation, and consistency validation.
"""

import pytest
from unittest.mock import AsyncMock, Mock
import json
from datetime import datetime

from src.services.creative.dialogue_generator import DialogueGenerator
from src.services.creative.character_voice_profiles import (
    CharacterVoiceProfile,
    DialogueLine,
    SceneDialogue
)


class TestDialogueGenerator:
    """Test suite for DialogueGenerator."""
    
    @pytest.fixture
    def mock_claude_client(self):
        """Mock Claude AI client."""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_gpt_client(self):
        """Mock GPT AI client."""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def dialogue_generator(self, mock_claude_client, mock_gpt_client):
        """DialogueGenerator instance with mocked AI clients."""
        return DialogueGenerator(
            claude_client=mock_claude_client,
            gpt_client=mock_gpt_client
        )


@pytest.fixture
def sample_character_analysis():
    """Sample character analysis from Phase 3."""
    return {
        'character_name': 'Luna',
        'core_traits': ['ambitious', 'scheming', 'endearing'],
        'speech_patterns': [
            'Whines when pleading',
            'Speaks quickly when excited',
            'Uses simple vocabulary'
        ],
        'catchphrases': ['Ricky!', 'But why not?', 'Oh!'],
        'relationships': [
            {
                'character': 'Ricky',
                'relationship_type': 'spouse',
                'description': 'Loving but often frustrated husband',
                'dynamic': 'Respectful but pushy'
            }
        ]
    }


@pytest.fixture
def sample_transformation_rules():
    """Sample transformation rules from Phase 3."""
    return {
        'original_setting': '1950s New York apartment',
        'modern_equivalent': '2025 Los Angeles smart home',
        'character_transformations': [
            {
                'original_character': 'Lucy Ricardo',
                'modern_name': 'Luna',
                'motivation_update': 'Wants YouTube fame instead of showbiz'
            }
        ],
        'technology_integration': ['smartphones', 'social media', 'ring lights']
    }


@pytest.fixture
def sample_scene():
    """Sample scene from episode outline."""
    return {
        'scene_number': 1,
        'location': 'Living Room',
        'time_of_day': 'Morning',
        'characters': ['Luna', 'Ricky'],
        'description': 'Luna pitches YouTube collab idea to Ricky',
        'plot_relevance': 'A-plot',
        'comedic_beats': [
            "Luna mispronounces 'algorithm'",
            "Ricky's patronizing response"
        ],
        'estimated_runtime': 90
    }


@pytest.fixture
def sample_episode_context():
    """Sample episode outline context."""
    return {
        'episode_number': 1,
        'episode_title': 'The Algorithm',
        'logline': 'Luna wants to collaborate on Ricky\'s YouTube channel',
        'a_plot_summary': 'Luna schemes to get on Ricky\'s channel',
        'b_plot_summary': 'Ethel tries new cooking app',
        'scenes': []
    }


@pytest.fixture
def sample_narrative_structure():
    """Sample narrative analysis."""
    return {
        'recurring_devices': ['scheme backfires', 'physical comedy'],
        'humor_style': 'slapstick with wordplay',
        'opening_convention': 'domestic scene with conflict',
        'closing_convention': 'lesson learned, status quo restored'
    }


@pytest.fixture
def mock_voice_profile_response():
    """Mock AI response for voice profile creation."""
    return json.dumps({
        'vocabulary_level': 'simple',
        'sentence_structure': 'rambling',
        'verbal_tics': ['Oh!', 'like', 'you know'],
        'catchphrases': ['Ricky!', 'But why not?'],
        'emotional_range': ['excitable', 'scheming', 'endearing'],
        'speech_patterns': [
            'Whining when pleading',
            'Fast-paced when excited',
            'Uses lots of hand gestures'
        ],
        'relationship_dynamics': {
            'Ricky': 'respectful but pushy',
            'Ethel': 'conspiratorial and friendly'
        },
        'education_level': 'high school',
        'cultural_background': '2025 LA social media culture',
        'age_appropriate_language': 'late 20s millennial/gen-z hybrid',
        'humor_style': 'physical comedy with earnest delivery'
    })


@pytest.fixture
def mock_dialogue_response():
    """Mock AI response for dialogue generation."""
    return json.dumps({
        'dialogue': [
            {
                'character': 'LUNA',
                'line': 'Ricky! Ricky, look at this!',
                'emotion': 'excited',
                'delivery_note': 'rushing in, waving phone',
                'pause_before': 0.0,
                'is_comedic_beat': False,
                'comedic_beat_type': None
            },
            {
                'character': 'RICKY',
                'line': 'What is it now, Luna?',
                'emotion': 'patient but wary',
                'delivery_note': 'not looking up from coffee',
                'pause_before': 0.5,
                'is_comedic_beat': False,
                'comedic_beat_type': None
            },
            {
                'character': 'LUNA',
                'line': 'Your video got twelve million views! We should do a collab and boost the algor-rhythm!',
                'emotion': 'excitable',
                'delivery_note': 'mispronouncing deliberately',
                'pause_before': 0.0,
                'is_comedic_beat': True,
                'comedic_beat_type': 'setup'
            },
            {
                'character': 'RICKY',
                'line': 'Algorithm. Al-go-rith-m. And no.',
                'emotion': 'patronizing',
                'delivery_note': 'correcting pronunciation',
                'pause_before': 1.0,
                'is_comedic_beat': True,
                'comedic_beat_type': 'punchline'
            }
        ]
    })


class TestDialogueGenerator:
    """Test suite for DialogueGenerator."""

    def test_initialization(self, mock_claude_client):
        """Test DialogueGenerator initializes correctly."""
        generator = DialogueGenerator(
            claude_client=mock_claude_client,
            gpt_client=None,
            database_manager=None
        )

        assert generator.claude == mock_claude_client
        assert generator.gpt is None
        assert generator.db is None
        assert generator.voice_profiles == {}

    @pytest.mark.asyncio
    async def test_create_voice_profile_success(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_character_analysis,
        sample_transformation_rules,
        mock_voice_profile_response
    ):
        """Test successful voice profile creation."""
        # Setup mock
        mock_claude_client.generate = AsyncMock(
            return_value=mock_voice_profile_response
        )

        # Create voice profile
        profile = await dialogue_generator.create_voice_profile(
            character_analysis=sample_character_analysis,
            transformation_rules=sample_transformation_rules,
            character_name='Luna'
        )

        # Verify profile created correctly
        assert isinstance(profile, CharacterVoiceProfile)
        assert profile.character_name == 'Luna'
        assert profile.vocabulary_level == 'simple'
        assert profile.sentence_structure == 'rambling'
        assert 'Oh!' in profile.verbal_tics
        assert 'Ricky!' in profile.catchphrases
        assert 'excitable' in profile.emotional_range
        assert 'Ricky' in profile.relationship_dynamics

        # Verify profile cached
        assert 'Luna' in dialogue_generator.voice_profiles

        # Verify AI called
        mock_claude_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_voice_profile_fallback_on_error(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_character_analysis,
        sample_transformation_rules
    ):
        """Test voice profile creation falls back on AI error."""
        # Setup mock to raise error
        mock_claude_client.generate = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Create voice profile
        profile = await dialogue_generator.create_voice_profile(
            character_analysis=sample_character_analysis,
            transformation_rules=sample_transformation_rules,
            character_name='Luna'
        )

        # Verify fallback profile created
        assert isinstance(profile, CharacterVoiceProfile)
        assert profile.character_name == 'Luna'
        assert profile.vocabulary_level == 'simple'
        assert profile.sentence_structure == 'medium'
        assert profile.emotional_range == ['neutral']

    @pytest.mark.asyncio
    async def test_create_voice_profile_uses_character_name_from_analysis(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_character_analysis,
        sample_transformation_rules,
        mock_voice_profile_response
    ):
        """Test voice profile uses character name from analysis if not provided."""
        mock_claude_client.generate = AsyncMock(
            return_value=mock_voice_profile_response
        )

        # Create without explicit name
        profile = await dialogue_generator.create_voice_profile(
            character_analysis=sample_character_analysis,
            transformation_rules=sample_transformation_rules
        )

        # Should use name from analysis
        assert profile.character_name == 'Luna'

    @pytest.mark.asyncio
    async def test_generate_dialogue_success(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_scene,
        sample_episode_context,
        sample_narrative_structure,
        mock_dialogue_response
    ):
        """Test successful dialogue generation."""
        # Setup mock
        mock_claude_client.generate = AsyncMock(
            return_value=mock_dialogue_response
        )

        # Generate dialogue
        scene_dialogue = await dialogue_generator.generate_dialogue(
            scene=sample_scene,
            episode_context=sample_episode_context,
            narrative_structure=sample_narrative_structure
        )

        # Verify scene dialogue created
        assert isinstance(scene_dialogue, SceneDialogue)
        assert scene_dialogue.scene_number == 1
        assert scene_dialogue.location == 'Living Room'
        assert 'Luna' in scene_dialogue.characters_present
        assert 'Ricky' in scene_dialogue.characters_present

        # Verify dialogue lines
        assert len(scene_dialogue.dialogue_lines) == 4
        assert all(
            isinstance(line, DialogueLine)
            for line in scene_dialogue.dialogue_lines
        )

        # Verify first line
        first_line = scene_dialogue.dialogue_lines[0]
        assert first_line.character == 'LUNA'
        assert 'Ricky' in first_line.line
        assert first_line.emotion == 'excited'

        # Verify comedic beats counted
        assert scene_dialogue.comedic_beats_count == 2

        # Verify runtime estimated
        assert scene_dialogue.total_runtime_estimate > 0

    @pytest.mark.asyncio
    async def test_generate_dialogue_with_voice_profiles(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_scene,
        sample_episode_context,
        sample_narrative_structure,
        mock_dialogue_response
    ):
        """Test dialogue generation uses voice profiles if available."""
        # Add voice profile
        luna_profile = CharacterVoiceProfile(
            character_name='Luna',
            vocabulary_level='simple',
            sentence_structure='rambling',
            verbal_tics=['Oh!'],
            catchphrases=['Ricky!'],
            emotional_range=['excitable'],
            speech_patterns=['Fast when excited'],
            relationship_dynamics={'Ricky': 'pushy but respectful'}
        )
        dialogue_generator.voice_profiles['Luna'] = luna_profile

        mock_claude_client.generate = AsyncMock(
            return_value=mock_dialogue_response
        )

        # Generate dialogue
        scene_dialogue = await dialogue_generator.generate_dialogue(
            scene=sample_scene,
            episode_context=sample_episode_context,
            narrative_structure=sample_narrative_structure
        )

        # Verify higher confidence score with voice profiles
        assert scene_dialogue.confidence_score > 0.5

    @pytest.mark.asyncio
    async def test_generate_dialogue_fallback_on_error(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_scene,
        sample_episode_context,
        sample_narrative_structure
    ):
        """Test dialogue generation returns empty on error."""
        # Setup mock to fail
        mock_claude_client.generate = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Generate dialogue
        scene_dialogue = await dialogue_generator.generate_dialogue(
            scene=sample_scene,
            episode_context=sample_episode_context,
            narrative_structure=sample_narrative_structure
        )

        # Verify empty dialogue returned
        assert isinstance(scene_dialogue, SceneDialogue)
        assert len(scene_dialogue.dialogue_lines) == 0
        assert scene_dialogue.comedic_beats_count == 0
        assert scene_dialogue.confidence_score == 0.0

    @pytest.mark.asyncio
    async def test_generate_dialogue_calculates_runtime(
        self,
        dialogue_generator,
        mock_claude_client,
        sample_scene,
        sample_episode_context,
        sample_narrative_structure,
        mock_dialogue_response
    ):
        """Test runtime estimation based on word count."""
        mock_claude_client.generate = AsyncMock(
            return_value=mock_dialogue_response
        )

        scene_dialogue = await dialogue_generator.generate_dialogue(
            scene=sample_scene,
            episode_context=sample_episode_context,
            narrative_structure=sample_narrative_structure
        )

        # Should estimate based on ~150 words/minute
        # 4 lines with ~40 words total = ~16 seconds
        assert scene_dialogue.total_runtime_estimate > 0
        assert scene_dialogue.total_runtime_estimate < 60

    def test_validate_dialogue_consistency_with_profiles(
        self,
        dialogue_generator
    ):
        """Test consistency validation with voice profiles."""
        # Add voice profiles
        dialogue_generator.voice_profiles['Luna'] = CharacterVoiceProfile(
            character_name='Luna',
            vocabulary_level='simple',
            sentence_structure='rambling',
            verbal_tics=[],
            catchphrases=[],
            emotional_range=[],
            speech_patterns=[],
            relationship_dynamics={}
        )

        # Create sample lines
        lines = [
            DialogueLine(
                character='Luna',
                line='Test line',
                emotion='happy'
            )
        ]

        # Validate
        score = dialogue_generator._validate_dialogue_consistency(
            dialogue_lines=lines,
            characters=['Luna']
        )

        # Should return high score with profile
        assert score >= 0.8

    def test_validate_dialogue_consistency_without_profiles(
        self,
        dialogue_generator
    ):
        """Test consistency validation without voice profiles."""
        lines = [
            DialogueLine(
                character='Unknown',
                line='Test line',
                emotion='neutral'
            )
        ]

        score = dialogue_generator._validate_dialogue_consistency(
            dialogue_lines=lines,
            characters=['Unknown']
        )

        # Should return lower score without profiles
        assert score == 0.5

    def test_validate_dialogue_consistency_empty_lines(
        self,
        dialogue_generator
    ):
        """Test consistency validation with empty dialogue."""
        score = dialogue_generator._validate_dialogue_consistency(
            dialogue_lines=[],
            characters=[]
        )

        # Should return 0 for empty
        assert score == 0.0


class TestCharacterVoiceProfile:
    """Test suite for CharacterVoiceProfile dataclass."""

    def test_voice_profile_creation(self):
        """Test creating voice profile."""
        profile = CharacterVoiceProfile(
            character_name='Test',
            vocabulary_level='sophisticated',
            sentence_structure='eloquent',
            verbal_tics=['indeed', 'quite'],
            catchphrases=['Elementary!'],
            emotional_range=['analytical', 'aloof'],
            speech_patterns=['Formal British English'],
            relationship_dynamics={'Watson': 'condescending mentor'}
        )

        assert profile.character_name == 'Test'
        assert profile.vocabulary_level == 'sophisticated'

    def test_get_speaking_style_summary(self):
        """Test speaking style summary generation."""
        profile = CharacterVoiceProfile(
            character_name='Luna',
            vocabulary_level='simple',
            sentence_structure='rambling',
            verbal_tics=['Oh!', 'like'],
            catchphrases=['Ricky!'],
            emotional_range=['excitable'],
            speech_patterns=[],
            relationship_dynamics={}
        )

        summary = profile.get_speaking_style_summary()

        assert 'Luna' in summary
        assert 'simple' in summary
        assert 'rambling' in summary
        assert 'Oh!' in summary
        assert 'Ricky!' in summary

    def test_get_relationship_guidance(self):
        """Test retrieving relationship-specific guidance."""
        profile = CharacterVoiceProfile(
            character_name='Luna',
            vocabulary_level='simple',
            sentence_structure='rambling',
            verbal_tics=[],
            catchphrases=[],
            emotional_range=[],
            speech_patterns=[],
            relationship_dynamics={
                'Ricky': 'respectful but pushy',
                'Ethel': 'conspiratorial'
            }
        )

        assert profile.get_relationship_guidance('Ricky') == 'respectful but pushy'
        assert profile.get_relationship_guidance('Ethel') == 'conspiratorial'
        assert profile.get_relationship_guidance('Fred') is None

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        original = CharacterVoiceProfile(
            character_name='Luna',
            vocabulary_level='simple',
            sentence_structure='rambling',
            verbal_tics=['Oh!'],
            catchphrases=['Ricky!'],
            emotional_range=['excitable'],
            speech_patterns=['Fast'],
            relationship_dynamics={'Ricky': 'pushy'},
            humor_style='physical'
        )

        # Convert to dict
        data = original.to_dict()

        # Convert back
        restored = CharacterVoiceProfile.from_dict(data)

        # Verify match
        assert restored.character_name == original.character_name
        assert restored.vocabulary_level == original.vocabulary_level
        assert restored.verbal_tics == original.verbal_tics
        assert restored.humor_style == original.humor_style


class TestDialogueLine:
    """Test suite for DialogueLine dataclass."""

    def test_dialogue_line_creation(self):
        """Test creating dialogue line."""
        line = DialogueLine(
            character='LUNA',
            line='Ricky!',
            emotion='excited',
            delivery_note='rushing in',
            pause_before=0.5,
            is_comedic_beat=True,
            comedic_beat_type='callback'
        )

        assert line.character == 'LUNA'
        assert line.line == 'Ricky!'
        assert line.is_comedic_beat is True

    def test_format_for_screenplay(self):
        """Test screenplay formatting."""
        line = DialogueLine(
            character='LUNA',
            line='I have an idea!',
            emotion='excited',
            delivery_note='eyes gleaming',
            is_comedic_beat=False
        )

        formatted = line.format_for_screenplay()

        assert 'LUNA' in formatted
        assert 'eyes gleaming' in formatted
        assert 'I have an idea!' in formatted

    def test_format_for_screenplay_without_delivery_note(self):
        """Test screenplay formatting without delivery note."""
        line = DialogueLine(
            character='RICKY',
            line='No.',
            emotion='firm'
        )

        formatted = line.format_for_screenplay()

        assert 'RICKY' in formatted
        assert 'No.' in formatted
        assert '(' not in formatted  # No parenthetical


class TestSceneDialogue:
    """Test suite for SceneDialogue dataclass."""

    def test_scene_dialogue_creation(self):
        """Test creating scene dialogue."""
        lines = [
            DialogueLine(
                character='LUNA',
                line='Test 1',
                emotion='happy'
            ),
            DialogueLine(
                character='RICKY',
                line='Test 2',
                emotion='calm'
            )
        ]

        scene = SceneDialogue(
            scene_number=1,
            location='Living Room',
            characters_present=['Luna', 'Ricky'],
            dialogue_lines=lines,
            total_runtime_estimate=30,
            comedic_beats_count=1,
            confidence_score=0.85
        )

        assert scene.scene_number == 1
        assert len(scene.dialogue_lines) == 2

    def test_get_dialogue_text(self):
        """Test extracting plain dialogue text."""
        lines = [
            DialogueLine(character='A', line='First line', emotion='happy'),
            DialogueLine(character='B', line='Second line', emotion='calm')
        ]

        scene = SceneDialogue(
            scene_number=1,
            location='Room',
            characters_present=['A', 'B'],
            dialogue_lines=lines,
            total_runtime_estimate=10,
            comedic_beats_count=0
        )

        text = scene.get_dialogue_text()

        assert 'First line' in text
        assert 'Second line' in text

    def test_get_screenplay_format(self):
        """Test full screenplay formatting."""
        lines = [
            DialogueLine(
                character='LUNA',
                line='Hello!',
                emotion='excited',
                pause_before=1.0
            ),
            DialogueLine(
                character='RICKY',
                line='Hi.',
                emotion='calm'
            )
        ]

        scene = SceneDialogue(
            scene_number=5,
            location='Kitchen',
            characters_present=['Luna', 'Ricky'],
            dialogue_lines=lines,
            total_runtime_estimate=10,
            comedic_beats_count=0
        )

        formatted = scene.get_screenplay_format()

        assert 'SCENE 5 - KITCHEN' in formatted
        assert 'LUNA' in formatted
        assert 'RICKY' in formatted
        assert 'PAUSE - 1.0 seconds' in formatted
