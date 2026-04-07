"""Main orchestration for surface mesh repair."""

from __future__ import annotations

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.repair.duplicates import (
    remove_duplicate_points,
    remove_duplicate_faces,
    remove_isolated_vertices,
)
from compgeom.mesh.surface.repair.manifold import (
    remove_non_manifold_faces,
    remove_non_manifold_vertices,
    remove_degenerate_faces,
    remove_self_intersections,
)
from compgeom.mesh.surface.repair.components import remove_small_components
from compgeom.mesh.surface.repair.normals import fix_normals, orient_normals_outward


def repair(mesh: TriMesh) -> TriMesh:
    """Runs the standard repair pipeline."""
    mesh = remove_duplicate_points(mesh)
    mesh = remove_degenerate_faces(mesh)
    mesh = remove_duplicate_faces(mesh)
    mesh = remove_non_manifold_faces(mesh)
    mesh = remove_non_manifold_vertices(mesh)
    mesh = remove_self_intersections(mesh)
    mesh = fix_normals(mesh)
    mesh = orient_normals_outward(mesh)
    mesh = remove_small_components(mesh)
    mesh = remove_isolated_vertices(mesh)
    return mesh
