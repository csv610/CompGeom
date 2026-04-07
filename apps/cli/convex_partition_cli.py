from __future__ import annotations

import argparse

from compgeom.polygon import convex_decompose_polygon
from _shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Partition a polygon into convex pieces."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1

    mesh = convex_decompose_polygon(points)
    pieces = [[mesh.vertices[idx] for idx in face] for face in mesh.faces]
    print(f"Polygon partitioned into {len(pieces)} convex pieces.")
    for index, partition in enumerate(pieces):
        print(f"Partition {index}: {[v.id for v in partition]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
