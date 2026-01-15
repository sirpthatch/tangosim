"""Tests for game recording and serialization functionality."""

import pytest
import json
import tempfile
import os

from tangosim.models import Tile, TangoAction, ActionType
from tangosim.recorder import GameRecord, create_game_record


class TestTileSerialization:
    """Tests for Tile serialization."""

    def test_to_dict(self):
        """Tile.to_dict should produce correct dictionary."""
        tile = Tile([True, False, True, False, True, False], 0)
        d = tile.to_dict()
        assert d['pattern'] == [True, False, True, False, True, False]
        assert d['color'] == 0
        assert 'id' in d

    def test_from_dict(self):
        """Tile.from_dict should recreate tile correctly."""
        original = Tile([True, True, False, False, True, False], 1)
        d = original.to_dict()
        restored = Tile.from_dict(d)
        assert restored.pattern == original.pattern
        assert restored.color == original.color
        assert restored.id == original.id

    def test_roundtrip(self):
        """Tile should survive serialization roundtrip."""
        original = Tile([False, False, False, True, True, True], 0)
        restored = Tile.from_dict(original.to_dict())
        assert original.is_rotationally_equal(restored)


class TestTangoActionSerialization:
    """Tests for TangoAction serialization."""

    def test_place_action_to_dict(self):
        """PLACE action should serialize correctly."""
        tile = Tile([True, False, False, False, False, False], 0)
        action = TangoAction(
            action_type=ActionType.PLACE,
            tile=tile,
            player=0,
            destination=(1, 2)
        )
        d = action.to_dict()
        assert d['action_type'] == 'PLACE'
        assert d['destination'] == [1, 2]
        assert d['origin'] is None
        assert d['player'] == 0

    def test_move_action_to_dict(self):
        """MOVE action should serialize correctly."""
        tile = Tile([True, True, False, False, False, False], 1)
        action = TangoAction(
            action_type=ActionType.MOVE,
            tile=tile,
            player=1,
            destination=(3, 4),
            origin=(1, 2)
        )
        d = action.to_dict()
        assert d['action_type'] == 'MOVE'
        assert d['destination'] == [3, 4]
        assert d['origin'] == [1, 2]
        assert d['player'] == 1

    def test_from_dict_place(self):
        """PLACE action should deserialize correctly."""
        tile = Tile([True, False, False, False, False, False], 0)
        original = TangoAction(
            action_type=ActionType.PLACE,
            tile=tile,
            player=0,
            destination=(0, 0)
        )
        d = original.to_dict()
        restored = TangoAction.from_dict(d)
        assert restored.action_type == ActionType.PLACE
        assert restored.destination == (0, 0)
        assert restored.origin is None
        assert restored.player == 0

    def test_from_dict_move(self):
        """MOVE action should deserialize correctly."""
        tile = Tile([True, True, True, False, False, False], 1)
        original = TangoAction(
            action_type=ActionType.MOVE,
            tile=tile,
            player=1,
            destination=(2, 3),
            origin=(0, 1)
        )
        d = original.to_dict()
        restored = TangoAction.from_dict(d)
        assert restored.action_type == ActionType.MOVE
        assert restored.destination == (2, 3)
        assert restored.origin == (0, 1)
        assert restored.player == 1

    def test_action_validation_place(self):
        """PLACE action should validate correctly."""
        tile = Tile([True, False, False, False, False, False], 0)
        action = TangoAction(
            action_type=ActionType.PLACE,
            tile=tile,
            player=0,
            destination=(0, 0)
        )
        # Should not raise
        action.validate()

    def test_action_validation_move(self):
        """MOVE action should validate correctly."""
        tile = Tile([True, False, False, False, False, False], 0)
        action = TangoAction(
            action_type=ActionType.MOVE,
            tile=tile,
            player=0,
            destination=(1, 0),
            origin=(0, 0)
        )
        # Should not raise
        action.validate()

    def test_action_validation_place_with_origin_fails(self):
        """PLACE action with origin should fail validation."""
        tile = Tile([True, False, False, False, False, False], 0)
        action = TangoAction(
            action_type=ActionType.PLACE,
            tile=tile,
            player=0,
            destination=(0, 0),
            origin=(1, 1)
        )
        with pytest.raises(AssertionError):
            action.validate()

    def test_action_validation_move_without_origin_fails(self):
        """MOVE action without origin should fail validation."""
        tile = Tile([True, False, False, False, False, False], 0)
        action = TangoAction(
            action_type=ActionType.MOVE,
            tile=tile,
            player=0,
            destination=(1, 0)
        )
        with pytest.raises(AssertionError):
            action.validate()


class TestGameRecord:
    """Tests for GameRecord class."""

    def test_create_game_record(self):
        """create_game_record should create a valid record."""
        tiles_p0 = {Tile([True, False, False, False, False, False], 0)}
        tiles_p1 = {Tile([True, False, False, False, False, False], 1)}

        action = TangoAction(
            action_type=ActionType.PLACE,
            tile=Tile([True, False, False, False, False, False], 0),
            player=0,
            destination=(0, 0)
        )

        record = create_game_record(
            game_mode='simple',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[action],
            final_scores=[5, 3],
            rounds=10
        )

        assert record.game_mode == 'simple'
        assert record.winner == 0  # Player 0 won
        assert record.final_scores == [5, 3]
        assert record.rounds == 10
        assert len(record.actions) == 1

    def test_create_game_record_tie(self):
        """create_game_record should handle ties correctly."""
        tiles_p0 = {Tile([True, False, False, False, False, False], 0)}
        tiles_p1 = {Tile([True, False, False, False, False, False], 1)}

        record = create_game_record(
            game_mode='advanced',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[],
            final_scores=[5, 5],
            rounds=10
        )

        assert record.winner == -1  # Tie

    def test_to_json(self):
        """GameRecord.to_json should produce valid JSON."""
        tiles_p0 = {Tile([True, False, False, False, False, False], 0)}
        tiles_p1 = {Tile([True, False, False, False, False, False], 1)}

        record = create_game_record(
            game_mode='simple',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[],
            final_scores=[5, 3],
            rounds=10
        )

        json_str = record.to_json()
        parsed = json.loads(json_str)
        assert parsed['game_mode'] == 'simple'
        assert parsed['winner'] == 0
        assert parsed['final_scores'] == [5, 3]

    def test_from_json(self):
        """GameRecord.from_json should restore record correctly."""
        tiles_p0 = {Tile([True, False, False, False, False, False], 0)}
        tiles_p1 = {Tile([True, False, False, False, False, False], 1)}

        original = create_game_record(
            game_mode='advanced',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[],
            final_scores=[3, 7],
            rounds=15
        )

        json_str = original.to_json()
        restored = GameRecord.from_json(json_str)

        assert restored.game_mode == original.game_mode
        assert restored.winner == original.winner
        assert restored.final_scores == original.final_scores
        assert restored.rounds == original.rounds

    def test_save_and_load(self):
        """GameRecord should save and load from file correctly."""
        tiles_p0 = {Tile([True, False, False, False, False, False], 0)}
        tiles_p1 = {Tile([True, False, False, False, False, False], 1)}

        original = create_game_record(
            game_mode='simple',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[],
            final_scores=[10, 8],
            rounds=20
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            original.save(filepath)
            restored = GameRecord.load(filepath)

            assert restored.game_mode == original.game_mode
            assert restored.winner == original.winner
            assert restored.final_scores == original.final_scores
            assert restored.rounds == original.rounds
        finally:
            os.unlink(filepath)

    def test_get_actions(self):
        """get_actions should deserialize actions correctly."""
        tiles_p0 = {Tile([True, False, False, False, False, False], 0)}
        tiles_p1 = {Tile([True, False, False, False, False, False], 1)}

        action = TangoAction(
            action_type=ActionType.PLACE,
            tile=Tile([True, False, False, False, False, False], 0),
            player=0,
            destination=(0, 0)
        )

        record = create_game_record(
            game_mode='simple',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[action],
            final_scores=[5, 3],
            rounds=10
        )

        actions = record.get_actions()
        assert len(actions) == 1
        assert actions[0].action_type == ActionType.PLACE
        assert actions[0].destination == (0, 0)

    def test_get_initial_tiles(self):
        """get_initial_tiles should deserialize tiles correctly."""
        tile_p0 = Tile([True, False, False, False, False, False], 0)
        tile_p1 = Tile([True, True, False, False, False, False], 1)
        tiles_p0 = {tile_p0}
        tiles_p1 = {tile_p1}

        record = create_game_record(
            game_mode='simple',
            initial_tiles=[tiles_p0, tiles_p1],
            actions=[],
            final_scores=[5, 3],
            rounds=10
        )

        initial_tiles = record.get_initial_tiles()
        assert len(initial_tiles) == 2
        assert len(initial_tiles[0]) == 1
        assert len(initial_tiles[1]) == 1
