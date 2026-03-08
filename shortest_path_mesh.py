import sys

from geometry_utils import Point
from trianglemesh.path import shortest_path


def parse_mesh_query(lines):
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
                source = Point(float(parts[0]), float(parts[1]))
            elif target is None and len(parts) >= 2:
                target = Point(float(parts[0]), float(parts[1]))
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

    return triangles, source, target


def format_point(point):
    return f"({point.x:.6f}, {point.y:.6f})"


def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "true"
    triangles, source, target = parse_mesh_query(sys.stdin.readlines())
    if not triangles:
        print("No triangles found in input.")
        return
    if source is None or target is None:
        print("Need source and target points in a Q section.")
        return

    try:
        path, total_length = shortest_path(triangles, source, target, mode=mode)
    except ValueError as exc:
        print(str(exc))
        return

    print(f"Mode: {mode}")
    print(f"Path length: {total_length:.6f}")
    print(f"Path vertices: {len(path)}")
    for index, point in enumerate(path, start=1):
        print(f"  {index:3}: {format_point(point)}")


if __name__ == "__main__":
    main()
