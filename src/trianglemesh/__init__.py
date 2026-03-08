"""Shared geometry and algorithm package for the TriangleMesh project."""

from .geometry import EPSILON, Point
from .planar import DCEL, DCELFace, DCELHalfEdge, DCELVertex, build_polygon_dcel, locate_face

__all__ = [
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
    "EPSILON",
    "Point",
    "build_polygon_dcel",
    "locate_face",
]
