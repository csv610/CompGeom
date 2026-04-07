"""Centralized tolerance and epsilon configuration for robust floating-point operations."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING
from compgeom.kernel.point import Point2D

EPSILON: float = 1e-9

def is_zero(value: float, tol: float = EPSILON) -> bool:
    """Check if a floating point value is close to zero."""
    return abs(value) <= tol

def are_close(p1: Point2D, p2: Point2D, tol: float = EPSILON) -> bool:
    """Check if two 2D points are close to each other."""
    return abs(p1.x - p2.x) <= tol and abs(p1.y - p2.y) <= tol

def is_positive(value: float, tol: float = EPSILON) -> bool:
    """Check if a value is strictly greater than zero (by at least tolerance)."""
    return value > tol

def is_negative(value: float, tol: float = EPSILON) -> bool:
    """Check if a value is strictly less than zero (by at least negative tolerance)."""
    return value < -tol
