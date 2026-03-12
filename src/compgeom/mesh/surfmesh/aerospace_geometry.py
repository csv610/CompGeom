"""Aerospace and Planetary geometry algorithms."""
import math
from typing import List, Tuple

from ..mesh import TriangleMesh
from ...kernel import Point3D

class AerospaceGeometry:
    """Provides algorithms for spacecraft design and planetary mapping."""

    @staticmethod
    def wgs84_to_ecef(lat: float, lon: float, alt: float) -> Point3D:
        """
        Converts Geodetic coordinates (WGS84) to ECEF (Earth-Centered, Earth-Fixed) 3D points.
        lat, lon in degrees.
        """
        # WGS84 constants
        a = 6378137.0 # semi-major axis
        f = 1 / 298.257223563 # flattening
        e2 = 2*f - f**2 # eccentricity squared
        
        rad_lat = math.radians(lat)
        rad_lon = math.radians(lon)
        
        n = a / math.sqrt(1 - e2 * math.sin(rad_lat)**2)
        
        x = (n + alt) * math.cos(rad_lat) * math.cos(rad_lon)
        y = (n + alt) * math.cos(rad_lat) * math.sin(rad_lon)
        z = (n * (1 - e2) + alt) * math.sin(rad_lat)
        
        return Point3D(x, y, z)

    @staticmethod
    def generate_ellipsoid_mesh(a: float, b: float, c: float, resolution: int = 30) -> TriangleMesh:
        """
        Generates a 3D mesh of an ellipsoid (standard for planetary body modeling).
        a, b, c: semi-axes lengths.
        """
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            theta = math.pi * i / resolution # 0 to pi
            for j in range(resolution + 1):
                phi = 2 * math.pi * j / resolution # 0 to 2pi
                
                x = a * math.sin(theta) * math.cos(phi)
                y = b * math.sin(theta) * math.sin(phi)
                z = c * math.cos(theta)
                vertices.append(Point3D(x, y, z))
                
        for i in range(resolution):
            for j in range(resolution):
                p1 = i * (resolution + 1) + j
                p2 = p1 + (resolution + 1)
                
                faces.append((p1, p2, p1 + 1))
                faces.append((p1 + 1, p2, p2 + 1))
                
        return TriangleMesh(vertices, faces)

    @staticmethod
    def rotation_stability(inertia_tensor: Tuple[Tuple[float, ...], ...]) -> str:
        """
        Analyzes the rotational stability of a spacecraft based on its inertia tensor.
        Uses the Intermediate Axis Theorem (Tennis Racket Effect).
        """
        import numpy as np
        it = np.array(inertia_tensor)
        eigenvalues = np.sort(np.linalg.eigvals(it))
        
        # Eigenvalues I1 < I2 < I3
        # Rotation is stable around I1 (minimum) and I3 (maximum)
        # Unstable around I2 (intermediate)
        return f"Stable axes: Major ({eigenvalues[2]:.2f}) and Minor ({eigenvalues[0]:.2f}). Unstable: Intermediate ({eigenvalues[1]:.2f})."
