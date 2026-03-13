import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.distance_map import DistanceMapSolver

def test_distance_map_solver_basic():
    # A simple square polygon
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    grid, extent = DistanceMapSolver.solve(poly, resolution=10)
    
    assert len(grid) > 0
    assert len(grid[0]) > 0
    # Check that distances are non-negative
    for row in grid:
        for val in row:
            assert val >= 0

def test_distance_map_solver_empty():
    grid, extent = DistanceMapSolver.solve([])
    assert grid == [[]]
    assert extent == (0, 0, 0, 0)

def test_distance_map_visualize():
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    grid, extent = DistanceMapSolver.solve(poly, resolution=5)
    svg = DistanceMapSolver.visualize_svg(grid, extent)
    assert "<svg" in svg
    assert "</svg>" in svg
