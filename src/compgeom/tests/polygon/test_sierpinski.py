from compgeom.kernel import Point2D
from compgeom.polygon import generate_sierpinski_triangle

def test_sierpinski():
    # Depth 0 should be just one triangle
    triangles_d0 = generate_sierpinski_triangle(depth=0)
    assert len(triangles_d0) == 1
    
    # Depth 1 should be three triangles
    triangles_d1 = generate_sierpinski_triangle(depth=1)
    assert len(triangles_d1) == 3
    
    # Depth 3 should be 3^3 = 27 triangles
    triangles_d3 = generate_sierpinski_triangle(depth=3)
    assert len(triangles_d3) == 27
    
    # Check first triangle of depth 1
    # Initial vertices (0,0), (100,0), (50, 86.6)
    t = triangles_d1[0]
    # One of the corners should be (0,0)
    assert any(p.x == 0 and p.y == 0 for p in t)

if __name__ == "__main__":
    test_sierpinski()
