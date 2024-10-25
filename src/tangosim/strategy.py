from tangosim.models import Tile, GameState
from typing import Set, Tuple, List

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

class GreedyStrategy(Strategy):

    def __init__(self, player:int):
        super().__init__()
        self.player = player

    def formulate_turn(self, 
                  game_state:GameState, 
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Returns a tuple of (tile to place, (x,y) location)
        maximum_move_score = 0
        maximum_move_piece = None
        maximum_move_position = None

        for tile in available_pieces:
            rotational_projections = [tile.rotate(n) for n in range(0, 6)]
            for position in game_state.available_positions:
                for projection in rotational_projections:
                    score = game_state.score_potential_move(projection, position)
                    if score != None and score >= maximum_move_score:
                        maximum_move_score = score
                        maximum_move_piece = projection
                        maximum_move_position = position
        
        print(f"Player {self.player} Move {maximum_move_piece.pattern} to {maximum_move_position} for {maximum_move_score} points")
        return (maximum_move_piece, maximum_move_position)
        
    
    def pick_piece_to_pop(self,
                          game_state:GameState,
                          available_pieces:Set[Tile],
                          possible_pop_locations:List[Tuple[int, int]]) -> Tuple[int, int]:
        print(f"Player {self.player} Popping {possible_pop_locations[0]}")
        return possible_pop_locations[0]
