from typing import List, Tuple, Dict, Set

def get_marker_idx(position: int) -> int:
    return (position + 3) % 6

class Tile:

    def __init__(self, 
                 pattern: List[bool], 
                 color:int) -> None:
        self.pattern = pattern
        self.color = color

    def num_ticks(self) -> int:
        count = 0
        for x in self.pattern:
            if x: count+=1
        return count
    
    def rotate(self, steps=1):
        return Tile(self.pattern[-steps:]+self.pattern[:-steps], self.color)
    
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
                    (position[0], position[1]+2),
                    (position[0]+1, position[1]+1),
                    (position[0]+1, position[1]-1),
                    (position[0], position[1]-2),
                    (position[0]-1, position[1]-1),
                    (position[0]-1, position[1]+1),
                ]
class GameState:

    def __init__(self):
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
            [p for p in bordering_positions if p not in self.tiles]

        # Check for popping condition
        surrounded_positions = []
        for adj_position in bordering_positions:
            if adj_position in self.tiles:
                if self.is_surrounded(adj_position):
                    surrounded_positions.append(adj_position)

        self.available_positions.update(available_bordering_positions)
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