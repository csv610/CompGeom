import sys

from compgeom.geometry import Point
from compgeom.mesh import mesh_neighbors


def parse_mesh_query(lines):
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
                points_map[point_id] = Point(x, y, point_id)
            except ValueError:
                continue
            continue

        try:
            if len(parts) >= 3:
                ids = [int(value) for value in parts[:3]]
                triangles.append(tuple(points_map[point_id] for point_id in ids))
        except (ValueError, KeyError):
            continue

    return triangles, query_vertex, query_triangle


def main():
    triangles, query_vertex, query_triangle = parse_mesh_query(sys.stdin.readlines())
    if not triangles:
        print("No triangles found in input.")
        return

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


if __name__ == "__main__":
    main()
