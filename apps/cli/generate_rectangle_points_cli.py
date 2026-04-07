from __future__ import annotations

import argparse

from compgeom.algo.points_sampling import PointSampler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate random points inside a rectangle.")
    parser.add_argument("--width", type=float, default=6.0, help="Rectangle width.")
    parser.add_argument("--height", type=float, default=4.0, help="Rectangle height.")
    parser.add_argument("--count", type=int, default=100, help="Number of points to generate.")
    args = parser.parse_args(argv)

    width, height = args.width, args.height
    n_points = args.count

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
