"""Polynomial approximation for simple polygons."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from .polygon import Polygon

from ..kernel import Point2D


def solve_linear_system(matrix: List[List[float]], b: List[float]) -> List[float]:
    """Solve Ax = b using Gaussian elimination."""
    n = len(b)
    # Forward elimination
    for i in range(n):
        pivot = matrix[i][i]
        for j in range(i + 1, n):
            factor = matrix[j][i] / pivot
            for k in range(i, n):
                matrix[j][k] -= factor * matrix[i][k]
            b[j] -= factor * b[i]

    # Back substitution
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = b[i]
        for j in range(i + 1, n):
            x[i] -= matrix[i][j] * x[j]
        x[i] /= matrix[i][i]
    return x


def approximate_polynomials(polygon: Polygon, order: int) -> Tuple[List[float], List[float]]:
    """
    Fits parametric polynomials x(t) and y(t) of a given order to the polygon vertices.
    t is normalized arc length [0, 1].
    
    Returns:
        A tuple (x_coeffs, y_coeffs) where coeffs are [a0, a1, ..., an] 
        for sum(ai * t^i).
    """
    vertices = polygon.vertices
    if not vertices:
        return [], []
    
    n = len(vertices)
    # Calculate cumulative distance (arc length)
    distances = [0.0]
    total_dist = 0.0
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
        total_dist += dist
        distances.append(total_dist)
    
    # Parametrize t in [0, 1]
    # We include the last vertex (closing the loop) to ensure periodicity
    # So we have n+1 data points
    t_values = [d / total_dist for d in distances]
    x_values = [p.x for p in vertices] + [vertices[0].x]
    y_values = [p.y for p in vertices] + [vertices[0].y]
    
    m = order + 1
    # Build normal equations: (T^T * T) * c = T^T * y
    # matrix[i][j] = sum(t_k^(i+j))
    # rhs_x[i] = sum(x_k * t_k^i)
    
    matrix = [[0.0] * m for _ in range(m)]
    rhs_x = [0.0] * m
    rhs_y = [0.0] * m
    
    for tk, xk, yk in zip(t_values, x_values, y_values):
        powers = [tk**i for i in range(2 * order + 1)]
        for i in range(m):
            rhs_x[i] += xk * powers[i]
            rhs_y[i] += yk * powers[i]
            for j in range(m):
                matrix[i][j] += powers[i + j]
                
    # Solve for coefficients
    x_coeffs = solve_linear_system([row[:] for row in matrix], rhs_x)
    y_coeffs = solve_linear_system([row[:] for row in matrix], rhs_y)
    
    return x_coeffs, y_coeffs


def evaluate_polynomial(coeffs: List[float], t: float) -> float:
    """Evaluate polynomial sum(ai * t^i) using Horner's method."""
    res = 0.0
    for c in reversed(coeffs):
        res = res * t + c
    return res
