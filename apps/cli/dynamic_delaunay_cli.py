from __future__ import annotations

import argparse
from compgeom import Point2D
from compgeom import DynamicDelaunay
from _shared import read_input_lines, parse_points

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a dynamic Delaunay triangulation.")
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

    dt = DynamicDelaunay()
    print("Adding points incrementally...")
    for p in points:
        dt.add_point(p)
    tris = dt.get_triangles()
    print(f"Final Triangulation: {len(tris)} triangles.")
    for triangle in tris:
        print(f"Triangle: {sorted([vertex.id for vertex in triangle])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
