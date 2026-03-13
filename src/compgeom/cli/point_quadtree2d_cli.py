from __future__ import annotations

import argparse

from compgeom import PointQuadtree
from compgeom.cli._shared import demo_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a 2D point quadtree from demo points.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in point cloud.")
    args = parser.parse_args(argv)
    points = demo_points()
    qt = PointQuadtree()
    for point in points:
        qt.insert(point)
    print(f"Point Quadtree built with {qt.count} points.\n")
    qt.display()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
