import pytest
import sys

from tangosim.models import GameState, Tile, get_marker_idx, get_bordering_positions

def test_can_rotate_tile() -> None:
    tile = Tile([True, False, False, False, False, False], 0)
    rotated_tile = tile.rotate(1)
    assert rotated_tile.pattern == [False, True, False, False, False, False]

def test_available_positions() -> None:
    game_state = GameState()
    game_board = game_state.get_tiles()
    assert len(game_board) == 0

def test_initial_available_position() -> None:
    game_state = GameState()
    available_positions = game_state.get_available_positions()
    assert len(available_positions)  == 1
    assert available_positions.pop() == (0,0)

def test_available_positions_updates() -> None:
    game_state = GameState()
    game_state.place_tile(
        Tile([True, False, False, False, False, False], 0), 
        (0,0))
    available_positions = game_state.get_available_positions()
    assert len(available_positions)  == 6
    assert available_positions == set([
        (0,-1), (1,-1), (1, 0), (0, 1), (-1, 1), (-1, 0)
    ])

def test_place_tile_throws_when_tile_unavailable() -> None:
    game_state = GameState()
    game_state.place_tile(
        Tile([True, False, False, False, False, False], 0), 
        (0,0))
    
    with pytest.raises(Exception):
        game_state.place_tile.place_tile(
            Tile([True, False, False, False, False, False], 0), 
            (3,3))
        
def test_available_positions_updates_with_2_pieces() -> None:
    game_state = GameState()
    game_state.place_tile(
        Tile([True, False, False, False, False, False], 0), 
        (0,0))
    game_state.place_tile(
        Tile([False, False, False, True, False, False], 0), 
        (0,-1))
    
    available_positions = game_state.get_available_positions()
    assert len(available_positions) == 8
    assert available_positions == set([
        (0,-2), (1,-2), (1, -1), (1, 0), (0, 1),
        (-1, 1), (-1, 0), (-1, -1)
        ])
    
def test_marker_idx() -> None:
    correct_border_lookups = {
        0:3,
        1:4,
        2:5,
        3:0,
        4:1,
        5:2
    }

    for pos, correct in correct_border_lookups.items():
        assert get_marker_idx(pos) == correct

def test_border_tile_constraint() -> None:
    game_state = GameState()
    game_state.place_tile(
        Tile([True, False, False, False, False, False], 0), 
        (0,0))
    game_state.place_tile(
        Tile([False, False, False, True, False, False], 0), 
        (0,-1))
    
    with pytest.raises(Exception):
        game_state.place_tile(
            Tile([False, False, False, True, False, False], 0), 
            (0,-1)) # Should raise an exception because existing tile on location
    
    game_state.place_tile(
            Tile([True, False, False, False, False, False], 0), 
            (1,-1)) # Should be fine, with one marker up

    with pytest.raises(Exception):
        game_state.place_tile(
            Tile([True, False, False, True, False, False], 0), 
            (0,1)) # Should raise an exception because top marker does not align
        
def test_rotational_equals() -> None:
    tile = Tile([True, False, False, False, False, False], 0)
    rotationally_equal_tiles = [tile.rotate(n) for n in range(1,6)]
    not_equal_tile = Tile([True, True, False, False, False, False], 0)

    assert all([tile.is_rotationally_equal(t) for t in rotationally_equal_tiles])
    assert tile.is_rotationally_equal(not_equal_tile) == False

def test_single_pop() -> None:
    game_state = GameState()
    center_tile = Tile([True, True, True, True, True, True], 0)
    assert game_state.place_tile(
        center_tile, 
        (0,0)) == []

    bordering_positions = get_bordering_positions((0,0))

    for position in bordering_positions[0:-1]:
        assert game_state.place_tile(
            Tile([True, True, True, True, True, True], 0), 
            position) == []
    
    # Place the last tile, that pops the center
    assert game_state.place_tile(
        Tile([True, True, True, True, True, True], 0), 
        bordering_positions[-1]) == [(0,0)]
    
    assert (0,0) not in game_state.get_available_positions()


def test_cannot_place_tile_in_center() -> None:
    game_state = GameState()
    center_tile = Tile([True, True, True, True, True, True], 0)
    
    assert game_state.place_tile(
            center_tile, 
            (0,0)) == []

    bordering_positions = get_bordering_positions((0,0))

    for position in bordering_positions:
        game_state.place_tile(
            Tile([True, True, True, True, True, True], 0), 
            position)

    with pytest.raises(Exception):
        game_state.place_tile(
            center_tile, 
            (0,0))

def test_one_point_score() -> None:
    game_state = GameState()
    center_tile = Tile([True, True, True, True, True, True], 0)
    
    game_state.place_tile(
            center_tile, 
            (0,0)) 
    game_state.place_tile(
        Tile([True, True, True, True, True, True], 0), 
        (0,-1))
    
    assert game_state.get_scores() == [1,0]

def test_multi_point_score() -> None:
    game_state = GameState()
    center_tile = Tile([True, True, True, True, True, True], 0)
    
    game_state.place_tile(
            center_tile, 
            (0,0)) 
    game_state.place_tile(
        Tile([True, True, True, True, True, True], 0), 
        (0,-1))
    game_state.place_tile(
        Tile([True, True, True, True, True, True], 1), 
        (1,-1))
    game_state.place_tile(
        Tile([True, True, True, True, True, True], 1), 
        (1,0))
    game_state.place_tile(
        Tile([True, True, True, True, True, True], 0), 
        (0,1))
    
    assert game_state.get_scores() == [2,1]

def test_score_pop_full() -> None:
    game_state = GameState()
    center_tile = Tile([True, True, True, True, True, True], 0)
    
    game_state.place_tile(
            center_tile, 
            (0,0))

    borders = get_bordering_positions((0,0))
    color = 0
    for border_tile in borders:    
        game_state.place_tile(
            Tile([True, True, True, True, True, True], color), 
            border_tile)
        color = (color + 1) % 2

    assert game_state.score_pop((0,0), 0) == -3
    assert game_state.score_pop((0,0), 1) == 3

def test_score_pop_partial() -> None:
    game_state = GameState()
    center_tile = Tile([True, True, True, True, True, True], 0)
    
    game_state.place_tile(
            center_tile, 
            (0,0))

    borders = get_bordering_positions((0,0))
    color = 0
    for border_tile in borders:    
        game_state.place_tile(
            Tile([True, True, True, True, True, True], color), 
            border_tile)
        color = (color + 1) % 2

    assert game_state.score_pop((0,0), 0) == -3
    assert game_state.score_pop((0,0), 1) == 3

def test_properly_detected_enclosure() -> None:
    game_state = GameState()
    
    #Place ring of tiles
    ring = [(0,0), (1,-1), (2,-1), (3,-1),
            (3, 0), (2, 1), (1, 1), (0, 1)]
    for r in ring:
        game_state.place_tile(
            Tile([True, True, True, True, True, True], 0),
            r
        )
    
    print("Enclosure checks...")
    assert game_state.is_enclosed((1, 0)) == True
    assert game_state.is_enclosed((2, 0)) == True

    assert game_state.is_enclosed((0, -1)) == False

    with pytest.raises(Exception):
        game_state.place_tile(
            Tile([True, True, True, True, True, True], 0),
            (1,0))


class TestBoardConnectivity:
    """Tests for the would_move_disconnect_board method."""

    def test_single_tile_cannot_disconnect(self):
        """Moving a single tile cannot disconnect the board."""
        gs = GameState()
        tile = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile, (0, 0))

        # Moving the only tile anywhere keeps the board "connected" (single tile)
        assert gs.would_move_disconnect_board((0, 0), (1, 0)) == False

    def test_two_tiles_move_adjacent_stays_connected(self):
        """Moving a tile to stay adjacent keeps the board connected."""
        gs = GameState()
        tile1 = Tile([True, True, True, True, True, True], 0)
        tile2 = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (1, 0))

        # Moving tile2 to a position still adjacent to tile1 stays connected
        assert gs.would_move_disconnect_board((1, 0), (0, 1)) == False

    def test_two_tiles_move_away_disconnects(self):
        """Moving a tile away from the other disconnects the board."""
        gs = GameState()
        tile1 = Tile([True, True, True, True, True, True], 0)
        tile2 = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (1, 0))

        # Moving tile2 far away disconnects
        assert gs.would_move_disconnect_board((1, 0), (5, 5)) == True

    def test_three_tiles_line_middle_away_disconnects(self):
        """Moving the middle tile in a line away disconnects the board."""
        gs = GameState()
        # Place three tiles in a line: (0,0) - (1,0) - (2,0)
        tile1 = Tile([True, True, True, True, True, True], 0)
        tile2 = Tile([True, True, True, True, True, True], 0)
        tile3 = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (1, 0))
        gs.place_tile(tile3, (2, 0))

        # Moving middle tile (1,0) far away disconnects (0,0) from (2,0)
        assert gs.would_move_disconnect_board((1, 0), (0, 5)) == True

    def test_three_tiles_line_middle_to_bridge_stays_connected(self):
        """Moving the middle tile to another bridging position keeps connected."""
        gs = GameState()
        # Place tiles in a bent line where middle tile can move to alternate bridge
        # (0,0) - (1,0) - (1,1)
        # (1,0) is the bridge, and it can move to (0,1) which is adjacent to both
        tile1 = Tile([True, True, True, True, True, True], 0)
        tile2 = Tile([True, True, True, True, True, True], 0)
        tile3 = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (1, 0))
        gs.place_tile(tile3, (1, 1))

        # (0,1) is adjacent to both (0,0) and (1,1) - so moving bridge there keeps connected
        assert gs.would_move_disconnect_board((1, 0), (0, 1)) == False

    def test_three_tiles_triangle_stays_connected(self):
        """Three tiles in a triangle - moving one stays connected."""
        gs = GameState()
        # Place three tiles in a triangle shape
        tile1 = Tile([True, True, True, True, True, True], 0)
        tile2 = Tile([True, True, True, True, True, True], 0)
        tile3 = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (1, 0))
        gs.place_tile(tile3, (0, 1))  # Adjacent to both

        # Moving any tile to another adjacent spot keeps connected
        # Move tile3 to (1, -1) which is adjacent to both remaining tiles
        assert gs.would_move_disconnect_board((0, 1), (1, -1)) == False

    def test_end_tile_can_move_without_disconnecting(self):
        """Moving an end tile of a line doesn't disconnect."""
        gs = GameState()
        # Place three tiles in a line: (0,0) - (1,0) - (2,0)
        tile1 = Tile([True, True, True, True, True, True], 0)
        tile2 = Tile([True, True, True, True, True, True], 0)
        tile3 = Tile([True, True, True, True, True, True], 0)
        gs.place_tile(tile1, (0, 0))
        gs.place_tile(tile2, (1, 0))
        gs.place_tile(tile3, (2, 0))

        # Moving end tile (0,0) to extend the other end keeps connected
        assert gs.would_move_disconnect_board((0, 0), (3, 0)) == False

    def test_bridge_tile_move_to_new_bridge_stays_connected(self):
        """A bridge tile can move to a new bridging position."""
        gs = GameState()
        # Create two groups connected by a bridge:
        # Group 1: (0,0), (0,1)
        # Bridge: (1,0)
        # Group 2: (2,0), (2,1)
        tiles = [
            Tile([True, True, True, True, True, True], 0) for _ in range(5)
        ]
        gs.place_tile(tiles[0], (0, 0))
        gs.place_tile(tiles[1], (0, 1))
        gs.place_tile(tiles[2], (1, 0))  # Bridge
        gs.place_tile(tiles[3], (2, 0))
        gs.place_tile(tiles[4], (2, 1))

        # Moving bridge to (1, 1) which is adjacent to (0,1) and (2,1) stays connected
        assert gs.would_move_disconnect_board((1, 0), (1, 1)) == False

        # Moving bridge far away disconnects
        assert gs.would_move_disconnect_board((1, 0), (5, 5)) == True
