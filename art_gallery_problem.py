import sys
from geometry_utils import Point
from polygon_utils import solve_art_gallery

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if len(points) < 3:
        print("Need at least 3 points for a polygon."); return
    guards = solve_art_gallery(points)
    print(f"Placed {len(guards)} guards (n={len(points)}):")
    for g in guards: print(f"Guard at {g}")

if __name__ == "__main__":
    main()
