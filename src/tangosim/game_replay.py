"""Run a game and save SVG renders of each round."""

import os
from typing import List, Optional

from tangosim.models import GameState, Tile
from tangosim.gameengine import SimpleTangoGame, AdvancedTangoGame, TangoGame
from tangosim.strategy import Strategy, GreedyStrategy, RandomStrategy
from tangosim.renderer import save_gamestate_svg
from tangosim.recorder import GameRecord, create_game_record


def play_and_render(
    strategies: List[Strategy],
    output_dir: str,
    game_mode: str = 'simple',
    show_available: bool = True,
    show_coordinates: bool = False,
    save_record: str = None
) -> Optional[GameRecord]:
    """Play a game and render each round to SVG files.

    Args:
        strategies: List of strategy instances for each player
        output_dir: Directory to save SVG files
        game_mode: 'simple' or 'advanced'
        show_available: Show available positions in renders
        show_coordinates: Show coordinate labels on tiles
        save_record: Optional filepath to save game record JSON

    Returns:
        GameRecord if save_record is provided, None otherwise
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create game
    if game_mode == 'simple':
        game = SimpleTangoGame(strategies)
    elif game_mode == 'advanced':
        game = AdvancedTangoGame(strategies)
    else:
        raise ValueError(f"Unknown game mode: {game_mode}")

    # Save initial tiles for recording
    initial_tiles = [set(tiles) for tiles in game.player_tiles]

    # Render initial state (empty board)
    filepath = os.path.join(output_dir, "round0.svg")
    save_gamestate_svg(
        game.gamestate,
        filepath,
        show_available_positions=show_available,
        show_coordinates=show_coordinates
    )
    print(f"Saved: {filepath}")

    # Play the game round by round
    round_num = 0
    while True:
        round_num += 1
        active_player_idx = (round_num - 1) % len(strategies)

        if game.is_game_over(active_player_idx):
            break

        # Execute the turn
        action = game._execute_turn(active_player_idx)

        # Render after this round
        filepath = os.path.join(output_dir, f"round{round_num}.svg")
        save_gamestate_svg(
            game.gamestate,
            filepath,
            show_available_positions=show_available,
            show_coordinates=show_coordinates
        )
        action_type = action.action_type.name if action else "SKIP"
        print(f"Saved: {filepath} (Player {active_player_idx + 1} {action_type})")

    # Print final results
    scores = game.gamestate.get_scores()
    print(f"\nGame complete after {round_num} rounds")
    print(f"Final scores: Player 1: {scores[0]}, Player 2: {scores[1]}")

    if scores[0] > scores[1]:
        print("Winner: Player 1")
    elif scores[1] > scores[0]:
        print("Winner: Player 2")
    else:
        print("Result: Tie")

    # Create and optionally save game record
    record = None
    record = create_game_record(
            game_mode=game_mode,
            initial_tiles=initial_tiles,
            actions=game.action_history,
            final_scores=scores,
            rounds=round_num
        )
    record.save(save_record)
    print(f"\nGame record saved to: {save_record}")

    return record


def main() -> None:
    """Run a game between two greedy strategies and save renders."""
    strategies = [GreedyStrategy(0), GreedyStrategy(1)]
    play_and_render(
        strategies,
        output_dir="output/game_renders",
        game_mode='advanced',
        show_available=True,
        show_coordinates=True,
        save_record="output/game_renders/game_record.json"
    )


if __name__ == "__main__":
    main()
