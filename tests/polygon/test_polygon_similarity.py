import math
import pytest
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, polygons_are_similar, reorder_to_match

def test_polygon_similarity():
    # 1. Square - basic cases
    sq1 = Polygon([Point2D(0,0), Point2D(1,0), Point2D(1,1), Point2D(0,1)])
    sq2 = Polygon([Point2D(10,10), Point2D(20,10), Point2D(20,20), Point2D(10,20)]) # Translated & Scaled
    sq3 = Polygon([Point2D(0,0), Point2D(1,1), Point2D(0,2), Point2D(-1,1)]) # Rotated
    sq4 = Polygon([Point2D(0,1), Point2D(0,0), Point2D(1,0), Point2D(1,1)]) # Reflected (CW)
    sq5 = Polygon([Point2D(0,0), Point2D(0,1), Point2D(1,1), Point2D(1,0)]) # Different starting point
    
    assert polygons_are_similar(sq1, sq2) is True
    assert polygons_are_similar(sq1, sq3) is True
    assert polygons_are_similar(sq1, sq4) is True
    assert polygons_are_similar(sq1, sq5) is True

    # 2. Triangles - reflection and scale
    t1 = Polygon([Point2D(0,0), Point2D(2,0), Point2D(1, 3)])
    t2 = Polygon([Point2D(0,0), Point2D(1, 3), Point2D(2, 0)]) # Reflected
    t3 = Polygon([Point2D(0,0), Point2D(4,0), Point2D(2, 6)]) # Scaled (2x)
    t4 = Polygon([Point2D(0,0), Point2D(2,0), Point2D(1, 4)]) # Different shape
    
    assert polygons_are_similar(t1, t2) is True
    assert polygons_are_similar(t1, t3) is True
    assert polygons_are_similar(t1, t4) is False

    # 3. Concave polygons
    c1 = Polygon([Point2D(0,0), Point2D(4,0), Point2D(4,4), Point2D(2,2), Point2D(0,4)])
    c2 = Polygon([Point2D(0,0), Point2D(0,4), Point2D(2,2), Point2D(4,4), Point2D(4,0)]) # Reflected
    c3 = Polygon([Point2D(10,10), Point2D(14,10), Point2D(14,14), Point2D(12,12), Point2D(10,14)]) # Translated
    
    assert polygons_are_similar(c1, c2) is True
    assert polygons_are_similar(c1, c3) is True

    # 4. Edge cases: Different vertex counts
    p_pentagon = Polygon([Point2D(0,0), Point2D(2,0), Point2D(3,1), Point2D(1,2), Point2D(-1,1)])
    assert polygons_are_similar(sq1, p_pentagon) is False

    # 6. Redundant points (Auto-clean)
    p_extra = Polygon([Point2D(0,0), Point2D(0.5, 0), Point2D(1,0), Point2D(1,1), Point2D(0,1)]) # Square with extra point
    assert polygons_are_similar(sq1, p_extra, auto_clean=True) is True
    assert polygons_are_similar(sq1, p_extra, auto_clean=False) is False

    # 7. Reorder to match (using triangle to avoid symmetry ambiguity)
    t1 = Polygon([Point2D(0,0), Point2D(10,0), Point2D(5, 5)]) # Base triangle
    t_shifted = Polygon([Point2D(5, 5), Point2D(0,0), Point2D(10,0)]) # Shifted by 1
    reordered = reorder_to_match(t1, t_shifted)
    # The first point of reordered should match the first point of t1
    assert reordered[0].x == t1.vertices[0].x
    assert reordered[0].y == t1.vertices[0].y

if __name__ == "__main__":
    test_polygon_similarity()
