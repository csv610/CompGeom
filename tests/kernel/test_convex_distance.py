from compgeom.kernel import Point2D
from compgeom.cli.convex_polygon_distance_cli import _polygon_distance

def test_polygon_distance_disjoint():
    poly1 = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
    poly2 = [Point2D(5, 0), Point2D(7, 0), Point2D(7, 2), Point2D(5, 2)]
    
    dist = _polygon_distance(poly1, poly2)
    assert dist == 3.0

def test_polygon_distance_intersecting():
    poly1 = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
    poly2 = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
    
    dist = _polygon_distance(poly1, poly2)
    assert dist == 0.0

def test_polygon_distance_contained():
    poly1 = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
    poly2 = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
    
    dist = _polygon_distance(poly1, poly2)
    assert dist == 0.0

def test_polygon_distance_touching():
    poly1 = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
    poly2 = [Point2D(2, 0), Point2D(4, 0), Point2D(4, 2), Point2D(2, 2)]
    
    dist = _polygon_distance(poly1, poly2)
    assert dist == 0.0
