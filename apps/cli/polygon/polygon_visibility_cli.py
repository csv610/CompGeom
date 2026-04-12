from __future__ import annotations

import argparse
from compgeom import Point2D
from compgeom.polygon.polygon_visibility import visible_boundary_segments
from .._shared import read_input_lines, parse_points


def format_point(point: Point2D) -> str:
    return f"({point.x:.6f}, {point.y:.6f})"


def parse_input(lines):
    points = parse_points(lines)
    if not points:
        raise ValueError("No points found in input.")
    return points[0], points[1:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute visible boundary segments for a polygon.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--query", nargs=2, type=float, help="Query point as 'x y'")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        # Default for demo
        query = Point2D(1.0, 2.5)
        polygon = [Point2D(0, 0), Point2D(5, 0), Point2D(5, 1), Point2D(2, 1), 
                   Point2D(2, 4), Point2D(5, 4), Point2D(5, 5), Point2D(0, 5)]
    else:
        if args.query:
            query = Point2D(args.query[0], args.query[1])
            polygon = parse_points(lines)
        else:
            try:
                query, polygon = parse_input(lines)
            except ValueError:
                print("Error: Could not parse input.")
                return 1

    if not polygon or len(polygon) < 3:
        print("Error: Polygon must have at least 3 vertices.")
        return 1

    segments = visible_boundary_segments(query, polygon)
    if not segments:
        print("Visible Segments:")
        print("  None")
        return 0

    print("Visible Segments:")
    for index, (start, end) in enumerate(segments, start=1):
        print(f"  {index:3}: {format_point(start)} -> {format_point(end)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
