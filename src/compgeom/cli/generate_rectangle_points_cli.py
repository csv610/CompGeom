from __future__ import annotations

from compgeom.algo.points_sampling import PointSampler


def main() -> int:
    width, height = 6.0, 4.0
    n_points = 100

    points = PointSampler.in_rectangle(width, height, n_points)
    print(
        f"Generated {len(points)} points in rectangle centered at (0.0000, 0.0000), "
        f"width {width:.4f}, height {height:.4f}:"
    )
    for point in points:
        print(f"  ({point.x:.6f}, {point.y:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
