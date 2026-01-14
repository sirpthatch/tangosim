# TangoSim

A Python-based simulator for the Tango tile-laying game with support for multiple AI strategies and game analysis.

## Overview

TangoSim simulates the strategic tile-laying game Tango, where players place hexagonal tiles on a growing board. The game uses an axial coordinate system for hexagonal grids.

## Features

- **Hexagonal Tile System**: Uses axial coordinates for efficient hex grid management
- **Multiple AI Strategies**:
  - `RandomStrategy`: Makes random valid moves
  - `GreedyStrategy`: Optimizes for immediate scoring opportunities
- **Game Simulation**: Full game engine with rule enforcement and scoring
- **Tile Mechanics**:
  - 6-sided hexagonal tiles with colored patterns
  - Rotational tile placement
  - Tile popping dynamics
  - Enclosure detection
- **Testing Suite**: Comprehensive test coverage for game mechanics
- **Diagnostics**: Track game statistics and strategy performance

## Installation

### Prerequisites

- Python 3.8 or higher

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd tangosim
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Usage

### Running a Simulation

```python
from tangosim.models import Tile
from tangosim.strategy import GreedyStrategy, RandomStrategy
from tangosim.gameengine import SimpleTangoGame

# Create player strategies
player1 = RandomStrategy(player=0)
player2 = GreedyStrategy(player=1)

# Initialize and run game
game = SimpleTangoGame([player1, player2])
game_state, last_player = game.play()

# Get results
scores = game_state.get_scores()
print(f"Final scores: {scores}")
```

### Command Line

Run a simple simulation:
```bash
python -m tangosim.main
```

## Project Structure

```
tangosim/
├── src/
│   └── tangosim/
│       ├── __init__.py
│       ├── models.py        # Core game models (Tile, GameState)
│       ├── gameengine.py    # Game loop and rule enforcement
│       ├── strategy.py      # AI strategy implementations
│       └── main.py          # Entry point for simulations
├── tests/
│   ├── test_models.py       # Tests for game models
│   └── test_gameengine.py   # Tests for game engine
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
├── requirements.txt         # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tangosim --cov-report=html
```

### Code Quality

```bash
# Run linter
pylint src/tangosim/

# Run type checking
mypy src/tangosim/
```

### Environment Setup

The project includes a development setup script:
```bash
source bin/init_dev.sh
```

## Game Mechanics

### Tiles

- Hexagonal tiles with 6 sides
- Each side can be colored or uncolored
- Tiles belong to a specific player color
- Can be rotated in 60-degree increments

### Board

- Uses axial coordinate system (q, r)
- Grows dynamically as tiles are placed
- Reference: [Red Blob Games - Hexagonal Grids](https://www.redblobgames.com/grids/hexagons/#coordinates)

### Scoring

- Points awarded for specific tile patterns
- Includes single-pop and multi-pop scoring
- Enclosure detection for strategic play

## Roadmap

See the [README](README) file for current development tasks including:
- Simulation result analysis
- Defensive strategy implementation
- Weighted tile value strategies
- Game diagnostics (turn analysis, first-player advantage)
- Post-play tile visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass and code passes linting
5. Submit a pull request

## License

[Add license information]

## Authors

Thatcher

## Acknowledgments

- Hexagonal grid coordinate system based on [Red Blob Games](https://www.redblobgames.com/grids/hexagons/)
