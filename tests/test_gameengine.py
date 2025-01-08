import pytest

from tangosim.models import GameState, Tile
from tangosim.gameengine import SimpleTangoGame
from tangosim.strategy import GreedyStrategy

def test_onepiece_game() -> None:
    player1_strategy = GreedyStrategy(0)
    player2_strategy = GreedyStrategy(1)

    player1_tiles = set([Tile([True, False, False, False, False, False], 0)])
    player2_tiles = set([Tile([True, False, False, False, False, False], 1)])

    game = SimpleTangoGame([player1_strategy, player2_strategy],
                           [player1_tiles, player2_tiles])
    (gamestate, last_player, rounds) = game.play()
    assert last_player == 0
    assert gamestate.get_scores() == [0,0]


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
    assert gamestate.get_scores() == [1,1]