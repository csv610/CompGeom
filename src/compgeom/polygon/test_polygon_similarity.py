
import math
from compgeom.kernel import Point
from compgeom.polygon import Polygon, are_similar

def test_polygon_similarity():
    print("--- Running Polygon Similarity Tests ---")

    # 1. Square - basic cases
    sq1 = Polygon([Point(0,0), Point(1,0), Point(1,1), Point(0,1)])
    sq2 = Polygon([Point(10,10), Point(20,10), Point(20,20), Point(10,20)]) # Translated & Scaled
    sq3 = Polygon([Point(0,0), Point(1,1), Point(0,2), Point(-1,1)]) # Rotated
    sq4 = Polygon([Point(0,1), Point(0,0), Point(1,0), Point(1,1)]) # Reflected (CW)
    sq5 = Polygon([Point(0,0), Point(0,1), Point(1,1), Point(1,0)]) # Different starting point
    
    print(f"Similar squares (translated, scaled): {sq1.is_similar(sq2)}") # True
    print(f"Similar squares (rotated): {sq1.is_similar(sq3)}")           # True
    print(f"Similar squares (reflected/CW): {sq1.is_similar(sq4)}")      # True
    print(f"Similar squares (cyclic shift): {sq1.is_similar(sq5)}")      # True

    # 2. Triangles - reflection and scale
    t1 = Polygon([Point(0,0), Point(2,0), Point(1, 3)])
    t2 = Polygon([Point(0,0), Point(1, 3), Point(2, 0)]) # Reflected
    t3 = Polygon([Point(0,0), Point(4,0), Point(2, 6)]) # Scaled (2x)
    t4 = Polygon([Point(0,0), Point(2,0), Point(1, 4)]) # Different shape
    
    print(f"Similar triangles (reflected): {are_similar(t1, t2)}")       # True
    print(f"Similar triangles (scaled): {are_similar(t1, t3)}")          # True
    print(f"Not similar triangles: {are_similar(t1, t4)}")               # False

    # 3. Concave polygons
    c1 = Polygon([Point(0,0), Point(4,0), Point(4,4), Point(2,2), Point(0,4)])
    c2 = Polygon([Point(0,0), Point(0,4), Point(2,2), Point(4,4), Point(4,0)]) # Reflected
    c3 = Polygon([Point(10,10), Point(14,10), Point(14,14), Point(12,12), Point(10,14)]) # Translated
    
    print(f"Similar concave (reflected): {are_similar(c1, c2)}")         # True
    print(f"Similar concave (translated): {are_similar(c1, c3)}")        # True

    # 4. Edge cases: Different vertex counts
    p_pentagon = Polygon([Point(0,0), Point(2,0), Point(3,1), Point(1,2), Point(-1,1)])
    print(f"Different vertex counts: {are_similar(sq1, p_pentagon)}")    # False

    # 6. Redundant points (Auto-clean)
    p_extra = Polygon([Point(0,0), Point(0.5, 0), Point(1,0), Point(1,1), Point(0,1)]) # Square with extra point
    print(f"Redundant points (auto_clean=True): {sq1.is_similar(p_extra, auto_clean=True)}")   # True
    print(f"Redundant points (auto_clean=False): {sq1.is_similar(p_extra, auto_clean=False)}") # False

    # 7. Reorder to match (using triangle to avoid symmetry ambiguity)
    t1 = Polygon([Point(0,0), Point(10,0), Point(5, 5)]) # Base triangle
    t_shifted = Polygon([Point(5, 5), Point(0,0), Point(10,0)]) # Shifted by 1
    reordered = t1.reorder_to_match(t_shifted)
    print(f"t1 start: {t1.vertices[0]}")
    print(f"reordered start: {reordered[0]}")
    print(f"Reordered to match: {reordered[0] == t1.vertices[0]}")

    print("--- Tests Completed ---")

if __name__ == "__main__":
    test_polygon_similarity()
