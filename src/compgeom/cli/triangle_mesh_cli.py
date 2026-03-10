from __future__ import annotations

from compgeom.cli._shared import demo_points
from compgeom.mesh.delaunay_triangulation import triangulate


def main() -> int:
    points = demo_points()
    triangles, skipped = triangulate(points)
    if skipped:
        print("Skipped Points:")
        for point, reason in skipped:
            print(f"  {point}: {reason}")
    print(f"\nFinal Mesh: {len(triangles)} active triangles constructed.")
    for index, (a, b, c) in enumerate(triangles):
        ids = sorted([a.id, b.id, c.id])
        print(f"Triangle {index:3}: {ids[0]:3}, {ids[1]:3}, {ids[2]:3}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
