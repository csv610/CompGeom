
from compgeom.kernel import Point2D
from compgeom.polygon import PolygonGenerator

def test_fractals():
    print("--- Running Fractal Curve Tests ---")
    
    # 1. Koch Snowflake
    # Depth 0: 3 points (triangle)
    # Each depth multiplies edge count by 4
    # Depth 1: 3 * 4 = 12 points
    # Depth 2: 3 * 4 * 4 = 48 points
    ks2 = PolygonGenerator.koch_snowflake(depth=2)
    print(f"Koch Snowflake (depth 2): {len(ks2)} points") # Expected 48
    
    # 2. Dragon Curve
    # Points = 2^depth + 1
    # Depth 1: 3 points
    # Depth 10: 1025 points
    dc10 = PolygonGenerator.dragon_curve(depth=10)
    print(f"Dragon Curve (depth 10): {len(dc10)} points") # Expected 1025
    
    # 3. De Rham Curve (Lévy C curve using w=0.5 + 0.5j)
    # Points = 2^depth + 1
    levy5 = PolygonGenerator.de_rham_curve(depth=5, w=complex(0.5, 0.5))
    print(f"Lévy C Curve (depth 5): {len(levy5)} points") # Expected 33

    print("--- Test Completed ---")

if __name__ == "__main__":
    test_fractals()
