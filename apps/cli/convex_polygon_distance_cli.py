from __future__ import annotations

import argparse
from compgeom import Point2D, dist_point_to_segment, is_point_in_polygon
from _shared import read_input_lines, parse_points


def _polygon_distance(polygon_a: list[Point2D], polygon_b: list[Point2D]) -> float:
    if any(is_point_in_polygon(point, polygon_b) for point in polygon_a):
        return 0.0
    if any(is_point_in_polygon(point, polygon_a) for point in polygon_b):
        return 0.0

    best = float("inf")
    for point in polygon_a:
        for index, start in enumerate(polygon_b):
            end = polygon_b[(index + 1) % len(polygon_b)]
            best = min(best, dist_point_to_segment(point, start, end))

    for point in polygon_b:
        for index, start in enumerate(polygon_a):
            end = polygon_a[(index + 1) % len(polygon_a)]
            best = min(best, dist_point_to_segment(point, start, end))
    return best


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure the minimum distance between two convex polygons."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input provided. Provide two polygons separated by 'NEXT'.")
        return 1
        
    # Split input into two polygons
    poly_lines_a = []
    poly_lines_b = []
    current = poly_lines_a
    for line in lines:
        if line.strip().upper() == "NEXT":
            current = poly_lines_b
            continue
        current.append(line)
        
    if not poly_lines_b and len(poly_lines_a) > 2:
        # If no explicit separator, try to split in half if even
        # But it's better to be explicit. Let's just assume first 3+ are poly A, rest are poly B if we can find a heuristic
        # For now, let's require 'NEXT' or two clear blocks.
        print("Error: Provide two polygons separated by 'NEXT' line.")
        return 1

    polygon_a = parse_points(poly_lines_a)
    polygon_b = parse_points(poly_lines_b)
    
    if len(polygon_a) < 3 or len(polygon_b) < 3:
        print("Error: Both polygons must have at least 3 vertices.")
        return 1
        
    distance = _polygon_distance(polygon_a, polygon_b)
    print(f"Minimum distance between polygons: {distance:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
