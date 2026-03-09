import sys
from compgeom.geometry import Point
from compgeom.polygon import hertel_mehlhorn

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if len(points) < 3: return
    partitions, polygon = hertel_mehlhorn(points)
    print(f"Polygon partitioned into {len(partitions)} convex pieces.")
    for i, part in enumerate(partitions): print(f"Partition {i}: {sorted(part)}")

if __name__ == "__main__":
    main()
