from __future__ import annotations

from compgeom.cli._shared import demo_points
from compgeom.algo.points_sampling import PointSampler


def main() -> int:
    center = demo_points()[0]
    x, y, radius = center.x, center.y, 2.5
    n_points = 100

    points = PointSampler.in_circle(center, radius, n_points)
    print(f"Generated {len(points)} points in circle centered at ({x:.4f}, {y:.4f}) with radius {radius:.4f}:")
    for point in points:
        print(f"  ({point.x:.6f}, {point.y:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
