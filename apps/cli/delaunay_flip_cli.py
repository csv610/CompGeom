from __future__ import annotations

import argparse
import sys

from ._shared import read_input_lines, parse_point_fields
from compgeom.mesh import DelaunayMesher, build_topology


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Delaunay edge flips on a mesh."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input mesh provided.")
        return 1

    points_map, triangles_data, reading_points = {}, [], True
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if parts[0].upper() == "T":
            reading_points = False
            continue
        if reading_points:
            point = parse_point_fields(
                parts, point_id=len(points_map), with_id=len(parts) >= 3
            )
            if point is None:
                reading_points = False
            else:
                points_map[point.id] = point
        if not reading_points:
            try:
                if len(parts) >= 3:
                    p_ids = [int(x) for x in parts[:3]]
                    triangles_data.append([points_map[pid] for pid in p_ids])
            except (ValueError, KeyError):
                continue

    if not triangles_data:
        print("Error: Could not parse mesh data from stdin.")
        return 1

    mesh = build_topology(triangles_data)
    DelaunayMesher.delaunay_flip(mesh)

    print(f"Delaunay Triangulation: {len(mesh)} triangles.")
    for i, tri in enumerate(mesh):
        ids = sorted([v.id for v in tri.vertices])
        print(f"Triangle {i:3}: {ids[0]:3}, {ids[1]:3}, {ids[2]:3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
