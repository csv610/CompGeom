"""Polygon algorithms and generators."""

from __future__ import annotations

import heapq
import math
import random
from collections import deque
from typing import List, Tuple, Union

from ..geometry import (
    EPSILON,
    Point,
    Point3D,
    contains_point,
    cross_product,
    is_on_segment,
    length,
    sub,
)
from ..math_utils import distance, signed_area_twice


class _TriangleView:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = (v1, v2, v3)


def _ensure_ccw(polygon: list[Point]) -> list[Point]:
    return polygon if signed_area_twice(polygon) >= 0 else list(reversed(polygon))


def _ensure_cw(polygon: list[Point]) -> list[Point]:
    return polygon if signed_area_twice(polygon) <= 0 else list(reversed(polygon))


def _same_point(a: Point, b: Point, tolerance: float = 1e-7) -> bool:
    return abs(a.x - b.x) <= tolerance and abs(a.y - b.y) <= tolerance


def _point_on_boundary(point: Point, polygon: list[Point]) -> bool:
    return any(is_on_segment(point, polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon)))


def _proper_segment_intersection(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1 = cross_product(a, b, c)
    o2 = cross_product(a, b, d)
    o3 = cross_product(c, d, a)
    o4 = cross_product(c, d, b)

    if abs(o1) <= EPSILON and is_on_segment(c, a, b):
        return False
    if abs(o2) <= EPSILON and is_on_segment(d, a, b):
        return False
    if abs(o3) <= EPSILON and is_on_segment(a, c, d):
        return False
    if abs(o4) <= EPSILON and is_on_segment(b, c, d):
        return False
    return (o1 > EPSILON) != (o2 > EPSILON) and (o3 > EPSILON) != (o4 > EPSILON)


def _segment_inside_polygon(polygon: list[Point], start: Point, end: Point) -> bool:
    midpoint = Point((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not is_point_in_polygon(midpoint, polygon) and not _point_on_boundary(midpoint, polygon):
        return False

    for index, edge_start in enumerate(polygon):
        edge_end = polygon[(index + 1) % len(polygon)]
        shared_endpoint = start == edge_start or start == edge_end or end == edge_start or end == edge_end
        if shared_endpoint:
            continue
        if _proper_segment_intersection(start, end, edge_start, edge_end):
            return False
    return True


def _ray_segment_intersection(origin: Point, angle: float, start: Point, end: Point) -> tuple[float, Point] | None:
    direction = Point(math.cos(angle), math.sin(angle))
    edge = sub(end, start)
    delta = sub(start, origin)
    denominator = direction.x * edge.y - direction.y * edge.x
    if abs(denominator) <= EPSILON:
        return None

    ray_t = (delta.x * edge.y - delta.y * edge.x) / denominator
    edge_u = (delta.x * direction.y - delta.y * direction.x) / denominator
    if ray_t < -EPSILON or edge_u < -EPSILON or edge_u > 1 + EPSILON:
        return None

    intersection = Point(origin.x + ray_t * direction.x, origin.y + ray_t * direction.y)
    if distance(intersection, start) <= 1e-6:
        intersection = start
    elif distance(intersection, end) <= 1e-6:
        intersection = end
    return ray_t, intersection


def _cleanup_polygon(points: list[Point]) -> list[Point]:
    if not points:
        return []

    cleaned: list[Point] = []
    for point in points:
        if cleaned and _same_point(point, cleaned[-1]):
            continue
        cleaned.append(point)

    if len(cleaned) > 1 and _same_point(cleaned[0], cleaned[-1]):
        cleaned.pop()

    simplified: list[Point] = []
    for point in cleaned:
        if len(simplified) < 2:
            simplified.append(point)
            continue
        if abs(cross_product(simplified[-2], simplified[-1], point)) <= 1e-7 and is_on_segment(
            simplified[-1], simplified[-2], point
        ):
            simplified[-1] = point
            continue
        simplified.append(point)

    if len(simplified) >= 3 and abs(cross_product(simplified[-2], simplified[-1], simplified[0])) <= 1e-7:
        if is_on_segment(simplified[-1], simplified[-2], simplified[0]):
            simplified.pop()
    return simplified


def get_polygon_properties(polygon: list[Point]):
    area_twice = signed_area_twice(polygon)
    area = area_twice / 2.0
    if abs(area) < 1e-12:
        return 0, Point(0, 0), "Degenerate"

    centroid_x = 0.0
    centroid_y = 0.0
    for index, p1 in enumerate(polygon):
        p2 = polygon[(index + 1) % len(polygon)]
        cross = (p1.x * p2.y) - (p2.x * p1.y)
        centroid_x += (p1.x + p2.x) * cross
        centroid_y += (p1.y + p2.y) * cross

    centroid_x /= 6.0 * area
    centroid_y /= 6.0 * area
    orientation = "CCW" if area > 0 else "CW"
    return abs(area), Point(centroid_x, centroid_y), orientation


def is_point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        if is_on_segment(point, start, end):
            return True

    inside = False
    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        intersects_scanline = (start.y > point.y) != (end.y > point.y)
        if intersects_scanline and point.x < (end.x - start.x) * (point.y - start.y) / (end.y - start.y) + start.x:
            inside = not inside
    return inside


def is_ear(a: Point, b: Point, c: Point, polygon: list[Point]) -> bool:
    if cross_product(a, b, c) <= 0:
        return False

    triangle = _TriangleView(a, b, c)
    return not any(
        point not in (a, b, c) and contains_point(triangle, point)
        for point in polygon
    )


def triangulate_polygon(polygon: list[Point]):
    polygon = _ensure_ccw(list(polygon))
    remaining_indices = list(range(len(polygon)))
    working_polygon = list(polygon)
    triangles: list[tuple[int, int, int]] = []

    while len(remaining_indices) > 3:
        for offset, current in enumerate(remaining_indices):
            prev_index = remaining_indices[offset - 1]
            next_index = remaining_indices[(offset + 1) % len(remaining_indices)]
            if is_ear(polygon[prev_index], polygon[current], polygon[next_index], working_polygon):
                triangles.append((prev_index, current, next_index))
                remaining_indices.pop(offset)
                working_polygon.pop(offset)
                break
        else:
            break

    if len(remaining_indices) == 3:
        triangles.append(tuple(remaining_indices))

    return triangles, polygon


def visibility_polygon(viewpoint: Point, polygon: list[Point]) -> list[Point]:
    if not is_point_in_polygon(viewpoint, polygon):
        raise ValueError("Viewpoint must lie inside or on the boundary of the polygon.")

    intersections: list[tuple[float, float, Point]] = []
    perturbation = 1e-7
    for vertex in polygon:
        base_angle = math.atan2(vertex.y - viewpoint.y, vertex.x - viewpoint.x)
        for angle in (base_angle - perturbation, base_angle, base_angle + perturbation):
            best: tuple[float, Point] | None = None
            for index, start in enumerate(polygon):
                end = polygon[(index + 1) % len(polygon)]
                hit = _ray_segment_intersection(viewpoint, angle, start, end)
                if hit is None:
                    continue
                distance, point = hit
                if distance < -EPSILON:
                    continue
                if best is None or distance < best[0]:
                    best = (distance, point)
            if best is not None:
                intersections.append((angle, best[0], best[1]))

    intersections.sort(key=lambda item: (item[0], item[1]))
    return _cleanup_polygon([point for _, _, point in intersections])


def shortest_path_in_polygon(polygon: list[Point], source: Point, target: Point) -> tuple[list[Point], float]:
    if not is_point_in_polygon(source, polygon):
        raise ValueError("Source point must lie inside or on the boundary of the polygon.")
    if not is_point_in_polygon(target, polygon):
        raise ValueError("Target point must lie inside or on the boundary of the polygon.")

    nodes = [source, target, *polygon]
    graph: dict[int, list[tuple[int, float]]] = {index: [] for index in range(len(nodes))}
    for left in range(len(nodes)):
        for right in range(left + 1, len(nodes)):
            if not _segment_inside_polygon(polygon, nodes[left], nodes[right]):
                continue
            weight = distance(nodes[left], nodes[right])
            graph[left].append((right, weight))
            graph[right].append((left, weight))

    distances = {0: 0.0}
    previous: dict[int, int] = {}
    queue = [(0.0, 0)]
    while queue:
        currentdistance, node = heapq.heappop(queue)
        if currentdistance > distances.get(node, float("inf")) + EPSILON:
            continue
        if node == 1:
            break
        for neighbor, weight in graph[node]:
            candidate = currentdistance + weight
            if candidate + EPSILON < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    if 1 not in distances:
        raise ValueError("No path found inside the polygon.")

    path_indices = [1]
    while path_indices[-1] != 0:
        path_indices.append(previous[path_indices[-1]])
    path_indices.reverse()
    path = [nodes[index] for index in path_indices]
    return path, distances[1]


def _domain_contains_point(point: Point, outer: list[Point], holes: list[list[Point]]) -> bool:
    if not is_point_in_polygon(point, outer):
        return False
    return not any(is_point_in_polygon(point, hole) and not _point_on_boundary(point, hole) for hole in holes)


def _segment_inside_domain(
    start: Point,
    end: Point,
    outer: list[Point],
    holes: list[list[Point]],
    allow_hole_endpoint: Point | None = None,
) -> bool:
    midpoint = Point((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not _domain_contains_point(midpoint, outer, holes):
        return False

    boundaries = [outer, *holes]
    for boundary in boundaries:
        for index, edge_start in enumerate(boundary):
            edge_end = boundary[(index + 1) % len(boundary)]
            shared_endpoint = start == edge_start or start == edge_end or end == edge_start or end == edge_end
            if shared_endpoint:
                continue
            if allow_hole_endpoint is not None and (edge_start == allow_hole_endpoint or edge_end == allow_hole_endpoint):
                continue
            if _proper_segment_intersection(start, end, edge_start, edge_end):
                return False
    return True


def _splice_hole_into_polygon(outer: list[Point], hole: list[Point]) -> list[Point]:
    hole_vertex_index = max(range(len(hole)), key=lambda index: (hole[index].x, -hole[index].y))
    hole_vertex = hole[hole_vertex_index]

    candidates = []
    for outer_index, outer_vertex in enumerate(outer):
        if not _segment_inside_domain(hole_vertex, outer_vertex, outer, [hole], allow_hole_endpoint=hole_vertex):
            continue
        candidates.append((distance(hole_vertex, outer_vertex), outer_index))
    if not candidates:
        raise ValueError("Failed to connect hole to outer boundary.")

    _, outer_index = min(candidates)
    outer_vertex = outer[outer_index]

    rotated_hole = hole[hole_vertex_index:] + hole[:hole_vertex_index]
    merged: list[Point] = []
    merged.extend(outer[: outer_index + 1])
    merged.append(hole_vertex)
    merged.extend(rotated_hole[1:])
    merged.append(hole_vertex)
    merged.append(outer_vertex)
    merged.extend(outer[outer_index + 1 :])
    return merged


def triangulate_polygon_with_holes(
    outer_boundary: list[Point],
    holes: list[list[Point]] | None = None,
) -> tuple[list[tuple[Point, Point, Point]], list[Point]]:
    holes = holes or []
    merged_polygon = _ensure_ccw(list(outer_boundary))
    for hole in holes:
        merged_polygon = _splice_hole_into_polygon(merged_polygon, _ensure_cw(list(hole)))

    triangle_indices, merged_polygon = triangulate_polygon(merged_polygon)
    triangles = [tuple(merged_polygon[index] for index in triangle) for triangle in triangle_indices]
    return triangles, merged_polygon


def solve_art_gallery(polygon_input: list[Point]) -> list[Point]:
    triangles, polygon = triangulate_polygon(polygon_input)
    if not triangles:
        return []

    colors = {}
    first = triangles[0]
    colors[first[0]], colors[first[1]], colors[first[2]] = 0, 1, 2

    processed = [False] * len(triangles)
    processed[0] = True
    queue = deque([0])

    while queue:
        current_index = queue.popleft()
        current_triangle = triangles[current_index]
        for index, triangle in enumerate(triangles):
            if processed[index]:
                continue

            shared = set(current_triangle).intersection(triangle)
            if len(shared) != 2:
                continue

            new_vertex = next(iter(set(triangle) - shared))
            colors[new_vertex] = 3 - sum(colors[vertex] for vertex in shared)
            processed[index] = True
            queue.append(index)

    groups = [[], [], []]
    for vertex_index, color in colors.items():
        groups[color].append(polygon[vertex_index])
    return min(groups, key=len)


def get_triangulation_with_diagonals(polygon: list[Point]):
    polygon = _ensure_ccw(list(polygon))
    polygon_size = len(polygon)
    working_polygon = list(polygon)
    working_indices = list(range(polygon_size))
    triangles: list[tuple[int, int, int]] = []
    diagonals: list[tuple[int, int]] = []

    while len(working_indices) > 3:
        for offset, current in enumerate(working_indices):
            prev_index = working_indices[offset - 1]
            next_index = working_indices[(offset + 1) % len(working_indices)]
            if not is_ear(polygon[prev_index], polygon[current], polygon[next_index], working_polygon):
                continue

            triangles.append((prev_index, current, next_index))
            if abs(next_index - prev_index) != 1 and {prev_index, next_index} != {0, polygon_size - 1}:
                diagonals.append(tuple(sorted((prev_index, next_index))))
            working_indices.pop(offset)
            working_polygon.pop(offset)
            break
        else:
            break

    if len(working_indices) == 3:
        triangles.append(tuple(working_indices))
    return triangles, diagonals, polygon


def hertel_mehlhorn(polygon_input: list[Point]):
    triangles, diagonals, polygon = get_triangulation_with_diagonals(polygon_input)
    partitions = [list(triangle) for triangle in triangles]
    reflex_vertices = {
        index
        for index in range(len(polygon))
        if cross_product(polygon[index - 1], polygon[index], polygon[(index + 1) % len(polygon)]) <= 0
    }

    for diagonal in diagonals:
        shared_partitions = [
            partition_index
            for partition_index, partition in enumerate(partitions)
            if diagonal[0] in partition and diagonal[1] in partition
        ]
        if len(shared_partitions) != 2:
            continue

        u, v = diagonal
        if u in reflex_vertices or v in reflex_vertices:
            continue

        first, second = shared_partitions
        merged = list(set(partitions[first]) | set(partitions[second]))
        partitions.pop(max(first, second))
        partitions.pop(min(first, second))
        partitions.append(merged)

    return partitions, polygon


def graham_scan(points: list[Point]) -> list[Point]:
    if len(points) <= 2:
        return points

    anchor = min(points, key=lambda point: (point.y, point.x))

    def polar_order(point: Point):
        if point == anchor:
            return (-math.inf, 0)
        return (
            math.atan2(point.y - anchor.y, point.x - anchor.x),
            (point.x - anchor.x) ** 2 + (point.y - anchor.y) ** 2,
        )

    hull: list[Point] = []
    for point in sorted(points, key=polar_order):
        while len(hull) >= 2 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    return hull


def monotone_chain(points: list[Point]) -> list[Point]:
    if len(points) <= 2:
        return points

    ordered_points = sorted(points, key=lambda point: (point.x, point.y))
    lower: list[Point] = []
    for point in ordered_points:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[Point] = []
    for point in reversed(ordered_points):
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def generate_random_convex_polygon(
    num_points: int = 10,
    x_range=(0, 100),
    y_range=(0, 100),
) -> list[Point]:
    points = [
        Point(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(num_points)
    ]
    return monotone_chain(points)


def is_convex(polygon: list[Point]) -> bool:
    if len(polygon) < 3:
        return True

    turn_directions = [
        cross_product(polygon[i], polygon[(i + 1) % len(polygon)], polygon[(i + 2) % len(polygon)])
        for i in range(len(polygon))
    ]
    non_zero_turns = [turn > 0 for turn in turn_directions if abs(turn) > 1e-9]
    return all(non_zero_turns) or not any(non_zero_turns)


def generate_simple_polygon(
    n_points: int = 20,
    x_range=(0, 100),
    y_range=(0, 100),
) -> list[Point]:
    points = [
        Point(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(n_points)
    ]
    center_x = sum(point.x for point in points) / n_points
    center_y = sum(point.y for point in points) / n_points
    ordered = sorted(points, key=lambda point: math.atan2(point.y - center_y, point.x - center_x))
    return [Point(point.x, point.y, index) for index, point in enumerate(ordered)]


def generate_points_in_triangle(
    a: Union[Point, Point3D], 
    b: Union[Point, Point3D], 
    c: Union[Point, Point3D], 
    n_points: int = 100
) -> list[Union[Point, Point3D]]:
    """Samples points uniformly from the interior of a triangle (2D or 3D)."""
    is_3d = isinstance(a, Point3D) or isinstance(b, Point3D) or isinstance(c, Point3D)
    
    samples: list[Union[Point, Point3D]] = []
    for _ in range(n_points):
        r1 = random.random()
        r2 = random.random()
        if r1 + r2 > 1:
            r1, r2 = 1 - r1, 1 - r2
        
        px = a.x + r1 * (b.x - a.x) + r2 * (c.x - a.x)
        py = a.y + r1 * (b.y - a.y) + r2 * (c.y - a.y)
        
        if is_3d:
            az = getattr(a, 'z', 0.0)
            bz = getattr(b, 'z', 0.0)
            cz = getattr(c, 'z', 0.0)
            pz = az + r1 * (bz - az) + r2 * (cz - az)
            samples.append(Point3D(px, py, pz))
        else:
            samples.append(Point(px, py))
            
    return samples


def get_convex_diameter(polygon: List[Point]) -> float:
    """Calculates the maximum diameter of a convex polygon using Rotating Calipers."""
    if len(polygon) < 2:
        return 0.0
    if len(polygon) == 2:
        return distance(polygon[0], polygon[1])

    n = len(polygon)
    max_d_sq = 0.0
    k = 1
    
    for i in range(n):
        while True:
            # Area of triangle formed by edge (i, i+1) and vertex k
            area = abs(cross_product(polygon[i], polygon[(i + 1) % n], polygon[k]))
            # Area of triangle with next vertex k+1
            next_area = abs(cross_product(polygon[i], polygon[(i + 1) % n], polygon[(k + 1) % n]))
            
            if next_area > area:
                k = (k + 1) % n
            else:
                break
        
        d1 = (polygon[i].x - polygon[k].x)**2 + (polygon[i].y - polygon[k].y)**2
        d2 = (polygon[(i + 1) % n].x - polygon[k].x)**2 + (polygon[(i + 1) % n].y - polygon[k].y)**2
        max_d_sq = max(max_d_sq, d1, d2)
        
    return math.sqrt(max_d_sq)


__all__ = [
    "generate_points_in_triangle",
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "get_convex_diameter",
    "get_polygon_properties",
    "get_triangulation_with_diagonals",
    "graham_scan",
    "hertel_mehlhorn",
    "is_convex",
    "is_ear",
    "is_point_in_polygon",
    "monotone_chain",
    "shortest_path_in_polygon",
    "solve_art_gallery",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
    "visibility_polygon",
]
