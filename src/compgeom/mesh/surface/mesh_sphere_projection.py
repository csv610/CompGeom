"""Sphere Projection: Projects a surface mesh onto a sphere."""

from __future__ import annotations

import numpy as np

from compgeom.kernel import Point3D
from compgeom.mesh.surface.smoothing import laplacian_smoothing
from compgeom.mesh.surface.surface_mesh import SurfaceMesh


def _compute_bounding_sphere(vertices: np.ndarray) -> tuple[np.ndarray, float]:
    """Compute bounding sphere (center and radius) from vertices."""
    center = np.mean(vertices, axis=0)
    radius = float(np.max(np.linalg.norm(vertices - center, axis=1)))
    return center, radius


def project(mesh: SurfaceMesh, smoothing_steps: int = 0) -> SurfaceMesh:
    """
    Projects a surface mesh onto its bounding sphere.

    Args:
        mesh: Input surface mesh to project.
        smoothing_steps: Number of Laplacian smoothing iterations to apply.

    Returns:
        New SurfaceMesh with vertices projected onto the sphere.
    """
    vertices = np.array([[v.x, v.y, v.z] for v in mesh.vertices], dtype=np.float64)
    faces = np.array(mesh.faces, dtype=np.int32)

    sphere_center, sphere_radius = _compute_bounding_sphere(vertices)

    centered_v = vertices - sphere_center
    dists = np.linalg.norm(centered_v, axis=1)
    dists[dists < 1e-12] = 1.0
    scales = sphere_radius / dists
    projected_vertices = sphere_center + centered_v * scales[:, np.newaxis]

    if smoothing_steps > 0:
        new_vertices = [Point3D(v[0], v[1], v[2]) for v in projected_vertices]
        smoothed_mesh = SurfaceMesh(new_vertices, [tuple(f) for f in faces])
        smoothed_mesh = laplacian_smoothing(smoothed_mesh, iterations=smoothing_steps)
        projected_vertices = np.array([[v.x, v.y, v.z] for v in smoothed_mesh.vertices], dtype=np.float64)
        centered_v = projected_vertices - sphere_center
        dists = np.linalg.norm(centered_v, axis=1)
        dists[dists < 1e-12] = 1.0
        scales = sphere_radius / dists
        projected_vertices = sphere_center + centered_v * scales[:, np.newaxis]

    new_vertices = [Point3D(v[0], v[1], v[2], id=i) for i, v in enumerate(projected_vertices)]
    return SurfaceMesh(new_vertices, [tuple(f) for f in faces])
