import sys
from compgeom.geometry import Point
from compgeom.triangulation import triangulate

def main():
    points = []
    lines = sys.stdin.readlines()
    if not lines: return
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            try:
                x, y = float(parts[0]), float(parts[1])
                points.append(Point(x, y, len(points)))
            except ValueError: continue
    triangles, skipped = triangulate(points)
    if skipped:
        print("Skipped Points:")
        for p, reason in skipped: print(f"  {p}: {reason}")
    print(f"\nFinal Mesh: {len(triangles)} active triangles constructed.")
    for i, (a, b, c) in enumerate(triangles):
        ids = sorted([a.id, b.id, c.id])
        print(f"Triangle {i:3}: {ids[0]:3}, {ids[1]:3}, {ids[2]:3}")

if __name__ == "__main__":
    main()
