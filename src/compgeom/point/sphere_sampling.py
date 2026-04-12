"""Sphere and SO(3) sampling algorithms."""

from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple
from compgeom.kernel import Point3D

class SphereSampler:
    """Generates points on the surface of a unit sphere or rotations in SO(3)."""

    @staticmethod
    def healpix_sampling(n_side: int = 1) -> List[Point3D]:
        """Number of points is 12 * n_side^2."""
        n_pix = 12 * n_side * n_side
        points = []
        for i in range(n_pix):
            z, phi = SphereSampler._pix2ang_ring(n_side, i)
            theta = math.acos(z)
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            points.append(Point3D(x, y, z))
        return points

    @staticmethod
    def _pix2ang_ring(n_side: int, pix: int) -> Tuple[float, float]:
        n_cap = 2 * n_side * (n_side - 1)
        n_pix = 12 * n_side * n_side
        if pix < n_cap:
            i_ring = math.floor(math.sqrt(pix + 1.0 - 0.5)) + 1
            if i_ring > n_side: i_ring = n_side
            p_ring = pix + 1 - 2 * i_ring * (i_ring - 1)
            z = 1.0 - (i_ring**2) / (3.0 * n_side**2)
            phi = (p_ring - 0.5) * (math.pi / (2.0 * i_ring))
        elif pix < n_pix - n_cap:
            pix_rel = pix - n_cap
            i_ring = math.floor(pix_rel / (4 * n_side)) + n_side
            p_ring = (pix_rel % (4 * n_side)) + 1
            z = (4.0 * n_side - 2.0 * i_ring) / (3.0 * n_side)
            s_offset = 1 if (i_ring - n_side) % 2 == 0 else 0.5
            phi = (p_ring - s_offset * 0.5) * (math.pi / (2.0 * n_side))
        else:
            pix_inv = n_pix - pix - 1
            i_ring_inv = math.floor(math.sqrt(pix_inv + 1.0 - 0.5)) + 1
            i_ring = 4 * n_side - i_ring_inv
            p_ring = pix_inv + 1 - 2 * i_ring_inv * (i_ring_inv - 1)
            z = -1.0 + (i_ring_inv**2) / (3.0 * n_side**2)
            phi = (p_ring - 0.5) * (math.pi / (2.0 * i_ring_inv))
        return z, phi

    @staticmethod
    def sample_so3(n: int) -> List[Tuple[float, float, float, float]]:
        """
        Uniformly samples rotations in SO(3) as Quaternions (w, x, y, z).
        Uses the algorithm by James Arvo (1992).
        """
        quaternions = []
        for _ in range(n):
            u1, u2, u3 = np.random.rand(3)
            
            # Use u1 to sample the rotation around the Z axis
            # Use u2, u3 to sample the direction of the Z axis
            q = [
                math.sqrt(1 - u1) * math.sin(2 * math.pi * u2),
                math.sqrt(1 - u1) * math.cos(2 * math.pi * u2),
                math.sqrt(u1) * math.sin(2 * math.pi * u3),
                math.sqrt(u1) * math.cos(2 * math.pi * u3)
            ]
            quaternions.append(tuple(q))
        return quaternions

    @staticmethod
    def quaternion_to_matrix(q: Tuple[float, float, float, float]) -> np.ndarray:
        """Converts a quaternion (w, x, y, z) to a 3x3 rotation matrix."""
        w, x, y, z = q
        return np.array([
            [1 - 2*y*y - 2*z*z,     2*x*y - 2*z*w,     2*x*z + 2*y*w],
            [2*x*y + 2*z*w,         1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
            [2*x*z - 2*y*w,         2*y*z + 2*x*w,     1 - 2*x*x - 2*y*y]
        ])
