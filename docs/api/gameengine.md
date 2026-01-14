# Game Engine API

The `tangosim.gameengine` module provides the main game loop and rule enforcement.

## SimpleTangoGame

Main game controller that manages game flow, player turns, and rule enforcement.

### Constructor

```python
SimpleTangoGame(strategies: List[Strategy])
```

**Parameters:**
- `strategies` (List[Strategy]): List of Strategy instances, one per player

**Example:**
```python
from tangosim.gameengine import SimpleTangoGame
from tangosim.strategy import RandomStrategy, GreedyStrategy

player1 = RandomStrategy(0)
player2 = GreedyStrategy(1)
game = SimpleTangoGame([player1, player2])
```

### Methods

#### `play() -> Tuple[GameState, int]`

Runs the complete game from start to finish.

**Returns:** Tuple of (final_game_state, last_player_id)

**Example:**
```python
final_state, last_player = game.play()
scores = final_state.get_scores()
print(f"Player {last_player} made the last move")
print(f"Final scores: {scores}")
```

### Game Flow

The game engine handles:

1. **Initialization**: Sets up the initial game state
2. **Turn Management**: Alternates between players
3. **Move Validation**: Ensures all moves follow game rules
4. **Tile Placement**: Applies valid moves to the board
5. **Pop Mechanics**: Handles tile popping when triggered
6. **Enclosure Detection**: Identifies enclosed board regions
7. **Scoring**: Tracks and updates player scores
8. **Game End**: Detects when no more moves are possible

### Rule Enforcement

The game engine automatically enforces:

- Valid tile placement positions
- Proper tile adjacency rules
- Border tile constraints (no placement in the center)
- Pop mechanics when required
- Turn order

### Diagnostics

The game engine can be extended to collect diagnostics:

- Number of turns played
- Average moves evaluated per turn
- First-player advantage statistics
- Time per move

## Game Lifecycle

```
┌─────────────────┐
│  Initialize     │
│  Game State     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Player Turn    │<─────┐
│  - Get Strategy │      │
│  - Formulate    │      │
│  - Validate     │      │
│  - Apply Move   │      │
└────────┬────────┘      │
         │               │
         v               │
┌─────────────────┐      │
│  Check Pops     │      │
│  - Detect       │      │
│  - Apply        │      │
└────────┬────────┘      │
         │               │
         v               │
┌─────────────────┐      │
│  Update Scores  │      │
└────────┬────────┘      │
         │               │
         v               │
    More Moves? ─────────┘
         │ No
         v
┌─────────────────┐
│  Game Complete  │
│  Return Results │
└─────────────────┘
```

## Error Handling

The game engine raises exceptions for:

- Invalid tile placement attempts
- Strategy errors (returned invalid moves)
- Malformed game state

## Performance Considerations

- Game state is immutable (new state created each turn)
- Strategies should cache expensive computations
- Large simulations may benefit from parallel processing

## Extending the Game Engine

To create custom game variants:

1. Subclass `SimpleTangoGame`
2. Override specific game mechanics
3. Maintain core rule enforcement

Example:
```python
from tangosim.gameengine import SimpleTangoGame
from tangosim.models import GameState

class TimedTangoGame(SimpleTangoGame):
    def __init__(self, strategies, time_limit=60):
        super().__init__(strategies)
        self.time_limit = time_limit

    def play(self):
        # Add timing logic
        import time
        start = time.time()
        result = super().play()
        elapsed = time.time() - start
        print(f"Game completed in {elapsed:.2f} seconds")
        return result
```
