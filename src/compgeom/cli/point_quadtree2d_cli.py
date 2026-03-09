import sys
from compgeom import Point
from compgeom import PointQuadtree

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if not points:
        print("No valid points provided."); return
    qt = PointQuadtree()
    for p in points: qt.insert(p)
    print(f"Point Quadtree built with {qt.count} points.\n")
    qt.display()

if __name__ == "__main__":
    main()
