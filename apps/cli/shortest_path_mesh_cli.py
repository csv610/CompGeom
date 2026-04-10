from __future__ import annotations

import argparse
from compgeom import Point2D
from ._shared import read_input_lines
from compgeom.algo.path import shortest_path


def parse_mesh_query(lines: list[str]) -> tuple[list[tuple[Point2D, Point2D, Point2D]], Point2D | None, Point2D | None]:
    points_map = {}
    triangles = []
    reading_points = True
    reading_query = False
    source = None
    target = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        tag = parts[0].upper()
        if tag == "T":
            reading_points = False
            continue
        if tag == "Q":
            reading_query = True
            continue

        if reading_query:
            if source is None and len(parts) >= 2:
                source = Point2D(float(parts[0]), float(parts[1]))
            elif target is None and len(parts) >= 2:
                target = Point2D(float(parts[0]), float(parts[1]))
            continue

        if reading_points:
            if len(parts) < 2:
                continue
            try:
                if len(parts) >= 3:
                    point_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                else:
                    point_id = len(points_map)
                    x = float(parts[0])
                    y = float(parts[1])
                points_map[point_id] = Point2D(x, y, point_id)
            except ValueError:
                continue
            continue

        try:
            if len(parts) >= 3:
                ids = [int(value) for value in parts[:3]]
                triangles.append(tuple(points_map[point_id] for point_id in ids))
        except (ValueError, KeyError):
            continue

    return triangles, source, target


def format_point(point: Point2D) -> str:
    return f"({point.x:.6f}, {point.y:.6f})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute a shortest path across a mesh.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument(
        "--mode",
        default="true",
        help="Shortest-path mode forwarded to the path solver.",
    )
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input mesh and query points provided.")
        return 1
        
    triangles, source, target = parse_mesh_query(lines)
    if not triangles or source is None or target is None:
        print("Error: Could not parse triangles or source/target points from input.")
        return 1

    try:
        path, total_length = shortest_path(triangles, source, target, mode=args.mode)
    except ValueError as exc:
        print(str(exc))
        return 1

    print(f"Mode: {args.mode}")
    print(f"Path length: {total_length:.6f}")
    print(f"Path vertices: {len(path)}")
    for index, point in enumerate(path, start=1):
        print(f"  {index:3}: {format_point(point)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
