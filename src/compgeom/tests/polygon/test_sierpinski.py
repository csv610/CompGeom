
from compgeom.kernel import Point2D
from compgeom.polygon import PolygonGenerator

def test_sierpinski():
    print("--- Running Sierpinski Triangle Test ---")
    
    # Depth 0 should be just one triangle
    triangles_d0 = PolygonGenerator.sierpinski_triangle(depth=0)
    print(f"Depth 0: {len(triangles_d0)} triangle") # Expected 1
    
    # Depth 1 should be three triangles
    triangles_d1 = PolygonGenerator.sierpinski_triangle(depth=1)
    print(f"Depth 1: {len(triangles_d1)} triangles") # Expected 3
    
    # Depth 3 should be 3^3 = 27 triangles
    triangles_d3 = PolygonGenerator.sierpinski_triangle(depth=3)
    print(f"Depth 3: {len(triangles_d3)} triangles") # Expected 27
    
    # Check first triangle of depth 1
    # Initial: (0,0), (100,0), (50, 86.6)
    # Midpoints: (50,0), (75, 43.3), (25, 43.3)
    # First sub-triangle: (0,0), (50,0), (25, 43.3)
    t = triangles_d1[0]
    print(f"First triangle V0: {t[0]}") # Expected P(0,0)
    print(f"First triangle V1: {t[1]}") # Expected P(50,0)
    print(f"First triangle V2: {t[2]}") # Expected P(25, 43.3)

    print("--- Test Completed ---")

if __name__ == "__main__":
    test_sierpinski()
