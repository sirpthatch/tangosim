from typing import List, Tuple, Dict, Set
import itertools

## Some Notes:
## * Tile positions are using an axial coordinate system, defined here: https://www.redblobgames.com/grids/hexagons/#coordinates

def get_marker_idx(position: int) -> int:
    return (position + 3) % 6
    
class Tile:
    inc_id = itertools.count()
    def __init__(self, 
                 pattern: List[bool], # 6 sides rotating clockwise from top, true if colored
                 color:int,
                 index = None) -> None:
        assert len(pattern) == 6

        self.id = index if index else next(Tile.inc_id)
        self.pattern = pattern
        self.color = color

    def num_ticks(self) -> int:
        count = 0
        for x in self.pattern:
            if x: count+=1
        return count
    
    def rotate(self, steps=1):
        return Tile(self.pattern[-steps:]+self.pattern[:-steps], self.color, self.id)
    
    def is_rotationally_equal(self, tile:'Tile') -> bool:
        if tile.color != self.color:
            return False
        
        for n in range(0,6):
            rotated_pattern = self.pattern[-n:]+self.pattern[:-n]
            if rotated_pattern == tile.pattern:
                return True
        
        return False

def get_bordering_positions(position:Tuple[int, int]) -> List[Tuple[int, int]]:
        return [
            (position[0], position[1]-1),
            (position[0]+1, position[1]-1),
            (position[0]+1, position[1]),
            (position[0], position[1]+1),
            (position[0]-1, position[1]+1),
            (position[0]-1, position[1]),
        ]
        
        #return [
        #            (position[0], position[1]+2),
        #            (position[0]+1, position[1]+1),
        #            (position[0]+1, position[1]-1),
        #            (position[0], position[1]-2),
        #            (position[0]-1, position[1]-1),
        #            (position[0]-1, position[1]+1),
        #        ]
class GameState:

    def __init__(self, num_players=2):
        self.num_players = num_players
        self.available_positions = set()
        self.available_positions.add((0,0))
        self.tiles = dict()

    def find_conflicting_tile_position(self, tile:Tile, position:Tuple[int, int]) -> Tuple[int, Tile]:
        # Returns tuple of (edge index, conflicting tile) if there is a conflict, None otherwise
        bordering_positions = get_bordering_positions(position)
        
        bordering_occupied_positions_mask = [
            (1 if p in self.tiles else 0 ) for p in bordering_positions
        ]

        for idx in range(0,6):
            if not bordering_occupied_positions_mask[idx]:
                continue

            border_position = bordering_positions[idx]
            border_tile = self.tiles[border_position]
            if tile.pattern[idx] != border_tile.pattern[get_marker_idx(idx)]:
                return idx, border_tile
        
        return None
 
    def place_tile(self, tile:Tile, position:Tuple[int, int]) -> List[Tuple[int, int]]:
        # Places the tile and returns list of positions that are surrounded
        # Check if spot is free and connected
        if position not in self.available_positions:
            raise Exception(f"Position {position} not in available positions: {self.available_positions}")

        if position in self.tiles:
            raise Exception(f"Tile already placed at {position}")

        # Check if bordering tiles satisfy tile marker constraint
        bordering_positions = get_bordering_positions(position)
        
        possible_conflict = self.find_conflicting_tile_position(tile, position)
        if possible_conflict != None:
            (idx, conflicting_tile) = possible_conflict
            raise Exception(f"Tile markers do not line up: {tile.pattern} and {conflicting_tile.pattern} @ border {idx}")

        if all([p in self.tiles for p in bordering_positions]):
            raise Exception("Cannot place tile there, it would be surrounded")

        self.tiles[position] = tile
        
        # calculate changes to available positions
        self.available_positions.remove(position)

        available_bordering_positions = \
            [p for p in bordering_positions if p not in self.tiles and not(all(q in self.tiles for q in get_bordering_positions(p)))]

        self.available_positions.update(available_bordering_positions)
        enclosed_positions = [x for x in self.available_positions if self.is_surrounded(x)]
        list(map(self.available_positions.remove, enclosed_positions))

        # Check for popping condition
        surrounded_positions = []
        for adj_position in bordering_positions:
            if adj_position in self.tiles:
                if self.is_surrounded(adj_position):
                    surrounded_positions.append(adj_position)

        return surrounded_positions    

    def is_surrounded(self, position:Tuple[int, int]) -> bool:
        bordering_positions = get_bordering_positions(position)
        return all([p in self.tiles for p in bordering_positions])

    def pop_piece(self, position:Tuple[int, int]) -> Tile:
        if position not in self.tiles:
            raise Exception(f"Attempting to pop a location that has no tile:{position}")
        
        return self.tiles.pop(position)

    def get_available_positions(self) -> Set[Tuple[int, int]]:
        return self.available_positions
    
    def get_tiles(self) -> Dict[Tuple[int, int], Tile]:
        return self.tiles
    
    def get_scores(self) -> List[int]:
        scored_pairs = set()
        scores = [0]*self.num_players
        for position, tile in self.tiles.items():
            bordering_positions = get_bordering_positions(position)
            for rot_idx in range(0, len(bordering_positions)):
                if bordering_positions[rot_idx] in self.tiles:
                    paired_tile = self.tiles[bordering_positions[rot_idx]]
                    if tile.pattern[rot_idx] and tile.color == paired_tile.color:
                        scoring_pair = tuple(sorted([tile.id, paired_tile.id]))
                        if scoring_pair not in scored_pairs:
                            scores[tile.color] += 1
                            scored_pairs.add(scoring_pair)
        return scores

    def score_potential_move(self, tile:Tile, position:Tuple[int, int]) -> int:
        if position not in self.available_positions:
            return None
        
        score = 0
        bordering_positions = get_bordering_positions(position)
        for rot_idx in range(0, len(bordering_positions)):
            if bordering_positions[rot_idx] in self.tiles:
                paired_tile = self.tiles[bordering_positions[rot_idx]]
                if tile.pattern[rot_idx] != paired_tile.pattern[get_marker_idx(rot_idx)]:
                    return None
                
                if tile.pattern[rot_idx] and tile.color == paired_tile.color:
                    score += 1
        
        pops = self.check_and_score_pops(tile, position)
        if len(pops):
            max_pop_score = max([y for (_,y) in pops])
            score += max_pop_score
        return score
    
    def check_and_score_pops(self, tile:Tile, position:Tuple[int, int]) -> List[Tuple[Tuple[int, int], int]]:
        """Returns a list of (location, score) for pops that could happen if placing 
           tile at position
        """
        bordering_positions = get_bordering_positions(position)
        pops = list()
        for adj_position in bordering_positions:
            adj_bordering_positions = get_bordering_positions(adj_position)
            adj_bordering_positions.append(position)
            is_popped = all([p in self.tiles for p in adj_bordering_positions])
            if is_popped:
                score = self.score_pop(adj_position, tile.color)
                pops.append((adj_position, score))
        return pops
    
    def score_pop(self, position:Tuple[int, int], color:int) -> int:
        """Returns the score for player 'color' for popping position 'position'"""
        popped_tile = self.tiles[position]
        bordering_positions = get_bordering_positions(position)
        score = 0
        for rot_idx in range(0, len(bordering_positions)):
            border_tile = self.tiles[bordering_positions[rot_idx]]
            if popped_tile.pattern[rot_idx] and popped_tile.color == border_tile.color:
                if border_tile.color == color:
                    score -= 1
                else:
                    score += 1
        return score