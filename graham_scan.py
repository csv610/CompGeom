import sys
from geometry_utils import Point
from polygon_utils import graham_scan

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if not points:
        print("No valid points provided."); return
    hull = graham_scan(points)
    print(f"Convex Hull (Graham Scan) has {len(hull)} vertices:")
    for p in hull: print(f"  ({p.x:.4f}, {p.y:.4f})")

if __name__ == "__main__":
    main()
