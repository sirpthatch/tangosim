# Models API

The `tangosim.models` module contains the core data structures for representing game state and tiles.

## Tile

Represents a hexagonal tile in the game.

### Constructor

```python
Tile(pattern: List[bool], color: int, index: Optional[int] = None)
```

**Parameters:**
- `pattern` (List[bool]): List of 6 boolean values representing colored sides, rotating clockwise from top
- `color` (int): Player color/ID that owns this tile
- `index` (Optional[int]): Unique identifier for the tile (auto-generated if not provided)

**Example:**
```python
# Create a tile with alternating colored sides for player 0
tile = Tile([True, False, True, False, True, False], color=0)
```

### Methods

#### `num_ticks() -> int`
Returns the number of colored sides on the tile.

#### `rotate(steps: int = 1) -> Tile`
Returns a new Tile rotated by the specified number of steps (60-degree increments).

**Parameters:**
- `steps` (int): Number of 60-degree rotations clockwise (default: 1)

**Returns:** New rotated Tile instance

**Example:**
```python
rotated = tile.rotate(2)  # Rotate 120 degrees clockwise
```

#### `is_rotationally_equal(tile: Tile) -> bool`
Checks if two tiles are equivalent under rotation.

**Parameters:**
- `tile` (Tile): Tile to compare against

**Returns:** True if tiles match under any rotation, False otherwise

## GameState

Represents the current state of the game board.

### Key Methods

#### `get_available_positions() -> Set[Tuple[int, int]]`
Returns all valid positions where a tile can be placed.

**Returns:** Set of (q, r) coordinate tuples using axial coordinates

#### `place_tile(tile: Tile, position: Tuple[int, int], player: int) -> GameState`
Places a tile at the specified position and returns a new GameState.

**Parameters:**
- `tile` (Tile): The tile to place
- `position` (Tuple[int, int]): Axial coordinates (q, r) for placement
- `player` (int): Player ID placing the tile

**Returns:** New GameState after tile placement

**Raises:** Exception if placement is invalid

#### `score_potential_move(tile: Tile, position: Tuple[int, int]) -> Optional[int]`
Calculates the score that would result from placing a tile.

**Parameters:**
- `tile` (Tile): The tile to potentially place
- `position` (Tuple[int, int]): Position to evaluate

**Returns:** Score value if move is valid, None if invalid

#### `get_scores() -> List[int]`
Returns the current scores for all players.

**Returns:** List of integer scores indexed by player ID

## Utility Functions

### `get_marker_idx(position: int) -> int`
Converts a position index to a marker index.

**Parameters:**
- `position` (int): Position value (0-5)

**Returns:** Marker index (0-5)

### `get_bordering_positions(position: Tuple[int, int]) -> List[Tuple[int, int]]`
Returns all six neighboring positions for a given hex coordinate.

**Parameters:**
- `position` (Tuple[int, int]): Axial coordinates (q, r)

**Returns:** List of 6 neighboring coordinate tuples

**Example:**
```python
neighbors = get_bordering_positions((0, 0))
# Returns: [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]
```

## Coordinate System

TangoSim uses axial coordinates for hexagonal grids as defined by [Red Blob Games](https://www.redblobgames.com/grids/hexagons/#coordinates).

- Coordinates are represented as `(q, r)` tuples
- The center tile is at position `(0, 0)`
- Six neighbors surround each hex in a consistent pattern
