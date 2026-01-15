from tangosim.models import Tile, GameState, TangoAction, ActionType, get_bordering_positions
from typing import Set, Tuple, List
from random import randint


class Strategy:

    def __init__(self):
        self.turn_number = 0
        self.turn_diagnostics = []

    def formulate_action(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         player_idx: int) -> TangoAction:
        """Formulate the action for this turn.

        Args:
            game_state: Current game state
            available_pieces: Tiles in player's hand
            player_idx: The player's index (color)

        Returns:
            TangoAction with either PLACE or MOVE action type
        """
        self.turn_number += 1
        return self.formulate_action_impl(game_state, available_pieces, player_idx)

    def formulate_action_impl(self,
                              game_state: GameState,
                              available_pieces: Set[Tile],
                              player_idx: int) -> TangoAction:
        """Override this in subclasses to implement action logic.

        Returns:
            TangoAction for this turn
        """
        raise NotImplementedError()

    def pick_piece_to_pop(self,
                          game_state: GameState,
                          available_pieces: Set[Tile],
                          possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Select which piece to pop when multiple options exist.

        Returns:
            The (q, r) location to pop
        """
        raise NotImplementedError()


class RandomStrategy(Strategy):

    def __init__(self, player: int):
        super().__init__()
        self.player = player

    def formulate_action_impl(self,
                              game_state: GameState,
                              available_pieces: Set[Tile],
                              player_idx: int) -> TangoAction:
        """Randomly choose between placing a new tile or moving an existing one."""
        # Try to move an existing tile (50% chance if possible)
        move_action = self._try_formulate_move(game_state, player_idx)
        if move_action is not None:
            return move_action

        # Place a new tile
        return self._formulate_placement(game_state, available_pieces, player_idx)

    def _formulate_placement(self,
                             game_state: GameState,
                             available_pieces: Set[Tile],
                             player_idx: int) -> TangoAction:
        """Find a random valid placement."""
        viable_moves = []
        available_positions = list(game_state.get_available_positions())

        for tile in available_pieces:
            for position in available_positions:
                for projection in tile.unique_rotations:
                    score = game_state.score_potential_move(projection, position)
                    if score is not None:
                        viable_moves.append((projection, position))

        (piece, position) = viable_moves[randint(0, len(viable_moves) - 1)]
        diags = {
            "turn": self.turn_number,
            "moves_evaluated": len(viable_moves)
        }
        self.turn_diagnostics.append(diags)
        print(f"Player {self.player} Place {piece.pattern} to {position}")

        return TangoAction(
            action_type=ActionType.PLACE,
            tile=piece,
            player=player_idx,
            destination=position
        )

    def _try_formulate_move(self,
                            game_state: GameState,
                            player_idx: int) -> TangoAction:
        """Try to formulate a move action. Returns None if no move or randomly choosing not to move."""
        # Get all player's tiles on the board that can move
        movable_tiles = []
        for pos, tile in game_state.tiles.items():
            if tile.color == player_idx:
                move_range = 6 - tile.num_ticks()  # Blank edges = movement range
                if move_range > 0:
                    movable_tiles.append((pos, tile, move_range))

        if not movable_tiles:
            return None  # No tiles can move

        # 50% chance to try moving instead of placing
        if randint(0, 1) == 0:
            return None

        # Pick a random movable tile
        from_pos, tile, max_distance = movable_tiles[randint(0, len(movable_tiles) - 1)]

        # Find valid destinations
        valid_moves = self._get_valid_move_destinations(game_state, from_pos, tile, max_distance)

        if not valid_moves:
            return None  # No valid moves for this tile

        # Pick random destination and rotation
        to_pos, rotated_tile = valid_moves[randint(0, len(valid_moves) - 1)]
        print(f"Player {self.player} Moving tile from {from_pos} to {to_pos}")

        return TangoAction(
            action_type=ActionType.MOVE,
            tile=rotated_tile,
            player=player_idx,
            destination=to_pos,
            origin=from_pos
        )

    def _get_valid_move_destinations(self, game_state: GameState, from_pos: Tuple[int, int],
                                     tile: Tile, max_distance: int) -> List[Tuple[Tuple[int, int], Tile]]:
        """Get all valid (destination, rotated_tile) pairs for a move."""
        valid_moves = []

        # BFS to find positions within range
        visited = {from_pos}
        current_frontier = {from_pos}

        for _ in range(max_distance):
            next_frontier = set()
            for pos in current_frontier:
                for neighbor in get_bordering_positions(pos):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        # Can move through empty spaces or spaces with tiles
                        if neighbor not in game_state.tiles:
                            next_frontier.add(neighbor)
                            # Check if we can legally place here
                            for rotation in tile.unique_rotations:
                                if self._is_valid_move_destination(game_state, neighbor, rotation, from_pos):
                                    valid_moves.append((neighbor, rotation))
            current_frontier = next_frontier

        return valid_moves

    def _is_valid_move_destination(self, game_state: GameState, position: Tuple[int, int],
                                   tile: Tile, from_pos: Tuple[int, int]) -> bool:
        """Check if a position is a valid move destination."""
        # Can't be surrounded (all 6 neighbors occupied)
        bordering = get_bordering_positions(position)
        occupied_neighbors = sum(1 for p in bordering if p in game_state.tiles and p != from_pos)
        if occupied_neighbors == 6:
            return False

        # Check edge constraints with neighbors (excluding the tile we're moving)
        for idx, neighbor_pos in enumerate(bordering):
            if neighbor_pos in game_state.tiles and neighbor_pos != from_pos:
                neighbor_tile = game_state.tiles[neighbor_pos]
                opposite_idx = (idx + 3) % 6
                if tile.pattern[idx] != neighbor_tile.pattern[opposite_idx]:
                    return False

        return True

    def pick_piece_to_pop(self,
                          game_state: GameState,
                          available_pieces: Set[Tile],
                          possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        pop_location = possible_pop_locations[randint(0, len(possible_pop_locations) - 1)]
        print(f"Player {self.player} Popping {pop_location}")
        return pop_location


class GreedyStrategy(Strategy):

    def __init__(self, player: int):
        super().__init__()
        self.player = player

    def formulate_action_impl(self,
                              game_state: GameState,
                              available_pieces: Set[Tile],
                              player_idx: int) -> TangoAction:
        """Choose the action (place or move) that maximizes score."""
        # Find the best placement
        best_place_score = -1
        best_place_tile = None
        best_place_position = None
        available_positions = list(game_state.get_available_positions())

        evaluated_moves = 0
        for tile in available_pieces:
            for position in available_positions:
                for projection in tile.unique_rotations:
                    score = game_state.score_potential_move(projection, position)
                    if score is not None and score > best_place_score:
                        best_place_score = score
                        best_place_tile = projection
                        best_place_position = position
                    evaluated_moves += 1

        diags = {
            "turn": self.turn_number,
            "moves_evaluated": evaluated_moves
        }
        self.turn_diagnostics.append(diags)

        # Find the best move (only if it beats placing)
        best_move_action = self._find_best_move(game_state, player_idx, best_place_score)

        if best_move_action is not None:
            return best_move_action

        # Return placement action
        return TangoAction(
            action_type=ActionType.PLACE,
            tile=best_place_tile,
            player=player_idx,
            destination=best_place_position
        )

    def _find_best_move(self,
                        game_state: GameState,
                        player_idx: int,
                        score_to_beat: int) -> TangoAction:
        """Find the best move action if it beats the score_to_beat. Returns None otherwise."""
        best_move = None
        best_move_score = score_to_beat

        for pos, tile in game_state.tiles.items():
            if tile.color != player_idx:
                continue

            move_range = 6 - tile.num_ticks()
            if move_range == 0:
                continue

            # Find all valid destinations for this tile
            valid_moves = self._get_valid_move_destinations(game_state, pos, tile, move_range)

            for to_pos, rotated_tile in valid_moves:
                score = self._score_move(game_state, pos, to_pos, rotated_tile)
                if score > best_move_score:
                    best_move_score = score
                    best_move = TangoAction(
                        action_type=ActionType.MOVE,
                        tile=rotated_tile,
                        player=player_idx,
                        destination=to_pos,
                        origin=pos
                    )

        return best_move

    def _get_valid_move_destinations(self, game_state: GameState, from_pos: Tuple[int, int],
                                     tile: Tile, max_distance: int) -> List[Tuple[Tuple[int, int], Tile]]:
        """Get all valid (destination, rotated_tile) pairs for a move."""
        valid_moves = []

        visited = {from_pos}
        current_frontier = {from_pos}

        for _ in range(max_distance):
            next_frontier = set()
            for pos in current_frontier:
                for neighbor in get_bordering_positions(pos):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        if neighbor not in game_state.tiles:
                            next_frontier.add(neighbor)
                            for rotation in tile.unique_rotations:
                                if self._is_valid_move_destination(game_state, neighbor, rotation, from_pos):
                                    valid_moves.append((neighbor, rotation))
            current_frontier = next_frontier

        return valid_moves

    def _is_valid_move_destination(self, game_state: GameState, position: Tuple[int, int],
                                   tile: Tile, from_pos: Tuple[int, int]) -> bool:
        """Check if a position is a valid move destination."""
        bordering = get_bordering_positions(position)
        occupied_neighbors = sum(1 for p in bordering if p in game_state.tiles and p != from_pos)
        if occupied_neighbors == 6:
            return False

        for idx, neighbor_pos in enumerate(bordering):
            if neighbor_pos in game_state.tiles and neighbor_pos != from_pos:
                neighbor_tile = game_state.tiles[neighbor_pos]
                opposite_idx = (idx + 3) % 6
                if tile.pattern[idx] != neighbor_tile.pattern[opposite_idx]:
                    return False

        return True

    def _score_move(self, game_state: GameState, from_pos: Tuple[int, int],
                    to_pos: Tuple[int, int], tile: Tile) -> int:
        """Score a potential move (simplified - just count matching colored edges)."""
        score = 0
        bordering = get_bordering_positions(to_pos)

        for idx, neighbor_pos in enumerate(bordering):
            if neighbor_pos in game_state.tiles and neighbor_pos != from_pos:
                neighbor_tile = game_state.tiles[neighbor_pos]
                if tile.pattern[idx] and tile.color == neighbor_tile.color:
                    score += 1

        return score

    def pick_piece_to_pop(self,
                          game_state: GameState,
                          available_pieces: Set[Tile],
                          possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        maximum_pop = None
        maximum_pop_score = None
        for location in possible_pop_locations:
            pop_score = game_state.score_pop(location, self.player)
            if maximum_pop is None or pop_score > maximum_pop_score:
                maximum_pop_score = pop_score
                maximum_pop = location

        return maximum_pop
