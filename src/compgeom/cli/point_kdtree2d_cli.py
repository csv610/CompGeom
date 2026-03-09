import sys
from compgeom import Point
from compgeom import build_kdtree, display_kdtree

def main():
    points = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) >= 2:
            try: points.append(Point(float(parts[0]), float(parts[1]), len(points)))
            except ValueError: continue
    if not points:
        print("No valid points provided."); return
    root = build_kdtree(points)
    print(f"2D KD-Tree built with {len(points)} points.\n")
    display_kdtree(root)

if __name__ == "__main__":
    main()
