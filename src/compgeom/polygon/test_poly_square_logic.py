import math
from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.poly_square import poly_square

def test_poly_square_functional():
    # A rectangle rotated by 45 degrees
    s2 = math.sqrt(2) / 2
    vertices = [
        Point2D(0, 0),
        Point2D(s2, s2),
        Point2D(0, 2 * s2),
        Point2D(-s2, s2)
    ]
    
    # Orient segment 0: (0,0) -> (s2, s2)
    # The segment angle is 45 degrees (pi/4).
    # target_angle = round(pi/4 / (pi/2)) * (pi/2) = round(0.5) * pi/2 = 0.
    # So it should rotate by -45 degrees.
    squared = poly_square(vertices, 0)
    
    p1, p2 = squared[0], squared[1]
    angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
    assert math.isclose(angle, 0, abs_tol=1e-7)
    
    # Orient segment 0 to 90 degrees by choosing a different segment or target.
    # If we take segment 1: (s2, s2) -> (0, 2*s2), angle is 135 degrees (3pi/4).
    # target_angle = round(1.5) * pi/2 = 2 * pi/2 = pi (180 deg).
    squared_v2 = poly_square(vertices, 1)
    p1, p2 = squared_v2[1], squared_v2[2]
    angle_v2 = math.atan2(p2.y - p1.y, p2.x - p1.x)
    assert math.isclose(angle_v2, math.pi, abs_tol=1e-7)

def test_polygon_method_poly_square():
    vertices = [
        Point2D(0, 0),
        Point2D(1, 1),
        Point2D(0, 2)
    ]
    poly = Polygon(vertices)
    
    # Method call
    squared_poly = poly.poly_square(0)
    assert isinstance(squared_poly, Polygon)
    
    p1, p2 = squared_poly[0], squared_poly[1]
    angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
    assert math.isclose(angle % (math.pi / 2), 0, abs_tol=1e-7)

def test_polygon_method_alias():
    vertices = [
        Point2D(0, 0),
        Point2D(1, 1),
        Point2D(0, 2)
    ]
    poly = Polygon(vertices)
    
    # Alias call
    squared_poly = poly.orient_to_cardinal(0)
    
    p1, p2 = squared_poly[0], squared_poly[1]
    angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
    assert math.isclose(angle % (math.pi / 2), 0, abs_tol=1e-7)

if __name__ == "__main__":
    test_poly_square_functional()
    test_polygon_method_poly_square()
    test_polygon_method_alias()
    print("All poly_square tests passed!")
