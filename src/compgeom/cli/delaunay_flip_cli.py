from __future__ import annotations

from compgeom.cli._shared import demo_mesh_lines, parse_point_fields
from compgeom.mesh.delaunay_triangulation import DelaunayMesher, build_topology

def main() -> int:
    points_map, triangles_data, reading_points = {}, [], True
    for line in demo_mesh_lines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if parts[0].upper() == 'T':
            reading_points = False
            continue
        if reading_points:
            point = parse_point_fields(parts, point_id=len(points_map), with_id=len(parts) >= 3)
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
    mesh = build_topology(triangles_data)
    DelaunayMesher.delaunay_flip(mesh)
    print(f"Delaunay Triangulation: {len(mesh)} triangles.")
    for i, tri in enumerate(mesh):
        ids = sorted([v.id for v in tri.vertices])
        print(f"Triangle {i:3}: {ids[0]:3}, {ids[1]:3}, {ids[2]:3}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
