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
        
class GameState:

    def __init__(self, num_players=2):
        self.num_players = num_players
        self._available_positions = set()
        self._available_positions.add((0,0))
        self.tiles = dict()
        self._min_coordinates = (0,0)
        self._max_coordinates = (0,0)

    def print_state(self) -> None:
        print(f"Available Positions: {len(self._available_positions)} - {self._available_positions}")
        print(f"Filtered Available Positions: {len(self.get_available_positions())} - {self.get_available_positions()}")
        print(f"Max Coordinates: {self._max_coordinates}")
        print(f"Min Coordinates: {self._min_coordinates}")

    def is_enclosed(self, position:Tuple[int, int], positions_checked=set()) -> bool:
        if position in self.tiles:
            raise Exception("Checking if occupied tile is enclosed")

        # Do a recursive check on positions, with base case being 
        # that the position is outside of the maximimum envelope of the 
        # board

        if position[0] < self._min_coordinates[0] or \
            position[1] < self._min_coordinates[1] or \
                position[0] > self._max_coordinates[0] or \
                    position[1] > self._max_coordinates[1]:
                    return False

        new_empty_bordering_positions = [x for x in get_bordering_positions(position) \
            if x not in self.tiles and x not in positions_checked]
            
        if len(new_empty_bordering_positions) == 0:
            return True
            
        new_positions = positions_checked.copy()
        new_positions.add(position)

        for new_position in new_empty_bordering_positions:
            new_positions = positions_checked.copy()
            new_positions.add(position)
            if not self.is_enclosed(new_position,positions_checked=new_positions):
                return False
            
        return True
    
        #return all(map(lambda x: self.is_enclosed(x,positions_checked=new_positions), \
        #    new_empty_bordering_positions))

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
 
    def get_available_positions(self) -> List[Tuple[int, int]]:
        return [x for x in self._available_positions if not self.is_enclosed(x)]
    
    def place_tile(self, tile:Tile, position:Tuple[int, int]) -> List[Tuple[int, int]]:
        # Places the tile and returns list of positions that are surrounded
        # Check if spot is free and connected
        if position not in self._available_positions:
            raise Exception(f"Position {position} not in available positions: {self._available_positions}")

        if position in self.tiles:
            raise Exception(f"Tile already placed at {position}")
        
        if self.is_enclosed(position):
            print(f"Failing for {position}")
            self.print_state()
            raise Exception(f"Position {position} would be inside an enclosed area")

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
        self._available_positions.remove(position)

        #available_bordering_positions = \
        #    [p for p in bordering_positions if p not in self.tiles and not(all(q in self.tiles for q in get_bordering_positions(p)))]

        # Maybe this is right, and then we do not need the check below
        available_bordering_positions = \
            [p for p in bordering_positions if p not in self.tiles]# and not self.is_enclosed(p)]


        self._available_positions.update(available_bordering_positions)
        positions_to_remove = list()
        for x in self._available_positions:
            if self.is_surrounded(x) or self.is_enclosed(x):
                positions_to_remove.append(x)
                
        for x in positions_to_remove:
            self._available_positions.remove(x)
        
        # Check for popping condition
        surrounded_positions = []
        for adj_position in bordering_positions:
            if adj_position in self.tiles:
                if self.is_surrounded(adj_position):
                    surrounded_positions.append(adj_position)

        self._adjust_max_bounds(position)
        return surrounded_positions    

    def _adjust_max_bounds(self, position:Tuple[int, int]) -> None:
        if position[0] < self._min_coordinates[0]:
            self._min_coordinates = (position[0]-1, self._min_coordinates[1])
        if position[1] < self._min_coordinates[1]:
            self._min_coordinates = (self._min_coordinates[0], position[1]-1)

        if position[0] > self._max_coordinates[0]:
            self._max_coordinates = (position[0]+1, self._max_coordinates[1])
        if position[1] > self._max_coordinates[1]:
            self._max_coordinates = (self._max_coordinates[0], position[1]+1)

    def is_surrounded(self, position:Tuple[int, int]) -> bool:
        bordering_positions = get_bordering_positions(position)
        return all([p in self.tiles for p in bordering_positions])

    def pop_piece(self, position:Tuple[int, int]) -> Tile:
        if position not in self.tiles:
            raise Exception(f"Attempting to pop a location that has no tile:{position}")
        
        return self.tiles.pop(position)

    def get_available_positions(self) -> Set[Tuple[int, int]]:
        return self._available_positions
    
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
        if position not in self._available_positions:
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