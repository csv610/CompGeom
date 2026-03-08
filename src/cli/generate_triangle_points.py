import sys
from geometry_utils import Point
from polygon_utils import generate_points_in_triangle

def main():
    lines = sys.stdin.readlines()
    if len(lines) < 3: return
    try:
        pts = [Point(float(lines[i].split()[0]), float(lines[i].split()[1])) for i in range(3)]
        n = int(lines[3].strip()) if len(lines) > 3 else 100
    except (ValueError, IndexError): return
    triangle_points = generate_points_in_triangle(pts[0], pts[1], pts[2], n)
    print(f"Generated {n} uniform points in triangle {pts[0]}, {pts[1]}, {pts[2]}:")
    for p in triangle_points: print(f"{p.x:.6f} {p.y:.6f}")

if __name__ == "__main__":
    main()
