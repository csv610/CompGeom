"""Surface mesh repair subpackage."""

from compgeom.mesh.surface.repair.components import remove_small_components
from compgeom.mesh.surface.repair.core import repair
from compgeom.mesh.surface.repair.duplicates import (
    remove_duplicate_faces,
    remove_duplicate_points,
    remove_isolated_vertices,
)
from compgeom.mesh.surface.repair.manifold import (
    _get_triangle_coords,
    _tri_tri_intersect,
    remove_degenerate_faces,
    remove_non_manifold_faces,
    remove_non_manifold_vertices,
    remove_self_intersections,
)
from compgeom.mesh.surface.repair.normals import fix_normals, orient_normals_outward

__all__ = [
    "repair",
    "remove_duplicate_points",
    "remove_duplicate_faces",
    "remove_isolated_vertices",
    "remove_non_manifold_faces",
    "remove_non_manifold_vertices",
    "remove_degenerate_faces",
    "remove_self_intersections",
    "remove_small_components",
    "fix_normals",
    "orient_normals_outward",
]
