"""Game simulation module for running batch games and collecting statistics."""

from dataclasses import dataclass, field
from typing import Type, List, Dict, Tuple, Optional, Callable, Any
import json
import statistics
import sys
import io

from tangosim.models import GameState, Tile, get_bordering_positions
from tangosim.gameengine import TangoGame, SimpleTangoGame, AdvancedTangoGame
from tangosim.strategy import Strategy


@dataclass
class DistributionStats:
    """Statistical summary of a distribution."""
    mean: float
    std: float
    min_val: float
    max_val: float
    median: float
    count: int

    @classmethod
    def from_values(cls, values: List[float]) -> 'DistributionStats':
        """Create stats from a list of values."""
        if not values:
            return cls(0.0, 0.0, 0.0, 0.0, 0.0, 0)
        return cls(
            mean=statistics.mean(values),
            std=statistics.stdev(values) if len(values) > 1 else 0.0,
            min_val=min(values),
            max_val=max(values),
            median=statistics.median(values),
            count=len(values)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'mean': self.mean,
            'std': self.std,
            'min': self.min_val,
            'max': self.max_val,
            'median': self.median,
            'count': self.count
        }


@dataclass
class GameResult:
    """Result from a single game."""
    scores: List[int]
    winner: int  # Player index, or -1 for tie
    score_gap: int  # Winner score - loser score (0 if tie)
    rounds: int
    neighbor_affinity: List[float]  # Per-player clustering metric


@dataclass
class SimulationResults:
    """Aggregated results from running multiple game simulations."""

    num_games: int
    wins: List[int]  # Win count per player
    ties: int
    win_percentages: List[float]  # Win percentage per player
    score_distributions: List[DistributionStats]  # Per player
    score_gap_distribution: DistributionStats  # Winner - loser, excluding ties
    rounds_distribution: DistributionStats
    neighbor_affinity_distributions: List[DistributionStats]  # Per player
    raw_results: List[GameResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'num_games': self.num_games,
            'wins': self.wins,
            'ties': self.ties,
            'win_percentages': self.win_percentages,
            'score_distributions': [d.to_dict() for d in self.score_distributions],
            'score_gap_distribution': self.score_gap_distribution.to_dict(),
            'rounds_distribution': self.rounds_distribution.to_dict(),
            'neighbor_affinity_distributions': [
                d.to_dict() for d in self.neighbor_affinity_distributions
            ]
        }

    def to_json(self, indent: int = 2) -> str:
        """Export results as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def compute_neighbor_affinity(gamestate: GameState, num_players: int = 2) -> List[float]:
    """Compute neighbor affinity clustering metric for each player.

    The neighbor affinity is the ratio of same-color neighbors to total neighbors
    for all tiles owned by a player. A higher value indicates more clustered
    tile placement.

    Args:
        gamestate: The final game state
        num_players: Number of players in the game

    Returns:
        List of affinity scores (0.0 to 1.0) per player
    """
    same_color_neighbors = [0] * num_players
    total_neighbors = [0] * num_players

    for position, tile in gamestate.tiles.items():
        player = tile.color
        bordering_positions = get_bordering_positions(position)

        for neighbor_pos in bordering_positions:
            if neighbor_pos in gamestate.tiles:
                total_neighbors[player] += 1
                neighbor_tile = gamestate.tiles[neighbor_pos]
                if neighbor_tile.color == player:
                    same_color_neighbors[player] += 1

    # Compute ratios (avoid division by zero)
    affinities = []
    for player in range(num_players):
        if total_neighbors[player] > 0:
            affinities.append(same_color_neighbors[player] / total_neighbors[player])
        else:
            affinities.append(0.0)

    return affinities


def run_single_game(
    game_class: Type[TangoGame],
    strategy_factories: List[Callable[[int], Strategy]],
    suppress_output: bool = True
) -> GameResult:
    """Run a single game and return the result.

    Args:
        game_class: SimpleTangoGame or AdvancedTangoGame
        strategy_factories: List of callables that take player_idx and return Strategy
        suppress_output: If True, suppress print statements during game

    Returns:
        GameResult with all metrics computed
    """
    # Create fresh strategy instances for each game
    strategies = [factory(idx) for idx, factory in enumerate(strategy_factories)]

    game = game_class(strategies)

    # Suppress output by redirecting print (strategies print move info)
    if suppress_output:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    try:
        gamestate, last_player, rounds = game.play()
    finally:
        if suppress_output:
            sys.stdout = old_stdout

    scores = gamestate.get_scores()

    # Determine winner
    max_score = max(scores)
    winners = [i for i, s in enumerate(scores) if s == max_score]

    if len(winners) > 1:
        winner = -1  # Tie
        score_gap = 0
    else:
        winner = winners[0]
        loser_scores = [s for i, s in enumerate(scores) if i != winner]
        score_gap = max_score - max(loser_scores) if loser_scores else 0

    # Compute neighbor affinity
    neighbor_affinity = compute_neighbor_affinity(gamestate, len(strategies))

    return GameResult(
        scores=scores,
        winner=winner,
        score_gap=score_gap,
        rounds=rounds,
        neighbor_affinity=neighbor_affinity
    )


class Simulator:
    """Run batch game simulations and collect statistics."""

    def __init__(
        self,
        strategy_factories: List[Callable[[int], Strategy]],
        game_mode: str = 'simple',
        num_games: int = 1000
    ):
        """Initialize the simulator.

        Args:
            strategy_factories: List of callables that create Strategy instances.
                               Each callable takes player_idx (int) and returns Strategy.
                               Example: [lambda p: GreedyStrategy(p), lambda p: RandomStrategy(p)]
            game_mode: 'simple' for SimpleTangoGame, 'advanced' for AdvancedTangoGame
            num_games: Number of games to simulate (default 1000)
        """
        self.strategy_factories = strategy_factories
        self.num_games = num_games

        if game_mode == 'simple':
            self.game_class = SimpleTangoGame
        elif game_mode == 'advanced':
            self.game_class = AdvancedTangoGame
        else:
            raise ValueError(f"Unknown game mode: {game_mode}. Use 'simple' or 'advanced'.")

    def run(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        keep_raw_results: bool = False
    ) -> SimulationResults:
        """Run the simulation and return aggregated results.

        Args:
            progress_callback: Optional callback(current, total) for progress reporting
            keep_raw_results: If True, include raw GameResult list in results

        Returns:
            SimulationResults with all statistics computed
        """
        results: List[GameResult] = []
        num_players = len(self.strategy_factories)

        for i in range(self.num_games):
            result = run_single_game(
                self.game_class,
                self.strategy_factories,
                suppress_output=True
            )
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, self.num_games)

        return self._aggregate_results(results, num_players, keep_raw_results)

    def _aggregate_results(
        self,
        results: List[GameResult],
        num_players: int,
        keep_raw: bool
    ) -> SimulationResults:
        """Aggregate individual game results into statistics."""

        # Win counts
        wins = [0] * num_players
        ties = 0
        for r in results:
            if r.winner == -1:
                ties += 1
            else:
                wins[r.winner] += 1

        # Win percentages
        total = len(results)
        win_percentages = [w / total * 100 for w in wins]

        # Score distributions per player
        score_distributions = []
        for player in range(num_players):
            player_scores = [float(r.scores[player]) for r in results]
            score_distributions.append(DistributionStats.from_values(player_scores))

        # Score gap distribution (excluding ties)
        score_gaps = [float(r.score_gap) for r in results if r.winner != -1]
        score_gap_dist = DistributionStats.from_values(score_gaps)

        # Rounds distribution
        rounds_list = [float(r.rounds) for r in results]
        rounds_dist = DistributionStats.from_values(rounds_list)

        # Neighbor affinity distributions per player
        affinity_dists = []
        for player in range(num_players):
            affinities = [r.neighbor_affinity[player] for r in results]
            affinity_dists.append(DistributionStats.from_values(affinities))

        return SimulationResults(
            num_games=total,
            wins=wins,
            ties=ties,
            win_percentages=win_percentages,
            score_distributions=score_distributions,
            score_gap_distribution=score_gap_dist,
            rounds_distribution=rounds_dist,
            neighbor_affinity_distributions=affinity_dists,
            raw_results=results if keep_raw else []
        )


def print_results(
    results: SimulationResults,
    player_names: Optional[List[str]] = None
) -> None:
    """Print human-readable summary of simulation results.

    Args:
        results: SimulationResults to display
        player_names: Optional names for players (defaults to "Player 0", "Player 1", etc.)
    """
    num_players = len(results.wins)
    if player_names is None:
        player_names = [f"Player {i}" for i in range(num_players)]

    print("=" * 60)
    print(f"SIMULATION RESULTS ({results.num_games} games)")
    print("=" * 60)

    # Win statistics
    print("\n--- Win Statistics ---")
    for i, name in enumerate(player_names):
        print(f"  {name}: {results.wins[i]} wins ({results.win_percentages[i]:.1f}%)")
    print(f"  Ties: {results.ties} ({results.ties / results.num_games * 100:.1f}%)")

    # Score distributions
    print("\n--- Score Distributions ---")
    for i, name in enumerate(player_names):
        dist = results.score_distributions[i]
        print(f"  {name}:")
        print(f"    Mean: {dist.mean:.2f} | Std: {dist.std:.2f}")
        print(f"    Min: {dist.min_val:.0f} | Max: {dist.max_val:.0f} | Median: {dist.median:.1f}")

    # Score gap
    print("\n--- Score Gap (Winner - Loser) ---")
    gap = results.score_gap_distribution
    if gap.count > 0:
        print(f"  Mean: {gap.mean:.2f} | Std: {gap.std:.2f}")
        print(f"  Min: {gap.min_val:.0f} | Max: {gap.max_val:.0f} | Median: {gap.median:.1f}")
    else:
        print("  No decisive games (all ties)")

    # Game length
    print("\n--- Game Length (Rounds) ---")
    rnd = results.rounds_distribution
    print(f"  Mean: {rnd.mean:.2f} | Std: {rnd.std:.2f}")
    print(f"  Min: {rnd.min_val:.0f} | Max: {rnd.max_val:.0f} | Median: {rnd.median:.1f}")

    # Neighbor affinity
    print("\n--- Neighbor Affinity (Clustering) ---")
    for i, name in enumerate(player_names):
        aff = results.neighbor_affinity_distributions[i]
        print(f"  {name}:")
        print(f"    Mean: {aff.mean:.3f} | Std: {aff.std:.3f}")
        print(f"    Min: {aff.min_val:.3f} | Max: {aff.max_val:.3f}")

    print("\n" + "=" * 60)


def save_results_json(results: SimulationResults, filepath: str) -> None:
    """Save simulation results to a JSON file.

    Args:
        results: SimulationResults to save
        filepath: Path to output JSON file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(results.to_json())


def simulate(
    strategy1: Type[Strategy],
    strategy2: Type[Strategy],
    num_games: int = 1000,
    game_mode: str = 'simple',
    verbose: bool = True,
    json_output: Optional[str] = None
) -> SimulationResults:
    """Convenience function to run a simulation between two strategies.

    Args:
        strategy1: Strategy class for player 0
        strategy2: Strategy class for player 1
        num_games: Number of games to simulate
        game_mode: 'simple' or 'advanced'
        verbose: If True, print results to console
        json_output: If provided, save results to this JSON file path

    Returns:
        SimulationResults

    Example:
        >>> from tangosim.simulator import simulate
        >>> from tangosim.strategy import GreedyStrategy, RandomStrategy
        >>> results = simulate(GreedyStrategy, RandomStrategy, num_games=100)
    """
    # Use default arguments to capture the strategy class properly
    sim = Simulator(
        strategy_factories=[
            lambda p, s=strategy1: s(p),
            lambda p, s=strategy2: s(p)
        ],
        game_mode=game_mode,
        num_games=num_games
    )

    # Progress reporting for verbose mode
    def progress(current: int, total: int) -> None:
        if current % 100 == 0 or current == total:
            print(f"\rProgress: {current}/{total} games...", end='', flush=True)

    results = sim.run(progress_callback=progress if verbose else None)

    if verbose:
        print()  # Newline after progress
        print_results(results, [strategy1.__name__, strategy2.__name__])

    if json_output:
        save_results_json(results, json_output)
        if verbose:
            print(f"\nResults saved to: {json_output}")

    return results
