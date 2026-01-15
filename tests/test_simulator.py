"""Tests for the game simulator module."""

import pytest
import json
import tempfile
import os

from tangosim.simulator import (
    Simulator, SimulationResults, GameResult, DistributionStats,
    compute_neighbor_affinity, run_single_game, simulate,
    print_results, save_results_json
)
from tangosim.strategy import GreedyStrategy, RandomStrategy
from tangosim.gameengine import SimpleTangoGame, AdvancedTangoGame
from tangosim.models import GameState, Tile


class TestDistributionStats:
    """Tests for the DistributionStats dataclass."""

    def test_from_values_empty(self):
        """Empty list should produce zero stats."""
        stats = DistributionStats.from_values([])
        assert stats.count == 0
        assert stats.mean == 0.0
        assert stats.std == 0.0
        assert stats.min_val == 0.0
        assert stats.max_val == 0.0

    def test_from_values_single(self):
        """Single value should have zero std."""
        stats = DistributionStats.from_values([5.0])
        assert stats.count == 1
        assert stats.mean == 5.0
        assert stats.std == 0.0
        assert stats.min_val == 5.0
        assert stats.max_val == 5.0
        assert stats.median == 5.0

    def test_from_values_multiple(self):
        """Multiple values should compute correct stats."""
        stats = DistributionStats.from_values([1, 2, 3, 4, 5])
        assert stats.count == 5
        assert stats.mean == 3.0
        assert stats.min_val == 1
        assert stats.max_val == 5
        assert stats.median == 3.0
        assert stats.std > 0

    def test_to_dict(self):
        """to_dict should produce correct dictionary."""
        stats = DistributionStats.from_values([1, 2, 3])
        d = stats.to_dict()
        assert 'mean' in d
        assert 'std' in d
        assert 'min' in d
        assert 'max' in d
        assert 'median' in d
        assert 'count' in d


class TestNeighborAffinity:
    """Tests for the neighbor affinity clustering metric."""

    def test_empty_board(self):
        """Empty board should return zero affinity."""
        gs = GameState()
        affinity = compute_neighbor_affinity(gs)
        assert affinity == [0.0, 0.0]

    def test_single_tile(self):
        """Single tile with no neighbors should have zero affinity."""
        gs = GameState()
        gs.place_tile(Tile([True] * 6, 0), (0, 0))
        affinity = compute_neighbor_affinity(gs)
        assert affinity[0] == 0.0  # No neighbors to compare

    def test_two_same_color_tiles(self):
        """Two adjacent tiles of same color should have 1.0 affinity."""
        gs = GameState()
        tile1 = Tile([False, False, False, True, False, False], 0)
        tile2 = Tile([True, False, False, False, False, False], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (0, 1))
        affinity = compute_neighbor_affinity(gs)
        assert affinity[0] == 1.0  # All neighbors same color
        assert affinity[1] == 0.0  # Player 1 has no tiles

    def test_two_different_color_tiles(self):
        """Two adjacent tiles of different colors should have 0.0 affinity."""
        gs = GameState()
        tile1 = Tile([False, False, False, True, False, False], 0)
        tile2 = Tile([True, False, False, False, False, False], 1)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (0, 1))
        affinity = compute_neighbor_affinity(gs)
        assert affinity[0] == 0.0  # Neighbor is different color
        assert affinity[1] == 0.0  # Neighbor is different color


class TestRunSingleGame:
    """Tests for the run_single_game function."""

    def test_returns_game_result(self):
        """Should return a properly structured GameResult."""
        result = run_single_game(
            SimpleTangoGame,
            [lambda p: GreedyStrategy(p), lambda p: GreedyStrategy(p)]
        )
        assert isinstance(result, GameResult)
        assert len(result.scores) == 2
        assert result.rounds > 0
        assert len(result.neighbor_affinity) == 2

    def test_winner_determined(self):
        """Winner should be correctly determined."""
        result = run_single_game(
            SimpleTangoGame,
            [lambda p: GreedyStrategy(p), lambda p: RandomStrategy(p)]
        )
        if result.winner != -1:
            # Winner should have highest score
            assert result.scores[result.winner] == max(result.scores)
            assert result.score_gap > 0
        else:
            # Tie - scores should be equal
            assert result.scores[0] == result.scores[1]
            assert result.score_gap == 0

    def test_output_suppressed(self):
        """Game output should be suppressed when requested."""
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = captured = io.StringIO()
        try:
            run_single_game(
                SimpleTangoGame,
                [lambda p: GreedyStrategy(p), lambda p: GreedyStrategy(p)],
                suppress_output=True
            )
        finally:
            sys.stdout = old_stdout
        # Should have no output
        assert captured.getvalue() == ""


class TestSimulator:
    """Tests for the Simulator class."""

    def test_small_simulation(self):
        """Small simulation should complete correctly."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: RandomStrategy(p)
            ],
            num_games=10
        )
        results = sim.run()
        assert results.num_games == 10
        assert sum(results.wins) + results.ties == 10

    def test_advanced_mode(self):
        """Advanced game mode should work."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            game_mode='advanced',
            num_games=5
        )
        results = sim.run()
        assert results.num_games == 5

    def test_invalid_game_mode(self):
        """Invalid game mode should raise ValueError."""
        with pytest.raises(ValueError):
            Simulator(
                strategy_factories=[lambda p: GreedyStrategy(p)],
                game_mode='invalid'
            )

    def test_progress_callback(self):
        """Progress callback should be called."""
        progress_calls = []

        def callback(current, total):
            progress_calls.append((current, total))

        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=5
        )
        sim.run(progress_callback=callback)
        assert len(progress_calls) == 5
        assert progress_calls[-1] == (5, 5)

    def test_keep_raw_results(self):
        """Raw results should be kept when requested."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=5
        )
        results = sim.run(keep_raw_results=True)
        assert len(results.raw_results) == 5

    def test_discard_raw_results_by_default(self):
        """Raw results should be discarded by default."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=5
        )
        results = sim.run()
        assert len(results.raw_results) == 0


class TestSimulationResults:
    """Tests for the SimulationResults dataclass."""

    def test_to_dict(self):
        """to_dict should produce complete dictionary."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=5
        )
        results = sim.run()
        d = results.to_dict()
        assert 'num_games' in d
        assert 'wins' in d
        assert 'ties' in d
        assert 'win_percentages' in d
        assert 'score_distributions' in d
        assert 'score_gap_distribution' in d
        assert 'rounds_distribution' in d
        assert 'neighbor_affinity_distributions' in d

    def test_to_json(self):
        """to_json should produce valid JSON."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=5
        )
        results = sim.run()
        json_str = results.to_json()
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['num_games'] == 5


class TestOutputFunctions:
    """Tests for output functions."""

    def test_print_results_runs(self):
        """print_results should run without error."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=3
        )
        results = sim.run()
        # Should not raise
        print_results(results)
        print_results(results, player_names=['Alice', 'Bob'])

    def test_save_results_json(self):
        """save_results_json should create valid JSON file."""
        sim = Simulator(
            strategy_factories=[
                lambda p: GreedyStrategy(p),
                lambda p: GreedyStrategy(p)
            ],
            num_games=3
        )
        results = sim.run()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            save_results_json(results, filepath)
            with open(filepath, 'r') as f:
                data = json.load(f)
            assert data['num_games'] == 3
        finally:
            os.unlink(filepath)


class TestSimulateConvenience:
    """Tests for the simulate convenience function."""

    def test_simulate_basic(self):
        """Basic simulate call should work."""
        results = simulate(
            GreedyStrategy, RandomStrategy,
            num_games=5,
            verbose=False
        )
        assert results.num_games == 5

    def test_simulate_advanced_mode(self):
        """simulate with advanced mode should work."""
        results = simulate(
            GreedyStrategy, GreedyStrategy,
            num_games=3,
            game_mode='advanced',
            verbose=False
        )
        assert results.num_games == 3

    def test_simulate_json_output(self):
        """simulate with json_output should create file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            results = simulate(
                GreedyStrategy, GreedyStrategy,
                num_games=3,
                verbose=False,
                json_output=filepath
            )
            assert os.path.exists(filepath)
            with open(filepath, 'r') as f:
                data = json.load(f)
            assert data['num_games'] == 3
        finally:
            os.unlink(filepath)
