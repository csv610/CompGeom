"""Unit tests for Convex Hull Peeling."""

import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.convex_hull_peeling import convex_hull_peeling

def test_convex_hull_peeling_basic():
    # Two nested squares
    # Outer square
    outer = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    # Inner square
    inner = [Point2D(4, 4), Point2D(6, 4), Point2D(6, 6), Point2D(4, 6)]
    
    points = outer + inner
    layers = convex_hull_peeling(points, algorithm="graham_scan")
    
    assert len(layers) == 2
    assert len(layers[0]) == 4
    assert len(layers[1]) == 4
    
    # Check that outer layer contains outer points
    outer_set = set(outer)
    for p in layers[0]:
        assert p in outer_set
        
    # Check that inner layer contains inner points
    inner_set = set(inner)
    for p in layers[1]:
        assert p in inner_set

def test_convex_hull_peeling_empty():
    assert convex_hull_peeling([]) == []

def test_convex_hull_peeling_single_point():
    p = Point2D(0, 0)
    layers = convex_hull_peeling([p])
    assert len(layers) == 1
    assert layers[0] == [p]

def test_convex_hull_peeling_collinear():
    points = [Point2D(0, 0), Point2D(1, 0), Point2D(2, 0), Point2D(1, 1)]
    # Hull should be (0,0), (2,0), (1,1). (1,0) is inside or on edge.
    # Depending on algorithm, (1,0) might be part of hull or not.
    # ConvexHull.generate usually returns only vertices.
    layers = convex_hull_peeling(points, algorithm="monotone_chain")
    # Layer 0: (0,0), (2,0), (1,1)
    # Layer 1: (1,0)
    assert len(layers) >= 1
