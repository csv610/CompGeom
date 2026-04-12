from __future__ import annotations

import argparse
from compgeom import build_kdtree, display_kdtree
from .._shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a 2D KD-tree.")
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
        
    root = build_kdtree(points)
    print(f"2D KD-Tree built with {len(points)} points.\n")
    display_kdtree(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
