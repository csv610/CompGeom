from compgeom.kernel import Point2D
from compgeom.polygon import (
    generate_koch_snowflake, 
    generate_dragon_curve, 
    generate_de_rham_curve
)

def test_fractals():
    # 1. Koch Snowflake
    # Depth 0: 3 segments (3 points for the triangle)
    # Each segment is replaced by 4 segments.
    # Depth 2: 3 * 4^2 = 48 segments -> 48 points
    ks2 = generate_koch_snowflake(depth=2)
    assert len(ks2) == 48
    
    # 2. Dragon Curve
    # Points = 2^depth + 1
    # Depth 10: 2^10 + 1 = 1025 points
    dc10 = generate_dragon_curve(depth=10)
    assert len(dc10) == 1025
    
    # 3. De Rham Curve (Lévy C curve using w=0.5 + 0.5j)
    # Points = 2^depth + 1
    # Depth 5: 2^5 + 1 = 33 points
    levy5 = generate_de_rham_curve(depth=5, w=complex(0.5, 0.5))
    assert len(levy5) == 33

if __name__ == "__main__":
    test_fractals()
