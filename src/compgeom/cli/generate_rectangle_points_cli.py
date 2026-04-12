from __future__ import annotations

import argparse

from compgeom.algo.points_sampling import PointSampler
from compgeom.mesh import to_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate random points inside a rectangle."
    )
    parser.add_argument(
        "-w", "--width", type=float, default=1.0, help="Rectangle width."
    )
    parser.add_argument("--height", type=float, default=1.0, help="Rectangle height.")
    parser.add_argument(
        "--count", type=int, default=100, help="Number of points to generate."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default="rectangle_points.off",
        help="Path to output file.",
    )
    args = parser.parse_args(argv)

    width, height = args.width, args.height
    n_points = args.count

    points = PointSampler.in_rectangle(width, height, n_points)

    to_file(args.output, points, faces=[])
    print(f"Wrote {len(points)} points to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
