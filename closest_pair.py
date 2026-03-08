import sys
from geometry_utils import Point
from proximity_utils import closest_pair

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if len(points) < 2:
        print("Need at least 2 points."); return
    dist, (p1, p2) = closest_pair(points)
    print(f"Closest Pair: {p1} and {p2}\nDistance:     {dist:.6f}")

if __name__ == "__main__":
    main()
