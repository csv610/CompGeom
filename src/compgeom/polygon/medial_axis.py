"""Approximate medial axis for simple 2D polygons."""

from __future__ import annotations

import math
from typing import List, Set, Tuple, Sequence, Dict

from compgeom.kernel import Point2D, triangle_circumcenter, length, sub
from compgeom.polygon.polygon import Polygon
from compgeom.mesh.surface.trimesh.delaunay_triangulation import build_topology, triangulate
from compgeom.polygon.tolerance import EPSILON


def sample_boundary_for_medial_axis(polygon: Polygon | Sequence[Point2D], max_segment_length: float = 0.25) -> list[Point2D]:
    """Samples the boundary of a polygon for medial axis approximation."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    ordered = poly_obj.ensure_ccw().as_list()
    perimeter_scale = max(max_segment_length, EPSILON)
    samples = []
    next_id = 0

    for index, start in enumerate(ordered):
        end = ordered[(index + 1) % len(ordered)]
        samples.append(Point2D(start.x, start.y, next_id))
        next_id += 1

        segment_len = length(sub(start, end))
        subdivisions = max(1, int(segment_len / perimeter_scale))
        for step in range(1, subdivisions):
            t = step / subdivisions
            samples.append(
                Point2D(
                    start.x + t * (end.x - start.x),
                    start.y + t * (end.y - start.y),
                    next_id,
                )
            )
            next_id += 1
    return samples


def approximate_medial_axis(polygon: Polygon | Sequence[Point2D], resolution: float = 0.25) -> dict:
    """Approximate the medial axis of a polygon using Delaunay triangulation."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    if len(poly_obj) < 3:
        return {"samples": [], "centers": [], "segments": []}

    boundary_samples = sample_boundary_for_medial_axis(poly_obj, max_segment_length=resolution)
    mesh_obj = triangulate(boundary_samples)
    sampled_triangles = [(mesh_obj.vertices[f[0]], mesh_obj.vertices[f[1]], mesh_obj.vertices[f[2]]) for f in mesh_obj.faces]
    if not sampled_triangles:
        return {"samples": boundary_samples, "centers": [], "segments": []}

    mesh = build_topology(sampled_triangles)
    interior_centers = {}
    centers = []
    next_center_id = 0

    def triangle_centroid(triangle):
        a, b, c = triangle
        return Point2D((a.x + b.x + c.x) / 3.0, (a.y + b.y + c.y) / 3.0)

    for triangle_index, mesh_triangle in enumerate(mesh):
        triangle = tuple(mesh_triangle.vertices)
        centroid = triangle_centroid(triangle)
        if not poly_obj.contains_point(centroid):
            continue

        center = triangle_circumcenter(*triangle)
        if center is None or not poly_obj.contains_point(Point2D(center.x, center.y)):
            continue

        interior_centers[triangle_index] = Point2D(center.x, center.y, next_center_id)
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
            if length(sub(start, end)) <= EPSILON:
                continue
            
            # Segment key
            ka = (round(start.x / EPSILON), round(start.y / EPSILON))
            kb = (round(end.x / EPSILON), round(end.y / EPSILON))
            key = (ka, kb) if ka <= kb else (kb, ka)
            segments[key] = (start, end)

    return {
        "samples": boundary_samples,
        "centers": centers,
        "segments": list(segments.values()),
    }


__all__ = ["sample_boundary_for_medial_axis", "approximate_medial_axis"]
