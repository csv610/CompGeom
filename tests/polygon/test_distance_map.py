import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.distance_map import solve_distance_map, visualize_distance_map_svg

def test_distance_map_solver_basic():
    # A simple square polygon
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    grid, extent = solve_distance_map(poly, resolution=10)
    
    assert len(grid) > 0
    assert len(grid[0]) > 0
    # Check that distances are non-negative
    for row in grid:
        for val in row:
            assert val >= 0

def test_distance_map_solver_empty():
    grid, extent = solve_distance_map([])
    assert grid == [[]]
    assert extent == (0, 0, 0, 0)

def test_distance_map_visualize():
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    grid, extent = solve_distance_map(poly, resolution=5)
    svg = visualize_distance_map_svg(grid, extent)
    assert "<svg" in svg
    assert "</svg>" in svg
