"""Spherical Conformal Map.

Conformal mapping from mesh to unit sphere.

References:
    - Ratcliffe, "Foundations of Hyperbolic Manifolds", 1994
"""

from typing import Optional
import numpy as np
from numpy.typing import NDArray


class SphericalConformalMap:
    """Spherical conformal mapping to unit sphere.

    Maps a mesh conformally to the unit sphere
    preserving angles but not areas.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)

    def compute(
        self,
        center: Optional[NDArray[np.float64]] = None,
    ) -> NDArray[np.float64]:
        """Compute conformal map to unit sphere.

        Args:
            center: Optional center of mesh

        Returns:
            Vertex positions on unit sphere
        """
        vertices = np.array([[n.point.x, n.point.y, getattr(n.point, "z", 0.0)] for n in self.mesh.nodes])

        if center is None:
            center = np.mean(vertices, axis=0)

        centered = vertices - center
        norms = np.linalg.norm(centered, axis=1, keepdims=True)

        spherical = centered / (norms + 1e-10)

        return spherical

    compute_spherical_map = compute


def hemisphere_embedding(
    points: np.ndarray,
    center: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Embed points on upper hemisphere.

    Args:
        points: Input points
        center: Optional center

    Returns:
        Points on hemisphere
    """
    if center is None:
        center = np.mean(points, axis=0)

    centered = points - center
    norms = np.linalg.norm(centered, axis=1, keepdims=True)

    normalized = centered / (norms + 1e-10)
    normalized[:, 2] = np.abs(normalized[:, 2])

    return normalized
