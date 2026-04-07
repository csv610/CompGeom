from __future__ import annotations

import argparse
from compgeom import PointQuadtree
from _shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a 2D point quadtree.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1
        
    qt = PointQuadtree()
    for point in points:
        qt.insert(point)
    print(f"Point Quadtree built with {qt.count} points.\n")
    qt.display()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
