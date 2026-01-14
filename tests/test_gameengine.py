import pytest

from tangosim.models import GameState, Tile
from tangosim.gameengine import SimpleTangoGame, AdvancedTangoGame, TangoGame
from tangosim.strategy import GreedyStrategy, RandomStrategy


class TestSimpleTangoGame:
    """Tests for the simple (original) game mode."""

    def test_onepiece_game(self) -> None:
        player1_strategy = GreedyStrategy(0)
        player2_strategy = GreedyStrategy(1)

        player1_tiles = set([Tile([True, False, False, False, False, False], 0)])
        player2_tiles = set([Tile([True, False, False, False, False, False], 1)])

        game = SimpleTangoGame([player1_strategy, player2_strategy],
                               [player1_tiles, player2_tiles])
        (gamestate, last_player, rounds) = game.play()
        assert last_player == 0
        assert gamestate.get_scores() == [0, 0]

    def test_twopiece_game(self) -> None:
        player1_strategy = GreedyStrategy(0)
        player2_strategy = GreedyStrategy(1)

        player1_tiles = set([
            Tile([True, False, False, True, False, False], 0),
            Tile([True, False, False, False, False, False], 0)])
        player2_tiles = set([
            Tile([True, False, False, True, False, False], 1),
            Tile([True, False, False, False, False, False], 1)])
        game = SimpleTangoGame([player1_strategy, player2_strategy],
                               [player1_tiles, player2_tiles])
        (gamestate, last_player, rounds) = game.play()
        assert last_player == 0
        assert gamestate.get_scores() == [1, 1]

    def test_full_game_completes(self) -> None:
        """A full game with default tiles should complete without errors."""
        game = SimpleTangoGame([GreedyStrategy(0), GreedyStrategy(1)])
        (gamestate, last_player, rounds) = game.play()
        assert rounds > 0
        assert len(gamestate.tiles) > 0


class TestAdvancedTangoGame:
    """Tests for the advanced game mode with tile movement."""

    def test_advanced_game_completes(self) -> None:
        """An advanced game should complete without errors."""
        game = AdvancedTangoGame([GreedyStrategy(0), GreedyStrategy(1)])
        (gamestate, last_player, rounds) = game.play()
        assert rounds > 0
        assert len(gamestate.tiles) > 0

    def test_movement_range_calculation(self) -> None:
        """Tiles with fewer filled edges should have more movement range."""
        # A tile with 1 filled edge can move up to 5 spaces
        tile1 = Tile([True, False, False, False, False, False], 0)
        assert 6 - tile1.num_ticks() == 5

        # A tile with 3 filled edges can move up to 3 spaces
        tile3 = Tile([True, True, True, False, False, False], 0)
        assert 6 - tile3.num_ticks() == 3

        # A tile with all filled edges cannot move
        tile6 = Tile([True, True, True, True, True, True], 0)
        assert 6 - tile6.num_ticks() == 0

    def test_advanced_game_end_condition(self) -> None:
        """Advanced game ends when a player has no tiles AND highest score."""
        # Test that the game doesn't end just because a player has no tiles
        # Use is_game_over directly to test the condition

        game = AdvancedTangoGame([GreedyStrategy(0), GreedyStrategy(1)])

        # Place some tiles to set up a scenario
        tile1 = Tile([True, False, False, False, False, False], 0)
        tile2 = Tile([False, False, False, True, False, False], 1)
        game.gamestate.place_tile(tile1, (0, 0))
        game.gamestate.place_tile(tile2, (0, 1))

        # Player 0 has no tiles left
        game.player_tiles[0] = set()

        # Scores: Player 0 has 0 points, Player 1 has 0 points (no matching colored edges)
        scores = game.gamestate.get_scores()
        assert scores[0] == 0
        assert scores[1] == 0

        # Player 0 has no tiles but doesn't have highest score (tied)
        # Game should NOT be over for player 0
        assert game.is_game_over(0) is False

        # Give player 0 a tile and place it to create a scoring connection
        scoring_tile = Tile([False, False, False, True, False, False], 0)
        game.gamestate.place_tile(scoring_tile, (0, -1))
        # Now player 0 has one matching edge with tile1

        # Clear player 0's tiles again
        game.player_tiles[0] = set()

        # Now player 0 should have 1 point from the connection
        scores = game.gamestate.get_scores()
        assert scores[0] == 1

        # Player 0 has no tiles AND has highest score - game is over
        assert game.is_game_over(0) is True

    def test_get_valid_move_destinations_empty_for_full_tile(self) -> None:
        """A fully filled tile should have no valid move destinations."""
        game = AdvancedTangoGame([GreedyStrategy(0), GreedyStrategy(1)])

        # Place a fully filled tile
        full_tile = Tile([True, True, True, True, True, True], 0)
        game.gamestate.place_tile(full_tile, (0, 0))

        # Should have no valid destinations
        destinations = game.get_valid_move_destinations((0, 0))
        assert len(destinations) == 0


class TestTangoGameBase:
    """Tests for the base TangoGame class."""

    def test_init_gamepieces_creates_13_tiles(self) -> None:
        """Each player should start with 13 unique tiles."""
        tiles = TangoGame._init_gamepieces(0)
        assert len(tiles) == 13

    def test_init_gamepieces_all_same_color(self) -> None:
        """All tiles from _init_gamepieces should have the same color."""
        tiles = TangoGame._init_gamepieces(1)
        for tile in tiles:
            assert tile.color == 1

    def test_different_players_have_different_colors(self) -> None:
        """Different players should have tiles with different colors."""
        game = SimpleTangoGame([GreedyStrategy(0), GreedyStrategy(1)])
        for tile in game.player_tiles[0]:
            assert tile.color == 0
        for tile in game.player_tiles[1]:
            assert tile.color == 1


class TestGameStateMoveMethods:
    """Tests for the new GameState methods supporting tile movement."""

    def test_remove_tile(self) -> None:
        """remove_tile should remove a tile and update available positions."""
        gs = GameState()
        tile = Tile([True, False, False, False, False, False], 0)
        gs.place_tile(tile, (0, 0))

        assert (0, 0) in gs.tiles
        assert (0, 0) not in gs.get_available_positions()

        removed = gs.remove_tile((0, 0))
        assert removed.id == tile.id
        assert (0, 0) not in gs.tiles
        assert (0, 0) in gs.get_available_positions()

    def test_remove_tile_nonexistent_raises(self) -> None:
        """remove_tile should raise an exception for non-existent positions."""
        gs = GameState()
        with pytest.raises(Exception):
            gs.remove_tile((0, 0))

    def test_place_tile_for_move(self) -> None:
        """place_tile_for_move should place a tile and check constraints."""
        gs = GameState()

        # Place first tile normally
        tile1 = Tile([True, False, False, False, False, False], 0)
        gs.place_tile(tile1, (0, 0))

        # Place second tile using move method
        tile2 = Tile([False, False, False, True, False, False], 0)
        surrounded = gs.place_tile_for_move(tile2, (0, -1))

        assert (0, -1) in gs.tiles
        assert len(surrounded) == 0

    def test_place_tile_for_move_conflict_raises(self) -> None:
        """place_tile_for_move should raise on edge conflicts."""
        gs = GameState()

        # Place first tile
        tile1 = Tile([True, False, False, False, False, False], 0)
        gs.place_tile(tile1, (0, 0))

        # Try to place conflicting tile
        tile2 = Tile([True, True, True, True, True, True], 0)  # All edges filled
        # This should conflict with tile1's top edge (index 0)
        # tile2's bottom edge (index 3) would need to match tile1's top (index 0)
        # tile1 has True at index 0, tile2 has True at index 3, so this should work
        # Let's create an actual conflict
        tile_conflict = Tile([False, False, False, False, False, False], 0)  # All blank
        with pytest.raises(Exception):
            gs.place_tile_for_move(tile_conflict, (0, -1))


# Keep old test functions for backwards compatibility
def test_onepiece_game() -> None:
    player1_strategy = GreedyStrategy(0)
    player2_strategy = GreedyStrategy(1)

    player1_tiles = set([Tile([True, False, False, False, False, False], 0)])
    player2_tiles = set([Tile([True, False, False, False, False, False], 1)])

    game = SimpleTangoGame([player1_strategy, player2_strategy],
                           [player1_tiles, player2_tiles])
    (gamestate, last_player, rounds) = game.play()
    assert last_player == 0
    assert gamestate.get_scores() == [0, 0]


def test_twopiece_game() -> None:
    player1_strategy = GreedyStrategy(0)
    player2_strategy = GreedyStrategy(1)

    player1_tiles = set([
        Tile([True, False, False, True, False, False], 0),
        Tile([True, False, False, False, False, False], 0)])
    player2_tiles = set([
        Tile([True, False, False, True, False, False], 1),
        Tile([True, False, False, False, False, False], 1)])
    game = SimpleTangoGame([player1_strategy, player2_strategy],
                           [player1_tiles, player2_tiles])
    (gamestate, last_player, rounds) = game.play()
    assert last_player == 0
    assert gamestate.get_scores() == [1, 1]
