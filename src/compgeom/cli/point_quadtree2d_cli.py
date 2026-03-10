from __future__ import annotations

from compgeom import PointQuadtree
from compgeom.cli._shared import demo_points


def main() -> int:
    points = demo_points()
    qt = PointQuadtree()
    for point in points:
        qt.insert(point)
    print(f"Point Quadtree built with {qt.count} points.\n")
    qt.display()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
