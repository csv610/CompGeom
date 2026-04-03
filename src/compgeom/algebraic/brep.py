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
    Non-Uniform Rational B-Spline (NURBS) surface implementation.
    Uses tensor product of B-spline basis functions with homogeneous coordinates.
    """
    def __init__(self, control_points: np.ndarray, weights: np.ndarray,
                 knots_u: List[float], knots_v: List[float],
                 degree_u: int = 3, degree_v: int = 3):
        """
        Args:
            control_points: (m, n, 3) array of control points
            weights: (m, n) array of weights
            knots_u: Knot vector in u direction (length m + degree_u + 1)
            knots_v: Knot vector in v direction (length n + degree_v + 1)
            degree_u: Degree in u direction
            degree_v: Degree in v direction
        """
        self.cp = control_points
        self.weights = weights
        self.knots_u = knots_u
        self.knots_v = knots_v
        self.degree_u = degree_u
        self.degree_v = degree_v
        self.m = control_points.shape[0]
        self.n = control_points.shape[1]

    def _find_knot_span(self, u: float, knots: List[float], degree: int, n: int) -> int:
        """Find the knot span index for parameter u."""
        if u >= knots[n]:
            return n - 1
        if u <= knots[degree]:
            return degree

        low, high = degree, n
        mid = (low + high) // 2
        while u < knots[mid] or u >= knots[mid + 1]:
            if u < knots[mid]:
                high = mid
            else:
                low = mid
            mid = (low + high) // 2
        return mid

    def _basis_function(self, i: int, p: int, u: float, knots: List[float]) -> float:
        """
        Compute B-spline basis function N_{i,p}(u) using Cox-de Boor recursion.
        """
        if p == 0:
            return 1.0 if knots[i] <= u < knots[i + 1] else 0.0

        # Handle endpoint case
        if u == knots[-1] and i == len(knots) - p - 2:
            return 1.0

        left = 0.0
        right = 0.0

        denom1 = knots[i + p] - knots[i]
        if denom1 != 0:
            left = (u - knots[i]) / denom1 * self._basis_function(i, p - 1, u, knots)

        denom2 = knots[i + p + 1] - knots[i + 1]
        if denom2 != 0:
            right = (knots[i + p + 1] - u) / denom2 * self._basis_function(i + 1, p - 1, u, knots)

        return left + right

    def evaluate(self, u: float, v: float) -> Point3D:
        """Evaluate NURBS surface at (u, v) using rational basis functions."""
        # Clamp parameters to [0, 1]
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))

        # Map to knot domain
        u_knot = u * (self.knots_u[-1] - self.knots_u[0]) + self.knots_u[0]
        v_knot = v * (self.knots_v[-1] - self.knots_v[0]) + self.knots_v[0]

        # Find knot spans
        span_u = self._find_knot_span(u_knot, self.knots_u, self.degree_u, self.m)
        span_v = self._find_knot_span(v_knot, self.knots_v, self.degree_v, self.n)

        # Evaluate basis functions
        basis_u = [self._basis_function(i, self.degree_u, u_knot, self.knots_u)
                   for i in range(span_u - self.degree_u, span_u + 1)]
        basis_v = [self._basis_function(j, self.degree_v, v_knot, self.knots_v)
                   for j in range(span_v - self.degree_v, span_v + 1)]

        # Compute weighted point (in homogeneous coordinates)
        xh, yh, zh, wh = 0.0, 0.0, 0.0, 0.0
        for ii, i in enumerate(range(span_u - self.degree_u, span_u + 1)):
            for jj, j in enumerate(range(span_v - self.degree_v, span_v + 1)):
                if 0 <= i < self.m and 0 <= j < self.n:
                    b = basis_u[ii] * basis_v[jj]
                    w = self.weights[i, j]
                    xh += self.cp[i, j, 0] * w * b
                    yh += self.cp[i, j, 1] * w * b
                    zh += self.cp[i, j, 2] * w * b
                    wh += w * b

        # Project from homogeneous coordinates
        if abs(wh) < 1e-12:
            wh = 1.0
        return Point3D(xh / wh, yh / wh, zh / wh)

    def normal(self, u: float, v: float) -> np.ndarray:
        """Compute surface normal via numerical differentiation."""
        eps = 1e-5

        p = self.evaluate(u, v)
        pu = self.evaluate(min(u + eps, 1.0), v)
        pv = self.evaluate(u, min(v + eps, 1.0))

        du = np.array([pu.x - p.x, pu.y - p.y, pu.z - p.z])
        dv = np.array([pv.x - p.x, pv.y - p.y, pv.z - p.z])

        n = np.cross(du, dv)
        norm = np.linalg.norm(n)
        return n / (norm + 1e-12)
