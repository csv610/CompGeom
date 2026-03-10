"""Polygon data structures and algorithms."""

from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple, Union

from ..geo_math.geometry import (
    EPSILON,
    Point,
    Point3D,
    clip_polygon,
    contains_point,
    cross_product,
    is_on_segment,
    sub,
)
from ..geo_math.math_utils import distance, signed_area_twice


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
    n = len(polygon)
    if n == 0:
        return False
    for i in range(n):
        if is_on_segment(point, polygon[i], polygon[(i + 1) % n]):
            return True
    return False


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


def _ray_segment_intersection(
    origin: Point, angle: float, start: Point, end: Point
) -> tuple[float, Point] | None:
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


def _is_ear(a: Point, b: Point, c: Point, polygon: list[Point]) -> bool:
    if cross_product(a, b, c) <= 0:
        return False

    triangle = _TriangleView(a, b, c)
    for point in polygon:
        if point is not a and point is not b and point is not c:
            if contains_point(triangle, point):
                return False
    return True


def _ear_clip(
    polygon: list[Point],
    *,
    collect_diagonals: bool = False,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
    ordered = _ensure_ccw(list(polygon))
    polygon_size = len(ordered)
    working_polygon = list(ordered)
    working_indices = list(range(polygon_size))
    triangles: list[tuple[int, int, int]] = []
    diagonals: list[tuple[int, int]] = []

    while len(working_indices) > 3:
        for offset, current in enumerate(working_indices):
            prev_index = working_indices[offset - 1]
            next_index = working_indices[(offset + 1) % len(working_indices)]
            if not _is_ear(ordered[prev_index], ordered[current], ordered[next_index], working_polygon):
                continue

            triangles.append((prev_index, current, next_index))
            if collect_diagonals and abs(next_index - prev_index) != 1 and {prev_index, next_index} != {
                0,
                polygon_size - 1,
            }:
                diagonals.append(tuple(sorted((prev_index, next_index))))
            working_indices.pop(offset)
            working_polygon.pop(offset)
            break
        else:
            break

    if len(working_indices) == 3:
        triangles.append(tuple(working_indices))

    return triangles, diagonals, ordered


@dataclass(frozen=True, slots=True)
class PolygonProperties:
    area: float
    centroid: Point
    orientation: str


class ConvexHull:
    """Convex hull construction algorithms."""

    @staticmethod
    def _next_hull_point(current: Point, candidate: Point, challenger: Point) -> Point:
        turn = cross_product(current, candidate, challenger)
        if turn < -EPSILON:
            return challenger
        if abs(turn) <= EPSILON and distance(current, challenger) > distance(current, candidate):
            return challenger
        return candidate

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def quick_hull(points: list[Point]) -> list[Point]:
        if len(points) <= 2:
            return points

        unique_points = sorted(set(points), key=lambda point: (point.x, point.y))
        if len(unique_points) <= 2:
            return unique_points

        leftmost = unique_points[0]
        rightmost = unique_points[-1]

        def distance_from_line(a: Point, b: Point, p: Point) -> float:
            return abs(cross_product(a, b, p))

        def build_hull(a: Point, b: Point, candidates: list[Point]) -> list[Point]:
            if not candidates:
                return []

            farthest = max(candidates, key=lambda point: distance_from_line(a, b, point))
            left_of_af = [point for point in candidates if cross_product(a, farthest, point) > EPSILON]
            left_of_fb = [point for point in candidates if cross_product(farthest, b, point) > EPSILON]
            return build_hull(a, farthest, left_of_af) + [farthest] + build_hull(farthest, b, left_of_fb)

        upper = [point for point in unique_points[1:-1] if cross_product(leftmost, rightmost, point) > EPSILON]
        lower = [point for point in unique_points[1:-1] if cross_product(rightmost, leftmost, point) > EPSILON]

        hull = [leftmost] + build_hull(leftmost, rightmost, upper) + [rightmost] + build_hull(
            rightmost,
            leftmost,
            lower,
        )
        return ConvexHull.monotone_chain(hull)

    @staticmethod
    def chan(points: list[Point]) -> list[Point]:
        unique_points = sorted(set(points), key=lambda point: (point.x, point.y))
        if len(unique_points) <= 2:
            return unique_points

        n = len(unique_points)
        t = 1
        while True:
            m = min(1 << (1 << t), n)
            hulls = [
                ConvexHull.monotone_chain(unique_points[i : i + m]) for i in range(0, n, m)
            ]
            start = min(unique_points, key=lambda point: (point.x, point.y))
            hull = [start]

            for _ in range(m):
                next_point = None
                for sub_hull in hulls:
                    for point in sub_hull:
                        if point == hull[-1]:
                            continue
                        if next_point is None:
                            next_point = point
                            continue
                        next_point = ConvexHull._next_hull_point(hull[-1], next_point, point)

                if next_point is None:
                    return hull
                if next_point == start:
                    return ConvexHull.monotone_chain(hull)
                hull.append(next_point)

            t += 1

    @staticmethod
    def is_convex_hull(points: list[Point], hull: list[Point]) -> bool:
        if not hull:
            return len(set(points)) == 0

        unique_points = set(points)
        if any(vertex not in unique_points for vertex in hull):
            return False
        if len(set(hull)) != len(hull):
            return False
        if len(hull) == 1:
            return len(unique_points) == 1 and hull[0] in unique_points
        if len(hull) == 2:
            a, b = hull
            return all(abs(cross_product(a, b, point)) <= EPSILON for point in unique_points)

        for i in range(len(hull)):
            if cross_product(hull[i - 1], hull[i], hull[(i + 1) % len(hull)]) <= EPSILON:
                return False

        hull_polygon = Polygon(hull)
        for point in unique_points:
            if not hull_polygon.contains_point(point):
                return False
        return True

@dataclass(frozen=True, slots=True)
class Polygon:
    vertices: tuple[Point, ...]

    def __init__(self, vertices: Sequence[Point]):
        object.__setattr__(self, "vertices", tuple(vertices))

    def __iter__(self):
        return iter(self.vertices)

    def __len__(self) -> int:
        return len(self.vertices)

    def __getitem__(self, index: int) -> Point:
        return self.vertices[index]

    def as_list(self) -> list[Point]:
        return list(self.vertices)

    def ensure_ccw(self) -> Polygon:
        return Polygon(_ensure_ccw(self.as_list()))

    def ensure_cw(self) -> Polygon:
        return Polygon(_ensure_cw(self.as_list()))

    def properties(self) -> PolygonProperties:
        polygon = self.vertices
        n = len(polygon)
        if n < 3:
            return PolygonProperties(0.0, Point(0, 0), "Degenerate")

        area_twice = 0.0
        centroid_x = 0.0
        centroid_y = 0.0
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            cross = (p1.x * p2.y) - (p2.x * p1.y)
            area_twice += cross
            centroid_x += (p1.x + p2.x) * cross
            centroid_y += (p1.y + p2.y) * cross

        area = area_twice / 2.0
        if abs(area) < 1e-12:
            return PolygonProperties(0.0, Point(0, 0), "Degenerate")

        centroid_x /= 6.0 * area
        centroid_y /= 6.0 * area
        orientation = "CCW" if area > 0 else "CW"
        return PolygonProperties(abs(area), Point(centroid_x, centroid_y), orientation)

    def contains_point(self, point: Point) -> bool:
        polygon = self.vertices
        n = len(polygon)
        if n < 3:
            return False

        inside = False
        for i in range(n):
            start = polygon[i]
            end = polygon[(i + 1) % n]

            if is_on_segment(point, start, end):
                return True

            if ((start.y > point.y) != (end.y > point.y)) and (
                point.x < (end.x - start.x) * (point.y - start.y) / (end.y - start.y) + start.x
            ):
                inside = not inside

        return inside

    def _segment_inside_boundaries(
        self,
        start: Point,
        end: Point,
        boundaries: list[list[Point]],
        midpoint_inside: Callable[[Point], bool],
        allow_boundary_endpoint: Point | None = None,
    ) -> bool:
        midpoint = Point((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
        if not midpoint_inside(midpoint):
            return False

        for boundary in boundaries:
            for index, edge_start in enumerate(boundary):
                edge_end = boundary[(index + 1) % len(boundary)]
                shared_endpoint = start == edge_start or start == edge_end or end == edge_start or end == edge_end
                if shared_endpoint:
                    continue
                if allow_boundary_endpoint is not None and (
                    edge_start == allow_boundary_endpoint or edge_end == allow_boundary_endpoint
                ):
                    continue
                if _proper_segment_intersection(start, end, edge_start, edge_end):
                    return False
        return True

    def _segment_inside(self, start: Point, end: Point) -> bool:
        polygon = self.as_list()
        return self._segment_inside_boundaries(
            start,
            end,
            [polygon],
            lambda midpoint: self.contains_point(midpoint) or _point_on_boundary(midpoint, polygon),
        )

    def triangulate(self) -> tuple[list[tuple[int, int, int]], list[Point]]:
        triangles, _, polygon = _ear_clip(self.as_list())
        return triangles, polygon

    def visibility_polygon(self, viewpoint: Point) -> list[Point]:
        polygon = self.as_list()
        if not self.contains_point(viewpoint):
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
                    hit_distance, point = hit
                    if hit_distance < -EPSILON:
                        continue
                    if best is None or hit_distance < best[0]:
                        best = (hit_distance, point)
                if best is not None:
                    intersections.append((angle, best[0], best[1]))

        intersections.sort(key=lambda item: (item[0], item[1]))
        return _cleanup_polygon([point for _, _, point in intersections])

    def kernel(self) -> list[Point]:
        polygon = self.ensure_ccw().as_list()
        if len(polygon) < 3:
            return []

        kernel = list(polygon)
        for index, start in enumerate(polygon):
            end = polygon[(index + 1) % len(polygon)]
            kernel = clip_polygon(kernel, start, end)
            if not kernel:
                return []
        return _cleanup_polygon(kernel)

    def shortest_path(self, source: Point, target: Point) -> tuple[list[Point], float]:
        if not self.contains_point(source):
            raise ValueError("Source point must lie inside or on the boundary of the polygon.")
        if not self.contains_point(target):
            raise ValueError("Target point must lie inside or on the boundary of the polygon.")

        polygon = self.as_list()
        nodes = [source, target, *polygon]
        graph: dict[int, list[tuple[int, float]]] = {index: [] for index in range(len(nodes))}
        for left in range(len(nodes)):
            for right in range(left + 1, len(nodes)):
                if not self._segment_inside(nodes[left], nodes[right]):
                    continue
                weight = distance(nodes[left], nodes[right])
                graph[left].append((right, weight))
                graph[right].append((left, weight))

        distances = {0: 0.0}
        previous: dict[int, int] = {}
        queue = [(0.0, 0)]
        while queue:
            current_distance, node = heapq.heappop(queue)
            if current_distance > distances.get(node, float("inf")) + EPSILON:
                continue
            if node == 1:
                break
            for neighbor, weight in graph[node]:
                candidate = current_distance + weight
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

    def _domain_contains_point(self, point: Point, holes: list[list[Point]]) -> bool:
        if not self.contains_point(point):
            return False
        return not any(is_point_in_polygon(point, hole) and not _point_on_boundary(point, hole) for hole in holes)

    def _segment_inside_domain(
        self,
        start: Point,
        end: Point,
        holes: list[list[Point]],
        allow_hole_endpoint: Point | None = None,
    ) -> bool:
        outer = self.as_list()
        return self._segment_inside_boundaries(
            start,
            end,
            [outer, *holes],
            lambda midpoint: self._domain_contains_point(midpoint, holes),
            allow_boundary_endpoint=allow_hole_endpoint,
        )

    def _splice_hole(self, hole: list[Point]) -> Polygon:
        outer = self.as_list()
        hole_vertex_index = max(range(len(hole)), key=lambda index: (hole[index].x, -hole[index].y))
        hole_vertex = hole[hole_vertex_index]

        candidates = []
        for outer_index, outer_vertex in enumerate(outer):
            if not self._segment_inside_domain(hole_vertex, outer_vertex, [hole], allow_hole_endpoint=hole_vertex):
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
        return Polygon(merged)

    def triangulate_with_holes(
        self, holes: list[list[Point]] | None = None
    ) -> tuple[list[tuple[Point, Point, Point]], list[Point]]:
        holes = holes or []
        merged_polygon = self.ensure_ccw()
        for hole in holes:
            merged_polygon = merged_polygon._splice_hole(_ensure_cw(list(hole)))

        triangle_indices, merged_vertices = merged_polygon.triangulate()
        triangles = [tuple(merged_vertices[index] for index in triangle) for triangle in triangle_indices]
        return triangles, merged_vertices

    def triangulation_with_diagonals(self) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
        return _ear_clip(self.as_list(), collect_diagonals=True)

    def hertel_mehlhorn(self) -> tuple[list[list[int]], list[Point]]:
        triangles, diagonals, polygon = self.triangulation_with_diagonals()
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

    def is_convex(self) -> bool:
        polygon = self.vertices
        if len(polygon) < 3:
            return True

        turn_directions = [
            cross_product(polygon[i], polygon[(i + 1) % len(polygon)], polygon[(i + 2) % len(polygon)])
            for i in range(len(polygon))
        ]
        non_zero_turns = [turn > 0 for turn in turn_directions if abs(turn) > 1e-9]
        return all(non_zero_turns) or not any(non_zero_turns)

    def reflex_vertices(self) -> list[Point]:
        if len(self.vertices) < 3:
            return []

        poly = self.ensure_ccw().as_list()
        reflex = []
        for i in range(len(poly)):
            p_prev = poly[i - 1]
            p_curr = poly[i]
            p_next = poly[(i + 1) % len(poly)]
            if cross_product(p_prev, p_curr, p_next) < -1e-9:
                reflex.append(p_curr)
        return reflex

    def convex_diameter(self) -> float:
        polygon = self.vertices
        if len(polygon) < 2:
            return 0.0
        if len(polygon) == 2:
            return distance(polygon[0], polygon[1])

        n = len(polygon)
        max_d_sq = 0.0
        k = 1

        for i in range(n):
            while True:
                area = abs(cross_product(polygon[i], polygon[(i + 1) % n], polygon[k]))
                next_area = abs(
                    cross_product(polygon[i], polygon[(i + 1) % n], polygon[(k + 1) % n])
                )
                if next_area > area:
                    k = (k + 1) % n
                else:
                    break

            d1 = (polygon[i].x - polygon[k].x) ** 2 + (polygon[i].y - polygon[k].y) ** 2
            d2 = (
                (polygon[(i + 1) % n].x - polygon[k].x) ** 2
                + (polygon[(i + 1) % n].y - polygon[k].y) ** 2
            )
            max_d_sq = max(max_d_sq, d1, d2)

        return math.sqrt(max_d_sq)

    @classmethod
    def from_random_convex(
        cls,
        num_points: int = 10,
        x_range: tuple[float, float] = (0, 100),
        y_range: tuple[float, float] = (0, 100),
    ) -> Polygon:
        points = [
            Point(random.uniform(*x_range), random.uniform(*y_range), index)
            for index in range(num_points)
        ]
        return cls(ConvexHull.monotone_chain(points))

    @classmethod
    def from_simple_random(
        cls,
        n_points: int = 20,
        x_range: tuple[float, float] = (0, 100),
        y_range: tuple[float, float] = (0, 100),
    ) -> Polygon:
        points = [
            Point(random.uniform(*x_range), random.uniform(*y_range), index)
            for index in range(n_points)
        ]
        center_x = sum(point.x for point in points) / n_points
        center_y = sum(point.y for point in points) / n_points
        ordered = sorted(points, key=lambda point: math.atan2(point.y - center_y, point.x - center_x))
        return cls(Point(point.x, point.y, index) for index, point in enumerate(ordered))


def get_polygon_properties(polygon: list[Point]) -> tuple[float, Point, str]:
    properties = Polygon(polygon).properties()
    return properties.area, properties.centroid, properties.orientation


def is_point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    return Polygon(polygon).contains_point(point)


def is_ear(a: Point, b: Point, c: Point, polygon: list[Point]) -> bool:
    return _is_ear(a, b, c, polygon)


def triangulate_polygon(polygon: list[Point]) -> tuple[list[tuple[int, int, int]], list[Point]]:
    return Polygon(polygon).triangulate()


def visibility_polygon(viewpoint: Point, polygon: list[Point]) -> list[Point]:
    return Polygon(polygon).visibility_polygon(viewpoint)


def polygon_kernel(polygon: list[Point]) -> list[Point]:
    return Polygon(polygon).kernel()


def shortest_path_in_polygon(
    polygon: list[Point], source: Point, target: Point
) -> tuple[list[Point], float]:
    return Polygon(polygon).shortest_path(source, target)


def triangulate_polygon_with_holes(
    outer_boundary: list[Point],
    holes: list[list[Point]] | None = None,
) -> tuple[list[tuple[Point, Point, Point]], list[Point]]:
    return Polygon(outer_boundary).triangulate_with_holes(holes)


def get_triangulation_with_diagonals(
    polygon: list[Point],
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
    return Polygon(polygon).triangulation_with_diagonals()


def hertel_mehlhorn(polygon_input: list[Point]) -> tuple[list[list[int]], list[Point]]:
    return Polygon(polygon_input).hertel_mehlhorn()


def graham_scan(points: list[Point]) -> list[Point]:
    return ConvexHull.graham_scan(points)


def monotone_chain(points: list[Point]) -> list[Point]:
    return ConvexHull.monotone_chain(points)


def generate_random_convex_polygon(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    return Polygon.from_random_convex(num_points, x_range, y_range).as_list()


def is_convex(polygon: list[Point]) -> bool:
    return Polygon(polygon).is_convex()


def generate_simple_polygon(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    return Polygon.from_simple_random(n_points, x_range, y_range).as_list()


def get_reflex_vertices(polygon: list[Point]) -> list[Point]:
    return Polygon(polygon).reflex_vertices()


def generate_points_in_triangle(
    a: Union[Point, Point3D],
    b: Union[Point, Point3D],
    c: Union[Point, Point3D],
    n_points: int = 100,
) -> list[Union[Point, Point3D]]:
    """Sample points uniformly from the interior of a triangle (2D or 3D)."""
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
            az = getattr(a, "z", 0.0)
            bz = getattr(b, "z", 0.0)
            cz = getattr(c, "z", 0.0)
            pz = az + r1 * (bz - az) + r2 * (cz - az)
            samples.append(Point3D(px, py, pz))
        else:
            samples.append(Point(px, py))

    return samples


def get_convex_diameter(polygon: List[Point]) -> float:
    return Polygon(polygon).convex_diameter()


__all__ = [
    "ConvexHull",
    "Polygon",
    "PolygonProperties",
    "generate_points_in_triangle",
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "get_convex_diameter",
    "get_polygon_properties",
    "get_reflex_vertices",
    "get_triangulation_with_diagonals",
    "graham_scan",
    "hertel_mehlhorn",
    "is_convex",
    "is_ear",
    "is_point_in_polygon",
    "monotone_chain",
    "polygon_kernel",
    "shortest_path_in_polygon",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
    "visibility_polygon",
]
