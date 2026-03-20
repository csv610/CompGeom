"""Unit tests for Maximum Overlap of Convex Polygons."""
import pytest
import math
from compgeom.kernel import Point2D
from compgeom.polygon.maximum_overlap import MaximumOverlap

def test_maximum_overlap_identity():
    # Square side 10
    poly = [Point2D(0,0), Point2D(10,0), Point2D(10,10), Point2D(0,10)]
    t, area = MaximumOverlap.solve(poly, poly)
    
    # Best translation should be very close to (0,0)
    assert t.x == pytest.approx(0.0, abs=0.5)
    assert t.y == pytest.approx(0.0, abs=0.5)
    assert area == pytest.approx(100.0, rel=0.01)

def test_maximum_overlap_shifted_squares():
    # P: [0,10]x[0,10]
    p = [Point2D(0,0), Point2D(10,0), Point2D(10,10), Point2D(0,10)]
    # Q: [0,5]x[0,5] (Smaller square)
    q = [Point2D(0,0), Point2D(5,0), Point2D(5,5), Point2D(0,5)]
    
    t, area = MaximumOverlap.solve(p, q)
    
    # Q should be fully inside P for any translation that keeps it within [0,10]^2
    # One such t is (2.5, 2.5) if centroids were aligned.
    # The max area should be 25.0
    assert area == pytest.approx(25.0, rel=0.01)

def test_maximum_overlap_disjoint():
    # P at origin, Q far away
    p = [Point2D(0,0), Point2D(1,0), Point2D(1,1), Point2D(0,1)]
    q = [Point2D(100,100), Point2D(101,100), Point2D(101,101), Point2D(100,101)]
    
    t, area = MaximumOverlap.solve(p, q)
    
    # The algorithm should find the translation that brings Q back to P
    # t ~ (-100, -100)
    assert area == pytest.approx(1.0, rel=0.01)
    assert t.x == pytest.approx(-100.0, abs=0.5)
    assert t.y == pytest.approx(-100.0, abs=0.5)
