"""Poincaré Disk Model.

Hyperbolic geometry embedding in the Poincaré disk model.

References:
    - Ratcliffe, "Foundations of Hyperbolic Manifolds", 1994
    - Cannon et al., "Hyperbolic Geometry", 1997
"""

from typing import Optional
import numpy as np
from numpy.typing import NDArray


class PoincareDiskEmbedding:
    """Poincaré disk embedding for hyperbolic geometry."""

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)

    def compute(
        self,
        boundary_type: str = "circle",
    ) -> NDArray[np.float64]:
        """Compute Poincaré disk embedding.

        Args:
            boundary_type: "circle" (conformal) or "square"

        Returns:
            UV coordinates in Poincaré disk
        """
        from compgeom.mesh.surface.tutte_embedding import TutteEmbedding

        solver = TutteEmbedding(self.mesh)
        u, v = solver.compute_embedding(boundary_type=boundary_type, iterations=50)

        disk_coords = np.zeros((self.num_v, 2))

        for i in range(self.num_v):
            norm = np.sqrt(u[i] ** 2 + v[i] ** 2)
            if norm < 1 - 1e-10:
                r = (1 - np.sqrt(1 - norm**2)) / norm * norm if norm > 1e-10 else 0
                disk_coords[i, 0] = u[i] * r
                disk_coords[i, 1] = v[i] * r
            else:
                disk_coords[i, 0] = u[i]
                disk_coords[i, 1] = v[i]

        return disk_coords


def poincare_disk_embedding(
    points: NDArray[np.float64],
    center: Optional[NDArray[np.float64]] = None,
    scale: float = 1.0,
) -> NDArray[np.float64]:
    """Embed points in Poincaré disk model.

    Args:
        points: Input (x, y, z) points
        center: Optional center of mesh
        scale: Scale factor

    Returns:
        Points in Poincaré disk
    """
    if center is None:
        center = np.mean(points, axis=0)

    centered = points - center
    norms = np.linalg.norm(centered, axis=1, keepdims=True)

    result = np.zeros_like(points)
    for i in range(len(points)):
        if norms[i, 0] < 1e-10:
            result[i] = centered[i]
        else:
            r = norms[i, 0]
            result[i] = centered[i] / (scale * (1 + r)) if r <= scale else centered[i] / scale

    return result[:, :2]


def poincare_to_hyperbolic(
    disk_points: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Convert Poincaré disk point to hyperbolic distance.

    Args:
        disk_points: Points in Poincaré disk

    Returns:
        Hyperbolic distances
    """
    norms = np.linalg.norm(disk_points, axis=1)
    return 2 * np.arctanh(norms)


def hyperbolic_distance(
    p1: NDArray[np.float64],
    p2: NDArray[np.float64],
) -> float:
    """Compute hyperbolic distance between two points in Poincaré disk.

    Args:
        p1: First point
        p2: Second point

    Returns:
        Hyperbolic distance
    """
    diff = p1 - p2
    dist_sq = np.dot(diff, diff)

    norm1_sq = np.dot(p1, p1)
    norm2_sq = np.dot(p2, p2)

    if norm1_sq < 1e-10 or norm2_sq < 1e-10:
        return np.sqrt(dist_sq)

    cosh_d = (1 + norm1_sq + norm2_sq + dist_sq) / (2 * np.sqrt(norm1_sq * norm2_sq))

    if cosh_d < 1:
        return 0.0
    return np.arccosh(cosh_d)
