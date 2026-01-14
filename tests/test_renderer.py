"""Tests for the SVG renderer."""

import math
from tangosim.models import Tile, GameState
from tangosim.renderer import (
    _axial_to_pixel,
    _hexagon_corners,
    _edge_triangle,
    render_gamestate_svg,
    save_gamestate_svg,
    PLAYER_COLORS,
)


class TestCoordinateConversion:
    """Tests for axial to pixel coordinate conversion."""

    def test_origin_with_no_offset(self):
        """Origin (0,0) should map to (0,0) with no offset."""
        x, y = _axial_to_pixel(0, 0, 40.0)
        assert x == 0.0
        assert y == 0.0

    def test_origin_with_offset(self):
        """Origin should be shifted by offset."""
        x, y = _axial_to_pixel(0, 0, 40.0, offset=(100, 50))
        assert x == 100.0
        assert y == 50.0

    def test_q_axis_moves_right(self):
        """Increasing q should move right (positive x)."""
        x1, _ = _axial_to_pixel(0, 0, 40.0)
        x2, _ = _axial_to_pixel(1, 0, 40.0)
        assert x2 > x1

    def test_r_axis_moves_down(self):
        """Increasing r should move down (positive y)."""
        _, y1 = _axial_to_pixel(0, 0, 40.0)
        _, y2 = _axial_to_pixel(0, 1, 40.0)
        assert y2 > y1

    def test_neighbors_equidistant(self):
        """All 6 neighbors should be the same distance from center."""
        size = 40.0
        center_x, center_y = _axial_to_pixel(0, 0, size)
        neighbors = [
            (0, -1), (1, -1), (1, 0),
            (0, 1), (-1, 1), (-1, 0)
        ]
        distances = []
        for q, r in neighbors:
            nx, ny = _axial_to_pixel(q, r, size)
            dist = math.sqrt((nx - center_x) ** 2 + (ny - center_y) ** 2)
            distances.append(dist)

        # All distances should be equal (within floating point tolerance)
        for d in distances:
            assert abs(d - distances[0]) < 0.001


class TestHexagonGeometry:
    """Tests for hexagon corner and edge calculations."""

    def test_hexagon_has_six_corners(self):
        """Hexagon should have exactly 6 corners."""
        corners = _hexagon_corners(0, 0, 40)
        assert len(corners) == 6

    def test_corners_equidistant_from_center(self):
        """All corners should be the same distance from center."""
        cx, cy, size = 100, 100, 40
        corners = _hexagon_corners(cx, cy, size)
        for corner_x, corner_y in corners:
            dist = math.sqrt((corner_x - cx) ** 2 + (corner_y - cy) ** 2)
            assert abs(dist - size) < 0.001

    def test_corners_60_degrees_apart(self):
        """Corners should be 60 degrees apart."""
        corners = _hexagon_corners(0, 0, 40)
        angles = []
        for x, y in corners:
            angle = math.atan2(y, x)
            angles.append(angle)

        # Sort and check differences
        angles.sort()
        for i in range(len(angles) - 1):
            diff = angles[i + 1] - angles[i]
            assert abs(diff - math.radians(60)) < 0.001

    def test_edge_triangle_returns_three_points(self):
        """Edge triangle should return three points (two corners + center)."""
        corners = _hexagon_corners(0, 0, 40)
        center = (0, 0)
        for edge_idx in range(6):
            triangle = _edge_triangle(corners, center, edge_idx)
            assert len(triangle) == 3

    def test_edge_triangle_apex_near_center(self):
        """Edge triangle apex should be near the center (but inset)."""
        corners = _hexagon_corners(100, 100, 40)
        center = (100, 100)
        for edge_idx in range(6):
            triangle = _edge_triangle(corners, center, edge_idx)
            apex = triangle[2]
            # Apex should be closer to center than to the edge
            edge_mid = ((triangle[0][0] + triangle[1][0]) / 2,
                        (triangle[0][1] + triangle[1][1]) / 2)
            dist_to_center = math.sqrt((apex[0] - center[0])**2 + (apex[1] - center[1])**2)
            dist_to_edge = math.sqrt((apex[0] - edge_mid[0])**2 + (apex[1] - edge_mid[1])**2)
            assert dist_to_center < dist_to_edge

    def test_edge_triangle_points_near_corners(self):
        """Edge triangle edge points should be near (but inset from) adjacent corners."""
        corners = _hexagon_corners(0, 0, 40)
        center = (0, 0)
        for edge_idx in range(6):
            triangle = _edge_triangle(corners, center, edge_idx)
            # First two points should be on the edge line, slightly inset from corners
            # The corner mapping uses offset 4 to align with axial coordinates
            corner_offset = 4
            start_idx = (edge_idx + corner_offset) % 6
            end_idx = (edge_idx + corner_offset + 1) % 6
            # Points should be close to but not exactly at corners
            start_dist = math.sqrt((triangle[0][0] - corners[start_idx][0])**2 +
                                   (triangle[0][1] - corners[start_idx][1])**2)
            end_dist = math.sqrt((triangle[1][0] - corners[end_idx][0])**2 +
                                 (triangle[1][1] - corners[end_idx][1])**2)
            # With 5% inset, distances should be small but non-zero
            assert 0 < start_dist < 10
            assert 0 < end_dist < 10


class TestRenderGamestate:
    """Tests for the main render function."""

    def test_render_empty_gamestate(self):
        """Empty gamestate should render without error."""
        gs = GameState()
        svg = render_gamestate_svg(gs)
        assert svg.startswith('<?xml version="1.0"')
        assert '<svg' in svg
        assert '</svg>' in svg

    def test_render_single_tile(self):
        """Single tile should render correctly."""
        gs = GameState()
        tile = Tile([True, False, False, False, False, False], color=0)
        gs.place_tile(tile, (0, 0))
        svg = render_gamestate_svg(gs)
        assert '<polygon' in svg  # Hexagon shape
        assert PLAYER_COLORS[0] in svg  # Player color for marked edge

    def test_render_both_player_colors(self):
        """Both player colors should appear when tiles from both players exist."""
        gs = GameState()
        tile0 = Tile([True, False, False, False, False, False], color=0)
        tile1 = Tile([False, False, False, True, False, False], color=1)
        gs.place_tile(tile0, (0, 0))
        gs.place_tile(tile1, (1, 0))
        svg = render_gamestate_svg(gs)
        assert PLAYER_COLORS[0] in svg
        assert PLAYER_COLORS[1] in svg

    def test_scores_displayed(self):
        """Scores should appear in the SVG."""
        gs = GameState()
        tile = Tile([True, True, True, True, True, True], color=0)
        gs.place_tile(tile, (0, 0))
        svg = render_gamestate_svg(gs)
        # Score text should be present
        assert 'Player 1:' in svg
        assert 'Player 2:' in svg

    def test_available_positions_rendered_when_enabled(self):
        """Available positions should render when flag is True."""
        gs = GameState()
        tile = Tile([True, False, False, False, False, False], color=0)
        gs.place_tile(tile, (0, 0))
        svg = render_gamestate_svg(gs, show_available_positions=True)
        # Should have dashed polygons for available positions
        assert 'stroke-dasharray' in svg

    def test_available_positions_hidden_when_disabled(self):
        """Available positions should not render when flag is False."""
        gs = GameState()
        tile = Tile([True, False, False, False, False, False], color=0)
        gs.place_tile(tile, (0, 0))
        svg = render_gamestate_svg(gs, show_available_positions=False)
        # Should not have dashed polygons
        assert 'stroke-dasharray' not in svg

    def test_coordinates_shown_when_enabled(self):
        """Coordinate labels should appear when show_coordinates is True."""
        gs = GameState()
        tile = Tile([True, False, False, False, False, False], color=0)
        gs.place_tile(tile, (0, 0))
        svg = render_gamestate_svg(gs, show_coordinates=True)
        assert '(0,0)' in svg

    def test_svg_is_valid_xml_structure(self):
        """SVG should have proper XML structure."""
        gs = GameState()
        tile = Tile([True, True, False, False, False, False], color=0)
        gs.place_tile(tile, (0, 0))
        svg = render_gamestate_svg(gs)

        # Check basic structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in svg
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg
        assert svg.count('<svg') == 1
        assert svg.count('</svg>') == 1


class TestSaveGamestate:
    """Tests for the file-saving function."""

    def test_save_creates_file(self, tmp_path):
        """save_gamestate_svg should create a file."""
        gs = GameState()
        tile = Tile([True, False, True, False, True, False], color=0)
        gs.place_tile(tile, (0, 0))

        filepath = tmp_path / "test_output.svg"
        save_gamestate_svg(gs, str(filepath))

        assert filepath.exists()

    def test_saved_file_content_matches_render(self, tmp_path):
        """Saved file content should match render output."""
        gs = GameState()
        tile = Tile([True, True, True, False, False, False], color=1)
        gs.place_tile(tile, (0, 0))

        expected = render_gamestate_svg(gs)
        filepath = tmp_path / "test_output.svg"
        save_gamestate_svg(gs, str(filepath))

        with open(filepath, 'r') as f:
            actual = f.read()

        assert actual == expected
