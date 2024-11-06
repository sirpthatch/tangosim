from typing import Set, Tuple, List
from tangosim.models import GameState, Tile
from tangosim.strategy import Strategy


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

            [True, True, True, True, True, False],
            [True, True, True, True, True, True]
        ]
        return set([Tile(p, color) for p in possible_tile_configurations])

    def __init__(self, players:List[Strategy], player_tiles:List[Set[Tile]] = None):
        self.players = players
        self.player_tiles = player_tiles if player_tiles else [SimpleTangoGame._init_gamepieces(n) for n in range(0, len(players))]
        
        self.gamestate = GameState()

    def play(self) -> Tuple[GameState, int]:
        # Plays the game to the end, and returns the game state and the winning color
        round = -1
        active_player_idx = 0
        while(True):
            round += 1
            active_player_idx = round % len(self.players)

            if self.is_game_over(active_player_idx):
                break

            strategy = self.players[active_player_idx]
            available_tiles = self.player_tiles[active_player_idx]

            (tile_to_place, location) = strategy.formulate_turn(self.gamestate, available_tiles)
            surrounded_tiles = self.gamestate.place_tile(tile_to_place, location)

            self.player_tiles[active_player_idx] = set(
                [t for t in available_tiles if not t.is_rotationally_equal(tile_to_place)])

            while(len(surrounded_tiles)):
                print(f"Surrounded Tiles: {surrounded_tiles}")
                location_to_pop = strategy.pick_piece_to_pop(self.gamestate, 
                                                             self.player_tiles[active_player_idx], 
                                                             surrounded_tiles)
                print(f"Chose location: {location_to_pop}")
                popped_tile = self.gamestate.pop_piece(location_to_pop)
                surrounded_tiles.remove(location_to_pop)
                self.player_tiles[popped_tile.color].add(popped_tile)

                surrounded_tiles = [t for t in surrounded_tiles if self.gamestate.is_surrounded(t)]
                
        return (self.gamestate, active_player_idx)
        
    def is_game_over(self, whose_turn:int) -> bool:
        return len(self.player_tiles[whose_turn]) == 0