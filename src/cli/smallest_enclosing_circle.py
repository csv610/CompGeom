import sys
import random
from geometry_utils import Point
from proximity_utils import welzl

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1])))
            except ValueError: continue
    if not points: return
    random.shuffle(points)
    center, radius = welzl(list(points), [])
    print(f"Smallest Enclosing Circle:\n  Center: ({center.x:.6f}, {center.y:.6f})\n  Radius: {radius:.6f}")

if __name__ == "__main__":
    main()
