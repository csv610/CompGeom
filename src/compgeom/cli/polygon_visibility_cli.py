from __future__ import annotations

import argparse
from compgeom import Point2D
from compgeom.polygon.polygon_visibility import visible_boundary_segments
from compgeom.cli._shared import read_nonempty_stdin_lines, parse_points


def format_point(point: Point2D) -> str:
    return f"({point.x:.6f}, {point.y:.6f})"


def parse_input(lines):
    points = parse_points(lines)
    if not points:
        raise ValueError("No points found in input.")
    return points[0], points[1:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute visible boundary segments for a polygon provided via stdin.")
    parser.add_argument("--query", nargs=2, type=float, help="Query point as 'x y'")
    args = parser.parse_args(argv)

    if argv is None or len(argv) == 0:
        try:
            lines = read_nonempty_stdin_lines()
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
                    query, polygon = parse_input(lines)
        except (OSError, ValueError):
            return 1
    else:
        remaining = [a for a in argv if not a.startswith("-")]
        if args.query:
            query = Point2D(args.query[0], args.query[1])
            polygon = parse_points(remaining)
        else:
            if not remaining:
                # Default for demo
                query = Point2D(1.0, 2.5)
                polygon = [Point2D(0, 0), Point2D(5, 0), Point2D(5, 1), Point2D(2, 1), 
                           Point2D(2, 4), Point2D(5, 4), Point2D(5, 5), Point2D(0, 5)]
            else:
                query, polygon = parse_input(remaining)

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
