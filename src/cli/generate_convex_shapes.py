import sys
from polygon_utils import generate_random_convex_polygon

def main():
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20
    hull = generate_random_convex_polygon(num_samples)
    print(f"Generated Random Convex Polygon with {len(hull)} vertices:")
    for p in hull: print(f"{p.x:.4f} {p.y:.4f}")

if __name__ == "__main__":
    main()
