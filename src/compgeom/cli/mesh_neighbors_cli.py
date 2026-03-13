from __future__ import annotations

import argparse

from compgeom import Point2D
from compgeom import mesh_neighbors
from ._shared import demo_mesh_lines, parse_point_fields


def parse_mesh_query(lines: list[str]) -> tuple[list[tuple[Point2D, Point2D, Point2D]], int | None, int | None]:
    points_map = {}
    triangles = []
    reading_points = True
    query_vertex = None
    query_triangle = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        tag = parts[0].upper()
        if tag == "T":
            reading_points = False
            continue
        if tag == "P" and len(parts) >= 2:
            try:
                query_vertex = int(parts[1])
            except ValueError:
                pass
            continue
        if tag == "F" and len(parts) >= 2:
            try:
                query_triangle = int(parts[1])
            except ValueError:
                pass
            continue

        if reading_points:
            point = parse_point_fields(parts, point_id=len(points_map), with_id=len(parts) >= 3)
            if point is None:
                continue
            points_map[point.id] = point
            continue

        try:
            if len(parts) >= 3:
                ids = [int(value) for value in parts[:3]]
                triangles.append(tuple(points_map[point_id] for point_id in ids))
        except (ValueError, KeyError):
            continue

    return triangles, query_vertex, query_triangle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect neighbor relationships in a demo mesh.")
    parser.parse_args(argv)
    lines = [*demo_mesh_lines(), "P 1\n", "F 0\n"]
    triangles, query_vertex, query_triangle = parse_mesh_query(lines)

    neighbors = mesh_neighbors(triangles)

    if query_vertex is not None:
        print(f"Point {query_vertex} neighbors: {neighbors['vertex_neighbors'].get(query_vertex, [])}")
    else:
        print("Point neighbors:")
        for vertex_id in sorted(neighbors["vertex_neighbors"]):
            print(f"  {vertex_id}: {neighbors['vertex_neighbors'][vertex_id]}")

    if query_triangle is not None:
        print(f"Triangle {query_triangle} neighbors: {neighbors['triangle_neighbors'].get(query_triangle, [])}")
    else:
        print("Triangle neighbors:")
        for triangle_id in sorted(neighbors["triangle_neighbors"]):
            print(f"  {triangle_id}: {neighbors['triangle_neighbors'][triangle_id]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
