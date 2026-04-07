from __future__ import annotations

import argparse
import random
from compgeom import Point2D, welzl
from _shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the smallest enclosing circle for 2D points."
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

    # Welzl's algorithm is sensitive to order; shuffle for expected O(n) performance
    random.shuffle(points)
    center, radius = welzl(list(points), [])
    
    print(f"Smallest Enclosing Circle:")
    print(f"  Center: ({center.x:.6f}, {center.y:.6f})")
    print(f"  Radius: {radius:.6f}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
