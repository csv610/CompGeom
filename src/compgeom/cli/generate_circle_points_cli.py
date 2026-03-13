from __future__ import annotations

import argparse

from compgeom.cli._shared import demo_points
from compgeom.algo.points_sampling import PointSampler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate random points inside a circle.")
    parser.add_argument("--radius", type=float, default=2.5, help="Circle radius.")
    parser.add_argument("--count", type=int, default=100, help="Number of points to generate.")
    args = parser.parse_args(argv)

    center = demo_points()[0]
    x, y, radius = center.x, center.y, args.radius
    n_points = args.count

    points = PointSampler.in_circle(center, radius, n_points)
    print(f"Generated {len(points)} points in circle centered at ({x:.4f}, {y:.4f}) with radius {radius:.4f}:")
    for point in points:
        print(f"  ({point.x:.6f}, {point.y:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
