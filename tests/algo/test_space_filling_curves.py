
import pytest
from compgeom.algo.space_filling_curves import SpaceFillingCurves

def is_neighbor(idx1, idx2, width):
    x1, y1 = idx1 % width, idx1 // width
    x2, y2 = idx2 % width, idx2 // width
    return abs(x1 - x2) + abs(y1 - y2) == 1

def test_hilbert():
    order = 3
    width = 2**order
    indices = SpaceFillingCurves.hilbert(order)
    assert len(indices) == width * width
    assert len(set(indices)) == width * width
    # Successive points must be neighbors
    for i in range(len(indices) - 1):
        assert is_neighbor(indices[i], indices[i+1], width)

def test_peano():
    level = 2
    width = 3**level
    indices = SpaceFillingCurves.peano(level)
    assert len(indices) == width * width
    assert len(set(indices)) == width * width
    # Successive points must be neighbors
    for i in range(len(indices) - 1):
        assert is_neighbor(indices[i], indices[i+1], width)

def test_morton():
    level = 3
    width = 2**level
    indices = SpaceFillingCurves.morton(level)
    assert len(indices) == width * width
    assert len(set(indices)) == width * width

def test_zigzag():
    width, height = 4, 5
    indices = SpaceFillingCurves.zigzag(width, height)
    assert len(indices) == width * height
    assert len(set(indices)) == width * height

def test_sweep():
    width, height = 10, 10
    indices = SpaceFillingCurves.sweep(width, height)
    assert len(indices) == width * height
    assert len(set(indices)) == width * height
    # Sweep is continuous
    for i in range(len(indices) - 1):
        assert is_neighbor(indices[i], indices[i+1], width)

def test_visualize_mock():
    # We can't easily test SVG output, but we can check it returns a string
    indices = SpaceFillingCurves.sweep(2, 2)
    svg = SpaceFillingCurves.visualize(indices, 2, 2)
    assert isinstance(svg, str)
    assert "<svg" in svg
