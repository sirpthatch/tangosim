from tangosim.models import Tile, GameState
from typing import Set, Tuple, List
from random import randint

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

class RandomStrategy(Strategy):

    def __init__(self, player:int):
        super().__init__()
        self.player = player

    def formulate_turn(self, 
                  game_state:GameState, 
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Returns a tuple of (tile to place, (x,y) location)
        viable_moves = list()

        for tile in available_pieces:
            rotational_projections = [tile.rotate(n) for n in range(0, 6)]
            for position in game_state.available_positions:
                for projection in rotational_projections:
                    score = game_state.score_potential_move(projection, position)
                    if score != None:
                        viable_moves.append((projection, position))
                        
        (piece, position) = viable_moves[randint(0, len(viable_moves)-1)] 
        print(f"Player {self.player} Move {piece.pattern} to {position}")
        return (piece, position)
        
    
    def pick_piece_to_pop(self,
                          game_state:GameState,
                          available_pieces:Set[Tile],
                          possible_pop_locations:List[Tuple[int, int]]) -> Tuple[int, int]:
        pop_location = possible_pop_locations[randint(0, len(possible_pop_locations)-1)]
        print(f"Player {self.player} Popping {pop_location}")
        return pop_location

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
        maximum_pop = None
        maximum_pop_score = None
        for location in possible_pop_locations:
            pop_score = game_state.score_pop(location, self.player)
            if maximum_pop == None or pop_score > maximum_pop_score:
                    maximum_pop_score = pop_score
                    maximum_pop = location
                        
        print(f"Player {self.player} Popping {maximum_pop} for {maximum_pop_score} points")
        return maximum_pop
