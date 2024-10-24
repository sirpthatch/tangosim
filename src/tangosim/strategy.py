from models import Tile, GameState
from typing import Set, Tuple

class Strategy:

    def formulate_turn(self, 
                  game_state:GameState, 
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Returns a tuple of (tile to place, (x,y) location)
        raise NotImplemented()
    
    def pick_piece_to_pop(self,
                          game_state:GameState,
                          available_pieces:Set[Tile],
                          possible_pop_locations:List[Tuple[int, int]]) -> Tuple[int, int]:
        # Returns the location to pop
        raise NotImplemented()
