# Strategy API

The `tangosim.strategy` module provides interfaces and implementations for AI player strategies.

## Strategy (Base Class)

Abstract base class for all game strategies.

### Constructor

```python
Strategy()
```

Initializes strategy with turn tracking.

### Attributes

- `turn_number` (int): Current turn number for this strategy
- `turn_diagnostics` (List): Diagnostic data collected during gameplay

### Methods

#### `formulate_turn(game_state: GameState, available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]`

Main method called by the game engine to get the next move.

**Parameters:**
- `game_state` (GameState): Current state of the game
- `available_pieces` (Set[Tile]): Tiles available to place

**Returns:** Tuple of (tile_to_place, (q, r) position)

**Note:** This method increments `turn_number` automatically. Override `formulate_turn_impl()` instead.

#### `formulate_turn_impl(game_state: GameState, available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]`

Implementation method to be overridden by subclasses.

**Parameters:**
- `game_state` (GameState): Current state of the game
- `available_pieces` (Set[Tile]): Tiles available to place

**Returns:** Tuple of (tile_to_place, position)

**Must Override:** Subclasses must implement this method

#### `pick_piece_to_pop(game_state: GameState, available_pieces: Set[Tile], possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]`

Called when the player must choose a tile to pop from the board.

**Parameters:**
- `game_state` (GameState): Current state of the game
- `available_pieces` (Set[Tile]): Tiles available to the player
- `possible_pop_locations` (List[Tuple[int, int]]): Valid positions to pop

**Returns:** Coordinate tuple of the position to pop

**Must Override:** Subclasses must implement this method

## RandomStrategy

Strategy that makes random valid moves.

### Constructor

```python
RandomStrategy(player: int)
```

**Parameters:**
- `player` (int): Player ID this strategy is playing for

### Example

```python
from tangosim.strategy import RandomStrategy

strategy = RandomStrategy(player=0)
```

## GreedyStrategy

Strategy that maximizes immediate scoring opportunities, including pop maximization.

### Constructor

```python
GreedyStrategy(player: int)
```

**Parameters:**
- `player` (int): Player ID this strategy is playing for

### Behavior

- Evaluates all possible moves (tiles × positions × rotations)
- Scores each potential move
- Incorporates pop scoring and maximization
- Selects the move with the highest immediate score
- Breaks ties randomly

### Example

```python
from tangosim.strategy import GreedyStrategy

strategy = GreedyStrategy(player=1)
```

## Creating Custom Strategies

To create a custom strategy:

1. Subclass `Strategy`
2. Implement `formulate_turn_impl()`
3. Implement `pick_piece_to_pop()`
4. Optionally use `turn_diagnostics` for debugging

### Example: Defensive Strategy

```python
from tangosim.strategy import Strategy
from tangosim.models import Tile, GameState
from typing import Set, Tuple, List

class DefensiveStrategy(Strategy):
    def __init__(self, player: int):
        super().__init__()
        self.player = player

    def formulate_turn_impl(self,
                           game_state: GameState,
                           available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Evaluate moves that minimize opponent scoring
        best_move = None
        min_opponent_advantage = float('inf')

        for tile in available_pieces:
            for rotation in range(6):
                rotated = tile.rotate(rotation)
                for position in game_state.get_available_positions():
                    score = game_state.score_potential_move(rotated, position)
                    if score is not None:
                        # Calculate opponent advantage after this move
                        advantage = self._calculate_opponent_advantage(
                            game_state, rotated, position
                        )
                        if advantage < min_opponent_advantage:
                            min_opponent_advantage = advantage
                            best_move = (rotated, position)

        return best_move

    def pick_piece_to_pop(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        # Choose pop that minimizes opponent scoring potential
        return possible_pop_locations[0]  # Simplified

    def _calculate_opponent_advantage(self,
                                     game_state: GameState,
                                     tile: Tile,
                                     position: Tuple[int, int]) -> float:
        # Your logic here
        return 0.0
```

## Strategy Best Practices

1. **Performance**: Cache expensive computations
2. **Diagnostics**: Use `turn_diagnostics` to track decision-making
3. **Testing**: Write unit tests for strategy behavior
4. **Documentation**: Document your strategy's approach and trade-offs
