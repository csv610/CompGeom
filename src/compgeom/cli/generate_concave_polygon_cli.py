from __future__ import annotations

import argparse
import meshio
from compgeom.polygon import generate_concave_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate concave polygons.")
    parser.add_argument(
        "-n", "--num_points", type=int, default=15, help="Number of vertices"
    )
    parser.add_argument(
        "-o", "--output", default="concave_polygon.off", help="Output polygon file"
    )
    args = parser.parse_args(argv)

    print(f"Generating random concave polygon with {args.num_points} vertices...")

    poly = generate_concave_polygon(args.num_points)

    to_file(args.output, poly)


if __name__ == "__main__":
    raise SystemExit(main())
