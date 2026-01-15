"""Run a simulation between strategies."""

from tangosim.strategy import GreedyStrategy, RandomStrategy
from tangosim.simulator import simulate


def main() -> None:
    results = simulate(
        GreedyStrategy, RandomStrategy,
        num_games=1000,
        game_mode='advanced',
        json_output='sim_results.json'
    )


if __name__ == "__main__":
    main()