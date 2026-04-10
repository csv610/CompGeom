from __future__ import annotations

import argparse
from compgeom import get_polygon_properties
from ._shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute properties of a polygon.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No polygon provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse polygon from input.")
        return 1
        
    area, centroid, orientation = get_polygon_properties(points)
    print(f"Polygon Properties:")
    print(f"  Area:        {area:.4f}")
    print(f"  Centroid:    ({centroid.x:.4f}, {centroid.y:.4f})")
    print(f"  Orientation: {orientation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
