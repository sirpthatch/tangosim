"""SVG renderer for TangoSim game states."""

import math
from typing import Dict, List, Set, Tuple, Optional

from tangosim.models import GameState, Tile

# Color scheme
PLAYER_COLORS = {
    0: "#2E86AB",  # Steel blue
    1: "#E94F37",  # Vermilion red
}
HEXAGON_FILL = "#F8F8F8"
HEXAGON_STROKE = "#888888"
AVAILABLE_FILL = "#E8FFE8"
AVAILABLE_STROKE = "#88CC88"
BACKGROUND_COLOR = "#FFFFFF"
SCORE_HEADER_BG = "#F0F0F0"
TEXT_COLOR = "#333333"

# Layout constants
SCORE_HEADER_HEIGHT = 50
PADDING = 30


def _axial_to_pixel(q: int, r: int, size: float, offset: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    """Convert axial coordinates to pixel coordinates for pointy-top hexagons."""
    x = size * math.sqrt(3) * (q + r / 2) + offset[0]
    y = size * 1.5 * r + offset[1]
    return (x, y)


def _hexagon_corners(center_x: float, center_y: float, size: float) -> List[Tuple[float, float]]:
    """Calculate the 6 corner points of a pointy-top hexagon."""
    corners = []
    for i in range(6):
        angle_deg = 60 * i - 30  # Start at -30 degrees for pointy-top
        angle_rad = math.radians(angle_deg)
        corner_x = center_x + size * math.cos(angle_rad)
        corner_y = center_y + size * math.sin(angle_rad)
        corners.append((corner_x, corner_y))
    return corners


def _edge_triangle(corners: List[Tuple[float, float]],
                   center: Tuple[float, float],
                   edge_index: int,
                   inset: float = 0.05) -> List[Tuple[float, float]]:
    """Get triangle points for a filled edge (0-5).

    Returns three points: two corners of the edge (inset slightly) and a point
    partway toward the center.

    Args:
        corners: The 6 corners of the hexagon
        center: The center point of the hexagon
        edge_index: Which edge (0-5, clockwise from top)
        inset: Fraction to inset from full size (0.05 = 5% smaller on each edge)

    The game model uses axial coordinates where edges map to neighbors as:
    - Edge 0: top neighbor (q, r-1) -> faces -120 degrees
    - Edge 1: top-right neighbor (q+1, r-1) -> faces -60 degrees
    - Edge 2: bottom-right neighbor (q+1, r) -> faces 0 degrees
    - Edge 3: bottom neighbor (q, r+1) -> faces 60 degrees
    - Edge 4: bottom-left neighbor (q-1, r+1) -> faces 120 degrees
    - Edge 5: top-left neighbor (q-1, r) -> faces 180 degrees

    The hexagon corners are generated starting at -30 degrees:
    - Corner 0: -30 degrees (top-right)
    - Corner 1: 30 degrees (right)
    - Corner 2: 90 degrees (bottom-right)
    - Corner 3: 150 degrees (bottom-left)
    - Corner 4: 210 degrees (left)
    - Corner 5: 270 degrees (top-left)

    So edge 0 (facing -120°/top) uses corners 4 and 5 (the top-left edge of the hex).
    """
    # Map game edge index to renderer corner indices
    # Game edge 0 faces -120° (top), which is between corners 4 (210°) and 5 (270°)
    # Each subsequent game edge is 60° clockwise
    corner_offset = 4  # Corner index for the start of game edge 0
    start_idx = (edge_index + corner_offset) % 6
    end_idx = (edge_index + corner_offset + 1) % 6

    start_corner = corners[start_idx]
    end_corner = corners[end_idx]

    # Inset the edge corners along the edge (toward each other)
    inset_start = (
        start_corner[0] + inset * (end_corner[0] - start_corner[0]),
        start_corner[1] + inset * (end_corner[1] - start_corner[1]),
    )
    inset_end = (
        end_corner[0] + inset * (start_corner[0] - end_corner[0]),
        end_corner[1] + inset * (start_corner[1] - end_corner[1]),
    )

    # Calculate the midpoint of the edge
    edge_mid = (
        (start_corner[0] + end_corner[0]) / 2,
        (start_corner[1] + end_corner[1]) / 2,
    )

    # Move the apex toward the center, but stop short by inset amount
    apex = (
        edge_mid[0] + (1 - inset * 2) * (center[0] - edge_mid[0]),
        edge_mid[1] + (1 - inset * 2) * (center[1] - edge_mid[1]),
    )

    return [inset_start, inset_end, apex]


def _svg_polygon(points: List[Tuple[float, float]], fill: str, stroke: str,
                 stroke_width: float = 1, stroke_dasharray: Optional[str] = None,
                 opacity: Optional[float] = None) -> str:
    """Generate SVG polygon element."""
    points_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    attrs = f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"'
    if stroke_dasharray:
        attrs += f' stroke-dasharray="{stroke_dasharray}"'
    if opacity is not None:
        attrs += f' opacity="{opacity}"'
    return f'<polygon points="{points_str}" {attrs}/>'

def _svg_rect(x: float, y: float, width: float, height: float,
              fill: str, stroke: Optional[str] = None, rx: float = 0) -> str:
    """Generate SVG rect element."""
    attrs = f'x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="{fill}"'
    if stroke:
        attrs += f' stroke="{stroke}"'
    if rx > 0:
        attrs += f' rx="{rx}"'
    return f'<rect {attrs}/>'


def _svg_text(x: float, y: float, text: str, font_size: int = 14,
              anchor: str = "start", fill: str = TEXT_COLOR,
              font_weight: str = "normal") -> str:
    """Generate SVG text element."""
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{font_size}" font-family="system-ui, sans-serif" text-anchor="{anchor}" fill="{fill}" font-weight="{font_weight}">{text}</text>'


def _calculate_bounds(positions: Set[Tuple[int, int]], hex_size: float) -> Tuple[float, float, float, float]:
    """Calculate pixel bounding box for a set of positions."""
    if not positions:
        return (0, 0, 0, 0)

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for q, r in positions:
        px, py = _axial_to_pixel(q, r, hex_size)
        min_x = min(min_x, px - hex_size)
        max_x = max(max_x, px + hex_size)
        min_y = min(min_y, py - hex_size)
        max_y = max(max_y, py + hex_size)

    return (min_x, min_y, max_x, max_y)


def _render_tile(tile: Tile, center_x: float, center_y: float, hex_size: float,
                 show_coordinates: bool = False, position: Optional[Tuple[int, int]] = None) -> str:
    """Render a single tile as SVG elements."""
    elements = []
    corners = _hexagon_corners(center_x, center_y, hex_size)
    center = (center_x, center_y)

    # Base hexagon
    elements.append(_svg_polygon(corners, HEXAGON_FILL, HEXAGON_STROKE, stroke_width=1.5))

    # Colored triangles where pattern is True (edge to center)
    player_color = PLAYER_COLORS.get(tile.color, "#999999")
    for i, is_marked in enumerate(tile.pattern):
        if is_marked:
            triangle_points = _edge_triangle(corners, center, i)
            elements.append(_svg_polygon(triangle_points, player_color, player_color, stroke_width=0.5))

    # Coordinate label if requested
    if show_coordinates and position:
        label = f"({position[0]},{position[1]})"
        elements.append(_svg_text(center_x, center_y + 4, label, font_size=10, anchor="middle", fill="#666666"))

    return "\n    ".join(elements)


def _render_available_position(center_x: float, center_y: float, hex_size: float) -> str:
    """Render an available position as a subtle dashed hexagon."""
    corners = _hexagon_corners(center_x, center_y, hex_size)
    return _svg_polygon(corners, AVAILABLE_FILL, AVAILABLE_STROKE,
                        stroke_width=1.5, stroke_dasharray="5,5", opacity=0.6)


def _render_score_footer(scores: List[int], width: float, start_x: float, start_y: float) -> str:
    """Render the score footer bar below the game board."""
    elements = []

    # Background bar
    elements.append(_svg_rect(start_x, start_y, width, SCORE_HEADER_HEIGHT, SCORE_HEADER_BG, rx=5))

    # Player 0 score (left side)
    swatch_x = start_x + 15
    swatch_y = start_y + 13
    elements.append(_svg_rect(swatch_x, swatch_y, 24, 24, PLAYER_COLORS[0], rx=3))
    elements.append(_svg_text(swatch_x + 34, swatch_y + 17, f"Player 1: {scores[0]}", font_size=16, font_weight="bold"))

    # Player 1 score (right side)
    swatch_x_right = start_x + width - 150
    elements.append(_svg_rect(swatch_x_right, swatch_y, 24, 24, PLAYER_COLORS[1], rx=3))
    elements.append(_svg_text(swatch_x_right + 34, swatch_y + 17, f"Player 2: {scores[1]}", font_size=16, font_weight="bold"))

    return "\n  ".join(elements)


def render_gamestate_svg(
    gamestate: GameState,
    hex_size: float = 40.0,
    show_available_positions: bool = True,
    show_coordinates: bool = False,
) -> str:
    """Render a GameState to an SVG string.

    Args:
        gamestate: The GameState to render
        hex_size: Size of hexagons in pixels (center to corner)
        show_available_positions: Whether to show where tiles can be placed
        show_coordinates: Whether to show (q,r) labels on tiles

    Returns:
        Complete SVG document as a string
    """
    tiles = gamestate.get_tiles()
    available = gamestate.get_available_positions()
    scores = gamestate.get_scores()

    # Collect all positions for bounds calculation
    all_positions = set(tiles.keys())
    if show_available_positions:
        all_positions.update(available)

    # Handle empty board
    if not all_positions:
        all_positions.add((0, 0))

    # Calculate bounds for the game board
    min_x, min_y, max_x, max_y = _calculate_bounds(all_positions, hex_size)

    # Store board bottom for score footer placement
    board_max_y = max_y

    # Add padding around the board
    min_x -= PADDING
    min_y -= PADDING
    max_x += PADDING
    max_y += PADDING + SCORE_HEADER_HEIGHT + 10  # Extra space for footer

    width = max_x - min_x
    height = max_y - min_y

    # Build SVG content
    svg_elements = []

    # Background
    svg_elements.append(_svg_rect(min_x, min_y, width, height, BACKGROUND_COLOR))

    # Available positions (render first so tiles appear on top)
    if show_available_positions:
        for q, r in available:
            px, py = _axial_to_pixel(q, r, hex_size)
            svg_elements.append(_render_available_position(px, py, hex_size))

    # Placed tiles
    for (q, r), tile in tiles.items():
        px, py = _axial_to_pixel(q, r, hex_size)
        svg_elements.append(_render_tile(tile, px, py, hex_size, show_coordinates, (q, r)))

    # Score footer (below the game board)
    footer_y = board_max_y + PADDING
    svg_elements.append(_render_score_footer(scores, width - 20, min_x + 10, footer_y))

    # Assemble SVG document
    content = "\n  ".join(svg_elements)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width:.0f}" height="{height:.0f}"
     viewBox="{min_x:.2f} {min_y:.2f} {width:.2f} {height:.2f}">
  {content}
</svg>'''

    return svg


def save_gamestate_svg(
    gamestate: GameState,
    filepath: str,
    **kwargs
) -> None:
    """Render gamestate and save to file.

    Args:
        gamestate: The GameState to render
        filepath: Path to save the SVG file
        **kwargs: Additional arguments passed to render_gamestate_svg
    """
    svg_content = render_gamestate_svg(gamestate, **kwargs)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
