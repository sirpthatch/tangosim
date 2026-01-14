from tangosim.models import Tile, GameState
from typing import Set, Tuple, List
from random import randint

class Strategy:

    def __init__(self):
        self.turn_number = 0
        self.turn_diagnostics = []

    def formulate_turn(self, 
                  game_state:GameState, 
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        self.turn_number += 1
        return self.formulate_turn_impl(game_state, available_pieces)
    
    def formulate_turn_impl(self, 
                  game_state:GameState, 
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Returns a tuple of (tile to place, (q,r) location)
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

    def formulate_turn_impl(self,
                  game_state:GameState,
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Returns a tuple of (tile to place, (q,r) location)
        viable_moves = list()
        available_positions = list(game_state.get_available_positions())

        for tile in available_pieces:
            for position in available_positions:
                for projection in tile.unique_rotations:
                    score = game_state.score_potential_move(projection, position)
                    if score != None:
                        viable_moves.append((projection, position))

        (piece, position) = viable_moves[randint(0, len(viable_moves)-1)]
        diags = {
            "turn": self.turn_number,
            "moves_evaluated" : len(viable_moves)
        }
        self.turn_diagnostics.append(diags) 
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
        
    def formulate_turn_impl(self,
                  game_state:GameState,
                  available_pieces:Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Returns a tuple of (tile to place, (q,r) location)
        maximum_move_score = 0
        maximum_move_piece = None
        maximum_move_position = None
        available_positions = list(game_state.get_available_positions())

        evaluated_moves = 0
        for tile in available_pieces:
            for position in available_positions:
                for projection in tile.unique_rotations:
                    score = game_state.score_potential_move(projection, position)
                    if score != None and score >= maximum_move_score:
                        maximum_move_score = score
                        maximum_move_piece = projection
                        maximum_move_position = position
                    evaluated_moves += 1
        
        diags = {
            "turn": self.turn_number,
            "moves_evaluated" :evaluated_moves
        }
        self.turn_diagnostics.append(diags) 
        #print(f"Player {self.player} Move {maximum_move_piece.pattern} to {maximum_move_position} for {maximum_move_score} points")
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
                        
        #print(f"Player {self.player} Popping {maximum_pop} for {maximum_pop_score} points")
        return maximum_pop
