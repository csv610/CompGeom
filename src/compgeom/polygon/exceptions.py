"""Domain-specific exceptions for polygon operations."""

from __future__ import annotations

class PolygonError(Exception):
    """Base class for exceptions in the polygon module."""
    pass

class PointOutsidePolygonError(PolygonError):
    """Raised when a point is expected to be inside or on the boundary of a polygon but is not."""
    pass

class PolygonPathNotFoundError(PolygonError):
    """Raised when a path between two points within a polygon cannot be found."""
    pass

class HoleConnectionError(PolygonError):
    """Raised when an algorithm fails to connect a hole to the outer boundary of a polygon."""
    pass

class UnsupportedAlgorithmError(PolygonError):
    """Raised when a requested decomposition or processing algorithm is not supported."""
    pass

class DegeneratePolygonError(PolygonError):
    """Raised when a polygon is degenerate (e.g., area is zero, or too few vertices)."""
    pass
