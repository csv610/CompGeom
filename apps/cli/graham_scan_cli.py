from __future__ import annotations

import argparse
from ._shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.polygon.convex_hull import GrahamScan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the convex hull of a point set.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--visualize", action="store_true", help="Visualize the convex hull using pyvista.")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1

    hull = GrahamScan().generate(points)
    print(f"Convex Hull (Graham Scan) has {len(hull)} vertices:")
    for point in hull:
        print(f"  ({point.x:.4f}, {point.y:.4f})")
        
    if args.visualize:
        visualize_with_pyvista(points=points, polygons=[hull])
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
