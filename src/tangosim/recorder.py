"""Game recording and replay functionality."""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set

from tangosim.models import Tile, TangoAction


@dataclass
class GameRecord:
    """A complete record of a game that can be serialized and replayed."""

    game_mode: str
    initial_tiles: List[List[Dict[str, Any]]]  # Per-player starting tiles (serialized)
    actions: List[Dict[str, Any]]  # Serialized TangoActions
    final_scores: List[int]
    winner: int  # Player index, -1 for tie
    rounds: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'game_mode': self.game_mode,
            'initial_tiles': self.initial_tiles,
            'actions': self.actions,
            'final_scores': self.final_scores,
            'winner': self.winner,
            'rounds': self.rounds
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameRecord':
        """Create GameRecord from dictionary."""
        return cls(
            game_mode=data['game_mode'],
            initial_tiles=data['initial_tiles'],
            actions=data['actions'],
            final_scores=data['final_scores'],
            winner=data['winner'],
            rounds=data['rounds']
        )

    def to_json(self, indent: int = 2) -> str:
        """Export as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> 'GameRecord':
        """Create GameRecord from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def save(self, filepath: str) -> None:
        """Save record to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> 'GameRecord':
        """Load record from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def get_actions(self) -> List[TangoAction]:
        """Deserialize and return the list of TangoActions."""
        return [TangoAction.from_dict(a) for a in self.actions]

    def get_initial_tiles(self) -> List[Set[Tile]]:
        """Deserialize and return the initial tile sets for each player."""
        return [
            set(Tile.from_dict(t) for t in player_tiles)
            for player_tiles in self.initial_tiles
        ]


def create_game_record(
    game_mode: str,
    initial_tiles: List[Set[Tile]],
    actions: List[TangoAction],
    final_scores: List[int],
    rounds: int
) -> GameRecord:
    """Create a GameRecord from game data.

    Args:
        game_mode: 'simple' or 'advanced'
        initial_tiles: List of tile sets per player at game start
        actions: List of TangoActions taken during game
        final_scores: Final score for each player
        rounds: Number of rounds played

    Returns:
        GameRecord ready for serialization
    """
    # Determine winner
    max_score = max(final_scores)
    winners = [i for i, s in enumerate(final_scores) if s == max_score]
    winner = winners[0] if len(winners) == 1 else -1

    return GameRecord(
        game_mode=game_mode,
        initial_tiles=[[t.to_dict() for t in tiles] for tiles in initial_tiles],
        actions=[a.to_dict() for a in actions],
        final_scores=final_scores,
        winner=winner,
        rounds=rounds
    )
