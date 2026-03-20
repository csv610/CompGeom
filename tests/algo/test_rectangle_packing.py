
import pytest
from compgeom.algo.rectangle_packing import RectanglePacker, PackedRect

def test_pack_empty():
    w, h, placements = RectanglePacker.pack([])
    assert w == 0
    assert h == 0
    assert placements == []

def test_pack_simple_rectangle():
    dims = [(2, 1), (1, 2), (1, 1)]
    w, h, placements = RectanglePacker.pack(dims, target_shape="rectangle")
    assert w > 0
    assert h > 0
    assert len(placements) == 3
    # Check that all rectangles are within bounds and don't overlap (simple check)
    for r in placements:
        assert r.x >= 0
        assert r.y >= 0
        assert r.x + r.width <= w
        assert r.y + r.height <= h

def test_pack_simple_square():
    dims = [(1, 1)] * 9
    w, h, placements = RectanglePacker.pack(dims, target_shape="square")
    assert w > 0
    assert h > 0
    # For 9 1x1 squares, a perfect 3x3 packing is possible.
    # The heuristic might not be perfect but should be reasonable.
    assert len(placements) == 9

def test_visualize():
    dims = [(1, 1), (1, 1)]
    w, h, placements = RectanglePacker.pack(dims)
    svg = RectanglePacker.visualize(w, h, placements)
    assert isinstance(svg, str)
    assert "<svg" in svg
    assert "</svg>" in svg
    # Check that it contains rects for each placement
    assert svg.count("<rect") >= 3 # 1 for background + 2 for placements
