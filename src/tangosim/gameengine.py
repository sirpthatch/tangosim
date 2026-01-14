from typing import Set, Tuple, List, Optional
from tangosim.models import GameState, Tile, get_bordering_positions
from tangosim.strategy import Strategy


class TangoGame:
    """Base class for Tango game variants."""

    @staticmethod
    def _init_gamepieces(color: int) -> Set[Tile]:
        """Initialize the standard set of 13 tiles for a player."""
        possible_tile_configurations = [
            [True, False, False, False, False, False],

            [True, True, False, False, False, False],
            [True, False, True, False, False, False],
            [True, False, False, True, False, False],

            [True, True, True, False, False, False],
            [True, False, True, True, False, False],
            [True, False, True, False, True, False],
            [True, False, True, False, False, True],

            [False, False, True, True, True, True],
            [False, True, False, True, True, True],
            [False, True, True, False, True, True],

            [True, True, True, True, True, False],
            [True, True, True, True, True, True]
        ]
        return set([Tile(p, color) for p in possible_tile_configurations])

    def __init__(self, players: List[Strategy], player_tiles: List[Set[Tile]] = None):
        self.players = players
        self.player_tiles = player_tiles if player_tiles else [
            TangoGame._init_gamepieces(n) for n in range(len(players))
        ]
        self.gamestate = GameState()

    def play(self, max_rounds: int = 1000) -> Tuple[GameState, int, int]:
        """Play the game to completion.

        Args:
            max_rounds: Maximum number of rounds before forcing game end (prevents infinite loops)

        Returns:
            Tuple of (final GameState, last active player index, total rounds)
        """
        round_num = -1
        active_player_idx = 0

        while round_num < max_rounds:
            round_num += 1
            active_player_idx = round_num % len(self.players)

            if self.is_game_over(active_player_idx):
                break

            self._execute_turn(active_player_idx)

        return (self.gamestate, active_player_idx, round_num)

    def _execute_turn(self, player_idx: int) -> None:
        """Execute a single turn for the given player. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _execute_turn")

    def is_game_over(self, whose_turn: int) -> bool:
        """Check if the game is over. Override in subclasses for different end conditions."""
        return len(self.player_tiles[whose_turn]) == 0

    def _handle_pops(self, player_idx: int, surrounded_tiles: List[Tuple[int, int]]) -> None:
        """Handle popping of surrounded tiles."""
        strategy = self.players[player_idx]

        while len(surrounded_tiles):
            location_to_pop = strategy.pick_piece_to_pop(
                self.gamestate,
                self.player_tiles[player_idx],
                surrounded_tiles
            )
            popped_tile = self.gamestate.pop_piece(location_to_pop)
            surrounded_tiles.remove(location_to_pop)
            self.player_tiles[popped_tile.color].add(popped_tile)

            # Re-check remaining positions - some may no longer be surrounded
            surrounded_tiles = [t for t in surrounded_tiles if self.gamestate.is_surrounded(t)]

    def _place_tile_and_update(self, player_idx: int, tile: Tile, location: Tuple[int, int]) -> None:
        """Place a tile and handle the resulting game state updates."""
        available_tiles = self.player_tiles[player_idx]
        surrounded_tiles = self.gamestate.place_tile(tile, location)

        # Remove the placed tile from player's hand
        self.player_tiles[player_idx] = set(
            [t for t in available_tiles if not t.is_rotationally_equal(tile)]
        )

        # Handle any pops
        self._handle_pops(player_idx, surrounded_tiles)


class SimpleTangoGame(TangoGame):
    """Simple Tango game - players can only place new tiles from their hand."""

    def _execute_turn(self, player_idx: int) -> None:
        """Execute a simple turn: place a tile from hand."""
        strategy = self.players[player_idx]
        available_tiles = self.player_tiles[player_idx]

        (tile_to_place, location) = strategy.formulate_turn(self.gamestate, available_tiles)
        self._place_tile_and_update(player_idx, tile_to_place, location)


class AdvancedTangoGame(TangoGame):
    """Advanced Tango game - players can place tiles OR move existing tiles on the board.

    Move rules:
    - A player can move one of their own tiles already on the board
    - The tile can move up to N spaces, where N = number of blank (unfilled) edges
    - Tiles can rotate when moved
    - Moved tiles can land in enclosed areas (but not surrounded positions)
    - Game ends when a player has no tiles AND has the most points
    """

    def _execute_turn(self, player_idx: int) -> None:
        """Execute an advanced turn: place a tile OR move an existing tile."""
        strategy = self.players[player_idx]
        available_tiles = self.player_tiles[player_idx]

        # First, check if strategy wants to move an existing tile
        move_action = strategy.formulate_move(
            self.gamestate,
            available_tiles,
            player_idx
        )

        if move_action is not None:
            (from_pos, to_pos, rotated_tile) = move_action
            self._move_tile(player_idx, from_pos, to_pos, rotated_tile)
        elif len(available_tiles) > 0:
            # Fall back to placing a new tile (only if player has tiles)
            (tile_to_place, location) = strategy.formulate_turn(self.gamestate, available_tiles)
            self._place_tile_and_update(player_idx, tile_to_place, location)
        # If no tiles and no move action, turn is skipped (player waits for opponent)

    def _move_tile(self, player_idx: int, from_pos: Tuple[int, int],
                   to_pos: Tuple[int, int], rotated_tile: Tile) -> None:
        """Move a tile from one position to another."""
        # Remove tile from old position
        self.gamestate.remove_tile(from_pos)

        # Place at new position (this handles constraint checking)
        surrounded_tiles = self.gamestate.place_tile_for_move(rotated_tile, to_pos)

        # Handle any pops
        self._handle_pops(player_idx, surrounded_tiles)

    def is_game_over(self, whose_turn: int) -> bool:
        """Game ends when a player has no tiles AND has the highest score."""
        if len(self.player_tiles[whose_turn]) > 0:
            return False

        # Player has no tiles - check if they have the highest score
        scores = self.gamestate.get_scores()
        player_score = scores[whose_turn]
        max_opponent_score = max(
            score for i, score in enumerate(scores) if i != whose_turn
        )

        return player_score > max_opponent_score

    def get_valid_move_destinations(self, from_pos: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all valid destination positions for moving a tile.

        Args:
            from_pos: The current position of the tile to move

        Returns:
            Set of valid destination positions within movement range
        """
        tile = self.gamestate.tiles.get(from_pos)
        if tile is None:
            return set()

        # Movement range = number of blank (unfilled) edges
        max_distance = 6 - tile.num_ticks()
        if max_distance == 0:
            return set()

        # BFS to find all positions within range
        valid_destinations = set()
        visited = {from_pos}
        current_frontier = {from_pos}

        for distance in range(1, max_distance + 1):
            next_frontier = set()
            for pos in current_frontier:
                for neighbor in get_bordering_positions(pos):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        # Position is valid if it's empty or has a tile (we'll remove ours)
                        # But we need to check if placing there would be legal
                        if neighbor not in self.gamestate.tiles or neighbor == from_pos:
                            next_frontier.add(neighbor)
                            if neighbor != from_pos:
                                valid_destinations.add(neighbor)
            current_frontier = next_frontier

        return valid_destinations
