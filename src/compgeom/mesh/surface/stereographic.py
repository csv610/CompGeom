"""Stereographic Projection.

Forward and inverse stereographic projection between plane and sphere.

References:
    - Ratcliffe, "Foundations of Hyperbolic Manifolds", 1994
"""

from typing import List, Tuple
import numpy as np
from numpy.typing import NDArray


def stereographic_forward(
    points: List[Tuple[float, float]],
    radius: float = 1.0,
) -> NDArray[np.float64]:
    """Forward stereographic projection from plane to sphere.

    Args:
        points: List of (x, y) points on plane
        radius: Radius of target sphere (default 1.0)

    Returns:
        Array of (x, y, z) points on sphere
    """
    n = len(points)
    result = np.zeros((n, 3))

    for i, (x, y) in enumerate(points):
        r2 = x * x + y * y
        scale = radius * radius / (r2 + radius * radius)
        result[i, 0] = 2 * radius * x * scale
        result[i, 1] = 2 * radius * y * scale
        result[i, 2] = radius * (r2 - radius * radius) / (r2 + radius * radius)

    return result


def stereographic_inverse(
    sphere_points: NDArray[np.float64],
    radius: float = 1.0,
) -> List[Tuple[float, float]]:
    """Inverse stereographic projection from sphere to plane.

    Args:
        sphere_points: Array of (x, y, z) points on sphere
        radius: Radius of sphere (default 1.0)

    Returns:
        List of (x, y) points on plane
    """
    result = []

    for i in range(len(sphere_points)):
        x, y, z = sphere_points[i]
        if np.abs(z - radius) < 1e-10:
            result.append((float("inf"), float("inf")))
        else:
            scale = radius / (radius - z)
            result.append((x * scale / (2 * radius), y * scale / (2 * radius)))

    return result
