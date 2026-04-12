from __future__ import annotations

import argparse
from .._shared import read_input_lines, parse_points
from compgeom.algo.points_sampling import PointSampler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate random points inside a triangle.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--count", type=int, default=100, help="Number of points to generate.")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input points provided. Provide 3 vertices of a triangle.")
        return 1
    pts = parse_points(lines)
    if len(pts) < 3:
        print("Error: At least 3 vertices are required to define a triangle.")
        return 1

    n = args.count
    triangle_points = PointSampler.in_triangle(pts[0], pts[1], pts[2], n)
    print(f"Generated {n} uniform points in triangle {pts[0]}, {pts[1]}, {pts[2]}:")
    for point in triangle_points:
        print(f"{point.x:.6f} {point.y:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
