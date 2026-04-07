"""Mesh processing subpackage."""

from compgeom.mesh.surface.processing.smoothing import (
    laplacian_smoothing,
    bilateral_smoothing,
    taubin_smoothing,
)
from compgeom.mesh.surface.processing.subdivision import (
    loop_subdivision,
    catmull_clark,
)
from compgeom.mesh.surface.processing.repair import (
    fill_holes,
    flip_normals,
)
from compgeom.mesh.surface.processing.geometry import (
    mesh_offset,
    mesh_clipping,
)

__all__ = [
    "laplacian_smoothing",
    "bilateral_smoothing",
    "taubin_smoothing",
    "loop_subdivision",
    "catmull_clark",
    "fill_holes",
    "flip_normals",
    "mesh_offset",
    "mesh_clipping",
]
