"""
Tests for StageDirectionGenerator component.

Tests visual scene descriptions, physical comedy choreography,
and camera suggestions.
"""

import pytest
from unittest.mock import AsyncMock, Mock
import json
from datetime import datetime

from src.services.creative.stage_direction_generator import StageDirectionGenerator
from src.services.creative.stage_direction_models import (
    StageDirection,
    PhysicalComedySequence,
    CameraSuggestion,
    SceneStageDirections
)
from src.services.creative.character_voice_profiles import (
    DialogueLine,
    SceneDialogue
)


class TestStageDirectionGenerator:
    """Test suite for StageDirectionGenerator."""
    
    @pytest.fixture
    def stage_direction_generator(self, mock_claude_client, mock_gpt_client):
        """StageDirectionGenerator instance with mocked AI clients."""
        return StageDirectionGenerator(
            claude_client=mock_claude_client,
            gpt_client=mock_gpt_client
        )
    
    @pytest.fixture
    def sample_scene(self):
        """Sample scene outline."""
        return {
            'scene_number': 1,
            'location': 'Living Room',
            'time_of_day': 'Morning',
            'characters': ['Luna', 'Ricky'],
            'description': 'Luna tries to adjust ring light setup',
            'plot_relevance': 'A-plot',
            'comedic_beats': ['Ring light falls', 'Luna trips over cables'],
            'estimated_runtime': 90
        }
    
    @pytest.fixture
    def sample_scene_dialogue(self):
        """Sample scene dialogue."""
        lines = [
            DialogueLine(
                character='LUNA',
                line='I think I almost have it!',
                emotion='excited',
                delivery_note='adjusting ring light precariously',
                pause_before=0.0,
                is_comedic_beat=False
            ),
            DialogueLine(
                character='RICKY',
                line='Luna, be careful with that...',
                emotion='worried',
                delivery_note='watching nervously',
                pause_before=0.5,
                is_comedic_beat=False
            ),
            DialogueLine(
                character='LUNA',
                line='I got it! See?',
                emotion='triumphant',
                delivery_note='just as light starts to wobble',
                pause_before=0.0,
                is_comedic_beat=True,
                comedic_beat_type='setup'
            )
        ]
        
        return SceneDialogue(
            scene_number=1,
            location='Living Room',
            characters_present=['Luna', 'Ricky'],
            dialogue_lines=lines,
            total_runtime_estimate=30,
            comedic_beats_count=1
        )
    
    @pytest.fixture
    def mock_stage_directions_response(self):
        """Mock AI response for stage directions."""
        return json.dumps({
            'opening_description': 'Living room cluttered with photography equipment. Ring lights, tripods, and tangled cables everywhere. LUNA stands on a stepladder adjusting a large ring light.',
            'action_beats': [
                {
                    'timing': 'BEFORE LINE',
                    'description': 'Luna reaches up to tighten ring light mount',
                    'duration_estimate': 2.0,
                    'involves_characters': ['Luna'],
                    'visual_gag': False,
                    'camera_suggestion': {
                        'shot_type': 'MEDIUM',
                        'focus': 'Luna on ladder',
                        'reasoning': 'Establish precarious situation',
                        'movement': None,
                        'timing': 'Opening'
                    }
                },
                {
                    'timing': 'DURING LINE',
                    'description': 'Ring light wobbles slightly',
                    'duration_estimate': 1.0,
                    'involves_characters': ['Luna'],
                    'visual_gag': True,
                    'camera_suggestion': {
                        'shot_type': 'CLOSE-UP',
                        'focus': 'Wobbling mount',
                        'reasoning': 'Build tension',
                        'movement': None,
                        'timing': 'During dialogue'
                    }
                }
            ],
            'physical_comedy_sequences': [
                {
                    'beat_name': 'Ring Light Disaster',
                    'setup_actions': [
                        {
                            'timing': 'CONTINUOUS',
                            'description': 'Luna adjusts light, making it wobble more',
                            'duration_estimate': 2.0,
                            'involves_characters': ['Luna']
                        }
                    ],
                    'escalation_actions': [
                        {
                            'timing': 'CONTINUOUS',
                            'description': 'Luna tries to steady light, ladder wobbles',
                            'duration_estimate': 2.0,
                            'involves_characters': ['Luna']
                        },
                        {
                            'timing': 'CONTINUOUS',
                            'description': 'Ricky rushes to help, trips over cable',
                            'duration_estimate': 2.0,
                            'involves_characters': ['Ricky']
                        }
                    ],
                    'climax_action': {
                        'timing': 'CONTINUOUS',
                        'description': 'Ring light crashes down, Luna ducks, Ricky catches it',
                        'duration_estimate': 3.0,
                        'involves_characters': ['Luna', 'Ricky']
                    },
                    'resolution_action': {
                        'timing': 'AFTER',
                        'description': 'Both frozen, looking at each other, light between them',
                        'duration_estimate': 2.0,
                        'involves_characters': ['Luna', 'Ricky']
                    },
                    'total_duration': 11.0
                }
            ],
            'camera_suggestions': [
                {
                    'shot_type': 'WIDE',
                    'focus': 'Full room chaos',
                    'reasoning': 'Show complete physical comedy',
                    'movement': 'PAN',
                    'timing': 'During climax'
                },
                {
                    'shot_type': 'TWO-SHOT',
                    'focus': 'Luna and Ricky faces',
                    'reasoning': 'Capture reactions',
                    'movement': None,
                    'timing': 'Resolution'
                }
            ],
            'closing_description': 'Luna sheepishly climbs down. Equipment still scattered. Ricky carefully sets ring light down.'
        })
    
    def test_initialization(self, mock_claude_client):
        """Test StageDirectionGenerator initializes correctly."""
        generator = StageDirectionGenerator(
            claude_client=mock_claude_client,
            gpt_client=None,
            database_manager=None
        )
        
        assert generator.claude == mock_claude_client
        assert generator.gpt is None
        assert generator.db is None
    
    @pytest.mark.asyncio
    async def test_generate_stage_directions_success(
        self,
        stage_direction_generator,
        mock_claude_client,
        sample_scene,
        sample_scene_dialogue,
        mock_stage_directions_response
    ):
        """Test successful stage direction generation."""
        # Setup mock
        mock_claude_client.generate = AsyncMock(
            return_value=mock_stage_directions_response
        )
        
        # Generate stage directions
        directions = await stage_direction_generator.generate_stage_directions(
            scene=sample_scene,
            scene_dialogue=sample_scene_dialogue,
            comedic_beats=['Ring light falls', 'Luna trips']
        )
        
        # Verify scene stage directions created
        assert isinstance(directions, SceneStageDirections)
        assert directions.scene_number == 1
        assert 'cluttered with photography equipment' in directions.opening_description
        assert 'Equipment still scattered' in directions.closing_description
        
        # Verify action beats
        assert len(directions.action_beats) == 2
        assert all(isinstance(beat, StageDirection) for beat in directions.action_beats)
        
        first_beat = directions.action_beats[0]
        assert first_beat.timing == 'BEFORE LINE'
        assert 'reaches up' in first_beat.description
        assert first_beat.duration_estimate == 2.0
        assert 'Luna' in first_beat.involves_characters
        
        # Verify physical comedy sequences
        assert len(directions.physical_comedy_sequences) == 1
        sequence = directions.physical_comedy_sequences[0]
        assert isinstance(sequence, PhysicalComedySequence)
        assert sequence.beat_name == 'Ring Light Disaster'
        assert len(sequence.setup_actions) == 1
        assert len(sequence.escalation_actions) == 2
        assert sequence.total_duration == 11.0
        
        # Verify camera suggestions
        assert len(directions.camera_suggestions) == 2
        assert all(isinstance(cam, CameraSuggestion) for cam in directions.camera_suggestions)
        
        first_cam = directions.camera_suggestions[0]
        assert first_cam.shot_type == 'WIDE'
        assert first_cam.movement == 'PAN'
        assert 'chaos' in first_cam.focus.lower()
        
        # Verify total runtime calculated
        assert directions.total_visual_runtime > 0
        
        # Verify AI called
        mock_claude_client.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_stage_directions_without_comedic_beats(
        self,
        stage_direction_generator,
        mock_claude_client,
        sample_scene,
        sample_scene_dialogue
    ):
        """Test stage direction generation without comedic beats."""
        # Mock response without physical comedy
        mock_response = json.dumps({
            'opening_description': 'Living room setup',
            'action_beats': [
                {
                    'timing': 'CONTINUOUS',
                    'description': 'Characters talk',
                    'duration_estimate': 1.0,
                    'involves_characters': ['Luna'],
                    'visual_gag': False,
                    'camera_suggestion': None
                }
            ],
            'physical_comedy_sequences': [],
            'camera_suggestions': [],
            'closing_description': 'Scene ends'
        })
        
        mock_claude_client.generate = AsyncMock(return_value=mock_response)
        
        # Generate without comedic beats
        directions = await stage_direction_generator.generate_stage_directions(
            scene=sample_scene,
            scene_dialogue=sample_scene_dialogue,
            comedic_beats=None
        )
        
        # Should still work, just no physical comedy
        assert isinstance(directions, SceneStageDirections)
        assert len(directions.physical_comedy_sequences) == 0
        assert len(directions.action_beats) == 1
    
    @pytest.mark.asyncio
    async def test_generate_stage_directions_fallback_on_error(
        self,
        stage_direction_generator,
        mock_claude_client,
        sample_scene,
        sample_scene_dialogue
    ):
        """Test stage direction generation falls back on error."""
        # Setup mock to fail
        mock_claude_client.generate = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Generate stage directions (should fallback)
        directions = await stage_direction_generator.generate_stage_directions(
            scene=sample_scene,
            scene_dialogue=sample_scene_dialogue,
            comedic_beats=['Ring light falls']
        )
        
        # Should return minimal fallback
        assert isinstance(directions, SceneStageDirections)
        assert directions.scene_number == 1
        assert len(directions.action_beats) == 0
        assert len(directions.physical_comedy_sequences) == 0
        assert directions.total_visual_runtime == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_physical_comedy_sequence(
        self,
        stage_direction_generator,
        mock_claude_client
    ):
        """Test physical comedy sequence generation."""
        # Mock AI response
        mock_response = json.dumps({
            'beat_name': 'Cable Trip',
            'setup_actions': [
                {
                    'description': 'Luna walks backward focusing on phone',
                    'duration_estimate': 2.0,
                    'involves_characters': ['Luna']
                }
            ],
            'escalation_actions': [
                {
                    'description': 'Foot catches cable',
                    'duration_estimate': 1.0,
                    'involves_characters': ['Luna']
                }
            ],
            'climax_action': {
                'description': 'Luna trips, arms windmilling',
                'duration_estimate': 2.0,
                'involves_characters': ['Luna']
            },
            'resolution_action': {
                'description': 'Lands on couch, phone still in hand',
                'duration_estimate': 1.0,
                'involves_characters': ['Luna']
            },
            'total_duration': 6.0
        })
        
        mock_claude_client.generate = AsyncMock(return_value=mock_response)
        
        # Generate sequence
        sequence = await stage_direction_generator._generate_physical_comedy_sequence(
            comedic_beat='Luna trips over cable',
            characters=['Luna'],
            location='Living Room'
        )
        
        # Verify sequence created
        assert isinstance(sequence, PhysicalComedySequence)
        assert 'Cable Trip' in sequence.beat_name or 'Luna trips' in sequence.beat_name
        assert sequence.total_duration > 0
    
    @pytest.mark.asyncio
    async def test_generate_physical_comedy_sequence_fallback(
        self,
        stage_direction_generator,
        mock_claude_client
    ):
        """Test physical comedy sequence generation with AI failure."""
        # Setup mock to fail
        mock_claude_client.generate = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Generate sequence (should fallback)
        sequence = await stage_direction_generator._generate_physical_comedy_sequence(
            comedic_beat='Luna trips',
            characters=['Luna'],
            location='Living Room'
        )
        
        # Should return basic sequence
        assert isinstance(sequence, PhysicalComedySequence)
        assert 'Luna trips' in sequence.beat_name
        assert sequence.total_duration > 0
        assert isinstance(sequence.climax_action, StageDirection)
    
    def test_suggest_camera_work_physical_comedy(
        self,
        stage_direction_generator
    ):
        """Test camera suggestions for physical comedy."""
        suggestion = stage_direction_generator._suggest_camera_work(
            action_type='physical_comedy',
            emotional_beat='slapstick'
        )
        
        assert isinstance(suggestion, CameraSuggestion)
        assert suggestion.shot_type == 'WIDE'
        assert 'full action' in suggestion.focus.lower()
        assert 'physical' in suggestion.reasoning.lower()
    
    def test_suggest_camera_work_punchline(
        self,
        stage_direction_generator
    ):
        """Test camera suggestions for punchline."""
        suggestion = stage_direction_generator._suggest_camera_work(
            action_type='dialogue',
            emotional_beat='punchline'
        )
        
        assert isinstance(suggestion, CameraSuggestion)
        assert suggestion.shot_type == 'CLOSE-UP'
        assert 'face' in suggestion.focus.lower()
        assert 'reaction' in suggestion.reasoning.lower()
    
    def test_suggest_camera_work_reaction(
        self,
        stage_direction_generator
    ):
        """Test camera suggestions for reaction."""
        suggestion = stage_direction_generator._suggest_camera_work(
            action_type='dialogue',
            emotional_beat='reaction'
        )
        
        assert isinstance(suggestion, CameraSuggestion)
        assert suggestion.shot_type == 'CLOSE-UP'
        assert 'character' in suggestion.focus.lower()
    
    def test_suggest_camera_work_default(
        self,
        stage_direction_generator
    ):
        """Test camera suggestions for default case."""
        suggestion = stage_direction_generator._suggest_camera_work(
            action_type='dialogue',
            emotional_beat='normal'
        )
        
        assert isinstance(suggestion, CameraSuggestion)
        assert suggestion.shot_type == 'MEDIUM'
        assert suggestion.movement is None


class TestCameraSuggestion:
    """Test suite for CameraSuggestion dataclass."""
    
    def test_camera_suggestion_creation(self):
        """Test creating camera suggestion."""
        camera = CameraSuggestion(
            shot_type='CLOSE-UP',
            focus='Luna\'s face',
            reasoning='Capture scheming expression',
            movement='ZOOM IN',
            timing='During punchline'
        )
        
        assert camera.shot_type == 'CLOSE-UP'
        assert camera.focus == 'Luna\'s face'
        assert camera.movement == 'ZOOM IN'
        assert camera.timing == 'During punchline'
    
    def test_camera_suggestion_format_for_script(self):
        """Test camera suggestion formatting."""
        camera = CameraSuggestion(
            shot_type='WIDE',
            focus='Full room',
            reasoning='Show chaos',
            movement='PAN',
            timing='Opening'
        )
        
        formatted = camera.format_for_script()
        
        assert 'WIDE' in formatted
        assert 'PAN' in formatted
        assert 'Full room' in formatted
    
    def test_camera_suggestion_format_without_movement(self):
        """Test camera suggestion formatting without movement."""
        camera = CameraSuggestion(
            shot_type='MEDIUM',
            focus='Characters',
            reasoning='Standard coverage'
        )
        
        formatted = camera.format_for_script()
        
        assert 'MEDIUM' in formatted
        assert 'Characters' in formatted
        assert 'PAN' not in formatted
    
    def test_camera_suggestion_to_dict(self):
        """Test camera suggestion serialization."""
        camera = CameraSuggestion(
            shot_type='TWO-SHOT',
            focus='Luna and Ricky',
            reasoning='Show interaction',
            movement=None,
            timing='Continuous'
        )
        
        data = camera.to_dict()
        
        assert data['shot_type'] == 'TWO-SHOT'
        assert data['focus'] == 'Luna and Ricky'
        assert data['movement'] is None


class TestStageDirection:
    """Test suite for StageDirection dataclass."""
    
    def test_stage_direction_creation(self):
        """Test creating stage direction."""
        direction = StageDirection(
            timing='BEFORE LINE',
            description='Luna rushes to window',
            duration_estimate=2.5,
            involves_characters=['Luna'],
            visual_gag=False
        )
        
        assert direction.timing == 'BEFORE LINE'
        assert direction.description == 'Luna rushes to window'
        assert direction.duration_estimate == 2.5
        assert 'Luna' in direction.involves_characters
        assert direction.visual_gag is False
    
    def test_stage_direction_with_camera(self):
        """Test stage direction with camera suggestion."""
        camera = CameraSuggestion(
            shot_type='CLOSE-UP',
            focus='Luna',
            reasoning='Capture reaction'
        )
        
        direction = StageDirection(
            timing='DURING LINE',
            description='Luna reacts',
            duration_estimate=1.0,
            involves_characters=['Luna'],
            visual_gag=False,
            camera_suggestion=camera
        )
        
        assert direction.camera_suggestion is not None
        assert direction.camera_suggestion.shot_type == 'CLOSE-UP'
    
    def test_stage_direction_format_for_screenplay(self):
        """Test stage direction screenplay formatting."""
        direction = StageDirection(
            timing='CONTINUOUS',
            description='Luna trips over cable',
            duration_estimate=2.0,
            involves_characters=['Luna'],
            visual_gag=True
        )
        
        formatted = direction.format_for_screenplay()
        
        assert '[Luna trips over cable]' in formatted
    
    def test_stage_direction_format_with_camera(self):
        """Test stage direction formatting with camera."""
        camera = CameraSuggestion(
            shot_type='WIDE',
            focus='Full action',
            reasoning='Show slapstick'
        )
        
        direction = StageDirection(
            timing='CONTINUOUS',
            description='Physical comedy',
            duration_estimate=3.0,
            involves_characters=['Luna'],
            visual_gag=True,
            camera_suggestion=camera
        )
        
        formatted = direction.format_for_screenplay()
        
        assert '[Physical comedy]' in formatted
        assert 'WIDE' in formatted
    
    def test_stage_direction_to_dict(self):
        """Test stage direction serialization."""
        direction = StageDirection(
            timing='AFTER LINE',
            description='Characters freeze',
            duration_estimate=1.5,
            involves_characters=['Luna', 'Ricky'],
            visual_gag=False
        )
        
        data = direction.to_dict()
        
        assert data['timing'] == 'AFTER LINE'
        assert data['description'] == 'Characters freeze'
        assert data['duration_estimate'] == 1.5
        assert 'Luna' in data['involves_characters']


class TestPhysicalComedySequence:
    """Test suite for PhysicalComedySequence dataclass."""
    
    def test_physical_comedy_sequence_creation(self):
        """Test creating physical comedy sequence."""
        setup = [
            StageDirection(
                timing='CONTINUOUS',
                description='Setup action',
                duration_estimate=1.0,
                involves_characters=['Luna'],
                visual_gag=True
            )
        ]
        
        escalation = [
            StageDirection(
                timing='CONTINUOUS',
                description='Escalation action',
                duration_estimate=2.0,
                involves_characters=['Luna'],
                visual_gag=True
            )
        ]
        
        climax = StageDirection(
            timing='CONTINUOUS',
            description='Climax action',
            duration_estimate=3.0,
            involves_characters=['Luna'],
            visual_gag=True
        )
        
        resolution = StageDirection(
            timing='AFTER',
            description='Resolution action',
            duration_estimate=1.0,
            involves_characters=['Luna'],
            visual_gag=True
        )
        
        sequence = PhysicalComedySequence(
            beat_name='Test Gag',
            setup_actions=setup,
            escalation_actions=escalation,
            climax_action=climax,
            resolution_action=resolution,
            total_duration=7.0
        )
        
        assert sequence.beat_name == 'Test Gag'
        assert len(sequence.setup_actions) == 1
        assert len(sequence.escalation_actions) == 1
        assert sequence.total_duration == 7.0
    
    def test_get_all_actions(self):
        """Test getting all actions in sequence."""
        setup = [StageDirection('C', 'Setup', 1.0, ['A'], True)]
        escalation = [
            StageDirection('C', 'Esc1', 1.0, ['A'], True),
            StageDirection('C', 'Esc2', 1.0, ['A'], True)
        ]
        climax = StageDirection('C', 'Climax', 2.0, ['A'], True)
        resolution = StageDirection('A', 'Resolution', 1.0, ['A'], True)
        
        sequence = PhysicalComedySequence(
            beat_name='Test',
            setup_actions=setup,
            escalation_actions=escalation,
            climax_action=climax,
            resolution_action=resolution,
            total_duration=6.0
        )
        
        all_actions = sequence.get_all_actions()
        
        # Should have 1 setup + 2 escalation + 1 climax + 1 resolution = 5
        assert len(all_actions) == 5
        assert all_actions[0].description == 'Setup'
        assert all_actions[1].description == 'Esc1'
        assert all_actions[2].description == 'Esc2'
        assert all_actions[3].description == 'Climax'
        assert all_actions[4].description == 'Resolution'
    
    def test_format_for_screenplay(self):
        """Test physical comedy sequence screenplay formatting."""
        setup = [StageDirection('C', 'Setup', 1.0, ['Luna'], True)]
        escalation = [StageDirection('C', 'Build tension', 2.0, ['Luna'], True)]
        climax = StageDirection('C', 'Big fall', 3.0, ['Luna'], True)
        resolution = StageDirection('A', 'Dust off', 1.0, ['Luna'], True)
        
        sequence = PhysicalComedySequence(
            beat_name='Cable Trip',
            setup_actions=setup,
            escalation_actions=escalation,
            climax_action=climax,
            resolution_action=resolution,
            total_duration=7.0
        )
        
        formatted = sequence.format_for_screenplay()
        
        assert 'PHYSICAL COMEDY: Cable Trip' in formatted
        assert '[Setup]' in formatted
        assert '[Big fall]' in formatted
        assert 'Duration: 7.0s' in formatted
    
    def test_to_dict(self):
        """Test physical comedy sequence serialization."""
        setup = [StageDirection('C', 'Setup', 1.0, ['Luna'], True)]
        escalation = [StageDirection('C', 'Escalate', 1.0, ['Luna'], True)]
        climax = StageDirection('C', 'Climax', 2.0, ['Luna'], True)
        resolution = StageDirection('A', 'Resolve', 1.0, ['Luna'], True)
        
        sequence = PhysicalComedySequence(
            beat_name='Test',
            setup_actions=setup,
            escalation_actions=escalation,
            climax_action=climax,
            resolution_action=resolution,
            total_duration=5.0
        )
        
        data = sequence.to_dict()
        
        assert data['beat_name'] == 'Test'
        assert len(data['setup_actions']) == 1
        assert len(data['escalation_actions']) == 1
        assert data['total_duration'] == 5.0


class TestSceneStageDirections:
    """Test suite for SceneStageDirections dataclass."""
    
    def test_scene_stage_directions_creation(self):
        """Test creating scene stage directions."""
        action_beats = [
            StageDirection('BEFORE', 'Action 1', 1.0, ['Luna'], False)
        ]
        
        sequences = []
        
        camera_suggestions = [
            CameraSuggestion('WIDE', 'Room', 'Establish scene')
        ]
        
        directions = SceneStageDirections(
            scene_number=1,
            opening_description='Living room scene',
            action_beats=action_beats,
            physical_comedy_sequences=sequences,
            closing_description='Scene ends',
            camera_suggestions=camera_suggestions,
            total_visual_runtime=10.0
        )
        
        assert directions.scene_number == 1
        assert len(directions.action_beats) == 1
        assert len(directions.camera_suggestions) == 1
        assert directions.total_visual_runtime == 10.0
    
    def test_get_all_directions(self):
        """Test getting all directions including sequences."""
        action_beats = [
            StageDirection('BEFORE', 'Beat 1', 1.0, ['Luna'], False)
        ]
        
        sequence_setup = [StageDirection('C', 'Setup', 1.0, ['Luna'], True)]
        sequence_escalation = [StageDirection('C', 'Escalate', 1.0, ['Luna'], True)]
        sequence_climax = StageDirection('C', 'Climax', 2.0, ['Luna'], True)
        sequence_resolution = StageDirection('A', 'Resolve', 1.0, ['Luna'], True)
        
        sequence = PhysicalComedySequence(
            beat_name='Gag',
            setup_actions=sequence_setup,
            escalation_actions=sequence_escalation,
            climax_action=sequence_climax,
            resolution_action=sequence_resolution,
            total_duration=5.0
        )
        
        directions = SceneStageDirections(
            scene_number=1,
            opening_description='Open',
            action_beats=action_beats,
            physical_comedy_sequences=[sequence],
            closing_description='Close',
            camera_suggestions=[],
            total_visual_runtime=15.0
        )
        
        all_directions = directions.get_all_directions()
        
        # 1 action beat + 4 from sequence = 5 total
        assert len(all_directions) == 5
    
    def test_format_for_screenplay(self):
        """Test scene stage directions screenplay formatting."""
        action_beats = [
            StageDirection('BEFORE', 'Luna enters', 1.0, ['Luna'], False)
        ]
        
        camera_suggestions = [
            CameraSuggestion('MEDIUM', 'Luna', 'Track entrance')
        ]
        
        directions = SceneStageDirections(
            scene_number=5,
            opening_description='Kitchen is messy',
            action_beats=action_beats,
            physical_comedy_sequences=[],
            closing_description='Luna exits',
            camera_suggestions=camera_suggestions,
            total_visual_runtime=20.0
        )
        
        formatted = directions.format_for_screenplay()
        
        assert 'SCENE 5' in formatted
        assert 'Kitchen is messy' in formatted
        assert '[Luna enters]' in formatted
        assert 'Luna exits' in formatted
        assert 'CAMERA NOTES' in formatted
        assert 'Total Visual Runtime: 20.0s' in formatted
    
    def test_to_dict(self):
        """Test scene stage directions serialization."""
        action_beats = [
            StageDirection('DURING', 'Action', 1.0, ['Luna'], False)
        ]
        
        directions = SceneStageDirections(
            scene_number=3,
            opening_description='Scene opens',
            action_beats=action_beats,
            physical_comedy_sequences=[],
            closing_description='Scene closes',
            camera_suggestions=[],
            total_visual_runtime=5.0
        )
        
        data = directions.to_dict()
        
        assert data['scene_number'] == 3
        assert data['opening_description'] == 'Scene opens'
        assert len(data['action_beats']) == 1
        assert data['total_visual_runtime'] == 5.0
        assert 'generated_at' in data
