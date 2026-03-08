import sys

from geometry_utils import Point
from trianglemesh.mesh import euler_characteristic


def parse_mesh(lines):
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
                reading_points = False
            continue

        try:
            if len(parts) >= 3:
                ids = [int(value) for value in parts[:3]]
                triangles.append(tuple(points_map[point_id] for point_id in ids))
        except (ValueError, KeyError):
            continue

    return triangles


def main():
    triangles = parse_mesh(sys.stdin.readlines())
    if not triangles:
        print("No triangles found in input.")
        return

    result = euler_characteristic(triangles)
    print("Mesh Topology:")
    print(f"  Vertices: {result['vertices']}")
    print(f"  Edges:    {result['edges']}")
    print(f"  Faces:    {result['faces']}")
    print(f"  Euler characteristic: {result['euler_characteristic']}")


if __name__ == "__main__":
    main()
