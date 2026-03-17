
from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_sampling import sample_polygon_boundary, get_parametric_coordinate

def test_sampling():
    # Square (0,0) to (2,2)
    # Perimeter = 8
    poly = Polygon([Point2D(0,0), Point2D(2,0), Point2D(2,2), Point2D(0,2)])
    
    # 1. Test basic uniform sampling
    samples = sample_polygon_boundary(poly, 8)
    print("--- Basic 8 samples (Square) ---")
    for p, t in samples:
        print(f"P({p.x}, {p.y}), t={t:.3f}")
    
    # Expected points: (0,0), (1,0), (2,0), (2,1), (2,2), (1,2), (0,2), (0,1)
    # with t = 0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875
    
    # 2. Test fixed nodes
    fixed = [Point2D(1.5, 0.0), Point2D(2.0, 1.5)]
    samples_fixed = sample_polygon_boundary(poly, 4, fixed_nodes=fixed)
    print("\n--- 4 samples + 2 fixed nodes ---")
    for p, t in samples_fixed:
        print(f"P({p.x}, {p.y}), t={t:.3f}")

    # 3. Test parametric coordinate
    t_fixed = get_parametric_coordinate(poly.vertices, Point2D(2, 1))
    print(f"\nParametric coordinate of (2,1): {t_fixed}") # Should be 3/8 = 0.375

if __name__ == "__main__":
    test_sampling()
