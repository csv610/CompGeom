"""Approximate medial axis for simple 2D polygons."""

from __future__ import annotations

from .geometry import EPSILON, Point, get_circumcenter, length, sub
from .polygon import is_point_in_polygon
from .mesh import build_topology, triangulate


def polygon_area(polygon):
    return 0.5 * sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


def ensure_ccw(polygon):
    return polygon if polygon_area(polygon) >= 0 else list(reversed(polygon))


def edge_length(a, b):
    return length(sub(a, b))


def sample_polygon_boundary(polygon, max_segment_length=0.25):
    polygon = ensure_ccw(list(polygon))
    perimeter_scale = max(max_segment_length, 1e-6)
    samples = []
    next_id = 0

    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        samples.append(Point(start.x, start.y, next_id))
        next_id += 1

        segment_len = edge_length(start, end)
        subdivisions = max(1, int(segment_len / perimeter_scale))
        for step in range(1, subdivisions):
            t = step / subdivisions
            samples.append(
                Point(
                    start.x + t * (end.x - start.x),
                    start.y + t * (end.y - start.y),
                    next_id,
                )
            )
            next_id += 1
    return samples


def triangle_centroid(triangle):
    a, b, c = triangle
    return Point((a.x + b.x) / 3.0, (a.y + b.y) / 3.0)


def triangle_circumcenter(triangle):
    return get_circumcenter(*triangle)


def point_key(point):
    return (round(point.x / EPSILON), round(point.y / EPSILON))


def segment_key(a, b):
    ka = point_key(a)
    kb = point_key(b)
    return (ka, kb) if ka <= kb else (kb, ka)


def approximate_medial_axis(polygon, max_segment_length=0.25):
    if len(polygon) < 3:
        return {"samples": [], "centers": [], "segments": []}

    boundary_samples = sample_polygon_boundary(polygon, max_segment_length=max_segment_length)
    sampled_triangles, _ = triangulate(boundary_samples)
    if not sampled_triangles:
        return {"samples": boundary_samples, "centers": [], "segments": []}

    mesh = build_topology(sampled_triangles)
    interior_centers = {}
    centers = []
    next_center_id = 0

    for triangle_index, mesh_triangle in enumerate(mesh):
        triangle = tuple(mesh_triangle.vertices)
        centroid = triangle_centroid(triangle)
        if not is_point_in_polygon(centroid, polygon):
            continue

        center = triangle_circumcenter(triangle)
        if center is None or not is_point_in_polygon(center, polygon):
            continue

        interior_centers[triangle_index] = Point(center.x, center.y, next_center_id)
        centers.append(interior_centers[triangle_index])
        next_center_id += 1

    segments = {}
    for triangle_index, mesh_triangle in enumerate(mesh):
        if triangle_index not in interior_centers:
            continue
        for neighbor in mesh_triangle.neighbors:
            if neighbor is None:
                continue
            neighbor_index = mesh.index(neighbor)
            if neighbor_index not in interior_centers:
                continue
            start = interior_centers[triangle_index]
            end = interior_centers[neighbor_index]
            if edge_length(start, end) <= EPSILON:
                continue
            segments[segment_key(start, end)] = (start, end)

    return {
        "samples": boundary_samples,
        "centers": centers,
        "segments": list(segments.values()),
    }


__all__ = ["approximate_medial_axis", "sample_polygon_boundary"]
