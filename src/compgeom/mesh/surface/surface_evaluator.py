"""Analytic and procedural surface evaluation interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
import numpy as np

from compgeom.kernel import Point3D

class SurfaceEvaluator(ABC):
    """
    Interface for objects that can evaluate surface properties (position, normal, curvature)
    at arbitrary parameters (u, v).
    Useful for conforming meshes to BREP/CAD analytic surfaces.
    """
    @abstractmethod
    def evaluate(self, u: float, v: float) -> Point3D:
        """Returns the 3D point at parameters (u, v)."""
        pass

    @abstractmethod
    def normal(self, u: float, v: float) -> np.ndarray:
        """Returns the surface normal at parameters (u, v)."""
        pass

    def tangent_u(self, u: float, v: float, eps: float = 1e-5) -> np.ndarray:
        """Computes numerical tangent in U direction."""
        p1 = self.evaluate(u - eps, v)
        p2 = self.evaluate(u + eps, v)
        t = np.array([p2.x - p1.x, p2.y - p1.y, getattr(p2, 'z', 0.0) - getattr(p1, 'z', 0.0)])
        return t / (np.linalg.norm(t) + 1e-12)

    def tangent_v(self, u: float, v: float, eps: float = 1e-5) -> np.ndarray:
        """Computes numerical tangent in V direction."""
        p1 = self.evaluate(u, v - eps)
        p2 = self.evaluate(u, v + eps)
        t = np.array([p2.x - p1.x, p2.y - p1.y, getattr(p2, 'z', 0.0) - getattr(p1, 'z', 0.0)])
        return t / (np.linalg.norm(t) + 1e-12)

class SphereEvaluator(SurfaceEvaluator):
    """Analytic evaluation for a sphere."""
    def __init__(self, center: Point3D, radius: float):
        self.center = center
        self.radius = radius

    def evaluate(self, u: float, v: float) -> Point3D:
        """u: azimuth [0, 2pi], v: inclination [0, pi]"""
        x = self.center.x + self.radius * math.cos(u) * math.sin(v)
        y = self.center.y + self.radius * math.sin(u) * math.sin(v)
        z = getattr(self.center, 'z', 0.0) + self.radius * math.cos(v)
        return Point3D(x, y, z)

    def normal(self, u: float, v: float) -> np.ndarray:
        p = self.evaluate(u, v)
        n = np.array([p.x - self.center.x, p.y - self.center.y, getattr(p, 'z', 0.0) - getattr(self.center, 'z', 0.0)])
        return n / self.radius

import math
