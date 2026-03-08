import math
import sys

from geometry_utils import EPSILON, Point, cross_product, is_on_segment, length, sub


def point_key(point):
    return (round(point.x / EPSILON), round(point.y / EPSILON))


def polygon_key(polygon):
    keys = [point_key(point) for point in polygon]
    if not keys:
        return ()

    candidates = []
    for sequence in (keys, list(reversed(keys))):
        min_index = min(range(len(sequence)), key=sequence.__getitem__)
        candidates.append(tuple(sequence[min_index:] + sequence[:min_index]))
    return min(candidates)


def segment_parameter(point, start, end):
    dx = end.x - start.x
    dy = end.y - start.y
    if abs(dx) >= abs(dy):
        return 0.0 if abs(dx) < EPSILON else (point.x - start.x) / dx
    return 0.0 if abs(dy) < EPSILON else (point.y - start.y) / dy


def signed_polygon_area(polygon):
    return 0.5 * sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


def canonical_segment(segment):
    start, end = segment
    return (start, end) if point_key(start) <= point_key(end) else (end, start)


def segment_intersection_points(seg1, seg2):
    a, b = seg1
    c, d = seg2
    ab = sub(b, a)
    cd = sub(d, c)
    denominator = ab.x * cd.y - ab.y * cd.x
    ac = sub(c, a)

    if abs(denominator) > EPSILON:
        t = (ac.x * cd.y - ac.y * cd.x) / denominator
        u = (ac.x * ab.y - ac.y * ab.x) / denominator
        if -EPSILON <= t <= 1 + EPSILON and -EPSILON <= u <= 1 + EPSILON:
            return [Point(a.x + t * ab.x, a.y + t * ab.y)]
        return []

    if abs(cross_product(a, b, c)) > EPSILON or abs(cross_product(a, b, d)) > EPSILON:
        return []

    overlap_points = []
    for point in (a, b, c, d):
        if is_on_segment(point, a, b) and is_on_segment(point, c, d):
            overlap_points.append(point)

    unique = {}
    for point in overlap_points:
        unique[point_key(point)] = point
    return list(unique.values())


def find_intersection_points(segments):
    intersections = {}
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            for point in segment_intersection_points(segments[i], segments[j]):
                intersections[point_key(point)] = point
    return list(intersections.values())


def split_segments(segments):
    split_points = []
    for start, end in segments:
        split_points.append({point_key(start): start, point_key(end): end})

    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            intersections = segment_intersection_points(segments[i], segments[j])
            for point in intersections:
                split_points[i][point_key(point)] = point
                split_points[j][point_key(point)] = point

    result = {}
    for index, (start, end) in enumerate(segments):
        ordered = sorted(
            split_points[index].values(),
            key=lambda point: segment_parameter(point, start, end),
        )
        for left, right in zip(ordered, ordered[1:]):
            if length(sub(right, left)) < EPSILON:
                continue
            segment = canonical_segment((left, right))
            result[(point_key(segment[0]), point_key(segment[1]))] = segment
    return list(result.values())


def build_graph(segments):
    vertices = {}
    adjacency = {}

    for start, end in segments:
        start_key = point_key(start)
        end_key = point_key(end)
        vertices[start_key] = start
        vertices[end_key] = end
        adjacency.setdefault(start_key, set()).add(end_key)
        adjacency.setdefault(end_key, set()).add(start_key)

    ordered_neighbors = {}
    for vertex_key, neighbors in adjacency.items():
        vertex = vertices[vertex_key]
        ordered_neighbors[vertex_key] = sorted(
            neighbors,
            key=lambda neighbor_key: math.atan2(
                vertices[neighbor_key].y - vertex.y,
                vertices[neighbor_key].x - vertex.x,
            ),
        )

    return vertices, ordered_neighbors


def trace_faces(vertices, ordered_neighbors):
    visited = set()
    polygons = []

    for start_key, neighbors in ordered_neighbors.items():
        for next_key in neighbors:
            directed_edge = (start_key, next_key)
            if directed_edge in visited:
                continue

            face = []
            current_key, following_key = directed_edge
            while True:
                visited.add((current_key, following_key))
                face.append(vertices[current_key])

                neighbor_cycle = ordered_neighbors[following_key]
                reverse_index = neighbor_cycle.index(current_key)
                next_index = (reverse_index - 1) % len(neighbor_cycle)
                new_key = neighbor_cycle[next_index]

                current_key, following_key = following_key, new_key
                if (current_key, following_key) == directed_edge:
                    break
                if len(face) > len(visited) + 1:
                    break

            if len(face) < 3:
                continue

            area = signed_polygon_area(face)
            if area <= EPSILON:
                continue
            polygons.append(face)

    unique = {}
    for polygon in polygons:
        unique[polygon_key(polygon)] = polygon
    return list(unique.values())


def analyze_arrangement(segments):
    intersection_points = find_intersection_points(segments)
    split = split_segments(segments)
    vertices, ordered_neighbors = build_graph(split)
    polygons = trace_faces(vertices, ordered_neighbors)
    return intersection_points, split, polygons


def parse_segments(lines):
    segments = []
    for line_number, line in enumerate(lines, start=1):
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 4:
            raise ValueError(f"Line {line_number}: expected 4 numbers, got {len(parts)}")

        x1, y1, x2, y2 = map(float, parts)
        start = Point(x1, y1)
        end = Point(x2, y2)
        if start == end:
            continue
        segments.append((start, end))
    return segments


def format_point(point):
    return f"({point.x:.6f}, {point.y:.6f})"


def main():
    try:
        segments = parse_segments(sys.stdin.readlines())
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        return

    intersection_points, split, polygons = analyze_arrangement(segments)

    print("Intersection Points:")
    if not intersection_points:
        print("  None")
    else:
        for index, point in enumerate(sorted(intersection_points, key=point_key), start=1):
            print(f"  {index:3}: {format_point(point)}")

    print("\nNon-Intersecting Segments:")
    if not split:
        print("  None")
    else:
        for index, (start, end) in enumerate(split, start=1):
            print(f"  {index:3}: {format_point(start)} -> {format_point(end)}")

    print("\nPolygons:")
    if not polygons:
        print("  None")
        return

    for index, polygon in enumerate(polygons, start=1):
        vertices = ", ".join(format_point(point) for point in polygon)
        print(f"  {index:3}: {vertices}")


if __name__ == "__main__":
    main()
