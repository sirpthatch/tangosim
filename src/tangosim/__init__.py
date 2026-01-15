"""TangoSim - A simulator for the Tango tile-laying game."""

from tangosim.models import Tile, GameState, TangoAction, ActionType
from tangosim.renderer import render_gamestate_svg, save_gamestate_svg
from tangosim.simulator import (
    Simulator,
    SimulationResults,
    GameResult,
    DistributionStats,
    simulate,
    compute_neighbor_affinity,
    print_results,
    save_results_json,
)
from tangosim.recorder import GameRecord, create_game_record

__all__ = [
    "Tile",
    "GameState",
    "TangoAction",
    "ActionType",
    "render_gamestate_svg",
    "save_gamestate_svg",
    "Simulator",
    "SimulationResults",
    "GameResult",
    "DistributionStats",
    "simulate",
    "compute_neighbor_affinity",
    "print_results",
    "save_results_json",
    "GameRecord",
    "create_game_record",
]
