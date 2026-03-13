
import math
from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_symmetry import orient_polygon_for_symmetry, get_moments

def validate_symmetry(name, poly):
    print(f"\n--- Testing {name} ---")
    oriented = orient_polygon_for_symmetry(poly)
    
    # 1. Check Centroid
    props = oriented.properties()
    print(f"Centroid: ({props.centroid.x:.4e}, {props.centroid.y:.4e})")
    assert abs(props.centroid.x) < 1e-9
    assert abs(props.centroid.y) < 1e-9
    
    # 2. Check Ixy (should be near 0 for principal axis alignment)
    _, ix, iy, ixy = get_moments(oriented.as_list())
    print(f"Ixy (Product of Inertia): {ixy:.4e}")
    print(f"Ix: {ix:.4e}, Iy: {iy:.4e}")
    
    # Ixy should be significantly smaller than the moments of inertia
    assert abs(ixy) < 1e-9 or abs(ixy) / max(ix, iy) < 1e-7

def test_convex_shapes():
    # Test 1: Rectangle (Already symmetric)
    rect = Polygon([Point2D(0,0), Point2D(2,0), Point2D(2,1), Point2D(0,1)])
    validate_symmetry("Rectangle", rect)
    
    # Test 2: Right Triangle
    tri = Polygon([Point2D(0,0), Point2D(10,0), Point2D(0,5)])
    validate_symmetry("Right Triangle", tri)
    
    # Test 3: Random Convex Polygon
    # Using the factory method from the codebase
    random_convex = Polygon.from_random_convex(num_points=12, x_range=(0, 100), y_range=(0, 100))
    validate_symmetry("Random Convex", random_convex)

if __name__ == "__main__":
    test_convex_shapes()
    print("\nAll convex symmetry tests passed!")
