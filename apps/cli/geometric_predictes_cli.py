from __future__ import annotations

import argparse
from ._shared import read_input_lines, parse_points
from compgeom import Point2D, contains_point, in_circle, orientation_sign


def is_point_inside_triangle(point: Point2D, a: Point2D, b: Point2D, c: Point2D) -> bool:
    return contains_point(a, b, c, point)


def is_point_inside_circle(point: Point2D, a: Point2D, b: Point2D, c: Point2D) -> bool:
    orient = orientation_sign(a, b, c)
    if orient == 0:
        return False
    if orient < 0:
        b, c = c, b
    return in_circle(a, b, c, point)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate geometric predicates for provided points.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--points", nargs=8, type=float, help="Points coordinates: ax ay bx by cx cy px py")
    
    args = parser.parse_args(argv)
    
    a = b = c = pt = None
    lines = read_input_lines(args.input)
    if lines:
        pts = parse_points(lines)
        if len(pts) >= 4:
            a, b, c, pt = pts[:4]

    if not a and args.points:
        p = args.points
        a = Point2D(p[0], p[1])
        b = Point2D(p[2], p[3])
        c = Point2D(p[4], p[5])
        pt = Point2D(p[6], p[7])

    if not a:
        print("Error: No points provided. Use --points ax ay bx by cx cy px py or provide input file.")
        return 1

    print(f"Points: A={a}, B={b}, C={c}, P={pt}")
    print("orientation(a, b, c) =", orientation_sign(a, b, c))
    print("is_point_inside_triangle =", is_point_inside_triangle(pt, a, b, c))
    print("is_point_inside_circle =", is_point_inside_circle(pt, a, b, c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
