# Quick Start Guide

This guide will help you run your first Tango game simulation in minutes.

## Installation

First, set up your environment:

```bash
# Clone the repository
git clone <repository-url>
cd tangosim

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

## Your First Simulation

Create a file called `first_game.py`:

```python
from tangosim.models import Tile
from tangosim.strategy import RandomStrategy, GreedyStrategy
from tangosim.gameengine import SimpleTangoGame

# Create two players with different strategies
player1 = RandomStrategy(player=0)
player2 = GreedyStrategy(player=1)

# Create and run the game
game = SimpleTangoGame([player1, player2])
final_state, last_player = game.play()

# Display results
scores = final_state.get_scores()
print(f"Game Over!")
print(f"Player 0 (Random):  {scores[0]} points")
print(f"Player 1 (Greedy):  {scores[1]} points")
print(f"Winner: Player {0 if scores[0] > scores[1] else 1}")
```

Run it:

```bash
python first_game.py
```

## Running Multiple Simulations

To get meaningful statistics, run multiple games:

```python
from tangosim.strategy import RandomStrategy, GreedyStrategy
from tangosim.gameengine import SimpleTangoGame

def run_simulation(num_games=100):
    player1_wins = 0
    player2_wins = 0
    ties = 0

    for i in range(num_games):
        player1 = RandomStrategy(0)
        player2 = GreedyStrategy(1)

        game = SimpleTangoGame([player1, player2])
        final_state, _ = game.play()
        scores = final_state.get_scores()

        if scores[0] > scores[1]:
            player1_wins += 1
        elif scores[1] > scores[0]:
            player2_wins += 1
        else:
            ties += 1

        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{num_games} games...")

    print(f"\nResults after {num_games} games:")
    print(f"Random Strategy wins:  {player1_wins} ({player1_wins/num_games*100:.1f}%)")
    print(f"Greedy Strategy wins:  {player2_wins} ({player2_wins/num_games*100:.1f}%)")
    print(f"Ties:                  {ties} ({ties/num_games*100:.1f}%)")

if __name__ == "__main__":
    run_simulation(100)
```

## Creating Custom Tiles

```python
from tangosim.models import Tile

# Create a tile with 3 colored sides for player 0
# Pattern: [top, top-right, bottom-right, bottom, bottom-left, top-left]
tile = Tile(
    pattern=[True, False, True, False, True, False],
    color=0
)

# Check how many colored sides
print(f"This tile has {tile.num_ticks()} colored sides")

# Rotate the tile
rotated = tile.rotate(2)  # Rotate 120 degrees

# Check if tiles are rotationally equivalent
if tile.is_rotationally_equal(rotated):
    print("These tiles are equivalent under rotation")
```

## Understanding Game State

```python
from tangosim.models import GameState, Tile

# Start with an empty game state
state = GameState()

# Get available positions (initially just the center neighbors)
positions = state.get_available_positions()
print(f"Available positions: {positions}")

# Create and place a tile
tile = Tile([True, True, False, False, False, False], color=0)
new_state = state.place_tile(tile, list(positions)[0], player=0)

# Check scores
scores = new_state.get_scores()
print(f"Scores after first move: {scores}")
```

## Next Steps

- [Learn about game rules](game_rules.md)
- [Understand the coordinate system](coordinates.md)
- [Create custom strategies](custom_strategies.md)
- [Explore the API reference](../api/models.md)

## Testing Your Setup

Run the test suite to verify everything works:

```bash
pytest tests/ -v
```

All tests should pass. If you encounter issues, check:
1. Virtual environment is activated
2. All dependencies are installed
3. Python version is 3.8 or higher

## Common Issues

### Import Errors

If you get import errors, make sure your PYTHONPATH includes the `src` directory:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

Or use the provided setup script:

```bash
source bin/init_dev.sh
```

### Module Not Found

Make sure you're running from the project root directory and the virtual environment is activated.
