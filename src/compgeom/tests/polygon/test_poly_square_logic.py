import pytest
import math
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, poly_square

def test_poly_square_functional():
    vertices = [
        Point2D(0, 0),
        Point2D(1, 1),
        Point2D(0, 2)
    ]
    squared_0 = poly_square(vertices, 0)
    squared_1 = poly_square(vertices, 1)
    
    assert len(squared_0) == 3
    assert len(squared_1) == 3
    assert squared_0 != squared_1

def test_poly_square_symmetry():
    # Square at 45 degrees
    s = math.sqrt(2)/2
    # Vertices: (s,s), (-s,s), (-s,-s), (s,-s)
    # Segment 0: (s,s) -> (-s,s) is horizontal (angle pi)
    # Actually, let's use a different square
    vertices = [Point2D(1, 0), Point2D(0, 1), Point2D(-1, 0), Point2D(0, -1)]
    # Segment 0: (1,0) -> (0,1) angle is 3pi/4 (135 deg)
    
    # poly_square(..., 0) should rotate it to align segment 0 (135 deg) to 90 or 180.
    # Nearest cardinal to 135 is 90 or 180. 
    # Target 90 (pi/2): rotation = -45 deg. (1,0) rotates to (s, -s)
    # Target 180 (pi): rotation = +45 deg. (1,0) rotates to (s, s)
    
    squared = poly_square(vertices, 0)
    
    # After squaring, at least one segment should be horizontal or vertical.
    # Check if any segment is horizontal or vertical.
    found_cardinal = False
    for i in range(len(squared)):
        p1, p2 = squared[i], squared[(i+1)%len(squared)]
        if abs(p1.x - p2.x) < 1e-7 or abs(p1.y - p2.y) < 1e-7:
            found_cardinal = True
            break
    assert found_cardinal

def test_poly_square_invalid_index():
    vertices = [Point2D(0,0), Point2D(1,0), Point2D(0,1)]
    with pytest.raises(IndexError):
        poly_square(vertices, 100)
