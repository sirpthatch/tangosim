# Hexagonal Coordinate System

TangoSim uses an axial coordinate system for representing hexagonal grids, based on the system described by [Red Blob Games](https://www.redblobgames.com/grids/hexagons/#coordinates).

## Axial Coordinates

Each hexagonal tile position is represented by two coordinates: `(q, r)`.

```
      (-1,-1) (0,-1) (1,-1)
         \     |     /
    (-1,0)-(0,0)-(1,0)
         /     |     \
      (-1,1) (0,1) (1,1)
```

### Properties

- **Origin**: The center of the board is at `(0, 0)`
- **Q-axis**: Increases moving right
- **R-axis**: Increases moving down-right
- **Neighbors**: Each hex has exactly 6 neighbors

## Neighbor Positions

The six neighbors of any position `(q, r)` are always:

```python
def get_bordering_positions(position):
    q, r = position
    return [
        (q, r-1),      # Top
        (q+1, r-1),    # Top-right
        (q+1, r),      # Bottom-right
        (q, r+1),      # Bottom
        (q-1, r+1),    # Bottom-left
        (q-1, r),      # Top-left
    ]
```

## Visual Reference

```
            (0,-2)
           /      \
      (-1,-1)    (1,-2)
         /  \    /  \
    (-2,0) (0,-1) (1,-1)
       / \  /  \  /  \
  (-2,1)(-1,0)(0,0)(1,0)
     / \  /  \  /  \  /
(-2,2)(-1,1)(0,1)(1,1)
   / \  /  \  /  \  /
(-2,3)(-1,2)(0,2)(1,2)
```

## Advantages of Axial Coordinates

1. **Simple Arithmetic**: Easy to calculate neighbors
2. **No Redundancy**: Each position has one unique representation
3. **Efficient Storage**: Only 2 values needed per position
4. **Distance Calculation**: Straightforward distance formulas

## Distance Between Hexes

The distance between two hex positions can be calculated as:

```python
def hex_distance(a, b):
    """Calculate the distance between two hex positions."""
    aq, ar = a
    bq, br = b
    return (abs(aq - bq) + abs(aq + ar - bq - br) + abs(ar - br)) // 2
```

## Rotation Around Origin

To rotate a position around the origin by 60 degrees clockwise:

```python
def rotate_clockwise(position):
    """Rotate position 60 degrees clockwise around origin."""
    q, r = position
    return (-r, q + r)
```

Multiple rotations:
```python
def rotate_n_times(position, n):
    """Rotate position n*60 degrees clockwise around origin."""
    q, r = position
    for _ in range(n % 6):
        q, r = -r, q + r
    return (q, r)
```

## Common Patterns

### Ring Around Position

Get all positions at distance `n` from a center:

```python
def get_ring(center, radius):
    """Get all positions at exactly radius distance from center."""
    if radius == 0:
        return [center]

    results = []
    q, r = center
    # Start at the "top" position
    q, r = q, r - radius

    # Walk around the ring
    for direction in range(6):
        for step in range(radius):
            results.append((q, r))
            # Move in current direction
            dq, dr = DIRECTIONS[direction]
            q, r = q + dq, r + dr

    return results
```

### Spiral Pattern

Visit hexes in a spiral pattern outward from center:

```python
def spiral_from_center(center, max_radius):
    """Generate positions in spiral order from center."""
    yield center
    for radius in range(1, max_radius + 1):
        for pos in get_ring(center, radius):
            yield pos
```

## Tile Sides and Positions

Tiles have 6 sides, indexed 0-5, rotating clockwise from the top:

```
       0
    5     1
    4     2
       3
```

When a tile is placed at position `(q, r)`:
- Side 0 faces toward position `(q, r-1)`
- Side 1 faces toward position `(q+1, r-1)`
- Side 2 faces toward position `(q+1, r)`
- Side 3 faces toward position `(q, r+1)`
- Side 4 faces toward position `(q-1, r+1)`
- Side 5 faces toward position `(q-1, r)`

## Coordinate Conversion

### To Cube Coordinates

Axial `(q, r)` can be converted to cube `(x, y, z)` where `x + y + z = 0`:

```python
def axial_to_cube(q, r):
    x = q
    z = r
    y = -x - z
    return (x, y, z)
```

### From Cube Coordinates

```python
def cube_to_axial(x, y, z):
    q = x
    r = z
    return (q, r)
```

## Working with Coordinates in TangoSim

```python
from tangosim.models import get_bordering_positions, GameState

# Get neighbors of a position
position = (1, 2)
neighbors = get_bordering_positions(position)
print(f"Neighbors of {position}: {neighbors}")

# In a game, check available positions
state = GameState()
available = state.get_available_positions()
print(f"Can place tiles at: {available}")
```

## Further Reading

- [Red Blob Games: Hexagonal Grids](https://www.redblobgames.com/grids/hexagons/)
- [Coordinate Systems Comparison](https://www.redblobgames.com/grids/hexagons/#coordinates)
- [Algorithms on Hex Grids](https://www.redblobgames.com/grids/hexagons/#algorithms)
