from __future__ import annotations

import argparse
from compgeom import Point2D, do_intersect
from _shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test intersection between two segments.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No points provided. Provide 4 points defining 2 segments.")
        return 1
    points = parse_points(lines)
    if len(points) < 4:
        print("Error: At least 4 points are required to define two segments.")
        return 1
        
    p1, q1 = points[0], points[1]
    p2, q2 = points[2], points[3]
    intersect = do_intersect(p1, q1, p2, q2)
    
    print(f"Segment 1: {p1} to {q1}")
    print(f"Segment 2: {p2} to {q2}")
    print(f"Result: Intersect? {intersect}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
