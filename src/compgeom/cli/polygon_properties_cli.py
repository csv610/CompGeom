import sys
from compgeom import Point
from compgeom import get_polygon_properties

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1])))
            except ValueError: continue
    if len(points) < 3:
        print("Need at least 3 points."); return
    area, centroid, orientation = get_polygon_properties(points)
    print(f"Polygon Properties:\n  Area:        {area:.4f}\n  Centroid:    ({centroid.x:.4f}, {centroid.y:.4f})\n  Orientation: {orientation}")

if __name__ == "__main__":
    main()
