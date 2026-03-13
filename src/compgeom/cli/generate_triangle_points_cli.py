from __future__ import annotations

import argparse

from compgeom.cli._shared import demo_points
from compgeom.algo.points_sampling import PointSampler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate random points inside a demo triangle.")
    parser.add_argument("--count", type=int, default=100, help="Number of points to generate.")
    args = parser.parse_args(argv)

    pts = demo_points()[:3]
    n = args.count
    triangle_points = PointSampler.in_triangle(pts[0], pts[1], pts[2], n)
    print(f"Generated {n} uniform points in triangle {pts[0]}, {pts[1]}, {pts[2]}:")
    for point in triangle_points:
        print(f"{point.x:.6f} {point.y:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
