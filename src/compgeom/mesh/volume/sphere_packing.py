"""Sphere packing algorithms inside closed surface meshes."""

from __future__ import annotations

import math
import random
from typing import List, Tuple

import numpy as np
from scipy.spatial import KDTree

from compgeom.kernel import Point3D, distance_3d
from compgeom.kernel.sphere import Sphere
from compgeom.kernel.math_utils import EPSILON

INSIDE_MARGIN = 1e-6


def pack_spheres_in_mesh(
    vertices: List[Point3D],
    faces: List[List[int]],
    radius: float,
) -> List[Point3D]:
    """
    Packs spheres of a given radius into a closed surface mesh.

    Args:
        vertices: List of 3D points defining the mesh vertices.
        faces: List of faces (each face is a list of vertex indices).
        radius: Radius of spheres to pack.

    Returns:
        List of Point3D representing the centers of the packed spheres.
    """
    if not vertices or not faces or radius <= 0:
        return []

    vertices_array = np.array([[v.x, v.y, v.z] for v in vertices])

    min_bound = vertices_array.min(axis=0)
    max_bound = vertices_array.max(axis=0)

    dx = 2 * radius
    dy = 2 * radius
    dz = 2 * radius

    candidates = []
    x = min_bound[0] + radius
    while x <= max_bound[0] - radius:
        y = min_bound[1] + radius
        while y <= max_bound[1] - radius:
            z = min_bound[2] + radius
            while z <= max_bound[2] - radius:
                candidates.append(Point3D(x, y, z))
                z += dz
            y += dy
        x += dx

    packed = []
    for center in candidates:
        if is_sphere_inside_mesh(center, radius, vertices, faces):
            packed.append(center)

    return packed


def pack_spheres_best_position(
    vertices: List[Point3D],
    faces: List[List[int]],
    radius: float,
    num_iterations: int = 500,
    candidates_per_iteration: int = 1000,
) -> List[Point3D]:
    """
    Packs spheres using iterative best-position placement.
    At each iteration, finds the position that maximizes minimum distance
    to existing spheres and boundary.

    Args:
        vertices: List of 3D points defining the mesh vertices.
        faces: List of faces (each face is a list of vertex indices).
        radius: Radius of spheres to pack.
        num_iterations: Maximum number of spheres to place.
        candidates_per_iteration: Number of random candidates to try per sphere.

    Returns:
        List of Point3D representing the centers of the packed spheres.
    """
    vertices_array = np.array([[v.x, v.y, v.z] for v in vertices])

    min_bound = vertices_array.min(axis=0)
    max_bound = vertices_array.max(axis=0)

    packed = []
    packed_array = np.array([[p.x, p.y, p.z] for p in packed])

    if len(packed_array) > 0:
        tree = KDTree(packed_array)

    for _ in range(num_iterations):
        best_center = None
        best_min_dist = -1.0

        for _ in range(candidates_per_iteration):
            x = np.random.uniform(min_bound[0] + radius, max_bound[0] - radius)
            y = np.random.uniform(min_bound[1] + radius, max_bound[1] - radius)
            z = np.random.uniform(min_bound[2] + radius, max_bound[2] - radius)
            center = Point3D(x, y, z)

            if not is_sphere_inside_mesh(center, radius, vertices, faces):
                continue

            if len(packed_array) > 0:
                dists = tree.query([x, y, z], k=1)
                min_dist = dists[0]
            else:
                min_dist = float("inf")

            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_center = center

        if best_center is None:
            break

        packed.append(best_center)
        packed_array = np.array([[p.x, p.y, p.z] for p in packed])
        tree = KDTree(packed_array)

    return packed


def pack_spheres_greedy(
    vertices: List[Point3D],
    faces: List[List[int]],
    radius: float,
    min_distance: float | None = None,
) -> List[Point3D]:
    """
    Packs spheres using greedy placement - places each sphere at the
    largest possible position without overlapping existing spheres.

    Args:
        vertices: List of 3D points defining the mesh vertices.
        faces: List of faces (each face is a list of vertex indices).
        radius: Radius of spheres to pack.
        min_distance: Minimum distance between sphere centers. Defaults to 2*radius.

    Returns:
        List of Point3D representing the centers of the packed spheres.
    """
    if min_distance is None:
        min_distance = 2 * radius

    vertices_array = np.array([[v.x, v.y, v.z] for v in vertices])

    min_bound = vertices_array.min(axis=0)
    max_bound = vertices_array.max(axis=0)

    step = radius * 0.5
    candidates = []
    x = min_bound[0] + radius
    while x <= max_bound[0] - radius:
        y = min_bound[1] + radius
        while y <= max_bound[1] - radius:
            z = min_bound[2] + radius
            while z <= max_bound[2] - radius:
                candidates.append(Point3D(x, y, z))
                z += step
            y += step
        x += step

    candidates.sort(key=lambda p: min(distance_3d(p, v) for v in vertices), reverse=True)

    packed = []
    packed_array = np.array([[p.x, p.y, p.z] for p in packed]) if packed else np.array([]).reshape(0, 3)

    if len(packed_array) > 0:
        tree = KDTree(packed_array)

    for center in candidates:
        if not is_sphere_inside_mesh(center, radius, vertices, faces):
            continue

        if len(packed_array) > 0:
            dists = tree.query([center.x, center.y, center.z], k=1)
            if dists[0] < min_distance:
                continue

        packed.append(center)
        packed_array = np.array([[p.x, p.y, p.z] for p in packed])
        tree = KDTree(packed_array)

    return packed


def is_sphere_inside_mesh(
    center: Point3D,
    radius: float,
    vertices: List[Point3D],
    faces: List[List[int]],
) -> bool:
    """
    Checks if a sphere is entirely contained within a closed mesh.

    Args:
        center: Center of the sphere.
        radius: Radius of the sphere.
        vertices: Mesh vertices.
        faces: Mesh faces.

    Returns:
        True if sphere is fully inside the mesh.
    """
    if not _is_point_inside_mesh(center, vertices, faces):
        return False

    for face in faces:
        if len(face) < 3:
            continue

        v0 = vertices[face[0]]
        for i in range(1, len(face) - 1):
            v1 = vertices[face[i]]
            v2 = vertices[face[i + 1]]

            dist = _point_to_triangle_distance(center, v0, v1, v2)
            if dist < radius - EPSILON:
                return False

    return True


def _is_point_inside_mesh(
    point: Point3D,
    vertices: List[Point3D],
    faces: List[List[int]],
) -> bool:
    """Ray casting to check if point is inside closed mesh."""
    vertices_array = np.array([[v.x, v.y, v.z] for v in vertices])

    offsets = [INSIDE_MARGIN, 0.5 * INSIDE_MARGIN, 2 * INSIDE_MARGIN]
    for offset in offsets:
        for _ in range(3):
            ray_dir = np.array([0, 0, 1])
            ray_origin = np.array([point.x + offset, point.y + offset, point.z + offset])

            intersections = 0
            for face in faces:
                if len(face) < 3:
                    continue

                tri = [vertices_array[i] for i in face[:3]]
                if _ray_triangle_intersect(ray_origin, ray_dir, tri):
                    intersections += 1

            if (intersections % 2) == 1:
                return True

            offset *= 2

    return False


def _ray_triangle_intersect(
    ray_origin: np.ndarray,
    ray_dir: np.ndarray,
    tri: List[np.ndarray],
) -> bool:
    """Möller-Trumbore ray-triangle intersection."""
    epsilon = 1e-9

    v0, v1, v2 = tri[0], tri[1], tri[2]
    edge1 = v1 - v0
    edge2 = v2 - v0

    h = np.cross(ray_dir, edge2)
    a = np.dot(edge1, h)

    if abs(a) < epsilon:
        return False

    f = 1.0 / a
    s = ray_origin - v0
    u = f * np.dot(s, h)

    if u < 0.0 or u > 1.0:
        return False

    q = np.cross(s, edge1)
    v = f * np.dot(ray_dir, q)

    if v < 0.0 or u + v > 1.0:
        return False

    t = f * np.dot(edge2, q)
    return t > epsilon


def _point_to_triangle_distance(
    point: Point3D,
    v0: Point3D,
    v1: Point3D,
    v2: Point3D,
) -> float:
    """Computes the minimum distance from a point to a triangle."""
    p = np.array([point.x, point.y, point.z])
    a = np.array([v0.x, v0.y, v0.z])
    b = np.array([v1.x, v1.y, v1.z])
    c = np.array([v2.x, v2.y, v2.z])

    ab = b - a
    ac = c - a
    ap = p - a

    d1 = np.dot(ab, ap)
    d2 = np.dot(ac, ap)
    d3 = np.dot(ab, ab)
    d4 = np.dot(ab, ac)
    d5 = np.dot(ac, ac)

    denom = d3 * d5 - d4 * d4
    if abs(denom) < 1e-12:
        return min(distance_3d(point, v0), distance_3d(point, v1), distance_3d(point, v2))

    s = (d1 * d5 - d2 * d4) / denom
    t = (d1 * d4 - d2 * d3) / denom

    if s >= 0 and t >= 0 and s + t <= 1:
        proj = a + s * ab + t * ac
        return np.linalg.norm(p - proj)

    return min(
        _point_to_segment_distance(p, a, b),
        _point_to_segment_distance(p, b, c),
        _point_to_segment_distance(p, c, a),
    )


def _point_to_segment_distance(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    """Distance from point to line segment."""
    ab = b - a
    ap = p - a

    t = max(0, min(1, np.dot(ap, ab) / np.dot(ab, ab)))
    proj = a + t * ab

    return np.linalg.norm(p - proj)


def optimal_sphere_radius(
    vertices: List[Point3D],
    faces: List[List[int]],
    num_spheres: int,
    tolerance: float = 1e-3,
) -> float:
    """
    Finds the maximum radius such that at least `num_spheres` can be packed.

    Args:
        vertices: Mesh vertices.
        faces: Mesh faces.
        num_spheres: Target number of spheres.
        tolerance: Precision for binary search.

    Returns:
        Maximum radius that fits at least num_spheres.
    """
    if not vertices or num_spheres <= 0:
        return 0.0

    vertices_array = np.array([[v.x, v.y, v.z] for v in vertices])
    min_bound = vertices_array.min(axis=0)
    max_bound = vertices_array.max(axis=0)

    extent = max_bound - min_bound
    high = float(max(extent)) / 2.0
    low = 0.0

    if high <= 0:
        return 0.0

    best_radius = 0.0

    for _ in range(30):
        if high - low < tolerance:
            break

        mid = (low + high) / 2.0
        centers = pack_spheres_in_mesh(vertices, faces, mid)

        if len(centers) >= num_spheres:
            best_radius = mid
            low = mid
        else:
            high = mid

    return best_radius


def calculate_packing_efficiency(
    vertices: List[Point3D],
    faces: List[List[int]],
    centers: List[Point3D],
    radius: float,
) -> float:
    """
    Calculates packing efficiency as ratio of sphere volume to mesh volume.

    Args:
        vertices: Mesh vertices.
        faces: Mesh faces.
        centers: Sphere centers.
        radius: Sphere radius.

    Returns:
        Packing efficiency as percentage (0-100).
    """
    if not centers or radius <= 0:
        return 0.0

    mesh_volume = _calculate_mesh_volume(vertices, faces)
    if mesh_volume <= 0:
        return 0.0

    sphere_volume = len(centers) * (4.0 / 3.0) * math.pi * (radius**3)
    return (sphere_volume / mesh_volume) * 100


def _calculate_mesh_volume(
    vertices: List[Point3D],
    faces: List[List[int]],
) -> float:
    """Calculates volume of a closed mesh using divergence theorem."""
    vertices_array = np.array([[v.x, v.y, v.z] for v in vertices])

    volume = 0.0
    for face in faces:
        if len(face) < 3:
            continue

        v0 = vertices_array[face[0]]
        if len(face) == 3:
            v1, v2 = vertices_array[face[1]], vertices_array[face[2]]
            tri = np.array([v0, v1, v2])
            normal = np.cross(v1 - v0, v2 - v0)
            center = (v0 + v1 + v2) / 3.0
            volume += np.dot(center, normal)
        else:
            v1 = vertices_array[face[1]]
            v2 = vertices_array[face[2]]
            v3 = vertices_array[face[3]]
            quad = np.array([v0, v1, v2, v3])
            c1 = (v0 + v1 + v2) / 3.0
            c2 = (v0 + v2 + v3) / 3.0
            n1 = np.cross(v1 - v0, v2 - v0)
            n2 = np.cross(v2 - v0, v3 - v0)
            volume += np.dot(c1, n1) + np.dot(c2, n2)

    return abs(volume) / 6.0


__all__ = [
    "pack_spheres_in_mesh",
    "pack_spheres_greedy",
    "pack_spheres_best_position",
    "is_sphere_inside_mesh",
    "optimal_sphere_radius",
    "calculate_packing_efficiency",
]
