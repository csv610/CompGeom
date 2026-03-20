"""Boundary Representation (BREP) and NURBS/Parametric Kernel."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Union
import numpy as np
import math

from compgeom.kernel import Point3D

class ParametricCurve(ABC):
    """Abstract interface for parametric curves C(t)."""
    @abstractmethod
    def evaluate(self, t: float) -> Point3D:
        """Evaluates the curve at parameter t in [0, 1]."""
        pass

    @abstractmethod
    def tangent(self, t: float) -> np.ndarray:
        """Returns the tangent vector at parameter t."""
        pass

class ParametricSurface(ABC):
    """Abstract interface for parametric surfaces S(u, v)."""
    @abstractmethod
    def evaluate(self, u: float, v: float) -> Point3D:
        """Evaluates the surface at parameters (u, v) in [0, 1]^2."""
        pass

    @abstractmethod
    def normal(self, u: float, v: float) -> np.ndarray:
        """Returns the surface normal at parameters (u, v)."""
        pass

class BezierSurface(ParametricSurface):
    """
    Implements a tensor-product Bezier surface patch.
    """
    def __init__(self, control_points: np.ndarray):
        """
        control_points: (M, N, 3) array of control points.
        """
        self.cp = control_points
        self.m, self.n = control_points.shape[:2]

    def evaluate(self, u: float, v: float) -> Point3D:
        # Bernstein basis evaluation
        def bernstein(n, i, t):
            return math.comb(n, i) * (t**i) * ((1 - t)**(n - i))

        p = np.zeros(3)
        for i in range(self.m):
            bu = bernstein(self.m - 1, i, u)
            for j in range(self.n):
                bv = bernstein(self.n - 1, j, v)
                p += bu * bv * self.cp[i, j]
        return Point3D(p[0], p[1], p[2])

    def normal(self, u: float, v: float) -> np.ndarray:
        # Numerical differentiation for normal calculation
        eps = 1e-5
        p = self.evaluate(u, v)
        pu = self.evaluate(u + eps, v)
        pv = self.evaluate(u, v + eps)
        
        du = np.array([pu.x - p.x, pu.y - p.y, getattr(pu, 'z', 0.0) - getattr(p, 'z', 0.0)])
        dv = np.array([pv.x - p.x, pv.y - p.y, getattr(pv, 'z', 0.0) - getattr(p, 'z', 0.0)])
        
        n = np.cross(du, dv)
        return n / (np.linalg.norm(n) + 1e-12)

class NURBSSurface(ParametricSurface):
    """
    Placeholder for a full Non-Uniform Rational B-Spline surface implementation.
    """
    def __init__(self, control_points: np.ndarray, weights: np.ndarray, knots_u: List[float], knots_v: List[float]):
        pass

    def evaluate(self, u: float, v: float) -> Point3D:
        return Point3D(0, 0, 0) # Placeholder

    def normal(self, u: float, v: float) -> np.ndarray:
        return np.array([0, 0, 1]) # Placeholder
