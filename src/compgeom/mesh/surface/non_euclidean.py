"""Non-Euclidean Geometry.

Simple re-export module for non-Euclidean geometry tools.

Submodules:
- stereographic: plane <-> sphere projection
- poincare_disk: hyperbolic geometry
- spherical_map: conformal sphere embedding
"""

import numpy as np

from compgeom.mesh.surface.stereographic import (
    stereographic_forward,
    stereographic_inverse,
)
from compgeom.mesh.surface.poincare_disk import (
    PoincareDiskEmbedding,
    poincare_disk_embedding,
    poincare_to_hyperbolic,
    hyperbolic_distance,
)
from compgeom.mesh.surface.spherical_map import (
    SphericalConformalMap,
    hemisphere_embedding,
)


def poincare_disk_map(mesh, boundary_type: str = "circle"):
    """Convenience function for Poincaré disk embedding.

    Note: Requires TutteEmbedding from tutte_embedding module.
    """
    from compgeom.mesh.surface.tutte_embedding import TutteEmbedding

    solver = TutteEmbedding(mesh)
    u, v = solver.compute_embedding(boundary_type=boundary_type, iterations=50)

    n = len(mesh.nodes)
    coords = np.zeros((n, 2))
    for i in range(n):
        norm = np.sqrt(u[i] ** 2 + v[i] ** 2)
        if norm < 1 - 1e-10:
            r = (1 - np.sqrt(1 - norm**2)) / norm * norm if norm > 1e-10 else 0
            coords[i, 0] = u[i] * r
            coords[i, 1] = v[i] * r
        else:
            coords[i, 0] = u[i]
            coords[i, 1] = v[i]

    return [(coords[i, 0], coords[i, 1]) for i in range(n)]
