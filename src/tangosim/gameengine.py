from typing import Set, Tuple
from models import GameState, Tile
from strategy import Strategy


class SimpleTangoGame:

    def _init_gamepieces(color:int) -> Set[Tile]:
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

            [True, True, True, True, True, False]
            [True, True, True, True, True, True]
        ]
        return set([Tile(p, color) for p in possible_tile_configurations])

    def __init__(self, players:List[Strategy]):
        self.players = players
        self.player_tiles = [SimpleTangoGame._init_gamepieces(n) for n in range(0, len(players))]
        
        self.gamestate = GameState()

    def play(self) -> Tuple[GameState, int]:
        # Plays the game to the end, and returns the game state and the winning color
        round = 0
        active_player_idx = 0
        while(True):
            round += 1
            active_player_idx = round & len(self.players)

            if self.is_game_over(active_player_idx):
                break

            strategy = self.players[active_player_idx]
            available_tiles = self.player_tiles[active_player_idx]

            (tile_to_place, location) = strategy.formulate_turn(self.gamestate, available_tiles)
            surrounded_tiles = self.gamestate.place_tile(tile_to_place, location)

            self.player_tiles[active_player_idx] = set(
                [t for t in available_tiles if not t.is_rotationally_equal(tile_to_place)])

            while(len(surrounded_tiles)):
                strategy.pick
            if possible_popped_tile:
                self.player_tiles[possible_popped_tile.color].add(possible_popped_tile)

        return (self.gamestate, active_player_idx)
        
    def is_game_over(self, whose_turn:int) -> bool:
        return len(self.player_tiles[whose_turn]) == 0