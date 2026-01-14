# Creating Custom Strategies

This guide shows you how to create custom AI strategies for TangoSim.

## Strategy Interface

All strategies must inherit from the `Strategy` base class and implement two methods:

```python
from tangosim.strategy import Strategy
from tangosim.models import Tile, GameState
from typing import Set, Tuple, List

class MyStrategy(Strategy):
    def formulate_turn_impl(self,
                           game_state: GameState,
                           available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        """Choose a tile and position for this turn."""
        # Your implementation here
        pass

    def pick_piece_to_pop(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Choose which piece to pop when required."""
        # Your implementation here
        pass
```

## Example 1: First-Valid-Move Strategy

The simplest strategy - just pick the first valid move:

```python
from tangosim.strategy import Strategy
from tangosim.models import Tile, GameState
from typing import Set, Tuple, List

class FirstMoveStrategy(Strategy):
    def __init__(self, player: int):
        super().__init__()
        self.player = player

    def formulate_turn_impl(self,
                           game_state: GameState,
                           available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        # Try each tile in each position
        for tile in available_pieces:
            for position in game_state.get_available_positions():
                # Try the tile without rotation
                if game_state.score_potential_move(tile, position) is not None:
                    return (tile, position)

        # Should never reach here in a valid game
        raise Exception("No valid moves found")

    def pick_piece_to_pop(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        # Just pick the first available
        return possible_pop_locations[0]
```

## Example 2: Edge-Preferring Strategy

Prefer moves near the edges:

```python
from tangosim.strategy import Strategy
from tangosim.models import Tile, GameState
from typing import Set, Tuple, List
import random

class EdgeStrategy(Strategy):
    def __init__(self, player: int):
        super().__init__()
        self.player = player

    def _distance_from_center(self, position: Tuple[int, int]) -> float:
        """Calculate Euclidean distance from origin."""
        q, r = position
        return (q*q + r*r + q*r) ** 0.5

    def formulate_turn_impl(self,
                           game_state: GameState,
                           available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        valid_moves = []

        # Collect all valid moves with their distances
        for tile in available_pieces:
            for rotation in range(6):
                rotated = tile.rotate(rotation)
                for position in game_state.get_available_positions():
                    score = game_state.score_potential_move(rotated, position)
                    if score is not None:
                        distance = self._distance_from_center(position)
                        valid_moves.append((rotated, position, distance))

        # Sort by distance (farthest first)
        valid_moves.sort(key=lambda x: x[2], reverse=True)

        # Pick the farthest valid move
        tile, position, _ = valid_moves[0]
        return (tile, position)

    def pick_piece_to_pop(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        # Pop the piece closest to center
        return min(possible_pop_locations, key=self._distance_from_center)
```

## Example 3: Defensive Strategy

Minimize opponent's scoring opportunities:

```python
from tangosim.strategy import Strategy
from tangosim.models import Tile, GameState, get_bordering_positions
from typing import Set, Tuple, List

class DefensiveStrategy(Strategy):
    def __init__(self, player: int):
        super().__init__()
        self.player = player

    def _evaluate_opponent_options(self,
                                   game_state: GameState,
                                   position: Tuple[int, int]) -> int:
        """Count how many new positions this move opens up for opponent."""
        neighbors = get_bordering_positions(position)
        new_positions = 0

        for neighbor in neighbors:
            # Check if this neighbor is empty and adjacent to existing tiles
            # (simplified - full implementation would check game state)
            if neighbor not in game_state.get_available_positions():
                neighbor_neighbors = get_bordering_positions(neighbor)
                if any(n in game_state.get_available_positions()
                       for n in neighbor_neighbors):
                    new_positions += 1

        return new_positions

    def formulate_turn_impl(self,
                           game_state: GameState,
                           available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        valid_moves = []

        # Evaluate all valid moves
        for tile in available_pieces:
            for rotation in range(6):
                rotated = tile.rotate(rotation)
                for position in game_state.get_available_positions():
                    my_score = game_state.score_potential_move(rotated, position)
                    if my_score is not None:
                        opponent_options = self._evaluate_opponent_options(
                            game_state, position
                        )
                        # Favor high score, few opponent options
                        value = my_score - (opponent_options * 0.5)
                        valid_moves.append((rotated, position, value))

        # Pick move with best defensive value
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        tile, position, _ = valid_moves[0]
        return (tile, position)

    def pick_piece_to_pop(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        # Pop pieces that give opponent fewer options
        return min(possible_pop_locations,
                  key=lambda p: self._evaluate_opponent_options(game_state, p))
```

## Example 4: Look-Ahead Strategy

Consider future moves:

```python
from tangosim.strategy import Strategy
from tangosim.models import Tile, GameState
from typing import Set, Tuple, List

class LookAheadStrategy(Strategy):
    def __init__(self, player: int, depth: int = 2):
        super().__init__()
        self.player = player
        self.depth = depth

    def _simulate_move(self,
                       game_state: GameState,
                       tile: Tile,
                       position: Tuple[int, int]) -> GameState:
        """Apply a move and return the new game state."""
        return game_state.place_tile(tile, position, self.player)

    def _evaluate_position(self,
                          game_state: GameState,
                          available_pieces: Set[Tile],
                          depth: int) -> float:
        """Recursively evaluate a position."""
        if depth == 0:
            scores = game_state.get_scores()
            return scores[self.player]

        best_value = float('-inf')

        for tile in list(available_pieces)[:3]:  # Limit branching
            for position in list(game_state.get_available_positions())[:5]:
                score = game_state.score_potential_move(tile, position)
                if score is not None:
                    new_state = self._simulate_move(game_state, tile, position)
                    new_pieces = available_pieces - {tile}
                    value = self._evaluate_position(new_state, new_pieces, depth - 1)
                    best_value = max(best_value, value)

        return best_value if best_value != float('-inf') else 0

    def formulate_turn_impl(self,
                           game_state: GameState,
                           available_pieces: Set[Tile]) -> Tuple[Tile, Tuple[int, int]]:
        best_move = None
        best_value = float('-inf')

        for tile in available_pieces:
            for rotation in range(6):
                rotated = tile.rotate(rotation)
                for position in game_state.get_available_positions():
                    if game_state.score_potential_move(rotated, position) is not None:
                        new_state = self._simulate_move(game_state, rotated, position)
                        new_pieces = available_pieces - {tile}
                        value = self._evaluate_position(
                            new_state, new_pieces, self.depth - 1
                        )

                        if value > best_value:
                            best_value = value
                            best_move = (rotated, position)

        return best_move

    def pick_piece_to_pop(self,
                         game_state: GameState,
                         available_pieces: Set[Tile],
                         possible_pop_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        return possible_pop_locations[0]
```

## Strategy Testing

Always test your strategy:

```python
import pytest
from tangosim.strategy import RandomStrategy
from tangosim.gameengine import SimpleTangoGame
from my_strategies import EdgeStrategy

def test_edge_strategy_completes_game():
    """Test that EdgeStrategy can complete a full game."""
    player1 = EdgeStrategy(0)
    player2 = RandomStrategy(1)

    game = SimpleTangoGame([player1, player2])
    final_state, _ = game.play()

    # Game should complete
    scores = final_state.get_scores()
    assert len(scores) == 2
    assert all(s >= 0 for s in scores)

def test_edge_strategy_vs_random():
    """Run multiple games and check win rate."""
    wins = 0
    games = 50

    for _ in range(games):
        player1 = EdgeStrategy(0)
        player2 = RandomStrategy(1)
        game = SimpleTangoGame([player1, player2])
        final_state, _ = game.play()
        scores = final_state.get_scores()

        if scores[0] > scores[1]:
            wins += 1

    win_rate = wins / games
    print(f"EdgeStrategy win rate: {win_rate:.2%}")
    # Should do better than random (>50%)
    assert win_rate > 0.4  # Allow some variance
```

## Best Practices

1. **Start Simple**: Begin with a basic strategy and iterate
2. **Profile Performance**: Use diagnostics to identify bottlenecks
3. **Validate Moves**: Always check that moves are legal
4. **Test Thoroughly**: Run many simulations to evaluate effectiveness
5. **Document Strategy**: Explain your approach and trade-offs
6. **Handle Edge Cases**: Consider what happens with few pieces left

## Debugging Strategies

Use the `turn_diagnostics` attribute to track decisions:

```python
class DebugStrategy(Strategy):
    def formulate_turn_impl(self, game_state, available_pieces):
        # Log information
        self.turn_diagnostics.append({
            'turn': self.turn_number,
            'available_positions': len(game_state.get_available_positions()),
            'available_pieces': len(available_pieces),
        })

        # ... make move ...

# After game
strategy = DebugStrategy(0)
# ... play game ...
print(strategy.turn_diagnostics)
```

## Performance Tips

- Cache expensive computations
- Limit search depth in look-ahead strategies
- Use early termination when appropriate
- Profile your code to find hotspots
- Consider move ordering for alpha-beta pruning

## Next Steps

- Study the [GreedyStrategy implementation](../../src/tangosim/strategy.py)
- Run tournaments between strategies
- Analyze game outcomes to refine your approach
- Share your strategies with the community!
