import sys
from polygon_utils import generate_simple_polygon, is_convex

def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20
    for _ in range(10):
        polygon = generate_simple_polygon(n_samples)
        if not is_convex(polygon): break
    print(f"Generated Random Simple Polygon ({'Concave' if not is_convex(polygon) else 'Convex'}) with {len(polygon)} vertices:")
    for p in polygon: print(f"{p.x:.4f} {p.y:.4f}")

if __name__ == "__main__":
    main()
