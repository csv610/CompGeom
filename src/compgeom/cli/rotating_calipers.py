import sys
from compgeom.geometry import Point
from compgeom.proximity import farthest_pair

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if not points: return
    dist, (p1, p2) = farthest_pair(points)
    print(f"Farthest Pair (Diameter): {p1} and {p2}\nMaximum Distance:         {dist:.6f}")

if __name__ == "__main__":
    main()
