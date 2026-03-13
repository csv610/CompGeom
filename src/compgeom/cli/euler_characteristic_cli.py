from __future__ import annotations

import argparse

from compgeom import euler_characteristic
from compgeom.cli._shared import demo_mesh_lines, parse_point_fields


def parse_mesh(lines: list[str]) -> list[tuple[object, object, object]]:
    points_map = {}
    triangles = []
    reading_points = True

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        if parts[0].upper() == "T":
            reading_points = False
            continue

        if reading_points:
            point = parse_point_fields(
                parts,
                point_id=len(points_map),
                with_id=len(parts) >= 3,
            )
            if point is None:
                reading_points = False
            else:
                points_map[point.id] = point
            continue

        try:
            if len(parts) >= 3:
                ids = [int(value) for value in parts[:3]]
                triangles.append(tuple(points_map[point_id] for point_id in ids))
        except (ValueError, KeyError):
            continue

    return triangles


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute Euler characteristic for a demo mesh.")
    parser.parse_args(argv)
    triangles = parse_mesh(demo_mesh_lines())
    result = euler_characteristic(triangles)
    print("Mesh Topology:")
    print(f"  Vertices: {result['vertices']}")
    print(f"  Edges:    {result['edges']}")
    print(f"  Faces:    {result['faces']}")
    print(f"  Euler characteristic: {result['euler_characteristic']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
